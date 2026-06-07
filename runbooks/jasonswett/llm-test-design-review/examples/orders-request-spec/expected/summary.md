# Test Design Review — Results

## Overview
- **Date**: 2026-06-07T00:00:00Z
- **Files reviewed**: `d0436129.00.rb`
- **Focus**: all guidelines

## Findings by guideline

| Guideline | Count | Severity (H/M/L) |
|-----------|-------|------------------|
| `specification-format` | 1 | H |
| `avoid-arbitrariness` | 1 | H |
| `observable-not-method-calls` | 1 | H |
| `describe-the-essence` | 1 | M |
| `no-described-class` | 1 | M |
| `no-tight-coupling` | 1 | M |
| **Total** | **6** | — |

## Overall assessment

The file covers two scenarios in just 21 lines and has the virtue of brevity, but accumulates six design violations across both tests. The first test suffers from a vague name (`"works"`), an order-dependent record retrieval (`Order.last`), and an outer `describe "POST /orders"` that captures the HTTP mechanism rather than the scenario's meaning. The second test asserts on a mock method call (`have_received(:charge)`) instead of an observable outcome, and binds itself to `PaymentGateway`'s internal construction via `allow(PaymentGateway).to receive(:new)`. The highest-value fix is to replace the mock assertion with an assertion on a persisted `Charge` record (or a test-mode gateway log), which would simultaneously resolve `observable-not-method-calls` and `no-tight-coupling` and make the test resilient to refactoring.

## Notes / Limitations

All guidelines were evaluated. Ruby/RSpec-specific guidelines (`no-described-class`, `no-have-current-path`, `no-instance-variable-set`, `no-private-method-hacks`) were applied as written. Guidelines not applicable to this file's content (`arrange-act-assert`, `avoid-forward-reference`, `essential-not-incidental`, `high-level-of-abstraction`, `no-speculative-coding`, `one-level-of-abstraction`, `test-ends-not-means`, `behavior-not-implementation`) were reviewed and found to have no violations.
