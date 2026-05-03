---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/google-search-ads-builder/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/google-search-ads-builder
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Google Search Ads Builder
  imported_at: '2026-05-03T02:34:26Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: google-search-ads-builder
    confidence: high
secrets: {}
---

# Google Search Ads Builder — Agent Runbook

## Objective

Build a complete Google Search Ads campaign from structured product intake through keyword research, campaign architecture, ad copy, negative keywords, bid recommendations, and import-ready Google Ads Editor files. The runbook emphasizes buyer-language research from competitors, review sites, communities, search suggestions, and the advertiser's own site before creating campaign structure. The final output must be ready for a human marketer to review, adjust, and import into Google Ads Editor.

This runbook was imported from a Gooseworks directory mirror. The source of truth is the pinned upstream `SKILL.md` recorded in `origin.url`; the user-supplied directory URL is preserved only for audit provenance.

## REQUIRED OUTPUT FILES (MANDATORY)

You MUST write all of the following files to `/app/results`. The task is NOT complete until every file exists and is non-empty.

| File | Description |
|---|---|
| `/app/results/campaign_strategy.md` | Campaign strategy document with overview, research summary, funnel map, ad groups, keyword rationale, budgets, and launch checklist |
| `/app/results/google_ads_editor_import.csv` | Import-ready campaign rows for Google Ads Editor |
| `/app/results/keyword_research.csv` | Keyword universe with source, funnel stage, intent, match type, score, and recommended ad group |
| `/app/results/ad_copy.csv` | Responsive Search Ad headlines and descriptions by ad group |
| `/app/results/negative_keywords.csv` | Campaign-level and ad-group-level negative keywords |
| `/app/results/bid_budget_recommendations.md` | Bid strategy and budget allocation recommendations |
| `/app/results/summary.md` | Executive summary of campaign, assumptions, high-priority launch actions, and unresolved questions |
| `/app/results/validation_report.json` | Structured validation results with stages, checks, and `overall_passed` |

## Parameters

| Parameter | Default | Required | Description |
|---|---:|---:|---|
| `results_dir` | `/app/results` | No | Directory where all required output files are written |
| `product_name` | none | Yes | Product or brand being advertised |
| `product_url` | none | Yes | Website or landing page for product audit and ad destination |
| `value_prop` | none | Yes | One-line value proposition |
| `product_category` | none | Yes | Category buyers use when searching |
| `icp` | none | Yes | Ideal customer profile, role, pain, and company stage |
| `monthly_budget` | none | Yes | Monthly Google Ads budget for campaign and bid recommendations |
| `conversion_goal` | none | Yes | Primary goal such as demo bookings, trials, purchases, or downloads |
| `landing_pages` | none | No | Destination URLs, or note that landing pages need to be created |
| `competitor_domains` | none | Yes | Three to five competitor domains for keyword and positioning research |
| `geographic_targeting` | none | Yes | Countries or regions for targeting |
| `existing_keywords` | none | No | Known or currently bid keywords |
| `known_converting_keywords` | none | No | Existing performance data or historically converting terms |

## Dependencies

| Dependency | Type | Required | Purpose |
|---|---|---:|---|
| Web search capability | Agent tool | Yes | Competitor, review, community, and search-suggestion research |
| Webpage fetch capability | Agent tool | Yes | Extract competitor positioning, review language, and site content |
| Spreadsheet or CSV writer | Local tool | Yes | Write keyword, ad copy, negative keyword, and import files |
| Google Ads Editor | External app | No | Human review and import after outputs are generated |

## Step 1: Environment Setup

1. Create `/app/results` if it does not exist.
2. Confirm all required inputs are available: `product_name`, `product_url`, `value_prop`, `product_category`, `icp`, `monthly_budget`, `conversion_goal`, `competitor_domains`, and `geographic_targeting`.
3. If required inputs are missing, write `validation_report.json` with `overall_passed=false`, write `summary.md` naming the missing inputs, and stop.
4. Create empty working tables for keywords, ad groups, ad copy, negatives, and validation checks.

```bash
mkdir -p /app/results
```

## Step 2: Intake and Campaign Brief

Capture the advertiser's business context before researching keywords.

| Field | What to collect |
|---|---|
| Product | Product name, URL, one-line value proposition, and product category |
| Audience | ICP, buyer role, pain, stage, and search vocabulary |
| Commercial setup | Monthly budget, conversion goal, geography, and landing pages |
| Market | Three to five competitors plus existing or known-converting keywords |

Write the intake summary into `campaign_strategy.md` and flag assumptions that need human confirmation.

## Step 3: Deep Keyword Research

Generate seed keywords in three buckets: problem-aware, solution-aware, and brand or competitor. For each competitor domain, research organic ranking pages, visible ad positioning, comparison pages, alternatives pages, pricing pages, and category list pages. Use fetched pages to capture exact buyer language, not only marketer-authored category labels.

Mine review language from G2, Capterra, category review pages, and competitor review pages. Mine community terminology from Reddit and Hacker News when relevant. Audit the advertiser's own site for repeated product, feature, pain, and outcome language. Expand the set with search suggestions, related searches, question formats, and comparison modifiers.

