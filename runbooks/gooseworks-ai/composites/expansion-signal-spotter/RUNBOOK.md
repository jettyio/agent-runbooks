---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/expansion-signal-spotter/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/expansion-signal-spotter
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Expansion Signal Spotter
  imported_at: '2026-05-03T02:54:33Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: expansion-signal-spotter
    confidence: high
secrets: null
---

# Expansion Signal Spotter — Agent Runbook

## Objective

Monitor existing customer accounts for expansion signals and turn those signals into a prioritized weekly opportunity report. The runbook scans public web, hiring, funding, product-usage, and stakeholder-change signals, scores opportunities by signal strength, account value, and timing, then produces talk tracks for customer-facing follow-up. Use it when customer success, sales, or founders need a repeatable way to find upsell, cross-sell, or volume expansion opportunities in the existing customer base.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/expansion_signal_report.md` | Weekly expansion opportunity report with Hot, Warm, and Watch opportunities |
| `/app/results/account_signal_data.json` | Structured account-level signals, sources, scores, and recommended plays |
| `/app/results/talk_tracks.md` | Customer-ready talk tracks for Hot and Warm opportunities |
| `/app/results/summary.md` | Executive summary of the run, inputs, top opportunities, and issues |
| `/app/results/validation_report.json` | Programmatic validation report for required outputs and scoring checks |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Results directory | `results_dir` | `/app/results` | Output directory for all required files |
| Customer list | `customer_list` | required | CSV or sheet of customer accounts with domain, plan, MRR/ARR, seats, usage, and primary contact details |
| Product tiers | `product_tiers` | required | Available plans, upgrade triggers, limits, and packaging |
| Cross-sell products | `cross_sell_products` | optional | Add-ons or adjacent products to evaluate against each account |
| Expansion triggers | `expansion_triggers` | optional | Signal definitions that indicate readiness to buy more |
| Key contacts | `key_contacts` | optional | Champion and decision-maker profiles to monitor |
| Minimum account value | `minimum_account_value` | optional | Revenue floor for scanned accounts |
| Accounts to exclude | `accounts_to_exclude` | optional | Churn-risk, paused, disputed, or otherwise excluded accounts |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Web search capability | Tool | Yes | Search hiring, funding, company news, launches, partnerships, and executive changes |
| Webpage fetch capability | Tool | Yes | Read career pages, press releases, company announcements, and public profile pages |
| Product usage export | Data | Optional | Seats, quota consumption, feature adoption, API usage, and department-level usage trends |
| LinkedIn/profile monitoring | Tool | Optional | Monitor champion promotions, departures, role changes, and stakeholder announcements |
| Job posting detection | Tool | Optional | Extract structured hiring signals from career pages and public job listings |

## Step 1: Environment Setup

1. Create `/app/results` and confirm it is writable.
2. Resolve all required inputs: customer list, product tiers, and any account filters.
3. Normalize account records so each account has a company name, domain, current plan, current revenue, seat or usage information when available, and primary contact.
4. Write a setup entry into `/app/results/validation_report.json` if any required input is missing, then stop before scanning.

## Step 2: Load Account Data

Read the customer list from the supplied CSV, sheet, CRM export, or structured text. For each account, capture company name, domain, primary contact LinkedIn URL, current plan or tier, MRR or ARR, seats, usage, and any notes that affect expansion eligibility.

Exclude accounts that are in active churn risk, paused, in dispute, below the configured minimum account value, or explicitly listed in `accounts_to_exclude`.

## Step 3: Detect Expansion Signals

For each eligible account, run targeted searches for recent hiring, funding, revenue, product launch, partnership, geographic expansion, and category-specific news signals. Include searches such as:

```text
"[company name]" hiring OR "we're hiring" OR "join our team"
site:linkedin.com/jobs "[company name]" [relevant role keywords]
"[company name]" funding OR raised OR series OR investment
"[company name]" launch OR "new product" OR partnership OR expansion
```

When usage data is available, flag accounts approaching plan limits, adopting higher-tier features, showing power-user behavior, spreading across multiple teams, or increasing API usage. When stakeholder data is available, detect champion promotions, champion departures, and new executive sponsors.

## Step 4: Score Opportunities

Compute an expansion score for each account:

```text
Expansion Score = Signal Strength x Account Value x Timing
```

Use signal strength from 1 to 5, account value multipliers of 2.0x for top accounts, 1.5x for mid-tier accounts, and 1.0x for smaller accounts, and timing multipliers of 2.0x for signals detected this week, 1.5x for this month, and 1.0x for older signals.

Classify opportunities as Hot for scores of 15 or more, Warm for 8 to 14, and Watch for 3 to 7.

## Step 5: Generate Talk Tracks

For every Hot and Warm opportunity, write a talk track that connects the detected signal to the customer’s business goal, identifies the expansion type, estimates additional MRR when possible, names the timing reason, and lists the main risk or blocker.

Use this structure for each account:

```markdown
ACCOUNT: [Company Name]
CURRENT PLAN: [Plan] - $[MRR]/mo
EXPANSION TYPE: [Upsell / Cross-sell / Volume increase]
ESTIMATED EXPANSION: $[additional MRR]/mo

