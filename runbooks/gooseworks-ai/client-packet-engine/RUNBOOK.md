---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/client-packet-engine/SKILL.md"
  source_host: "github.com"
  source_title: "Client Packet Engine"
  imported_at: "2026-05-01T03:18:06Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    skill_name: "client-packet-engine"
    confidence: "high"
secrets: {}
---

# Client Packet Engine — Agent Runbook

## Objective

Batch pipeline that takes a list of companies and produces finished GTM pitch packets — intelligence
packages, growth strategies, and executed sample work (lead lists, content drafts, email sequences).
Designed for prospective client pitches, not live campaign execution. The engine processes companies
in parallel through four phases: intake & validation, research & strategy generation, strategy
execution (in pitch-packet mode — no live sends), and final packaging. A human checkpoint after
Phase 1 allows selection of which generated strategies to execute before incurring Phase 3 costs.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files before the task is complete. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary: companies processed, strategies executed, total cost, per-company packet locations |
| `/app/results/validation_report.json` | Structured validation results with stages and `overall_passed` |
| `/app/results/batch_report.md` | Final batch summary table (companies × strategies × leads × cost) |
| `/app/results/client_packets/` | Directory tree of per-company deliverables (see Phase 4) |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Root output directory for all results and client packets |
| Company list | *(required)* | One or more companies: `name` + `url`. Minimum 1, warn if >10 |
| Budget per company | `$5.00` | Hard cost ceiling per company; warn at 80% ($4.00) |
| Max parallel companies | `3` | Concurrent companies in Phase 1 |
| Max parallel strategies | `5` | Concurrent strategy executions in Phase 3 |
| Skip phases | *(none)* | Optional list of phase numbers to skip (e.g. `[4]`) |
| Strategy filter | *(none)* | Pre-filter strategies (e.g. `"P0 only"`) |
| Pitch packet mode | `true` | When `true` (default): sample outputs only — no live emails, no paid enrichment. Set `false` only with explicit user confirmation |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `client-onboarding` playbook | Internal skill | Yes | Phases 1–3 of intelligence gathering and strategy generation |
| `client-package-local` playbook | Internal skill | Yes | Phase 4 packaging into dated deliverable directories |
| `job-posting-intent` | Capability skill | Conditional | Signal detection for hiring-signal outbound strategies |
| `linkedin-post-research` | Capability skill | Conditional | LinkedIn signal detection |
| `review-scraper` | Capability skill | Conditional | Competitor review mining |
| `company-contact-finder` | Capability skill | Yes | Find decision-maker contacts (Gooseworks MCP — free) |
| `email-drafting` | Capability skill | Conditional | Draft email sequences (pitch-packet mode: draft only, no send) |
| `content-asset-creator` | Capability skill | Conditional | Generate HTML reports and comparison pages |
| `apollo-lead-finder` | Capability skill | Conditional | Lead discovery (pitch-packet mode: free search only, no paid enrichment) |
| `web-archive-scraper` | Capability skill | Conditional | Archived page scraping for competitive intel |
| `luma-event-attendees` | Capability skill | Conditional | Event attendee scraping |
| `conference-speaker-scraper` | Capability skill | Conditional | Conference speaker list scraping |
| `lead-qualification` | Capability skill | Conditional | ICP scoring of raw leads |
| `cold-email-outreach` | Capability skill | Conditional | Live send (only when `pitch_packet_mode: false` with explicit user confirmation) |
| `linkedin-outreach` | Capability skill | Conditional | Live LinkedIn send (only when `pitch_packet_mode: false`) |
| Apify credits | External API | Yes | Required for SEO, ads, and content scraping in Phase 1 (~$1.50/company) |

---

## Step 1: Environment Setup

Verify inputs and initialize the output directory structure.

```bash
mkdir -p /app/results/client_packets
mkdir -p /app/results/work

# Confirm pitch_packet_mode is enabled unless explicitly overridden
if [ "${PITCH_PACKET_MODE:-true}" = "false" ]; then
  echo "WARNING: pitch_packet_mode=false enables live campaign execution."
  echo "Emails WILL be sent and Apollo credits WILL be spent."
  echo "Confirm with user before proceeding."
fi

echo "Results dir: /app/results"
echo "Client packets dir: /app/results/client_packets"
```

