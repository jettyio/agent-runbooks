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
    source_collection: "playbooks"
    skill_name: "outbound-prospecting-engine"
    confidence: "high"
secrets: {}
---

# Outbound Prospecting Engine — Agent Runbook

## Objective

Build and run a complete end-to-end outbound prospecting system: detect intent signals from job postings, funding announcements, and social media, research target companies, find decision-maker contacts, generate personalized messaging, and launch a Smartlead outreach campaign. The agent monitors multiple signal sources in parallel, qualifies leads against ICP criteria, deduplicates contacts via a shared cache, and outputs a running meeting pipeline. Re-running weekly keeps the prospect pool fresh and the campaign optimized.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/signals.json` | Raw signal list — companies and signal context from all sources |
| `/app/results/qualified_leads.json` | Scored and filtered lead list after ICP qualification |
| `/app/results/contacts.json` | Decision-maker contact details (name, title, email, LinkedIn) |
| `/app/results/email_sequences.json` | Personalized email sequences per lead or segment |
| `/app/results/campaign_config.json` | Smartlead campaign configuration (name, schedule, mailboxes) |
| `/app/results/campaign_result.json` | Result from campaign launch (campaign ID, lead count, status) |
| `/app/results/summary.md` | Executive summary with run metadata, lead counts, campaign link, and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| ICP criteria | *(required)* | Path or inline definition of ideal customer profile |
| Signal keywords | *(required)* | Keywords for intent signal monitoring (job titles, technologies, pain phrases) |
| Client context | *(required)* | Path to `client-context.md` with value props, positioning, and approved messaging |
| Signal sources | `job-postings,funding,linkedin-posts` | Comma-separated list of sources to activate |
| Max leads per run | `50` | Cap on qualified leads per weekly cycle |
| Campaign name | *(derived from client context)* | Smartlead campaign name |
| Dry run | `false` | If `true`, generate all outputs but do NOT launch the campaign |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `job-posting-intent` | Skill | Conditional | Detect companies with active budget signals via job postings |
| `linkedin-post-research` | Skill | Conditional | Find LinkedIn posts discussing the client's problem space |
| `linkedin-commenter-extractor` | Skill | Conditional | Extract commenters on high-signal LinkedIn posts |
| `funding-signal-monitor` | Skill | Conditional | Detect companies with fresh capital (Series A–C, seed) |
| `company-contact-finder` | Skill | Yes | Find decision-maker emails and LinkedIn URLs at target companies |
| `lead-qualification` | Skill | Yes | Score and filter companies against ICP criteria |
| `contact-cache` | Skill | Yes | Deduplicate contacts against previously contacted leads |
| `setup-outreach-campaign` | Skill | Yes | Create and configure a Smartlead campaign |
| `agentmail` | Skill | Conditional | Send emails via agent-managed mailboxes if Smartlead is unavailable |
| Smartlead API | External API | Yes | Campaign creation, lead upload, mailbox allocation |
| LinkedIn | External API | Conditional | Required for linkedin-post-research and linkedin-commenter-extractor |

---

## Step 1: Environment Setup

```bash
# Verify required output directory
mkdir -p /app/results

# Confirm required inputs exist
for var in ICP_CRITERIA SIGNAL_KEYWORDS CLIENT_CONTEXT; do
  if [ -z "${!var}" ]; then
    echo "WARNING: $var not set — will prompt during execution"
  fi
done

echo "=== Environment ready ==="
```

Verify the client context file is accessible. If `CLIENT_CONTEXT` points to a
file path, confirm it exists and is non-empty before proceeding.

---

## Step 2: Define Signal Sources

Based on the client's ICP and motion, select which intent signals to monitor.
Run enabled signal skills **in parallel** to maximize throughput.

| Signal Source | Best For | Skill |
|---------------|----------|-------|
| Job postings | Companies with allocated budget | `job-posting-intent` |
| Funding announcements | Companies with fresh capital | `funding-signal-monitor` |
| LinkedIn posts/comments | Practitioners discussing the problem | `linkedin-post-research` + `linkedin-commenter-extractor` |
| Conference attendees | People actively engaged with the space | `luma-event-attendees` |
| Competitor customers | Companies already buying similar solutions | `eightfold-customer-finder` |

```python
# Pseudocode — replace with actual skill invocations
import json, pathlib

SIGNAL_SOURCES = ["job-postings", "funding", "linkedin-posts"]  # from Parameters

signals = []

if "job-postings" in SIGNAL_SOURCES:
    # Invoke job-posting-intent skill with SIGNAL_KEYWORDS
    pass

