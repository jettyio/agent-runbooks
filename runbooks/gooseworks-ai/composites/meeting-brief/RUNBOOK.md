---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/meeting-brief/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/meeting-brief
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Meeting Brief
  imported_at: '2026-05-03T02:45:45Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: meeting-brief
    confidence: high
secrets: {}
---

# Meeting Brief - Agent Runbook

## Objective

Prepare daily meeting briefs by checking the operator's calendar, filtering out internal attendees, researching each external participant, and generating concise context for upcoming conversations. This runbook converts the original Meeting Brief skill into a Jetty programmatic workflow with explicit outputs, validation, and privacy controls. It supports email and Slack delivery while preserving local logs, research cache, and sent-brief tracking.

The source was resolved from the Gooseworks directory mirror to the upstream GitHub `SKILL.md` before import. Original description: Daily meeting preparation system that checks your calendar each morning, deeply researches external attendees (LinkedIn, company info, GitHub, past notes), and sends you personalized briefs via email (1 per person). Use when you want automated preparation for upcoming meetings with context about each person you're meeting.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/summary.md` | Executive summary of the run, meetings processed, delivery status, and issues |
| `/app/results/validation_report.json` | Structured validation report with stage results and `overall_passed` |
| `/app/results/briefs.json` | Machine-readable list of generated briefs and delivery state |
| `/app/results/research_cache_manifest.json` | Manifest of people researched and cached source files |
| `/app/results/sent_log.json` | De-duplication log for briefs sent during the run |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Results directory | `/app/results` | `/app/results` | Output directory for all required outputs |
| Skill directory | `skill_dir` | `skills/meeting-brief` | Local checkout path containing the skill scripts |
| `team_members` | config.json | Source default | Meeting brief configuration value |
| `team_domains` | config.json | Source default | Meeting brief configuration value |
| `schedule` | config.json | Source default | Meeting brief configuration value |
| `timezone` | config.json | Source default | Meeting brief configuration value |
| `your_email` | config.json | Source default | Meeting brief configuration value |
| `brief_from` | config.json | Source default | Meeting brief configuration value |
| `slack_webhook` | config.json | Source default | Meeting brief configuration value |
| `send_email` | config.json | Source default | Meeting brief configuration value |
| `send_slack` | config.json | Source default | Meeting brief configuration value |
| `include_calendar_details` | config.json | Source default | Meeting brief configuration value |
| `research_depth` | config.json | Source default | Meeting brief configuration value |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| `gcalcli` | Yes | Fetch today's calendar agenda |
| `node` | Yes | Run source JavaScript research and brief-generation scripts |
| `gh` | Optional | GitHub profile lookup when `research_depth` is `standard` or `deep` |
| `web_search` | Yes | Find LinkedIn, company, and recent-news context |
| `memory_search` | Optional | Include past notes when `research_depth` is `deep` |
| Gmail skill or SMTP sender | Optional | Send email briefs when `send_email=true` |
| Slack incoming webhook | Optional | Send Slack briefs when `send_slack=true` |

## Step 1: Environment Setup

1. Create `/app/results` and ensure it is writable.
2. Confirm `config.json` exists in the skill directory; if it does not, copy `config.json.example` and fill in team filters, timezone, destination email, and delivery preferences.
3. Verify calendar access with `gcalcli agenda today tomorrow`.
4. Verify optional integrations only when enabled: `gh auth status` for GitHub lookup, Gmail sender credentials for email, and `slack_webhook` for Slack.
5. Write a setup stage to `/app/results/validation_report.json`.

## Step 2: Load Configuration

Read `config.json` and validate `team_members`, `team_domains`, `schedule`, `timezone`, `your_email`, `send_email`, `send_slack`, `include_calendar_details`, and `research_depth`. Fail fast if both `send_email` and `send_slack` are false and no file-output mode is configured. Normalize team domains to lowercase before filtering.

## Step 3: Fetch Today's Meetings

Run `scripts/check_calendar.sh` or the equivalent `gcalcli` command for today's agenda in the configured timezone. Parse meeting title, time, location, description, and attendees into JSON. Store the normalized meeting data under the skill data directory and include a count in `/app/results/summary.md`.

## Step 4: Filter External Attendees

For each attendee, skip exact matches from `team_members` and any email ending in a configured `team_domains` entry. De-duplicate attendees across meetings and check `data/sent/YYYY-MM-DD.json` so the run does not resend a brief for a person already handled today.

## Step 5: Research Each Person

For every remaining external attendee, run `node scripts/research_person.js "<name>" "<email>" "<company>"`. Use web search for LinkedIn, company information, recent news, and professional background. If `research_depth` is `standard` or `deep`, use GitHub lookup for likely engineering profiles; if `deep`, search memory and past notes. Write `/app/results/research_cache_manifest.json` with every person, cache file, and research depth used.

## Step 6: Generate and Deliver Briefs

Run `node scripts/generate_brief.js research_output.json meeting_context.json` for each researched attendee. Produce email-style concise bullets and Slack-style narrative context. When enabled, send email via the Gmail skill and Slack via `scripts/send_slack.sh`; otherwise retain file output only. Record all generated briefs, destination channels, and delivery outcomes in `/app/results/briefs.json`.

## Step 7: Iterate on Errors (max 3 rounds)

If calendar fetch, research, generation, or delivery fails, retry the failing stage with a targeted fix for max 3 rounds. Common fixes include refreshing `gcalcli` authentication, lowering `research_depth` from `deep` to `standard`, disabling a failed delivery channel, or re-running only attendees missing briefs. After the third failed round, stop and write the failure to `summary.md` and `validation_report.json`.

## Step 8: Persist Logs and Personal CRM Entries

Save each researched person to `supernotes/people/` with research data, meeting context, and run date. Update `data/sent/YYYY-MM-DD.json` only after a brief is generated and the selected delivery path succeeds or a file-only brief is intentionally retained. Copy the de-duplication state to `/app/results/sent_log.json`.

## Final Checklist

Run this verification before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json" "$RESULTS_DIR/briefs.json" "$RESULTS_DIR/research_cache_manifest.json" "$RESULTS_DIR/sent_log.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f"
  fi
done
```

Confirm every external attendee has either a generated brief or a documented skip reason, delivery channels match `config.json`, and no internal team member was included.

## Common Fixes

| Issue | Fix |
|---|---|
| No meetings found | Run `gcalcli agenda today tomorrow` and verify calendar authorization |
| Briefs missing information | Increase `research_depth` or inspect `data/research/` for failed lookups |
| Duplicate briefs | Check `data/sent/` before delivery and normalize attendee email addresses |
| Slack delivery fails | Verify `slack_webhook` and fall back to file output for that person |
| Email delivery fails | Verify Gmail sender credentials and retain the generated brief in `/app/results/briefs.json` |

## Tips

1. Test with `DRY_RUN=true` before enabling delivery.
2. Start with `research_depth=quick`, then move to `standard` or `deep` when the extra context is worth the run time.
3. Keep `team_members` and `team_domains` current so internal meetings are skipped consistently.
4. Review `data/sent/` after each run to confirm de-duplication is working.
5. Tune `scripts/generate_brief.js` prompts when the brief tone or structure needs to match your workflow.