Every candidate keyword must be recorded in `keyword_research.csv` with source, inferred intent, funnel stage, match type recommendation, and notes.

## Step 4: Keyword Architecture

Map keywords to funnel stages: top of funnel, middle of funnel, bottom of funnel, competitor, and brand. Classify intent as transactional, commercial, problem-aware, informational, navigational, competitor, or jobs-to-be-done. Estimate competitive density from SERP quality, advertiser presence, CPC expectations, and competitor dominance.

Create a match-type matrix using exact match for high-intent terms, phrase match for controlled expansion, broad match only when budget and conversion tracking support it, and negatives to protect spend. Score each keyword from 1 to 10 using intent, relevance, volume proxy, competition, CPC risk, and landing page fit. Identify the top 10 quick-win launch keywords.

## Step 5: Campaign and Ad Group Structure

Design tightly themed ad groups around intent, funnel stage, and landing page fit. Avoid mixing broad problem queries with high-intent commercial or competitor terms in the same ad group. Recommended launch structure is:

| Campaign or ad group type | Use when |
|---|---|
| Brand | The product has existing search demand |
| Competitor | Competitor alternatives and comparison terms are allowed by strategy |
| Category high intent | Buyers search for the product category directly |
| Problem or pain | Pain terms have clear commercial follow-through |
| Feature or use case | Use cases map to distinct landing pages or messaging |

Document the full structure in `campaign_strategy.md` and mirror it in `google_ads_editor_import.csv`.

## Step 6: Ad Copy Generation

For every ad group, generate three Responsive Search Ads. Each ad group should include 15 headline candidates and 4 description candidates covering value proposition, pain, differentiator, proof, CTA, category fit, and landing page continuity. Keep headlines within Google Ads limits and descriptions within the platform's character limits.

Write all variants to `ad_copy.csv` with columns for campaign, ad group, asset type, text, character count, message angle, and pinning recommendation if any.

## Step 7: Negative Keywords

Build campaign-level negatives for low-intent, job-seeking, educational, free-only, template-only, support, login, unrelated consumer, and research-only queries. Add category-specific negatives where ambiguous terms could pull irrelevant traffic. Add ad-group-level negatives to prevent intent overlap between groups.

Write `negative_keywords.csv` with keyword, match type, level, campaign, ad group when applicable, and rationale.

## Step 8: Bid Strategy and Budget Recommendation

Recommend budget allocation by funnel stage and campaign type. Use high-intent exact and phrase campaigns for the highest-confidence spend, competitor campaigns only when landing page and brand strategy support them, and exploratory problem-aware campaigns with capped budgets.

Write `bid_budget_recommendations.md` with the recommended bid strategy, launch budget splits, conversion tracking assumptions, and a first two-week optimization plan.

## Step 9: Export Files

Create `google_ads_editor_import.csv` with campaign, ad group, keyword, match type, final URL, headline, description, status, bid, budget, and negative keyword rows as appropriate for Google Ads Editor review. Also update the strategy document with campaign overview, research summary, competitive density map, campaign structure, keywords by ad group, ad copy, negatives, bid recommendations, quick wins, and launch checklist.

## Step 10: Validate Outputs

Run structural checks before finishing:

1. Confirm every required output file exists and is non-empty.
2. Confirm each ad group has keywords, at least three Responsive Search Ad concepts, and relevant negatives.
3. Confirm `google_ads_editor_import.csv` has consistent campaign and ad group names.
4. Confirm keyword rows include source, funnel stage, intent, score, and match type.
5. Confirm `summary.md` lists assumptions and manual review items.

## Step 11: Iterate on Errors (max 3 rounds)

If validation fails, perform up to max 3 rounds of targeted fixes. Re-check the failed files after each round and update `validation_report.json`. Stop early when all required outputs pass validation.

### Common Fixes

| Issue | Fix |
|---|---|
| Missing required input | Write a clear blocking question to `summary.md` and set `overall_passed=false` |
| Thin keyword set | Return to competitor, review, community, and search-suggestion research |
| Overlapping ad groups | Add ad-group-level negatives and split mixed-intent keywords |
| Import CSV has inconsistent names | Normalize campaign and ad group names across all CSV files |
| Ads exceed character limits | Rewrite the asset and preserve the angle in notes |

## Final Checklist

Run the verification script and do not finish until it prints PASS for each required file.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/campaign_strategy.md" \
  "$RESULTS_DIR/google_ads_editor_import.csv" \
  "$RESULTS_DIR/keyword_research.csv" \
  "$RESULTS_DIR/ad_copy.csv" \
  "$RESULTS_DIR/negative_keywords.csv" \
  "$RESULTS_DIR/bid_budget_recommendations.md" \
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

Use the exact words buyers use in reviews, communities, comparisons, and search suggestions. Prioritize high-intent, landing-page-aligned keywords before broad expansion, and treat Google Ads Editor output as a reviewable import draft rather than an unchecked production launch.
