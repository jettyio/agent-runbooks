# Conference abstract scraper (Jetty runbook)

**Turn a conference supplement issue into clean, searchable JSON.** Point it at a journal
ISSN + volume/issue and the conference's own Confex meeting program, and it produces one
structured record per accepted abstract — DOI, authors, publication date, issue ordering,
and the full abstract text — with a completeness check that guarantees nothing is skipped,
merged, or duplicated.

Two sources by design:

- **CrossRef** for canonical metadata and page-number ordering (no API key).
- **The conference's Confex program** for full text — publisher sites (jscai.org,
  sciencedirect.com, …) sit behind a Cloudflare/WAF block that has no per-page workaround,
  while the conference's own program is open and carries the same pre-publication text.

## Flow

1. **Discover** — query CrossRef for the issue, sort by page number, take the first N.
2. **Extract** — open the Confex program with Playwright, match each title (normalized),
   read the full abstract body and the program's internal record id.
3. **Evaluate** — PASS / PARTIAL / FAIL per abstract, plus a batch completeness check
   (count, no duplicate ids/DOIs, every discovered entry present exactly once).
4. **Iterate** — up to 3 rounds on failures, then write the summary and validation report.

## Deliverables (`{{results_dir}}/`)

| File | What |
|------|------|
| `abstracts.json` | One object per abstract: `abstract_id`, `title`, `conference`, `doi_or_url`, `authors`, `publication_date`, `full_text`, `source_page_url`, `confex_paper_id` |
| `summary.md` | Results breakdown, completeness check, sample successes/failures |
| `validation_report.json` | Stage results, per-status counts, `overall_passed` |

## Parameters

`crossref_issn` · `crossref_volume_issue` · `confex_program_url` · `max_abstracts` —
defaults target the SCAI 2026 Scientific Sessions supplement (JSCAI vol. 5, issue 4).

## Examples

See `examples/` — real runs on Jetty (`volpiglio` collection) with the run's inputs,
`expected/` outputs, `trajectory.json`, and a thumbnail. Confex session names and program
URLs are conference- and year-specific; check the conference's public program page when
targeting a different event.
