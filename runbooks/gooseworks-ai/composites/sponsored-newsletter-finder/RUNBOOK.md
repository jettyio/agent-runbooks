---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/sponsored-newsletter-finder/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/sponsored-newsletter-finder
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Sponsored Newsletter Finder
  imported_at: '2026-05-03T02:34:48Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: sponsored-newsletter-finder
    confidence: high
secrets: null
---

# Sponsored Newsletter Finder — Agent Runbook

## Objective
Discover newsletters in a target niche that are relevant to the user's ideal customer profile, evaluate audience fit, estimate sponsorship cost, and produce a ranked shortlist ready for outreach. The runbook uses web research to identify candidate newsletters, scores each one against audience and sponsorship criteria, checks competitor sponsorship signals, and recommends a budget allocation for a small test campaign. It is best suited for teams with a defined ICP, a paid distribution budget, and a goal of testing newsletter sponsorships before committing more spend.

## REQUIRED OUTPUT FILES (MANDATORY)

Write all outputs to `/app/results` unless `output_path` explicitly points elsewhere.

| File | Description |
|---|---|
| `/app/results/newsletter-sponsors-<YYYY-MM-DD>.md` | Ranked sponsorship shortlist with tiers, scoring rationale, competitor findings, budget allocation, and outreach templates. |
| `/app/results/newsletter-sponsors-data.json` | Structured candidate data, source URLs, scores, estimates, and assumptions used in the shortlist. |
| `/app/results/summary.md` | Executive summary with ICP, budget, top recommendations, and caveats. |
| `/app/results/validation_report.json` | Programmatic validation report covering setup, research, scoring, output generation, and final file checks. |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Directory where required outputs are written. |
| `icp_definition` | required | Target role, industry, company size or stage, and buyer/user context. |
| `monthly_budget` | required | Approximate sponsorship budget, such as `$1,000-3,000/month`. |
| `geography` | `global` | Target geography for the audience. |
| `campaign_goal` | `awareness` | `awareness` or `direct_response`. |
| `known_newsletters` | none | Newsletters the user already knows or subscribes to; use as seeds. |
| `known_competitors` | none | Competitors to search for sponsorship signals. |
| `output_path` | `/app/results/newsletter-sponsors-<YYYY-MM-DD>.md` | Optional final markdown output path. |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Web search | Tool | Yes | Discover newsletters, sponsorship pages, directories, and competitor sponsorship evidence. |
| Markdown writer | Agent capability | Yes | Produce the final ranked shortlist. |
| JSON writer | Agent capability | Yes | Persist structured candidate data and validation results. |

## Step 1: Environment Setup

1. Create `results_dir` if it does not exist.
2. Resolve today's UTC date for output filenames.
3. Confirm `icp_definition` and `monthly_budget` are present before research begins.
4. If required inputs are missing, write `validation_report.json` with `overall_passed=false`, write `summary.md` explaining the missing inputs, and stop.

```bash
mkdir -p /app/results
python - <<'RUNBOOK_PY'
from pathlib import Path
Path('/app/results').mkdir(parents=True, exist_ok=True)
print('Environment ready')
RUNBOOK_PY
```

## Step 2: Intake

Capture the operating brief:

- ICP definition: title, industry, stage, company size, and buying context.
- Monthly budget range.
- Geography.
- Campaign goal: awareness or direct response.
- Known newsletters that can seed discovery.
- Known competitors that can seed competitive intelligence.

Normalize the brief into a short search profile and save it in `newsletter-sponsors-data.json` under `inputs`.

## Step 3: Discovery via Web Search

Run searches from multiple angles and collect candidates with source URLs:

```text
"[ICP industry] newsletter" sponsorship
"[ICP role] newsletter" site:substack.com OR site:beehiiv.com
"best newsletters for [ICP role/industry]"
"[ICP industry] newsletter" "advertise" OR "sponsor"
"[competitor company] newsletter sponsorship"
newsletter directory "[ICP industry]"
```

Also inspect newsletter directories and sponsorship marketplaces when relevant: `newsletter.directory`, `paved.com`, `swapstack.co`, and `sparkloop.co`.

For each candidate, collect newsletter name, URL, sponsorship page URL, subscriber count if available, audience description, send frequency, pricing or CPM if available, and evidence URLs. Keep at least 8 candidates when search results allow it; if fewer than 8 credible candidates exist, explain why in `summary.md`.

## Step 4: Evaluate Each Newsletter

Score every candidate across five dimensions from 1 to 5:

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Audience match | Unrelated audience | Partial overlap | Direct ICP match |
| Reach | Under 1,000 subscribers | 5,000-20,000 subscribers | 20,000+ subscribers |
| Engagement | No open-rate data | About 30-40% open rate | 40%+ open rate |
| Niche specificity | Generic business newsletter | Industry newsletter | Role-specific newsletter |
| Sponsor accessibility | No sponsor info found | Inquiry required | Clear pricing or marketplace listing |

