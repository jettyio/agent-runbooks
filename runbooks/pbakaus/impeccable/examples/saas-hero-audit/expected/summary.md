# Impeccable Audit — Executive Summary

## Run Details

| Key | Value |
|-----|-------|
| **Operation** | `audit` (read-only, no changes made) |
| **Target** | `/app/assets/b8bda6fc.00.html` |
| **Detector** | `impeccable detect` (npx impeccable@latest) |
| **Node version** | v24.16.0 |
| **Date** | 2026-06-07 |

## Findings

| Metric | Count |
|--------|-------|
| Total anti-patterns | **22** |
| AI-slop tells | **13** |
| Quality issues | **9** |
| Detector exit code | `2` (findings present) |

**Verdict:** The artifact reads as AI-generated. Thirteen distinct slop tells were detected alongside nine accessibility/quality violations.

## Anti-patterns by Rule

| Rule | Count | Category |
|------|-------|----------|
| `low-contrast` | 6 | quality |
| `side-tab` | 3 | slop |
| `gradient-text` | 2 | slop |
| `ai-color-palette` | 1 | slop |
| `broken-image` | 1 | quality |
| `dark-glow` | 1 | slop |
| `extreme-negative-tracking` | 1 | slop |
| `hero-eyebrow-chip` | 1 | slop |
| `marketing-buzzword` | 1 | slop |
| `oversized-h1` | 1 | slop |
| `overused-font` | 1 | slop |
| `single-font` | 1 | slop |
| `skipped-heading` | 1 | quality |
| `tight-leading` | 1 | quality |

## Caveats

- Operation was `audit` only — the target file was **not modified**.
- For URL targets, browser-mode rendering catches additional layout/contrast rules; this was a static-HTML scan.

## Provenance

This audit was performed using the **impeccable** detector:

> impeccable © 2025-2026 Paul Bakaus, Apache-2.0.  
> Builds on Anthropic's frontend-design skill (Apache-2.0, © 2025 Anthropic, PBC).  
> Typography reference incorporates additions from ehmo's typecraft-guide-skill.  
> Source: https://github.com/pbakaus/impeccable

The detector is the authoritative grader: findings and exit codes are derived directly from `impeccable detect --json`, not from LLM judgement.
