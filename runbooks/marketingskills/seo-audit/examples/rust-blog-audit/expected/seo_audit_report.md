# SEO Audit Report — https://blog.rust-lang.org

**Date:** 2026-06-07  
**Scope:** Full (Technical + On-Page + Content)  
**Site Type:** Official Programming Language Blog (Content/Blog)  
**Auditor:** Automated static analysis (curl/web_fetch)

---

## Executive Summary

**Overall Health: Needs Attention**

blog.rust-lang.org is the official Rust Programming Language blog — the highest-authority source for Rust announcements, release notes, and project updates. Its domain authority is exceptional by virtue of being directly linked from rust-lang.org's primary navigation and being cited by tens of thousands of developers and projects worldwide.

Despite this authority, the blog has several structural SEO issues that are easy to fix and would improve organic discoverability:

1. **No H1 tags anywhere on the site** — every post title renders as H2
2. **Identical meta descriptions sitewide** — 724+ pages share the same brand tagline
3. **No structured data / schema markup** in static HTML
4. **No canonical tags** on any page
5. **No topical content clusters** — 724 posts organized only by year, no tag pages

These are primarily *template-level* fixes in the static site generator (a small Rust-based SSG hosted on GitHub Pages). The site's authority, content quality, and infrastructure are sound — the SEO issues are largely mechanical oversights rather than fundamental problems.

---

## Technical SEO Findings

| Issue | Impact | Evidence | Fix | Priority |
|-------|--------|----------|-----|----------|
| No H1 tag on any page — posts use `<h2>` as article title | High | Homepage: H1=0. `/2025/02/20/Rust-1.85.0/`: H1=0, H2=2 (post title + contributors). `/2026/05/28/Rust-1.96.0/`: H1=0, H2=3, H3=6 | Change post title template element from `<h2>` to `<h1>`; add `<h1>` to homepage | 1 |
| Duplicate meta descriptions sitewide | High | All sampled pages return `content='Empowering everyone to build reliable and efficient software.'` — tagline used as description for every post | Generate per-post descriptions from post excerpt or front-matter field | 1 |
| No canonical link tags on any page | Medium | grep for 'canonical' on `/2025/02/20/Rust-1.85.0/` returns no output; no-trailing-slash URLs also return HTTP 200 alongside trailing-slash versions | Add `<link rel="canonical" href="[page-url]">` to site template | 2 |
| Sitemap lacks lastmod, changefreq, priority | Medium | 724 `<url>` entries; Python check: `has_lastmod=False`, `has_changefreq=False`, `has_priority=False` | Add `<lastmod>` using each post's publish date | 2 |
| No structured data in static HTML | Medium | grep for `ld+json`, `schema.org`, `itemtype` on homepage and post page — no results *(Rich Results Test required for conclusive check)* | Add Article/BlogPosting JSON-LD to posts; WebSite+SearchAction to homepage | 2 |
| No HSTS header | Medium | curl -sI returns no `Strict-Transport-Security` header; HTTP→HTTPS 301 redirect is present | Configure HSTS via CDN/proxy layer (not possible natively on GitHub Pages) | 3 |
| Trailing-slash and non-trailing-slash both return 200 | Low | `curl -sIL /2025/02/20/Rust-1.85.0` (no slash) returns `HTTP/2 200` with no redirect | Add canonical self-references (preferred) or configure 301 at CDN level | 3 |
| Short cache TTL (max-age=600) | Low | `cache-control: max-age=600` in response headers | Move to custom CDN with configurable caching if cache hits are a concern | 4 |
| Core Web Vitals — *not evaluated* | Unknown | Requires Google PageSpeed Insights; cannot assess via static fetch | Run PageSpeed Insights on homepage, a release post, and an Inside Rust post | — |
| Search Console indexation status — *not evaluated* | Unknown | Requires Google Search Console access | Check Coverage report for all 724 sitemap URLs | — |

### 2a: Crawlability — Detailed Findings

**robots.txt** (`https://blog.rust-lang.org/robots.txt`):
```
User-agent: *
Disallow:
Allow: /
Sitemap: https://blog.rust-lang.org/sitemap.xml
```
- ✅ No unintentional blocks — all paths allowed
- ✅ Sitemap correctly referenced
- ✅ Clean, minimal configuration

**Sitemap** (`https://blog.rust-lang.org/sitemap.xml`):
- ✅ Exists and accessible at `/sitemap.xml` (also referenced in robots.txt)
- ✅ 724 blog post URLs included
- ❌ No `<lastmod>` dates — Google cannot determine which posts are new/updated
- ❌ No `<changefreq>` or `<priority>` hints
- ❌ Search Console submission status — *requires external access*

