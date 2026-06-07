# PDF Processing — Run Summary

## Operation
- **Operation**: extract-tables
- **Input**: /app/assets/3bc97289.00.pdf (3202 bytes, 1 page)
- **Output**: /app/results/extracted_tables.json, /app/results/extracted_tables.xlsx
- **Date**: 2026-06-07T03:07:17Z

## Results
- 1 table extracted from page 1
- 6 data rows, 5 columns: Item, Description, Qty, Unit Price, Amount
- All cells cleaned (blank/NaN → null); JSON validated with allow_nan=False

## Validation

| Check | Status | Notes |
|-------|--------|-------|
| Input file exists | ✓ PASS | /app/assets/3bc97289.00.pdf |
| Operation completed | ✓ PASS | extract-tables |
| extracted_tables.json non-empty | ✓ PASS | |
| extracted_tables.json valid JSON | ✓ PASS | |
| extracted_tables.xlsx non-empty | ✓ PASS | |
| summary.md written | ✓ PASS | |
| validation_report.json written | ✓ PASS | |

## Issues / Notes
- None

## Provenance
- Skill: pdf by anthropics/skills
- Origin: https://skills.sh/anthropics/skills/pdf
- Imported by: skill-to-runbook-converter v1.0.0
