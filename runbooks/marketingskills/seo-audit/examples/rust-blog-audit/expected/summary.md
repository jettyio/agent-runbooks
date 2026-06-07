# SEO Audit — Executive Summary
**Site:** https://blog.rust-lang.org  
**Date:** 2026-06-07  
**Site Type:** Official Programming Language Blog (Content/Blog)  
**Overall Health:** Needs Attention

---

## Top 5 Priority Issues

### 1. Missing H1 Tags on Every Page (High — Priority 1)
The entire blog has no `<h1>` element on any page. Post titles render as `<h2>`, and the homepage's highest-level heading is `<h3>` (year groupings). This contradicts basic semantic HTML and SEO best practice — Google explicitly uses H1 as the primary on-page relevance signal.

**Fix:** Change the post title element from `<h2>` to `<h1>` in the blog template. Add a visible `<h1>` to the homepage (e.g., wrapping the site title).

---

### 2. Site-Wide Duplicate Meta Descriptions (High — Priority 1)
All 724+ pages share the identical meta description: *"Empowering everyone to build reliable and efficient software."* — the brand tagline. Every post's `og:description` and `twitter:description` tags are also identically set to the same tagline.

**Fix:** Generate unique per-post meta descriptions from the post's first paragraph or a dedicated front-matter field. This is a template-level change in the static site generator.

---

### 3. No Structured Data / Schema Markup (Medium — Priority 2)
No JSON-LD structured data is present in static HTML (schema.org Article, BlogPosting, WebSite, or Organization). Rich results (article dates, sitelinks searchbox) are unavailable, reducing SERP visibility.

**Fix:** Add Article/BlogPosting JSON-LD to each post, WebSite+SearchAction to the homepage, and Organization site-wide. Verify with Rich Results Test after implementation.

*(Note: Conclusive schema check requires the Rich Results Test — static HTML only was verified here.)*

---

### 4. No Canonical Tags on Any Page (Medium — Priority 2)
All posts lack `<link rel="canonical">` self-references. Without canonical tags, both trailing-slash and non-trailing-slash URL forms serve content (`/Rust-1.85.0/` and `/Rust-1.85.0` both return 200), creating potential duplicate content exposure if the site is scraped or syndicated.

**Fix:** Add self-referencing canonical tags to every page in the site template.

---

### 5. No Topical Content Clusters or Tag Navigation (Medium — Priority 2)
724 posts are organized only by year, with no topic tags, category pages, or pillar content. This fragments topical authority — Google cannot easily identify the site's strongest subject areas (e.g., async Rust, WebAssembly, Cargo), and readers cannot browse by topic.

**Fix:** Implement a tagging system with 10–15 core topic tags. Create indexable tag pages with descriptive introductions. Add 3–5 contextual internal links per post to related posts.

---

## Quick Wins (Low Effort, Immediate Impact)

| Win | Effort | Impact |
|-----|--------|--------|
| Fix H1 on post template (single line change in site generator) | Low | High |
| Add self-referencing canonical tag to site template | Low | Medium |
| Fix empty `twitter:description` on Inside Rust index page | Very Low | Low |
| Fix empty `og:description` on Releases index page | Very Low | Low |
| Add `<lastmod>` to sitemap.xml entries using post dates | Low | Medium |

---

## Strengths (Do Not Break)

- **Domain authority is exceptional** — official rust-lang.org links to this blog in its primary navigation
- **HTTPS and HTTP→HTTPS redirect** are correctly configured
- **Robots.txt** is clean: no unintentional blocks, sitemap referenced, all paths allowed
- **Sitemap.xml** exists with all 724 blog post URLs
- **Post titles are unique** and follow a consistent ` | Rust Blog` suffix pattern
- **Favicons, social images, and viewport meta** are properly configured
- **CDN (Fastly via GitHub Pages)** provides global delivery
- **Atom/RSS feed** (`feed.xml`) supports content syndication and discovery
