# Voice Training Workflow

Triggered when Virgil says: "train voice", "analyze my writing", "voice samples", "update voice profile"

## What It Does

Analyzes writing samples to extract or update the voice profile in `voice-profile.json`. Can process new samples, recalibrate from approved posts, or incorporate feedback.

## Flow

### Analyze New Samples

1. Virgil provides writing samples (pastes text, gives file paths, or points to a folder)

2. Save raw samples to `voice-samples/`:
   ```
   voice-samples/YYYY-MM-DD-source.md
   ```

3. Analyze across all samples for:
   - **Sentence length distribution**: Count words per sentence, calculate short/medium/long percentages
   - **Tone markers**: What energy comes through? (conversational, direct, cheeky, warm, etc.)
   - **Vocabulary patterns**: Common words, banned words that appear, jargon vs simple language
   - **Structure patterns**: How does he open? Close? Transition? How long are paragraphs?
   - **Punctuation habits**: Ellipsis, dashes, swearing, emojis, formatting
   - **Compression ratio**: How many words does he use to make a point vs how many an average writer would use?
   - **Signature phrases**: Recurring phrases that are uniquely his

4. Present findings to Virgil:
   ```
   Voice Analysis from [X] samples:

   Sentence rhythm: [X]% short (1-5 words), [X]% medium (6-15), [X]% long (16+)
   Average sentence: [X] words
   Tone: [list]
   Top vocabulary: [most used simple words]
   Compression: [high/medium/low] — [example of compression]
   Signature phrases found: [list]
   Structure pattern: [how posts typically flow]
   ```

5. Ask: "Update voice-profile.json with these findings?"

6. If yes, read current `voice-profile.json`, merge new data, write updated file.

### Recalibrate from Approved Posts

When Virgil says "recalibrate" or "retrain from approved":

1. Read all files in `approved/`
2. Run the same analysis as above but on approved posts only
3. Compare to current `voice-profile.json`
4. Show differences:
   ```
   Changes detected:
   - Sentence length shifted: was 40/45/15, now 35/50/15
   - New signature phrase found: "[phrase]"
   - Hook style preference: mostly bold_statement (7/10 posts)
   ```
5. Ask: "Apply these updates?"

### Quick Voice Check

When Virgil says "check this against my voice" and pastes text:

1. Read `voice-profile.json` and `references/guardrails.md`
2. Score the text against the profile:
   - Sentence length match: [yes/no]
   - Tone match: [yes/no]
   - Banned words found: [list or none]
   - Banned patterns found: [list or none]
   - Compression level: [matches/too verbose]
3. Give a simple verdict: "Sounds like you" or "Sounds off — [specific issues]"

## What NOT to Do

- Don't override voice-profile.json without showing changes first
- Don't use samples from other people (unless Virgil explicitly says "I want to write more like this person")
- Don't merge DM voice with post voice — they're different registers
