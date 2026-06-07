# Impeccable audit — `/app/assets/b8bda6fc.00.html`

**Findings:** 22 (13 AI-slop, 9 quality)  
**Verdict:** reads as AI-generated — see tells

| # | Rule | Category | Line | Snippet |
|---|------|----------|------|---------|
| 1 | `side-tab` | slop | — | `border-left: 4px + border-radius: 16px` |
| 2 | `side-tab` | slop | — | `border-left: 4px + border-radius: 16px` |
| 3 | `side-tab` | slop | — | `border-left: 4px + border-radius: 16px` |
| 4 | `gradient-text` | slop | — | `background-clip: text + gradient` |
| 5 | `low-contrast` | quality | — | `3.6:1 (need 4.5:1) — text #64748b on #111935` |
| 6 | `low-contrast` | quality | — | `3.6:1 (need 4.5:1) — text #64748b on #111935` |
| 7 | `low-contrast` | quality | — | `3.6:1 (need 4.5:1) — text #64748b on #111935` |
| 8 | `low-contrast` | quality | — | `3.6:1 (need 4.5:1) — text #64748b on #111935` |
| 9 | `low-contrast` | quality | — | `3.6:1 (need 4.5:1) — text #64748b on #111935` |
| 10 | `low-contrast` | quality | — | `3.6:1 (need 4.5:1) — text #64748b on #111935` |
| 11 | `hero-eyebrow-chip` | slop | — | `eyebrow chip (tracked-caps) "Introducing Nimbus"` |
| 12 | `broken-image` | quality | — | `<img src="">` |
| 13 | `extreme-negative-tracking` | slop | — | `letter-spacing: -0.07em — "Supercharge your team` |
| 14 | `tight-leading` | quality | — | `line-height 1.19x (need >=1.3)` |
| 15 | `oversized-h1` | slop | — | `84px h1, 81 chars "Supercharge your team with ou` |
| 16 | `overused-font` | slop | — | `Primary font: inter` |
| 17 | `single-font` | slop | — | `only font used is inter` |
| 18 | `skipped-heading` | quality | — | `<h1> "Supercharge your team with our enterprise-` |
| 19 | `ai-color-palette` | slop | — | `Purple/violet accent colors detected` |
| 20 | `gradient-text` | slop | — | `background-clip: text + gradient` |
| 21 | `dark-glow` | slop | — | `Colored glow (rgb(124,58,237)) on dark page` |
| 22 | `marketing-buzzword` | slop | — | `8 buzzword phrases: "cing Nimbus Supercharge you` |

### 1. Side-tab accent border (`side-tab`)
- **Location:** line — — `border-left: 4px + border-radius: 16px`
- **Why it matters:** Thick colored border on one side of a card — the most recognizable tell of AI-generated UIs. Use a subtler accent or remove it entirely.

### 2. Side-tab accent border (`side-tab`)
- **Location:** line — — `border-left: 4px + border-radius: 16px`
- **Why it matters:** Thick colored border on one side of a card — the most recognizable tell of AI-generated UIs. Use a subtler accent or remove it entirely.

### 3. Side-tab accent border (`side-tab`)
- **Location:** line — — `border-left: 4px + border-radius: 16px`
- **Why it matters:** Thick colored border on one side of a card — the most recognizable tell of AI-generated UIs. Use a subtler accent or remove it entirely.

### 4. Gradient text (`gradient-text`)
- **Location:** line — — `background-clip: text + gradient`
- **Why it matters:** Gradient text is decorative rather than meaningful — a common AI tell, especially on headings and metrics. Use solid colors for text.

### 5. Low contrast text (`low-contrast`)
- **Location:** line — — `3.6:1 (need 4.5:1) — text #64748b on #111935`
- **Why it matters:** Text does not meet WCAG AA contrast requirements (4.5:1 for body, 3:1 for large text). Increase the contrast between text and background.

### 6. Low contrast text (`low-contrast`)
- **Location:** line — — `3.6:1 (need 4.5:1) — text #64748b on #111935`
- **Why it matters:** Text does not meet WCAG AA contrast requirements (4.5:1 for body, 3:1 for large text). Increase the contrast between text and background.

### 7. Low contrast text (`low-contrast`)
- **Location:** line — — `3.6:1 (need 4.5:1) — text #64748b on #111935`
- **Why it matters:** Text does not meet WCAG AA contrast requirements (4.5:1 for body, 3:1 for large text). Increase the contrast between text and background.

### 8. Low contrast text (`low-contrast`)
- **Location:** line — — `3.6:1 (need 4.5:1) — text #64748b on #111935`
- **Why it matters:** Text does not meet WCAG AA contrast requirements (4.5:1 for body, 3:1 for large text). Increase the contrast between text and background.

