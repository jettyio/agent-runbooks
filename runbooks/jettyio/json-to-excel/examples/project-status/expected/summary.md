# JSON → Excel — project-status — Results

## Overview
- **Date**: 2026-06-07T04:16:30.411872Z
- **Template**: bc354d46.00.xlsx  ·  **Data**: bc354d46.01.json  ·  **Overflow strategy**: alert
- **Sheets touched**: Status
- **Fills**: 4  |  **Placed**: 4  |  **Skipped**: 0  |  **Failed**: 0

## Results Summary
| Status | Count | % |
|--------|-------|---|
| PASS | 4 | 100% |
| PARTIAL | 0 | 0% |
| FAIL | 0 | 0% |
| SKIPPED | 0 | — |

## Overflow Events
- **Total**: 0  ·  resolved by insert / alert: 0 / 0  ·  top offenders: []

## Notes Applied
No notes file uploaded — no rules extracted.

## Recommendations / Limitations
- No overflow events occurred; all 4 workstream rows fit within the template.
- RAG values (Green/Amber/Red) written to dropdown-validated cells as plain text; values should match the dropdown list for validation to pass in Excel.
- % Complete values coerced to floats (e.g. "85%" → 0.85) per the cell's `0%` number_format.
