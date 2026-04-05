# Ghostwriter Skill

## Context

We're building a LinkedIn content writing skill as a **single skill with sub-workflows** that runs in Claude Code.

The goal: a full ghostwriting system running locally as one skill on Drive + Supabase.

## Architecture (One Toolbox)

Following Anthropic's skill best practices (see `Resources/skill-architecture-guide.md`):
- One skill folder, one SKILL.md entry point, sub-workflows as reference files
- Progressive disclosure: Claude loads only what's needed per task
- SKILL.md target 500-800 lines (realistic for this scope), reference files loaded on demand
- All data self-contained inside the skill folder

```
Skills/ghostwriter/
├── SKILL.md                    # Entry point (500-800 lines)
│                                # Main write flow + intent routing table
├── PRODUCT.md                  # Living status tracker
├── BUILD-PLAN.md               # This plan (saved copy)
│
├── references/                 # Sub-workflows (loaded on demand)
│   ├── voice-training.md       # Analyze samples → voice JSON
│   ├── swipe-workflow.md       # Save/search inspiration posts (manual paste, no scraping)
│   ├── hooks-workflow.md       # Browse/suggest hooks & templates
│   ├── knowledge-workflow.md   # Add/chunk/embed docs
│   ├── brand-workflow.md       # Set up or update brand identity
│   ├── trends-workflow.md      # Surface trending topics via web search
│   └── guardrails.md           # Voice rules, banned words, quality gate
│
├── scripts/                    # Runtime scripts (stdlib only, zero pip installs)
│   ├── query_vectors.py        # Supabase pgvector similarity search
│   ├── embed_and_store.py      # Chunk + embed + upsert to Supabase
│   └── setup.sql               # CREATE TABLE statements for Supabase
│
├── brand.md                    # Brand identity data (Layer 2)
├── voice-profile.json          # Extracted voice style (Layer 3)
│
├── voice-samples/              # Raw writing samples for training
├── swipe/                      # Saved inspiration posts (manually pasted)
├── templates/
│   ├── hooks.json              # Start with 20-30, grow over time
│   └── frameworks.json         # Start with 10-15, grow over time
├── knowledge/                  # Source docs (originals)
├── approved/                   # Past approved posts: YYYY-MM-DD-slug.md
└── ghost-posts.json            # Pillar balance + post metadata (cap at 100 entries)
```

## Decisions & Constraints

| Decision | Why |
|----------|-----|
| No LinkedIn scraping | Legal risk. Swipe = manual paste only |
| No graphics/Canva | Deferred. Not core to writing loop |
| No competitive analysis scraping | No viable data source without LinkedIn API |
| No newsletter-writer patterns | Completely separate skill, different domain |
| No reference to external skills | Self-contained, no dependencies on imagegen/firecrawl/Nelly |
| Templates start small | 20-30 hooks + 10-15 frameworks, not 360. Grow over time |
| SKILL.md 500-800 lines | 500 is unrealistic for this scope based on existing skill sizes |
| Replace existing linkedin-writer | Ghostwriter supersedes it. One domain = one skill |
| Scripts use stdlib only | `urllib.request` for HTTP (matches imagegen pattern). Zero pip installs needed |
| Skip `allowed-tools` frontmatter | No existing skill in vault uses it. Follow convention |
| API keys hardcoded in SKILL.md | Matches imagegen pattern (Gemini key in SKILL.md). Will refactor later if needed |
| Daily notes path: `Daily/YYYY-MM-DD.md` | Ignore numbered variants. Use `date +%Y-%m-%d` to get today |
| Approved post naming: `YYYY-MM-DD-slug.md` | Date-prefix for sorting. Retrieve last 5 via `ls -t approved/ \| head -5` |
| Template embedding deferred | At 20-30 items, read JSON directly. Embed to pgvector only when 100+ items |
| ghost-posts.json kept | Simplest pillar balance tracker. Cap at last 100 entries, archive older |

## Feature → Skill Mapping

