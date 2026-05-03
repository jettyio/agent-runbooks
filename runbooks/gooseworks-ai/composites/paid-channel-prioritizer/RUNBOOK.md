---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/paid-channel-prioritizer/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/paid-channel-prioritizer
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Paid Channel Prioritizer
  imported_at: '2026-05-03T02:33:21Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: paid-channel-prioritizer
    confidence: high
secrets: null
---
# Paid Channel Prioritizer — Agent Runbook

## Objective

For founders who don't know where to start with paid ads. Analyzes ICP, competitor ad presence, budget constraints, and product type to recommend which 1-2 paid channels to start with and provides a 90-day ramp plan. Prevents the common mistake of spreading a small budget across too many platforms.

This runbook guides an agent through intake, competitor ad research, channel scoring, and recommendation synthesis for an early-stage paid acquisition plan. The agent must concentrate the available budget on the best one or two channels, explain tradeoffs, and produce a practical 90-day ramp plan.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/channel-strategy.md` | Paid channel strategy with profile, scoring, recommendation, budget allocation, and 90-day ramp plan. |
| `/app/results/summary.md` | Executive summary of the run, decisions, and notable assumptions. |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed`. |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Results directory | `/app/results` | Directory where all required output files are written. |
| product-name-url | Required | What are you selling? |
| business-model | Required | SaaS / Marketplace / E-commerce / Service / App |
| b2b-or-b2c | Required | Drives channel selection heavily |
| icp | Required | Who are you selling to? (Role, company size, industry) |
| monthly-ad-budget | Required | Be honest — how much can you spend? |
| average-deal-size-ltv | Required | What's a customer worth? |
| current-acquisition-channels | Required | How are you getting customers today? (Organic, referral, outbound, etc.) |
| competitor-names | Required | 3-5 competitors |
| landing-page-ready | Required | Do you have a dedicated LP or just a homepage? |
| conversion-goal | Required | Free trial / Demo / Purchase / Lead magnet download |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Web search | Tool | Yes | Used to inspect competitor ad libraries, paid search traces, and channel validation signals. |
| Markdown writer | Agent capability | Yes | Used to write the final strategy report. |
| Basic arithmetic | Agent capability | Yes | Used for budget allocation, daily caps, and weighted scoring. |

## Step 1: Environment Setup

1. Create `/app/results` if it does not exist.
2. Confirm the user has provided product, ICP, budget, competitors, landing-page readiness, and conversion-goal information.
3. If any required intake item is missing, ask only for the missing items before continuing.
4. Initialize `/app/results/validation_report.json` with setup status.

## Step 2: Intake

Collect and normalize the following profile fields:

- Product name and URL
- Business model
- B2B or B2C motion
- ICP, including role, company size, industry, and buyer context
- Monthly ad budget
- Average deal size or LTV
- Current acquisition channels
- Three to five competitors
- Landing page readiness
- Conversion goal

## Step 3: Competitor Ad Presence Research

Use web search and public ad libraries to build a competitor channel map. Search for each competitor across Meta Ad Library, Google Ads Transparency Center, LinkedIn sponsored content traces, Twitter/X ads, YouTube, and TikTok.

Record whether each competitor appears active, not found, or ambiguous for each channel. Treat competitor spend as validation, but do not copy a competitor channel blindly if the user's budget or ICP makes it impractical.

## Step 4: Channel Scoring

Score Google Search, Meta, LinkedIn, YouTube, Twitter/X, and TikTok from 1 to 10 on:

- Buyer intent, weighted 25%
- Targeting precision, weighted 20%
- Competitor validation, weighted 15%
- Budget efficiency, weighted 15%
- ICP reachability, weighted 15%
- Creative requirements, weighted 10%

Calculate a weighted score for each channel and preserve the reasoning behind every score that materially affects the final ranking.

## Step 5: Recommendation

Select the primary channel based on weighted score, minimum viable budget, and creative readiness. Select a secondary channel only when the budget is sufficient, the channel serves a distinct funnel stage, and the user can support its creative needs.

Apply this allocation guide:

| Budget Level | Recommendation |
|---|---|
| Under $1.5K/month | One channel only. |
| $1.5K-$3K/month | One primary channel plus limited retargeting. |
| $3K-$7K/month | Two channels with roughly 65% primary, 25% secondary, and 10% retargeting. |
| $7K+/month | Two or three channels with explicit testing budget. |

## Step 6: 90-Day Ramp Plan

Create a ramp plan with:

- Month 1 foundation: tracking, landing page, audiences or keywords, and initial variants.
- Month 2 optimization: conversion review, retargeting, new tests, and landing-page improvements.
- Month 3 scale or pivot: budget changes, diagnosis criteria, and when to rerun the analysis.

## Step 7: Write Strategy Output

Write `/app/results/channel-strategy.md` with these sections:

- `# Paid Channel Strategy — [Product Name] — [DATE]`
- `## Your Profile`
- `## Channel Scoring`
- `## Why [Primary Channel]`
- `## Why NOT [Channel They Might Assume]`
- `## Budget Allocation`
- `## 90-Day Ramp Plan`
- `## Pre-Launch Checklist`

## Step 8: Iterate on Errors (max 3 rounds)

If the strategy is incomplete or internally inconsistent, make targeted corrections and re-check it. Stop after max 3 rounds. Acceptable corrections include recalculating weighted scores, tightening budget allocation, resolving unsupported competitor claims, and adding missing pre-launch checklist items.

## Common Fixes

| Issue | Fix |
|---|---|
| Missing intake data | Ask for only the missing fields, then continue from Step 2. |
| Budget split across too many platforms | Reduce to one primary channel or one primary plus retargeting. |
| Unsupported competitor claim | Add a source note or mark the signal as ambiguous. |
| Weighted score mismatch | Recalculate the weighted total and update the verdict. |

## Step 9: Final Checklist

Run this verification before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in "$RESULTS_DIR/channel-strategy.md" "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

Checklist:

- The strategy recommends one primary channel and, only when justified, one secondary channel.
- The channel scoring table includes weighted scores and verdicts.
- The budget allocation fits the stated monthly budget.
- The 90-day ramp plan includes setup, learning, optimization, and scale-or-pivot decisions.
- `summary.md` and `validation_report.json` are present.

## Tips

Concentrate small budgets where learning can compound. A channel that is popular in the category still fails if the user cannot afford its minimum viable spend or produce the creative it requires.
