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
    skill_name: "client-onboarding"
    confidence: "high"
secrets: {}
---

# Client Onboarding — Agent Runbook

## Objective

Run the full onboarding playbook for a new client, producing a Client Intelligence Package and Growth Strategy Recommendations. The process covers three phases: parallel intelligence gathering (company, competitor, founder, SEO, AEO, paid ads, industry, and GTM research), synthesis and diagnosis into a structured intelligence package, and prioritized growth strategy generation with machine-readable execution tags. The runbook follows the Client Launch Playbook phases 1–3 as documented at `docs/agency-playbook/client-launch-playbook.md`.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**All of the following files MUST exist and be non-empty before this runbook is considered complete.**

| File | Description |
|------|-------------|
| `/app/results/clients/<client-name>/intelligence/company-research.md` | Deep web research: product, pricing, team, funding, customers, tech stack, news |
| `/app/results/clients/<client-name>/intelligence/competitor-research.md` | Top 5-10 competitors: positioning, pricing, strengths, weaknesses |
| `/app/results/clients/<client-name>/intelligence/founder-research.md` | Founders: backgrounds, LinkedIn, thought leadership, public visibility |
| `/app/results/clients/<client-name>/intelligence/seo-content-audit.md` | Full SEO footprint: content inventory, domain metrics, competitive gaps, brand voice |
| `/app/results/clients/<client-name>/intelligence/aeo-visibility.md` | AI answer engine visibility across key queries |
| `/app/results/clients/<client-name>/intelligence/ad-strategy.md` | Active Meta and Google ads for client and top competitors |
| `/app/results/clients/<client-name>/intelligence/industry-scan.md` | Industry events and news from the past week |
| `/app/results/clients/<client-name>/intelligence/gtm-analysis.md` | GTM scorecard across all dimensions |
| `/app/results/clients/<client-name>/intelligence-package.md` | Synthesized Client Intelligence Package (Phase 2 output) |
| `/app/results/clients/<client-name>/growth-strategies.md` | Prioritized growth strategies with execution tags (Phase 3 output) |
| `/app/results/summary.md` | Executive summary of the run: client, phases completed, key findings |
| `/app/results/validation_report.json` | Structured validation results with stages and `overall_passed` |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Root output directory |
| `company_name` | *(required)* | The client company name (e.g. "Acme Corp") |
| `company_url` | *(required)* | The client company website URL (e.g. "https://acme.com") |
| `client_name` | Slugified `company_name` | Directory slug used under `clients/` |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Web search | Tool | Yes | General web research for company, competitors, founders, industry |
| Web fetch | Tool | Yes | Fetch specific pages, LinkedIn profiles, ad libraries |
| `seo-content-audit` skill | Composite skill | Yes | Orchestrates site-content-catalog + seo-domain-analyzer + brand-voice-extractor |
| `aeo-visibility` skill | Capability skill | Yes | Tests AI answer engine visibility |
| `meta-ad-scraper` skill | Capability skill | Yes | Scrapes active Meta ads |
| `google-ad-scraper` skill | Capability skill | Yes | Scrapes active Google ads |
| `industry-scanner` skill | Composite skill | Yes | Scans industry news and events |
| `company-current-gtm-analysis` skill | Composite skill | Yes | Scores the client's current GTM |
| `linkedin-profile-post-scraper` | Capability skill | Yes | Scrapes founder LinkedIn activity |
| Growth frameworks reference | Documentation | Yes | `docs/growth-frameworks.md` — used in Phase 2 synthesis |

---

## Step 1: Environment Setup

Verify all required inputs and create the client folder structure.