if "funding" in SIGNAL_SOURCES:
    # Invoke funding-signal-monitor skill
    pass

if "linkedin-posts" in SIGNAL_SOURCES:
    # Invoke linkedin-post-research + linkedin-commenter-extractor
    pass

pathlib.Path("/app/results/signals.json").write_text(json.dumps(signals, indent=2))
print(f"Collected {len(signals)} raw signals")
```

**Output**: `/app/results/signals.json` — raw signal list with companies and signal context.

---

## Step 3: Qualify and Score Leads

**Skill**: `lead-qualification`

Filter the raw signal list against ICP criteria. Score each lead with priority
based on signal strength:
- Multi-signal leads (e.g., job posting + funding) = highest priority
- Single job posting = medium priority
- Single social mention = lowest priority (awareness only)

```python
import json, pathlib

signals = json.loads(pathlib.Path("/app/results/signals.json").read_text())

# Invoke lead-qualification skill
qualified = []
for signal in signals:
    score = 0
    if signal.get("job_posting"):
        score += 2
    if signal.get("funding"):
        score += 2
    if signal.get("linkedin_mention"):
        score += 1
    if score > 0:  # passes ICP filter
        qualified.append({**signal, "score": score})

qualified.sort(key=lambda x: x["score"], reverse=True)
qualified = qualified[:50]  # MAX_LEADS cap

pathlib.Path("/app/results/qualified_leads.json").write_text(json.dumps(qualified, indent=2))
print(f"Qualified {len(qualified)} leads")
```

**Human checkpoint**: Review `/app/results/qualified_leads.json` before proceeding to
contact finding. Confirm the lead list matches expectations before spending
API credits on contact lookup.

---

## Step 4: Find Decision-Maker Contacts

**Skill**: `company-contact-finder`

For each qualified company, find the specific decision-makers matching the
target titles defined in the ICP. Retrieve email addresses and LinkedIn URLs.

```python
import json, pathlib

leads = json.loads(pathlib.Path("/app/results/qualified_leads.json").read_text())

contacts = []
for lead in leads:
    # Invoke company-contact-finder for each company
    # Returns: [{ name, title, email, linkedin_url, company }]
    found = []  # placeholder — replace with actual skill call
    contacts.extend(found)

pathlib.Path("/app/results/contacts.json").write_text(json.dumps(contacts, indent=2))
print(f"Found {len(contacts)} contacts")
```

---

## Step 5: Deduplicate via Contact Cache

**Skill**: `contact-cache`

Check all discovered contacts against the shared contact cache to avoid
re-contacting leads that have already been reached. Add new contacts to the
cache. Skip any contact that has a prior outreach record.

```python
import json, pathlib

contacts = json.loads(pathlib.Path("/app/results/contacts.json").read_text())

# Invoke contact-cache skill: check + update
new_contacts = []
for contact in contacts:
    # If contact not in cache → keep and add to cache
    # If contact in cache → skip
    new_contacts.append(contact)  # placeholder

# Overwrite contacts with deduplicated list
pathlib.Path("/app/results/contacts.json").write_text(json.dumps(new_contacts, indent=2))
print(f"After deduplication: {len(new_contacts)} net-new contacts")
```

---

## Step 6: Personalize Outreach

For each net-new contact, generate a personalized email sequence using three
inputs: the intent signal that surfaced the lead, the company's context and
pain, and the client's value proposition from `client-context.md`.

```python
import json, pathlib

contacts = json.loads(pathlib.Path("/app/results/contacts.json").read_text())
client_context = pathlib.Path("/app/results/client_context.md").read_text() if pathlib.Path("/app/results/client_context.md").exists() else ""

sequences = []
for contact in contacts:
    sequence = {
        "contact": contact,
        "emails": [
            {
                "subject": f"[Personalized] {contact.get('company')} — re: {contact.get('signal_context', 'your growth')}",
                "body": f"Hi {contact.get('name', 'there')},\n\n[Personalize based on signal: {contact.get('signal_context')}]\n\n[Value prop from client context]\n\n[CTA]\n\nBest,\n[Sender]"
            },
            {
                "subject": "Following up",
                "body": "[Follow-up sequence email 2]"
            },
            {
                "subject": "Last note",
                "body": "[Follow-up sequence email 3]"
            }
        ]
    }
    sequences.append(sequence)

