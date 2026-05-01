---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/client-onboarding/SKILL.md"
  source_host: "github.com"
  source_title: "Client Onboarding"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    source_collection: "playbooks"
    skill_name: "client-onboarding"
    confidence: "high"
secrets: {}
---

# Client Onboarding — Agent Runbook

## Objective

Run the full onboarding playbook for a new client. This runbook orchestrates three phases of work: intelligence gathering (parallel deep research across company, competitors, founders, SEO, AEO, paid ads, industry, and GTM), synthesis of all research into a Client Intelligence Package, and generation of prioritized Growth Strategy Recommendations. By the end of a successful run the agent has produced a complete Client Intelligence Package and a set of P0/P1/P2 growth strategies tagged with machine-readable execution metadata, ready for human review before implementation.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to the client folder.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `clients/<client-name>/context.md` | Running context for the client populated during research |
| `clients/<client-name>/intelligence/company-research.md` | Phase 1 Step 1 output: company deep research |
| `clients/<client-name>/intelligence/competitor-research.md` | Phase 1 Step 2 output: competitor deep research |
| `clients/<client-name>/intelligence/founder-research.md` | Phase 1 Step 3 output: founder research |
| `clients/<client-name>/intelligence/seo-content-audit.md` | Phase 1 Step 4 output: SEO content audit |
| `clients/<client-name>/intelligence/aeo-visibility.md` | Phase 1 Step 5 output: AEO visibility check |
| `clients/<client-name>/intelligence/ad-strategy.md` | Phase 1 Step 6 output: paid ads strategy review |
| `clients/<client-name>/intelligence/industry-scan.md` | Phase 1 Step 7 output: industry intelligence scan |
| `clients/<client-name>/intelligence/gtm-analysis.md` | Phase 1 Step 8 output: current GTM analysis |
| `clients/<client-name>/intelligence-package.md` | Phase 2 output: synthesized Client Intelligence Package |
| `clients/<client-name>/growth-strategies.md` | Phase 3 output: prioritized growth strategies with execution tags |
| `/app/results/summary.md` | Executive summary of run result, issues, and next steps |
| `/app/results/validation_report.json` | Structured validation results with stages and `overall_passed` |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for meta-outputs |
| `company-name` | *(required)* | Name of the client company being onboarded |
| `company-url` | *(required)* | Website URL of the client company |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Web search | Tool | Yes | Used in Phase 1 for company, competitor, and founder research |
| Web fetch | Tool | Yes | Used to retrieve pages and profiles during research |
| `seo-content-audit` skill | Sub-skill | Yes | Orchestrates site-content-catalog + seo-domain-analyzer + brand-voice-extractor |
| `aeo-visibility` skill | Sub-skill | Yes | Tests AI answer-engine visibility for key queries |
| `meta-ad-scraper` skill | Sub-skill | Yes | Scrapes active Meta ads for client and competitors |
| `google-ad-scraper` skill | Sub-skill | Yes | Scrapes active Google ads for client and competitors |
| `industry-scanner` skill | Sub-skill | Yes | Scans recent industry news and activity |
| `company-current-gtm-analysis` skill | Sub-skill | Yes | Scores the client's current GTM across all dimensions |
| `linkedin-profile-post-scraper` skill | Sub-skill | Yes | Scrapes LinkedIn profiles and posts for founder research |
| `docs/growth-frameworks.md` | Internal doc | Recommended | Reference framework for Phase 2 synthesis |

---

## Step 1: Environment Setup

Validate inputs and create the client folder structure before beginning any research.

