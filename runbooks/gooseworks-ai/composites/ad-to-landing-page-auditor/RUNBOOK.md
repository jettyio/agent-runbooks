---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/ad-to-landing-page-auditor/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/ad-to-landing-page-auditor
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Ad-to-Landing Page Auditor
  imported_at: '2026-05-03T02:33:33Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: ad-to-landing-page-auditor
    confidence: high
secrets: {}
---

# Ad-to-Landing Page Auditor — Agent Runbook

## Objective

Audit the message match between paid ads and their landing pages. The runbook compares each ad's promise, wording, CTA, and conversion goal against the destination page's headline, body, CTA, trust signals, and form friction, then identifies the disconnects most likely to depress conversion rates. It produces a prioritized remediation plan that can be used by marketing, growth, or product teams.

Source summary: Analyze the message match between your ads and landing pages. Checks if the promise in the ad copy carries through to the landing page headline, body, and CTA. Flags disconnects that kill conversion rates. Works with Google, Meta, and LinkedIn ads.

## REQUIRED OUTPUT FILES (MANDATORY)

All files below MUST be written to `/app/results` and MUST be non-empty before the run is complete.

| File | Description |
|---|---|
| `/app/results/ad_inventory.csv` | Normalized inventory of each ad, platform, copy, CTA, destination URL, and known conversion rate |
| `/app/results/landing_page_audit.json` | Extracted landing page elements and per-page audit notes |
| `/app/results/message_match_report.md` | Pairwise ad-to-page scorecard with evidence and conversion risks |
| `/app/results/prioritized_fixes.md` | Ranked fixes with suggested copy, CTA, and page changes |
| `/app/results/summary.md` | Executive summary with strongest mismatches, highest-impact fixes, and run metadata |
| `/app/results/validation_report.json` | Structured validation results, stages, file checks, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Results directory | `/app/results` | Output directory for all required files |
| Ad copy | Required | Headlines, descriptions, CTA text, platform, and campaign context for each ad |
| Landing page URLs | Required | Destination URL for each ad |
| Conversion goal | Required | Desired post-click action such as demo, trial, purchase, or download |
| Known conversion rates | Optional | Current click-to-conversion rates per ad or landing page |
| CSV export | Optional | Ad platform export that can be parsed instead of manual ad entry |

## Dependencies

| Dependency | Type | Required | Purpose |
|---|---|---|---|
| `python` | CLI | Yes | Parse inputs, fetch pages, and write structured outputs |
| `requests` | Python package | Yes | Retrieve landing page HTML when browser tooling is unavailable |
| `beautifulsoup4` | Python package | Optional | Extract page text and primary elements from HTML |
| `curl` | CLI | Optional | Fallback page retrieval |
| `fetch_webpage` | Agent tool | Optional | Preferred webpage fetch capability when available |

## Step 1: Environment Setup

Create `/app/results`, verify Python is available, and install optional parsing dependencies when needed.

```bash
mkdir -p /app/results
python - <<'PY'
import sys
print(sys.version)
PY
pip install requests beautifulsoup4 >/tmp/ad_lp_audit_deps.log 2>&1 || true
```

Record the resolved inputs in the validation report. If ad copy, landing page URLs, or conversion goal are missing, stop and write `validation_report.json` with `overall_passed=false`.

## Step 2: Intake and Normalization

Collect the required ad data:

| Field | Notes |
|---|---|
| Ad ID | Stable identifier from the platform export or generated sequential ID |
| Platform | Google Search, Meta, LinkedIn, or other source |
| Headline | Primary ad headline |
| Body/Description | Main supporting ad copy |
| CTA | Ad call to action |
| Landing Page URL | Final URL after redirects when possible |
| Conversion Rate | Optional known click-to-conversion rate |

If a CSV export is provided, parse it into the same schema. Write the normalized inventory to `/app/results/ad_inventory.csv`.

## Step 3: Landing Page Audit

For each unique landing page URL, fetch the page content.

```bash
curl -L --max-time 30 "<landing_page_url>" -o /tmp/landing-page.html
```

Extract the hero headline, subheadline, primary CTA, CTA position, social proof, benefits, form fields, video presence, and trust signals. Store the extracted page records in `/app/results/landing_page_audit.json`.

## Step 4: Message Match Scoring

For every ad to landing-page pair, score each dimension from 1 to 10:

| Dimension | Scoring question |
|---|---|
| Promise continuity | Does the page headline deliver the promise made in the ad? |
| Language match | Does the page reuse the ad's key words and phrases? |
| Visual continuity | Does the page feel like a continuation of the ad creative when visual context is available? |
| CTA alignment | Does the page ask for the action implied by the ad? |
| Specificity preservation | Are numbers, audience qualifiers, offers, and constraints preserved? |
| Friction match | Does the page's form or purchase flow match the commitment level implied by the ad? |

Calculate an average score and classify each pair as strong match, acceptable, weak, or broken. Include evidence snippets for every score.

## Step 5: Identify Conversion Killers

Flag the common disconnects:

| Issue | Example |
|---|---|
| Promise swap | Ad promises one outcome, page leads with a different product or generic message |
| CTA mismatch | Ad says download, page asks for a sales call |
| Audience drift | Ad targets a specific role or segment, page speaks broadly |
| Offer disappearance | Discount, trial, benchmark, or asset from the ad is missing on the page |
| Excessive friction | Low-commitment ad routes to a long form or high-pressure sales workflow |

Prioritize issues by severity, traffic or spend where known, conversion-rate gap, and ease of repair.

## Step 6: Generate Recommendations

Write `/app/results/message_match_report.md` with the scorecard and evidence. Write `/app/results/prioritized_fixes.md` with recommended changes, including revised hero copy, CTA text, proof placement, and form-friction reductions.

## Step 7: Iterate on Errors (max 3 rounds)

If required inputs are missing, a page cannot be fetched, extraction fails, or score evidence is too thin, perform up to max 3 rounds of targeted repair:

1. Ask for the missing ad, page, or conversion-goal data when it cannot be inferred.
2. Retry failed page fetches with redirects enabled and a browser-like user agent.
3. Fall back to manual extraction from provided page text or screenshots.

After max 3 rounds, continue with clearly marked partial findings if at least one ad and one landing page can be evaluated.

## Step 8: Validation

Write `/app/results/summary.md` and `/app/results/validation_report.json`.

## Final Checklist

Run:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/ad_inventory.csv" \
  "$RESULTS_DIR/landing_page_audit.json" \
  "$RESULTS_DIR/message_match_report.md" \
  "$RESULTS_DIR/prioritized_fixes.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

The run passes only when every required output exists, scores include evidence, and the validation report sets `overall_passed=true` or clearly explains any partial result.

## Common Fixes

| Issue | Fix |
|---|---|
| Landing page blocks automated fetch | Retry with a browser-like user agent, use `fetch_webpage`, or ask for page text |
| CSV fields do not match the expected schema | Map platform-specific fields into headline, body, CTA, URL, and conversion rate |
| Multiple ads share one landing page | Audit the page once, then score every ad-page pair separately |
| CTA is absent above the fold | Flag as a high-severity friction issue and recommend a visible primary CTA |

## Tips

Keep the ad's promise visible in the first screen of the landing page, reuse the exact high-intent language from the ad, and align the CTA with the user's expected commitment level.
