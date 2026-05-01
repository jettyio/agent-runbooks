---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/coreyhaines31/marketingskills/seo-audit"
  source_host: "skills.sh"
  source_title: "SEO Audit"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "coreyhaines31"
    skill_name: "seo-audit"
    confidence: "high"
secrets: {}
---

# SEO Audit — Agent Runbook

## Objective

Conduct a comprehensive SEO audit of a target website, systematically assessing crawlability and indexation, technical foundations, on-page optimization, content quality, and authority signals. The agent gathers site context, identifies issues using available tools, and produces a prioritized action plan with impact levels and specific remediation steps. Schema markup is validated via Google Rich Results Test or browser-based inspection rather than static HTML parsing, to avoid false negatives from JavaScript-injected structured data. The audit concludes with a structured report categorizing findings by priority and site-type-specific recommendations.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/audit_report.md` | Full SEO audit report with findings per section and prioritized action plan |
| `/app/results/technical_findings.json` | Structured technical SEO findings (crawlability, speed, mobile, HTTPS, URLs) |
| `/app/results/onpage_findings.json` | Structured on-page SEO findings (titles, meta, headings, content, images, links) |
| `/app/results/content_findings.json` | Content quality assessment (E-E-A-T, depth, engagement signals) |
| `/app/results/action_plan.md` | Prioritized action plan: critical fixes, high-impact improvements, quick wins |
| `/app/results/summary.md` | Executive summary with overall health score, top issues, and quick wins |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

If you finish your analysis but have not written all files, go back and write them before stopping.

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Target URL | *(required)* | The site or page URL to audit |
| Site type | `auto-detect` | Site type: `saas`, `ecommerce`, `blog`, `local`, `multilingual` |
| Scope | `full` | Audit scope: `full`, `technical`, `onpage`, `content` |
| Search Console access | `false` | Whether Google Search Console data is available |
| Competitor URLs | *(optional)* | Comma-separated URLs of top organic competitors |
| Priority keywords | *(optional)* | Comma-separated target keywords/topics |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `requests` | Python package | Yes | Fetch target URLs and check HTTP status codes |
| `beautifulsoup4` | Python package | Yes | Parse HTML to extract meta tags, headings, canonical tags |
| `lxml` | Python package | Yes | HTML parser backend for BeautifulSoup |
| `pyyaml` | Python package | Yes | Parse and emit structured findings |
| Google PageSpeed Insights API | External API | Recommended | Fetch Core Web Vitals data for LCP, INP, CLS |
| Google Rich Results Test | External tool | Recommended | Validate schema markup (renders JavaScript) |
| Google Search Console | External tool | Optional | Coverage report, Core Web Vitals, index status |

## Step 1: Environment Setup

```bash
# Install dependencies
pip install requests beautifulsoup4 lxml pyyaml

# Create output directories
mkdir -p /app/results

# Verify TARGET_URL is set
if [ -z "${TARGET_URL}" ]; then
  echo "ERROR: TARGET_URL is not set. Set it before running."
  exit 1
fi

echo "Setup complete. Auditing: ${TARGET_URL}"
```

Verify the target URL is reachable:

```python
import requests

target_url = "TARGET_URL_HERE"
r = requests.get(target_url, timeout=15, allow_redirects=True)
print(f"Final URL: {r.url}")
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type', '')}")
```

## Step 2: Initial Assessment — Gather Site Context

Before auditing, collect the following context (from task description or by asking):

1. **Site Context**
   - What type of site? (SaaS, e-commerce, blog, local, multilingual)
   - What are the primary SEO goals and priority keywords/topics?

2. **Current State**
   - Known issues or concerns?
   - Current organic traffic level?
   - Any recent changes or migrations?

3. **Scope**
   - Full site audit or specific pages?
   - Technical + on-page, or one focus area?
   - Access to Search Console / analytics?

```python
import json, pathlib

# Record site context
site_context = {
    "target_url": "TARGET_URL_HERE",
    "site_type": "auto-detect",
    "scope": "full",
    "search_console_access": False,
    "known_issues": [],
    "priority_keywords": [],
    "competitors": []
}

