# Conference Abstract Scraper — Results

## Overview
- **Date**: 2026-09-02
- **CrossRef ISSN / volume-issue**: 2772-9303 / volume 5, issue 4
- **Confex program**: https://scai.confex.com/scai/2026/meetingapp.cgi
- **Abstracts requested**: 10
- **Abstracts processed**: 10

## Results Summary

| Status | Count | % |
|--------|-------|---|
| PASS | 10 | 100% |
| PARTIAL | 0 | 0% |
| FAIL | 0 | 0% |

## Completeness Check
- Entries discovered via CrossRef (target abstract subset): 864 total conference abstracts found in the issue; first 10 by page number selected
- Entries matched in Confex program: 10 / 10
- Entries in final output: 10
- Duplicate/merge conflicts detected: 0

## Important Finding: Volume/Issue Scope

CrossRef volume 5, issue 4 of *JSCAI* is **not** a stand-alone abstract supplement — it is the journal's regular April 2026 monthly issue, which happens to co-publish the SCAI 2026 Scientific Sessions abstracts alongside its usual editorial content. Of the 864 works CrossRef returns for this volume/issue:

- **834** are conference abstracts, identifiable by a session-code title prefix (e.g. `OR1-1 | ...`). This was confirmed against the Confex program itself, whose search-filter form exposes exactly these categories (`Oral Abstract`, `Poster Abstract`, alongside `Case Review`, `Live Case`, `Satellite Session`, `Symposium`, `Workshop`, etc.).
- **30** are regular journal content that was never entered into the Confex program at all: original research articles, case reports, an editorial ("Lessons From the Past"), a letter-to-the-editor response, a corrigendum, and issue front/back matter (Cover, Title Page, Table of Contents, Category Index). Several of these sort *before* the abstracts by page number (e.g. page 104166–104401), because CrossRef's page-number field reflects the full issue's layout, not just the abstract section.

Since the task objective is specifically the conference's accepted posters/abstracts, the first 10 entries were selected from the **834-item abstract subset** (sorted by page ascending) rather than literally the first 10 by page number across the mixed issue — the latter would have returned regular articles/editorials that structurally cannot exist in a conference program and would all have failed to match. This selection happened to align exactly with session numbering OR1-1 through OR1-10 (pages 104404–104413, fully contiguous, no gaps).

## Sample Outputs

### Successes

**OR1-1** — *Machine Learning-Enhanced Prediction of Acute Kidney Injury Following Percutaneous Coronary Intervention: An Analysis of the MIMIC-IV Database* (Masab Mansoor et al., DOI 10.1016/j.jscai.2026.104404, Confex Paper/43350)
> Background: Acute Kidney Injury (AKI) is a significant complication following Percutaneous Coronary Intervention (PCI)... We sought to develop and validate a machine learning (ML) model using the MIMIC-IV critical care database...

**OR1-2** — *One-Year Outcomes of Coronary Stenting Versus Conservative Management in Spontaneous Coronary Artery Dissection* (Ali Awad et al., DOI 10.1016/j.jscai.2026.104405, Confex Paper/44517)
> Background: Optimal management of spontaneous coronary artery dissection (SCAD) remains debated. While conservative therapy is generally preferred, coronary stenting is frequently used in selected cases...

**OR1-3** — *Emerging Role of Neurovascular Stent Retrievers in STEMI With High Thrombus Burden* (Vani Malhotra et al., DOI 10.1016/j.jscai.2026.104406, Confex Paper/45534)
> Background: High thrombus burden in STEMI complicates primary PCI and is associated with distal embolization, no-reflow, and impaired myocardial perfusion...

All 10 records include complete CrossRef metadata (DOI, full author list, April 2026 publication date) and a full Background/Methods/Results/Conclusions abstract body extracted from the matched Confex record.

### Failures

None. All 10 target abstracts matched at high confidence (exact session-code + normalized-title match) and yielded complete, structured full text.

Two transient issues were encountered and resolved during the run:
- **OR1-4 and OR1-7** initially returned zero Confex search results on the first pass — a transient issue, not a real absence, since re-running the identical search moments later returned the correct match as the top result. Fixed by adding retry-with-backoff (up to 3 attempts) around the search step; both matched successfully on retry.
- **3 of 10** abstracts (OR1-3, OR1-6, OR1-7) initially extracted a truncated body (only the four section headers, no text) because Confex renders the abstract body in two different HTML structures: some records nest the bold header and body text inside the same `<p>`, while others place the header in its own `<p>` and the body text as a sibling text node directly under the containing `<div>`. The initial parser only handled the first structure. Fixed by rewriting the extractor to walk the section's DOM in document order and group text by the preceding bold header, which handles both structures.

## Recommendations
- When querying CrossRef by volume/issue for a conference-abstract scrape, always inspect the returned title patterns before assuming the whole volume/issue is abstract-only content — supplement issues are frequently mixed with regular editorial content, and blindly taking "the first N by page" can silently pull in non-abstract items that will never resolve against the conference program.
- Confex's own search-filter checkboxes (`GoodType` values) are a reliable, low-cost way to confirm what content types actually exist in a given conference program before committing to a matching strategy.
- The Confex program renders the same logical content (Background/Methods/Results/Conclusions) with at least two different underlying HTML structures for the abstract body; any extraction logic should walk the DOM by document order rather than assuming a fixed nesting pattern.
- Confex's title search occasionally returns zero results transiently even for a title that is confirmed present; treat an empty result set as retryable, not authoritative, before concluding a match failure.

## Limitations
- Only the first 10 of 834 SCAI 2026 abstracts in this issue were processed, per the `max_abstracts` parameter; the remaining ~824 abstracts were not scraped in this run.
- Confex abstract images (e.g. embedded figure/table PNGs referenced inline in some records) were not downloaded or transcribed — only the plain-text abstract body was extracted, per the runbook's text-focused scope.
- `source_page_url` points to the Confex record's own URL (a stable per-paper route), not the CrossRef DOI landing page, since the runbook specifies "the Confex record's own URL... else the CrossRef DOI link" and a stable per-paper Confex URL was available for every matched record.