Fail fast if:
- No company list was provided
- `PITCH_PACKET_MODE` is `false` without an explicit user confirmation recorded in `/app/results/work/live_mode_confirmed.txt`

---

## Step 2: Phase 0 — Intake & Validation

Parse, validate, and cost-estimate the company list before spending any credits.

### Parse Input

Extract company `name` and `url` from the user's request. Normalize URLs:
- Add `https://` if missing
- Strip trailing slashes

### Validate Websites

For each company URL, perform a quick web fetch:
- Confirm site is reachable (not 404/500)
- Confirm content matches the company name (page title or body text)
- Flag mismatches and pause for user confirmation before continuing

### Estimate Costs

| Phase | Typical cost |
|-------|-------------|
| Phase 1 (research + audits) | ~$1.50/company |
| Phase 3 (strategy execution) | ~$1.00–$3.00/company |
| **Total** | **$2.50–$4.50/company** |

### Present Approval Summary

```
Batch Summary:
┌──────────────────┬─────────────────────────┬──────────┐
│ Company          │ URL                     │ Est Cost │
├──────────────────┼─────────────────────────┼──────────┤
│ Acme Corp        │ https://acme.com        │ ~$3.50   │
│ Beta Inc         │ https://beta.io         │ ~$3.50   │
└──────────────────┴─────────────────────────┴──────────┘
Total estimated cost: ~$7.00
Budget limit: $5.00/company
```

**Human checkpoint 1**: Get user approval before proceeding to Phase 1.

### Output

- Validated company list with confirmed URLs saved to `/app/results/work/validated_companies.json`
- Cost estimate acknowledged by user

---

## Step 3: Phase 1 — Research & Strategy Generation (max 3 rounds per company)

Run the `client-onboarding` playbook (Phases 1–3) for each company to produce intelligence packages
and growth strategies.

### Execution

Process up to **3 companies in parallel** using Task agents. Each company receives:

- **Phase 1**: Intelligence Gathering
  - Company research, competitor research, founder research
  - SEO audit, AEO visibility, ads review
  - Industry scan, GTM analysis
- **Phase 2**: Synthesis into Client Intelligence Package
- **Phase 3**: Strategy Generation with `<!-- execution -->` tags

### Cost Tracking

After each company completes, log actual costs:

```
Cost Tracker:
┌──────────────┬─────────────┬───────┬──────────┬───────────┐
│ Company      │ Phase       │ Spent │ Budget   │ Remaining │
├──────────────┼─────────────┼───────┼──────────┼───────────┤
│ Acme Corp    │ Phase 1     │ $1.40 │ $5.00    │ $3.60     │
└──────────────┴─────────────┴───────┴──────────┴───────────┘
```

Rules:
- Warn at 80% of per-company budget ($4.00)
- Hard stop at $5.00/company — package whatever was completed

### Output per Company

Write to `/app/results/client_packets/<company>/`:
- `intelligence-package.md`
- `growth-strategies.md` (with `<!-- execution -->` tags)
- `intelligence/` subdirectory with all Phase 1 research files

---

## Step 4: Phase 2 — Strategy Selection (Human Checkpoint)

Present generated strategies for user selection before executing anything in Phase 3.

### Presentation Format

For each company, display a summary table:

```
## Acme Corp — 7 strategies generated

| # | Strategy | Pattern | Priority | ICE | Est Leads | Est Cost |
|---|----------|---------|----------|-----|-----------|----------|
| 1 | Hiring signal outbound (DevOps roles) | signal-outbound | P0 | 8.2 | ~50 | $0.80 |
| 2 | Competitor displacement (vs BigCo)    | competitive-displacement | P0 | 7.5 | ~30 | $1.20 |
| 3 | Conference speaker prospecting        | event-prospecting | P1 | 6.8 | ~20 | $0.50 |
| 4 | SEO comparison content                | content-lead-gen | P1 | 6.5 | ~40 | $0.60 |
| 5 | Quarterly business review timing      | lifecycle-timing | P2 | 5.0 | ~15 | $0.30 |
| 6 | LinkedIn thought leadership           | manual | P2 | 4.5 | — | — |
| 7 | Partner co-marketing                  | manual | P2 | 3.8 | — | — |

Select strategies to execute: [e.g., "1-4", "all P0", "top 3 by ICE"]
```

