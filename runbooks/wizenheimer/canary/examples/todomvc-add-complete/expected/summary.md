# Canary QA — Results

## Overview
- **Date**: 2026-06-07T00:00:00Z  ·  **Target**: https://demo.playwright.dev/todomvc
- **Flow**: Add "Buy milk" and "Walk the dog" todos, verify counter at 2, mark "Buy milk" done, verify counter at 1 and item completed
- **Verdict**: PASS  ·  **Steps**: 7/7

## Steps

| # | Step | Action | Status | Console errors |
|---|------|--------|--------|----------------|
| 1 | open the app | navigate | PASS | 0 |
| 2 | add todo Buy milk | fill+enter | PASS | 0 |
| 3 | add todo Walk the dog | fill+enter | PASS | 0 |
| 4 | counter shows 2 items left | assert | PASS | 0 |
| 5 | mark Buy milk completed | click | PASS | 0 |
| 6 | counter shows 1 item left | assert | PASS | 0 |
| 7 | Buy milk is marked completed | assert | PASS | 0 |

## Most important finding
Flow passed clean — 7/7 steps, 0 console errors, 6 network requests with 0 failures.

## Artifacts
- `report.html` (self-contained, screenshots inlined) · `replay.py` (CI-ready, exits 0) · `trace.zip` · `network.har` · `console.log`
