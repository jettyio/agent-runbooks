# Test Design Review — Results

## Overview
- **Date**: 2026-06-07T00:00:00Z
- **Files reviewed**: `78d5514b.00.rb`
- **Focus**: all guidelines

## Findings by Guideline

| Guideline               | Count | Severity (H/M/L) |
|-------------------------|-------|------------------|
| describe-the-essence    | 2     | M, L             |
| avoid-forward-reference | 1     | H                |
| no-have-current-path    | 1     | M                |
| no-instance-variable-set| 1     | H                |
| no-tight-coupling       | 2     | H, M             |
| no-speculative-coding   | 1     | L                |
| **Total**               | **8** |                  |

## Overall Assessment

The file has two high-severity issues that should be fixed immediately. The forward-reference bug (lines 6–7: `let!(:order)` before `let!(:customer)`) almost certainly causes intermittent test failures in CI because `:order` tries to reference `:customer` before it is memoized. The `controller.instance_variable_set(:@order_count, 5)` call (line 23) completely bypasses the order-counting logic, making the second test a hollow assertion that can never catch a regression in the count query. The single highest-value fix is the forward-reference swap — it is a one-line change and is likely the root cause of any flakiness already observed. Once that is fixed, replacing `instance_variable_set` with real factory data makes the second test genuinely meaningful.

## Notes / Limitations

- The review was performed on the full file (no diff supplied).
- Guidelines `no-described-class` and `no-private-method-hacks` are not applicable to this file (no `described_class` or `send`/`public_send` present).
- The suggested fix for `can_view?` (Finding 7) references a hypothetical `grant_permission` API; the exact call must be adapted to the application's real authorization library.
