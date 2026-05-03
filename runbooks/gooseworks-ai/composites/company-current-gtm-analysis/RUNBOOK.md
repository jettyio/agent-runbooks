---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/company-current-gtm-analysis/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/company-current-gtm-analysis
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Company Current GTM Analysis
  imported_at: '2026-05-03T02:45:17Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: company-current-gtm-analysis
    confidence: high
secrets:
---

# Company Current GTM Analysis — Agent Runbook

## Objective

Perform a comprehensive current-state GTM analysis for a target company. The runbook researches visible activity across content, founder activity, SEO, hiring, social and community, acquisition channels, podcasts, review sites, competitive positioning, and partnerships. It produces a structured report that identifies what is working, what is missing, and where whitespace exists for new strategy.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/company_current_gtm_analysis.md` | Final evidence-backed GTM analysis report for the target company |
| `/app/results/summary.md` | Executive summary of the run, assumptions, and major findings |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Output directory where required files are written |
| `company_name` | required | Name of the target company to analyze |
| `company_url` | optional | Canonical company website, if known |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Web research access | External | Yes | Required to collect current public GTM evidence |
| Markdown writer | Agent capability | Yes | Required to produce the final report |
| JSON writer | Agent capability | Yes | Required to produce validation output |

## Step 1: Environment Setup

Validate the run context before performing research.

```bash
python - <<'INNER_PY'
import os, pathlib
results = pathlib.Path('/app/results')
results.mkdir(parents=True, exist_ok=True)
if not os.environ.get('COMPANY_NAME'):
    print('COMPANY_NAME may also be supplied interactively in the agent prompt')
print('Environment ready')
INNER_PY
```

## Step 2: Resolve Company Scope

Identify the target company's canonical website, core product categories, primary customer segments, and market category. Record assumptions in `research_notes.md` before collecting channel evidence.

## Step 3: Research Current GTM Channels

Analyze the company's current go-to-market activity across content and blog, founder and executive LinkedIn activity, SEO and traffic signals, hiring signals, social and community presence, acquisition channels, podcasts, review sites, competitive positioning, and partnerships. Use current public sources, retain source URLs, and separate observed facts from interpretation.

## Step 4: Synthesize Gaps And White Space

Compare the evidence across channels and identify what appears to be working, what is missing, and where a differentiated GTM strategy could fill genuine whitespace. Keep recommendations grounded in the evidence gathered in Step 3.

## Step 5: Write Final GTM Report

Create `/app/results/company_current_gtm_analysis.md` with an executive summary, channel-by-channel findings, evidence table, inferred strengths, missing motions, whitespace opportunities, and recommended next experiments.

## Step 6: Iterate on Errors (max 3 rounds)

If required outputs are missing, source evidence is thin, or findings are unsupported, perform up to max 3 rounds of targeted repair. Each round must update the report or validation output and note what changed.

### Common Fixes

| Issue | Fix |
|---|---|
| Company identity is ambiguous | Add an assumptions section and verify the canonical website before analysis |
| A GTM channel has no evidence | State that no current evidence was found and include the search/source path used |
| Recommendations repeat existing activity | Re-check the channel evidence and focus on gaps or underused motions |
| Output file missing | Recreate the file under `/app/results` and rerun final verification |

## Step 7: Final Checklist

Run this verification script before finishing.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in   "$RESULTS_DIR/company_current_gtm_analysis.md"   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

## Source Skill Structure

The imported skill included these source sections, preserved here as implementation guidance:

- **Quick Start**: Or if a client context file already exists:
- **Inputs**: | Input | Required | Source | |-------|----------|--------| | **Company name** | Yes | User provides or read from `clients/<client>/context.md` | | **Company website** | Yes | User provides or read from context | | **Founder/exec LinkedIn URLs** | Recommended | User provides, or search web for "[founder name] LinkedIn" | | **Known competitors** | Optional | Improves competitive positioning section | | **Client contex
- **Phase 1: Load Context**: 1. If a client context file exists at `clients/<client>/context.md`, read it for: - Company overview, founders, product, pricing - Known competitors, customers, market positioning - Any existing research or intelligence 2. If no context file exists, gather basics from the user: - Company name, website URL - Founder names and LinkedIn URLs (if known) - Industry/category - Known competitors (if any) 3. Create the outpu
- **Phase 2: Data Collection (Run in Parallel)**: Run as many of these research threads as possible in parallel. Each thread is independent.
- **2A. Blog & Content Strategy**: **Goal:** Understand their content strategy — topics, frequency, types, target audience, gaps. 1. **Fetch the blog page:** - WebFetch `<website>/blog` — extract all visible post titles, dates, categories, authors - If no `/blog`, try `/resources`, `/insights`, `/news`, `/articles` - Note: Many sites are JS-rendered. If WebFetch returns empty content, fall back to WebSearch: `site:<website> blog` 2. **Catalog content 
- **2B. Founder/Exec LinkedIn Activity**: **Goal:** Understand founder thought leadership presence, posting frequency, engagement, topics. **Requires:** Founder LinkedIn profile URLs. If not provided, search: `"<founder name>" LinkedIn <company>` 1. **Scrape recent posts:** 2. **Analyze the posts:** - Posting frequency (daily/weekly/monthly/rarely) - Content type breakdown: original posts vs. reposts vs. articles - Topics covered (product, industry, personal
- **2C. SEO & Web Traffic**: **Goal:** Estimate traffic, identify traffic sources, assess SEO investment level. 1. **Get traffic data:** - WebSearch: `<website> traffic site visitors similarweb` - WebFetch: `https://www.similarweb.com/website/<domain>/` (may or may not return data) - Look for: monthly visits, bounce rate, pages/visit, traffic sources, top countries 2. **Assess keyword strategy:** - WebSearch: `site:<website>` to see indexed page
- **2D. Hiring & Team Signals**: **Goal:** Understand team composition, growth trajectory, and strategic priorities from hiring patterns. 1. **Check careers page:** - WebFetch: `<website>/careers` or `<website>/jobs` - If JS-rendered, WebSearch: `<company> careers open positions <current year>` - Also check: Glassdoor, LinkedIn Jobs, Greenhouse (`boards.greenhouse.io/<company>`), Lever (`jobs.lever.co/<company>`) 2. **Catalog open roles by departmen
- **2E. Social Media & Community Presence**: **Goal:** Map their presence and activity level across every relevant channel. 1. **Twitter/X:** - WebSearch: `<company> Twitter OR X.com` - Find their handle, follower count, posting frequency - What do they post? (Product updates, industry commentary, engagement with community) 2. **Reddit:** - WebSearch: `"<company name>" OR "<product name>" site:reddit.com` - What are people saying? Positive/negative/neutral? - I
- **2F. Customer Acquisition & Reviews**: **Goal:** Understand how they get customers and what customers think. 1. **Review sites:** - WebSearch: `<company> OR <product> review G2 Capterra <current year>` - WebFetch G2/Capterra pages if URLs are findable - Note: rating, review count, common praise, common complaints - Optional: use `review-site-scraper` skill for detailed extraction 2. **Customer logos and case studies:** - WebFetch: `<website>/customers` or

## Tips

Use current source evidence for every substantive claim, distinguish missing evidence from negative proof, and make recommendations only after mapping what the company already appears to be doing.
