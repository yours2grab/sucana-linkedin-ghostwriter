# Swipe Workflow

Triggered when Virgil says: "save this post", "swipe", "inspiration", "save this for later"

## What It Does

Saves inspiring LinkedIn posts (from other creators) to the swipe/ folder AND optionally embeds them in Supabase for semantic search during writing.

No scraping. All posts are manually pasted by Virgil.

## Flow

### Step 1: Get the Post

Virgil pastes a post or describes it. Capture:
- The full post text
- Author name (ask if not provided)
- Tags (ask: "Any tags? e.g. hook, storytelling, agency, ppc")

### Step 2: Save to File

Save to `swipe/` folder:
```
swipe/YYYY-MM-DD-author-slug.md
```

File format:
```markdown
---
date: YYYY-MM-DD
author: [name]
tags: [tag1, tag2]
why: [one line on what makes this good — ask Virgil or infer]
---

[full post text]
```

### Step 3: Embed (Optional)

Ask: "Want me to embed this for search? (yes/skip)"

If yes:
```bash
python3 "$GHOSTWRITER_DIR/scripts/embed_and_store.py" \
  --table swipe_embeddings \
  --source "$GHOSTWRITER_DIR/swipe/[filename]" \
  --metadata '{"author":"[name]","tags":["tag1","tag2"]}' \
  --quiet
```

### Step 4: Confirm

"Saved to swipe/ and embedded. [X] swipe posts total."

## Browsing Swipe

When Virgil says "show me swipe posts" or "what inspiration do I have":

1. List files in swipe/:
```bash
ls -t "$GHOSTWRITER_DIR/swipe/" | head -10
```

2. If Virgil wants to search by topic:
```bash
python3 "$GHOSTWRITER_DIR/scripts/query_vectors.py" \
  --table swipe_embeddings \
  --query "[topic]" \
  --limit 5 \
  --quiet
```

## What Makes Good Swipe

Save posts that have:
- Strong hooks (study the opening line)
- Good structure (how they flow)
- Voice Virgil likes (conversational, direct)
- Topics relevant to the three pillars

Don't save:
- Corporate content
- AI-generated slop
- Posts that just went viral for controversy
