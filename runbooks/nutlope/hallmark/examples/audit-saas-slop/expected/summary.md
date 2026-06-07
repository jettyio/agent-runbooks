# Hallmark — audit — Results

## Overview
- **Date**: 2026-06-07T00:00:00Z
- **Operation**: audit
- **Brief**: Audit this landing page against Hallmark's anti-pattern list. It is a typical AI-generated SaaS landing page. Return a ranked punch list grouped by severity with a count line. Do NOT edit anything.
- **Input file**: `/app/assets/a45a609c.00.html` — single self-contained HTML file with embedded CSS, 101 lines

## Inferred context (audit)
No design decisions were made. The audit reads the uploaded page as-is and scores it against Hallmark's 58-gate slop test and named anti-pattern catalogue. All findings are observations, not prescriptions.

## Findings count
**7 critical · 9 major · 4 minor** = 20 total findings

| Severity | Count | Leading tells |
|----------|-------|---------------|
| Critical | 7 | AI template structure, purple gradient hero, 3-col feature grid, AI nav, AI footer, centred hero, Inter-everywhere |
| Major | 9 | Re-drawn browser chrome, italic header, invented metrics, emoji icons, no tokens, no interactive states, no responsive layout, centred everything, contrast failure |
| Minor | 4 | Cliché copy, emoji social icons, no tabular-nums, px prose max-width |

## What was produced
- `audit_report.md` — full ranked punch list grouped by severity; each finding includes Tell name, Where (file:line), Severity, and Fix; slop-gate table appended; verdict at end
- `summary.md` — this file
- `validation_report.json` — stage-by-stage pass/fail record

## Slop test (applied as audit rubric — gate failures)
**24 / 58 gates fail** on the audited page. No gate was skipped for genre leniency — the page carries no genre stamp, and its structure is editorial-SaaS, so universal gate rules apply throughout.

Key gate failures: 1 (Inter-everywhere), 2 (purple gradient), 3 (3-col equal card grid), 6 (centred-everything hero auto-fail), 7 (pure white gradient endpoint), 8 (AI template structure), 23 (accent overuse > 5%), 25 (prose max-width in px), 26 (no interactive states), 29 (gradient covers entire hero), 30 (emoji feature icons), 34 (no horizontal scroll protection), 38a (italic in h1), 40–41 (contrast failure on CTA band), 42 (AI nav), 43 (AI footer), 44 (hero exceeds fold), 45 (decorative chrome without semantic anchor), 46 (invented metrics), 47 (re-drawn browser chrome), 48 (inline hex values, no CSS custom properties), 49–51 (no responsive breakpoints).

## Verdict
**Ships as slop.** The page demonstrates near-perfect execution of the AI-generation fingerprint: structural AI template, three purple gradients, three invented metrics, three emoji feature-card icons, a hand-built fake browser bar, an italicised word in the hero h1, a system-font-only stack, and zero responsive design. No individual fix resolves this — the page needs a structural rebuild against a non-default macrostructure with a real token system, a verified font pairing, and content grounded in real facts.

## Limitations / notes
- The page has no Hallmark stamp, so the stamp-vs-page check is trivially N/A.
- No `design.md` in scope, so design-system drift checks do not apply.
- Contrast computation on CTA band is estimated from OKLCH lightness delta (white on #a78bfa ≈ L 72% → ~2:1 ratio); a tool-verified APCA Lc calculation may refine this.
- The audit does NOT edit the file; all findings are for human action.
