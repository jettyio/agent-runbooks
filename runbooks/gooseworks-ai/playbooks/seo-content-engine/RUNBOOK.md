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
    source_collection: "playbooks"
    skill_name: "seo-content-engine"
    confidence: "high"
---

# SEO Content Engine — Agent Runbook

## Objective

Build and run a compounding SEO content engine for a client, progressing through audit, gap analysis, keyword architecture, content calendar creation, content drafting, and publishing pipeline setup. The agent audits the current SEO state using composite skills (seo-content-audit, aeo-visibility), identifies competitive and funnel gaps, constructs a prioritized keyword architecture across TOFU/MOFU/BOFU stages, and produces a concrete content calendar and drafted content assets aligned to the client's brand voice. This runbook translates the gooseworks-ai `seo-content-engine` playbook skill into a Jetty-deployable, programmatically-evaluated agent workflow.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/seo_audit_summary.md` | Summary of the SEO audit findings (current state, domain authority, rankings) |
| `/app/results/content_gaps.md` | Identified content gaps: competitive, funnel, topic, and comparison gaps |
| `/app/results/keyword_architecture.md` | Keyword architecture organized by funnel stage (TOFU/MOFU/BOFU) |
| `/app/results/content_calendar.md` | Prioritized content calendar with weekly/monthly plan |
| `/app/results/content_drafts/` | Directory containing drafted content pieces |
| `/app/results/internal_linking_map.md` | Internal linking architecture design |
| `/app/results/summary.md` | Executive summary with run metadata and outcomes |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Company URL | *(required)* | Client website URL to audit |
| Target keywords | *(required)* | Initial seed keywords for the SEO strategy |
| Client context | *(required)* | Path to `context.md` with ICP, value props, positioning |
| Top competitors | *(optional)* | Comma-separated competitor URLs; if omitted, agent identifies them |
| Content cadence | `2-3 per week` | Target content publishing frequency |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `requests` | Python package | Yes | HTTP fetching for SEO audits and data gathering |
| `pyyaml` | Python package | Yes | Parsing skill frontmatter and configuration |
| `markdown-it-py` | Python package | Yes | Parsing and generating markdown content |
| `gh` | CLI | Yes | GitHub CLI for any repository operations |
| `git` | CLI | Yes | Version control for content assets |
| seo-content-audit skill | External skill | Yes | Composite skill: site-content-catalog + seo-domain-analyzer + brand-voice-extractor |
| aeo-visibility skill | External skill | Yes | Tests AI answer engine visibility for key queries |
| brand-voice-extractor skill | External skill | Yes | Extracts writing style profile from existing content |
| visual-brand-extractor skill | External skill | Yes | Extracts visual brand elements |
| content-asset-creator skill | External skill | Yes | Creates landing pages, reports, one-pagers |
| competitor-intel skill | External skill | Yes | Competitive intelligence gathering |

---

## Step 1: Environment Setup

```bash
# Install Python dependencies
pip install requests pyyaml markdown-it-py

# Verify CLI tools
command -v git >/dev/null || { echo "ERROR: git not installed"; exit 1; }
command -v gh  >/dev/null || { echo "ERROR: gh CLI not installed"; exit 1; }

# Create output directories
mkdir -p /app/results/content_drafts

# Validate required inputs
for var in COMPANY_URL TARGET_KEYWORDS CLIENT_CONTEXT_PATH; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var is not set"
    exit 1
  fi
done

echo "Environment ready."
```

Verify all required inputs are available. If `COMPANY_URL` is empty or not a valid `http(s)://` URL, fail fast with a clear error.

---

## Step 2: Audit Current State

Run the full SEO audit to understand the client's current position.

**Skills to invoke:**
- `seo-content-audit` (orchestrates site-content-catalog + seo-domain-analyzer + brand-voice-extractor)
- `aeo-visibility` — test AI answer engine visibility for key queries

