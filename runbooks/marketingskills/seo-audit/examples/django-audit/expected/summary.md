# SEO Audit Executive Summary — djangoproject.com

**Date:** 2026-06-07
**Overall Health:** Needs Attention
**Site Type:** Open-source developer framework / Community site

---

## Top 5 Priority Issues

### 1. Empty Meta Descriptions Sitewide (Critical)
Every primary page on djangoproject.com has `<meta name="description" content="">` — an empty string. Google auto-generates SERP snippets from body text, which are typically less compelling and less keyword-relevant than crafted descriptions. Blog posts exist as an exception but use "Posted by [Author] on [Date]" as their description, which is equally useless as a click driver.

**Impact:** Directly reduces click-through rate from search results across all pages.
**Fix:** Write unique 150–160 character meta descriptions for each page. Start with homepage, /start/, /start/overview/, and /download/.

---

### 2. No Canonical Tags on Any Page (High)
No `<link rel="canonical">` tag was found on any crawled page. The `og:url` tag provides a partial signal but `rel=canonical` is the authoritative deduplication directive for Google. Without it, any URL variant (trailing slash, query string, www vs non-www) can create duplicate indexation.

**Impact:** Risk of duplicate content diluting PageRank across URL variants.
**Fix:** Add self-referencing canonical tags to every page template.

---

### 3. HTTP Serving Content Without Redirecting to HTTPS (High)
`http://www.djangoproject.com/` returns HTTP 200 with full content rather than a 301 redirect to HTTPS. The HSTS header is present but is ignored by browsers on HTTP connections per RFC 6797. Googlebot may crawl both HTTP and HTTPS versions, splitting signals.

**Impact:** Potential duplicate indexation, split PageRank, and security signal weakening.
**Fix:** Add nginx redirect rule: `return 301 https://$host$request_uri;`

---

### 4. No Structured Data / Schema Markup (Medium-High)
No JSON-LD or microdata schema was detected in static HTML on any page. For a software project website, missing schema means no potential for rich results (SoftwareApplication cards, BlogPosting breadcrumbs, Sitelinks Search Box, FAQPage). Note: JavaScript-rendered schema cannot be confirmed via static fetch alone; verify via the Google Rich Results Test.

**Impact:** Missing eligible rich results in SERPs; no Sitelinks Search Box potential.
**Fix:** Add WebSite + SoftwareApplication schema to homepage; BlogPosting schema to weblog posts; BreadcrumbList to interior pages.

---

### 5. Sitemap Not Referenced in robots.txt (Medium)
The sitemap at `/sitemap.xml` (975 URLs, well-structured) exists and is accessible but is not referenced in `robots.txt`. Search engines discover it only through direct guessing or if it has been submitted manually to Search Console.

**Impact:** Slower sitemap discovery; potential for incomplete crawl coverage.
**Fix:** Add `Sitemap: https://www.djangoproject.com/sitemap.xml` to robots.txt.

---

## Quick Wins (Low effort, high impact)

| Win | Effort | Impact |
|-----|--------|--------|
| Add `Sitemap:` line to robots.txt | 5 minutes | Medium |
| Add self-referencing canonical tags to base template | 30 minutes | High |
| Fix HTTP→HTTPS redirect in nginx config | 1 hour | High |
| Remove empty `meta name="keywords"` tag from base template | 15 minutes | Low |
| Change announcement banner from `<h2>` to `<p>` or `<aside>` | 30 minutes | Medium |
| Write meta descriptions for 5 key pages | 2 hours | High |

---

## What's Working Well

- HTTPS and HSTS with preload are properly configured (once redirect is fixed)
- Non-www → www 301 redirect is in place
- Trailing slash consistency enforced via 301
- CDN (Varnish/Fastly) with excellent static asset caching (10-year headers, hash-based filenames)
- robots.txt is clean and does not block critical content
- Sitemap is comprehensive (975 URLs), current, and accessible
- Open Graph and Twitter Card tags are populated
- Mobile viewport meta tag is present
- Site architecture is logical with clear navigation hierarchy

---

## Requires External Tool (Not Evaluated)

- **Core Web Vitals / PageSpeed** — LCP, INP, CLS scores require PageSpeed Insights
- **Schema validation** — Whether schema exists via JavaScript requires Google Rich Results Test
- **Search Console Coverage** — Index status, crawl errors, manual actions
- **Backlink profile** — Domain authority, link quality (requires Ahrefs/Semrush)
- **Keyword rankings** — Current SERP positions (requires rank tracking tool)
