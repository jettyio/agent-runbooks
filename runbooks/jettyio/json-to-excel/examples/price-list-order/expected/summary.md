# JSON → Excel — price-list-order — Results

## Overview
- **Date**: 2026-06-07T04:17:05.592444Z
- **Template**: 48359a63.00.xlsx  ·  **Data**: 48359a63.01.json  ·  **Overflow strategy**: alert
- **Sheets touched**: Order
- **Fills**: 1  |  **Placed**: 1  |  **Skipped**: 0  |  **Failed**: 0

## Results Summary
| Status | Count | % |
|--------|-------|---|
| PASS | 1 | 100% |
| PARTIAL | 0 | 0% |
| FAIL | 0 | 0% |
| SKIPPED | 0 | 0% |

## Overflow Events
- **Total**: 0  ·  resolved by insert / alert: 0 / 0  ·  top offenders: none
- 5 data rows fit within 6 available placeholder rows — no overflow triggered.

## Notes Applied
No notes file was provided.

## Recommendations / Limitations
- All 5 purchase order line items written into A4:D9 (20 cells total).
- Column E formulas (=C4*D4 … =C9*D9, =SUM(E4:E9)) are fully preserved; Excel will compute Line Total and Subtotal automatically when the workbook is opened.
- Row 9 (A9:D9) is intentionally empty — only 5 rows of data were supplied for 6 available slots.
- Unit Price values stored as floats (48.5, 22.75, 310.0, 9.95, 120.0); column D has General number_format so no percent/currency coercion was applied.
- SKU and Item columns stored as strings; Qty stored as integers.