```bash
echo "=== CLIENT ONBOARDING SETUP ==="

# Required inputs
if [ -z "${COMPANY_NAME}" ]; then echo "ERROR: COMPANY_NAME is not set"; exit 1; fi
if [ -z "${COMPANY_URL}" ]; then echo "ERROR: COMPANY_URL is not set"; exit 1; fi

CLIENT_SLUG=$(echo "$COMPANY_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
CLIENT_DIR="clients/${CLIENT_SLUG}"

mkdir -p "${CLIENT_DIR}/intelligence"
mkdir -p "${CLIENT_DIR}/strategies"
mkdir -p "${CLIENT_DIR}/campaigns"
mkdir -p "${CLIENT_DIR}/leads"
mkdir -p "${CLIENT_DIR}/content"

# Initialize running notes
echo "# ${COMPANY_NAME} — Notes" > "${CLIENT_DIR}/notes.md"
echo "Onboarding started: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${CLIENT_DIR}/notes.md"
echo "URL: ${COMPANY_URL}" >> "${CLIENT_DIR}/notes.md"

mkdir -p /app/results
echo "Setup complete. Client dir: ${CLIENT_DIR}"
```

Expected folder structure after setup:

```
clients/<client-name>/
├── context.md              # Populated during research
├── notes.md                # Running log (initialized above)
├── intelligence/           # Phase 1 outputs
├── strategies/
├── campaigns/
├── leads/
└── content/
```

---

## Step 2: Phase 1 — Intelligence Gathering (max 8 parallel tasks)

Run all eight research tasks. Groups A and B may run in parallel with each other; tasks within each group may also run in parallel.

### Parallel Group A — General Research (run simultaneously)

#### Step 2.1: Company Deep Research

Conduct deep web research covering: products and pricing, team and leadership, funding history, customer base, technology stack, and recent news.

- **Method**: Web search + web fetch
- **Output**: `clients/<client-name>/intelligence/company-research.md`

#### Step 2.2: Competitor Deep Research

Identify the top 5–10 competitors and research their positioning, pricing, strengths, and weaknesses.

- **Method**: Web search + web fetch
- **Output**: `clients/<client-name>/intelligence/competitor-research.md`

#### Step 2.3: Founder Deep Research

Research all founders: backgrounds, LinkedIn presence, thought leadership, and public visibility.

- **Method**: Web search + `linkedin-profile-post-scraper`
- **Output**: `clients/<client-name>/intelligence/founder-research.md`

### Parallel Group B — Automated Audits (run simultaneously)

#### Step 2.4: SEO Content Audit

Run a full SEO footprint analysis: content inventory, domain metrics, competitive gaps, and brand voice extraction.

- **Skill**: `seo-content-audit` (orchestrates `site-content-catalog` + `seo-domain-analyzer` + `brand-voice-extractor`)
- **Output**: `clients/<client-name>/intelligence/seo-content-audit.md`

#### Step 2.5: AEO Visibility Check

Test the client's visibility across AI answer engines for key queries in their space.

- **Skill**: `aeo-visibility`
- **Output**: `clients/<client-name>/intelligence/aeo-visibility.md`

#### Step 2.6: Paid Ads Strategy Review

Scrape active Meta and Google ads for the client and their top competitors.

- **Skills**: `meta-ad-scraper` + `google-ad-scraper`
- **Output**: `clients/<client-name>/intelligence/ad-strategy.md`

#### Step 2.7: Industry Intelligence Scan

Scan everything happening in the client's industry in the past week.

- **Skill**: `industry-scanner`
- **Output**: `clients/<client-name>/intelligence/industry-scan.md`

#### Step 2.8: Current GTM Analysis

Score the client's current go-to-market motion across all key dimensions.

- **Skill**: `company-current-gtm-analysis`
- **Output**: `clients/<client-name>/intelligence/gtm-analysis.md`

### Parallel Execution Plan

```
Parallel Group A (general research — run simultaneously):
  Step 2.1: Company Deep Research
  Step 2.2: Competitor Deep Research
  Step 2.3: Founder Deep Research

Parallel Group B (automated audits — run simultaneously):
  Step 2.4: SEO Content Audit
  Step 2.5: AEO Visibility Check
  Step 2.6: Paid Ads Strategy Review
  Step 2.7: Industry Intelligence Scan
  Step 2.8: Current GTM Analysis
```

Groups A and B can run in parallel with each other.

