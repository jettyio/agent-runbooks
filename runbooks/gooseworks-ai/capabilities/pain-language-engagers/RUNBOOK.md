---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/pain-language-engagers/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/pain-language-engagers
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Pain-Language Engagers
  imported_at: '2026-05-03T02:53:29Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: pain-language-engagers
    confidence: high
secrets:
  APIFY_API_TOKEN:
    env: APIFY_API_TOKEN
    description: Apify API token used by the LinkedIn scraping actors
    required: true
---

# Pain-Language Engagers — Agent Runbook

## Objective
Find warm LinkedIn leads by searching for pain-language posts, extracting people who authored, reacted to, or commented on those posts, enriching their profiles, and filtering them against the user's ICP. The runbook starts with intake so the search terms reflect how operators describe the problem in their own words, not how vendors market a solution. It then builds a client config, runs the source pipeline in test mode first, reviews quality with the user, iterates when needed, and exports a qualified CSV lead list.

## REQUIRED OUTPUT FILES (MANDATORY)

All outputs MUST be written under `/app/results` unless an orchestrator supplies a different `results_dir`.

| File | Description |
|---|---|
| `/app/results/summary.md` | Executive summary of intake, search strategy, run settings, result counts, and follow-up notes |
| `/app/results/validation_report.json` | Structured validation results for setup, config generation, test run, full run, and output verification |
| `/app/results/client_config.json` | Approved client-specific pain-language, ICP, vendor-exclusion, company-page, and run-limit configuration |
| `/app/results/keyword_plan.md` | Human-readable pain-language keyword plan presented for approval before scraping |
| `/app/results/test_results_summary.md` | Test-mode result review, including relevance notes and recommended refinements |
| `/app/results/leads.csv` | Final deduplicated lead export with ICP tier and source engagement metadata |

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `results_dir` | `/app/results` | Directory where all required outputs are written |
| `client_name` | required | Slug used for config and CSV naming |
| `product_description` | required | One-sentence description of the product or service |
| `pain_context` | required | Description of the operational pain and day-to-day workaround without the product |
| `icp_industries` | required | Target industries or verticals for ICP filtering |
| `icp_titles` | required | Buyer and operator titles to prioritize |
| `excluded_titles_or_vendors` | optional | Titles, competitors, and vendor terms to classify as Tech Vendor or exclude |
| `geographic_focus` | `United States` | Country or region filter for enriched profiles |
| `linkedin_company_pages` | optional | Known company or publication pages where the ICP is likely to engage |
| `days_back` | `60` | Recency window for LinkedIn posts |
| `max_posts_per_keyword` | `50` | Maximum keyword-search posts per pain keyword |
| `max_posts_per_company` | `100` | Maximum company-page posts to inspect |
| `run_full_pipeline` | `false` | When false, stop after the mandatory test run and review |

## Dependencies

| Dependency | Required | Purpose |
|---|---:|---|
| `python3` | Yes | Runs the source pipeline script |
| `skills/pain-language-engagers/scripts/pain_language_engagers.py` | Yes | LinkedIn scraping, enrichment, ICP classification, deduplication, and CSV export |
| `APIFY_API_TOKEN` | Yes | Authenticates Apify actors used by the pipeline |
| `apimaestro/linkedin-posts-search-scraper-no-cookies` | Yes | Searches LinkedIn posts by pain-language keyword |
| `harvestapi/linkedin-company-posts` | Yes | Scrapes company-page posts and engagers |
| `harvestapi/linkedin-profile-scraper` | Yes | Enriches LinkedIn profiles with headline and location |
| `jq` | Recommended | Validates generated config JSON in shell checks |

## Step 1: Environment Setup

Verify the source pipeline and credentials before generating keywords or spending Apify credits.

```bash
set -euo pipefail
RESULTS_DIR="${RESULTS_DIR:-/app/results}"
mkdir -p "$RESULTS_DIR"

if [ -z "${APIFY_API_TOKEN:-}" ]; then
  echo "ERROR: APIFY_API_TOKEN is not set" >&2
  exit 1
fi

if [ ! -f skills/pain-language-engagers/scripts/pain_language_engagers.py ]; then
  echo "ERROR: source pipeline script not found at skills/pain-language-engagers/scripts/pain_language_engagers.py" >&2
  exit 1
fi

python3 --version
python3 skills/pain-language-engagers/scripts/pain_language_engagers.py --help >/tmp/pain_language_engagers_help.txt || true
```

Record setup status in `/app/results/validation_report.json`. If a required dependency or secret is missing, stop and write `/app/results/summary.md` with the blocker.

## Step 2: Intake and Pain Context

Ask the user for product, ICP, and LinkedIn signal-source context before running any scraping. Present the questions as a numbered list and tell the user to answer what is relevant and skip what is not.

### Product & Pain Context

1. What does your product or service do in one sentence?
2. What specific problem does it solve, and who feels this pain most acutely?
3. What does the ICP's day-to-day look like without your product, including frustrations, workarounds, and manual processes?
4. What phrases would someone use when complaining about this problem on LinkedIn?

### ICP Definition

5. What industries or verticals are your target buyers in?
6. What job titles or roles are ideal buyers?
7. What titles should be excluded?
8. Which competitors or vendor categories should be filtered out?
9. What geographic focus should be used?

