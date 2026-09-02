# ClinicalTrials.gov Condition Search Extraction - Results

## Overview
- **Date**: 2026-09-02
- **Condition searched**: Ulcerative colitis
- **First Posted date range**: 2026-07-25 to 2026-08-25
- **Candidate studies found (API)**: 22
- **Studies dropped by sanity check**: 1. NCT07781215 was dropped because its condition list only stated generic IBD and did not plausibly reference Ulcerative colitis.
- **Studies written to spreadsheet**: 21

## Results Summary

| Status | Count | % |
|--------|-------|---|
| PASS | 21 | 100.0% |
| PARTIAL | 0 | 0.0% |
| FAIL | 0 | 0.0% |

## Sample Outputs

### Successes

| Study Title | NCT Number | Study Status | Enrollment size | Study Type | Start Date |
|---|---|---|---|---|---|
| TOLerogenic Potential of Hematopoietic Stem and Progenitor Cells and Inflammatory Bowel Disease (TOL-IBD) | NCT07740499 | Not yet recruiting | 80 (Estimated) | Observational | 2026-10 (Estimated) |
| A Study to Investigate the Safety, Tolerability, and Pharmacokinetics of ONO-6414 Administered Orally in Healthy Adult Participants and Patients With Active Ulcerative Colitis | NCT07749768 | Not yet recruiting | 90 (Estimated) | Interventional | 2026-09-30 (Estimated) |
| Incremental Value of Traditional Chinese Medicine Features in Two-Stage Pre-Endoscopic Prediction | NCT07784114 | Completed | 1500 (Actual) | Observational | 2015-01-01 (Actual) |

### Failures / Not found fields

No retained study had a `Not found` field or failed extraction. NCT07781215 was excluded during the API-condition sanity check because its page-independent candidate condition was only `IBD (Inflammatory Bowel Disease)`.

## Recommendations
- The results are complete for the specified posting interval; rerun the search if the registry is updated or records are corrected.
- Review the candidate drop if generic IBD studies should be in scope for a future search.

## Limitations
- Only the study's own ClinicalTrials.gov page was used as a source for output values - no other registries, no cached/API-derived substitutions for displayed fields.