```bash
echo "=== SETUP ==="
# Validate required inputs
if [ -z "$COMPANY_NAME" ] || [ -z "$COMPANY_URL" ]; then
  echo "ERROR: COMPANY_NAME and COMPANY_URL must be set"
  exit 1
fi

CLIENT_NAME=$(echo "$COMPANY_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-\|-$//g')
RESULTS_DIR="/app/results"

# Create client folder structure
mkdir -p "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence"
mkdir -p "$RESULTS_DIR/clients/$CLIENT_NAME/strategies"
mkdir -p "$RESULTS_DIR/clients/$CLIENT_NAME/campaigns"
mkdir -p "$RESULTS_DIR/clients/$CLIENT_NAME/leads"
mkdir -p "$RESULTS_DIR/clients/$CLIENT_NAME/content"

# Initialize running log
cat > "$RESULTS_DIR/clients/$CLIENT_NAME/notes.md" <<EOF
# $COMPANY_NAME — Onboarding Notes

Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)
URL: $COMPANY_URL
EOF

echo "Client folder created at: $RESULTS_DIR/clients/$CLIENT_NAME/"
echo "CLIENT_NAME=$CLIENT_NAME"
```

---

## Step 2: Phase 1 — Intelligence Gathering

Run all 8 research steps. Groups A and B can execute in parallel with each other; steps within each group can also run simultaneously.

### Parallel Group A: General Research (Steps 2.1–2.3)

#### Step 2.1: Company Deep Research

Research the company thoroughly using web search and web fetch.

Topics to cover:
- Product overview, pricing tiers, and packaging
- Team size, key hires, and leadership
- Funding history and investors
- Known customers and case studies
- Tech stack (via BuiltWith, job postings, public repos)
- Recent news and press coverage

**Output**: `clients/<client-name>/intelligence/company-research.md`

Format:
```markdown
# Company Research: <Company Name>

## Overview
## Product & Pricing
## Team & Leadership
## Funding
## Customers & Case Studies
## Tech Stack
## Recent News
```

#### Step 2.2: Competitor Deep Research

Identify top 5–10 competitors, then research each.

For each competitor:
- Positioning and messaging
- Pricing and packaging
- Strengths and weaknesses
- Recent moves (funding, product launches, partnerships)

**Output**: `clients/<client-name>/intelligence/competitor-research.md`

#### Step 2.3: Founder Deep Research

Research each founder:
- Professional background and career history
- LinkedIn presence and follower count
- Recent posts and thought leadership themes
- Public visibility (podcasts, press mentions, speaking)

**Method**: Web search + `linkedin-profile-post-scraper`

**Output**: `clients/<client-name>/intelligence/founder-research.md`

---

### Parallel Group B: Automated Audits (Steps 2.4–2.8)

#### Step 2.4: SEO Content Audit

Run the `seo-content-audit` composite skill against the company URL.

This skill orchestrates:
1. `site-content-catalog` — inventory all public pages
2. `seo-domain-analyzer` — domain authority, backlinks, keyword rankings
3. `brand-voice-extractor` — tone, style, key messaging patterns

**Output**: `clients/<client-name>/intelligence/seo-content-audit.md`

#### Step 2.5: AEO Visibility Check

Run the `aeo-visibility` skill. Test visibility across AI answer engines (ChatGPT, Perplexity, Google SGE) for the company's primary use-case queries.

Record: which queries surface the client, with what framing, and which competitors appear instead.

**Output**: `clients/<client-name>/intelligence/aeo-visibility.md`

#### Step 2.6: Paid Ads Strategy Review

Run `meta-ad-scraper` and `google-ad-scraper` for the client and their top 3 competitors.

Capture:
- Active ad count and creative themes
- Offers and CTAs being tested
- Landing page destinations

**Output**: `clients/<client-name>/intelligence/ad-strategy.md`

#### Step 2.7: Industry Intelligence Scan

Run `industry-scanner` for the client's industry vertical. Scope to the past 7 days.

Capture: funding rounds, product launches, regulatory news, major partnerships, analyst reports.

**Output**: `clients/<client-name>/intelligence/industry-scan.md`

#### Step 2.8: Current GTM Analysis

Run `company-current-gtm-analysis` for the client. Score each GTM dimension.

**Output**: `clients/<client-name>/intelligence/gtm-analysis.md`

---

### Parallel Execution Plan

```
Parallel Group A (run simultaneously):
  Step 2.1: Company Deep Research
  Step 2.2: Competitor Deep Research
  Step 2.3: Founder Deep Research

Parallel Group B (run simultaneously):
  Step 2.4: SEO Content Audit
  Step 2.5: AEO Visibility Check
  Step 2.6: Paid Ads Strategy Review
  Step 2.7: Industry Intelligence Scan
  Step 2.8: Current GTM Analysis

Groups A and B can run concurrently.
```