**Collect:**
- Current content inventory (what exists, by type and topic)
- Domain authority, organic traffic, keyword rankings
- Competitive gap matrix (what competitors rank for that the client doesn't)
- Brand voice profile (writing style to match)
- AI answer engine visibility for the client's key queries

```python
import json, pathlib

# Invoke seo-content-audit skill (pseudo-code — replace with actual skill invocation)
audit_result = invoke_skill("seo-content-audit", {
    "company_url": COMPANY_URL,
    "client_context": CLIENT_CONTEXT_PATH
})

# Invoke aeo-visibility skill
aeo_result = invoke_skill("aeo-visibility", {
    "company_url": COMPANY_URL,
    "keywords": TARGET_KEYWORDS.split(",")
})

# Write audit summary
summary = f"""# SEO Audit Summary

## Domain
- URL: {COMPANY_URL}
- Domain Authority: {audit_result.get('domain_authority', 'N/A')}
- Organic Traffic (est.): {audit_result.get('organic_traffic', 'N/A')}

## Content Inventory
{audit_result.get('content_inventory_summary', 'See full audit output')}

## Keyword Rankings
{audit_result.get('keyword_rankings_summary', 'See full audit output')}

## AI Answer Engine Visibility
{aeo_result.get('visibility_summary', 'See aeo output')}

## Brand Voice Profile
{audit_result.get('brand_voice_summary', 'See brand voice extractor output')}
"""
pathlib.Path("/app/results/seo_audit_summary.md").write_text(summary)
print("seo_audit_summary.md written")
```

**Human checkpoint after Step 2:** Review audit findings before proceeding.

---

## Step 3: Identify Content Gaps

From the audit output, identify and categorize gaps.

**Gap types to identify:**
- **Competitive gaps**: Keywords competitors rank for that the client doesn't
- **Funnel gaps**: Missing content at TOFU, MOFU, or BOFU stages
- **Topic gaps**: Industry/vertical content that doesn't exist for the client
- **Comparison gaps**: Missing "vs" pages and "alternatives" pages

**Prioritization formula:** `search_volume × commercial_intent × (1 / competitive_difficulty)`

```python
import json, pathlib

gaps = {
    "competitive_gaps": [],   # [{keyword, competitor, volume, difficulty}]
    "funnel_gaps": {
        "tofu": [],
        "mofu": [],
        "bofu": []
    },
    "topic_gaps": [],
    "comparison_gaps": []
}

# Populate gaps from audit_result (replace with actual skill output parsing)
# ... gap analysis logic ...

pathlib.Path("/app/results/content_gaps.md").write_text(
    "# Content Gap Analysis\n\n" + json.dumps(gaps, indent=2)
)
print("content_gaps.md written")
```

---

## Step 4: Build Keyword Architecture

Organize target keywords by funnel stage and map to content types.

| Stage | Intent | Examples | Content Types |
|-------|--------|----------|---------------|
| **TOFU** | Awareness | "what is [category]", "[category] use cases", "how to [solve problem]" | Blog posts, guides |
| **MOFU** | Evaluation | "[category] comparison", "how to choose [solution]", "[compliance] requirements" | Comparison guides, whitepapers |
| **BOFU** | Decision | "[Company] vs [Competitor]", "[Competitor] alternatives", pricing guides, migration guides | Landing pages, comparison pages |

Map each keyword cluster to a specific content type and target URL slug.

```python
import pathlib

architecture_md = """# Keyword Architecture

## TOFU (Awareness)
| Keyword Cluster | Monthly Volume | Difficulty | Content Type | Target URL |
|-----------------|----------------|------------|--------------|------------|
| (populate from gap analysis) | | | | |

## MOFU (Evaluation)
| Keyword Cluster | Monthly Volume | Difficulty | Content Type | Target URL |
|-----------------|----------------|------------|--------------|------------|
| (populate from gap analysis) | | | | |

## BOFU (Decision)
| Keyword Cluster | Monthly Volume | Difficulty | Content Type | Target URL |
|-----------------|----------------|------------|--------------|------------|
| (populate from gap analysis) | | | | |
"""
pathlib.Path("/app/results/keyword_architecture.md").write_text(architecture_md)
print("keyword_architecture.md written")
```

---

## Step 5: Create Content Calendar

Build a prioritized content calendar. Max 3 rounds of refinement if the calendar is rejected at the human checkpoint.

**Priority order:**
1. **Week 1–2**: Highest-urgency BOFU pages (comparison pages, especially if competitors are publishing attack content)
2. **Week 2–4**: Core MOFU guides and evaluation content
3. **Week 4–8**: TOFU awareness content and programmatic SEO templates
4. **Ongoing**: 2–3 editorial pieces per week

```python
import pathlib

calendar_md = """# Content Calendar

## Week 1-2: BOFU Priority
| Priority | Title | Type | Target Keyword | Word Count | Owner |
|----------|-------|------|----------------|------------|-------|
| 1 | (populate) | Comparison page | | 2000 | Agent |

## Week 2-4: MOFU Core Guides
| Priority | Title | Type | Target Keyword | Word Count | Owner |
|----------|-------|------|----------------|------------|-------|

## Week 4-8: TOFU Awareness
| Priority | Title | Type | Target Keyword | Word Count | Owner |
|----------|-------|------|----------------|------------|-------|

## Ongoing Cadence
- Weekly: Publish 2-3 pieces, monitor rankings
- Monthly: Review performance, update calendar, refresh underperforming pages
- Quarterly: Re-run seo-content-audit to measure progress and identify new gaps
"""
pathlib.Path("/app/results/content_calendar.md").write_text(calendar_md)
print("content_calendar.md written")
```

**Human checkpoint after Step 5:** Review content calendar before drafting begins.

---

## Step 6: Iterate on Calendar (max 3 rounds)

If the calendar is rejected at the human checkpoint or fails internal review:

1. Read the specific feedback
2. Adjust priorities based on feedback (urgency, volume, difficulty scores)
3. Re-generate calendar and overwrite `/app/results/content_calendar.md`
4. Re-present for review
5. Repeat up to 3 times total

### Common Fixes

| Issue | Fix |
|-------|-----|
| Calendar priorities misaligned | Re-score using `volume × intent / difficulty`; move highest-score items to Week 1–2 |
| Brand voice mismatch in drafts | Re-run `brand-voice-extractor` on 5+ fresh source pieces; pass profile to content-asset-creator |
| Keyword gaps incomplete | Re-run `seo-content-audit` with expanded competitor list; add 2–3 more competitors |
| Missing BOFU comparison pages | Check competitor site for their "alternatives" and "vs" pages; mirror with client positioning |
| Internal links not resolving | Regenerate `internal_linking_map.md` after all slugs are finalized in `content_calendar.md` |
| `validation_report.json` missing | Re-run final checklist script; write report manually from check results if needed |

---

## Step 7: Draft Content

For each content piece in the calendar, use `content-asset-creator` skill with brand voice matching.

**For each content piece:**
- Match the client's brand voice and style (from brand-voice-extractor output)
- Include target keywords naturally (1–2% keyword density)
- Build internal linking to related content
- Include clear CTAs aligned to funnel stage
- Add structured data / schema markup recommendations

```python
import pathlib

drafts_dir = pathlib.Path("/app/results/content_drafts")
drafts_dir.mkdir(exist_ok=True)

# For each piece in content_calendar, invoke content-asset-creator
# content = invoke_skill("content-asset-creator", {...})
# (drafts_dir / f"{slug}.md").write_text(content)

print("Content drafts written to /app/results/content_drafts/")
```

**Human checkpoint after Step 7:** Review content drafts before publishing.

---

## Step 8: Build Internal Linking Architecture

Design the linking structure to maximize SEO equity flow.

```markdown
- TOFU pages → link to related MOFU pages
- MOFU pages → link to BOFU pages (comparison, pricing)
- BOFU pages → link to product/signup
- All pages → link to relevant pillar content
```

```python
import pathlib

linking_md = """# Internal Linking Architecture

## Pillar Content
| Pillar Page | URL | Links To |
|-------------|-----|----------|
| (populate) | | |

## Link Flow
- TOFU → MOFU → BOFU → Conversion
- Each TOFU page links to 2-3 MOFU pages
- Each MOFU page links to 1-2 BOFU pages
- BOFU pages link directly to product/signup page
"""
pathlib.Path("/app/results/internal_linking_map.md").write_text(linking_md)
print("internal_linking_map.md written")
```

---

## Step 9: Publish and Monitor Setup

Configure tracking and establish the ongoing cadence.

```bash
# Verify all output files before publish handoff
for f in \
  /app/results/seo_audit_summary.md \
  /app/results/content_gaps.md \
  /app/results/keyword_architecture.md \
  /app/results/content_calendar.md \
  /app/results/internal_linking_map.md; do
  [ -s "$f" ] && echo "PASS: $f" || echo "FAIL: $f missing or empty"
done

echo "Handoff package ready for client publish."
```

**Metrics to track:**
- Organic traffic by page/cluster
- Rankings by keyword cluster (weekly)
- Content-to-signup conversion rate

**Monitoring cadence:**
- **Weekly**: Publish 2–3 pieces, check rankings
- **Monthly**: Review content performance, update calendar, refresh underperforming pages
- **Quarterly**: Re-run `seo-content-audit` to measure progress and identify new gaps

---

## Final Checklist

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/seo_audit_summary.md" \
  "$RESULTS_DIR/content_gaps.md" \
  "$RESULTS_DIR/keyword_architecture.md" \
  "$RESULTS_DIR/content_calendar.md" \
  "$RESULTS_DIR/internal_linking_map.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== END VERIFICATION ==="
```

### Checklist

- [ ] `seo_audit_summary.md` exists and contains domain authority, content inventory, and keyword rankings
- [ ] `content_gaps.md` exists with competitive, funnel, topic, and comparison gaps identified
- [ ] `keyword_architecture.md` exists with TOFU/MOFU/BOFU keyword clusters mapped to content types
- [ ] `content_calendar.md` exists with prioritized weekly plan and ongoing cadence
- [ ] `content_drafts/` directory contains at least one drafted content piece
- [ ] `internal_linking_map.md` exists with pillar page structure defined
- [ ] `summary.md` exists and summarizes outcomes
- [ ] `validation_report.json` exists with `overall_passed: true`
- [ ] Human checkpoints completed: after audit (Step 2), calendar (Step 5), drafts (Step 7)

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Prioritize BOFU first.** Comparison pages and "vs" content drive the highest commercial intent. Start there even if TOFU content seems more scalable — revenue impact is faster.
- **Brand voice is non-negotiable.** Run `brand-voice-extractor` on at least 5 existing pieces before drafting. Generic content that doesn't match the client's voice will be rejected.
- **Quarterly re-audits compound.** The true value of this engine is in the quarterly re-run cycle — each audit reveals new gaps opened by competitor moves and algorithm updates.
- **Comparison gaps are often overlooked.** Most clients have zero "[Competitor] alternatives" or "[Client] vs [Competitor]" pages. These convert extremely well and are quick wins.
- **Internal linking is an SEO force multiplier.** A well-linked content cluster passes equity from high-DA TOFU pages down to BOFU pages that need ranking power.
- **Use programmatic SEO for TOFU scale.** For clients with broad addressable markets, TOFU content can be templated (city pages, use-case pages, industry pages) using `content-asset-creator` with variable substitution.
