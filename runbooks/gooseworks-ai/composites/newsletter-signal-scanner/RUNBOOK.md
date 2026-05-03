---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/newsletter-signal-scanner/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/newsletter-signal-scanner
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: newsletter-signal-scanner
  imported_at: '2026-05-03T02:45:40Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: newsletter-signal-scanner
    confidence: high
secrets:
  AGENTMAIL_API_KEY:
    env: AGENTMAIL_API_KEY
    description: AgentMail API key used to fetch newsletter inbox messages
    required: true
---

# Newsletter Signal Scanner — Agent Runbook

## Objective

Subscribe to and scan industry newsletters for buying signals, competitor mentions, ICP pain-language, brand mentions, and market shifts. This runbook uses an AgentMail inbox as the collection point, applies keyword campaigns to incoming newsletter emails, extracts concise signal snippets, and produces an actionable digest for marketing, sales, or competitive-intelligence teams. Use it when a team wants a repeatable intelligence feed without manually reading every newsletter.

If this import came through a directory mirror, treat the origin in frontmatter as the source of truth: `https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/newsletter-signal-scanner/SKILL.md`.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/newsletter-signals.json` | Campaign configuration used for the scan |
| `/app/results/newsletter-signals-[YYYY-MM-DD].md` | Signal digest containing matched newsletter snippets and recommended actions |
| `/app/results/summary.md` | Executive summary with run metadata and key signal counts |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Results directory | `/app/results` | Directory where all required output files are written |
| Newsletters to monitor | *(required)* | Newsletter names, sender domains, or subscription URLs to monitor |
| AgentMail inbox ID | *(required)* | Existing AgentMail inbox ID, or request creation of a new inbox before scanning |
| Keyword campaigns | *(required)* | Competitors, ICP pain-language, market-shift terms, and brand names to match |
| Digest delivery | `markdown file` | Slack channel, email recipient, or markdown file output |
| Frequency | `weekly` | Daily or weekly scan cadence |
| Config path | `/app/results/newsletter-signals.json` | Location for the persisted campaign configuration |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| `AGENTMAIL_API_KEY` | Secret | Yes | API key for AgentMail inbox access |
| `agentmail` | Python package | Yes | AgentMail client package, install with `pip3 install agentmail` |
| Python 3 | Runtime | Yes | Used for inbox fetch, parsing, matching, and digest generation |
| AgentMail inbox | External service | Yes | Receives and stores monitored newsletter emails |
| Newsletter subscriptions | External data | Yes | One or more newsletter senders configured for the inbox |

## Step 1: Environment Setup

Verify the results directory, required secret, and Python dependencies before scanning.

```bash
mkdir -p /app/results

if [ -z "${AGENTMAIL_API_KEY:-}" ]; then
  echo "ERROR: AGENTMAIL_API_KEY is not set"
  exit 1
fi

python3 - <<'PY'
import importlib.util
missing = [pkg for pkg in ["agentmail"] if importlib.util.find_spec(pkg) is None]
if missing:
    raise SystemExit("Missing packages: " + ", ".join(missing) + ". Install with: pip3 install agentmail")
print("Environment ready")
PY
```

If setup fails, write `/app/results/validation_report.json` with the setup stage marked `passed=false` and stop.

## Step 2: Intake and Campaign Configuration

Collect the monitoring inputs before scanning:

1. Which newsletters should be monitored? If unknown, ask what 3-5 newsletters the ICP reads and expand from there.
2. Which AgentMail inbox should receive the newsletters?
3. Which competitor names should be tracked?
4. Which ICP pain-language terms should be tracked?
5. Which market-shift terms should be tracked?
6. Which brand or product names should be tracked?
7. Where should the digest be delivered?
8. Should the scan run daily or weekly?

Write `/app/results/newsletter-signals.json`:

```json
{
  "inbox_id": "<agentmail_inbox_id>",
  "keyword_campaigns": {
    "competitors": ["Clay", "Apollo", "Outreach", "Salesloft"],
    "pain_language": ["pipeline is down", "outbound isn't working", "SDR ramp"],
    "market_shifts": ["AI SDR", "GTM engineer", "agent-led"],
    "brand_mentions": ["YourCompany", "yourcompany.com"]
  },
  "newsletters": [
    {"name": "Exit Five", "from_domain": "exitfive.com"},
    {"name": "The GTM Newsletter", "from_domain": "gtmnewsletter.com"}
  ],
  "output": {
    "format": "markdown",
    "path": "/app/results/newsletter-signals-[YYYY-MM-DD].md"
  }
}
```

## Step 3: Subscribe and Accumulate Newsletter Mail

For first-time setup, subscribe the AgentMail address to the selected newsletters:

1. Get the AgentMail inbox address from the AgentMail API.
2. Visit each newsletter subscription page and submit the AgentMail address.
3. Confirm subscriptions by checking the inbox for confirmation emails.
4. Allow 1-2 weeks of accumulation before the first full digest when historical coverage is required.

Record incomplete subscriptions in `summary.md` so readers know why a scan may have limited coverage.

## Step 4: Fetch Newsletter Emails

Fetch emails from the configured inbox since the last scan date. Filter to known newsletter senders using configured sender domains or names.

```python
from datetime import datetime, timezone
from agentmail import AgentMail

