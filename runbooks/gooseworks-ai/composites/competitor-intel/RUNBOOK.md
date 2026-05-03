---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/competitor-intel/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/competitor-intel
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Competitor Intelligence
  imported_at: '2026-05-03T02:46:34Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: competitor-intel
    confidence: high
secrets:
  APIFY_API_TOKEN:
    env: APIFY_API_TOKEN
    description: Optional Apify token for deeper Reddit, Twitter/X, and LinkedIn scraping.
    required: false
---

# Competitor Intelligence - Agent Runbook

## Objective
Research and monitor a defined set of competitors across public web sources, social channels, review sites, blogs, and optional Apify-backed social scraping. Build one structured profile per competitor, compare competitors against the user's company context, and translate the findings into positioning, product, content, and go-to-market recommendations. The runbook is designed for bounded research: gather evidence, cite sources, identify gaps, and produce reusable outputs that can be refreshed in future monitoring cycles.

This runbook was imported from a directory mirror. The canonical upstream source is `https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/competitor-intel/SKILL.md`, discovered from the user-supplied Gooseworks URL `https://skills.gooseworks.ai/skills/competitor-intel`.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/competitor_profiles.md` | Structured profile for each researched competitor, including overview, positioning, product, content, customer evidence, competitive signals, and opportunities. |
| `/app/results/competitive_landscape.md` | Cross-competitor landscape summary with positioning, content, feature, takeaway, and recommended-action tables. |
| `/app/results/monitoring_plan.md` | Optional recurring monitoring plan and change-tracking checklist; write a brief "not requested" note if ongoing monitoring is out of scope. |
| `/app/results/source_index.json` | Machine-readable list of source URLs, retrieval dates, competitor mappings, and evidence categories used in the analysis. |
| `/app/results/summary.md` | Executive summary of the research scope, key findings, recommendations, confidence level, and known gaps. |
| `/app/results/validation_report.json` | Structured validation report with stages, results, and `overall_passed`. |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Results directory | `/app/results` | Directory where all mandatory output files must be written. |
| Competitors | required | Two to five competitor names and websites supplied by the user. |
| Company context | required | The user's company, ICP, product category, positioning, and pricing context. |
| Focus areas | `everything` | Optional narrowed scope such as pricing, content, product, messaging, hiring, reviews, or social traction. |
| Depth | `quick_scan` | `quick_scan` for a bounded pass or `deep_dive` for comprehensive evidence collection. |
| Social scraping | `optional` | Use `APIFY_API_TOKEN` only when available and when the user asks for deeper Reddit, Twitter/X, or LinkedIn monitoring. |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| Web search | Yes | Find competitor pages, reviews, announcements, funding, launches, jobs, and current public signals. |
| Web fetch / browser access | Yes | Retrieve homepages, pricing pages, blogs, case studies, comparison pages, integrations, and careers pages. |
| `APIFY_API_TOKEN` | No | Optional deeper scraping for Reddit mentions, Twitter/X activity, and LinkedIn posts. |
| Markdown writer | Yes | Produce human-readable research outputs. |
| JSON writer | Yes | Produce `source_index.json` and `validation_report.json`. |

## Step 1: Environment Setup

1. Create the results directory and initialize empty working notes.
2. Confirm the user supplied two to five competitors, competitor websites when available, and the user's company context.
3. Confirm the research depth and focus areas. If any required input is missing, ask one concise clarification before starting research.
4. Check whether `APIFY_API_TOKEN` is available. Treat it as optional; never fail only because social scraping is unavailable.

```bash
mkdir -p /app/results
```

## Step 2: Intake

Ask for or confirm these inputs before collecting evidence:

1. Which competitors: two to five competitor names and websites.
2. User company context: what the user sells, ICP, positioning, pricing model, and known differentiators.
3. Focus areas: everything, pricing, content, product, messaging, hiring, reviews, social, or another explicit scope.
4. Depth: quick scan or deep dive.

Record the resolved scope at the top of `/app/results/summary.md`.

## Step 3: Competitor Profile Research

For each competitor, collect evidence across the following dimensions. Prefer primary sources first and label third-party claims clearly.

### Company Overview

- Homepage and about page: what they do and who they serve.
- Marketing copy and case studies: ICP and market focus.
- Pricing page: model, tiers, and visible price points.
- Funding and company size: search for funding, headcount, leadership, and recent company announcements.

### Product & Positioning

- Homepage hero and product pages: core value proposition and differentiators.
- Feature pages: major capabilities and integration claims.
- `/vs/`, `/alternatives/`, and comparison pages: how they frame alternatives.
- Recent launches: search for announcements and product updates from the last six months.

### Content & Marketing

- Blog or resources page: topics, formats, and approximate publishing frequency.
- LinkedIn and Twitter/X presence: activity level and engagement signals visible through web search or fetch.
- Content themes: recurring topics, target keywords, and funnel stage.
- Top-performing content: use available engagement indicators without overclaiming precision.

### Customer Evidence

- Customer logos and case studies from the competitor site.
- G2, Capterra, or similar review pages: rating, review count, common praise, and common complaints.
- Testimonials and quoted outcomes from marketing pages.

### Competitive Signals

- Competitors named by the competitor on comparison pages.
- Careers or jobs pages: hiring patterns and strategic signals.
- Partnerships, integrations, and ecosystem pages.
- Recent news, press, funding, and launch activity.

## Step 4: Optional Social Monitoring

Use Apify only when `APIFY_API_TOKEN` is available and the user requested deeper social evidence. Keep this step bounded to max 2 rounds per competitor: one collection round and one gap-fill round.

- Reddit: mentions of the competitor in relevant subreddits and discussion themes.
- Twitter/X: competitor account and founder or executive posts.
- LinkedIn: company, founder, CMO, or executive posts and visible engagement.

If Apify is unavailable, write a short limitation note and continue with web-search coverage.

## Step 5: Write Competitor Profiles

Write `/app/results/competitor_profiles.md` using this structure for each competitor:

```markdown
# Competitor Profile: [Company Name]
**Last updated:** [DATE]
**Website:** [URL]

