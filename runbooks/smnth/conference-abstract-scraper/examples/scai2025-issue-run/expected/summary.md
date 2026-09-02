# Conference Abstract Scraper — Results

## Overview
- **Date**: 2026-09-02
- **CrossRef ISSN / volume-issue**: 2772-9303 / volume 4, issue 5
- **Confex program**: https://scai.confex.com/scai/2025/meetingapp.cgi
- **Abstracts requested**: 12
- **Abstracts processed**: 12

## Results Summary

| Status | Count | % |
|--------|-------|---|
| PASS | 11 | 91.7% |
| PARTIAL | 1 | 8.3% |
| FAIL | 0 | 0% |

## Completeness Check
- Entries discovered via CrossRef: 12 (of 805 session-coded abstracts in vol. 4/issue 5, taking the first 12 by page number: OR1-1–OR1-12, pages 102652–102663, no gaps)
- Entries matched in Confex program: 12
- Entries in final output: 12
- Duplicate/merge conflicts detected: 0

## Sample Outputs

### Successes

**OR1-1** — *Outcomes of Balloon Pulmonary Angioplasty versus Medical Therapy in Chronic Thromboembolic Pulmonary Hypertension: A Real-World Analysis*
DOI: `10.1016/j.jscai.2025.102652` · Confex Paper 35852 (exact title match, score 1.0)
> Background: Chronic thromboembolic pulmonary hypertension (CTEPH) can be managed with medical therapy alone or in combination with balloon pulmonary angioplasty (BPA)... Medical therapy plus BPA was associated with significantly lower mortality compared to medical therapy alone (7.8% vs 24.1%, OR 3.755...)

**OR1-4** — *STRIKE-PE Analysis: Outcomes of Computer Assisted Vacuum Thrombectomy for Treatment of PE in Male vs Female Patients*
DOI: `10.1016/j.jscai.2025.102655` · Confex Paper 37435 (exact title match, score 1.0)
> Full Background/Methods/Results/Conclusions structure recovered (2,284 chars), including sex-stratified safety and dyspnea outcomes from the first 450 STRIKE-PE patients.

**OR1-9** — *Comparative Long-Term Clinical Outcomes of Ticagrelor vs. Prasugrel Following PCI of CTO: A Real-World Analysis from the Trinetx Database*
DOI: `10.1016/j.jscai.2025.102660` · Confex Paper 38542 (exact title match, score 1.0)
> Retrospective TriNetX cohort study (3,391 vs. 976 patients, propensity-matched to 974/974) comparing 5-year MACE, mortality, and bleeding outcomes between P2Y12 inhibitors.

### Partial / Notable Cases

**OR1-12** — *Drug-Coated Versus Uncoated Balloon for Side Branch in Coronary Bifurcation Lesions*
DOI: `10.1016/j.jscai.2025.102663` · Confex Paper 36046, status **PARTIAL**
The Confex program lists this record under a differently worded pre-publication title (*"Drug-Coated Balloons vs. Plain Balloon Angioplasty for Side Branch Management in Coronary Bifurcation Lesions: A Systematic Review and Meta-Analysis"*, Poster D-92) rather than as an Oral Abstract as the `OR1-` code would suggest. The naive surface-text search initially matched a *different* abstract ("Drug-Coated Balloon Versus Uncoated Balloon Angioplasty in the Management of Coronary **In-Stent Restenosis**") because it shared several leading words — this was caught and corrected by re-matching on distinctive-keyword (Jaccard token) overlap and manually verifying the corrected match's content (bifurcation lesions / side branch / DCB vs. BA, same outcome measures) against the CrossRef abstract. Full text (1,523 chars, complete 4-section structure) was recovered and is included; the entry is flagged PARTIAL rather than PASS because the title match required more than light normalization.

No hard failures occurred — every one of the 12 CrossRef-discovered entries has complete metadata and full abstract text in the final output.

## Recommendations
- When abstract titles differ substantially between CrossRef's published version and Confex's pre-publication listing, plain string-similarity search ranking (e.g. Levenshtein/SequenceMatcher on the raw title) can rank a topically-unrelated abstract above the correct one if it happens to share more leading characters. A keyword/token-overlap (Jaccard) score, or a combination of the two, is more robust and should be the default matching strategy rather than a fallback.
- Session codes (`OR1-`, `A-`, `E-`, etc.) assigned at CrossRef-publication time do not always match the session type (Oral Abstract vs. Poster) the record ultimately appears under in the conference program — don't use the code prefix alone to filter or validate a match.
- For any run where the top Confex search match's score falls in a middle band (roughly 0.5–0.75), it's worth spot-checking the retrieved full text against the CrossRef abstract's evident topic before trusting the match, as done here for OR1-12.

## Limitations
- Confex's search endpoint returns a relevance-ranked top-10 list; a correct match ranked below position 10 for both the code-stripped title and the short-title fallback query would not have been found. This did not occur in this run (all 12 correct matches appeared within the top 10 results for at least one query variant), but a program with much higher volume or more generic titles could hit this ceiling.
- `full_text` is taken verbatim from the Confex program's pre-publication abstract; it can differ in minor ways (added post-hoc statistics, corrected typos, e.g. the "628/50.4" figure formatting glitch visible in OR1-12's Results section) from the final published JSCAI version, since Confex text is not updated after the meeting.
- No page-number gaps or apparent withdrawals occurred in the selected range (OR1-1–OR1-12 are fully contiguous, pages 102652–102663), so gap-handling logic was exercised only outside the first-12 selection (see `validation_report.json` notes for the 4 duplicate-DOI records found elsewhere in the full volume/issue).
