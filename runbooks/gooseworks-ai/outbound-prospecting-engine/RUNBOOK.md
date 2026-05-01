---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/outbound-prospecting-engine/SKILL.md"
  source_host: "github.com"
  source_title: "Outbound Prospecting Engine"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    skill_name: "outbound-prospecting-engine"
    confidence: "high"
secrets: {}
---

# Outbound Prospecting Engine — Agent Runbook

## Objective

Build and run a complete outbound prospecting system that moves from intent-signal detection through company research, decision-maker contact finding, personalized messaging, and campaign launch. The agent detects buying signals (job postings, funding announcements, LinkedIn activity), qualifies and scores leads against an ICP, finds verified contact information, generates personalized email sequences, and sets up a Smartlead campaign. An ongoing weekly cadence keeps the pipeline fresh with new leads and continuously improves messaging based on campaign metrics.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/signal_report.md` | Summary of detected intent signals per source with company list |
| `/app/results/qualified_leads.json` | Scored and filtered lead list with ICP match rationale |
| `/app/results/contacts.json` | Decision-maker contacts (name, title, email, LinkedIn URL) |
| `/app/results/email_sequences.md` | Personalized email sequences per lead or segment |
| `/app/results/campaign_config.json` | Smartlead campaign configuration (name, schedule, mailboxes) |
| `/app/results/campaign_summary.md` | Post-launch campaign overview with performance baseline |
| `/app/results/summary.md` | Executive summary with run metadata and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `icp-criteria` | *(required)* | Path to ICP criteria document (titles, firmographics, pain points) |
| `signal-keywords` | *(required)* | Keywords and phrases to monitor for intent signals |
| `client-context` | *(required)* | Path to `context.md` with value props, positioning, approved messaging |
| Signal sources | `job-postings,funding` | Comma-separated list of signal sources to enable |
| Campaign name | `outbound-<date>` | Name for the Smartlead campaign |
| Max leads per run | `100` | Maximum leads to process per execution |
| Dry run | `false` | If `true`: generate outputs but do NOT launch the campaign |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `job-posting-intent` | Skill | Conditional | Detect companies with active hiring that matches ICP |
| `linkedin-post-research` | Skill | Conditional | Find LinkedIn posts discussing target problem space |
| `linkedin-commenter-extractor` | Skill | Conditional | Extract commenters from relevant LinkedIn posts |
| `funding-signal-monitor` | Skill | Conditional | Detect companies with recent funding announcements |
| `company-contact-finder` | Skill | Yes | Find decision-maker contacts at qualified companies |
| `lead-qualification` | Skill | Yes | Score and filter raw signals against ICP criteria |
| `contact-cache` | Skill | Yes | Deduplicate contacts; skip previously contacted leads |
| `setup-outreach-campaign` | Skill | Yes | Configure and launch Smartlead campaign |
| `agentmail` | Skill | Conditional | Alternative mailbox allocation if Smartlead unavailable |
| Smartlead API | External API | Yes | Campaign creation and management |
| LinkedIn | External API | Conditional | Required for LinkedIn signal sources |

## Step 1: Environment Setup

Verify all required inputs and credentials before proceeding.

```bash
# Verify required inputs are set
for var in ICP_CRITERIA_PATH SIGNAL_KEYWORDS CLIENT_CONTEXT_PATH; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var is not set"
    exit 1
  fi
done

# Create output directories
mkdir -p /app/results

# Verify at least one signal source is configured
if [ -z "$SIGNAL_SOURCES" ]; then
  SIGNAL_SOURCES="job-postings,funding"
  echo "Using default signal sources: $SIGNAL_SOURCES"
fi

echo "Environment verified. Signal sources: $SIGNAL_SOURCES"
echo "ICP: $ICP_CRITERIA_PATH"
echo "Client context: $CLIENT_CONTEXT_PATH"
```

## Step 2: Define Signal Sources

Based on the client's ICP and motion, select and configure signal sources. Run detection skills in parallel for efficiency.

| Signal Source | Best For | Skill |
|--------------|---------|-------|
| Job postings | Companies with allocated budget | `job-posting-intent` |
| Funding announcements | Companies with fresh capital | `funding-signal-monitor` |
| LinkedIn posts/comments | Practitioners discussing the problem | `linkedin-post-research` + `linkedin-commenter-extractor` |
| Conference attendees | People actively engaged with the space | `luma-event-attendees` |
| Competitor customers | Companies already buying similar solutions | `eightfold-customer-finder` |

```python
import json, pathlib

