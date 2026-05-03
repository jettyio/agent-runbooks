---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/tech-stack-teardown/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/tech-stack-teardown
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: tech-stack-teardown
  imported_at: '2026-05-03T02:54:37Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    source_collection: capabilities
    skill_name: tech-stack-teardown
    confidence: high
secrets:
  APIFY_API_TOKEN:
    env: APIFY_API_TOKEN
    description: Optional Apify API token used only when paid technology profiling
      is enabled.
    required: false
---

# tech-stack-teardown - Agent Runbook

## Objective
Reverse-engineer a company's sales, marketing, and outbound technology stack from public signals. This runbook checks DNS records, website source code, optional Apify technology profiling, blacklist databases, and public complaint signals. It works for one company or a batch of domains and produces structured evidence for each detected tool. No login to the target company's systems is required.

Source skill summary: Reverse-engineer a company's sales and marketing tech stack from public signals. Detects CRMs, cold email tools, people databases, ad pixels, email delivery services, and outbound sending domains via DNS records, website source inspection, Apify technology profiling, blacklist checks, and public spam complaint searches. Works on single companies or batches. Outputs a structured markdown report per company.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/summary.md` | Executive summary of analyzed domains, confirmed tools, risk signals, and caveats. |
| `/app/results/validation_report.json` | Programmatic validation report with stage results and overall pass/fail. |
| `/app/results/tech_stack_report.md` | Human-readable markdown report with findings per company. |
| `/app/results/evidence.json` | Structured evidence collected from DNS, website source, blacklist checks, and optional Apify profiling. |
| `/app/results/raw_dns.json` | Raw DNS observations for MX, SPF, DKIM, DMARC, TXT, and checked subdomains. |
| `/app/results/website_signals.json` | Website source signatures and detected pixels, scripts, analytics, forms, and framework hints. |
| `/app/results/apify_profile.json` | Optional Apify profiler results, or an empty object with `skipped=true` when disabled or unavailable. |

## Parameters

| Parameter | Default | Required | Description |
|---|---:|---:|---|
| Results directory | `/app/results` | No | Directory where all required output files must be written. |
| Domains | none | Yes | One or more company domains to analyze. Accept comma-separated values for batches. |
| Output format | `markdown` | No | Emit markdown, JSON, or both when supported by the local script. |
| No Apify | `false` | No | When true, skip paid Apify profiling and use only free checks. |
| Confirm paid profiling threshold | `5` domains | No | Confirm before running Apify on more than this many domains. |

## Dependencies

| Dependency | Required | Purpose |
|---|---:|---|
| `dig` | Yes | DNS lookups for MX, TXT, DMARC, DKIM, CNAME, blacklist, and outbound-domain checks. |
| `curl` | Yes | Fetch target website source for signature inspection. |
| `python3` | Yes | Run local collection and report-generation scripts. |
| `requests` and `python-dotenv` | Yes | HTTP fetching and optional `.env` loading for scripts. |
| `APIFY_API_TOKEN` | No | Enables Apify Technology Profiling Engine. |
| Web search capability | No | Used for public complaint and public stack-mention checks. |

## Step 1: Environment Setup

Create the results directory and verify local tools before inspecting any target.

```bash
mkdir -p /app/results
command -v dig >/dev/null || { echo "ERROR: dig is required"; exit 1; }
command -v curl >/dev/null || { echo "ERROR: curl is required"; exit 1; }
command -v python3 >/dev/null || { echo "ERROR: python3 is required"; exit 1; }
python3 -m pip install requests python-dotenv
```

If `APIFY_API_TOKEN` is present, record that paid profiling is available. Never write the token value to logs or output files.

## Step 2: Resolve Inputs

Normalize the requested domains before scanning.

1. Split comma-separated input into a de-duplicated domain list.
2. Strip URL schemes, paths, query strings, and trailing slashes.
3. Reject empty entries and values that are not plausible DNS names.
4. If more than 5 domains will use Apify, ask for confirmation before continuing.

Write the normalized domain list into `/app/results/evidence.json` under `inputs.domains`.

## Step 3: DNS and Email Infrastructure Scan