pathlib.Path("/app/results/site_context.json").write_text(json.dumps(site_context, indent=2))
```

**Important:** Check for `.agents/product-marketing-context.md` or `.claude/product-marketing-context.md` if running in a project context — use that information before asking questions.

## Step 3: Technical SEO Audit

Audit the following in priority order. For each finding, record: issue, impact (High/Medium/Low), evidence, fix recommendation, and priority (1–5).

### 3a: Crawlability

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

target_url = "TARGET_URL_HERE"
parsed = urlparse(target_url)
base = f"{parsed.scheme}://{parsed.netloc}"

# Check robots.txt
robots_url = urljoin(base, "/robots.txt")
robots_r = requests.get(robots_url, timeout=10)
print(f"robots.txt status: {robots_r.status_code}")
if robots_r.ok:
    print(robots_r.text[:1000])

# Check sitemap.xml
sitemap_url = urljoin(base, "/sitemap.xml")
sitemap_r = requests.get(sitemap_url, timeout=10)
print(f"sitemap.xml status: {sitemap_r.status_code}")

# Crawlability checklist items to audit:
crawl_checklist = [
    "robots.txt exists and accessible",
    "No important pages blocked by robots.txt",
    "Sitemap reference in robots.txt",
    "XML sitemap exists and accessible",
    "Sitemap contains only canonical, indexable URLs",
    "Important pages within 3 clicks of homepage",
    "No orphan pages (check via internal link scan)",
    "Parameterized URLs controlled",
    "No session IDs in URLs",
]
```

### 3b: Indexation & Canonicalization

```python
r = requests.get(target_url, timeout=15)
soup = BeautifulSoup(r.text, 'lxml')

# Check canonical tag
canonical = soup.find('link', rel='canonical')
print(f"Canonical: {canonical['href'] if canonical else 'MISSING'}")

# Check noindex
robots_meta = soup.find('meta', attrs={'name': 'robots'})
print(f"Robots meta: {robots_meta['content'] if robots_meta else 'not set'}")

# Check HTTPS redirect
http_url = target_url.replace("https://", "http://")
http_r = requests.get(http_url, timeout=10, allow_redirects=True)
print(f"HTTP→HTTPS redirect: {http_r.history}")

# Indexation checklist items to audit:
indexation_checklist = [
    "site:domain.com check performed",
    "No noindex on important pages",
    "Canonicals point correct direction",
    "No redirect chains/loops",
    "No soft 404s",
    "Duplicate content has canonicals",
    "www vs non-www consistent",
    "Trailing slash consistent",
]
```

### 3c: Site Speed & Core Web Vitals

```python
# Use PageSpeed Insights API
import json

target_url = "TARGET_URL_HERE"
psi_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={target_url}&strategy=mobile"

# Note: API key optional for limited usage
psi_r = requests.get(psi_url, timeout=30)
if psi_r.ok:
    psi_data = psi_r.json()
    lhci = psi_data.get('lighthouseResult', {})
    audits = lhci.get('audits', {})

    lcp = audits.get('largest-contentful-paint', {}).get('displayValue', 'unknown')
    cls = audits.get('cumulative-layout-shift', {}).get('displayValue', 'unknown')

    print(f"LCP: {lcp} (target: < 2.5s)")
    print(f"CLS: {cls} (target: < 0.1)")

# CWV targets:
# LCP < 2.5s, INP < 200ms, CLS < 0.1
```

### 3d: Mobile-Friendliness, HTTPS, URL Structure

```python
# Check HTTPS
is_https = target_url.startswith("https://")
print(f"HTTPS: {is_https}")

# Check viewport meta
viewport = soup.find('meta', attrs={'name': 'viewport'})
print(f"Viewport meta: {viewport['content'] if viewport else 'MISSING'}")

# URL structure checklist:
url_checklist = [
    "Readable, descriptive URLs",
    "Keywords in URLs where natural",
    "Consistent URL structure",
    "No unnecessary parameters",
    "Lowercase and hyphen-separated",
    "Valid SSL certificate",
    "No mixed content",
    "HSTS header present",
]
```

Record all technical findings to `/app/results/technical_findings.json`.

## Step 4: International SEO Audit (when applicable)

Run this step only if the site serves multiple languages or regions.

**Schema Markup Detection Limitation:**
> `web_fetch` and `curl` cannot reliably detect structured data / schema markup. Many CMS plugins inject JSON-LD via client-side JavaScript — it won't appear in static HTML. Use the browser tool (`document.querySelectorAll('script[type="application/ld+json"]')`), Google Rich Results Test, or Screaming Frog to validate schema.

```python
# Check hreflang tags
hreflang_tags = soup.find_all('link', rel='alternate')
hreflang_entries = []
for tag in hreflang_tags:
    if tag.get('hreflang'):
        hreflang_entries.append({
            "hreflang": tag['hreflang'],
            "href": tag.get('href', '')
        })

print(f"Hreflang entries found: {len(hreflang_entries)}")
for entry in hreflang_entries:
    print(f"  {entry['hreflang']}: {entry['href']}")

# Hreflang checklist:
hreflang_checklist = [
    "Self-referencing entry present on every page",
    "Reciprocal links (bidirectional)",
    "Valid codes (ISO 639-1 + optional ISO 3166-1 Alpha 2)",
    "x-default present pointing to fallback",
    "All target URLs return 200, are indexable, match canonical",
    "No duplicate language-region codes",
    "No cross-locale canonicals",
    "Each locale page self-canonicals",
    "No IP/Accept-Language content negotiation",
    "Trailing slash + case consistent across locale paths",
]
```

