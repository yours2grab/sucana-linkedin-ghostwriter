# Ghostwriter — Product Status

## What Is It
LinkedIn content skill rebuilt as a single Claude Code skill with sub-workflows. One `/ghostwriter` command, progressive disclosure, self-contained.

## Architecture Decision (2026-04-05)
- Rejected SaaS app (Next.js + Supabase + Inngest)
- Rejected separate slash commands per feature
- Chose: **One skill folder, one SKILL.md, sub-workflows as reference files**
- Pattern follows Anthropic's official skill best practices
- Reference: `Resources/skill-architecture-guide.md`

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Folder structure | Done | Created 2026-04-05, all subdirs created |
| BUILD-PLAN.md | Done | Full architecture spec, cross-checked 2x |
| PRODUCT.md | Done | This file |
| SKILL.md | Done | 386 lines, write flow + prompt layers + intent routing + learning loop |
| brand.md | Done | Extracted from Context/brand.md, ~400 tokens |
| voice-profile.json | Done | Full schema, analyzed from Voice Master + 10 approved posts |
| references/guardrails.md | Done | Banned words/phrases/patterns, quality gate, identity rules |
| ghost-posts.json | Done | Seeded with 10 existing approved posts, pillar counts initialized |
| voice-samples/ | Done | Copied linkedin-approved-posts.md for cold start reference |
| scripts/setup.sql | Done | pgvector extension + 3 tables + match_vectors function |
| scripts/query_vectors.py | Done | Similarity search, JSON to stdout, 3-retry, stdlib only |
| scripts/embed_and_store.py | Done | Chunk + embed + upsert, re-embedding support, stdlib only |
| references/knowledge-workflow.md | Done | Add docs to knowledge base via embed_and_store.py |
| references/swipe-workflow.md | Done | Save inspiration posts (manual paste + optional embed) |
| references/hooks-workflow.md | Done | Browse/suggest/add hooks and frameworks from JSON |
| references/voice-training.md | Done | Analyze samples, recalibrate, quick voice check |
| references/brand-workflow.md | Done | Setup, update, sync brand identity |
| references/trends-workflow.md | Done | Web search for trending topics, agency filter |
| templates/hooks.json | Done | 25 hooks seeded from approved posts analysis |
| templates/frameworks.json | Done | 12 frameworks seeded from approved posts analysis |
| Supabase tables | Deferred | Not needed until 100+ items in any category. Scripts ready when needed. |
| Honcho learning loop | Removed | Replaced with file-based: approved/ + ghost-posts.json + Daily notes |
| Daily notes integration | Wired in SKILL.md | Append ### Ghostwriter entries, needs live testing |
| Read budget rule | Wired in SKILL.md | Never read approved/ during write flow, ~260 lines total context |
| ghost-posts.json rotation | Wired in SKILL.md | Posts cap 100, rejections cap 20, trim oldest |
| linkedin-writer decommission | Done | Removed from Skills/CLAUDE.md active list |

## Phase Progress

- [x] Phase 0: Architecture planning + cross-check
- [x] Phase 1: Core writing loop (Steps 1-7) — voice tested, 3 test posts generated
- [x] Phase 2: Scripts built (Steps 8-10, 12) — testing blocked on Supabase credentials
- [x] Phase 3: Sub-workflows (Steps 14-19) — all 6 reference files built + templates seeded
- [x] Phase 4: Learning + research (Steps 21-24) — file-based learning (no Honcho), trends built, linkedin-writer decommissioned

## Decisions Made

| Date | Decision | Why |
|------|----------|-----|
| 2026-04-05 | Rejected SaaS, chose skill | Already have skill ecosystem, no need for web app |
| 2026-04-05 | One skill, not 8 commands | Anthropic best practice: one domain = one skill |
| 2026-04-05 | Hybrid storage (Drive + pgvector) | Files for editing, Supabase for semantic search |
| 2026-04-05 | Skip analytics, multi-platform, inline edit | Not needed for personal use |
| 2026-04-05 | Remove graphics/Canva | Deferred, not core to writing loop |
| 2026-04-05 | Remove competitive analysis | No viable data source without LinkedIn API |
| 2026-04-05 | No LinkedIn scraping | Legal risk. Swipe = manual paste |
| 2026-04-05 | No newsletter-writer patterns | Completely separate skill, different domain |
| 2026-04-05 | Memory: Daily notes + approved/ + ghost-posts.json | File-based only, no Honcho (confirmed correct after memory audit 2026-04-05) |
| 2026-04-05 | OpenAI text-embedding-3-small (1536 dims) | Not Voyage AI. Simpler, one API key, matches vector(1536) |
| 2026-04-05 | Scripts use stdlib only (urllib.request) | Matches imagegen pattern, zero pip installs |
| 2026-04-05 | API keys hardcoded in SKILL.md | Matches imagegen pattern, refactor later |
| 2026-04-05 | Templates start small (20-30 hooks) | Read JSON directly until 100+ items, then pgvector |
| 2026-04-05 | ghost-posts.json for pillar balance | Cap at 100 entries, archive older |
| 2026-04-05 | Ghostwriter replaces linkedin-writer | One domain = one skill. Decommission old in Phase 4 |
| 2026-04-05 | SKILL.md target 500-800 lines | 500 unrealistic for this scope |
| 2026-04-05 | Approved posts: YYYY-MM-DD-slug.md | Date-prefix for sorting, retrieve last 5 via ls -t |

## Blockers

None. Supabase/pgvector deferred until 100+ items in any category. `/linkg` is fully operational with file-based storage.
