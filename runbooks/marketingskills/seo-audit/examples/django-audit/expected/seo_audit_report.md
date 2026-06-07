# SEO Audit Report — https://www.djangoproject.com

**Date:** 2026-06-07
**Scope:** Full (Technical + On-Page + Content)
**Site Type:** Open-source developer framework / Community site (SaaS-adjacent)
**Auditor:** Automated static audit via curl/fetch

---

## Executive Summary

**Overall Health: Needs Attention**

djangoproject.com is a well-structured, fast, and credible site for one of the most widely used web frameworks. The technical foundation is solid — CDN, HSTS, correct redirects for www/trailing-slash, a comprehensive sitemap — but several foundational SEO elements are absent sitewide: meta descriptions are uniformly empty, canonical tags are missing entirely, HTTP content is served without redirecting to HTTPS, and no structured data markup was found.

These are not minor gaps; they directly affect click-through rate, indexation deduplication, and rich-result eligibility. The good news is that most fixes are template-level changes that can be shipped quickly.

**Top 5 issues:**
1. Empty meta descriptions on all primary pages (homepage, /start/, /download/, /community/, /foundation/, /weblog/)
2. No canonical tags sitewide
3. HTTP serves content without redirecting to HTTPS
4. No structured data / schema markup detected
5. Sitemap URL missing from robots.txt

**Quick wins identified:** canonical tags (30 min), robots.txt sitemap reference (5 min), HTTP→HTTPS redirect (1 hr), announcement banner heading fix (30 min), remove dead keywords meta tag (15 min).

---

## Technical SEO Findings

| Issue | Impact | Evidence | Fix | Priority |
|-------|--------|----------|-----|----------|
| HTTP does not redirect to HTTPS | High | `curl -sI http://www.djangoproject.com/` returns 200 OK; no Location header | Add nginx `return 301 https://$host$request_uri;` rule | 1 |
| No canonical tags on any page | High | grep for `<link rel="canonical">` returns empty on all checked pages | Add self-referencing canonical `<link rel="canonical">` in base template | 1 |
| Core Web Vitals — not evaluated | High | PageSpeed Insights unavailable in this environment | Requires external tool — run PSI on homepage, /start/overview/, and a weblog post | 1 |
| Sitemap not referenced in robots.txt | Medium | robots.txt has only two Disallow rules; no Sitemap directive despite sitemap.xml existing at /sitemap.xml with 975 URLs | Add `Sitemap: https://www.djangoproject.com/sitemap.xml` to robots.txt | 2 |
| Sitemap includes dashboard subdomain URLs | Medium | sitemap.xml contains `<loc>https://dashboard.djangoproject.com/</loc>` and `/metric/` — likely non-public tool | Remove dashboard.djangoproject.com URLs from sitemap or add noindex to those pages | 2 |
| H2 appears before H1 in DOM on multiple pages | Medium | Homepage: `<h2>Django Developer Survey</h2>` at line ~76, `<h1>Meet Django</h1>` follows. Same on /start/overview/ (H2 at line 145, H1 at line 163) | Change sitewide announcement banner to use `<p>`, `<aside>`, or `<div>` instead of `<h2>` | 3 |
| No structured data / schema markup | Medium | No `application/ld+json` or microdata found in static HTML across homepage and blog posts. Requires Google Rich Results Test for full JS-rendered verification | Add WebSite + SoftwareApplication JSON-LD to homepage; BlogPosting to weblog posts | 3 |
| No privacy policy or terms page | Medium | 404 returned for /privacy-policy/, /privacy/, /terms/, /contact/ — standard E-E-A-T trust signals expected by Google's QRG | Create /privacy/ and link from footer; add /contact/ with foundation contact info | 3 |
| HSTS header served on HTTP connection | Low | `curl -sI http://` returns `Strict-Transport-Security` header — ignored by browsers on HTTP per RFC 6797 | Fix HTTP→HTTPS redirect at nginx layer (resolves this automatically) | 4 |
| No lazy loading on images | Low | No `loading="lazy"` found; site uses inline SVGs for icons (acceptable). Future img elements should include lazy loading | Add `loading="lazy"` to all below-fold `<img>` elements when added | 5 |

### Crawlability Assessment

**robots.txt:** Clean. Only `/admin` and `/checklists` are blocked, both correct. No unintentional blocks on crawlable content. **Issue:** sitemap not referenced (see table above).

