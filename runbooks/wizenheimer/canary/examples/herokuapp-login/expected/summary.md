# Canary QA — Results

## Overview
- **Date**: 2026-06-07T23:43:40Z  ·  **Target**: https://the-internet.herokuapp.com/login
- **Flow**: Login with tomsmith / SuperSecretPassword!, assert success banner, logout, verify login form
- **Verdict**: PASS  ·  **Steps**: 7/7

## Steps
| # | Step | Action | Status | Console errors |
|---|------|--------|--------|----------------|
| 1 | open login page | navigate | ✓ PASS | 1 |
| 2 | fill username | fill | ✓ PASS | 1 |
| 3 | fill password | fill | ✓ PASS | 1 |
| 4 | submit login form | click | ✓ PASS | 5 |
| 5 | check success flash banner | assert | ✓ PASS | 5 |
| 6 | click logout | click | ✓ PASS | 11 |
| 7 | check login form returned | assert | ✓ PASS | 11 |

## Most important finding
Flow passed clean — 7 steps, 35 console errors

## Artifacts
- `report.html` (self-contained, screenshots inlined) · `replay.py` (CI-ready) · `trace.zip` · `network.har` · `console.log` · `steps.json`
