#!/usr/bin/env python3
"""
Embed and Store — Chunk text, generate embeddings, upsert to Supabase pgvector.

Usage:
  python3 embed_and_store.py --table knowledge_chunks --source /path/to/file.md
  python3 embed_and_store.py --table swipe_embeddings --source /path/to/file.md --metadata '{"author":"John","tags":["ppc"]}'
  echo "some text" | python3 embed_and_store.py --table knowledge_chunks --source stdin

Options:
  --table TABLE       Target table: knowledge_chunks, swipe_embeddings, template_embeddings
  --source PATH       File path to read, or "stdin" to read from stdin
  --metadata JSON     Optional JSON string with extra fields (author, tags, type, name, category)
  --supabase-url URL  Supabase project URL (or SUPABASE_URL env var)
  --supabase-key KEY  Supabase service role key (or SUPABASE_SERVICE_KEY env var)
  --openai-key KEY    OpenAI API key (or OPENAI_API_KEY env var)
  --chunk-size INT    Target chunk size in chars (default: 1500, ~375 tokens)
  --quiet             Suppress progress output
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
EMBEDDING_DIMS = 1536
DEFAULT_CHUNK_SIZE = 1500  # chars, roughly 375 tokens


# ─── Chunking ────────────────────────────────────────────────────────────

def chunk_text(text, chunk_size=DEFAULT_CHUNK_SIZE):
    """Split text into chunks at paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current) + len(para) + 2 > chunk_size and current:
            chunks.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para

    if current.strip():
        chunks.append(current.strip())

    return chunks


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
            print(f"ERROR: Embedding failed after 3 attempts: {e}", file=sys.stderr)
            return None


# ─── Supabase Upsert ─────────────────────────────────────────────────────

def supabase_request(url, key, method, path, body=None):
    """Make a request to Supabase REST API."""
    full_url = f"{url}/rest/v1/{path}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(full_url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status in (200, 201, 204):
                return True, None
            return False, f"Status {resp.status}"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return False, f"HTTP {e.code}: {error_body[:200]}"
    except urllib.error.URLError as e:
        return False, f"URL error: {e}"


def delete_existing(url, key, table, source_file):
    """Delete existing chunks for the same source file (re-embedding)."""
    path = f"{table}?source_file=eq.{urllib.request.quote(source_file)}"
    return supabase_request(url, key, "DELETE", path)


def insert_row(url, key, table, row):
    """Insert a single row into a Supabase table."""
    return supabase_request(url, key, "POST", table, row)


# ─── Main Logic ──────────────────────────────────────────────────────────

def embed_and_store(table, source, metadata, supabase_url, supabase_key,
                    openai_key, chunk_size, quiet):
    """Read source, chunk, embed, and store in Supabase."""

    # Read input
    if source == "stdin":
        text = sys.stdin.read()
        source_file = "stdin"
    else:
        if not os.path.exists(source):
            print(f"ERROR: File not found: {source}", file=sys.stderr)
            return False
        with open(source, "r", encoding="utf-8") as f:
            text = f.read()
        source_file = os.path.basename(source)

    if not text.strip():
        print("ERROR: Empty input", file=sys.stderr)
        return False

    # Parse metadata
    meta = {}
    if metadata:
        try:
            meta = json.loads(metadata)
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON metadata: {metadata}", file=sys.stderr)
            return False

    # Chunk the text
    if table == "swipe_embeddings":
        # Swipe posts are stored as single entries, not chunked
        chunks = [text.strip()]
    else:
        chunks = chunk_text(text, chunk_size)

    if not quiet:
        print(f"Table: {table}")
        print(f"Source: {source_file}")
        print(f"Chunks: {len(chunks)}")

    # Delete existing chunks for this source (re-embedding)
    if table == "knowledge_chunks" and source != "stdin":
        ok, err = delete_existing(supabase_url, supabase_key, table, source_file)
        if not quiet:
            if ok:
                print(f"Cleared old chunks for {source_file}")
            elif err:
                print(f"Warning: Could not clear old chunks: {err}")

    # Embed and store each chunk
    success_count = 0
    for i, chunk in enumerate(chunks):
        if not quiet:
            print(f"Embedding chunk {i+1}/{len(chunks)}...", end=" ")

        embedding = get_embedding(chunk, openai_key)
        if not embedding:
            if not quiet:
                print("FAILED")
            continue

        # Build row based on table
        if table == "knowledge_chunks":
            row = {
                "content": chunk,
                "source_file": source_file,
                "chunk_index": i,
                "token_count": len(chunk) // 4,  # rough estimate
                "embedding": embedding,
            }
        elif table == "swipe_embeddings":
            row = {
                "content": chunk,
                "author": meta.get("author", "unknown"),
                "tags": meta.get("tags", []),
                "embedding": embedding,
            }
        elif table == "template_embeddings":
            row = {
                "type": meta.get("type", "hook"),
                "name": meta.get("name", f"template_{i}"),
                "structure": meta.get("structure", {}),
                "category": meta.get("category", "general"),
                "embedding": embedding,
            }
        else:
            print(f"ERROR: Unknown table: {table}", file=sys.stderr)
            return False

        ok, err = insert_row(supabase_url, supabase_key, table, row)
        if ok:
            success_count += 1
            if not quiet:
                print("OK")
        else:
            if not quiet:
                print(f"FAILED: {err}")

        # Rate limit: 500ms between chunks
        if i < len(chunks) - 1:
            time.sleep(0.5)

    if not quiet:
        print(f"\nDone: {success_count}/{len(chunks)} chunks stored")

    return success_count > 0


# ─── CLI ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Chunk, embed, and store in Supabase pgvector")
    parser.add_argument("--table", required=True,
                        choices=["knowledge_chunks", "swipe_embeddings", "template_embeddings"],
                        help="Target table")
    parser.add_argument("--source", required=True, help="File path or 'stdin'")
    parser.add_argument("--metadata", default=None, help="JSON string with extra fields")
    parser.add_argument("--supabase-url", default=os.environ.get("SUPABASE_URL"),
                        help="Supabase project URL")
    parser.add_argument("--supabase-key", default=os.environ.get("SUPABASE_SERVICE_KEY"),
                        help="Supabase service role key")
    parser.add_argument("--openai-key", default=os.environ.get("OPENAI_API_KEY"),
                        help="OpenAI API key")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE,
                        help="Target chunk size in chars")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")

    args = parser.parse_args()

    if not args.supabase_url:
        print("ERROR: No Supabase URL. Use --supabase-url or set SUPABASE_URL", file=sys.stderr)
        sys.exit(1)
    if not args.supabase_key:
        print("ERROR: No Supabase key. Use --supabase-key or set SUPABASE_SERVICE_KEY", file=sys.stderr)
        sys.exit(1)
    if not args.openai_key:
        print("ERROR: No OpenAI key. Use --openai-key or set OPENAI_API_KEY", file=sys.stderr)
        sys.exit(1)

    success = embed_and_store(
        table=args.table,
        source=args.source,
        metadata=args.metadata,
        supabase_url=args.supabase_url,
        supabase_key=args.supabase_key,
        openai_key=args.openai_key,
        chunk_size=args.chunk_size,
        quiet=args.quiet,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