```
User-agent: *
Disallow: /admin
Disallow: /checklists
```

**Sitemap:** Accessible at `/sitemap.xml`. Contains 975 URLs, including recent weblog posts (dated June 2026), core pages, foundation pages, and community resources. URLs appear clean and canonical. **Issue:** includes `dashboard.djangoproject.com` URLs that appear to be non-public infrastructure.

**Site architecture:** Logical, shallow hierarchy. Key pages (download, documentation, community, foundation) are 1 click from homepage. Weblog posts are 2 clicks max. No orphan pages observed.

### Security & HTTPS

| Check | Status |
|-------|--------|
| Site served over HTTPS | PASS |
| HSTS header present | PASS — `max-age=31536000; includeSubDomains; preload` |
| HSTS preload eligible | PASS |
| Mixed content (HTTP resources on HTTPS) | PASS — no HTTP resource URLs found in HTML |
| HTTP → HTTPS redirect | **FAIL** — HTTP returns 200, not 301 |
| Valid SSL certificate | ASSUMED PASS (HTTPS loads without error; not verified programmatically) |

### URL Structure

| Check | Status |
|-------|--------|
| Non-www → www redirect | PASS — 301 redirect confirmed |
| Trailing slash consistency | PASS — `/start` → 301 → `/start/`, `/download` → 301 → `/download/` |
| Lowercase URLs | PASS |
| Descriptive URLs | PASS — `/start/overview/`, `/foundation/corporate-members/`, `/conduct/enforcement-manual/` |
| Unnecessary parameters | PASS — no URL parameters observed in sitemap |

### International SEO

The site is English-only (`<html lang="en">`, `Content-Language: en`). No hreflang annotations found in the sitemap or HTML. As a single-language site targeting English-speaking developers globally, this is acceptable. If international expansion is planned, hreflang implementation should be considered at that time.

---

## On-Page SEO Findings

| Issue | Impact | Evidence | Fix | Priority |
|-------|--------|----------|-----|----------|
| Empty meta descriptions on all primary pages | High | `<meta name="description" content="">` (empty) on homepage, /start/, /start/overview/, /download/, /community/, /foundation/, /weblog/ | Write unique 150–160 char descriptions per page | 1 |
| Blog post descriptions are author bylines | High | /weblog post meta description: "Posted by Natalia Bidart on June 3, 2026" — no content preview | Pull first excerpt sentence or add dedicated excerpt field to blog post model | 1 |
| Title tags are generic and miss keyword opportunities | Medium | "Django overview \| Django" — 'overview' is vague. "News & Events \| Django" — misses 'Django blog', 'Django releases'. Multiple pages repeat brand name redundantly | Revise titles: lead with primary keyword, avoid "Django \| Django" pattern | 2 |
| H1 and title misaligned on homepage and overview | Medium | Homepage: title="The web framework for perfectionists…", H1="Meet Django". Overview: title="Django overview", H1="Why Django?" | Align H1 with title tag primary keyword | 2 |
| /start/ page has thin content (~305 words) | Medium | Page body is primarily a link list to tutorials; no descriptive text explaining the path or what Django is | Expand to 500–700 words with step descriptions and a code snippet | 3 |
| OG description identical across most pages | Low | og:description = "The web framework for perfectionists with deadlines." on 5+ pages | Set og:description to match per-page meta description once those are written | 4 |
| Keywords meta tag in base template | Low | `<meta name="keywords" content="Python, Django, framework, open-source">` — ignored by all major search engines since 2009 | Remove from base template | 5 |
| Weblog index H1 low keyword value | Low | H1 is "News & Events" — misses "Django blog", "Django changelog", "Django releases" | Rename to "Django News & Releases" | 5 |

### Page-by-Page Findings

**Homepage (`/`)**
- Title: "The web framework for perfectionists with deadlines \| Django" (56 chars — within limit)
- H1: "Meet Django" — does not match title keyword signal; misses "Python web framework"
- Meta description: **EMPTY**
- DOM order: H2 ("Django Developer Survey") precedes H1 ("Meet Django")
- Content: Strong — clear value props (fast, secure, scalable), community links, news feed, code examples via sidebar
- Internal links: Good — all key nav sections linked; download and docs prominently linked