Compute `total_score` out of 25. Shortlist newsletters scoring 15 or higher, place scores 20-25 in Tier 1, scores 15-19 in Tier 2, and scores 10-14 in Tier 3 watchlist.

When pricing is not published, estimate from these benchmarks and mark the estimate clearly:

| Segment | Subscriber count | Estimated sponsorship rate |
|---|---:|---:|
| Micro | Under 5,000 | $50-150 flat rate |
| Small | 5,000-20,000 | $100-500 flat rate |
| Mid | 20,000-50,000 | $500-2,000 flat rate |
| Large | 50,000+ | $1,000-10,000 flat rate |

## Step 5: Competitive Intelligence

For each known competitor, search for newsletter sponsorship evidence:

```text
"[competitor name]" "sponsored by" newsletter
"[competitor name]" advertisement site:substack.com
"[competitor name]" "presented by" newsletter
```

If a competitor is sponsoring a candidate newsletter, mark it as validated audience fit and include the evidence in the final report. Do not inflate the numeric score unless the evidence also supports the scoring criteria.

## Step 6: Budget Allocation Recommendation

Build a monthly test plan that fits the declared budget and campaign goal. Prefer a small validation test before broad rollout. Include a table with newsletter, send frequency, cost per send, planned sends per month, and monthly cost. State the recommended first test and the measurement assumption, such as demo requests, signups, or qualified traffic.

## Step 7: Generate Outputs

Write the final markdown report to `/app/results/newsletter-sponsors-<YYYY-MM-DD>.md` using this structure:

```markdown
# Newsletter Sponsorship Shortlist — [DATE]
ICP: [description] | Budget: [range] | Goal: [awareness/direct response]

## Tier 1 — High Priority (Score 20-25)

### 1. [Newsletter Name]
- **URL:** [url]
- **Subscribers:** [N] ([source or estimated])
- **Open rate:** [X%] (disclosed or estimated)
- **Audience:** [description]
- **Send frequency:** [weekly/daily/etc]
- **Sponsorship type:** [dedicated/classified/banner mention]
- **Estimated cost:** $[X] per send
- **Estimated CPM:** $[X]
- **Past sponsors:** [list or none found]
- **Score:** [X/25]
- **Fit rationale:** [1-2 sentences]
- **Sponsor page:** [url or inquiry required]

## Tier 2 — Worth Testing (Score 15-19)

## Tier 3 — Watchlist (Score 10-14)

## Where Competitors Are Already Advertising

## Budget Allocation Recommendation

## Outreach Templates
```

Also write `/app/results/newsletter-sponsors-data.json`, `/app/results/summary.md`, and `/app/results/validation_report.json`.

## Step 8: Iterate on Errors (max 3 rounds)

If validation fails or output quality is incomplete, perform up to max 3 rounds of targeted repair:

| Issue | Fix |
|---|---|
| Required output missing | Regenerate that output from the structured candidate data. |
| Fewer than 5 candidates found | Run two additional query angles and document scarcity if still low. |
| No source URLs | Revisit each candidate and add evidence URLs or remove unsupported candidates. |
| Budget table exceeds budget | Reduce sends or move a candidate to the watchlist. |
| Scores lack rationale | Add one concise evidence-backed rationale per score. |

After each round, rerun the final verification script. Stop after max 3 rounds and report any residual issues in `summary.md`.

## Step 9: Final Checklist

Run this verification script before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in   "$RESULTS_DIR/newsletter-sponsors-$(date -u +%Y-%m-%d).md"   "$RESULTS_DIR/newsletter-sponsors-data.json"   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python - <<'VERIFY_PY'
import json, pathlib
report = json.loads(pathlib.Path('/app/results/validation_report.json').read_text())
if report.get('overall_passed'):
    print('PASS: validation_report overall_passed=true')
else:
    print('FAIL: validation_report overall_passed is not true')
VERIFY_PY
```

Checklist:

- [ ] Intake includes ICP, budget, geography, and campaign goal.
- [ ] Discovery includes source URLs for each candidate.
- [ ] Every candidate has a 5-dimension score and total score.
- [ ] Tier 1, Tier 2, and watchlist sections are present when candidates qualify.
- [ ] Budget allocation fits within the supplied monthly budget or explains the gap.
- [ ] Outreach templates are included.
- [ ] `summary.md` and `validation_report.json` are present.
- [ ] Verification script prints PASS for every required file.

## Common Fixes

| Issue | Fix |
|---|---|
| Search results are too broad | Add role, industry, and geography terms to each query. |
| Pricing is unavailable | Estimate from subscriber-count benchmarks and label as estimated. |
| Audience fit is unclear | Prefer newsletters with explicit reader descriptions, media kits, or sponsor pages. |
| Competitor evidence is missing | State that no public sponsorship evidence was found; do not invent validation. |

## Tips

Prefer narrow, role-specific newsletters over generic business publications when the campaign goal is direct response. Treat undisclosed pricing, subscriber counts, and open rates as assumptions, and preserve the evidence URLs so a marketer can verify before outreach.