### 9. Low contrast text (`low-contrast`)
- **Location:** line — — `3.6:1 (need 4.5:1) — text #64748b on #111935`
- **Why it matters:** Text does not meet WCAG AA contrast requirements (4.5:1 for body, 3:1 for large text). Increase the contrast between text and background.

### 10. Low contrast text (`low-contrast`)
- **Location:** line — — `3.6:1 (need 4.5:1) — text #64748b on #111935`
- **Why it matters:** Text does not meet WCAG AA contrast requirements (4.5:1 for body, 3:1 for large text). Increase the contrast between text and background.

### 11. Hero eyebrow / pill chip (`hero-eyebrow-chip`)
- **Location:** line — — `eyebrow chip (tracked-caps) "Introducing Nimbus" above h1 "Supercharge your team with our enterprise-grade, world-class"`
- **Why it matters:** A tiny uppercase letter-spaced label sitting immediately above an oversized hero headline — or the same shape rendered as a pill chip — is now the default AI SaaS hero. Drop the eyebrow, integrate the kicker into the headline, or run it as a navigation breadcrumb instead.

### 12. Broken or placeholder image (`broken-image`)
- **Location:** line — — `<img src="">`
- **Why it matters:** <img> tags with empty src, missing src, or placeholder values ship as broken-image boxes. Use real images, generated assets, or remove the tag.

### 13. Crushed letter spacing (`extreme-negative-tracking`)
- **Location:** line — — `letter-spacing: -0.07em — "Supercharge your team with our enterpris"`
- **Why it matters:** Letter-spacing pulled tighter than the point where characters keep their own shapes costs legibility. Tighten display type optically, not destructively.

### 14. Tight line height (`tight-leading`)
- **Location:** line — — `line-height 1.19x (need >=1.3)`
- **Why it matters:** Line height below 1.3x the font size makes multi-line text hard to read. Use 1.5 to 1.7 for body text so lines have room to breathe.

### 15. Oversized hero headline (`oversized-h1`)
- **Location:** line — — `84px h1, 81 chars "Supercharge your team with our enterprise-grade, world-class"`
- **Why it matters:** A full-sentence headline set at display size ends up dominating the viewport, leaving no room for anything else above the fold. A punchy one- or two-word headline at that size is fine — the problem is a long headline blown up too large. Set long headlines smaller, or tighten the copy.

### 16. Overused font (`overused-font`)
- **Location:** line — — `Primary font: inter`
- **Why it matters:** Inter, Roboto, Fraunces, Geist, Plus Jakarta Sans, and Space Grotesk are used on so many sites they no longer feel distinctive. Each new wave of AI-generated UIs converges on the same handful of faces. Choose a face that gives your interface personality.

### 17. Single font for everything (`single-font`)
- **Location:** line — — `only font used is inter`
- **Why it matters:** Only one font family is used for the entire page. Pair a distinctive display font with a refined body font to create typographic hierarchy.

### 18. Skipped heading level (`skipped-heading`)
- **Location:** line — — `<h1> "Supercharge your team with our enterprise-grade, world-class" followed by <h3> "Automate" (missing h2)`
- **Why it matters:** Heading levels should not skip (e.g. h1 then h3 with no h2). Screen readers use heading hierarchy for navigation. Skipping levels breaks the document outline.

### 19. AI color palette (`ai-color-palette`)
- **Location:** line — — `Purple/violet accent colors detected`
- **Why it matters:** Purple/violet gradients and cyan-on-dark are the most recognizable tells of AI-generated UIs. Choose a distinctive, intentional palette.

### 20. Gradient text (`gradient-text`)
- **Location:** line — — `background-clip: text + gradient`
- **Why it matters:** Gradient text is decorative rather than meaningful — a common AI tell, especially on headings and metrics. Use solid colors for text.

### 21. Dark mode with glowing accents (`dark-glow`)
- **Location:** line — — `Colored glow (rgb(124,58,237)) on dark page`
- **Why it matters:** Dark backgrounds with colored box-shadow glows are the default "cool" look of AI-generated UIs. Use subtle, purposeful lighting instead — or skip the dark theme entirely.

### 22. Marketing buzzword (`marketing-buzzword`)
- **Location:** line — — `8 buzzword phrases: "cing Nimbus Supercharge your team with o"`
- **Why it matters:** Generic SaaS phrases (streamline / empower / supercharge / world-class / enterprise-grade / next-generation / cutting-edge / etc) are instant AI tells. Pick a specific verb and noun that says what the product literally does.