---

## Step 3: Phase 2 — Synthesis & Diagnosis

> **HUMAN CHECKPOINT**: Before proceeding, confirm all 8 intelligence files exist and are non-empty.

Read all Phase 1 outputs and synthesize into a single Client Intelligence Package.

Reference framework: `docs/growth-frameworks.md`

### Diagnostic Steps

Work through each item in order:

1. **Assess PMF**: Does the retention curve flatten? Classify as Pre-PMF / PMF / Strong PMF.
2. **Determine ACV tier**: What viable channels does their price point support?
3. **Identify growth motion**: Product-led, marketing-led, sales-led, or blended?
4. **Assess scaling stage**: Pre-PMF → PMF → GTM Fit → Growth & Moat
5. **Score current GTM**: Rate each dimension A–F (from `gtm-analysis.md`)
6. **Map competitive landscape**: Top 5 competitors with strengths/weaknesses matrix
7. **Identify opportunity gaps**: Which Growth Matrix cells are empty or underserved?
8. **Flag risk factors**: Competitive threats, market risks, internal constraints

### Output Structure

Write `clients/<client-name>/intelligence-package.md` with these sections:

```markdown
# Client Intelligence Package: <Company Name>

## 1. Company Profile
## 2. Stage Assessment
   - PMF Status
   - ACV Tier
   - Growth Motion
   - Scaling Stage
## 3. Current GTM Scorecard (A-F per dimension)
## 4. Competitive Landscape
## 5. Industry Context
## 6. Opportunity Map (Growth Matrix gaps)
## 7. Risk Factors
```

---

## Step 4: Phase 3 — Strategy Generation

> **HUMAN CHECKPOINT**: Review the Intelligence Package for accuracy before generating strategies.

Read `intelligence-package.md` and generate prioritized growth strategies.

### Strategy Generation Process

For each identified opportunity gap, produce one strategy entry:

1. **Name the system**: Map to Growth Systems Taxonomy (Intelligence / Demand Creation / Pipeline)
2. **Describe the gap**: What's missing or broken?
3. **Propose the solution**: What system to build? Which skills power it?
4. **Estimate impact**: Expected lift based on available data
5. **Sequence**: P0 (immediate), P1 (4–6 weeks), P2 (8–10 weeks)
6. **Score**: ICE score (Impact × Confidence × Ease, each 1–10)
7. **Tag with structured execution block** (see format below)

### Prioritization Rules

1. Activation before acquisition — if activation is broken, fix that first
2. One channel deep before expanding
3. Engine over boost — compounding loops beat one-time campaigns
4. Always include at least one quick-win Pipeline strategy alongside longer-term Demand Creation
5. Match channel to ACV — no field sales for <$5K ACV

### Execution Tag Format

Every strategy MUST include a machine-readable execution tag:

```markdown
<!-- execution
pattern: signal-outbound
signal_type: job-posting
signal_keywords: ["keyword1", "keyword2"]
target_titles: ["Title 1", "Title 2"]
estimated_leads: 50
estimated_cost: 0.80
skills_required:
  - skill-name-1
  - skill-name-2
-->
```

Valid patterns: `signal-outbound`, `content-lead-gen`, `competitive-displacement`, `event-prospecting`, `lifecycle-timing`, `manual`.

Every strategy gets tagged — even manual ones.

### Output

Write `clients/<client-name>/growth-strategies.md` with P0/P1/P2 grouped strategies, each including: gap description, proposed solution, tactical steps, expected impact, timeline, ICE score, and execution tag.

Reference example: `clients/vapi/growth-strategies.md`

---

## Step 5: Iterate on Errors (max 3 rounds)

If any Phase 1 output file is missing or incomplete after the first pass:

1. Identify which steps failed (check file existence and minimum content length)
2. Re-run only the failed steps
3. Re-check outputs
4. Repeat up to 3 rounds total