### Selection Options

Accept flexible input:
- Specific numbers: `"1, 3, 5"`
- Ranges: `"1-4"`
- Priority-based: `"all P0"`, `"P0 and P1"`
- Score-based: `"top 3 by ICE"`
- All executable: `"all"` (skips `manual` strategies)
- Per-company overrides: `"Acme: 1-3, Beta: all P0"`

### Validation

- Warn if selected strategies exceed remaining per-company budget
- Flag any `manual` strategies (these produce a plan document, not automated execution)
- **Human checkpoint 2**: Confirm final selection before proceeding

---

## Step 5: Phase 3 — Strategy Execution (Pitch-Packet Mode) (max 3 rounds per strategy)

Execute selected strategies by routing each to the appropriate skill chain based on its
`<!-- execution -->` tag.

### Execution Pattern Router

| Pattern | Skills used | Pitch-packet output |
|---------|-------------|---------------------|
| `signal-outbound` | `job-posting-intent` / `linkedin-post-research` / `review-scraper` → `company-contact-finder` → `email-drafting` | Signal report + lead CSV + draft email sequences (NOT sent) |
| `content-lead-gen` | `content-asset-creator` → `apollo-lead-finder` (free search only) | Content asset (HTML) + lead list (names/titles/companies, no emails) |
| `competitive-displacement` | `web-archive-scraper` + `review-scraper` → `company-contact-finder` → `email-drafting` + `content-asset-creator` | Competitor intel report + lead CSV + email sequences + comparison page |
| `event-prospecting` | `luma-event-attendees` / `conference-speaker-scraper` → `lead-qualification` → `company-contact-finder` | Event attendee list + qualified leads CSV |
| `lifecycle-timing` | Web research → `company-contact-finder` → `email-drafting` | Trigger research + lead CSV + timing-aware email sequences |
| `manual` | *(no automation)* | Detailed step-by-step execution plan with tools, timelines, and KPIs |

### Parallelization

- Run up to **5 strategy executions concurrently** across all companies
- **Human checkpoint 3**: If any single API call would exceed $2, pause and confirm with user

### Output per Strategy

Write to `/app/results/client_packets/<company>/` in the appropriate subdirectory:

| Artifact type | Location |
|---------------|----------|
| Lead CSVs | `leads/` |
| Content assets | `content/` |
| Email sequences | `campaigns/` |
| Strategy plans | `strategies/` |
| Signal/research reports | `intelligence/` |

---

## Step 6: Phase 4 — Packaging

Run `client-package-local` for each company to produce the final dated deliverable.

### Steps

1. For each company, invoke `client-package-local`
2. Output lands in a dated package directory:

```
/app/results/client_packets/<company>/client-package/<YYYY-MM-DD>/
├── intelligence-package.md
├── growth-strategies.md
├── executed-strategies/
│   ├── strategy-1-signal-outbound/
│   │   ├── signal-report.md
│   │   ├── leads.csv
│   │   └── email-sequences.md
│   ├── strategy-2-competitive-displacement/
│   │   ├── competitor-intel.md
│   │   ├── leads.csv
│   │   ├── email-sequences.md
│   │   └── comparison-page.html
│   └── ...
└── summary.md
```

3. Generate a `summary.md` per packet:
   - Company overview (from intelligence package)
   - Strategies generated vs executed
   - Key metrics: total leads found, content assets created, email sequences drafted
   - Recommended next steps (what to do if the client signs)

---

## Step 7: Iterate on Errors (max 3 rounds)

For any failed skill execution or budget overrun:

