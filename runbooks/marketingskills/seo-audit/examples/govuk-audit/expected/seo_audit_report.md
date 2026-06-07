# SEO Audit Report — https://www.gov.uk

**Date:** 2026-06-07  
**Scope:** Full (Technical + On-Page + Content)  
**Site Type:** Government information portal — multilingual (English + Welsh)  
**Auditor:** Automated static audit via curl/HTTP + header analysis

---

## Executive Summary

**Overall health: Good**

GOV.UK is the official digital presence of the UK Government, operated by the Government Digital Service (GDS). The site is built on a mature, well-maintained publishing platform with an excellent technical foundation: global CDN delivery (Fastly), sub-35ms server response times, enforced HTTPS with HSTS preloading, HTTP/2, clean URL architecture, and a properly structured sitemap index covering 35 sub-sitemaps updated daily.

SEO fundamentals are largely sound. The gaps found in this audit are targeted and addressable:

1. **No hreflang implementation** for English ↔ Welsh content (bilingual gap)
2. **Schema markup unconfirmed** — requires browser/external tool to verify (cannot detect JavaScript-rendered JSON-LD)
3. **Homepage meta description too short** (62 chars; recommend 150–160)
4. **Core Web Vitals field data unavailable** — requires PageSpeed Insights
5. **Feature images on homepage lack meaningful alt text**

---

## Technical SEO Findings

