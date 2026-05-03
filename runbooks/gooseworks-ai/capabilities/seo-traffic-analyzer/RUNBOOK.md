---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/seo-traffic-analyzer/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/seo-traffic-analyzer
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: SEO & Traffic Analyzer
  imported_at: '2026-05-03T02:54:05Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: seo-traffic-analyzer
    confidence: high
secrets: null
---

# SEO and Traffic Analyzer - Agent Runbook

## Objective

Analyze a website's SEO visibility, keyword rankings, traffic estimates, and competitive positioning. Uses web search probes, SimilarWeb (free tier via web), and site: queries to build an SEO profile without requiring paid tool subscriptions. Useful for competitive intel, gap analysis, and reverse-engineering a company's organic acquisition strategy. This runbook turns that workflow into a Jetty programmatic-evaluation task that produces repeatable SEO findings, supporting observations, and validation metadata. The agent should rely on public web search, fetched pages, and transparent estimates, and it should clearly distinguish directly observed evidence from inference.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|------|-------------|
| `/app/results/seo_traffic_report.md` | Final SEO and traffic analysis for the target domain, including keyword, content, and competitor findings. |
| `/app/results/raw_observations.json` | Structured evidence gathered during the run, including queries, URLs, observations, and confidence notes. |
| `/app/results/summary.md` | Executive summary of the analysis, key recommendations, and notable caveats. |
| `/app/results/validation_report.json` | Structured validation report covering setup, evidence gathering, analysis, and final output checks. |

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| results_dir | No | `/app/results` | Directory where all required output files are written. |
| target-domain | Yes | — | Domain to analyze (e.g., "pump.co") |
| competitor-domains | No | none | Comma-separated competitor domains to compare |
| target-keywords | No | auto-inferred | Keywords to check rankings for |
| output-path | No | stdout | Where to save the analysis |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Web search | Tool | Yes | Run public search probes, including `site:` queries and keyword checks. |
| Web fetch | Tool | Yes | Fetch public pages for validation and content inspection. |
| Python 3.12 | Runtime | No | Useful for normalizing structured observations and validation metadata. |
| SimilarWeb public web pages | External site | No | Optional free-tier traffic and market context when accessible. |

## Step 1: Environment Setup

1. Create `/app/results` if it does not exist.
2. Resolve the target domain and normalize it to a registrable domain without protocol or path.
3. Initialize `/app/results/raw_observations.json` with arrays for `queries`, `pages`, `competitors`, `keywords`, and `caveats`.
4. If a required target domain is missing, write `validation_report.json` with `overall_passed=false` and stop.

## Step 2: Gather Search Evidence

Run the source skill's search probes and record every query, result URL, observation, and timestamp in `raw_observations.json`.

### SEO & Traffic Analyzer

Analyze a website's organic search visibility, estimate traffic, and map competitive positioning — all without paid SEO tool subscriptions. Uses web search probes, public data sources, and site: queries to build a comprehensive SEO profile.

##### Phase 1: Site Indexation & Structure

Assess the site's SEO footprint using site: queries.

**Searches to run:**
- `site:[domain]` — Estimate total indexed pages
- `site:[domain] blog` — Find blog content
- `site:[domain] intitle:` — See page title patterns
- `site:[domain]/pricing` or `site:[domain]/features` — Key conversion pages
- `site:[domain] filetype:pdf` — Whitepapers, guides (content marketing signal)

**What to extract:**
- Approximate number of indexed pages
- Content categories (blog, docs, landing pages, comparison pages)
- URL structure patterns
- Presence of key conversion pages (pricing, demo, signup)

##### Phase 2: Keyword Ranking Probes

Check where the target ranks for important keywords. For each keyword:

**Technique:** Run a WebSearch for the keyword and scan results for the target domain.

**Standard keyword categories to check:**

##### Phase 3: Traffic Estimation

Gather traffic signals from multiple sources:

##### Phase 4: Backlink & Authority Signals

Estimate domain authority through proxy signals:

- **Who links to them?** WebSearch: `"[domain]" -site:[domain]` and categorize sources
- **Press mentions:** WebSearch: `"[company name]" (TechCrunch OR VentureBeat OR Forbes OR "Business Insider")`
- **Industry recognition:** WebSearch: `"[company name]" (award OR "named" OR "recognized" OR "leader")`
- **Directory presence:** Check for listings on G2, Capterra, Product Hunt, AlternativeTo, AWS Marketplace

##### Phase 5: Competitive Comparison

For each competitor domain, repeat a subset of the above analysis:

- `site:[competitor]` — Indexed pages count
- Check the same target keywords — who ranks where?
- Compare content strategies (blog frequency, topics)

Build a comparison matrix:

| Keyword | [Target] Position | [Competitor 1] | [Competitor 2] | ... |
|---------|-------------------|-----------------|-----------------|-----|

##### Phase 6: Content Gap Analysis

Identify keywords and topics where competitors rank but the target doesn't:

- For each competitor, run: `site:[competitor] [keyword]` for keywords where target is absent
- WebSearch for `[category] + [topic]` and note which competitors appear but target doesn't
- Identify high-value content types competitors have that target lacks:
  - Comparison pages ("X vs Y")
  - Use case pages
  - ROI calculators / interactive tools
  - Integration pages
  - Customer stories / case studies
  - Glossary / educational content

##### Phase 7: Output

Generate a comprehensive SEO report:

```markdown

### SEO & Traffic Analysis: [domain]

**Date:** YYYY-MM-DD
**Competitors analyzed:** [list]

#### Executive Summary

[2-3 sentence overview of SEO posture]

#### Site Indexation

- Estimated indexed pages: X
- Content categories: [list]
- Key pages: [list]

##### Brand Keywords

| Keyword | Position | URL | Notes |
|---------|----------|-----|-------|

##### Category Keywords

| Keyword | Position | URL | Top Competitors |
|---------|----------|-----|-----------------|

##### Problem Keywords

| Keyword | Position | URL | Top Competitors |
|---------|----------|-----|-----------------|

#### Traffic Estimates

- Estimated monthly visits: X
- Top traffic sources: [organic, direct, referral, social, paid]
- Geographic breakdown: [if available]

#### Competitive Comparison

| Metric | [Target] | [Comp 1] | [Comp 2] | ... |
|--------|----------|----------|----------|-----|
| Indexed pages | | | | |
| Blog posts (est.) | | | | |
| Ranks for X keywords | | | | |

#### Content Gaps & Opportunities

1. [Gap 1]: Competitors rank for X but target doesn't
2. [Gap 2]: No comparison pages exist
3. [Gap 3]: Missing content type

#### Recommendations

1. [Priority action 1]
2. [Priority action 2]
...
```

#### Tips

- **Run quarterly** per client to track SEO progress
- **Brand keyword monitoring** is especially important — if competitors bid on your brand, you'll see it
- **Content gap analysis** directly feeds into content strategy recommendations
- **Comparison pages** are often the highest-ROI SEO content for B2B SaaS
- **This skill works without paid tools** but results from tools like Ahrefs/SEMrush will be more precise. If you have access to those, supplement this analysis with their data.
- **Combine with `industry-scanner`** to correlate SEO gaps with industry trends
- **SimilarWeb free tier** is rate-limited — if blocked, fall back to other estimation methods

#### Limitations

- Traffic estimates are rough approximations without paid tools
- Exact keyword positions can't be determined — only presence/absence on page 1
- Backlink analysis is limited to what's discoverable via web search
- Results may vary by geography and personalization

#### AI Agent Integration

When using this skill as an agent:

1. User provides target domain, optional competitors, optional keywords
2. Agent auto-infers relevant keywords from the domain's content if not provided
3. Agent runs all phases, collecting data into a structured report
4. Agent highlights the most actionable findings
5. User decides which gaps to address
6. Agent can chain to content creation or `sponsored-newsletter-finder` for distribution

**Example prompt:**
> "Analyze pump.co's SEO. Compare against vantage.sh, antimetal.com, prosperops.com. Check if they rank for cloud cost optimization keywords."

## Step 3: Analyze Rankings and Content

For each target keyword, search for the keyword with and without the brand name. Record whether the target domain appears in visible results, which competitors appear, and what content type is ranking. Treat ranking position as approximate unless an exact search result position is directly visible.

## Step 4: Compare Competitors

For every competitor domain provided, repeat the core indexation checks and compare indexed footprint, visible content themes, conversion pages, and apparent positioning. Keep comparisons evidence-backed and cite the query or fetched page that supports each claim.

## Step 5: Generate Outputs

Write `/app/results/seo_traffic_report.md` with sections for overview, indexation footprint, keyword visibility, traffic estimate context, competitor comparison, content gaps, recommendations, and caveats. Write `/app/results/summary.md` as a concise executive summary for decision makers.

## Step 6: Validate Evidence

Check that every material claim in the report is backed by an entry in `raw_observations.json`. If evidence is weak, downgrade the confidence label instead of overstating the conclusion.

## Step 7: Iterate on Errors (max 3 rounds)

If validation fails, perform at most 3 rounds of targeted fixes: gather the missing evidence, revise unsupported claims, regenerate the affected output file, and rerun validation.

## Common Fixes

| Issue | Fix |
|-------|-----|
| Missing target domain | Ask for or resolve a single domain before gathering evidence. |
| Unsupported ranking claim | Add the query and observed result evidence, or mark the claim as an estimate. |
| Traffic data unavailable | State that public traffic data was not available and rely on indexation and competitive proxies. |
| Output file missing | Regenerate the file and rerun the final checklist. |

## Final Checklist

Run this verification script before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/seo_traffic_report.md" \
  "$RESULTS_DIR/raw_observations.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

The run is complete only when every required output file exists, is non-empty, and `validation_report.json` reports `overall_passed=true`.

## Tips

- Prefer public, reproducible observations over opaque SEO estimates.
- Preserve the exact search query text used for each finding.
- Make confidence labels explicit when inferring traffic or competitive strength from proxies.