| # | Feature | Implementation | Where |
|---|-------------|----------------|-------|
| 1 | Chat-based post writing | **Main flow in SKILL.md** | SKILL.md |
| 2 | Voice/style training | Sub-workflow | references/voice-training.md |
| 3 | Knowledge base | Sub-workflow + Supabase pgvector | references/knowledge-workflow.md |
| 4 | Brand identity | Sub-workflow + brand.md | references/brand-workflow.md |
| 5 | Auto-memory | **Daily notes + ghost-posts.json + approved/** | Built-in |
| 6 | Swipe file | Sub-workflow + swipe/ folder (manual paste) | references/swipe-workflow.md |
| 7 | Templates | Sub-workflow + JSON files (pgvector when 100+ items) | references/hooks-workflow.md |
| 8 | LinkedIn preview | HTML file, open in browser | SKILL.md (inline) |
| 9 | Trending research | Sub-workflow + web search | references/trends-workflow.md |

**Removed:** Graphics, scheduling, competitive analysis, Chrome extension, analytics

## Prompt Architecture (Loaded in SKILL.md Step 0)

```
Layer 1: Base system prompt (~300 tokens)
  → "You are writing LinkedIn posts as Virgil. First person, his voice..."

Layer 2: Brand identity (~400 tokens)
  → From brand.md
  → Positioning, audience, pillars, tone, do-say/don't-say

Layer 3: Voice profile (~300 tokens)
  → From voice-profile.json
  → Sentence length, vocabulary, structure, signature phrases

Layer 4: Dynamic context (per request, ~4200 tokens)
  → Top-5 knowledge chunks (pgvector via scripts/query_vectors.py)
  → Top-3 relevant swipe posts (pgvector)
  → Top-2 matching templates/hooks (pgvector)

Fallback: If Supabase is unreachable, skip Layer 4. Write using Layers 1-3 + voice profile only.

Total: ~5200 tokens context + generation budget
```

## Intent Routing (in SKILL.md)

SKILL.md must include an explicit routing table so Claude knows which reference file to load:

```
| User says | Action |
|-----------|--------|
| "write a post", "linkedin post" | Run main write flow (in SKILL.md) |
| "train voice", "analyze my writing" | Read references/voice-training.md |
| "save this post", "swipe" | Read references/swipe-workflow.md |
| "suggest a hook", "templates" | Read references/hooks-workflow.md |
| "add to knowledge", "embed this" | Read references/knowledge-workflow.md |
| "set up brand", "update brand" | Read references/brand-workflow.md |
| "what's trending" | Read references/trends-workflow.md |
```

## Memory & Learning (3 layers)

| Layer | What | Where | When |
|-------|------|-------|------|
| **Short-term** | Recent approvals/rejections, feedback | **Daily notes** (`Daily/YYYY-MM-DD.md`) | Written after each approve/reject |
| **Metadata** | Pillar counts, rejections, post history | **ghost-posts.json** (cap 100 posts, 20 rejections) | Updated on approve/reject |
| **Structured** | Past approved posts (full text) | **approved/** folder | Skill reads last 5 before writing |

**Daily notes integration:**
- On approve: append to today's Daily note: `### Ghostwriter: Approved post on [topic], hook type: [type], pillar: [pillar]`
- On reject: append: `### Ghostwriter: Rejected draft — [reason from Virgil]`
- On next write: read last 3 Daily notes for recent patterns + check ghost-posts.json rejections

**Cold start (day 1, zero approved posts):**
- Use `Context/brand.md` voice rules as fallback for Layer 2
- Use voice-samples/ for Layer 3
- Skip "read last 5 approved" step
- After 5+ approved posts, switch to approved/-first pattern

## Supabase Integration

### Scripts (the execution path)

**`scripts/query_vectors.py`** — Similarity search at draft time
- Input: `--table` (knowledge_chunks|swipe_embeddings|template_embeddings), `--query` (text), `--limit` (int)
- Process: Embed query via OpenAI `text-embedding-3-small` (1536 dims), call Supabase REST API with pgvector `<=>` operator
- Output: JSON array of matching rows to stdout
- Uses `urllib.request` only (stdlib, no pip installs)
- Error handling: retries 2x on network failure, returns empty JSON array `[]` on persistent failure
- API keys: hardcoded in script (matches imagegen pattern), or read from SKILL.md-provided args
- Called from SKILL.md via Bash:
  ```
  python3 "/Users/virgilbrewster/My Drive/Virgil Brain/Skills/ghostwriter/scripts/query_vectors.py" --table knowledge_chunks --query "topic here" --limit 5
  ```
- SKILL.md instruction: "If script returns empty or non-zero exit, proceed without Layer 4 dynamic context"

**`scripts/embed_and_store.py`** — Chunk + embed + store
- Input: `--table`, `--source` (file path or stdin), `--metadata` (JSON string)
- Process: Split text at paragraph boundaries respecting 512-1024 token chunks, embed via OpenAI `text-embedding-3-small`, upsert to Supabase
- Handles re-embedding: deletes existing chunks for same source_file before inserting
- Uses `urllib.request` only (stdlib)
- Error handling: retries 2x, prints error to stderr on failure

**`scripts/setup.sql`** — Supabase table creation
- Run once in Supabase SQL editor
- Creates pgvector extension + 3 tables with correct column types
- Includes similarity search function for convenience

### Embedding model decision
**OpenAI `text-embedding-3-small`** (not Voyage AI). Produces 1536-dim vectors matching the `vector(1536)` column type. Simpler (one fewer API key), well-documented, cheaper.

### Tables (3)

| Table | Purpose | Columns |
|-------|---------|---------|
| `knowledge_chunks` | Embedded doc chunks | id, content, source_file, chunk_index, token_count, embedding vector(1536), created_at |
| `swipe_embeddings` | Searchable inspiration | id, content, author, tags text[], embedding vector(1536), created_at |
| `template_embeddings` | Hooks & frameworks | id, type (hook/framework), name, structure jsonb, category, embedding vector(1536) |

RLS not needed — single user. Simple select/insert.

## Voice Profile JSON Schema

```json
{
  "sentence_length": {
    "short_pct": 40,
    "medium_pct": 45,
    "long_pct": 15,
    "avg_words": 12
  },
  "tone": ["conversational", "direct", "first-person"],
  "vocabulary": {
    "tier": "simple",
    "banned_words": ["leverage", "empower", "game-changer", "dive in"],
    "signature_phrases": ["Let's fucking go", "One last dance", "That's the beauty"]
  },
  "structure": {
    "hook_style": "question or bold statement, max 8 words",
    "paragraph_length": "1-2 sentences",
    "post_length_range": [150, 400],
    "whitespace": "heavy, single-line paragraphs"
  },
  "punctuation": {
    "uses_ellipsis": true,
    "uses_em_dash": false,
    "uses_swearing": true
  },
  "content_ratio": {
    "reader_value_pct": 90,
    "personal_pct": 10
  }
}
```

Note: `Context/brand.md` remains the canonical brand source. `brand.md` inside the skill folder is a skill-specific subset optimized for prompt injection (Layer 2). If brand evolves, update the canonical source first, then refresh the skill copy.

## Build Order

### Phase 1: Core Writing Loop (no Supabase needed)
1. Create folder structure + PRODUCT.md + empty subdirs
2. Create brand.md from existing `Context/brand.md`
3. Create voice-profile.json by analyzing voice-samples/
4. Create references/guardrails.md (voice rules, banned words, quality gate)
5. Build SKILL.md with prompt architecture + main write flow + intent routing table
6. **Test voice profile independently:** Generate 3 test excerpts, compare to real posts
7. **Test write flow:** Write 5 posts via `/ghostwriter`, compare to Virgil's voice

### Phase 2: Scripts + Supabase
8. Build scripts/embed_and_store.py (chunk + embed + upsert)
9. Build scripts/query_vectors.py (similarity search)
10. Set up 3 Supabase tables with pgvector
11. Test scripts: embed a test doc, query it, verify results
12. Wire Layer 4 dynamic context injection into SKILL.md
13. **Test:** Write posts with knowledge injection, compare quality

### Phase 3: Sub-workflows
14. Build references/knowledge-workflow.md (uses embed_and_store.py)
15. Build references/swipe-workflow.md (manual paste + embed)
16. Seed templates/hooks.json (20-30 hooks) and frameworks.json (10-15 frameworks)
17. Build references/hooks-workflow.md (read JSON directly at this scale, pgvector later when 100+)
18. Build references/voice-training.md (sample analysis → JSON)
19. Build references/brand-workflow.md (interview → brand.md)
20. **Test:** Full loop — brand → voice → knowledge → write

### Phase 4: Learning + Research
21. ~~Honcho learning loop~~ — REMOVED, replaced with file-based (ghost-posts.json + Daily notes)
22. Wire Daily notes logging (append to today's Daily/YYYY-MM-DD.md on approve/reject)
23. Build references/trends-workflow.md (web search for trending topics)
24. Decommission linkedin-writer: remove from Skills/CLAUDE.md active list, archive old skill
25. **Test:** End-to-end daily workflow with learning loop

## Verification

- [ ] `/ghostwriter` produces posts matching Virgil's voice
- [ ] Voice profile JSON captures writing style from samples
- [ ] scripts/embed_and_store.py chunks and stores correctly
- [ ] scripts/query_vectors.py returns relevant results
- [ ] Knowledge search injects useful context into posts
- [ ] Swipe save (manual paste) + search works
- [ ] Hook suggestions match requested topics
- [ ] Brand identity injects correctly (Layer 2)
- [ ] ghost-posts.json updated on approve/reject (posts + rejections arrays)
- [ ] Daily notes updated on approve/reject
- [ ] Cold start works (zero approved posts)
- [ ] Fallback works (Supabase unreachable, Layers 1-3 only)
- [ ] Learning loop: approve → save → next write improves