**Getting Started (`/start/`)**
- Title: "Getting started with Django \| Django"
- H1: "Getting started with Django" — aligned with title (good)
- Meta description: **EMPTY**
- Content depth: Thin — ~305 words, primarily a link list

**Django Overview (`/start/overview/`)**
- Title: "Django overview \| Django"
- H1: "Why Django?" — misaligned with title
- Meta description: **EMPTY**
- DOM order: H2 appears before H1 (announcement banner)
- Content: Good descriptions of Django's features; Sites Using Django section present

**Download (`/download/`)**
- Title: "Download Django \| Django"
- H1: "How to get Django" — semi-aligned (different wording)
- Meta description: **EMPTY**
- OG description: "The latest official version is 6.0.6" — reactive, not keyword-rich

**Community (`/community/`)**
- Title: "Django Community \| Django"
- H1: "Community"
- Meta description: **EMPTY**

**Weblog (`/weblog/`)**
- Title: "News & Events \| Django"
- H1: "News & Events"
- Meta description: **EMPTY**

**Blog Post (`/weblog/2026/jun/03/security-releases/`)**
- Title: "Django security releases issued: 6.0.6 and 5.2.15 \| Weblog \| Django" — descriptive, good length
- H1: "Django security releases issued: 6.0.6 and 5.2.15" — aligned with title
- Meta description: "Posted by Natalia Bidart on June 3, 2026" — **useless as SERP snippet**
- Heading structure: H1 → H2 → H3 — correct hierarchy ✓
- Author attribution: Present in meta (og:article:author) and text

---

## Content Findings

| Issue | Impact | Evidence | Fix | Priority |
|-------|--------|----------|-----|----------|
| Blog posts valuable but meta undercuts SERP CTR | High | Meta description = author byline, not content summary | Fix blog post meta description template | 1 |
| No comparison / alternatives content | Medium | No pages targeting 'Django vs FastAPI', 'best Python web framework' queries | Create a /start/overview/why-django/ page or comparison blog post | 3 |
| No internal links from blog posts to product pages | Medium | Security release post does not link to /download/ or /security/ pages | Establish content linking template for blog posts | 3 |
| No case studies or 'Built with Django' content | Medium | /start/overview/ has logo grid but no narrative case studies | Create 4–8 short case study pages in /success-stories/ | 4 |
| E-E-A-T strong but not surfaced in text | Medium | Django Software Foundation, 20+ years of maintenance — credibility not stated on key pages | Add "Maintained by the Django Software Foundation since 2005" to footer; add text org names to Sites Using Django section | 4 |
| Content freshness indicators absent on feature pages | Low | /start/overview/ has no "Updated for Django 6.0" or last-reviewed date | Add version/date stamp to static feature pages | 5 |

### E-E-A-T Assessment

| Signal | Status | Notes |
|--------|--------|-------|
| **Experience** | Strong | Apache-licensed, 20-year open-source history; release notes show active development |
| **Expertise** | Strong | Core team members named in blog posts; CVE disclosures handled professionally |
| **Authoritativeness** | Strong | DSF is an established non-profit; Django used by Instagram, Pinterest, Disqus, Mozilla |
| **Trustworthiness** | Partial | HTTPS/HSTS good; no privacy policy or terms at standard URLs (404); no visible contact page |

---

## Site-Type Checklist (Open-Source Framework / SaaS-Adjacent)

- [x] CDN in use (Varnish/Fastly confirmed via x-served-by headers)
- [x] Static assets have long-term cache headers (max-age=315360000 / 10 years, hash-based filenames)
- [x] Responsive design with viewport meta tag
- [ ] Product/feature pages have sufficient content depth — /start/ is thin
- [ ] Comparison / alternative pages exist for high-intent queries — **missing**
- [ ] Glossary or educational long-form content present for topical authority — **missing on www** (exists in docs subdomain)
- [ ] Blog content links to relevant product pages — **not observed**
- [ ] Author bio pages with credentials — **missing**

---

## Prioritized Action Plan

### 1. Critical Fixes (blocking or directly suppressing ranking)

**1.1 Add canonical tags to base template** — 30 min effort
```html
<link rel="canonical" href="{{ request.build_absolute_uri(request.path) }}" />
```
Self-referencing canonicals prevent any URL variant from fragmenting index signals.

