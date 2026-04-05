# Trends Workflow

Triggered when Virgil says: "what's trending", "trending topics", "trends", "what should I write about", "what's hot in PPC"

## What It Does

Surfaces trending topics relevant to Virgil's three pillars using web search. Filters for topics that matter to agency owners, not just industry news.

## Flow

### Step 1: Search for Trends

Run web searches across these categories:

**PPC / Agency news:**
- "PPC news this week"
- "Google Ads changes [current month year]"
- "Meta Ads updates [current month year]"
- "agency reporting tools news"

**AI + Marketing:**
- "AI marketing tools news this week"
- "AI replacing marketing jobs"
- "AI automation agencies"

**Founder / Building:**
- "SaaS founder lessons LinkedIn"
- "building in public updates"

Use the firecrawl-search skill or WebSearch tool.

### Step 2: Filter with The Agency Owner Test

For each trend found, apply the filter from Virgil Voice Master:

> "Does this affect the day-to-day life of an agency owner?"

- Meta changing targeting algorithm → YES (real problem they wake up to)
- Meta's $30 billion forecast → NO (investor news, not operator news)

Keep only topics that pass.

### Step 3: Match to Pillars

Categorize each trending topic:
- Building in Public — if it connects to Sucana's journey
- Agency Insider — if it's about agency/PPC pain
- AI Founder Life — if it's about AI changing how you work

Check `ghost-posts.json` for pillar balance. Prioritize the underrepresented pillar.

### Step 4: Present

```
Trending Topics (filtered for agency relevance):

Building in Public:
1. [topic] — [one-line why it matters]
2. [topic] — [one-line]

Agency Insider:
3. [topic] — [one-line]
4. [topic] — [one-line]

AI Founder Life:
5. [topic] — [one-line]

Pillar balance: building [X], agency [Y], ai-life [Z]
Recommended: #[number] — underrepresented pillar

Pick a number to write, or say "more" for deeper research.
```

### Step 5: Write (If Virgil Picks)

Route back to the main write flow in SKILL.md with the selected topic.

## Cadence

Virgil can run this anytime. No scheduled automation (that's for LFG/Nelly). On-demand only.

## Sources to Trust

- Google Ads blog
- Meta for Business blog
- Search Engine Land
- PPC Hero
- Reddit: r/PPC, r/FacebookAds, r/googleads
- LinkedIn trending in PPC/marketing

## Sources to Ignore

- Generic "top 10 marketing trends" listicles
- Investor/earnings news
- Tools you've never heard of pitching themselves