| Issue | Impact | Evidence | Fix | Priority |
|-------|--------|----------|-----|----------|
| Core Web Vitals not evaluable (PageSpeed Insights required) | High | TTFB 25–34ms (CDN-cached, excellent). LCP/INP/CLS require field data. | Run PageSpeed Insights on homepage, /browse/benefits, /universal-credit. Targets: LCP <2.5s, INP <200ms, CLS <0.1 | 1 |
| No hreflang tags on English or Welsh pages | Medium | Zero hreflang attributes found on /, /universal-credit, /cymraeg. Welsh content exists but no language annotation signals the English↔Welsh relationship to Google. | Add hreflang="en-GB" and hreflang="cy" pairs with x-default to all bilingual page templates. Enforce full reciprocity. | 2 |
| Schema markup unverifiable via static fetch | Medium | No `<script type="application/ld+json">` in static HTML. May be JS-injected (cannot confirm). | Verify at https://search.google.com/test/rich-results. Implement WebSite + SearchAction (sitelinks searchbox) and BreadcrumbList on guide pages if absent. | 2 |
| Homepage meta description too short | Low | "GOV.UK - The best place to find government services and information." = 62 chars. Recommended: 150–160 chars. | Expand to ~150 chars covering government services breadth. One CMS edit. | 3 |
| Homepage feature images have empty alt text | Low | Four images (Find a Job, NI, Cost of Living, GOV.UK App) carry alt="". | Audit each in context; add descriptive alt where image conveys meaning beyond adjacent link text. | 3 |
| DeepCrawl bot fully blocked | Low | robots.txt: User-agent: deepcrawl / Disallow: /. Limits third-party SEO audit capability for GDS teams. | Consider replacing with Crawl-delay directive if load was the concern. | 5 |
| HSTS max-age inconsistency between www and non-www | Low | www: max-age=31536000 (1yr). non-www: max-age=63072000 (2yr). | Standardise to max-age=31536000; includeSubDomains; preload across both. | 4 |
| Sitemap sub-files use non-root path | Low | /sitemaps/sitemap_N.xml (correctly referenced from index). No action needed but monitor for stale URLs. | Periodically validate sub-sitemap URLs return 200 and are indexable. | 5 |
| Search results pages blocked (/search/all*) | None (correct) | robots.txt: Disallow: /search/all*. Correct practice — prevents search result page crawl. | No action needed. | 5 |
| Print URL variants blocked | None (correct) | Disallow: /*/print$. Correct — prevents near-duplicate print pages from polluting index. | No action needed. | 5 |

### Detailed Technical Analysis

#### Crawlability — PASS

- **robots.txt** is well-structured. Sitemap referenced correctly (`Sitemap: https://www.gov.uk/sitemap.xml`). Only intentional blocks in place.
- **Sitemap index** at `/sitemap.xml` correctly references 35 sub-sitemaps at `/sitemaps/sitemap_N.xml`. All sub-sitemaps have `lastmod` timestamps current to 2026-06-07. Sub-sitemaps contain canonical content URLs with priority values.
- No unintentional blocking of important content directories in robots.txt.

#### HTTPS & Security — PASS

- Site served over HTTP/2 via Fastly CDN.
- HTTP → HTTPS redirect: 301 (Varnish/Fastly-enforced). ✓
- Non-www → www redirect: 301 via /cymraeg chain ends at www.gov.uk. ✓
- HSTS present with `preload` flag: `strict-transport-security: max-age=31536000; preload`. ✓
- Strong security headers observed:
  - `Content-Security-Policy`: comprehensive policy with nonce-based script execution
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: interest-cohort=()` (disables FLoC)
  - `X-Frame-Options: SAMEORIGIN`

#### Canonicals — PASS

- Homepage: `<link rel="canonical" href="https://www.gov.uk/">` — self-referencing, correct.
- /universal-credit: `<link rel="canonical" href="https://www.gov.uk/universal-credit">` — self-referencing, correct.
- Both HTTP→HTTPS and non-www→www are enforced at the CDN level, preventing canonical inconsistency.

#### Site Speed — PASS (static evidence only)

- TTFB: 25–34ms (CDN-cached responses) — far below 600ms threshold.
- HTTP/2 multiplexing confirmed.
- Link preload headers for CSS and critical JS assets sent in response headers.
- `loading="lazy"` on images confirmed.
- CDN: Fastly (`x-served-by`, `x-cache: HIT`, `via: 1.1 varnish` headers).
- `cache-control: max-age=300, public` (5-minute public cache).
- ⚠️ Core Web Vitals (LCP, INP, CLS) **require PageSpeed Insights — not evaluated**.

#### Mobile — PASS

- `<meta name="viewport" content="width=device-width, initial-scale=1">` present.
- No separate mobile subdomain.
- GOV.UK Design System is responsive by design.
- Images use `loading="lazy"`.

#### International SEO (Hreflang) — FAIL

- Site has Welsh-language content (`/cymraeg` and associated Welsh guide pages).
- Zero hreflang annotations found on homepage, inner English pages, or `/cymraeg`.
- Without hreflang: Google cannot reliably identify language pairs; Welsh pages may be deprioritised or mistargeted in SERPs for Welsh-language queries.

#### URL Structure — PASS

- All URLs lowercase, hyphen-separated, descriptive.
- No extraneous parameters in permanent content URLs.
- Logical hierarchy: `/browse/[category]`, `/government/[section]`, `/[guide-slug]`.

---

## On-Page SEO Findings

| Issue | Impact | Evidence | Fix | Priority |
|-------|--------|----------|-----|----------|
| Homepage meta description too short | Medium | 62 chars. Google may auto-generate a worse snippet. | Expand to ~150 chars covering key service areas. | 3 |
| Homepage title tag could be more keyword-rich | Low | `<title lang="en">Welcome to GOV.UK</title>` = 20 chars. Not harmful for branded queries but uses no keywords. | Consider 'GOV.UK — Official UK Government Website' (~44 chars). Remove non-standard lang="" attribute from `<title>`. | 4 |
| Homepage H1 generic (no brand keyword) | Low | H1: "The best place to find government services and information". Accurate but not keyword-targeted. | Low priority given brand dominance. Optional: "Find UK government services and information". | 5 |
| Multiple H1 tags on guide pages (non-JS render) | Low | /universal-credit returns H1 "Universal Credit" + H1 "What Universal Credit is" in static fetch. Likely a JavaScript tab rendering issue. | Confirm via browser render. If Google sees both simultaneously, change subsection headings to H2. | 3 |
| Inner page meta descriptions — PASS | None | /browse/benefits: "Includes eligibility, appeals, tax credits and Universal Credit" — concise. /universal-credit: 155-char, keyword-rich description — excellent. | No action needed. | 5 |
| Canonical tags — PASS | None | Self-referencing canonicals confirmed on tested pages. | No action needed. | 5 |
| URL structure — PASS | None | Clean, hyphenated, descriptive, no unnecessary parameters. | No action needed. | 5 |
| Internal linking — PASS | None | 16-category navigation, footer links, homepage featured service links. Well-structured. | Run Screaming Frog crawl to identify any deep orphan pages. | 5 |

---

## Content Findings

| Issue | Impact | Evidence | Fix | Priority |
|-------|--------|----------|-----|----------|
| Backlink profile — requires external access | High | Cannot evaluate without Ahrefs/Semrush. GOV.UK is presumed to have an exceptional backlink profile given its status as official UK government domain. | Requires external tool — not evaluated. | 1 |
| Search Console coverage — requires external access | High | No Search Console access. Indexed URL count, crawl errors, and Coverage report status unknown. | Requires external access — not evaluated. GDS team should review Coverage report and Core Web Vitals report. | 1 |
| Welsh-language content not linked from English homepage | Medium | /cymraeg exists but no visible navigation link from English homepage observed in static HTML. | Add Welsh language toggle in site header/footer. Implement hreflang to signal bilingual structure. | 2 |
| E-E-A-T signals — exceptionally strong | None | Official UK Government site operated by GDS. HTTPS. Publisher metadata present (`govuk:primary-publishing-organisation`). Contact, privacy, cookies, and accessibility pages accessible. | No action needed. | 5 |
| Content freshness — PASS | None | Sitemaps updated 2026-06-07. govuk:updated-at present on pages. Content actively maintained. | No action needed. | 5 |
| Homepage content depth — appropriate for portal | None | Shallow by design — a navigational portal, not a content destination. | No action needed. | 5 |
| Guide page content quality — PASS | None | /universal-credit: multi-tab guide with clear headings, eligibility criteria, and actionable steps. Satisfies informational and transactional intent. | No action needed. | 5 |

### E-E-A-T Assessment

| Signal | Status | Notes |
|--------|--------|-------|
| Experience | Strong | First-hand government source with operational data |
| Expertise | Strong | Author is the UK Government; GDS publishing metadata present |
| Authoritativeness | Exceptional | Official government domain; .gov.uk TLD |
| Trustworthiness | Strong | HTTPS, clear purpose, privacy/cookies/accessibility pages, contact page |

---

## Site-Type Specific Checklist (Government Information Portal)

| Check | Status |
|-------|--------|
| Service pages have sufficient content depth | Pass — guides are multi-section with clear structured content |
| Navigation covers primary service categories | Pass — 16 top-level categories in header and footer |
| Search functionality present | Pass — sitewide search at /search |
| Accessibility compliance signals | Pass — skip links, ARIA labels, cookie consent |
| Privacy policy and cookies page | Pass — /help/cookies, /help/privacy-notice |
| Contact information accessible | Pass — /contact/govuk |
| HTTPS enforced | Pass |
| Hreflang for multilingual content | Fail — Welsh content not annotated |
| Schema markup | Unverifiable — requires external tool |
| Core Web Vitals | Unverifiable — requires PageSpeed Insights |

---

## Prioritized Action Plan

### 1. Critical / Blocking (Do First)

**None found** — the site has no crawlability or indexation-blocking issues detectable in a static audit.

### 2. High-Impact Improvements

**A. Verify and implement schema markup**
- Use Rich Results Test (https://search.google.com/test/rich-results) on homepage, a guide page (/universal-credit), and a publication page.
- If absent: Implement `WebSite` with `SearchAction` (sitelinks searchbox eligibility), `BreadcrumbList` on all guide/browse pages, `GovernmentOrganization` on department pages.
- **Est. effort:** 2–5 days (template change across publishing platform)
- **Impact:** Rich results eligibility, improved SERP presentation

**B. Implement hreflang for English ↔ Welsh content**
- Add `hreflang="en-GB"` and `hreflang="cy"` pair annotations to all pages that have a Welsh-language equivalent.
- Every annotated page must include a self-referencing hreflang entry.
- Add `hreflang="x-default"` pointing to the English fallback on the root.
- Ensure HTML annotations and sitemap annotations agree.
- **Est. effort:** 3–5 days (template change + QA)
- **Impact:** Correct language targeting for Welsh-speaking users in Google Search

**C. Run PageSpeed Insights field-data audit**
- Test: homepage, /browse/benefits (category/browse page), /universal-credit (guide page).
- Focus on: INP (cookie banner interaction cost), LCP (largest rendered element per page type), CLS (any layout shift from deferred CSS or cookie banner).
- **Est. effort:** 2 hours to run + triage
- **Impact:** Identifies any Core Web Vitals regressions before they affect rankings

**D. Review Search Console Coverage report**
- Compare submitted sitemap URL count vs. indexed URL count.
- Investigate any "Excluded" pages, especially those marked "Crawled — currently not indexed."
- **Est. effort:** 2 hours
- **Impact:** Identifies indexation leakage

### 3. Quick Wins (Low Effort, Fast Benefit)

**E. Expand homepage meta description**
- From: "GOV.UK - The best place to find government services and information." (62 chars)
- To: ~150 chars covering primary service areas (benefits, tax, passports, driving, employment, business).
- **Est. effort:** 30 minutes (one CMS content edit)
- **Impact:** Improved SERP snippet click-through rate for branded and navigational queries

**F. Add descriptive alt text to homepage feature images**
- Four images (Find a Job, National Insurance, Cost of Living, GOV.UK App) have `alt=""`.
- Audit in context — if images convey meaning beyond adjacent link text, add concise descriptive alt text.
- **Est. effort:** 1 hour
- **Impact:** Improved accessibility compliance and image-search discoverability

**G. Remove non-standard lang attribute from `<title>` element**
- `<title lang="en">` is not a standard HTML attribute for the title element. Remove `lang="en"`.
- **Est. effort:** 15 minutes (template fix)
- **Impact:** Clean, standards-compliant markup

### 4. Long-Term Recommendations

**H. Validate sub-sitemap URL health regularly**
- GOV.UK has 35 sub-sitemaps and a very large URL inventory. Over time, sitemaps may include redirected, soft-404, or noindex URLs.
- Automate monthly comparison of sitemap URLs against their HTTP status codes using Screaming Frog or a custom script.
- Purge stale URLs from sub-sitemaps promptly.

**I. Monitor Core Web Vitals field data in Search Console**
- Field data (real user measurements via CrUX) is more impactful to ranking than lab data.
- Set up monthly CWV monitoring across page types (homepage, guide, publication, browse).
- Prioritise INP — the cookie consent banner interaction is a likely CWV cost on first page load.

**J. Assess backlink profile for toxic links and gap opportunities**
- Use Ahrefs or Semrush to audit the referring domain profile.
- Identify any low-quality or potentially spammy links pointing to GOV.UK pages.
- Identify keyword-topic areas where the site is not ranking as strongly as expected relative to its authority level.
- **Est. effort:** 4–8 hours for initial analysis

**K. Audit thin locale pages (Welsh content)**
- If Welsh guide pages are machine-translated or minimal adaptations of English source, Google's helpful content system may evaluate them as thin.
- Ensure Welsh pages are fully translated and purpose-built — not just UI chrome translated around English body content.

---

## Related Skills

- **ai-seo**: Optimising GOV.UK content for AI-powered search engines (AEO, GEO) and LLM-indexed results
- **programmatic-seo**: Building SEO-optimised pages at scale across publication and statistics formats
- **site-architecture**: Reviewing page hierarchy, navigation design, and URL structure at the /government/ section level
- **schema-markup**: Implementing structured data (WebSite, BreadcrumbList, GovernmentOrganization, FAQPage) across the publishing platform
- **analytics-tracking**: Setting up and interpreting SEO performance measurement in GA4 and Search Console

---

## Audit Limitations

The following checks could not be completed without external tooling access:

| Check | Tool Required | Status |
|-------|--------------|--------|
| Core Web Vitals (LCP, INP, CLS) | PageSpeed Insights / CrUX | Requires external tool — not evaluated |
| Schema markup validation | Rich Results Test / browser JS rendering | Requires external tool — not evaluated |
| Indexed URL count vs. submitted URL count | Google Search Console | Requires external access — not evaluated |
| Coverage report (crawl errors, excluded pages) | Google Search Console | Requires external access — not evaluated |
| Backlink profile and domain authority | Ahrefs / Semrush | Requires external access — not evaluated |
| Competitor gap analysis | Ahrefs / Semrush | No competitors provided — not evaluated |
| Full site crawl for orphan pages / broken links | Screaming Frog / custom crawler | Requires full crawl — not evaluated |
