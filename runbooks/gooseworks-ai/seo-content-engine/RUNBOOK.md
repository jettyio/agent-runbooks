---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/seo-content-engine/SKILL.md"
  source_host: "github.com"
  source_title: "SEO Content Engine"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    skill_name: "seo-content-engine"
    confidence: "high"
secrets: {}
---

# SEO Content Engine — Agent Runbook

## Objective

Build and run a compounding SEO content engine for a client by orchestrating a full audit-to-publish pipeline. Starting from the client's website URL, target keywords, and context document, the agent audits current SEO state, identifies content gaps, builds a keyword architecture, generates a prioritized content calendar, drafts content assets with brand-voice alignment, designs an internal linking structure, and sets up an ongoing monitoring cadence. The pipeline integrates multiple specialized skills (seo-content-audit, aeo-visibility, content-asset-creator, competitor-intel) to deliver a complete, self-reinforcing SEO content strategy.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/seo_audit_report.md` | Full SEO audit output: content inventory, domain authority, keyword rankings, competitive gap matrix |
| `/app/results/content_gaps.md` | Prioritized content gap analysis (competitive, funnel, topic, comparison) |
| `/app/results/keyword_architecture.md` | TOFU/MOFU/BOFU keyword map with content type assignments |
| `/app/results/content_calendar.md` | Prioritized content calendar for the first 8 weeks plus ongoing cadence |
| `/app/results/content_drafts/` | Directory containing drafted content pieces (one file per content item) |
| `/app/results/internal_linking_plan.md` | Internal linking architecture document |
| `/app/results/summary.md` | Executive summary with run metadata, key decisions, and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

---

## Parameters

| Parameter | Value / Default | Description |
|-----------|----------------|-------------|
| Results directory | `/app/results` | Output directory for all generated artifacts |
| `company_url` | *(required)* | Client website URL (e.g., `https://acme.com`) |
| `target_keywords` | *(required)* | Comma-separated seed keywords or keyword themes to target |
| `client_context` | *(required)* | Path to or inline content of `client-context.md` with ICP, value props, positioning |
| `competitors` | *(optional)* | Known competitors to include in gap analysis; auto-detected if omitted |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `seo-content-audit` skill | Gooseworks skill | Yes | Orchestrates site-content-catalog + seo-domain-analyzer + brand-voice-extractor |
| `aeo-visibility` skill | Gooseworks skill | Yes | Tests AI answer engine visibility for key queries |
| `content-asset-creator` skill | Gooseworks skill | Yes | Drafts landing pages, reports, and one-pagers with brand-voice alignment |
| `competitor-intel` skill | Gooseworks skill | Yes | Builds competitive intelligence package |
| `brand-voice-extractor` skill | Gooseworks skill | Yes | Extracts writing style profile for brand-voice matching |
| `visual-brand-extractor` skill | Gooseworks skill | Yes | Extracts visual brand guidelines |
| Client website access | External | Yes | Publicly crawlable client site |
| SEO data source | External API | Recommended | Ahrefs, SEMrush, or equivalent for domain authority / keyword data |

---

## Step 1: Environment Setup

Verify all required inputs are present and create the output directory structure.

```bash
echo "=== ENVIRONMENT SETUP ==="

# Verify required inputs
for var in company_url target_keywords client_context; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var is not set"
    exit 1
  fi
done

# Create output directories
mkdir -p /app/results/content_drafts

echo "PASS: Environment ready"
echo "  company_url: $company_url"
echo "  target_keywords: $target_keywords"
echo "  client_context: $client_context"
```

---

## Step 2: Audit Current State

Run the full SEO audit to establish a baseline picture of the client's search presence.

**Skills invoked:**
- `seo-content-audit` — orchestrates site-content-catalog + seo-domain-analyzer + brand-voice-extractor + competitive gap matrix
- `aeo-visibility` — tests AI answer engine (AEO) visibility for the client's target queries

```bash
echo "=== STEP 2: AUDIT CURRENT STATE ==="

# Invoke seo-content-audit skill
# (replace with actual skill invocation mechanism)
echo "Running seo-content-audit for $company_url ..."

# Invoke aeo-visibility for top queries derived from target_keywords
echo "Running aeo-visibility checks ..."
```

