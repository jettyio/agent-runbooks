---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/playbooks/seo-content-engine/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/seo-content-engine
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: SEO Content Engine
  imported_at: '2026-05-03T02:45:32Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    source_collection: playbooks
    skill_name: seo-content-engine
    confidence: high
secrets: {}
---

# SEO Content Engine — Agent Runbook

## Objective

Build a compounding SEO content engine for a client by auditing the current search footprint, identifying competitive and funnel gaps, building keyword architecture, creating a prioritized content calendar, drafting content, and defining a publishing and monitoring pipeline. The runbook converts the source playbook into a programmatic workflow with explicit inputs, required outputs, human checkpoints, and validation criteria. The agent should preserve client positioning and brand voice while producing practical, reviewable SEO assets.

## REQUIRED OUTPUT FILES (MANDATORY)

All files MUST be written under the resolved `results_dir`. The task is incomplete until each file exists and is non-empty.

| File | Description |
|---|---|
| `summary.md` | Executive summary of the SEO content engine plan, key findings, and next actions. |
| `validation_report.json` | Structured validation results for each stage and the final output manifest. |
| `seo_audit_summary.md` | Current-state SEO audit covering content inventory, authority/ranking signals, and AI answer visibility. |
| `content_gap_analysis.md` | Prioritized competitive, funnel, topic, and comparison content gaps. |
| `keyword_architecture.csv` | Keyword clusters mapped to funnel stage, intent, content type, and priority. |
| `content_calendar.md` | 8-week prioritized content calendar with owners, target keywords, and publication cadence. |
| `draft_content_briefs.md` | Draft-ready briefs for prioritized content pieces, including CTA, internal links, and schema recommendations. |
| `internal_linking_plan.md` | Recommended TOFU/MOFU/BOFU linking structure and pillar-page relationships. |
| `monitoring_plan.md` | Metrics, review cadence, and refresh criteria for ongoing SEO performance management. |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Results directory | `results_dir` | `/app/results` | Directory where all required output files are written. |
| Client website URL | `client_website_url` | required | Client website to audit and use as the primary SEO target. |
| Client context path | `client_context_path` | `context.md` | File containing ICP, value props, positioning, and brand voice context. |
| Competitors | `competitors` | required | Top competitors used for gap analysis and comparison content planning. |
| Publishing cadence | `publishing_cadence` | `2-3 pieces per week` | Target ongoing editorial throughput. |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Web access | External | Yes | Review client site pages, competitor content, and public search surfaces. |
| Client context.md | Input file | Yes | Provides ICP, positioning, value props, and brand voice. |
| SEO audit tooling | Skill/tool | Preferred | Equivalent of `seo-content-audit`, including site catalog, domain analysis, and brand voice extraction. |
| AI answer visibility tooling | Skill/tool | Preferred | Equivalent of `aeo-visibility` for answer-engine visibility checks. |
| Spreadsheet or CSV writer | Local/tool | Yes | Produces `keyword_architecture.csv` in a structured format. |

## Step 1: Environment Setup

1. Resolve all parameters and create `results_dir` if it does not exist.
2. Verify `client_website_url` starts with `http://` or `https://`.
3. Verify `client_context_path` exists and is readable.
4. Normalize `competitors` into a newline-delimited list.
5. Initialize a validation report with stages for setup, audit, gaps, keyword architecture, calendar, drafting, internal linking, monitoring, and final verification.

If a required input is missing, write `validation_report.json` with `overall_passed=false`, write `summary.md` describing the missing input, and stop.

## Step 2: Audit Current State

Run the equivalent of `seo-content-audit` to establish the current search baseline. Combine a site content catalog, domain and ranking analysis, competitive gap matrix, and brand voice extraction.

Capture at minimum:

- Current content inventory grouped by type, topic, funnel stage, and freshness.
- Domain authority or comparable authority signal, organic traffic trend, and currently ranking keywords where available.
- Competitor keywords and pages that outperform the client.
- Brand voice patterns that future drafts should match.
- AI answer visibility for priority category and problem-solution queries.

Write `seo_audit_summary.md` with sources, assumptions, and confidence notes.

## Step 3: Identify Content Gaps

Analyze the audit and classify gaps into competitive, funnel, topic, and comparison opportunities.

Prioritize each gap using this formula unless better client data is available:

`priority = search demand * commercial intent * strategic fit / competitive difficulty`