**1.2 Fix HTTP → HTTPS redirect in nginx** — 1 hr effort
```nginx
server {
    listen 80;
    server_name www.djangoproject.com djangoproject.com;
    return 301 https://$host$request_uri;
}
```

**1.3 Write meta descriptions for all primary pages** — 2–4 hr effort
Start with: homepage, /start/, /start/overview/, /download/, /community/, /weblog/. Template fix for blog posts to pull content excerpt rather than author byline.

**1.4 Add sitemap reference to robots.txt** — 5 min effort
```
Sitemap: https://www.djangoproject.com/sitemap.xml
```

### 2. High-Impact Improvements

**2.1 Add JSON-LD structured data** — 4–6 hr effort across templates
- Homepage: `WebSite` (enables Sitelinks Search Box) + `SoftwareApplication`
- Blog posts: `BlogPosting` with `author`, `datePublished`, `headline`, `description`
- Interior pages: `BreadcrumbList`

Validate at: https://search.google.com/test/rich-results

**2.2 Fix heading order** — 30 min effort
Change the sitewide announcement banner element from `<h2>` to `<p class="announcement">` or `<aside>`. Ensure H1 is the first heading in DOM order on every page.

**2.3 Align title tags and H1s** — 2–3 hr effort
Update title tags to lead with primary keyword phrase; update H1s to match or complement. Priority pages: homepage, /start/overview/, /download/.

**2.4 Expand /start/ page content** — 4 hr effort
Target 500–700 words with step-by-step getting started path and a code snippet. This page directly targets 'how to get started with Django' — one of the highest-value queries for framework adoption.

**2.5 Add privacy policy and contact page** — 2 hr effort
Create /privacy/ with Django Software Foundation privacy information and link from footer. Add /contact/ with the foundation's contact details. These are required E-E-A-T trust signals.

### 3. Quick Wins (easy, immediate benefit)

- **Remove keywords meta tag** from base template (15 min) — dead markup
- **Fix dashboard subdomain in sitemap** — remove dashboard.djangoproject.com/\* entries (30 min)
- **Submit sitemap in Google Search Console** (5 min) — immediate crawl coverage improvement
- **Run PageSpeed Insights** on homepage and share results with team (15 min) — identifies CWV priorities that can't be audited statically

### 4. Long-term Recommendations

**4.1 Topical authority on www vs. docs subdomain**
Currently, all technical long-form content lives on `docs.djangoproject.com`. From Google's perspective, this is a separate entity. If www.djangoproject.com wants to rank for informational queries ('Django ORM', 'Django REST framework', 'Django authentication'), it needs either: (a) topical cluster content on www, or (b) strong cross-linking from docs to www for authority consolidation.

**4.2 Create comparison and alternatives content**
Pages targeting 'Django vs FastAPI', 'Django vs Flask', 'Python web framework comparison' are high-intent developer queries. djangoproject.com is the most authoritative possible source but currently cedes these SERPs entirely to third-party comparison sites.

**4.3 Built with Django / Success stories section**
4–8 short narrative case studies (300–600 words each) covering how Instagram, Mozilla, Disqus, etc. use Django. These support E-E-A-T, provide long-tail SEO surface area, and give developers social proof during framework evaluation.

**4.4 Author bio pages for weblog contributors**
Create author profile pages linked from blog posts. This supports E-E-A-T's Expertise signal and allows Google to associate content with known entities in the Python/Django space.

---

## External Tools Required (Not Evaluated in This Audit)

| Check | Tool Needed |
|-------|-------------|
| Core Web Vitals (LCP, INP, CLS) | Google PageSpeed Insights |
| Schema/structured data (JS-rendered) | Google Rich Results Test |
| Index coverage and crawl errors | Google Search Console |
| Backlink profile and domain authority | Ahrefs or Semrush |
| Competitor keyword gaps | Ahrefs, Semrush, or Similarweb |
| Current search rankings | Google Search Console or rank tracker |

---

## Related Skills

- **ai-seo** — For optimizing content for AI search engines (AEO, GEO, LLMO)
- **programmatic-seo** — For building SEO pages at scale (e.g., per-version docs landing pages)
- **site-architecture** — For page hierarchy, navigation design, and URL structure
- **schema-markup** — For implementing structured data across templates
- **page-cro** — For optimizing pages for conversion (framework adoption / donation)
- **analytics-tracking** — For measuring SEO performance via Search Console + GA4
