---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/ad-campaign-analyzer/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/ad-campaign-analyzer
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Ad Campaign Analyzer
  imported_at: '2026-05-03T02:33:56Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: ad-campaign-analyzer
    confidence: high
secrets: null
---

# Ad Campaign Analyzer — Agent Runbook

## Objective
Analyze paid advertising performance data and convert it into concrete campaign decisions. This runbook diagnoses which campaigns, ad groups, audiences, creatives, keywords, and channels are working, which are wasting budget, and where spend should be reduced, scaled, or tested. It also checks whether apparent winners are statistically credible, evaluates funnel quality, and produces an actionable budget reallocation plan with dollar amounts.

The source skill was imported from a directory mirror and resolved to the upstream `SKILL.md` before conversion. Use the upstream origin in the frontmatter for provenance and future diffing.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/campaign_analysis.md` | Narrative analysis of channel, campaign, ad group, creative, keyword, audience, and funnel performance |
| `/app/results/recommendations.csv` | Tabular cut, scale, hold, and test recommendations with rationale and priority |
| `/app/results/budget_reallocation.json` | Structured current-vs-recommended budget allocation, scenario modeling, and dollar shifts |
| `/app/results/summary.md` | Executive summary of findings, recommended actions, risks, and next steps |
| `/app/results/validation_report.json` | Programmatic validation report for input quality, analysis completeness, and output file checks |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Results directory | `results_dir` | `/app/results` | Directory where all required output artifacts are written |
| Campaign data | `campaign_data` | required | CSV export, pasted table, or screenshots from the advertising platform |
| Platform(s) | `platforms` | inferred from data | Google Ads, Meta Ads, LinkedIn Ads, or another paid channel |
| Time period | `time_period` | required | Date range covered by the campaign data |
| Monthly budget | `monthly_budget` | optional | Total ad spend available for reallocation recommendations |
| Primary goal | `primary_goal` | required | Conversion outcome such as demos, trials, purchases, or leads |
| Target metrics | `target_metrics` | optional | Target CPA, ROAS, CAC, or benchmark thresholds |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Python 3.12 | Runtime | Yes | Used for CSV parsing, calculations, and validation |
| `pandas` | Python package | Yes | Normalizes tabular ad-platform exports |
| `numpy` | Python package | Yes | Computes rates, confidence intervals, and scenario math |
| `scipy` | Python package | Optional | Statistical significance tests when enough sample volume exists |
| OCR or vision-capable model | Capability | Conditional | Required when campaign data arrives as screenshots |

## Step 1: Environment Setup

1. Create `/app/results` if it does not exist.
2. Install or verify `pandas`, `numpy`, and `scipy`.
3. Confirm the campaign data, platform list, time period, primary goal, and any target metrics are available.
4. If screenshot data is provided, extract it into a normalized table before analysis.

## Step 2: Normalize Campaign Data

1. Load the exported CSV, pasted table, or extracted screenshot data.
2. Standardize field names for spend, impressions, clicks, conversions, revenue, campaign, ad group, creative, keyword, audience, and channel.
3. Calculate derived metrics: CTR, CPC, CVR, CPA, ROAS, revenue per click, conversion value, and spend share.
4. Record data-quality issues such as missing conversion values, mismatched date ranges, or incomplete channel coverage.

## Step 3: Diagnose Performance

1. Rank each campaign entity by spend, conversions, CPA, ROAS, and conversion volume.
2. Separate high-spend low-return waste from low-spend opportunities that need more budget to learn.
3. Check statistical confidence before treating small-sample outliers as winners or failures.
4. Compare funnel stages to identify whether the constraint is click quality, landing-page conversion, offer fit, or downstream economics.

## Step 4: Generate Cut, Scale, Hold, and Test Decisions

1. Mark campaigns or entities for `cut` when spend is material and performance is below target without a credible learning rationale.
2. Mark campaigns or entities for `scale` when they beat target metrics with enough volume.
3. Mark uncertain entities for `hold` when more data is needed.
4. Propose focused tests for targeting, keywords, creative, landing pages, offers, and budget concentration.
5. Write `/app/results/recommendations.csv` with action, entity, platform, current metric values, reason, expected impact, and priority.

## Step 5: Reallocate Budget Across Channels

1. Compare Google, Meta, LinkedIn, and any other active channels on equal conversion and revenue definitions.
2. Identify over-funded channels and under-funded channels relative to marginal returns and learning needs.
3. Build conservative, balanced, and aggressive reallocation scenarios.
4. Write `/app/results/budget_reallocation.json` with current spend, recommended spend, dollar shift, rationale, assumptions, and expected outcome for each scenario.

## Step 6: Write Analysis Outputs

1. Write `/app/results/campaign_analysis.md` with findings by channel and by campaign entity.
2. Write `/app/results/summary.md` with the top decisions, recommended budget movement, and risks.
3. Call out data gaps and any places where the recommendation depends on assumptions.

## Step 7: Iterate on Analysis Quality (max 3 rounds)

If validation finds incomplete outputs or unsupported recommendations, run up to max 3 rounds of targeted correction:

1. Fix missing required files or invalid schemas first.
2. Re-check metric formulas and entity grouping.
3. Strengthen recommendations that lack a metric-backed rationale.
4. Re-run validation after each correction round.

## Common Fixes

| Issue | Fix |
|---|---|
| Missing conversions or revenue | Analyze CPA and funnel diagnostics, and flag ROAS as unavailable |
| Screenshot data extracted poorly | Re-run OCR or request a CSV export before making budget decisions |
| Small sample sizes | Downgrade decisions to hold/test unless statistical confidence is adequate |
| Platform exports use different attribution windows | Normalize windows or state that cross-channel comparison is directional |
| Required output missing | Regenerate the specific file and re-run the final verification script |

## Final Checklist

Run this verification before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/campaign_analysis.md" \
  "$RESULTS_DIR/recommendations.csv" \
  "$RESULTS_DIR/budget_reallocation.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

The runbook is complete only when every required output exists, every recommendation ties back to an observed metric or stated assumption, and the validation report has `overall_passed=true`.

## Tips

Prefer raw platform exports over screenshots. Keep the action list narrow enough to execute: a few high-confidence budget shifts and tests are more useful than a long list of weak observations.
