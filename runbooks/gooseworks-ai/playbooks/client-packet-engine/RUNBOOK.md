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
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    source_collection: "playbooks"
    skill_name: "client-packet-engine"
    confidence: "high"
secrets: {}
---

# Client Packet Engine — Agent Runbook

## Objective

This runbook automates a batch GTM pitch-packet pipeline. Given a list of company names and URLs, it runs intelligence gathering and strategy generation (via the client-onboarding playbook), presents ranked strategies for human selection, executes selected strategies in pitch-packet mode (no live campaigns or paid enrichment), and packages all outputs into local delivery packets. The goal is to demonstrate GTM value to prospective clients without launching real campaigns or spending on paid Apollo enrichment.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of the batch run — companies processed, strategies executed, outcomes |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/clients/<company>/intelligence-package.md` | Company intelligence package per client |
| `/app/results/clients/<company>/growth-strategies.md` | Growth strategies with execution tags per client |
| `/app/results/clients/<company>/client-package/<date>/summary.md` | Final pitch packet summary per client |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `company_list` | *(required)* | YAML list of `{ name, url }` objects — minimum 1, warn if >10 |
| `budget_per_company` | `$5.00` | Per-company cost cap. Warn at 80% ($4.00), hard stop at limit |
| `max_parallel_companies` | `3` | Max companies to process concurrently in Phase 1 |
| `max_parallel_strategies` | `5` | Max strategy executions to run concurrently in Phase 3 |
| `skip_phases` | `[]` | List of phase numbers to skip (e.g. `[4]` to skip packaging) |
| `strategy_filter` | `""` | Pre-filter strategies before presenting (e.g. `"P0 only"`) |
| `pitch_packet_mode` | `true` | Keep `true` to avoid live campaigns. Set `false` ONLY with explicit user confirmation |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `client-onboarding` | Playbook | Yes | Runs Phases 1–3 of intelligence gathering and strategy generation per company |
| `client-package-local` | Playbook | Yes | Packages all outputs into a dated delivery directory |
| `job-posting-intent` | Capability | Conditional | Detects hiring-signal buying triggers for `signal-outbound` pattern |
| `linkedin-post-research` | Capability | Conditional | Scrapes LinkedIn posts for signal detection |
| `review-scraper` | Capability | Conditional | Mines competitor reviews for `competitive-displacement` pattern |
| `company-contact-finder` | Capability | Conditional | Finds decision-maker contacts (Gooseworks MCP, free) |
| `email-drafting` | Capability | Conditional | Drafts outreach sequences (pitch-packet mode: no sending) |
| `content-asset-creator` | Capability | Conditional | Generates HTML reports, comparison pages, content assets |
| `apollo-lead-finder` | Capability | Conditional | Free lead search only — no paid Apollo enrichment in pitch-packet mode |
| `web-archive-scraper` | Capability | Conditional | Scrapes web archive data for competitive intel |
| `luma-event-attendees` | Capability | Conditional | Scrapes Luma event attendee lists |
| `conference-speaker-scraper` | Capability | Conditional | Scrapes conference speaker/attendee lists |
| `lead-qualification` | Capability | Conditional | Scores leads against ICP |
| `Apify credits` | External API | Yes | Used for SEO, ads, and content scraping in Phase 1; ~$1.50/company typical |

## Step 1: Environment Setup

Validate all inputs and confirm prerequisites before processing any companies.

```bash
echo "=== Environment Setup ==="

# Verify required inputs
if [ -z "$COMPANY_LIST" ]; then
  echo "ERROR: COMPANY_LIST is not set. Provide a YAML list of {name, url} objects."
  exit 1
fi

# Validate at least 1 company
COMPANY_COUNT=$(echo "$COMPANY_LIST" | python3 -c "import sys, yaml; data=yaml.safe_load(sys.stdin); print(len(data.get('companies', data)))")
if [ "$COMPANY_COUNT" -lt 1 ]; then
  echo "ERROR: company_list must contain at least 1 company."
  exit 1
