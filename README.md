# LinkedIn Ghostwriter

Claude Code skill that writes LinkedIn posts in your voice. One command (`/linkg`), multiple sub-workflows loaded on demand.

## What It Does

- **Writes posts** — first-person narrative, voice-matched, pillar-balanced
- **Trains voice** — learns from approved posts, recalibrates over time
- **Manages swipe files** — save inspiration posts for reference
- **Suggests hooks** — 25+ hooks and 12 frameworks from real post analysis
- **Embeds knowledge** — pgvector-powered knowledge base for context-rich writing
- **Surfaces trends** — web search filtered through your niche
- **Brand identity** — consistent positioning across all content

## Structure

```
ghostwriter/
├── SKILL.md              # Main skill definition + intent routing
├── brand.md              # Brand identity layer
├── voice-profile.json    # Voice style parameters
├── ghost-posts.json      # Post metadata + pillar tracking
├── approved/             # Approved posts (learning data)
├── swipe/                # Inspiration posts
├── ideas/                # Content backlog + used ideas
├── knowledge/            # Knowledge base docs
├── references/           # Sub-workflow definitions
│   ├── guardrails.md
│   ├── hooks-workflow.md
│   ├── swipe-workflow.md
│   ├── voice-training.md
│   ├── brand-workflow.md
│   ├── knowledge-workflow.md
│   └── trends-workflow.md
├── templates/
│   ├── hooks.json        # 25 hook templates
│   └── frameworks.json   # 12 post frameworks
├── scripts/
│   ├── setup.sql         # pgvector schema
│   ├── embed_and_store.py
│   └── query_vectors.py
└── voice-samples/        # Cold start voice examples
```

## Setup

1. Drop the `ghostwriter/` folder into your Claude Code `Skills/` directory
2. Trigger with `/linkg`, "ghostwriter", or "write a post"
3. The skill loads brand + voice + guardrails on every run (~260 lines context)

## Architecture

- **No SaaS dependency** — runs entirely as a Claude Code skill
- **File-based learning** — approved posts + JSON metadata, no database required
- **Supabase optional** — pgvector scripts ready for when knowledge base exceeds 100+ items
- **Progressive disclosure** — sub-workflows loaded only when needed

Built with [Claude Code](https://claude.ai/claude-code).
