---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/playbooks/outbound-prospecting-engine/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/outbound-prospecting-engine
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Outbound Prospecting Engine
  imported_at: '2026-05-03T02:45:30Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: outbound-prospecting-engine
    confidence: high
secrets: null
---

# Outbound Prospecting Engine — Agent Runbook

## Objective

End-to-end outbound prospecting: detect intent signals, research companies, find decision-maker contacts, personalize messaging, launch campaign. This runbook turns that playbook into a repeatable Jetty workflow that detects intent signals, qualifies accounts, finds decision makers, personalizes outreach, launches a campaign, and records results. Operators should use it when they have client positioning, target customer criteria, signal keywords, and approved outreach guidance. The workflow includes human review checkpoints before contact enrichment, campaign launch, and campaign iteration.

## REQUIRED OUTPUT FILES (MANDATORY)

Write all files to `/app/results`. The task is not complete until every file exists and is non-empty.

| File | Description |
|---|---|
| `/app/results/signal_sources.json` | Selected signal sources and the rationale for each source |
| `/app/results/raw_signals.csv` | Raw signal list with companies and signal context |
| `/app/results/qualified_leads.csv` | ICP-filtered and scored lead list |
| `/app/results/contacts.csv` | Decision-maker contacts for qualified companies |
| `/app/results/outreach_sequences.md` | Personalized outreach copy or segment-level sequence copy |
| `/app/results/campaign_launch_plan.md` | Campaign setup details, schedule, mailbox allocation, and launch checklist |
| `/app/results/metrics_review.md` | Campaign metrics, test results, and iteration recommendations |
| `/app/results/summary.md` | Executive summary of actions taken, outputs produced, and next operating cadence |
| `/app/results/validation_report.json` | Structured validation results with stages, output files, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Directory where all required output files are written |
| `client_context` | Required | Client context file or brief containing ICP, value props, positioning, excluded accounts, and offer details |
| `ideal_customer_profile` | Required | Account and persona criteria used to qualify companies and decision makers |
| `signal_keywords` | Required | Keywords, roles, products, pain terms, competitors, or events used for signal detection |
| `approved_messaging_or_email_sequences` | Optional | Approved messaging, prior sequences, tone guidance, compliance notes, or permission to draft new copy |
| `campaign_tool` | Operator choice | Outreach platform used for launch, such as a cold email or sales engagement tool |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Client context and ICP | Input data | Yes | Defines the target accounts, target titles, value proposition, and qualification rules |
| Signal data sources | External data | Yes | Job postings, funding announcements, LinkedIn activity, event attendance, competitor engagement, or equivalent sources |
| `lead-qualification` | Skill / workflow | Yes | Filters and scores companies against ICP criteria |
| `company-contact-finder` | Skill / workflow | Yes | Finds target decision makers, emails, and LinkedIn URLs |
| `contact-cache` | Skill / workflow | Yes | Deduplicates prospects and records outreach history |
| `cold-email-outreach` | Skill / workflow | Yes | Creates and schedules the outbound campaign |
| Outreach platform access | External system | Yes | Required to upload leads, allocate mailboxes, schedule sends, and monitor outcomes |

## Step 1: Environment Setup

1. Create `results_dir` and confirm it is writable.
2. Load the client context, ICP, signal keywords, and any approved messaging.
3. Confirm access to the selected signal sources, contact enrichment workflow, contact cache, and outreach platform.
4. Initialize `validation_report.json` with setup status and an empty stage list.

## Step 2: Define Signal Sources

Select the signal sources that best match the client's ICP and sales motion. Include at least one source and prefer multiple independent intent signals when available.

| Signal Source | Best For | Related Skill |
|---|---|---|
| Job postings | Companies with allocated budget | `job-posting-intent` |
| Funding announcements | Companies with fresh capital | `funding-signal-monitor` |
| LinkedIn posts/comments | Practitioners discussing the problem | `linkedin-post-research`, `linkedin-commenter-extractor` |
| Conference attendees | People actively engaged with the space | `luma-event-attendees` |
| Competitor customers | Companies already buying similar solutions | `competitor-post-engagers` |

Write `/app/results/signal_sources.json` with selected sources, keywords, inclusion rules, and rationale.