fi

if [ "$COMPANY_COUNT" -gt 10 ]; then
  echo "WARNING: $COMPANY_COUNT companies in batch — this will be a long run with high cost."
  echo "Estimated cost: ~\$$(echo "$COMPANY_COUNT * 3.5" | bc) total. Proceed? (y/n)"
fi

# Create output structure
mkdir -p /app/results/clients
mkdir -p /app/results/work

echo "Companies to process: $COMPANY_COUNT"
echo "Budget per company: ${BUDGET_PER_COMPANY:-$5.00}"
echo "Pitch-packet mode: ${PITCH_PACKET_MODE:-true}"
echo "Setup complete."
```

## Step 2: Phase 0 — Intake & Validation

Parse, validate, and cost-estimate all input companies before any work begins.

```python
import yaml, json, pathlib, urllib.request

companies_raw = """
companies:
  - name: "Example Corp"
    url: "https://example.com"
"""  # Replace with actual input

data = yaml.safe_load(companies_raw)
companies = data.get('companies', data) if isinstance(data, dict) else data

validated = []
for co in companies:
    name = co['name']
    url = co['url']
    if not url.startswith('http'):
        url = 'https://' + url
    url = url.rstrip('/')

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'jetty-skill-importer/1.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        reachable = resp.status == 200
    except Exception as e:
        reachable = False

    validated.append({'name': name, 'url': url, 'reachable': reachable})
    if not reachable:
        print(f"WARNING: {name} ({url}) is unreachable — will skip or flag")

# Cost estimate
est_per_company = 3.50  # typical $2.50–$4.50
total_est = len(validated) * est_per_company
budget_total = 5.00 * len(validated)

print(f"\nBatch Summary:")
print(f"{'Company':<20} {'URL':<35} {'Est Cost':>10} {'Reachable':>10}")
for co in validated:
    print(f"{co['name']:<20} {co['url']:<35} ~${est_per_company:>8.2f} {'YES' if co['reachable'] else 'NO':>10}")
print(f"\nTotal estimated: ~${total_est:.2f} / Budget: ${budget_total:.2f}")
print("\nProceed? (y/n)")

pathlib.Path("/app/results/work/validated_companies.json").write_text(json.dumps(validated, indent=2))
```

**Human Checkpoint 1**: User must approve the batch and cost estimate before proceeding.

## Step 3: Phase 1 — Research & Strategy Generation (max 3 rounds of retry per company)

Run the `client-onboarding` playbook (Phases 1–3) for each company, up to **3 companies in parallel**.

```
For each company in validated_companies:
  1. Run client-onboarding Phase 1: Intelligence Gathering
     - Company research, competitor research, founder research
     - SEO audit, AEO visibility, ads review, industry scan, GTM analysis
  2. Run client-onboarding Phase 2: Synthesize → intelligence-package.md
  3. Run client-onboarding Phase 3: Strategy Generation → growth-strategies.md (with <!-- execution --> tags)
  4. After each company completes, log actual Apify/API costs
     - At 80% of budget ($4.00): warn user
     - At 100% of budget ($5.00): hard stop for that company
```

**Output per company** (write to `/app/results/clients/<company>/`):
- `intelligence-package.md`
- `growth-strategies.md`
- `intelligence/` — all Phase 1 research files

**Cost tracking**: Log costs after each company to `/app/results/work/cost_tracker.json`.

## Step 4: Phase 2 — Strategy Selection (Human Checkpoint)

Present all generated strategies across all companies for user selection.

Format the presentation as a table per company:

```
## <Company> — N strategies generated

| # | Strategy | Pattern | Priority | ICE | Est Leads | Est Cost |
|---|----------|---------|----------|-----|-----------|----------|
| 1 | ...      | signal-outbound | P0 | 8.2 | ~50 | $0.80 |
...