## Step 5: On-Page SEO Audit

```python
import re

r = requests.get(target_url, timeout=15)
soup = BeautifulSoup(r.text, 'lxml')

# Title tag
title_tag = soup.find('title')
title_text = title_tag.get_text().strip() if title_tag else ''
print(f"Title: {title_text!r} ({len(title_text)} chars)")
print(f"  Target: 50-60 chars, primary keyword near start")

# Meta description
meta_desc = soup.find('meta', attrs={'name': 'description'})
desc_text = meta_desc['content'].strip() if meta_desc else ''
print(f"Meta desc: {desc_text!r} ({len(desc_text)} chars)")
print(f"  Target: 150-160 chars, includes primary keyword")

# Heading structure
h1s = soup.find_all('h1')
h2s = soup.find_all('h2')
h3s = soup.find_all('h3')
print(f"H1 count: {len(h1s)} (target: exactly 1)")
for h in h1s:
    print(f"  H1: {h.get_text().strip()!r}")

# Images without alt text
imgs = soup.find_all('img')
missing_alt = [img.get('src', '') for img in imgs if not img.get('alt')]
print(f"Images without alt text: {len(missing_alt)}/{len(imgs)}")

# Internal links
all_links = soup.find_all('a', href=True)
internal = [a['href'] for a in all_links if not a['href'].startswith('http') or target_url.split('/')[2] in a['href']]
print(f"Internal links: {len(internal)}")

# Record on-page findings
onpage_findings = {
    "title": {"text": title_text, "length": len(title_text), "issues": []},
    "meta_description": {"text": desc_text, "length": len(desc_text), "issues": []},
    "h1_count": len(h1s),
    "h1_texts": [h.get_text().strip() for h in h1s],
    "h2_count": len(h2s),
    "images_total": len(imgs),
    "images_missing_alt": len(missing_alt),
    "internal_link_count": len(internal),
}

import pathlib, json
pathlib.Path("/app/results/onpage_findings.json").write_text(json.dumps(onpage_findings, indent=2))
```

Assess for each page audited:
- **Title tags**: Unique, 50–60 chars, primary keyword near beginning, compelling
- **Meta descriptions**: Unique, 150–160 chars, includes keyword, clear value proposition and CTA
- **Heading structure**: One H1, logical hierarchy (H1→H2→H3), headings describe content
- **Content optimization**: Keyword in first 100 words, sufficient depth, satisfies search intent
- **Image optimization**: Descriptive filenames, alt text, compressed sizes, modern formats (WebP)
- **Internal linking**: Important pages well-linked, descriptive anchor text, no broken links

## Step 6: Content Quality Assessment

```python
# E-E-A-T signals checklist
eeat_checklist = {
    "experience": [
        "First-hand experience demonstrated",
        "Original insights/data present",
        "Real examples and case studies included",
    ],
    "expertise": [
        "Author credentials visible",
        "Information accurate and detailed",
        "Claims properly sourced",
    ],
    "authoritativeness": [
        "Recognized in the space",
        "Cited by others",
        "Industry credentials shown",
    ],
    "trustworthiness": [
        "Accurate information",
        "Business transparent",
        "Contact information available",
        "Privacy policy and terms present",
        "Site is HTTPS",
    ]
}

content_findings = {
    "eeat": eeat_checklist,
    "content_depth": {
        "comprehensive": None,
        "answers_followup": None,
        "better_than_competitors": None,
        "updated_current": None,
    },
    "site_type_issues": [],
}

import pathlib, json
pathlib.Path("/app/results/content_findings.json").write_text(json.dumps(content_findings, indent=2))
```

**Site-type-specific content issues to check:**
- **SaaS**: Product pages lack content depth; blog not integrated; missing comparison/alternative pages
- **E-commerce**: Thin category pages; duplicate product descriptions; missing product schema; faceted navigation duplicates
- **Content/Blog**: Outdated content; keyword cannibalization; poor internal linking; missing author pages
- **Multilingual**: Hreflang errors; cross-locale canonicals; thin locale pages; boilerplate-only translations; no x-default
- **Local**: Inconsistent NAP; missing local schema; no Google Business Profile optimization; no location pages

## Step 7: Iterate on Errors (max 3 rounds)

If any audit step fails to return data (network errors, parse failures, blocked access):

1. Note the specific failure and error message
2. Apply the targeted fix from the table below
3. Retry the failed step
4. Repeat up to 3 times total

### Common Fixes

