# JSON → Excel — budget-fy2026 — Results

## Overview
- **Date**: 2026-06-07T04:12:50.805327Z
- **Template**: 4fa49a03.00.xlsx  ·  **Data**: 4fa49a03.01.json  ·  **Overflow strategy**: alert
- **Sheets touched**: FY2026 Budget
- **Fills**: 9  |  **Placed**: 9  |  **Partial**: 0  |  **Skipped**: 0  |  **Failed**: 0

## Results Summary
| Status | Count | % |
|--------|-------|---|
| PASS | 9 | 100% |
| PARTIAL | 0 | 0% |
| FAIL | 0 | 0% |
| SKIPPED | 0 | — |

## Overflow Events
- **Total**: 0  ·  resolved by alert: 0  ·  inserts: 0

## Notes Applied
No notes file was present; all defaults applied.

## Recommendations / Limitations
- All 9 fills resolved successfully with exact Jaccard label matches.
- Formulas in column F (FY Total) and row 16 (TOTAL) were preserved.
- Section-label rows (Personnel, Operations, Marketing) were correctly identified as labels and not overwritten.
- No overflow events occurred (each label row had exactly the 4 placeholder cells needed).