1. **Skill failure**: Retry once. If still failing, log the error, skip that strategy, continue with remaining
2. **Budget exceeded**: Stop execution for that company, package whatever completed
3. **Website unreachable**: Skip company entirely, flag in final report, continue with others
4. **Rate limiting**: Back off and retry with exponential delay (max 3 retries)
5. **No executable strategies**: Generate all strategies but flag that manual execution is required

After 3 rounds of iteration on a single step, log the failure and move on. Record all failures in `validation_report.json`.

---

## Step 8: Final Report & Output Files

### Batch Summary

Present and write `/app/results/batch_report.md`:

```
Batch Complete: N/N companies processed

┌──────────────┬────────────┬───────────┬────────┬──────────┬───────────┐
│ Company      │ Strategies │ Executed  │ Leads  │ Content  │ Total Cost│
├──────────────┼────────────┼───────────┼────────┼──────────┼───────────┤
│ Acme Corp    │ 7          │ 4         │ 142    │ 3 assets │ $4.20     │
│ Beta Inc     │ 5          │ 3         │ 89     │ 2 assets │ $3.80     │
└──────────────┴────────────┴───────────┴────────┴──────────┴───────────┘

Total cost: $X.XX / $Y.YY budget
Packets saved to: /app/results/client_packets/<company>/client-package/<date>/
```

Write `/app/results/summary.md` and `/app/results/validation_report.json`.

---

## Step 9: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/batch_report.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

if [ ! -d "$RESULTS_DIR/client_packets" ] || [ -z "$(ls -A "$RESULTS_DIR/client_packets")" ]; then
  echo "FAIL: /app/results/client_packets/ is missing or empty"
else
  echo "PASS: client_packets/ directory present"
fi
echo "=== END VERIFICATION ==="
```

### Checklist

- [ ] `summary.md` exists with per-company outcomes, total cost, and packet locations
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] `batch_report.md` exists with a complete company × strategy matrix
- [ ] `/app/results/client_packets/` contains at least one dated package directory
- [ ] No company exceeded its budget without a logged explanation
- [ ] All human checkpoints were reached and user responses recorded
- [ ] Pitch-packet mode was respected — no live emails sent, no paid Apollo enrichment used (unless `pitch_packet_mode: false` was explicitly confirmed)

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Configuration Overrides

Users can override defaults at invocation:

```
Override options:
  budget_per_company: $10      # Default $5
  max_parallel_companies: 5    # Default 3
  max_parallel_strategies: 8   # Default 5
  skip_phases: [4]             # Skip packaging
  strategy_filter: "P0 only"   # Pre-filter strategies before Phase 2
  pitch_packet_mode: false     # Enable live campaign mode (CAREFUL — see Warning below)
```

**WARNING**: Setting `pitch_packet_mode: false` enables live campaign execution — emails will be
sent and Apollo credits will be spent. Only proceed with this setting after explicit, on-record
user confirmation.

---

## Common Fixes

| Issue | Fix |
|-------|-----|
| Company website unreachable | Skip company, flag in batch report, do not abort the whole batch |
| Strategy skill fails after retry | Log error to validation_report.json, skip strategy, continue |
| Budget overrun warning | Pause, report remaining budget, ask user whether to continue or package now |
| API call >$2 | Always pause and confirm with user before proceeding |
| No strategies have executable tags | Generate all strategies; flag in report that manual execution is required |
| `pitch_packet_mode: false` without confirmation | Refuse and request explicit written confirmation before continuing |

---

## Tips

- **Parallelism is your friend for Phase 1.** Up to 3 companies can run concurrently — use Task
  agents rather than sequential loops to keep runtime manageable for large batches.
- **Strategy selection quality matters.** A well-filtered Phase 2 selection (e.g. `"all P0"` or
  `"top 3 by ICE"`) keeps Phase 3 costs predictable and deliverables focused.
- **Cost tracking is non-optional.** Maintain the running cost log after every skill invocation so
  the 80% warning and hard stop fire correctly.
- **Pitch-packet mode is the default for a reason.** It lets you demonstrate value without
  triggering real campaigns. Never flip it without explicit, on-record user approval.
- **Human checkpoints protect everyone.** There are three mandatory stops: cost approval, strategy
  selection, and pre-large-API-call confirmation. Do not skip them.
