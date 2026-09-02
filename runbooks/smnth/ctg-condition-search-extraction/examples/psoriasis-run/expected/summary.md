# ClinicalTrials.gov Condition Search Extraction - Results

## Overview
- **Date**: 2026-09-02
- **Condition searched**: Psoriasis
- **First Posted date range**: 2026-07-25 to 2026-08-25
- **Candidate studies found (API)**: 17
- **Studies dropped by sanity check**: 5 (one Healthy Volunteers record, one Inflammatory Skin Conditions record, and three Psoriatic Arthritis records did not have a condition list that plausibly identified Psoriasis itself)
- **Studies written to spreadsheet**: 12

## Results Summary

| Status | Count | % |
|--------|-------|---|
| PASS | 12 | 100.0% |
| PARTIAL | 0 | 0.0% |
| FAIL | 0 | 0.0% |

## Sample Outputs

### Successes

| Study Title | NCT Number | Study Status | Enrollment size | Study Type | Start Date |
|---|---|---|---|---|---|
| A Study of HL40626S Tablets in Healthy Adults | NCT07736586 | Not yet recruiting | 64 (Estimated) | Interventional | 2026-08 (Estimated) |
| A Study of Guselkumab Given After Ustekinumab in Participants With Moderate to Severe Psoriasis in Routine Clinical Practice (G-START) | NCT07746583 | Recruiting | 100 (Estimated) | Observational | 2026-09-15 (Estimated) |
| A Study to Evaluate the Efficacy and Safety of LZM012 ( Psoriasis ) | NCT07746479 | Completed | 244 (Actual) | Interventional | 2025-06-23 (Actual) |

### Failures / Not found fields

None. No retained study had a `Not found` field and no study page was excluded.

## Recommendations
- Use the accompanying audit file to review the five condition-sanity drops if Psoriatic Arthritis or broader inflammatory-skin-condition studies should be included in a future search.
- Re-run close to the required reporting date if current recruitment statuses are important, because registry fields can change.

## Limitations
- Only the study's own ClinicalTrials.gov page was used as a source for extracted fields - no other registries, no cached/API-derived substitutions for displayed fields.