Select strategies to execute: [e.g., "1-4", "all P0", "top 3 by ICE"]
```

Accept flexible selection input:
- Specific numbers: `"1, 3, 5"`
- Ranges: `"1-4"`
- Priority-based: `"all P0"`, `"P0 and P1"`
- Score-based: `"top 3 by ICE"`
- All executable: `"all"` (skips `manual` pattern strategies)
- Per-company overrides: `"Acme: 1-3, Beta: all P0"`

**Validation before confirming**:
- Warn if selected strategies exceed remaining per-company budget
- Flag any `manual` pattern strategies (produce plan only, no automation)

**Human Checkpoint 2**: User must confirm final strategy selection before Phase 3.

## Step 5: Phase 3 — Strategy Execution (Pitch-Packet Mode)

Execute selected strategies using the pattern router below. Run up to **5 strategy executions concurrently**. Pause and confirm with user before any single API call >$2.

### Execution Pattern Router

| Pattern | Steps | Pitch-Packet Output |
|---------|-------|---------------------|
| `signal-outbound` | Detect signals (`job-posting-intent` / `linkedin-post-research` / `review-scraper`) → find contacts (`company-contact-finder`) → draft sequences (`email-drafting`, no sending) | Signal report + lead CSV + draft email sequences |
| `content-lead-gen` | Create content asset (`content-asset-creator`) → free lead search only (`apollo-lead-finder`, no paid enrichment) | Content asset (HTML) + lead list (names/titles/companies, no emails) |
| `competitive-displacement` | Mine competitor intel (`web-archive-scraper` + `review-scraper`) → find contacts (`company-contact-finder`) → draft outreach (`email-drafting`) → build comparison page (`content-asset-creator`) | Competitor intel report + lead CSV + email sequences + comparison page |
| `event-prospecting` | Find event attendees/speakers (`luma-event-attendees` / `conference-speaker-scraper`) → qualify leads (`lead-qualification`) → enrich contacts (`company-contact-finder`) | Event attendee list + qualified leads CSV |
| `lifecycle-timing` | Research triggers (web research) → find decision-makers (`company-contact-finder`) → draft timing-aware sequences (`email-drafting`) | Trigger research + lead CSV + timing-aware email sequences |
| `manual` | Generate step-by-step execution plan with recommended tools, timelines, KPIs | Strategy execution plan document (no automated work) |

**Output directories per company** (`/app/results/clients/<company>/`):
- Lead CSVs → `leads/`
- Content assets → `content/`
- Email sequences → `campaigns/`
- Strategy plans → `strategies/`
- Signal/research reports → `intelligence/`

**Cost tracking**: Update `/app/results/work/cost_tracker.json` after each strategy execution.

## Step 6: Phase 4 — Packaging

Run the `client-package-local` playbook for each company to produce the final deliverable.

```
For each company:
  1. Run client-package-local
  2. Output: clients/<company>/client-package/<YYYY-MM-DD>/
     ├── intelligence-package.md
     ├── growth-strategies.md
     ├── executed-strategies/
     │   ├── strategy-1-<pattern>/
     │   │   ├── signal-report.md (or equivalent)
     │   │   ├── leads.csv
     │   │   └── email-sequences.md (or equivalent)
     │   └── ...
     └── summary.md
  3. Generate summary.md with:
     - Company overview (from intelligence package)
     - Strategies generated + which were executed
     - Key metrics: leads found, content assets created, sequences drafted
     - Recommended next steps if client signs
```

## Step 7: Iterate on Errors (max 3 rounds)

For any failed skill execution or packaging step:

1. Log the error to `/app/results/work/error_log.json`
2. Apply the fix from the table below:

| Error | Fix |
|-------|-----|
| Website unreachable | Skip company, flag in final report, continue with others |
| Skill failure | Retry once; if still fails, log error, skip that strategy, continue |
| Budget exceeded | Stop execution for that company, package whatever was completed |
| Rate limiting | Exponential backoff, max 3 retries (wait 5s, 15s, 45s) |
| No executable strategies | Generate all strategies, flag that manual selection needed |
| API call >$2 | Pause and confirm with user (**Human Checkpoint 3**) |

After 3 rounds, if a company's processing is still failing, mark it as `partial` in the final report and continue with remaining companies.

## Step 8: Final Report & Output

After all companies are packaged, write the batch summary.

```python
import json, pathlib, datetime