signal_sources = [s.strip() for s in "${SIGNAL_SOURCES}".split(",")]
client_context = pathlib.Path("${CLIENT_CONTEXT_PATH}").read_text()
signal_keywords = "${SIGNAL_KEYWORDS}".split(",")

config = {
    "enabled_sources": signal_sources,
    "keywords": signal_keywords,
    "icp_criteria_path": "${ICP_CRITERIA_PATH}",
    "client_context_path": "${CLIENT_CONTEXT_PATH}"
}
print(f"Configured {len(signal_sources)} signal sources: {signal_sources}")
```

## Step 3: Run Signal Detection (max 3 rounds per source)

Execute all enabled signal skills with client-specific keywords. Re-try each source up to 3 rounds if the initial run returns zero results.

```python
# Run each enabled signal source skill
raw_signals = []

for source in signal_sources:
    print(f"Running signal detection: {source}")
    # Invoke the appropriate skill with keywords and ICP criteria
    # results = invoke_skill(source, keywords=signal_keywords, icp=icp_criteria)
    # raw_signals.extend(results)

print(f"Total raw signals detected: {len(raw_signals)}")
```

**Output**: Raw signal list — companies + signal context.

## Step 4: Qualify & Score Leads

**Skill**: `lead-qualification`

Filter the raw signal list against ICP criteria. Score each lead:
- Multi-signal leads = highest priority
- Job posting + funding = strongest intent
- Single social mention = lowest (awareness only)

```python
import json, pathlib

# Load ICP criteria
icp = pathlib.Path("${ICP_CRITERIA_PATH}").read_text()

qualified = []
for signal in raw_signals:
    # score = qualify_lead(signal, icp_criteria=icp)
    # if score > threshold:
    #     qualified.append({**signal, "score": score})
    pass

# Enforce max leads limit
qualified = sorted(qualified, key=lambda x: x.get("score", 0), reverse=True)
qualified = qualified[:int("${MAX_LEADS:-100}")]

pathlib.Path("/app/results/qualified_leads.json").write_text(json.dumps(qualified, indent=2))
print(f"Qualified {len(qualified)} leads")
```

**Human Checkpoint**: Review `/app/results/qualified_leads.json` before proceeding to contact finding.

## Step 5: Find Decision-Maker Contacts

**Skill**: `company-contact-finder`

For top qualified companies, find the specific decision-makers matching ICP target titles.

```python
import json, pathlib

qualified_leads = json.loads(pathlib.Path("/app/results/qualified_leads.json").read_text())
contacts = []

for lead in qualified_leads:
    # contact_info = find_contacts(
    #     company=lead["company"],
    #     target_titles=icp["target_titles"]
    # )
    # contacts.extend(contact_info)
    pass

pathlib.Path("/app/results/contacts.json").write_text(json.dumps(contacts, indent=2))
print(f"Found {len(contacts)} contacts")
```

## Step 6: Deduplicate via Contact Cache

**Skill**: `contact-cache`

Check all leads against the contact cache. Skip any that have been contacted before. Add new leads to cache after deduplication.

```python
import json, pathlib

contacts = json.loads(pathlib.Path("/app/results/contacts.json").read_text())
new_contacts = []

for contact in contacts:
    # if not contact_cache.exists(contact["email"]):
    #     new_contacts.append(contact)
    #     contact_cache.add(contact)
    pass

pathlib.Path("/app/results/contacts.json").write_text(json.dumps(new_contacts, indent=2))
print(f"After deduplication: {len(new_contacts)} net-new contacts")
```

## Step 7: Personalize Outreach

For each lead, generate a personalized email sequence using:
- The signal that surfaced them (the "why now")
- Their company context (what they do, their pain)
- The client's value proposition (how it solves their pain)

```python
import json, pathlib

contacts = json.loads(pathlib.Path("/app/results/contacts.json").read_text())
client_context = pathlib.Path("${CLIENT_CONTEXT_PATH}").read_text()
sequences = []

for contact in contacts:
    # sequence = generate_sequence(
    #     contact=contact,
    #     signal=contact["signal"],
    #     client_context=client_context
    # )
    # sequences.append({"contact": contact["email"], "sequence": sequence})
    pass

output = "\n\n---\n\n".join([
    f"## {s['contact']}\n\n{s['sequence']}" for s in sequences
])
pathlib.Path("/app/results/email_sequences.md").write_text(output)
print(f"Generated sequences for {len(sequences)} contacts")
```

**Human Checkpoint**: Review `/app/results/email_sequences.md` before launching the campaign.

## Step 8: Launch Campaign

**Skill**: `setup-outreach-campaign`

Set up a Smartlead campaign with the personalized lead list.

```python
import json, pathlib
from datetime import datetime

