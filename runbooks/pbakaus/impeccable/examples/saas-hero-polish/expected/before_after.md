# Polish run — before / after

**Target:** `/app/assets/2fc20cfd.00.html`
**Before:** 22 anti-pattern(s)  
**After:** 0 anti-pattern(s)  
**Verdict:** CLEAN — all findings resolved

## Rules resolved

| Rule | Before | After | Status |
|------|--------|-------|--------|
| `ai-color-palette` | 1 | 0 | ✓ resolved |
| `broken-image` | 1 | 0 | ✓ resolved |
| `dark-glow` | 1 | 0 | ✓ resolved |
| `extreme-negative-tracking` | 1 | 0 | ✓ resolved |
| `gradient-text` | 2 | 0 | ✓ resolved |
| `hero-eyebrow-chip` | 1 | 0 | ✓ resolved |
| `low-contrast` | 6 | 0 | ✓ resolved |
| `marketing-buzzword` | 1 | 0 | ✓ resolved |
| `oversized-h1` | 1 | 0 | ✓ resolved |
| `overused-font` | 1 | 0 | ✓ resolved |
| `side-tab` | 3 | 0 | ✓ resolved |
| `single-font` | 1 | 0 | ✓ resolved |
| `skipped-heading` | 1 | 0 | ✓ resolved |
| `tight-leading` | 1 | 0 | ✓ resolved |

## Regressions

_None — no new rules introduced._

## Fix summary

| Tell | Fix applied |
|------|-------------|
| `side-tab` | Removed one-sided `border-left`; replaced with full 1px `border` on cards |
| `gradient-text` | h1 set to solid `var(--ink)` color; removed `background-clip: text` |
| `ai-color-palette` | Replaced purple/cyan (#7c3aed → #06b6d4) with warm amber accent (#d4752a) |
| `dark-glow` | Removed colored `box-shadow` glow from cards |
| `overused-font` | Replaced Inter with DM Serif Display (headings) + Barlow (body) |
| `single-font` | Now uses two distinct font families |
| `hero-eyebrow-chip` | Removed `.eyebrow` span entirely |
| `oversized-h1` | Reduced h1 to 3.25rem (52 px) with a short concrete headline |
| `extreme-negative-tracking` | Tracking eased from −0.07em to −0.03em (above −0.05em floor) |
| `tight-leading` | Body `line-height` raised from 1.25 to 1.6 |
| `skipped-heading` | Changed card headings from h3 to h2 |
| `low-contrast` | Muted text raised to `#b0aca7` (≥ 7:1 contrast on `#171a22`) |
| `broken-image` | Removed logo strip with empty/placeholder `<img>` tags |
| `marketing-buzzword` | All copy rewritten with concrete verbs and product-specific nouns |
