# Hooks & Templates Workflow

Triggered when Virgil says: "suggest a hook", "templates", "hooks", "frameworks", "what hook should I use"

## What It Does

Browses and suggests hooks and frameworks from `templates/hooks.json` and `templates/frameworks.json`. At this scale (25 hooks, 12 frameworks) we read the JSON directly. When either file exceeds 100 items, embed to pgvector and search instead.

## Flow

### Suggest a Hook

1. Read `templates/hooks.json`
2. Ask Virgil (if not provided): "What's the topic?" and "Which pillar? (building in public / agency insider / ai founder life)"
3. Filter hooks by `best_for` matching the pillar
4. Present 5 hooks that fit, with the structure and an example
5. Format:

```
Topic: [topic]
Pillar: [pillar]

1. [Hook Name] — [category]
   Structure: [structure]
   Example: "[example]"

2. ...
```

6. Virgil picks one or says "none" for more options

### Suggest a Framework

1. Read `templates/frameworks.json`
2. Based on the topic and what Virgil described, suggest 3 matching frameworks
3. Format:

```
1. [Framework Name]
   Flow: [structure]
   Best when: [when]
   Example post: "[example_post hook]"

2. ...
```

### Add a Hook

When Virgil says "add this hook" or describes a new pattern:

1. Read `templates/hooks.json`
2. Get the next ID (max existing + 1)
3. Ask for: name, structure, example, category (bold_statement/question/scene/dialogue/statistic), best_for pillars
4. Append to the hooks array
5. Write updated JSON
6. Confirm: "Added hook #[ID]: [name]. [total] hooks now."

### Add a Framework

Same pattern:
1. Read `templates/frameworks.json`
2. Next ID, ask for fields
3. Append and write
4. Confirm

## Hook Categories

- `bold_statement` — declarative, punchy, no question mark
- `question` — ends with ? provokes thought
- `scene` — sets a visual, puts you somewhere
- `dialogue` — opens with a quote from a real person
- `statistic` — leads with a number or data point

## When to Embed (Future)

When hooks.json exceeds 100 items:
1. Embed all hooks to `template_embeddings` table
2. Switch this workflow to use `query_vectors.py` for search
3. Keep hooks.json as the source of truth, embed as index