| Issue | Fix |
|-------|-----|
| HTTP 403 / blocked by bot protection | Use a browser-like User-Agent header; try with `session.headers.update({"User-Agent": "Mozilla/5.0..."})` |
| robots.txt blocks crawling | Note the block as a finding; do not bypass — report it |
| Schema markup not found via `requests` | Use browser tool or Google Rich Results Test — static HTML cannot detect JS-injected JSON-LD |
| PageSpeed API rate limited | Retry with exponential backoff, or note that manual PageSpeed check is needed |
| Hreflang tags missing | Check both `<head>` and HTTP response headers (`Link:`) and XML sitemap |
| Soft 404 detection | Check response body for "not found" messaging even on 200 responses |

## Step 8: Compile Findings and Action Plan

```python
import json, pathlib

# Load all findings
technical = json.loads(pathlib.Path("/app/results/technical_findings.json").read_text())
onpage = json.loads(pathlib.Path("/app/results/onpage_findings.json").read_text())
content = json.loads(pathlib.Path("/app/results/content_findings.json").read_text())

# Build prioritized action plan
action_plan = {
    "critical": [],    # Blocking indexation or ranking
    "high_impact": [], # Major improvements
    "quick_wins": [],  # Easy, immediate benefit
    "long_term": [],   # Strategic improvements
}

# Write action plan
pathlib.Path("/app/results/action_plan.md").write_text("# Prioritized Action Plan\n\n## Critical Fixes\n\n## High-Impact Improvements\n\n## Quick Wins\n\n## Long-Term Recommendations\n")
```

Write the full audit report to `/app/results/audit_report.md` following this structure:

```markdown
# SEO Audit Report — [Site Name]

## Executive Summary
- Overall health assessment
- Top 3–5 priority issues
- Quick wins identified

## Technical SEO Findings
| Issue | Impact | Evidence | Fix | Priority |
|-------|--------|----------|-----|----------|
| ...   | High   | ...      | ... | 1        |

## On-Page SEO Findings
[Same table format]

## Content Findings
[Same table format]

## Prioritized Action Plan
1. Critical fixes (blocking indexation/ranking)
2. High-impact improvements
3. Quick wins (easy, immediate benefit)
4. Long-term recommendations
```

## Step 9: Write Summary and Validation Report

Write `/app/results/summary.md` with:
- Target site and audit date
- Overall health assessment (Good / Needs Work / Critical Issues)
- Top 3–5 priority issues
- Quick wins
- Scope covered

Write `/app/results/validation_report.json` with structured stage results.

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/audit_report.md" \
  "$RESULTS_DIR/technical_findings.json" \
  "$RESULTS_DIR/onpage_findings.json" \
  "$RESULTS_DIR/content_findings.json" \
  "$RESULTS_DIR/action_plan.md" \
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

- [ ] `audit_report.md` exists with Executive Summary, Technical, On-Page, and Content sections
- [ ] `technical_findings.json` contains structured crawlability, speed, mobile, HTTPS findings
- [ ] `onpage_findings.json` contains title, meta, heading, image, and link findings
- [ ] `content_findings.json` contains E-E-A-T assessment and site-type-specific issues
- [ ] `action_plan.md` contains prioritized recommendations (critical → quick wins → long-term)
- [ ] `summary.md` provides overall health assessment and top issues
- [ ] `validation_report.json` contains stages, results counts, and `overall_passed`
- [ ] Schema markup validated via browser tool or Rich Results Test (not just static HTML)
- [ ] Site-type-specific checklist items evaluated
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Schema markup detection:** `web_fetch` and `curl` strip `<script>` tags and cannot detect JS-injected JSON-LD. Always use the browser tool (`document.querySelectorAll('script[type="application/ld+json"]')`), Google Rich Results Test, or Screaming Frog for schema validation.
- **robots.txt is not auth bypass.** If a page is blocked, report it as a finding — do not circumvent the block.
- **Hreflang is bidirectional.** If page A points to page B via hreflang, page B must point back to page A. Missing return links cause Google to ignore the entire pair.
- **Canonical overrides hreflang.** When they conflict, canonical wins. Always check both are consistent.
- **Core Web Vitals are field data.** Lab tests (PageSpeed) approximate field experience. Prefer Search Console CWV report when available for real-user data.
- **Content quality is site-wide.** Many thin locale/tag pages drag down rankings for strong pages too. Recommend consolidation or noindex only after confirming the pages provide no indexing value.
- **Keyword cannibalization check:** Look for multiple pages targeting the same keyword — they compete against each other. Recommend consolidation or differentiation.
- **Related skills:** `ai-seo` for AI search optimization, `programmatic-seo` for at-scale page building, `schema-markup` for structured data implementation, `site-architecture` for navigation and URL structure, `analytics-tracking` for measuring performance.
