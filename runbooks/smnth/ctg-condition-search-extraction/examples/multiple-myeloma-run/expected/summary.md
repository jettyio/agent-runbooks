# ClinicalTrials.gov Condition Search Extraction — Results

## Overview
- **Date**: 2026-08-25
- **Condition searched**: Multiple myeloma
- **First Posted date range**: 2026-06-25 to 2026-08-25
- **Candidate studies found (API)**: 47
- **Studies dropped by sanity check**: 1 (`NCT07777406`: returned condition list was `Plasma Cell Neoplasms`, which did not plausibly reference the requested condition under the condition-list rule)
- **Studies written to spreadsheet**: 46

## Results Summary

| Status | Count | % |
|--------|-------|---|
| PASS | 46 | 100.0% |
| PARTIAL | 0 | 0.0% |
| FAIL | 0 | 0.0% |

## Sample Outputs

### Successes

| Study Title | NCT Number | Study Status | Enrollment size | Study Type | Start Date |
|---|---|---|---|---|---|
| Real-World Clinical Outcomes in Relapsed/Refractory Multiple Myeloma Treated With Pomalidomide Regimens | NCT07689006 | Completed | 341 (Actual) | Observational | 2024-12-23 (Actual) |
| CD38 Targeted -PET/ CT for Multiple Myeloma | NCT07782944 | Recruiting | 100 (Estimated) | Interventional | 2026-07-07 (Actual) |
| A Modular, Phase I/II, Multicentre Study to Evaluate AZD4045, in Participants With Relapsed or Refractory Multiple Myeloma | NCT07681596 | Not yet recruiting | 101 (Estimated) | Interventional | 2026-07-09 (Estimated) |

### Failures / Not found fields

No spreadsheet rows contain `Not found` fields. `NCT07777406` was excluded before page extraction because its API-returned condition list did not pass the requested condition sanity check.

## Recommendations
- Use the CSV as the complete result set for this requested posting-date window.
- Re-run the extraction if current recruitment status or enrollment values are needed later because study records can change after posting.

## Limitations
- Only each study's own rendered ClinicalTrials.gov page was used as the source for spreadsheet field values; no other registry, cached source, or API-derived substitution was used.
- The ClinicalTrials.gov API v2 was used only to identify candidates and perform the requested condition-list sanity check.
