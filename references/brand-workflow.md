# Brand Workflow

Triggered when Virgil says: "set up brand", "update brand", "brand identity", "change positioning"

## What It Does

Creates or updates `brand.md` (the skill-specific Layer 2 brand identity). This is the prompt context that tells the AI who Virgil is, who he writes for, and how to position content.

## Flow

### First-Time Setup (brand.md doesn't exist)

1. Check if `Context/brand.md` exists in the vault (canonical source)
   - If yes: read it, extract a skill-specific subset, save as `brand.md`
   - If no: run the brand interview below

2. **Brand Interview** — ask these questions one at a time:
   - Who are you? (name, role, company, age, location)
   - What are you building? (product, one sentence)
   - Who is your audience? (be specific — not "founders" generically)
   - What's your positioning? (how are you different from competitors?)
   - What are your 3 content pillars? (the themes you write about)
   - What's the content ratio? (how much educational vs promotional?)
   - What words/phrases are YOU? (things you'd say naturally)
   - What words/phrases are NOT you? (things that make you cringe)

3. Generate `brand.md` from answers. Target ~400 tokens.

4. Show Virgil the result. Ask: "Does this capture you?"

5. Save to `Skills/ghostwriter/brand.md`

### Update Brand

When Virgil says "update brand" or "change [specific thing]":

1. Read current `brand.md`
2. Ask what changed (or apply what Virgil described)
3. Show the diff: what's changing and why
4. Save updated version
5. Remind: "If this is a fundamental change, also update `Context/brand.md` (the canonical source)."

### Sync from Canonical

When brand evolves and `Context/brand.md` was updated first:

1. Read `Context/brand.md` (canonical)
2. Read current `Skills/ghostwriter/brand.md` (skill copy)
3. Show differences
4. Ask: "Sync skill brand.md with the canonical version?"
5. If yes: regenerate skill-specific subset

## Brand.md Structure

The file should always have these sections:
- **Who** — identity in 2-3 sentences
- **Audience** — specific, not generic
- **Positioning** — what makes you different
- **Three Pillars** — the themes
- **Voice** — how you sound (one paragraph)
- **Content Ratio** — educational vs promotional
- **Do Say** — signature phrases
- **Don't Say** — banned phrases
- **Post Format** — structural rules

Keep it under 400 tokens. This gets loaded into every prompt.