# Aggregate results from all companies
companies = json.loads(pathlib.Path("/app/results/work/validated_companies.json").read_text())
cost_tracker = json.loads(pathlib.Path("/app/results/work/cost_tracker.json").read_text()) if pathlib.Path("/app/results/work/cost_tracker.json").exists() else {}

lines = ["# Batch Complete\n"]
lines.append(f"| Company | Strategies | Executed | Leads | Content | Total Cost |")
lines.append(f"|---------|------------|----------|-------|---------|------------|")

for co in companies:
    name = co['name']
    stats = cost_tracker.get(name, {})
    lines.append(f"| {name} | {stats.get('strategies_generated', '?')} | {stats.get('strategies_executed', '?')} | {stats.get('leads_found', '?')} | {stats.get('content_assets', '?')} | ${stats.get('total_cost', 0):.2f} |")

total_budget = 5.00 * len(companies)
total_spent = sum(cost_tracker.get(co['name'], {}).get('total_cost', 0) for co in companies)
lines.append(f"\nTotal cost: ${total_spent:.2f} / ${total_budget:.2f} budget")
lines.append(f"Packets saved to: /app/results/clients/<company>/client-package/<date>/")

pathlib.Path("/app/results/summary.md").write_text("\n".join(lines))
```

Write `/app/results/validation_report.json` with stage results and `overall_passed`.

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"

# Check required top-level files
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Check per-company outputs
for co_dir in "$RESULTS_DIR/clients"/*/; do
  COMPANY=$(basename "$co_dir")
  for f in \
    "$co_dir/intelligence-package.md" \
    "$co_dir/growth-strategies.md"; do
    if [ ! -s "$f" ]; then
      echo "FAIL: $COMPANY — $f is missing or empty"
    else
      echo "PASS: $COMPANY — $(basename $f) exists"
    fi
  done
  PACKET_DIR=$(ls -d "$co_dir/client-package/"*/ 2>/dev/null | head -1)
  if [ -n "$PACKET_DIR" ] && [ -s "${PACKET_DIR}summary.md" ]; then
    echo "PASS: $COMPANY — client-package present"
  else
    echo "FAIL: $COMPANY — client-package/summary.md missing"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `summary.md` exists and covers all companies processed
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Each company has `intelligence-package.md` and `growth-strategies.md`
- [ ] Each company has a dated `client-package/` directory with `summary.md`
- [ ] Cost stayed within budget for each company (or overruns are documented)
- [ ] All `manual` pattern strategies produced plan documents
- [ ] Pitch-packet mode was maintained (no real emails sent, no paid Apollo credits spent)
- [ ] Verification script printed PASS for every required file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Pitch-packet mode is the default safety net.** Never set `pitch_packet_mode: false` without explicit user confirmation — it enables live campaign execution with real costs.
- **Parallelize aggressively but within limits.** Phase 1 caps at 3 concurrent companies; Phase 3 caps at 5 concurrent strategy executions. Exceeding these limits risks rate limiting and cost overruns.
- **Human checkpoints are non-negotiable.** There are three: (1) cost estimate approval, (2) strategy selection, (3) any single API call >$2. Do not auto-approve any of these.
- **Budget tracking is cumulative.** Phase 1 and Phase 3 costs both count toward the per-company budget. Track running totals after every skill call.
- **Warn early on large batches.** More than 10 companies will produce very long runtimes and potentially exceed budget. Surface this warning clearly before starting.
- **`manual` strategies still need output.** Generate a detailed execution plan document for each manual strategy even though no automation runs.
- **Retry once, then skip.** If a skill fails, retry exactly once. If it fails again, log the error, skip that strategy, and continue — do not block the whole batch on one failure.
