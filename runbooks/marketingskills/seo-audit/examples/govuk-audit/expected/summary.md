# SEO Audit Executive Summary — www.gov.uk

**Date:** 2026-06-07  
**Site Type:** Government information portal (multilingual: English + Welsh)  
**Overall Health:** Good — with targeted improvements available

---

## Overall Assessment

GOV.UK is an exceptionally well-engineered government portal with strong technical foundations: a global CDN (Fastly), sub-35ms TTFB, HSTS preloading, HTTP/2, clean URL architecture, a properly structured sitemap index (35 sub-sitemaps), correct HTTP→HTTPS and non-www→www redirects, and best-in-class E-E-A-T signals. The site ranks primarily on authority and navigational brand queries and is unlikely to have significant crawlability or indexation problems.

The actionable opportunities are concentrated in **hreflang implementation for Welsh-language content**, **schema markup verification**, **homepage meta description expansion**, and **Core Web Vitals field-data review** (which requires PageSpeed Insights access).

---

## Top Priority Issues

### Priority 1 — Requires External Tools (Cannot Pass/Fail Without Them)

1. **Core Web Vitals (PageSpeed Insights required)**  
   TTFB is excellent (25–34ms from CDN), but LCP, INP, and CLS cannot be measured statically. Given the cookie banner, JavaScript analytics loading, and asset preloading on every page, INP and CLS deserve scrutiny.  
   _Action: Run https://pagespeed.web.dev/ on homepage, /browse/benefits, and /universal-credit._

2. **Schema markup presence (Rich Results Test required)**  
   No `<script type="application/ld+json">` found in static HTML. GOV.UK may inject schema via JavaScript (Yoast-style). Without validation, it is unknown whether WebSite, BreadcrumbList, or GovernmentOrganization schema is implemented.  
   _Action: Test at https://search.google.com/test/rich-results. If absent, implement at minimum WebSite + SearchAction (sitelinks searchbox) and BreadcrumbList on guide pages._

### Priority 2 — Medium Impact, Actionable Now

3. **Missing hreflang for English ↔ Welsh content**  
   GOV.UK serves Welsh-language content (e.g. /cymraeg) but zero hreflang tags are implemented on any tested page. Google cannot reliably identify and serve the correct language version to Welsh-speaking users.  
   _Action: Add hreflang="en-GB" and hreflang="cy" pairs with x-default on all bilingual pages. Ensure full reciprocity (every English page pointing to its Welsh equivalent and vice versa)._

### Priority 3 — Quick Wins

4. **Homepage meta description too short (62 chars)**  
   The current description is well below the 150–160 character recommendation. This increases the likelihood of Google auto-generating a less favourable snippet for branded and navigational queries.  
   _Action: Expand to ~150 chars covering government services breadth. (One CMS config change.)_

5. **Homepage feature images missing meaningful alt text**  
   Four content images (Find a Job, National Insurance, Cost of Living, GOV.UK App) carry `alt=""`. If these images provide contextual meaning beyond adjacent link text, alt text should be added for both accessibility compliance and potential image-search signals.  
   _Action: Audit each image in context. Add short descriptive alt text if it conveys meaning not present in surrounding text._

---

## Quick Wins (Low Effort, Immediate Benefit)

| Win | Effort | Benefit |
|-----|--------|---------|
| Expand homepage meta description | 1 CMS edit | Improved SERP snippets |
| Add Welsh hreflang annotations | Template change | Correct language targeting for Welsh users |
| Run Rich Results Test on key page types | 30 minutes | Confirm schema status |
| Run PageSpeed Insights on 3 page types | 30 minutes | Identify any CWV regressions |

---

## What Is Working Well

- Sub-35ms TTFB from Fastly CDN — exceptional
- HSTS with preload enabled on both www and non-www
- 35 sub-sitemaps, updated daily, correctly referenced
- robots.txt: only relevant paths blocked (print, search results)
- Canonical tags correct on all tested pages
- HTTP→HTTPS and non-www→www 301 redirects in place
- Strong E-E-A-T signals (official government authority, GDS publishing metadata)
- Clean, hyphenated, descriptive URL structure
- Well-organised internal linking through browse and footer navigation
- Inner page meta descriptions are high quality (e.g. /universal-credit at 155 chars)
- Accessibility patterns (skip links, ARIA labels, responsive viewport) align with CWV best practices
