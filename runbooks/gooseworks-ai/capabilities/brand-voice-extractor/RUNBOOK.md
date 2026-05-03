---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/brand-voice-extractor/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/brand-voice-extractor
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Brand Voice Extractor
  imported_at: '2026-05-03T02:45:48Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: brand-voice-extractor
    confidence: high
secrets: {}
---

# Brand Voice Extractor — Agent Runbook

## Objective

Analyze a company's published content to extract a practical brand voice profile that future writing can match. The runbook samples 10-20 representative content pieces, captures evidence about tone, vocabulary, sentence structure, formatting, calls to action, and target persona, then synthesizes the findings into actionable writing guidelines. It is intended for outreach, content, campaign, and client work where output should reflect the company's existing voice rather than a generic style.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/brand_voice_profile.md` | Final brand voice profile with evidence, voice dimensions, and actionable writing guidelines |
| `/app/results/evidence_inventory.json` | Structured list of analyzed URLs, titles, extracted text metadata, and evidence snippets |
| `/app/results/summary.md` | Executive summary with company, source count, strongest findings, and issues |
| `/app/results/validation_report.json` | Structured validation report covering setup, source selection, extraction, analysis, and final file checks |

## Parameters

| Parameter | Default | Required | Description |
|---|---:|---:|---|
| `results_dir` | `/app/results` | No | Directory where all required output files must be written |
| `company_name` | None | Yes | Company or client whose brand voice should be analyzed |
| `content_urls` | None | Yes unless `content_inventory_path` is provided | Direct URLs to analyze |
| `content_inventory_path` | None | Yes unless `content_urls` is provided | Path to a prior `site-content-catalog` inventory |
| `number_of_pages` | `15` | No | Target number of pages to analyze; keep the final sample between 10 and 20 when possible |

## Dependencies

| Dependency | Type | Required | Purpose |
|---|---|---:|---|
| WebFetch-capable agent | Tool | Yes | Fetch pages and extract main content |
| Markdown writer | Agent capability | Yes | Produce the final profile and summary |
| JSON writer | Agent capability | Yes | Persist evidence and validation metadata |
| `site-content-catalog` output | Prior artifact | Conditional | Supplies candidate pages when direct URLs are not provided |

## Step 1: Environment Setup

1. Create `results_dir` if it does not exist.
2. Confirm `company_name` is present.
3. Confirm either `content_urls` or `content_inventory_path` is present.
4. Initialize `/app/results/validation_report.json` with a `setup` stage.

## Step 2: Select Content to Analyze

If direct URLs are provided, normalize and deduplicate them. Otherwise, read the content inventory and select a diverse sample of 10-20 pages:

- 8-10 blog posts spanning how-to, opinion, and product updates
- 2-3 landing pages such as homepage, product, or solutions pages
- 2-3 case studies or customer stories when available
- 1-2 comparison or versus pages when available

Prefer a mix of recent and older content and a mix of topics so consistency and voice evolution can be detected.

## Step 3: Fetch and Extract Text

For each selected URL:

1. Fetch the page.
2. Extract the main content body, excluding navigation, footer, sidebar, cookie banners, and unrelated page chrome.
3. Store title, URL, content type, raw text, word count, and any extraction warnings in `evidence_inventory.json`.
4. If a page cannot be fetched or has too little usable text, replace it with the next-best candidate and record the reason.

## Step 4: Analyze Voice Dimensions

Evaluate the sample across these dimensions and keep short evidence snippets for each finding:

- Tone: formality, emotional register, authority stance, humor usage, and directness
- Vocabulary and language: reading level, jargon, technical depth, power words, avoided terms, and distinctive phrases
- Sentence structure: sentence length, paragraph length, opening patterns, transitions, and fragments
- Formatting patterns: headers, lists, emphasis, media, calls to action, and callouts
- Content structure: article length, introductions, conclusions, data usage, examples, and storytelling
- Persona and audience: reader role, seniority, assumed knowledge, point of view, and relationship to the reader

## Step 5: Generate Brand Voice Profile

Write `/app/results/brand_voice_profile.md` using this structure:

```markdown
# Brand Voice Profile: [Company Name]
**Analyzed:** [Date] | **Content pieces analyzed:** [N]
**Sources:** [list of URLs analyzed]

## Voice Summary

## Tone Profile

## Language & Vocabulary

## Structure & Formatting

## Audience & Persona

## Writing Guidelines

### Do

### Don't

### Voice Samples
```

Use evidence from the analyzed content for every major claim. Include representative quotes only as short excerpts and attribute them to source URLs in the evidence inventory.

## Step 6: Validate Outputs

Check that:

- `brand_voice_profile.md` exists and includes all required sections.
- `evidence_inventory.json` contains the selected URL list and extraction metadata.
- The profile analyzes at least 10 pages unless fewer were provided or accessible.
- Every major voice dimension has evidence.
- `summary.md` and `validation_report.json` exist.

## Step 7: Iterate on Errors (max 3 rounds)

If validation fails or the evidence is thin, run up to max 3 rounds of targeted fixes. Replace failed URLs, add missing dimensions, tighten unsupported claims, or regenerate malformed files. Stop early once all required outputs pass validation.

## Common Fixes

| Issue | Fix |
|---|---|
| Fewer than 10 usable pages | Add more blog, landing, case study, or comparison URLs and record why the sample is limited |
| Weak evidence for tone | Pull short snippets that show formality, emotion, authority, humor, or directness |
| Generic writing guidelines | Rewrite each guideline so it names a concrete pattern and includes an example |
| Missing validation output | Rebuild `validation_report.json` from the completed stages |

## Final Checklist

Run this verification script before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="${RESULTS_DIR:-/app/results}"
for f in \
  "$RESULTS_DIR/brand_voice_profile.md" \
  "$RESULTS_DIR/evidence_inventory.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

The run is complete only when the verification script reports `PASS` for every required file.

## Tips

- 15 pages is the sweet spot: fewer than 10 usually misses variation, while more than 25 adds cost without much signal.
- Blog posts are usually the strongest voice signal because landing pages tend to be more formulaic.
- Look for consistency and inconsistency; if the company uses multiple voice modes, name when each mode appears.
- Flag content that appears ghost-written or dramatically different from the rest of the sample.