If after 3 rounds a required file is still empty or missing, record the failure in `summary.md` and proceed with a note in `validation_report.json`.

---

## Step 6: Validation

Run the following verification checks before completing:

```bash
echo "=== INTELLIGENCE FILE VALIDATION ==="
RESULTS_DIR="/app/results"
CLIENT_NAME="${CLIENT_NAME:-unknown}"

for f in \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/company-research.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/competitor-research.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/founder-research.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/seo-content-audit.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/aeo-visibility.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/ad-strategy.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/industry-scan.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/gtm-analysis.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence-package.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/growth-strategies.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Check growth-strategies has at least one execution tag
if grep -q "pattern:" "$RESULTS_DIR/clients/$CLIENT_NAME/growth-strategies.md" 2>/dev/null; then
  echo "PASS: growth-strategies.md contains execution tags"
else
  echo "FAIL: growth-strategies.md missing execution tags"
fi
```

---

## Step 7: Write Executive Summary

Write `/app/results/summary.md`:

```markdown
# Client Onboarding — Run Summary

## Overview
- **Date**: <run date>
- **Client**: <company_name> (<company_url>)
- **Phases completed**: Phase 1 (Intelligence), Phase 2 (Synthesis), Phase 3 (Strategies)

## Phase 1: Intelligence Files
| File | Status | Notes |
|------|--------|-------|
| company-research.md | ... | ... |
| competitor-research.md | ... | ... |
| founder-research.md | ... | ... |
| seo-content-audit.md | ... | ... |
| aeo-visibility.md | ... | ... |
| ad-strategy.md | ... | ... |
| industry-scan.md | ... | ... |
| gtm-analysis.md | ... | ... |

## Phase 2: Intelligence Package
- PMF Status: ...
- ACV Tier: ...
- Growth Motion: ...

## Phase 3: Strategies
- Total strategies: ...
- P0 count: ...
- P1 count: ...
- P2 count: ...

## Issues / Manual Follow-up
- <Any failed steps>
- <Any data gaps identified>
- <Human review checkpoints pending>

## Provenance
- Origin skill: https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/client-onboarding/SKILL.md
- Imported by: skill-to-runbook-converter v1.0.0
```

---

## Step 8: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
CLIENT_NAME="${CLIENT_NAME:-unknown}"

for f in \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/company-research.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/competitor-research.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/founder-research.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/seo-content-audit.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/aeo-visibility.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/ad-strategy.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/industry-scan.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence/gtm-analysis.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/intelligence-package.md" \
  "$RESULTS_DIR/clients/$CLIENT_NAME/growth-strategies.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

### Checklist

- [ ] All 8 intelligence files exist under `clients/<client-name>/intelligence/`
- [ ] `intelligence-package.md` contains all 7 required sections
- [ ] `growth-strategies.md` contains P0/P1/P2 strategies, each with an execution tag
- [ ] Every strategy execution tag includes `pattern`, `estimated_leads`, `estimated_cost`, `skills_required`
- [ ] `summary.md` exists and reflects the actual run
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Human checkpoint after Phase 2 was completed before Phase 3 was run
- [ ] Human checkpoint after Phase 3 was completed before handoff
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Parallelize aggressively.** Groups A and B can run at the same time. Within each group, all steps can also run simultaneously. This cuts the ~30 min intelligence phase significantly.
- **Slugify the client name consistently.** Use the same slug for all file paths so re-runs overwrite rather than duplicate.
- **Reference the example.** `clients/vapi/growth-strategies.md` is the canonical example for strategy format and execution tag density. Mirror it.
- **ICE score honestly.** Overestimate cost, underestimate leads. Strategies that look weaker on paper but are fast to execute often outperform in practice.
- **Every strategy gets tagged.** Even `pattern: manual` strategies need the execution tag so the packet engine can account for the full strategy set.
- **Human checkpoints are real gates.** Do not generate strategies before the Intelligence Package has been reviewed. Surface the package clearly and wait for approval.
- **Growth motion determines channel priority.** Product-led companies should emphasize activation and in-product growth signals; sales-led companies need pipeline strategies; marketing-led companies need demand creation engines.