Write `content_gap_analysis.md` with a ranked backlog. Include a human checkpoint asking the operator to approve the gap priorities before calendar creation.

## Step 4: Build Keyword Architecture

Map keyword clusters across funnel stages:

- TOFU: awareness queries such as `what is [category]`, `[category] use cases`, and `how to [solve problem]`.
- MOFU: evaluation queries such as `[category] comparison`, `how to choose [solution]`, and technical or compliance requirements.
- BOFU: decision queries such as `[Company] vs [Competitor]`, `[Competitor] alternatives`, pricing guides, and migration guides.

For every cluster, specify target keyword, supporting keywords, intent, content type, funnel stage, priority, and recommended URL slug. Write `keyword_architecture.csv`.

## Step 5: Create Content Calendar

Build an 8-week calendar ordered by business urgency and ranking opportunity:

1. Weeks 1-2: High-urgency BOFU pages, especially comparison and alternatives pages.
2. Weeks 2-4: Core MOFU guides and evaluation content.
3. Weeks 4-8: TOFU awareness content and programmatic SEO templates.
4. Ongoing: Maintain the requested cadence, defaulting to 2-3 editorial pieces per week.

Write `content_calendar.md` and include a checkpoint requiring review before drafting begins.

## Step 6: Draft Content Briefs

For each approved priority piece, draft a content brief rather than final-publishing copy unless the operator explicitly requests finished drafts.

Each brief MUST include:

- Target reader and funnel stage.
- Primary and secondary keywords used naturally.
- Search intent and angle.
- Outline with H1/H2/H3 recommendations.
- Internal links to related content and target conversion page.
- CTA recommendation.
- Structured data or schema markup recommendation when relevant.
- Brand voice notes from the audit.

Write `draft_content_briefs.md` and include a human review checkpoint before publishing.

## Step 7: Build Internal Linking Architecture

Design the link structure so awareness pages move readers toward evaluation and decision content:

- TOFU pages link to related MOFU guides and pillar content.
- MOFU pages link to BOFU comparison, pricing, migration, or product pages.
- BOFU pages link to product, signup, sales, or demo flows.
- Pillar pages collect and redistribute authority to cluster pages.

Write `internal_linking_plan.md` with anchor text recommendations and page-to-page relationships.

## Step 8: Publish and Monitor

Create a monitoring plan that tracks organic traffic by page and cluster, rankings by target keyword, assisted conversions, content-to-signup conversion, and pages requiring refresh.

Use this cadence:

- Weekly: publish planned pieces and monitor early ranking/indexing signals.
- Monthly: review performance, update the calendar, and refresh underperforming pages.
- Quarterly: re-run the audit to measure progress and discover new gaps.

Write `monitoring_plan.md`.

## Step 9: Iterate on Errors (max 3 rounds)

If validation fails or a human checkpoint rejects a section, perform up to max 3 rounds of targeted revision. Each round should identify the failed stage, adjust only the affected output files, and re-run validation before continuing.

## Common Fixes

| Issue | Fix |
|---|---|
| Missing required output file | Re-run the stage that owns the file and write a short placeholder with assumptions if data access is limited. |
| Keyword architecture lacks funnel stages | Reclassify every keyword as TOFU, MOFU, or BOFU before regenerating the calendar. |
| Calendar ignores priority | Re-sort by BOFU urgency, commercial intent, and difficulty-adjusted opportunity. |
| Drafts do not match brand voice | Re-read client context and the brand voice notes, then revise tone and examples. |
| Validation report is incomplete | Rebuild `validation_report.json` from the required stage list and include `overall_passed`. |

## Final Checklist

Run this verification before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="${results_dir:-/app/results}"
for f in   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"   "$RESULTS_DIR/seo_audit_summary.md"   "$RESULTS_DIR/content_gap_analysis.md"   "$RESULTS_DIR/keyword_architecture.csv"   "$RESULTS_DIR/content_calendar.md"   "$RESULTS_DIR/draft_content_briefs.md"   "$RESULTS_DIR/internal_linking_plan.md"   "$RESULTS_DIR/monitoring_plan.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

The run passes only when every required file is present, the validation report has `overall_passed=true`, and any human checkpoint decisions are reflected in `summary.md`.

## Tips

Prefer specific client evidence over generic SEO advice. Keep BOFU and comparison content close to product truth, use the client voice from `context.md`, and make assumptions explicit whenever search-volume or ranking data is unavailable.