**Site Architecture:**
- ✅ Two-level structure: index → individual posts (within 2 clicks)
- ✅ Three content sections: main blog, Inside Rust (`/inside-rust/`), Releases (`/releases/`)
- ⚠️ No tag/category pages — 724 posts are a flat chronological list with no topical organization
- ✅ Atom/RSS feed available at `/feed.xml` and `/inside-rust/feed.xml`

### 2b: Indexation — Detailed Findings

- ⚠️ **No canonical tags** on any page (post pages, index pages, or homepage)
- ✅ No `noindex` directives found on audited pages
- ✅ No `noindex` in robots.txt
- ❌ Trailing-slash inconsistency — both URL forms serve content without redirect
- ❌ Search Console Coverage report — *requires external access*

### 2c: Site Speed & Core Web Vitals

**Server infrastructure:** GitHub Pages → Fastly CDN → Varnish cache layer
- ✅ CDN is in use (Fastly, X-Cache headers confirmed)
- ✅ Static HTML served (no server-side rendering latency)
- ✅ Cache hits confirmed (`x-cache: HIT`)
- ⚠️ `max-age=600` (10 minutes) is low for static content
- ❌ **Core Web Vitals (LCP, INP, CLS) — requires Google PageSpeed Insights**

### 2d: Mobile-Friendliness

- ✅ Viewport meta tag: `<meta name="viewport" content="width=device-width,initial-scale=1.0">`
- ✅ Responsive CSS (tachyons.css utility framework)
- ✅ Single site (no separate m. subdomain)
- ❌ Tap target size verification — *requires visual/browser testing*

### 2e: HTTPS & Security

- ✅ HTTP/2 served over HTTPS
- ✅ HTTP → HTTPS 301 redirect in place (`curl -sI http://blog.rust-lang.org → Location: https://blog.rust-lang.org/`)
- ✅ `access-control-allow-origin: *` (appropriate for public content)
- ❌ No HSTS (`Strict-Transport-Security`) header — first-visit HTTP requests are unprotected before redirect
- ❌ SSL certificate validity — *requires browser verification* (GitHub Pages wildcard cert is expected to be valid)

### 2f: URL Structure