pathlib.Path("/app/results/email_sequences.json").write_text(json.dumps(sequences, indent=2))
print(f"Generated {len(sequences)} personalized sequences")
```

**Human checkpoint**: Review `/app/results/email_sequences.json` for quality and
compliance before launching the campaign. Adjust tone, subject lines, and CTAs
as needed.

---

## Step 7: Launch Campaign

**Skill**: `setup-outreach-campaign`

Set up a Smartlead campaign with the personalized sequences:

```python
import json, pathlib, os

sequences = json.loads(pathlib.Path("/app/results/email_sequences.json").read_text())
dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"

campaign_config = {
    "name": os.environ.get("CAMPAIGN_NAME", "Outbound Campaign"),
    "schedule": {"timezone": "America/New_York", "days": ["Mon", "Tue", "Wed", "Thu"], "start_hour": 9, "end_hour": 17},
    "sequences_count": len(sequences),
    "mailboxes": [],  # allocate from available pool
    "sending_limit_per_mailbox_per_day": 30
}
pathlib.Path("/app/results/campaign_config.json").write_text(json.dumps(campaign_config, indent=2))

if dry_run:
    result = {"campaign_id": None, "status": "dry_run", "lead_count": len(sequences)}
else:
    # Invoke setup-outreach-campaign skill
    result = {"campaign_id": None, "status": "launched", "lead_count": len(sequences)}

pathlib.Path("/app/results/campaign_result.json").write_text(json.dumps(result, indent=2))
print(f"Campaign result: {result}")
```

---

## Step 8: Iterate on Errors (max 3 rounds)

If any step above fails, apply targeted fixes and retry:

| Issue | Fix |
|-------|-----|
| Signal skill returns 0 results | Broaden keyword list; check API credentials |
| Lead qualification filters all leads | Relax ICP scoring threshold; review criteria |
| Contact finder returns no emails | Try alternate title variations; check API quota |
| Contact cache unavailable | Proceed without deduplication; flag in summary |
| Smartlead campaign creation fails | Check API key; verify mailbox allocation; use `agentmail` fallback |
| Email personalization is generic | Re-read client context; ensure signal context is propagated per contact |

After 3 rounds, if the same step still fails, write the failure into
`summary.md` and `validation_report.json` with `overall_passed: false`.

---

## Step 9: Monitor and Iterate (Ongoing Cadence)

After launch, establish a regular cadence for monitoring and improvement:

| Frequency | Action |
|-----------|--------|
| **Weekly** | Re-run Steps 2–7 to add new leads to the active campaign |
| **Bi-weekly** | Review open rates, reply rates, and meeting bookings; A/B test subject lines |
| **Monthly** | Assess overall pipeline contribution; adjust signal sources and ICP scoring |

Track outcomes in the contact cache so future runs avoid re-contacting cold leads.

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/signals.json" \
  "$RESULTS_DIR/qualified_leads.json" \
  "$RESULTS_DIR/contacts.json" \
  "$RESULTS_DIR/email_sequences.json" \
  "$RESULTS_DIR/campaign_config.json" \
  "$RESULTS_DIR/campaign_result.json" \
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

- [ ] `signals.json` exists and contains at least one signal entry
- [ ] `qualified_leads.json` exists with scored leads
- [ ] `contacts.json` exists with deduplicated contacts
- [ ] `email_sequences.json` exists with personalized sequences
- [ ] `campaign_config.json` exists with campaign configuration
- [ ] `campaign_result.json` exists (status may be `dry_run` if dry run mode)
- [ ] `summary.md` exists and includes lead count, campaign link or dry-run note
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Human checkpoints at Steps 3 and 6 were reviewed before proceeding
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Run signal skills in parallel.** Signal detection is independent across sources; parallel execution can cut wall-clock time by 60–80% on multi-source runs.
- **Multi-signal leads are gold.** A company showing both a job posting and a funding announcement has the strongest intent — always prioritize these in outreach sequencing.
- **Contact cache is shared state.** If multiple team members or agents run this playbook for overlapping ICPs, ensure the cache is on shared storage (not local disk) to prevent duplicate outreach.
- **Personalization requires signal context.** Generic email sequences underperform; always pass the specific signal that surfaced a lead into the personalization prompt.
- **Weekly re-runs should reuse the existing campaign.** Add new leads to the running Smartlead campaign rather than creating a new campaign each cycle to keep metrics consolidated.
- **Dry run before first launch.** On the first execution for a new client, set `DRY_RUN=true` and review `email_sequences.json` and `campaign_config.json` end-to-end before going live.
- **Human checkpoints are non-negotiable.** The qualified lead list (Step 3) and personalized copy (Step 6) must be reviewed by a human before spending outreach credits.
