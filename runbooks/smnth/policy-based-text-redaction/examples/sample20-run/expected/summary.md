# Policy-Based Text Redaction — Summary Report

## Overview

This run processed all 20 records in `/app/assets/c4395d52.00.json`, each of which
carries its own `policy` / `policy_ids` describing what categories of information
must be redacted from that record's `text`. For every record, a `redacted_text`
field was produced using literal (non-regex) string substitution, verified against
the exact source text (including embedded newlines and odd whitespace) before
being applied.

Redaction followed three rules throughout:

1. **Only redact what the record's own policy actually covers.** Several records
   carry `policy_ids` that reference categories (e.g. business/financial-services
   boilerplate, unrelated negotiation topics) that do not correspond to anything
   present in that record's `text`. In those cases, no redaction was invented for
   that category — inventing matches would have hurt both Redaction Precision and
   Context Preservation without any compliance benefit.
2. **Every occurrence of the same real-world entity gets the same marker.** Full
   names, first names, nicknames, sign-offs, and email addresses belonging to one
   person were mapped to a single numbered marker (e.g. `[REDACTED: PERSON_1]`),
   assigned in order of first appearance within the record. Markers are scoped
   per-record, not global across the dataset.
3. **Category markers describe the kind of information removed**, not who removed
   it or why (e.g. `SCHEDULE`, `TIMESTAMP`, `LOCATION`, `FINANCIAL`,
   `SUPPLY_VOLUME`, `LEGAL_STRATEGY`, `AFFILIATION`, `RELATIONSHIP`, `ID_NUMBER`,
   `CAPTURE_DETAILS`, `OFFICIAL`, `PROPERTY`, `PROJECT`, `MEETING_TOPIC`,
   `ADDRESS`, `PHONE`, `EMAIL`, `WEBSITE`, `DATE`, `TIME`, `EVENT`, `EMPLOYER`,
   `COMPETITOR`), keeping the sentence structure and surrounding meaning intact.

## Rubric Scores

Scale: 1 (poor) – 5 (excellent). Pass threshold: overall average ≥ 4.0, no
individual criterion below 3.

| Criterion | Overall Average |
|---|---|
| Policy Compliance | 4.85 |
| Context Preservation | 4.60 |
| Redaction Precision | 4.65 |
| Marker Consistency & Clarity | 4.90 |
| Readability | 4.65 |
| **Overall Average** | **4.73** |

**Result: PASS** (overall 4.73 ≥ 4.0; minimum criterion score 4.6 ≥ 3).

### Per-record scores

| ID | Domain-ish topic | PC | CP | RP | MC | R | Avg |
|---|---|---|---|---|---|---|---|
| 1579 | Enron scheduling email | 5 | 5 | 5 | 5 | 5 | 5.00 |
| 1589 | Enron industrial-gas sales email | 5 | 5 | 5 | 5 | 5 | 5.00 |
| 1262 | Meeting notice (climate/emissions) | 5 | 5 | 5 | 5 | 5 | 5.00 |
| 1527 | Personal email (Christmas party) | 5 | 4 | 4 | 5 | 5 | 4.60 |
| 1011 | Short Enron scheduling email | 5 | 5 | 5 | 5 | 5 | 5.00 |
| 1513 | Personal/family email | 5 | 4 | 4 | 5 | 5 | 4.60 |
| 1562 | Bank credit memo | 5 | 5 | 5 | 5 | 5 | 5.00 |
| 1465 | Enron trading email w/ price table | 5 | 5 | 5 | 5 | 5 | 5.00 |
| 1022 | Real-estate partnership email | 5 | 4 | 5 | 5 | 4 | 4.60 |
| 1532 | Personal email (move/reunion) | 5 | 5 | 5 | 5 | 5 | 5.00 |
| 1482 | Enron scheduling email | 5 | 5 | 5 | 5 | 5 | 5.00 |
| 1140 | Legal correspondence | 5 | 5 | 5 | 5 | 5 | 5.00 |
| 820 | State Dept. diplomatic email chain | 5 | 4 | 4 | 5 | 4 | 4.40 |
| 849 | OCR-garbled incident report | 4 | 4 | 4 | 4 | 3 | 3.80 |
| 784 | Journalist-capture briefing email | 5 | 4 | 5 | 5 | 4 | 4.60 |
| 938 | Diplomatic scheduling email | 5 | 4 | 4 | 5 | 4 | 4.40 |
| 966 | Short internal note | 4 | 4 | 4 | 4 | 4 | 4.00 |
| 443 | No policy-matching content | 4 | 5 | 4 | 5 | 5 | 4.60 |
| 16 | Survey / persona interviews | 5 | 5 | 5 | 5 | 5 | 5.00 |
| 119 | Personal reflection essay | 5 | 5 | 5 | 5 | 5 | 5.00 |

## Per-Record Notes

- **1579, 1589, 1262, 1011, 1482, 1140, 1532, 1465, 1562, 16, 119** — Clean
  business/legal/personal correspondence with clearly identifiable entities and
  categories. All policy-covered names, timestamps, schedules, locations,
  financial figures, and contact details were redacted with consistent numbered
  markers. Record 16 required special handling: two of its four personas
  ("Person A" and "Person B") share the literal first name "Vincenzo". A single
  global string replace would have collapsed them into one marker, so each
  persona's `Name:` field was redacted independently within its own text segment
  (bounded by the "Person A/B/C/D" headers), correctly yielding four distinct
  markers.
