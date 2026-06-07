# PDF Processing — Run Summary

## Operation
- **Operation**: extract-text + extract-tables (full extraction)
- **Input**: `/app/assets/6c756bcf.00.pdf` — "Evaluation of the sugar-sweetened beverage tax in Oakland, United States, 2015–2019" (PLOS Medicine, 20 pages, 656 KB)
- **Output**: `/app/results/extracted_text.txt`, `/app/results/extracted_tables.xlsx`, `/app/results/extracted_tables.json`, `/app/results/output.pdf`
- **Date**: 2026-06-07T01:13:14.919180Z

## Results
| Metric | Value |
|--------|-------|
| Pages processed | 20 |
| Characters extracted | 74,208 |
| Tables found | 5 (pages 8–12) |
| Table rows total | 47 |
| JSON valid | ✓ |

## Table Inventory
| Table | Source Page | Rows | Columns |
|-------|-------------|------|---------|
| 1 | 8 | 20 | 7 |
| 2 | 9 | 24 | 3 |
| 3 | 10 | 1 | 2 |
| 4 | 11 | 1 | 2 |
| 5 | 12 | 1 | 1 |

## Validation

| Check | Status | Notes |
|-------|--------|-------|
| Input file exists | ✓ PASS | 656,272 bytes |
| Text extraction | ✓ PASS | 74,208 chars across 20 pages |
| Table extraction | ✓ PASS | 5 tables |
| extracted_tables.json valid JSON | ✓ PASS | allow_nan=False, no NaN tokens |
| extracted_tables.xlsx written | ✓ PASS | 5 sheets |
| output.pdf written | ✓ PASS | 666,330 bytes |
| summary.md written | ✓ PASS | |
| validation_report.json written | ✓ PASS | |

## Issues / Notes
- Tables on pages 10–12 appear to be inline figure annotations (1–2 row tables); included for completeness.
- PDF is a born-digital typeset document (not scanned); OCR was not required.

## Provenance
- Skill: pdf by anthropics/skills
- Origin: https://skills.sh/anthropics/skills/pdf
- Imported by: skill-to-runbook-converter v1.0.0