## Step 3: Run Signal Detection

Execute the selected signal workflows with the client-specific keywords. Run sources in parallel when tooling allows. Preserve the source, company name, signal date, signal text, URL, and the reason the signal matters.

Write `/app/results/raw_signals.csv` with one row per observed company signal.

## Step 4: Qualify and Score Leads

Use `lead-qualification` to filter the raw signal list against the ICP. Score leads consistently:

- Multi-signal leads are highest priority.
- Job posting plus funding is the strongest intent pattern.
- Single social mention is lower confidence unless the post clearly names the pain or buying motion.

Pause for the human checkpoint after this step. Write `/app/results/qualified_leads.csv` with score, score rationale, fit notes, and disqualification reason when applicable.

## Step 5: Find Decision-Maker Contacts

For top qualified companies, use `company-contact-finder` to find the specific decision makers named by the ICP. Capture target title, name, company, email address, LinkedIn URL, source URL, and confidence.

Write `/app/results/contacts.csv`. Do not continue with contacts that are missing required consent, deliverability, or compliance checks for the operator's outreach policy.

## Step 6: Deduplicate Against Contact Cache

Use `contact-cache` to check all leads against previous outreach history. Add new contacts to the cache, skip contacts or companies already contacted within the configured cooldown, and record the deduplication decision in the contacts output.

## Step 7: Personalize Outreach

Generate a personalized 2-3 message sequence for each lead or segment using:

- The signal that surfaced the account as the why-now hook.
- Company context and likely pain.
- The client's value proposition and relevant proof.

Pause for the human checkpoint after this step. Write `/app/results/outreach_sequences.md` with copy grouped by company, persona, or segment.

## Step 8: Launch Campaign

Use `cold-email-outreach` or the selected campaign tool to create the campaign, upload the approved lead list, configure the sequence, allocate mailboxes, and set the sending schedule.

Write `/app/results/campaign_launch_plan.md` with campaign name, schedule, audience, exclusions, mailbox allocation, final send counts, and any items intentionally left unlaunched.

## Step 9: Monitor and Iterate (max 3 rounds)

Review open rates, reply rates, positive reply rate, meeting bookings, bounces, unsubscribes, and account-quality feedback. Run at most 3 rounds of iteration in a single execution: adjust subject lines, improve the why-now hook, refine segmentation, and add new leads from fresh signal detection.

Write `/app/results/metrics_review.md` after each review round and keep the latest recommendation at the top.

## Step 10: Ongoing Cadence

Document the operating cadence for the client:

- Weekly: re-run signal detection, qualify new leads, and add eligible leads to campaign.
- Bi-weekly: review campaign metrics and adjust messaging.
- Monthly: review pipeline contribution and adjust signal sources.

Include the cadence in `/app/results/summary.md`.

## Step 11: Final Checklist

Before finishing, run this verification script and fix any failure:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/signal_sources.json" \
  "$RESULTS_DIR/raw_signals.csv" \
  "$RESULTS_DIR/qualified_leads.csv" \
  "$RESULTS_DIR/contacts.csv" \
  "$RESULTS_DIR/outreach_sequences.md" \
  "$RESULTS_DIR/campaign_launch_plan.md" \
  "$RESULTS_DIR/metrics_review.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

The run is complete only when every required output file exists, human checkpoints have been recorded, and `validation_report.json` has `overall_passed=true` or clearly names the remaining manual blocker.

## Common Fixes

| Issue | Fix |
|---|---|
| Signal list is too broad | Tighten ICP filters, require stronger keywords, or prioritize multi-signal accounts |
| Not enough qualified leads | Add another signal source, broaden title filters, or re-run with adjacent pain keywords |
| Contact confidence is low | Re-run enrichment, verify with a secondary source, or move the account to manual review |
| Outreach copy is generic | Add the exact signal, company-specific context, and one concrete value proposition |
| Campaign should not launch yet | Stop after writing the launch plan and mark the blocking approval in `summary.md` |

## Tips

Use the signal that surfaced each company as the core personalization hook. Keep the contact cache current so weekly re-runs expand coverage without repeatedly contacting the same people.