## Overview
- **What they do:** [1-2 sentences]
- **ICP:** [who they sell to]
- **Stage:** [funding, headcount, or unknown]
- **Pricing:** [model and price points]

## Positioning
- **Value prop:** [their core claim]
- **Key differentiators:** [what they emphasize]
- **Positioning against us:** [how they frame the comparison, if known]

## Product
- **Core features:** [list]
- **Recent launches:** [last 6 months]
- **Integrations:** [key partners]

## Content & Marketing
- **Blog frequency:** [posts/month or observed cadence]
- **Top topics:** [themes]
- **Social activity:** [LinkedIn, Twitter/X, Reddit evidence]
- **Content strategy:** [dominant content type]

## Customer Evidence
- **Notable customers:** [logos or case studies]
- **G2/Capterra rating:** [score and review count]
- **Common praise:** [themes]
- **Common complaints:** [themes]

## Signals
- **Hiring:** [roles and implication]
- **Partnerships:** [recent partnerships]
- **News:** [recent announcements]

## Strengths & Weaknesses (vs. You)
### Where they're strong:
- [strength]

### Where they're weak:
- [weakness]

### Your opportunity:
- [gap to exploit]
```

## Step 6: Write Competitive Landscape Summary

Write `/app/results/competitive_landscape.md` with positioning, content, feature, takeaway, and recommended action sections. Include comparison tables for company claims, ICP focus, price point, differentiators, blog frequency, social presence, and feature coverage.

## Step 7: Ongoing Monitoring Plan

Write `/app/results/monitoring_plan.md`. If the user did not request recurring tracking, include a short note that monitoring was not requested and still provide a lightweight monthly checklist.

Monthly checks:

- Re-fetch competitor pricing pages and compare changes against the prior snapshot.
- Check new blog posts, resource themes, and comparison pages.
- Search for recent funding, product launches, customer announcements, and press.
- Review careers pages for hiring patterns.
- Update profiles with a "what changed" summary.

## Step 8: Source Index

Write `/app/results/source_index.json` with one entry per source consulted. Each entry should include competitor, URL, retrieval timestamp, category, and the claim supported.

## Step 9: Iterate on Evidence Gaps (max 3 rounds)

Run up to max 3 rounds of targeted gap filling before finalizing:

1. Check every competitor profile for missing pricing, ICP, positioning, customer evidence, and recent-news fields.
2. Prioritize gaps that change the recommendation or comparison tables.
3. Run focused searches or fetches for those gaps.
4. If a gap remains after 3 rounds or no reliable source exists, mark it `unknown` and explain the limitation in `/app/results/summary.md`.

## Final Checklist

Before finishing, verify that every mandatory output exists, is non-empty, and matches the requested scope. The run passes only when all required files are present and the validation report sets `overall_passed` correctly.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in   "$RESULTS_DIR/competitor_profiles.md"   "$RESULTS_DIR/competitive_landscape.md"   "$RESULTS_DIR/monitoring_plan.md"   "$RESULTS_DIR/source_index.json"   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python - <<'INNER_PY'
import json, pathlib
p = pathlib.Path('/app/results/validation_report.json')
print('PASS: validation_report.json parses' if p.exists() and isinstance(json.loads(p.read_text()).get('stages'), list) else 'FAIL: validation_report.json invalid')
INNER_PY
```

## Common Fixes

| Issue | Fix |
|---|---|
| Missing competitor website | Search the company name and confirm against official domain clues before using it. |
| Pricing not public | Mark pricing as `not publicly listed`; do not infer exact price points. |
| Review data unavailable | Use `unknown` and rely on customer pages, case studies, or public testimonials. |
| Social scraping unavailable | Continue with web-search evidence and note that structured social scraping was skipped. |
| Conflicting claims | Prefer primary sources, then recent reputable third-party sources; show the discrepancy when it affects conclusions. |

## Tips

Always separate observed evidence from interpretation. Use public source links for claims, avoid overclaiming social engagement precision, and label unknowns explicitly instead of filling gaps with guesses.