Capture and write the full audit output to `/app/results/seo_audit_report.md`. The report must include:
- Current content inventory (by type and topic)
- Domain authority, organic traffic, and keyword rankings
- Competitive gap matrix (what competitors rank for that the client does not)
- Brand voice profile (writing style extracted by brand-voice-extractor)
- AEO visibility scores for key queries

**Human checkpoint**: Share `seo_audit_report.md` with the client contact before proceeding to Step 3.

---

## Step 3: Identify Content Gaps

Analyze the audit output to identify and prioritize content opportunities across four gap types.

```python
# Identify gap categories from seo_audit_report.md
gaps = {
    "competitive_gaps": [],   # Keywords competitors rank for; client does not
    "funnel_gaps": [],        # Missing TOFU / MOFU / BOFU coverage
    "topic_gaps": [],         # Industry/vertical content that does not exist
    "comparison_gaps": []     # Missing "vs" and "alternatives" pages
}

# Prioritization formula: search_volume * commercial_intent_score * (1 / competitive_difficulty)
# Rank all gaps and select top N for the initial calendar
```

Write the prioritized list to `/app/results/content_gaps.md` with:
- Gap type, keyword / topic, estimated search volume, commercial intent (H/M/L), difficulty score, recommended content type

---

## Step 4: Build Keyword Architecture

Organize target keywords by funnel stage and map each cluster to a content type.

```markdown
# Keyword Architecture

## TOFU (Awareness)
- "what is [category]" → blog post / guide
- "[category] use cases" → blog post
- "how to [solve problem]" → tutorial / guide

## MOFU (Evaluation)
- "[category] comparison" → comparison page
- "how to choose [solution]" → buyer's guide
- "[compliance/technical] requirements" → technical guide

## BOFU (Decision)
- "[Company] vs [Competitor]" → comparison landing page
- "[Competitor] alternatives" → alternatives page
- pricing guides → pricing page
- migration guides → migration guide
```

Write the full keyword map to `/app/results/keyword_architecture.md`.

---

## Step 5: Create Content Calendar

Build a 8-week prioritized calendar based on urgency and funnel stage, plus an ongoing cadence plan.

Priority order:
1. **Week 1–2**: Highest-urgency BOFU pages (comparison pages; especially if competitors are publishing attack content)
2. **Week 2–4**: Core MOFU guides and evaluation content
3. **Week 4–8**: TOFU awareness content and programmatic SEO templates
4. **Ongoing**: 2–3 editorial pieces per week

**Human checkpoint**: Review content calendar with the client before drafting begins.

Write the calendar to `/app/results/content_calendar.md` with columns: Week, Content Title, Keyword Target, Funnel Stage, Content Type, Assignee / Skill, Status.

---

## Step 6: Draft Content

Use the `content-asset-creator` skill to draft each content item in the calendar, applying the brand voice profile extracted in Step 2.

Per content piece requirements:
- Match brand voice and writing style from `brand-voice-extractor` output
- Include target keywords naturally (no keyword stuffing)
- Build internal links to related content (see Step 7)
- Include clear CTAs aligned to funnel stage
- Add structured data / schema markup recommendations in comments

```bash
echo "=== STEP 6: DRAFT CONTENT ==="
for content_item in $(list_calendar_items); do
  echo "Drafting: $content_item ..."
  # invoke content-asset-creator skill
  # write output to /app/results/content_drafts/<slug>.md
done
```

**Human checkpoint**: Review all content drafts in `/app/results/content_drafts/` before publishing.

---

## Step 7: Build Internal Linking Architecture

Design the linking structure that ties all content pieces together into a cohesive SEO architecture.

Linking rules:
- TOFU pages → link to related MOFU pages
- MOFU pages → link to BOFU pages (comparison, pricing)
- BOFU pages → link to product / signup
- All pages → link to relevant pillar content

Write the linking plan to `/app/results/internal_linking_plan.md` with a table: Source Page → Destination Page → Anchor Text → Notes.

---

## Step 8: Publish & Monitor Setup

Provide the finalized content drafts to the client for publishing and configure ongoing monitoring.