- **1527, 1513** — Personal emails with informal register. Context Preservation
  and Redaction Precision scored 4 rather than 5 because some casual
  conversational context (e.g. banter, filler) sits very close to redacted spans,
  making the redacted version slightly more clipped than the fully clean
  business emails, though still fully readable.
- **1022** — Multi-party real-estate discussion; 5 distinct people and a
  property name were redacted with correct per-entity numbering. Readability
  dips slightly (4) because the underlying email itself is a run-on, informal
  message.
- **820, 938** — Complex diplomatic email chains with many participants (9 and 7
  respectively). All named individuals were mapped to consistent numbered
  markers, including nickname/initials forms (e.g. "Alec" → same marker as "Alec
  Ross"; "Cdm" → same marker as "Cheryl D. Mills"; "Pat"/"Dan" → same markers as
  their full-name forms). Context Preservation and Readability scored 4 because
  these are long forwarded chains with many redacted spans in close proximity,
  which necessarily reduces flow compared to shorter records, though the
  redactions themselves are precise.
- **849** — Source text is heavily OCR-garbled (broken words, stray characters
  like ".IB", inconsistent spacing) independent of any redaction performed.
  Dates, times, the incident location, and the "ACS Chief" role were redacted
  per policy; ambiguous garbled fragments were deliberately left untouched
  rather than guessing at their meaning, since incorrect redaction of
  unidentifiable text would misrepresent confidence in the source. This is the
  lowest-scoring record, driven primarily by Readability (3), which reflects
  the poor quality of the underlying OCR text rather than any redaction defect.
- **784** — Briefing email about a journalist's capture. Fixed during review:
  the header alias "sbwhoeop" was initially missed and left unredacted even
  though it refers to the same person as "Sid" elsewhere in the record; it now
  maps to the same `PERSON_2` marker. Affiliations, a relationship reference,
  and capture circumstances were redacted per policy while preserving the
  narrative.
- **966** — Very short note with ambiguous two-letter initials ("MS", "PIR")
  used as stand-ins for named individuals. Redacted as distinct people since
  they appear as addressee/signer, but the extreme brevity of the record limits
  how much can be verified from context, capping several criteria at 4.
- **443** — No content in the text corresponds to any category referenced by
  this record's `policy_ids`; the text discusses topics unrelated to the policy's
  stated redaction categories. No redaction was applied. Policy Compliance is
  scored 4 rather than 5 to reflect that this is a judgment call (absence of
  matching content vs. a missed redaction) rather than a clear-cut case, though
  review confirmed no policy-relevant spans exist in the text.

## Iteration History

**Round 1 (initial pass):** Built a per-record entity map and applied literal
string replacements for every record, covering all `policy_ids`-relevant
categories identified by reading each record's full policy text and body text.

**Round 1 refinement (same round, before formal scoring):** A full manual
line-by-line review of the entire redacted dataset caught four residual issues,
all fixed before formal rubric scoring:
1. Record 1562 — a bare `"82"` (an account/ID number per the "Name and ID
   number pair" policy clause) was left unredacted next to the redacted name;
   added an anchored replacement to catch it as `[REDACTED: ID_NUMBER]`.
2. Record 784 — the header alias `"sbwhoeop"` referred to the same person as
   `"Sid"` but wasn't mapped to that person's marker; fixed so both map to
   `PERSON_2`.
3. Record 938 — the initials `"Cdm"` (Cheryl D. Mills) appeared unredacted on
   their own line; mapped to the existing `PERSON_3` marker used for her full
   name elsewhere in the record.
4. Record 16 — names were entirely unredacted in the first pass; added
   segment-based redaction so each of the four personas gets its own numbered
   marker, correctly disambiguating the two personas who share the first name
   "Vincenzo".

After these fixes, `redact.py` was re-run cleanly with no "substring not found"
warnings, and the fixes were individually verified against the output JSON.

**Formal scoring (this round):** Overall average 4.73, minimum per-criterion
average 4.60 — both comfortably above the pass threshold (≥4.0 overall, no
criterion <3). No further iteration rounds were required.

## Recommendations

- For OCR-garbled source records (e.g. 849, and to a lesser extent 938), a
  pre-cleaning/OCR-correction pass before redaction would improve both
  Readability and confidence in Redaction Precision, since some garbled
  fragments could plausibly contain policy-relevant information that isn't
  currently identifiable with certainty.
- Records whose `policy_ids` don't correspond to any content in the `text`
  (443, and partially 1589/820/16) suggest the policy-tagging step upstream of
  this pipeline may be over-broad or misaligned with per-record content; a
  content-vs-policy consistency check earlier in the pipeline would reduce
  ambiguity in cases like these.
- Two-letter initials used as identifiers (record 966's "MS"/"PIR") are
  inherently harder to verify against source-of-truth identities than full
  names; flagging such low-confidence entity redactions for human review would
  be a reasonable enhancement to this workflow.

## Limitations

- Redaction was performed via literal substring matching against the exact
  source text; it does not generalize to variant spellings, misspellings, or
  entities not explicitly identified during review.
- For heavily corrupted/OCR-garbled records (849, 938), some ambiguous
  fragments were deliberately left unredacted rather than guessed at; this
  is a conservative choice that could under-redact if those fragments do in
  fact contain policy-relevant information.
- Record 443 was left fully unredacted because no content matching its stated
  policy categories was found in the text; this is a judgment call rather than
  an algorithmically certain determination.
- Scoring in this report is a structured self-assessment performed during
  manual review of all 20 redacted records, not an automated or
  third-party-audited score.