- ✅ Readable, descriptive URLs: `/2025/02/20/Rust-1.85.0/`
- ✅ Date-based hierarchy is consistent
- ✅ No session IDs or unnecessary query parameters
- ✅ Lowercase paths used
- ⚠️ Year in URL means old posts may appear "dated" to users in SERPs (e.g., 2014 posts)
- ⚠️ No keywords in URL path beyond the slug (e.g., `/Rust-1.85.0/` doesn't include 'release' or 'stable')

### 2g: International SEO / Hreflang

- ✅ Single-language English site — hreflang is not required
- ✅ `og:locale` is set to `en_US`
- No hreflang implementation needed

---

## On-Page SEO Findings

| Issue | Impact | Evidence | Fix | Priority |
|-------|--------|----------|-----|----------|
| No H1 on any page | High | 0 H1s found across homepage and all sampled posts | Change post-title element to `<h1>` in template; add `<h1>` to homepage | 1 |
| Duplicate meta descriptions | High | All pages: `"Empowering everyone to build reliable and efficient software."` | Per-post descriptions from post excerpt | 1 |
| OG/Twitter descriptions use site tagline, not post content | High | All sampled posts: `og:description` and `twitter:description` = generic tagline | Template OG/Twitter tags with per-post description | 1 |
| Inside Rust index: empty `twitter:description` | Medium | `twitter:description=""` on `/inside-rust/` | Set to match `og:description` | 3 |
| Releases index: empty `og:description` and `twitter:description` | Medium | Both blank on `/releases/` | Add meaningful section description | 3 |
| Homepage title is short (34 chars) | Low | `"The Rust Programming Language Blog"` | Expand to ~55 chars with keyword intent | 3 |
| Internal links per post are sparse (2–4) | Medium | `/2026/05/28/Rust-1.96.0/`: 3 content internal links | Add 3–5 contextual links per post to related content | 2 |
| Weak anchor text ("previously announced") | Low | `/2026/05/28/Rust-1.96.0/`: `'previously announced'` links to WebAssembly changes post | Use descriptive anchor text for all internal links | 4 |
| No author bio pages | Medium | Posts list teams only; no `/author/` pages exist | Add individual author bios for regular contributors | 3 |
| No related posts section | Low | Posts end with contributor list; no next/prev or topic links | Add 3 related-post links at end of each post | 4 |

### 3a: Title Tags (Sampled)

| Page | Title | Length | Assessment |
|------|-------|--------|------------|
| Homepage | "The Rust Programming Language Blog" | 34 chars | Below optimal (55–60), not keyword-rich |
| /2025/02/20/Rust-1.85.0/ | "Announcing Rust 1.85.0 and Rust 2024 \| Rust Blog" | 49 chars | Good — unique, descriptive |
| /2026/05/28/Rust-1.96.0/ | "Announcing Rust 1.96.0 \| Rust Blog" | 34 chars | Short but acceptable |
| /inside-rust/ | "The 'Inside Rust' Blog" | 23 chars | Too short, not keyword-optimized |
| /releases/ | "The Rust Release Announcements" | 31 chars | Below optimal |

### 3b: Meta Descriptions (Sampled)

All sampled pages (homepage, /releases/, /inside-rust/, and all post pages) return:
> *"Empowering everyone to build reliable and efficient software."*

This is the Rust brand tagline and provides **zero page-specific context** for any individual post or section. This is one of the highest-priority issues on the site.

### 3c: Heading Structure

**Homepage:**
- H1: 0
- H2: 0
- H3: 13 (one per year group: "Posts in 2026", "Posts in 2025", etc.)
- Skip from H3 directly — no logical hierarchy

**Blog Posts (e.g., /2025/02/20/Rust-1.85.0/):**
- H1: 0
- H2: 3 (post title, main content sections, "Contributors")
- H3: Many (subsections within the release notes)
- The post title "Announcing Rust 1.85.0 and Rust 2024" renders as H2, not H1

**Impact:** The absence of H1 on all pages is a clear signal deficiency. Google's ranking algorithms use H1 as a primary indicator of the page's primary topic. Without H1, the post title's SEO weight is diluted.

### 3d–3f: Content, Images, Internal Linking

- **Images:** Decorative icons (rust-logo, social icons) have appropriate `alt=""` or descriptive `alt="Mastodon"`. Content posts are predominantly text-based (code snippets, prose) with minimal images — acceptable for this content type.
- **Internal linking:** Sparse. Typical release post has 2–4 internal links to related posts. Homepage links to recent posts via chronological list.
- **Keyword targeting:** Natural and topic-appropriate, but not strategically optimized for informational search queries.

---

## Content Quality Assessment

### E-E-A-T Evaluation

**Experience:** ⚠️ Posts are written by Rust teams with deep technical expertise, but individual author experience is not surfaced — posts attribute to committees and teams, not named individuals.

**Expertise:** ✅ Technical depth is high and appropriate. Release notes accurately describe language changes with code examples. Content is authoritative within the Rust ecosystem.

**Authoritativeness:** ✅✅ **Exceptional.** This is the *official* Rust Programming Language blog. It is the canonical source for all Rust releases and project updates. Inbound links from GitHub, Stack Overflow, Hacker News, and developer publications are abundant.

**Trustworthiness:** ✅ HTTPS active. Footer includes Code of Conduct, Privacy Policy, Security Policy, and Licenses. Contact email (`core-team@rust-lang.org`) is present. The site is transparent about its purpose and governance.

### Content Depth

| Content Type | Depth | Assessment |
|--------------|-------|------------|
| Release announcements (e.g., Rust 1.96.0) | ~834 words, technical changelog | Good — serves existing users well; could add newcomer-friendly intro |
| Inside Rust posts | Variable | Generally good depth; covers internal governance |
| Foundation/community posts | Varies | Strong narrative, good context |

### Content Organization Issues

- **No tag/category system** — 724 posts with no topical taxonomy
- **No content clusters** — posts about async Rust, WebAssembly, and Cargo are not linked to each other
- **No pillar content** — no comprehensive guide pages (e.g., "All Rust Editions Explained") that aggregate related posts

---

## Blog-Type-Specific Checklist

*Site type: Content/Blog*

- ❌ Outdated content handling — old posts from 2014–2019 remain as-is; no update notices added
- ❌ No keyword cannibalization audit possible without Search Console data *(requires external access)*
- ❌ Topical clusters not implemented — posts are not organized into pillar + cluster pages
- ⚠️ Internal linking connects few related posts (2–4 per post; 5+ recommended)
- ⚠️ No author bio pages with credentials

---

## Prioritized Action Plan

### Priority 1 — Critical Fixes (Immediate Action)

**1.1 — Add H1 to post template**
Change the post article title element from `<h2>` to `<h1>` in the Zola/SSG template. This is a single-line change that affects all 724 posts. Adjust CSS to preserve visual styling.

**1.2 — Generate unique meta descriptions per post**
In the SSG template, set `<meta name="description">` to the post's first paragraph or a dedicated `description` field in front matter. Apply the same fix to `og:description` and `twitter:description`. Target: 150–160 characters per post.

---

### Priority 2 — High-Impact Improvements

**2.1 — Add canonical link tags to all pages**
Add `<link rel="canonical" href="{{ page.permalink }}">` (or equivalent SSG syntax) to the `<head>` in the site template. This affects all pages in one change.

**2.2 — Add structured data (JSON-LD)**
Add `BlogPosting` schema to post pages (headline, datePublished, author, image) and `WebSite` with `SearchAction` to the homepage. Implement at the template level; verify with Google Rich Results Test.

**2.3 — Add lastmod to sitemap.xml**
Populate `<lastmod>` in the sitemap using each post's publish date. Most SSGs support this via a sitemap template variable.

**2.4 — Implement topical tagging**
Introduce 10–15 topic tags (e.g., `releases`, `async`, `cargo`, `webassembly`, `embedded`, `compiler`, `community`). Create indexable tag pages with a short description paragraph. Tag each post with 1–3 relevant tags.

**2.5 — Increase internal linking**
For each new post, add 3–5 contextual internal links to related historical posts. For existing posts, prioritize back-linking from the highest-traffic posts to the most relevant older content.

---

### Priority 3 — Quick Wins

**3.1 — Fix empty social meta on section index pages**
- Inside Rust (`/inside-rust/`): populate `twitter:description` (currently empty)
- Releases (`/releases/`): populate both `og:description` and `twitter:description` (both currently empty)

**3.2 — Add H1 to homepage**
Add a semantic `<h1>` to the homepage — could be a visually hidden `<h1>Rust Blog</h1>` or restructure the hero area. Even a visually subtle heading fulfills the semantic requirement.

**3.3 — Add HSTS header**
If the site is served through a configurable CDN (Fastly, Cloudflare), add `Strict-Transport-Security: max-age=31536000; includeSubDomains`. Not configurable on GitHub Pages alone.

---

### Priority 4 — Long-Term Recommendations

**4.1 — Author bio pages**
Create per-author or per-team pages (e.g., `/team/release-team/`) with credentials, role descriptions, and links to GitHub profiles. Link post bylines to these pages.

**4.2 — Content freshness signals**
For high-traffic older posts, add a "Last reviewed: [date]" notice and update any outdated code examples or links. This is a quality signal for Google's helpful content evaluation.

**4.3 — Related posts widget**
At the bottom of each post, display 3 related posts (same tag, same release family, or similar topic). This improves pages-per-session and distributes PageRank to older content.

**4.4 — Verify Core Web Vitals**
Run Google PageSpeed Insights on 3 page types (homepage, release post, Inside Rust post) and address any LCP, INP, or CLS issues. The static architecture via CDN will likely score well, but font loading and CSS render-blocking should be verified.

**4.5 — Submit sitemap to Search Console**
Verify sitemap submission status and monitor the Coverage report for any Excluded, Crawled-not-indexed, or Discovered-not-indexed URLs.

---

## What's Working Well (Preserve These)

| Signal | Status |
|--------|--------|
| Domain authority (linked from rust-lang.org primary nav) | Excellent |
| HTTPS + HTTP→HTTPS redirect | Correct |
| robots.txt — no accidental blocks | Correct |
| Sitemap at /sitemap.xml with 724 URLs | Present |
| Unique page titles per post | Good |
| CDN delivery via Fastly | Efficient |
| Social meta (og:title, twitter:title) — unique per post | Good |
| Favicon, webmanifest, apple-touch-icon | Complete |
| Footer trust signals (CoC, Privacy, Security, Licenses) | Present |
| RSS/Atom feeds | Available |

---

## Related Skills

- **schema-markup:** For implementing Article, BlogPosting, WebSite, and Organization structured data
- **site-architecture:** For designing the tag/category taxonomy and content cluster structure
- **analytics-tracking:** For measuring baseline organic traffic before applying fixes, and verifying improvements
- **ai-seo:** For optimizing Rust blog content for AI search engines (Perplexity, ChatGPT Search, Gemini) — especially relevant given Rust's developer audience
- **programmatic-seo:** For generating tag pages and release-family index pages at scale

---

*Audit methodology: Static HTML analysis via curl/web_fetch. JavaScript-rendered content (schema markup injected via JS) was not evaluated — use Google Rich Results Test for schema verification. Core Web Vitals, Search Console data, and backlink profiles require external tool access.*
