# Post Ideas

Post ideas for `/linkg`. Each file is one week or batch.

## Structure

```
ideas/
├── README.md              # This file
├── backlog.md             # Unscheduled ideas (dump zone)
├── week-YYYY-WNN.md       # Weekly plan (e.g. week-2026-W14.md)
└── used.md                # Ideas that became posts (auto-moved)
```

## How It Works

1. Dump ideas anytime into `backlog.md` — one idea per line, pillar tag optional
2. When you say "I need 7 posts this week", the skill reads backlog + content-ideas.md + Daily notes
3. Skill creates a `week-YYYY-WNN.md` with the plan
4. After a post is approved, the idea moves from the weekly plan to `used.md`

## Idea Format (in backlog.md)

```
- [pillar] Hook or topic — optional context
```

Examples:
```
- [agency] Why most agencies pay for tools they forgot they have
- [building] We almost shipped a broken feature on purpose
- [ai-life] I asked Claude to roast my landing page
- The Monday morning data nightmare — no pillar tag = skill picks
```

## Sources

- `backlog.md` — your own ideas (priority 1)
- `/Users/virgilbrewster/My Drive/Sucana/Marketing/Research/content-ideas.md` — LFG-mined hooks (priority 2)
- Daily notes — recent events (priority 3)