For each domain, collect MX, SPF, DKIM, DMARC, TXT, and CNAME records. Check common DKIM selectors such as `google`, `selector1`, `selector2`, `s1`, `s2`, `k1`, `k2`, `mandrill`, `pm`, `smtp`, and `em`. Also inspect common sending and tracking subdomains including `mail`, `email`, `send`, `smtp`, `bounce`, `click`, `track`, `links`, and `go`.

Classify email and outbound infrastructure using the source skill's signal tables: Google Workspace, Microsoft 365, SendGrid, Amazon SES, HubSpot, Mailchimp, Mandrill, Zendesk, Freshdesk, Mailjet, Brevo, Salesforce, Marketo, Postmark, Mailgun, Smartlead tracking records, and verification TXT records.

## Step 4: Website Source Inspection

Fetch each homepage and inspect HTML, script URLs, meta tags, form handlers, and framework signatures.

```bash
curl -sL --max-time 30 https://example.com > /tmp/example-homepage.html
```

Search for signatures including HubSpot, Apollo, LinkedIn Insight Tag, Facebook Pixel, Segment, Mixpanel, Amplitude, PostHog, Intercom, Drift, Crisp, Zendesk, REB2B, Clearbit Reveal, 6sense, Demandbase, AdRoll, Google Tag Manager, and Google Analytics. Store raw observations in `/app/results/website_signals.json` and cite the exact pattern that produced each finding.

## Step 5: Optional Apify Technology Profiling

When `APIFY_API_TOKEN` is available and `no_apify` is false, run the Apify Technology Profiling Engine for deeper detection. Treat this as a paid step with an estimated cost near `$0.005` per domain. If Apify is skipped, write `/app/results/apify_profile.json` with `{"skipped": true, "reason": "no token or no_apify enabled"}`.

## Step 6: Blacklist and Complaint Checks

Check each domain against major DNS-based blacklists: Spamhaus, Barracuda, SpamCop, SORBS, SURBL, and URIBL. Add public complaint searches for spam, unsolicited email, cold email, blacklist references, and public mentions of detected tools when web search is available.

For blacklist checks, reverse the lookup form as needed for the target list and preserve both hit and miss results in `/app/results/evidence.json`.

## Step 7: Report Generation

Generate `/app/results/tech_stack_report.md` with one section per company:

- Confirmed tools with evidence.
- Email authentication assessment for SPF, DKIM, and DMARC.
- Deliverability signals from blacklists and complaints.
- Notable outbound domains and suspicious redirects.
- Confidence levels and gaps where a signal is suggestive but not conclusive.

For batches, add a comparative summary table at the end.

## Step 8: Iterate on Errors (max 3 rounds)

If any required output is missing, malformed, or lacks evidence for a claimed finding, perform up to 3 correction rounds:

1. Re-read `/app/results/validation_report.json` and identify the failing stage.
2. Re-run only the affected DNS, website, Apify, blacklist, or reporting step.
3. Rewrite the affected output file.
4. Re-run the final verification script.

A run may finish with partial findings when a website blocks HTTP fetching or Apify times out, but the report must name the missing signal and avoid overclaiming.

## Common Fixes

| Issue | Fix |
|---|---|
| `dig` is missing | Install `dnsutils` or run on an environment with DNS utilities. |
| Website fetch fails | Retry `https://www.<domain>`, then record the HTTP failure and continue with DNS-only evidence. |
| Apify profiler times out | Retry once, then mark Apify as skipped for that domain and rely on DNS plus source inspection. |
| No tools detected | Report the negative result and distinguish between no public signal and no tool usage. |
| SPF has only Google but cold email is suspected | Look for Smartlead tracking TXT records, outbound domains, redirects, and complaint evidence before claiming a cold-email tool. |

## Final Checklist

Run this verification before finishing.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"   "$RESULTS_DIR/tech_stack_report.md"   "$RESULTS_DIR/evidence.json"   "$RESULTS_DIR/raw_dns.json"   "$RESULTS_DIR/website_signals.json"   "$RESULTS_DIR/apify_profile.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

The run is complete only when `summary.md`, `validation_report.json`, and the evidence files exist and every tool claim in the report has a matching evidence entry.

## Tips

SPF and DKIM records are high-signal because they show which services are authorized or configured to send mail. A missing public signal is not proof that a tool is absent, especially for prospecting databases and sales tools that do not touch the website or DNS. Use Apify for broader web technology detection when paid profiling is acceptable, and keep free-only mode available for quick or large batch scans.
