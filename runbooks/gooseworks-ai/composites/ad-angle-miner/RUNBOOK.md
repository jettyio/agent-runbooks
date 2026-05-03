---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/ad-angle-miner/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/ad-angle-miner
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Ad Angle Miner
  imported_at: '2026-05-03T02:33:37Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    source_collection: composites
    skill_name: ad-angle-miner
    confidence: high
secrets:
  APIFY_API_TOKEN:
    required: false
    description: Required when collecting review or Reddit data through Apify actors.
---

# Ad Angle Miner — Agent Runbook

## Objective

Mine the highest-converting ad angles from customer reviews, Reddit complaints, support tickets, and competitor ads. Extracts actual pain language, competitor weaknesses, and outcome phrases that real buyers use. Outputs a ranked angle bank with proof quotes and recommended ad formats per angle. This runbook converts customer voice data into a ranked ad-angle bank with supporting evidence, buyer language, competitor weaknesses, and recommended ad formats. It should be used when a team needs new campaign angles grounded in real customer phrasing rather than internal brainstorming.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/angle_bank.md` | Ranked angle bank with evidence, rationale, and recommended ad formats |
| `/app/results/angle_bank.csv` | Spreadsheet-friendly angle bank with score, source mix, and proof quotes |
| `/app/results/source_evidence.json` | Normalized evidence records collected from reviews, Reddit, support tickets, X, and competitor ads |
| `/app/results/summary.md` | Executive summary of strongest angles, data coverage, and caveats |
| `/app/results/validation_report.json` | Structured validation report for collection, scoring, and output checks |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Results directory | `/app/results` | Output directory for all required files |
| Product | Required | Product name and one-sentence description |
| Competitors | Required | Two to five competitor names |
| ICP | Required | Target buyer role, company stage, and pain |
| Data sources | Required | Reviews, Reddit, X, support tickets, NPS comments, or competitor ads to mine |
| Tested angles | None | Existing tested angles to exclude or down-rank |
| Max items per source | `100` | Bounded collection limit per source |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| `APIFY_API_TOKEN` | Conditional | Required for Apify review and Reddit scraping |
| Web search access | Yes | Required for public B2B reviews, X complaints, and competitor ad discovery |
| Python 3.12 with `requests` | Yes | Normalize evidence and write structured outputs |
| CSV/JSON writing capability | Yes | Produce required machine-readable outputs |

## Step 1: Environment Setup

Create `/app/results` and verify the collection plan before making network requests. If Apify sources are selected, verify `APIFY_API_TOKEN` is set; otherwise continue with pasted files and web-search-accessible sources.

```bash
mkdir -p /app/results
if [ -z "${APIFY_API_TOKEN:-}" ]; then
  echo "APIFY_API_TOKEN not set; skip Apify-only collectors unless pasted evidence is provided."
fi
```

## Step 2: Intake

Capture the product, two to five competitors, ICP, selected data sources, and any angles already tested. Convert the intake into a collection plan with explicit source names, queries, item limits, and skip rules for previously tested angles.

## Step 3: Source Collection

Collect evidence from the selected sources. For Amazon reviews, start `web_wanderer/amazon-reviews-extractor`, poll until the actor succeeds, and fetch the dataset items. For Reddit, use `trudax/reddit-scraper-lite` with keyword searches or subreddit start URLs. For B2B review sites, X, support tickets, NPS comments, and competitor ads, use web search or provided files.

Keep collection bounded to max 2 rounds per source query. Stop early when a source yields enough repeated language patterns to score angles reliably.

## Step 4: Evidence Normalization

Normalize each evidence item into `source_evidence.json` with source type, product or competitor, rating or sentiment where available, text excerpt, URL or file provenance, date if present, and tags for pain, outcome, competitor weakness, objection, or buying trigger.

## Step 5: Angle Extraction

Extract candidate angles from repeated buyer language. Preserve exact proof quotes, especially complaints, outcome phrases, and comparison language. Group near-duplicates into a single angle and retain source diversity so one loud thread does not dominate the bank.

## Step 6: Score and Rank Angles

Score each angle using evidence volume, intensity of language, source diversity, ICP fit, competitor weakness, and novelty against tested angles. Produce a ranked bank with recommended ad formats such as problem-solution, comparison, founder POV, objection handling, proof-led testimonial, or pain-agitation.

## Step 7: Iterate on Errors (max 3 rounds)

If evidence is thin, scoring is tied, or quotes are not attributable, run targeted follow-up collection for max 3 rounds. Each round must name the missing evidence, the exact query or file to inspect, and the reason the result changes or does not change the ranking.

## Step 8: Write Outputs

Write `angle_bank.md`, `angle_bank.csv`, `source_evidence.json`, `summary.md`, and `validation_report.json` under `/app/results`. The Markdown summary should call out top angles, proof quotes, recommended ad formats, weak or missing data sources, and any angles skipped because they were already tested.

## Common Fixes

| Issue | Fix |
|---|---|
| Too few proof quotes | Run one targeted collection round against the strongest missing source |
| Angles overlap | Merge duplicates and keep the strongest phrasing as the canonical angle |
| Competitor data dominates | Split own-product outcomes from competitor weaknesses before ranking |
| Source has no URL | Record file name, row number, or pasted-input label as provenance |

## Final Checklist

Run this verification before finishing.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/angle_bank.md" \
  "$RESULTS_DIR/angle_bank.csv" \
  "$RESULTS_DIR/source_evidence.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

## Tips

Prioritize exact customer phrasing over polished marketing language. The strongest angles usually come from repeated pain statements, competitor complaints, and concrete outcome descriptions that can be quoted with provenance.
