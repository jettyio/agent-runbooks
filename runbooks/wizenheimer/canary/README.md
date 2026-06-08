# wizenheimer/canary — demo payload

A launch payload for the `wizenheimer/canary` runbook: the runbook, a `manifest.json`, and
three worked examples — each a real production QA run that drives a public test app in a real
browser and hands back a report **and** a reusable Playwright script.

```
canary/
  RUNBOOK.md                        # the runbook (v1.0.0, prism-playwright snapshot)
  manifest.json                     # directory metadata
  README.md                         # this file
  examples/
    todomvc-add-complete/           # CRUD flow — add + complete a todo
      input.json  trajectory.json  thumbnail.png
      expected/  report.html (primary) · replay.py (primary) · console.log · steps.json · summary.md · validation_report.json · screenshots/
      #          (the runbook also emits trace.zip + network.har; omitted here — 6–10 MB/run, reproducible)
    saucedemo-login-cart/           # auth + cart flow
      input.json  trajectory.json  thumbnail.png  expected/ …
    herokuapp-login/                # auth flow (login + logout)
      input.json  trajectory.json  thumbnail.png  expected/ …
```

## Attribution

Converted, with attribution, from **Canary** — [github.com/wizenheimer/canary](https://github.com/wizenheimer/canary)
(**MIT**), a QA harness for coding agents. Canary ships its own CLI, a QuickJS-WASM Playwright
sandbox, and a background daemon. This runbook **re-implements its core idea with plain
Playwright** so it runs in the Jetty sandbox with no install/daemon: describe a flow → the
agent drives a real browser → you get a self-contained report **and** a reusable replay
script. The on-disk format differs from canary's own `report.html`/session layout; the value
(report + evidence + a CI-ready script) is the same.

## What it does

You describe a user flow in plain language with the checks that must hold. The agent reads the
live page for real selectors, drives the flow through small intent-named steps, and captures
**evidence at every step** — a screenshot, console messages, network activity — plus a
Playwright **trace** for the whole session. It hands back both things canary insists on having
together: a **report.html** you can just open and read, and the exact **replay.py** that
reproduces the flow in CI with zero agent cost.

## The gallery: three flows, three public test apps

| # | App | Flow | Steps | Verdict | Trajectory |
|---|-----|------|-------|---------|-----------|
| 1 | TodoMVC | add two todos, complete one, assert the counter (2→1) | 7 | **PASS 7/7** | `c5172934` |
| 2 | SauceDemo | log in, add backpack to cart, assert cart badge = 1 | 7 | **PASS 7/7** | `8b80f8a0` |
| 3 | the-internet | log in, assert success banner, log out, assert form returns | 7 | **PASS 7/7** | `affed313` |

All three are green: real browser automation on Jetty's `prism-playwright` snapshot, with
real assertions (not just no-throw), per-step screenshots, a Playwright trace, and a
`replay.py` that parses and reproduces the flow. The targets are deterministic public test
apps (TodoMVC, SauceDemo, the-internet) — designed to be driven.

Each `report.html` is self-contained (screenshots inlined as base64): open it, commit it,
send it. Each `replay.py` is the CI artifact — re-run the flow forever with no agent cost.

## Reproduce (example 1)

```bash
TOKEN="$(grep '^JETTY_API_TOKEN_JON_RUNBOOKS=' .env | cut -d= -f2-)"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  --form-string 'init_params={"vars":{"target_url":"https://demo.playwright.dev/todomvc","flow":"Add two todos, complete one, assert the counter shows the right count.","headless":"true"}}' \
  "https://flows-api.jetty.io/api/v1/run/jon-runbooks/wizenheimer-canary"
```
