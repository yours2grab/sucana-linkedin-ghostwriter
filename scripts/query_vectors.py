#!/usr/bin/env python3
"""
Query Vectors — Semantic similarity search against Supabase pgvector tables.

Usage:
  python3 query_vectors.py --table knowledge_chunks --query "agency reporting pain" --limit 5
  python3 query_vectors.py --table swipe_embeddings --query "founder story hook" --limit 3

Output: JSON array of matching rows to stdout. Empty array [] on failure.

Options:
  --table TABLE       Target table: knowledge_chunks, swipe_embeddings, template_embeddings
  --query TEXT        Search query text
  --limit INT         Max results (default: 5)
  --supabase-url URL  Supabase project URL (or SUPABASE_URL env var)
  --supabase-key KEY  Supabase service role key (or SUPABASE_SERVICE_KEY env var)
  --openai-key KEY    OpenAI API key (or OPENAI_API_KEY env var)
  --quiet             Suppress progress output (only JSON to stdout)
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error


# ─── Configuration ───────────────────────────────────────────────────────

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_ENDPOINT = "https://api.openai.com/v1/embeddings"


# ─── OpenAI Embedding ────────────────────────────────────────────────────

def get_embedding(text, api_key):
    """Get embedding vector from OpenAI text-embedding-3-small."""
    body = json.dumps({
        "model": EMBEDDING_MODEL,
        "input": text,
    }).encode("utf-8")

    req = urllib.request.Request(
        EMBEDDING_ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["data"][0]["embedding"]
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            print(f"Embedding failed: {e}", file=sys.stderr)
            return None


# ─── Supabase RPC Query ──────────────────────────────────────────────────

def query_vectors(supabase_url, supabase_key, table, embedding, limit):
    """Call the match_vectors RPC function in Supabase."""
    url = f"{supabase_url}/rest/v1/rpc/match_vectors"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
    }

    body = json.dumps({
        "query_embedding": embedding,
        "target_table": table,
        "match_count": limit,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            print(f"Supabase query failed: {e}", file=sys.stderr)
            return []


# ─── Main Logic ──────────────────────────────────────────────────────────

def search(table, query, limit, supabase_url, supabase_key, openai_key, quiet):
    """Embed query, search Supabase, return results as JSON."""

    if not quiet:
        print(f"Table: {table}", file=sys.stderr)
        print(f"Query: {query[:100]}", file=sys.stderr)
        print(f"Limit: {limit}", file=sys.stderr)
        print("Embedding query...", file=sys.stderr)

    embedding = get_embedding(query, openai_key)
    if not embedding:
        print("[]")
        return False

    if not quiet:
        print("Searching...", file=sys.stderr)

    results = query_vectors(supabase_url, supabase_key, table, embedding, limit)

    # Output JSON to stdout (this is what SKILL.md reads)
    print(json.dumps(results, indent=2))

    if not quiet:
        print(f"Found: {len(results)} results", file=sys.stderr)

    return len(results) > 0


# ─── CLI ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Semantic search against Supabase pgvector")
    parser.add_argument("--table", required=True,
                        choices=["knowledge_chunks", "swipe_embeddings", "template_embeddings"],
                        help="Target table")
    parser.add_argument("--query", required=True, help="Search query text")
    parser.add_argument("--limit", type=int, default=5, help="Max results")
    parser.add_argument("--supabase-url", default=os.environ.get("SUPABASE_URL"),
                        help="Supabase project URL")
    parser.add_argument("--supabase-key", default=os.environ.get("SUPABASE_SERVICE_KEY"),
                        help="Supabase service role key")
    parser.add_argument("--openai-key", default=os.environ.get("OPENAI_API_KEY"),
                        help="OpenAI API key")
    parser.add_argument("--quiet", action="store_true", help="Only JSON to stdout")

    args = parser.parse_args()

    if not args.supabase_url:
        print("ERROR: No Supabase URL. Use --supabase-url or set SUPABASE_URL", file=sys.stderr)
        print("[]")
        sys.exit(1)
    if not args.supabase_key:
        print("ERROR: No Supabase key. Use --supabase-key or set SUPABASE_SERVICE_KEY", file=sys.stderr)
        print("[]")
        sys.exit(1)
    if not args.openai_key:
        print("ERROR: No OpenAI key. Use --openai-key or set OPENAI_API_KEY", file=sys.stderr)
        print("[]")
        sys.exit(1)

    success = search(
        table=args.table,
        query=args.query,
        limit=args.limit,
        supabase_url=args.supabase_url,
        supabase_key=args.supabase_key,
        openai_key=args.openai_key,
        quiet=args.quiet,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