if "${DRY_RUN:-false}" == "true":
    print("DRY RUN: Skipping campaign launch")
    campaign_config = {"dry_run": True, "status": "skipped"}
else:
    contacts = json.loads(pathlib.Path("/app/results/contacts.json").read_text())
    campaign_config = {
        "name": "${CAMPAIGN_NAME:-outbound-}" + datetime.utcnow().strftime("%Y%m%d"),
        "leads": contacts,
        "sequence_count": 3,
        "schedule": "business_hours",
        "status": "launched"
    }
    # campaign = smartlead.create_campaign(campaign_config)
    # campaign = smartlead.upload_leads(campaign["id"], contacts)
    # campaign = smartlead.set_schedule(campaign["id"])

pathlib.Path("/app/results/campaign_config.json").write_text(json.dumps(campaign_config, indent=2))
print(f"Campaign configured: {campaign_config.get('name')}")
```

## Step 9: Monitor & Report

Track initial campaign metrics and write the campaign summary.

```python
import json, pathlib
from datetime import datetime

contacts = json.loads(pathlib.Path("/app/results/contacts.json").read_text())
campaign_config = json.loads(pathlib.Path("/app/results/campaign_config.json").read_text())

summary = f"""# Campaign Summary

**Date**: {datetime.utcnow().strftime("%Y-%m-%d")}
**Campaign**: {campaign_config.get("name", "N/A")}
**Status**: {campaign_config.get("status", "unknown")}
**Total contacts uploaded**: {len(contacts)}
**Email sequences**: 3-touch

## Ongoing Cadence

- **Weekly**: Re-run signal detection, qualify new leads, add to campaign
- **Bi-weekly**: Review campaign metrics, adjust messaging
- **Monthly**: Review overall pipeline contribution, adjust signal sources

## Human Checkpoints Completed

- [ ] Qualified lead list reviewed (Step 4)
- [ ] Personalized email copy reviewed (Step 7)
- [ ] Campaign performance reviewed (post-launch)
"""

pathlib.Path("/app/results/campaign_summary.md").write_text(summary)
print("Campaign summary written")
```

## Step 10: Iterate on Errors (max 3 rounds)

If any step fails (signal detection returns 0 results, contact finder errors, campaign creation fails):

1. Read the error from the relevant output file or exception
2. Apply targeted fixes from the table below
3. Re-run the failing step only
4. Repeat up to 3 times per step

### Common Fixes

| Issue | Fix |
|-------|-----|
| Signal detection returns 0 results | Broaden keywords; try alternate signal source |
| Contact finder returns no emails | Widen target titles; check company size filter |
| All contacts already in cache | Extend lookback window for signal detection |
| Campaign creation fails | Verify Smartlead API key; check mailbox allocation |
| Email sequences are generic | Enrich contact with more signal context before generation |

## Step 11: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/signal_report.md" \
  "$RESULTS_DIR/qualified_leads.json" \
  "$RESULTS_DIR/contacts.json" \
  "$RESULTS_DIR/email_sequences.md" \
  "$RESULTS_DIR/campaign_config.json" \
  "$RESULTS_DIR/campaign_summary.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `signal_report.md` lists all detected signals with company context
- [ ] `qualified_leads.json` shows ICP match scores and rationale
- [ ] `contacts.json` contains verified emails and LinkedIn URLs
- [ ] `email_sequences.md` reviewed and approved before launch
- [ ] `campaign_config.json` reflects actual Smartlead campaign settings
- [ ] `campaign_summary.md` shows launch status and contact count
- [ ] `summary.md` exists with run metadata
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] All human checkpoints completed (Step 4 lead review, Step 7 copy review)

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Run signal sources in parallel** when possible — job-posting and funding detection are independent and can be executed concurrently to reduce total runtime.
- **Multi-signal leads are highest priority.** A company showing up in both job postings and a funding announcement has strong buying intent — prioritize these in the contact-finding and personalization steps.
- **Personalization drives reply rates.** The "why now" signal (what surfaced this company) is the most important personalization variable — always include it in the email opener.
- **Contact cache is append-only.** Never reset or clear the cache between runs — it protects against contacting the same person twice across campaigns.
- **Human checkpoints exist for a reason.** Do not skip the review steps for qualified leads and email copy — these are the highest-leverage points for quality control before spending sending credits.
- **A/B test systematically.** When adjusting subject lines or messaging, change one variable at a time so you can attribute performance differences.
