# Conference Abstract Scraper — Results

## Overview
- **Date**: 2026-08-19T21:50:06Z
- **Source URL**: https://www.jscai.org/issue/S2772-9303(26)X2005-1
- **Conference**: SCAI 2026 Scientific Sessions (Montreal, April 23-26, 2026)
- **Journal**: Journal of the Society for Cardiovascular Angiography & Interventions (JSCAI), Vol. 5, Issue 4S
- **Abstracts requested**: 20
- **Abstracts processed**: 20

## Results Summary

| Status | Count | % |
|--------|-------|---|
| PASS | 19 | 95.0% |
| PARTIAL | 1 | 5.0% |
| FAIL | 0 | 0.0% |

## Completeness Check
- Entries discovered via CrossRef (page-ordered supplement issue): 830
- First 20 entries selected by article page number (issue TOC order): 20
- Entries in final output: 20
- Duplicate/merge conflicts detected: 0

## Data Sources Used
1. **Article discovery & ordering**: CrossRef API (ISSN 2772-9303, Vol 5 Issue 4, sorted by article page number = issue TOC order)
2. **Abstract full text (19/20)**: SCAI Confex meeting program (scai.confex.com/scai/2026/meetingapp.cgi) — pre-publication versions matching published content
3. **Abstract full text (1/20 partial)**: OpenAlex inverted index — truncated (Background intro only, 273 chars)
4. **Metadata**: CrossRef API (authors, DOI, publication date)

> **Note**: jscai.org and sciencedirect.com were blocked by Cloudflare IP-level restrictions (Error 1000) preventing direct scraping. The Confex academic program provided equivalent abstract content for 19 of 20 entries.

## Sample Outputs

### Successes
**OR1-1 | Machine Learning-Enhanced Prediction of Acute Kidney Injury Following Pe**
- Session code: OR1-1
- DOI: https://doi.org/10.1016/j.jscai.2026.104404
- Authors: Masab Mansoor
- Date: 2026-04
- Text: Background:  Acute Kidney Injury (AKI) is a significant complication following Percutaneous Coronary Intervention (PCI), particularly in critically ill populations. Traditional risk stratification oft...

**OR1-2 | One-Year Outcomes of Coronary Stenting Versus Conservative Management in**
- Session code: OR1-2
- DOI: https://doi.org/10.1016/j.jscai.2026.104405
- Authors: Ali Awad, Qusai Alqudah, Ali Alramadan
- Date: 2026-04
- Text: Background Optimal management of spontaneous coronary artery dissection (SCAD) remains debated. While conservative therapy is generally preferred, coronary stenting is frequently used in selected case...

**OR1-3 | Emerging Role of Neurovascular Stent Retrievers in STEMI With High Throm**
- Session code: OR1-3
- DOI: https://doi.org/10.1016/j.jscai.2026.104406
- Authors: Vani Malhotra, Hema Gedela, Mohammed Amaanullah
- Date: 2026-04
- Text: Background High thrombus burden in STEMI complicates primary PCI and is associated with distal embolization, no-reflow, and impaired myocardial perfusion. Manual aspiration thrombectomy has not demons...



### Partial / Failures
**OR1-18 | Selective Serotonin Reuptake Inhibitors and Bleeding Risk in Patients U**
- Status: PARTIAL
- DOI: https://doi.org/10.1016/j.jscai.2026.104420
- Text available: 273 chars (truncated — full text blocked on jscai.org)



## Recommendations
- To recover the full OR1-18 abstract: access jscai.org from an IP not on Cloudflare's blocklist, or use an institutional access account
- All 19 PASS entries contain complete Background → Methods → Results → Conclusions abstract text from the SCAI Confex program
- The Confex program text is the pre-publication abstract; it matches the published JSCAI version with possible minor editorial edits

## Limitations
- jscai.org and sciencedirect.com not accessible from this environment (Cloudflare Error 1000 — IP blocked)
- Full text sourced from Confex (pre-publication) rather than the JSCAI published version; minor editorial differences possible
- OR1-18 (SSRI/Bleeding Risk) abstract is truncated (273 chars vs 1500-2200 chars typical) — only the introductory sentence available
- OR1-11 (In-Stent Restenosis) is absent from the issue between page 104413 (OR1-10) and 104414 (OR1-12) in CrossRef; likely withdrawn from publication