### Phase 1 Verification

```bash
CLIENT_DIR="clients/${CLIENT_SLUG}"
for f in company-research competitor-research founder-research seo-content-audit aeo-visibility ad-strategy industry-scan gtm-analysis; do
  path="${CLIENT_DIR}/intelligence/${f}.md"
  if [ ! -s "$path" ]; then echo "MISSING: $path"; else echo "OK: $path ($(wc -w < "$path") words)"; fi
done
```

---

## Step 3: Phase 2 — Synthesis & Diagnosis

> **Human Checkpoint**: Review the Intelligence Package for accuracy before generating strategies.

Read all Phase 1 outputs and synthesize them into a single Client Intelligence Package following the reference framework in `docs/growth-frameworks.md`.

### Diagnostic Steps

Work through each diagnostic question in order:

1. **Assess PMF**: Does the retention curve flatten? Classify as Pre-PMF / PMF / Strong PMF.
2. **Determine ACV tier**: What viable channels does their price point support?
3. **Identify growth motion**: Product-led, marketing-led, sales-led, or blended?
4. **Assess scaling stage**: Pre-PMF → PMF → GTM Fit → Growth & Moat.
5. **Score current GTM**: Rate each dimension A–F using the `gtm-analysis` output.
6. **Map competitive landscape**: Document top 5 competitors with strengths and weaknesses.
7. **Identify opportunity gaps**: Which Growth Matrix cells are empty?
8. **Flag risk factors**: Competitive threats, market risks, internal constraints.

### Output Structure

Write `clients/<client-name>/intelligence-package.md` with:

1. Company Profile
2. Stage Assessment (PMF, ACV, Motion, Scaling Stage)
3. Current GTM Scorecard (A–F per dimension)
4. Competitive Landscape
5. Industry Context
6. Opportunity Map (Growth Matrix gaps)
7. Risk Factors

---

## Step 4: Phase 3 — Strategy Generation (max 3 rounds)

> **Human Checkpoint**: Review strategies with client before implementation.

Read the Intelligence Package and generate prioritized growth strategies. For each identified opportunity gap:

1. **Name the system**: Map to the Growth Systems Taxonomy (Intelligence / Demand Creation / Pipeline).
2. **Describe the gap**: What is missing or broken?
3. **Propose the solution**: What system do we build? What skills power it?
4. **Estimate impact**: Expected lift based on available data.
5. **Sequence**: P0 (immediate), P1 (4–6 weeks), P2 (8–10 weeks).
6. **Score**: ICE score (Impact × Confidence × Ease, each 1–10).
7. **Tag execution pattern**: Add a structured `<!-- execution ... -->` YAML block per the format below.

### Prioritization Rules

1. Activation before acquisition — if activation is broken, fix that first.
2. One channel deep before expanding.
3. Engine over boost (compounding loops > one-time campaigns).
4. Always include at least one quick-win Pipeline strategy alongside longer-term Demand Creation.
5. Match channel to ACV (no field sales for <$5K ACV).

### Structured Execution Tag Format

Every strategy must include a machine-readable execution tag as an HTML comment:

```markdown
<!-- execution
pattern: signal-outbound
signal_type: job-posting
signal_keywords: ["DevOps", "SRE", "platform engineer"]
target_titles: ["VP Engineering", "CTO", "Head of Platform"]
estimated_leads: 50
estimated_cost: 0.80
skills_required:
  - job-posting-intent
  - company-contact-finder
  - email-drafting
-->
```

| Pattern | Use When |
|---------|----------|
| `signal-outbound` | A buying signal (hiring, social activity, reviews) maps to outreach |
| `content-lead-gen` | Strategy involves creating a content asset to attract leads |
| `competitive-displacement` | Strategy targets a competitor's unhappy customers |
| `event-prospecting` | Strategy involves finding and engaging event attendees |
| `lifecycle-timing` | Strategy depends on timing a trigger event |
| `manual` | Strategy requires human judgment not yet automatable |