### LinkedIn Signal Sources

10. Which LinkedIn company pages, publications, communities, competitors, or creators does the ICP follow or engage with?
11. Are there specific posts or creators that are known to attract the ICP?

Write the accepted intake notes into `/app/results/summary.md`.

## Step 3: Generate Pain-Language Keywords

Generate roughly 15 to 25 LinkedIn boolean-search keywords from the intake. Organize them into staffing/resource pain, operational friction, margin/growth pain, and process complaints. Every keyword should read like something a frustrated operator would type or say.

Also generate ICP keywords, tech-vendor exclusion terms, pain-pattern regexes, broad topic patterns, and hardcoded company pages. Present the plan in `/app/results/keyword_plan.md` and ask for approval before running the scraper.

Use this config shape when writing `/app/results/client_config.json`:

```json
{
  "client_name": "example-client",
  "pain_keywords": ["\"can't find X\"", "\"hiring Y\" problems"],
  "pain_patterns": ["can.t find X", "hiring Y", "manual.*process"],
  "icp_keywords": ["industry-term-1", "industry-term-2"],
  "tech_vendor_keywords": ["software engineer", "competitor-name"],
  "hardcoded_companies": ["https://www.linkedin.com/company/example/"],
  "industry_pages": ["https://www.linkedin.com/company/example/"],
  "broad_topic_patterns": ["industry", "sector", "niche-term"],
  "country_filter": "United States",
  "days_back": 60,
  "max_posts_per_keyword": 50,
  "max_posts_per_company": 100
}
```

Validate the JSON before continuing:

```bash
python3 -m json.tool /app/results/client_config.json >/tmp/client_config.validated.json
```

## Step 4: Run Test Pipeline

Always run a bounded test before a full run. Test mode limits keyword and company-page volume so the user can validate relevance without unnecessary spend.

```bash
python3 skills/pain-language-engagers/scripts/pain_language_engagers.py   --config /app/results/client_config.json   --test
```

After the test completes, write `/app/results/test_results_summary.md` with ICP breakdown, top likely leads, filtered-out examples, keyword performance, and relevance issues.

## Step 5: Review and Refine

Present the test results to the user and ask whether to adjust keywords, ICP terms, vendor exclusions, company pages, geography, or date range. Common fixes are listed below.

| Issue | Common Fix |
|---|---|
| Too many Tech Vendor results | Add vendor names, builder terms, and technical titles to `tech_vendor_keywords` |
| Missing obvious ICP leads | Add industry terms, buyer titles, and niche vocabulary to `icp_keywords` |
| Irrelevant posts | Tighten `pain_patterns` and remove broad solution-language keywords |
| Not enough results | Add more pain keywords, add relevant company pages, or expand `days_back` |

Repeat this refinement loop for max 3 rounds. After each round, rewrite `/app/results/client_config.json`, rerun Step 4, and update `/app/results/test_results_summary.md`.

## Step 6: Run Full Pipeline

Run the full pipeline only after test results are relevant and the user approves. If `run_full_pipeline=false`, stop after writing the summary and validation report, noting that no full CSV was requested.

```bash
python3 skills/pain-language-engagers/scripts/pain_language_engagers.py   --config /app/results/client_config.json
```

Move or copy the generated CSV to `/app/results/leads.csv`. The CSV must include: Name, LinkedIn Profile URL, Role, Company Name, Location, Source Page, Post URLs, Engagement Type, Comment Text, ICP Tier, and Niche Keyword.

## Step 7: Iterate on Errors (max 3 rounds)

If setup, config validation, the test run, the full run, or output verification fails, inspect the error, apply the smallest targeted fix, and rerun the failed stage. Stop after max 3 rounds and write the remaining blocker into `/app/results/summary.md` and `/app/results/validation_report.json`.

## Step 8: Write Reports

Write `/app/results/summary.md` with the run date, client name, approved keyword strategy, config path, test-run observations, full-run status, final lead count, and manual follow-up. Write `/app/results/validation_report.json` with stage-level pass/fail results and output file paths.

## Final Checklist

Run this verification before finishing.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="${RESULTS_DIR:-/app/results}"
for f in   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"   "$RESULTS_DIR/client_config.json"   "$RESULTS_DIR/keyword_plan.md"   "$RESULTS_DIR/test_results_summary.md"   "$RESULTS_DIR/leads.csv"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

Checklist:

- [ ] Intake was captured before keyword generation
- [ ] `/app/results/client_config.json` exists and parses as JSON
- [ ] `/app/results/keyword_plan.md` was approved before scraping
- [ ] Test mode ran before any full run
- [ ] User-visible review included ICP breakdown, top likely leads, filtered-out examples, and keyword performance
- [ ] `/app/results/leads.csv` exists after a full approved run, or the summary states why the full run was intentionally skipped
- [ ] `/app/results/summary.md` and `/app/results/validation_report.json` are non-empty

## Tips

Search for pain-language, not solution-language. Phrases such as `can't find drivers`, `check calls are killing us`, or `spending hours on manual data entry` are stronger signals than vendor terms such as `AI automation` or `workflow optimization`.