SIGNALS:
- [Signal] - [Source + date]

EXPANSION OPPORTUNITY:
[What they should buy and why now]

TALK TRACK:
"[Opening line tied to their business goal]"
"[Value bridge]"
"[Soft ask]"

TIMING: [Why now]
RISK: [Likely blocker]
```

## Step 6: Produce Required Outputs

Write `/app/results/expansion_signal_report.md` with the weekly report, including accounts scanned, total expansion pipeline identified, Hot/Warm/Watch summaries, account-level recommendations, trends, and the top three priorities for the week.

Write `/app/results/account_signal_data.json` with account names, detected signals, source URLs or citations, signal dates, scores, tiers, expansion plays, and follow-up recommendations.

Write `/app/results/talk_tracks.md` with all generated talk tracks for Hot and Warm opportunities.

## Step 7: Validate Outputs

Run structural checks before finishing:

```bash
echo "=== EXPANSION SIGNAL OUTPUT VALIDATION ==="
test -s /app/results/expansion_signal_report.md
test -s /app/results/account_signal_data.json
test -s /app/results/talk_tracks.md
test -s /app/results/summary.md
test -s /app/results/validation_report.json
python -m json.tool /app/results/account_signal_data.json >/dev/null
python -m json.tool /app/results/validation_report.json >/dev/null
```

The validation report must record the number of accounts scanned, the number of opportunities by tier, the total potential expansion MRR when estimable, and whether every required output exists.

## Step 8: Iterate on Errors (max 3 rounds)

If any required output is missing, any JSON file fails to parse, or a Hot/Warm opportunity lacks a signal source, perform up to max 3 rounds of targeted repair. Re-run only the failed scan, scoring, or output-generation step, then repeat validation. After 3 rounds, write remaining failures into `/app/results/summary.md` and set `overall_passed` to `false` in `/app/results/validation_report.json`.

## Common Fixes

| Issue | Fix |
|---|---|
| Customer list lacks domains | Search company names to infer official domains, then mark inferred domains in `account_signal_data.json` |
| Usage data is unavailable | Score using public signals only and note the limitation in the summary |
| Signal source is stale | Lower the timing multiplier or move the account to Watch |
| Expansion value is unknown | Use `null` for estimated MRR and rank by signal strength and account value |
| JSON validation fails | Re-emit the affected JSON with strict double-quoted keys and values |

## Scheduling

Run weekly, preferably before customer-success pipeline review:

```bash
0 8 * * 2 python3 run_skill.py expansion-signal-spotter
```

## Cost

| Component | Expected Cost |
|---|---|
| Web search for hiring, funding, and news | Free |
| LinkedIn/profile monitoring | About $0.50-$1.00 when an external scraper is used |
| Job posting detection | About $0.50 when an external structured detector is used |
| Analysis and talk tracks | Free, apart from model/runtime cost |

## Tips

Prioritize fresh, source-backed signals over weak historical indicators. The strongest expansion opportunities usually combine a usage signal with an external business signal and a clear timing reason.

## Final Checklist

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/expansion_signal_report.md" \
  "$RESULTS_DIR/account_signal_data.json" \
  "$RESULTS_DIR/talk_tracks.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python -m json.tool "$RESULTS_DIR/account_signal_data.json" >/dev/null && echo "PASS: account signal JSON parses"
python -m json.tool "$RESULTS_DIR/validation_report.json" >/dev/null && echo "PASS: validation JSON parses"
```
