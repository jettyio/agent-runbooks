---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/competitive-pricing-intel/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/competitive-pricing-intel
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Competitive Pricing Intel
  imported_at: '2026-05-03T02:53:19Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: competitive-pricing-intel
    confidence: high
secrets: null
---

# Competitive Pricing Intel — Agent Runbook

## Objective

Monitor competitor pricing pages using live page capture, historical Web Archive snapshots, and public pricing-change research. Monitor competitor pricing pages via live web scrape and Web Archive snapshots. Track plan changes, tier restructuring, new pricing models, and feature gating shifts. Produces a pricing comparison matrix and flags when a competitor changes packaging. Use when a product marketing team needs to stay current on competitive pricing or when preparing for a pricing change of their own. The runbook produces a current pricing matrix, flags packaging and feature-gating shifts, and summarizes implications for positioning or a planned pricing change.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/pricing-comparison-[YYYY-MM-DD].md` | Competitive pricing report with change alerts, matrix, ICP scenario pricing, feature gating, packaging strategy, and recommendations |
| `/app/results/current-pricing-snapshots.json` | Structured snapshot of each tracked pricing page and extraction metadata |
| `/app/results/historical-pricing-findings.json` | Web Archive and announcement findings used for change detection |
| `/app/results/summary.md` | Executive summary of products tracked, major changes, pricing position, and follow-up actions |
| `/app/results/validation_report.json` | Structured validation results with stages, checks, and `overall_passed` |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Results directory | `/app/results` | `/app/results` | Output directory for required artifacts |
| Product name and pricing page URL | `product_pricing_url` | *(required)* | Your product name and public pricing page URL |
| Competitors to track | `competitors` | *(required)* | Competitor names and pricing page URLs; 2-5 recommended |
| Pricing model | `pricing_model` | *(required)* | How your product charges: per seat, usage, flat, freemium, or hybrid |
| Key comparison dimensions | `comparison_dimensions` | Price, features, limits, support | Buyer-relevant comparison dimensions |
| Run mode | `run_mode` | `first_run` | `first_run` for baseline and history, or `recurring` for snapshot comparison |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Web search | Tool | Yes | Find pricing announcements, community reactions, and recent plan changes |
| Web page fetcher | Tool | Yes | Capture current pricing pages for each product |
| Web Archive | External site | Yes | Compare prior pricing page snapshots |
| Markdown writer | Runtime capability | Yes | Emit the final pricing-comparison report |
| JSON writer | Runtime capability | Yes | Emit structured snapshots, historical findings, and validation results |

## Step 1: Environment Setup

1. Create `/app/results` if it does not exist.
2. Validate that `product_pricing_url`, `competitors`, `pricing_model`, `comparison_dimensions`, and `run_mode` are present.
3. Initialize `current-pricing-snapshots.json`, `historical-pricing-findings.json`, `summary.md`, and `validation_report.json` paths.
4. Record the run timestamp in UTC and the list of products being tracked.

## Step 2: Intake

Collect and normalize the competitive set:

1. **Your product name + pricing page URL**
2. **Competitors to track** — Names + pricing page URLs (2-5 recommended)
3. **Your pricing model** — How do you charge? (per seat, usage, flat, freemium, etc.)
4. **Key comparison dimensions** — What matters to your buyer? (price per seat, included features, limits, support tiers)
5. **First run or recurring?**
   - **First run:** Full baseline capture + historical analysis
   - **Recurring:** Compare against last snapshot

Reject the run if no competitor pricing URLs are supplied. Keep the product list bounded to the user's requested set; if more than 5 competitors are supplied, process the first 5 and note the truncation in `summary.md`.

## Step 3: Current Pricing Capture

For each product and competitor pricing URL, fetch the current page and extract plan, price, packaging, and feature-gating details.

For each competitor's pricing page:

```
Fetch: [competitor pricing URL]
```

Extract:
- **Plan names and prices** — Every tier with monthly and annual pricing
- **Feature matrix** — What's included in each tier?
- **Limits** — Usage caps, seat limits, storage, API calls
- **Add-ons** — What costs extra beyond base plans?
- **Enterprise tier** — "Contact us" or listed price? What's gated behind sales?
- **Free tier / trial** — What's available without paying?
- **Pricing model** — Per seat / per user / usage-based / flat / hybrid
Search for past versions of their pricing page:

```
Search: "web.archive.org" "[competitor pricing URL]"
Fetch: web.archive.org/web/*/[competitor pricing URL]
```

Look for the last 2-3 snapshots to detect:
- **Price increases/decreases**
- **Plan restructuring** (new tiers added, tiers removed)
- **Feature gating changes** (features moved between tiers)
- **Model shifts** (e.g., moved from per-seat to usage-based)
- **Free tier changes** (expanded or restricted)
```
Search: "[competitor]" pricing change OR "new pricing" OR "updated plans"
Search: "[competitor]" blog pricing OR announcement plans
Search: "[competitor]" site:reddit.com pricing OR "price increase"
```

Capture any public announcements or community reactions to pricing changes.

Store the extracted records in `/app/results/current-pricing-snapshots.json` with URL, fetch timestamp, HTTP status, extracted plan data, and confidence notes.

## Step 4: Historical and Announcement Research

Search Web Archive snapshots and public announcements for pricing changes. Review the most recent 2-3 archived snapshots per pricing URL when available, then search for pricing-change posts, launch announcements, and community reactions.

Captured findings must include the source URL, observation date when known, previous value, current value, change type, and confidence level.

## Step 5: Pricing Analysis

Normalize all products into a comparable matrix and evaluate pricing position for the buyer scenario described by the user.

Build a normalized comparison across all competitors:

| Dimension | Your Product | Competitor A | Competitor B | Competitor C |
|-----------|-------------|-------------|-------------|-------------|
| **Starter price** | $X/mo | $X/mo | $X/mo | $X/mo |
| **Mid-tier price** | $X/mo | $X/mo | $X/mo | $X/mo |
| **Enterprise** | $X/mo or Custom | ... | ... | ... |
| **Pricing model** | [Model] | [Model] | [Model] | [Model] |
| **Free tier** | [Yes/No + limits] | ... | ... | ... |
| **Annual discount** | [X%] | ... | ... | ... |
| **Key limit (starter)** | [e.g., 5 seats] | ... | ... | ... |
| **Key limit (mid)** | [e.g., 20 seats] | ... | ... | ... |
| **Overage cost** | [$/unit or blocked] | ... | ... | ... |
| **Support included** | [Email/chat/phone] | ... | ... | ... |
For the ICP's typical use case, calculate effective cost:

```
Scenario: [Typical ICP — e.g., "10-person growth team, 5,000 contacts, 1,000 emails/month"]

Your Product: $[X]/mo for this scenario
Competitor A: $[X]/mo for this scenario
Competitor B: $[X]/mo for this scenario
```

This reveals true competitive pricing position, not just list price.
For each competitor, identify their packaging strategy:

| Strategy | Description | Who Uses It |
|----------|-------------|-------------|
| **Good-Better-Best** | 3 tiers, clear upgrade path | Most SaaS |
| **Usage-based** | Pay for what you use | API/infrastructure |
| **Per-seat** | Price scales with team | Collaboration tools |
| **Freemium** | Free forever, premium features | PLG products |
| **Reverse trial** | Full features free, then downgrade | Conversion-optimized |
| **Platform + add-ons** | Base platform + modular features | Enterprise |
Compare current snapshot against previous:

| Change Type | Severity | Example |
|------------|----------|---------|
| **Price increase** | High | Starter: $29 → $39/mo |
| **Price decrease** | High | Aggressive competitive move |
| **New tier added** | Medium | "Growth" plan between Starter and Pro |
| **Tier removed** | Medium | Simplified from 4 to 3 plans |
| **Feature ungated** | Medium | Feature moved from Pro to Starter |
| **Feature gated** | Medium | Feature moved from Starter to Pro |
| **Model change** | Critical | Shifted from per-seat to usage-based |
| **Free tier change** | High | Free plan limits reduced/expanded |

Classify each change by severity: `Critical`, `High`, `Medium`, or `Low`. A pricing model shift is `Critical`; price increases, decreases, and free-tier changes are usually `High`.

## Step 6: Write the Pricing Report

Write `/app/results/pricing-comparison-[YYYY-MM-DD].md` using this structure:

```markdown

Also write `/app/results/summary.md` with the top changes, your product's relative pricing position, and recommended next actions.

## Step 7: Validate Outputs

Run these checks and write `/app/results/validation_report.json`:

1. All mandatory output files exist and are non-empty.
2. Every requested competitor appears in `current-pricing-snapshots.json`.
3. The pricing report contains `Pricing Change Alerts`, `Competitive Pricing Matrix`, `ICP Scenario Pricing`, `Feature Gating Comparison`, `Packaging Strategy Summary`, and `Pricing Recommendations`.
4. Every high-severity or critical finding has at least one source URL.
5. `summary.md` includes issues or manual follow-up when data was missing or confidence was low.

## Step 8: Iterate on Errors (max 3 rounds)

If validation fails, inspect `validation_report.json`, fix the missing or weak section, and rerun validation. Stop after max 3 rounds and leave `overall_passed=false` if required evidence or output files are still missing.

### Common Fixes

| Issue | Fix |
|---|---|
| Missing competitor in snapshot JSON | Re-fetch that competitor's pricing page and append a structured record |
| Pricing report missing a required section | Re-render the report with the complete template from Step 6 |
| Finding lacks a source URL | Add the pricing page, archive snapshot, announcement, or community source used for the observation |
| Low extraction confidence | Add a manual note in `summary.md` and mark the affected values as approximate |

## Final Checklist

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
TODAY="$(date -u +%Y-%m-%d)"
for f in \
  "$RESULTS_DIR/pricing-comparison-$TODAY.md" \
  "$RESULTS_DIR/current-pricing-snapshots.json" \
  "$RESULTS_DIR/historical-pricing-findings.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

Checklist:

- `pricing-comparison-[YYYY-MM-DD].md` contains all report sections.
- `current-pricing-snapshots.json` includes every requested product and competitor.
- `historical-pricing-findings.json` records archive and announcement evidence.
- `summary.md` states the pricing position, major changes, and manual follow-up.
- `validation_report.json` includes stages, results, and `overall_passed`.

## Tips

- **web_search** — for pricing announcements and community reactions
- **fetch_webpage** — for scraping current pricing pages
- No API keys required

Run monthly (pricing changes are infrequent but impactful):

```bash
0 8 1 * * python3 run_skill.py competitive-pricing-intel --client <client-name>
```

Useful trigger phrases:

- "What are competitors charging?"
- "Has [competitor] changed their pricing?"
- "Build a pricing comparison matrix"
- "Run competitive pricing intel for [client]"
- "Monitor competitor pricing pages"
