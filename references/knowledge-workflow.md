# Knowledge Workflow

Triggered when Virgil says: "add to knowledge", "embed this", "knowledge base", "store this doc"

## What It Does

Takes a document (file path, URL content, or pasted text) and embeds it into Supabase pgvector for semantic search during post writing. Layer 4 of the prompt stack queries these chunks at draft time.

## Flow

### Step 1: Get the Input

Virgil provides one of:
- A file path → read the file
- Pasted text → use directly
- A URL → use firecrawl-scrape or defuddle to extract content, then embed the markdown output

Ask if unclear: "Is this a file path, pasted text, or a URL?"

### Step 2: Preview Before Embedding

Show Virgil:
- Source: [filename or "pasted text"]
- Length: [word count]
- Estimated chunks: [count based on ~375 words per chunk]
- Table: knowledge_chunks

Ask: "Embed this? (yes/no)"

### Step 3: Embed

Run:
```bash
python3 "$GHOSTWRITER_DIR/scripts/embed_and_store.py" \
  --table knowledge_chunks \
  --source "[file_path_or_stdin]" \
  --quiet
```

For pasted text, pipe it:
```bash
echo "[text]" | python3 "$GHOSTWRITER_DIR/scripts/embed_and_store.py" \
  --table knowledge_chunks \
  --source stdin \
  --quiet
```

### Step 4: Confirm

Report: "Embedded [X] chunks from [source]. Available for next post."

### Step 5: Test (Optional)

If Virgil wants to verify:
```bash
python3 "$GHOSTWRITER_DIR/scripts/query_vectors.py" \
  --table knowledge_chunks \
  --query "[topic from the doc]" \
  --limit 3 \
  --quiet
```

Show the returned chunks to verify relevance.

## Re-embedding

If you embed the same file again, the script automatically deletes old chunks for that source_file before inserting new ones. Safe to re-run.

## What Goes in Knowledge

Good candidates:
- ICP research docs
- Market research / Reddit scrapes
- Product specs and feature descriptions
- Industry reports or articles
- Meeting notes with insights
- Competitor analysis

Bad candidates (don't embed):
- Raw transcripts (too noisy)
- Approved posts (already in approved/ folder)
- Voice/brand docs (already in Layers 2-3)