### Output

Write `clients/<client-name>/growth-strategies.md` in P0/P1/P2 grouped format with gap, solution, tactical steps, expected impact, timeline, and execution tags. See `clients/vapi/growth-strategies.md` as a reference example.

---

## Step 5: Iterate on Errors (max 3 rounds)

If any Phase 1 research output is missing or incomplete:

1. Identify which step failed from the Phase 1 verification output.
2. Re-run the specific step.
3. Re-verify the output exists and is non-empty.
4. Repeat up to 3 times per step.

If any Phase 2 or Phase 3 output is structurally incomplete (missing required sections), re-generate the affected section and overwrite the file.

### Common Fixes

| Issue | Fix |
|-------|-----|
| Intelligence file missing | Re-run the specific Phase 1 step; check that the skill is available |
| Intelligence Package missing required section | Re-read Phase 1 outputs and regenerate the missing section |
| Growth strategies missing execution tags | Add `<!-- execution ... -->` blocks to all strategies, using `manual` pattern if no automation is available |
| Strategy file missing P0/P1/P2 grouping | Restructure file under the three priority headings |

---

## Step 6: Final Checklist

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
CLIENT_DIR="clients/${CLIENT_SLUG}"

# Phase 1 intelligence files
for f in company-research competitor-research founder-research seo-content-audit aeo-visibility ad-strategy industry-scan gtm-analysis; do
  path="${CLIENT_DIR}/intelligence/${f}.md"
  if [ ! -s "$path" ]; then echo "FAIL: $path missing or empty"; else echo "PASS: $path"; fi
done

# Phase 2 & 3 outputs
for f in "${CLIENT_DIR}/intelligence-package.md" "${CLIENT_DIR}/growth-strategies.md"; do
  if [ ! -s "$f" ]; then echo "FAIL: $f missing or empty"; else echo "PASS: $f"; fi
done

# Meta outputs
for f in /app/results/summary.md /app/results/validation_report.json; do
  if [ ! -s "$f" ]; then echo "FAIL: $f missing or empty"; else echo "PASS: $f"; fi
done

# Check all strategies have execution tags
if grep -q '<!-- execution' "${CLIENT_DIR}/growth-strategies.md"; then
  echo "PASS: execution tags present in growth-strategies.md"
else
  echo "FAIL: no execution tags found in growth-strategies.md"
fi

# Check human checkpoints are noted
echo "REMINDER: Confirm human checkpoint after Phase 2 before proceeding to Phase 3"
echo "REMINDER: Confirm human checkpoint after Phase 3 before client delivery"
```

### Checklist

- [ ] All 8 Phase 1 intelligence files exist and are non-empty
- [ ] `intelligence-package.md` contains all 7 required sections
- [ ] `growth-strategies.md` contains P0/P1/P2 grouped strategies
- [ ] Every strategy in `growth-strategies.md` has a `<!-- execution ... -->` tag
- [ ] All strategies have `estimated_leads`, `estimated_cost`, and `skills_required`
- [ ] Human checkpoint after Phase 2 acknowledged before Phase 3 started
- [ ] Human checkpoint after Phase 3 acknowledged before delivery
- [ ] `summary.md` and `validation_report.json` written to `/app/results`

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Run Groups A and B in parallel.** All 8 Phase 1 steps can overlap — typical wall-clock time is ~30 minutes when fully parallelized.
- **Slugify the client name consistently.** Use lowercase + hyphens for `<client-name>` in all paths so files from different phases land in the same folder.
- **Use `manual` execution tags sparingly.** If a strategy can be even partially automated, tag it with the automatable pattern and note limitations in the strategy description.
- **Estimate conservatively.** Overestimate cost, underestimate leads — better to over-deliver than under-deliver.
- **Reference the vapi example.** `clients/vapi/growth-strategies.md` shows the expected format and level of detail for Phase 3 output.
- **Every strategy gets tagged.** Even manual ones — this ensures the `client-packet-engine` playbook can account for all strategies.