Publishing checklist per page:
- [ ] Brand voice and style verified against profile
- [ ] Target keywords present naturally
- [ ] Internal links added per Step 7 plan
- [ ] CTA present and appropriate for funnel stage
- [ ] Structured data / schema markup recommendations noted
- [ ] Meta title and meta description written

Monitoring KPIs to track:
- Organic traffic by page / cluster
- Rankings by keyword (weekly)
- Content-to-signup conversion rate
- AEO visibility scores (monthly re-run)

---

## Step 9: Ongoing Cadence (max 12 review rounds)

Set up the recurring cadence for content operations. Repeat up to max 12 review rounds before requiring re-scoping.

| Cadence | Action |
|---------|--------|
| Weekly | Publish 2–3 pieces, monitor rankings, update content calendar |
| Monthly | Review content performance, refresh underperforming pages, update keyword architecture |
| Quarterly | Re-run `seo-content-audit` to measure progress and identify new gaps; restart from Step 3 |

---

## Step 10: Iterate on Errors (max 3 rounds)

If any step fails or produces incomplete output:

1. Read the specific failure from `validation_report.json`
2. Apply the targeted fix from the table below
3. Re-run the failed step and overwrite the affected output file
4. Re-validate

### Common Fixes

| Issue | Fix |
|-------|-----|
| seo-content-audit returns no data | Verify `company_url` is publicly crawlable; check SEO API credentials |
| Brand voice extraction fails | Provide a sample content piece manually for the extractor to analyze |
| Content calendar is empty | Ensure content_gaps.md was written with at least one gap entry |
| Draft file missing from content_drafts/ | Re-invoke content-asset-creator for that specific calendar item |
| Internal linking plan has broken references | Cross-check all page slugs in linking plan against content_calendar.md |

After 3 rounds, if a step still fails, document the failure in `summary.md` and set `overall_passed: false` in `validation_report.json`.

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/seo_audit_report.md" \
  "$RESULTS_DIR/content_gaps.md" \
  "$RESULTS_DIR/keyword_architecture.md" \
  "$RESULTS_DIR/content_calendar.md" \
  "$RESULTS_DIR/internal_linking_plan.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Check content_drafts directory has at least one file
DRAFT_COUNT=$(ls "$RESULTS_DIR/content_drafts/" 2>/dev/null | wc -l)
if [ "$DRAFT_COUNT" -gt 0 ]; then
  echo "PASS: content_drafts/ contains $DRAFT_COUNT file(s)"
else
  echo "FAIL: content_drafts/ is empty or missing"
fi
```

### Checklist

- [ ] `seo_audit_report.md` exists and includes domain authority, rankings, gap matrix, and brand voice profile
- [ ] `content_gaps.md` is prioritized and includes all four gap types
- [ ] `keyword_architecture.md` covers TOFU, MOFU, and BOFU clusters
- [ ] `content_calendar.md` covers at least 8 weeks with content items assigned
- [ ] `content_drafts/` contains at least one drafted content file
- [ ] `internal_linking_plan.md` covers all calendar content items
- [ ] `summary.md` exists and summarizes the run, key decisions, and issues
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Human checkpoints were observed at Steps 2, 5, and 6

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Run the audit first, plan second.** The keyword architecture and content calendar depend heavily on the audit output — do not shortcut Step 2 or the downstream steps will be based on assumptions rather than data.
- **BOFU before TOFU.** Comparison pages and alternatives pages have high commercial intent and often win rankings faster than broad awareness content. Prioritize them in Week 1–2.
- **Brand voice is non-negotiable.** Always apply the `brand-voice-extractor` output when drafting. Content that sounds off-brand creates friction in the publishing approval process.
- **Respect human checkpoints.** The runbook has three explicit human review gates (after audit, after calendar, after drafts). Do not skip them — client approval at each gate prevents wasted drafting effort.
- **AEO visibility is a leading indicator.** AI answer engine presence is growing rapidly; tracking AEO alongside traditional SERP rankings gives an early signal of content effectiveness.
- **The linking architecture is as important as the content.** A well-linked content cluster ranks faster than isolated pages. Build the linking plan in parallel with drafting, not after.
