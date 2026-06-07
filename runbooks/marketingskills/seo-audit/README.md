# marketingskills/seo-audit — demo payload

A launch payload for the `marketingskills/seo-audit` runbook: the optimized runbook, a
`manifest.json`, and three worked examples — each a real production audit of a live site.

```
seo-audit/
  RUNBOOK.md                        # the runbook (v1.1.0)
  manifest.json                     # directory metadata
  README.md                         # this file
  examples/
    govuk-audit/                    # government portal — Health: Good
      input.json  trajectory.json  thumbnail.png
      expected/  seo_audit_report.md (primary) · technical/onpage/content_findings.json · summary.md · validation_report.json
    django-audit/                   # framework site — Needs Attention
      input.json  trajectory.json  thumbnail.png  expected/ …
    rust-blog-audit/                # developer blog — Needs Attention
      input.json  trajectory.json  thumbnail.png  expected/ …
```

## What it does

Given a live site URL, the runbook runs a systematic, prioritized SEO audit — crawlability,
technical foundations, on-page optimization, content quality, and authority — and writes an
evidence-backed report with a prioritized action plan, plus structured findings JSON. It
adapts the checklist to the site type (SaaS, e-commerce, blog, multilingual, local).

## The gallery: three live sites, three health ratings

| # | Site | Type | Health | Findings | Top concrete issue | Trajectory |
|---|------|------|--------|----------|--------------------|-----------|
| 1 | gov.uk | government portal | **Good** | 26 | no English↔Welsh hreflang | `3d7d8b05` |
| 2 | djangoproject.com | framework / docs | Needs Attention | 28 | HTTP does not redirect to HTTPS | `6044edc3` |
| 3 | blog.rust-lang.org | developer blog | Needs Attention | 30 | (technical/on-page/content gaps) | `a73e0ed1` |

All three are green with `seo_audit_report.md` as the primary deliverable. The mix (one
strong site + two with real gaps) shows the runbook both validating good SEO and finding
concrete, fixable issues.

## What changed (v1.0.0 → v1.1.0), from auditing a real run

The prior run (audit of theguardian.com) worked but had hygiene/reliability bugs:

1. **Filename drift** — the agent wrote `audit_report.md` (+ a separate `action_plan.md`)
   instead of the *required* `seo_audit_report.md`, so the mandatory deliverable was
   "missing" by name. v1.1.0 enforces the exact filename and folds the action plan in.
2. **No `primary_outputs`** — now declares `seo_audit_report.md`, which resolves to
   `primary_files` (verified across all three runs).
3. **Unreliable URL input** — the runbook read a `$SITE_URL` env var that is never set (a
   no-target run failed). v1.1.0 reads `{{target_url}}` from an Inputs block (the
   substitution path that works) and stops interviewing the user.
4. **Honest tool limits** — the sandbox can't reach PageSpeed / Rich Results / Search
   Console / Ahrefs. The runbook now does a thorough **static** audit and explicitly flags
   Core Web Vitals, JS-rendered schema, indexation, and backlinks as "requires external
   tool" rather than reporting a pass/fail it couldn't verify (see the gov.uk report).

## Reproduce (example 1)

```bash
TOKEN="$(grep '^JETTY_API_TOKEN_JON_RUNBOOKS=' .env | cut -d= -f2-)"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  --form-string 'init_params={"vars":{"target_url":"https://www.gov.uk","scope":"full","site_type":"auto-detect"}}' \
  "https://flows-api.jetty.io/api/v1/run/jon-runbooks/seo-audit-safe-valley"
```