client = AgentMail()
config = load_config("/app/results/newsletter-signals.json")
emails = client.inboxes.messages.list(
    inbox_id=config["inbox_id"],
    after=config.get("last_scan_date")
)

newsletter_emails = [
    email for email in emails
    if is_known_newsletter_sender(email, config["newsletters"])
]
```

For each email, extract subject, sender, date, body text, and a source URL if one is available. Convert HTML email bodies to plain text before matching.

## Step 5: Apply Keyword Campaigns

For each newsletter email, scan every configured keyword campaign. Keep only emails with at least one keyword match.

```python
for email in newsletter_emails:
    matches = {}
    body = email.body_text.lower()
    for campaign, keywords in config["keyword_campaigns"].items():
        found = []
        for keyword in keywords:
            if keyword.lower() in body:
                context = extract_context(email.body_text, keyword, before=50, after=50)
                found.append({"keyword": keyword, "context": context})
        if found:
            matches[campaign] = found
    email.signal_matches = matches
```

## Step 6: Extract Signal Snippets

Normalize each match into a concise snippet with source context:

| Field | Description |
|---|---|
| Newsletter | Newsletter name or sender |
| Date | Email received or sent date |
| Campaign | Matched campaign bucket |
| Keyword | Keyword that triggered the match |
| Context | Clean excerpt around the keyword |
| Relevance | Why this signal matters for the target team |

Prefer exact context snippets over broad summaries. Keep excerpts short enough for a weekly digest to stay scannable.

## Step 7: Write Digest

Write the digest to `/app/results/newsletter-signals-[YYYY-MM-DD].md` using this structure:

```markdown
# Newsletter Signal Digest — Week of [DATE]

## Summary
- Newsletters scanned: [N]
- Emails with signals: [N]
- Top trending topic: [topic]

## Competitor Mentions

### [Competitor]
- **[Newsletter Name]** — [Date]
  > "[Context snippet]"
  Source: [email subject] | [URL if available]

## ICP Pain Language

- **[Newsletter Name]** — [Date]
  > "[Context snippet]"
  Relevance: [why this matters]

## Market Shift Signals

- **[Topic]** — mentioned in [N] newsletters this week
  > "[Context snippet]"

## Your Brand Mentions

[Any mentions of the configured company or product]

## Recommended Actions
1. [Specific action based on signals]
2. [Competitive response if needed]
```

## Step 8: Scheduling

For weekly operation, schedule the scanner before the team's recurring planning meeting.

```bash
# Every Monday at 7am
0 7 * * 1 python3 run_skill.py newsletter-signal-scanner --client <client-name>
```

Daily scans can use the same logic with a one-day lookback and a shorter digest template.

## Step 9: Iterate on Errors (max 3 rounds)

If setup, inbox fetch, parsing, matching, or digest validation fails, run at most 3 rounds of targeted correction:

1. Read the failed stage and message from `/app/results/validation_report.json`.
2. Fix only the failing input, credential, parser, or output-format issue.
3. Re-run the failed stage and regenerate affected outputs.
4. Stop after 3 rounds and mark `overall_passed=false` if the same failure remains.

## Common Fixes

| Issue | Fix |
|---|---|
| `AGENTMAIL_API_KEY` missing | Set the secret in the execution environment and rerun setup |
| No newsletter emails found | Confirm subscriptions and sender domains, then allow more accumulation time |
| Too many false positives | Tighten keyword campaigns or require phrase-boundary matching |
| Digest file missing | Re-run Step 7 and verify the output path uses `/app/results` |
| Empty recommended actions | Add a relevance rule for each campaign bucket before writing the digest |

## Step 10: Final Checklist

Run this verification script before completing the run:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
TODAY="$(date -u +%Y-%m-%d)"

for f in \
  "$RESULTS_DIR/newsletter-signals.json" \
  "$RESULTS_DIR/newsletter-signals-$TODAY.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

python3 - <<'PY'
import json, pathlib
report = json.loads(pathlib.Path("/app/results/validation_report.json").read_text())
if not report.get("overall_passed"):
    raise SystemExit("FAIL: overall_passed is false")
print("PASS: validation_report.json overall_passed=true")
PY
```

The run is complete only when the script prints `FINAL OUTPUT VERIFICATION` and every required output line is `PASS`.

## Tips

- Keep keyword campaigns narrow enough to avoid noisy digests.
- Store sender domains in config so newsletter renames do not break monitoring.
- Separate competitor, pain-language, market-shift, and brand terms so recommended actions can be tailored by signal type.
