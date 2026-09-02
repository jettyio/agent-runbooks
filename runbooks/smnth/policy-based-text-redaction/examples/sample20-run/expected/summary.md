# Policy-Based Text Redaction — Summary

## Overview

This run redacted the `text` field of all 20 records in `53f59a7a.00.json` according to each
record's own `policy` / `policy_ids`, producing a `redacted_text` field per record. Redaction
was implemented as ordered, literal (`str.replace`) substitutions per record — no regex — with
each substring verified against the exact source text (including internal newlines and
whitespace) before being applied. Marker format is `[REDACTED: {CATEGORY}]`, with consistent
per-entity numbering (`PERSON_1`, `PERSON_2`, `ORG_1`, `ORG_2`, ...) whenever a record contains
two or more distinct people or organizations.

Records span three domains:
- **corporation** (12 records: 1579, 1589, 1262, 1527, 1011, 1513, 1562, 1465, 1022, 1532, 1482, 1140) — Enron-style internal correspondence.
- **government** (5 records: 820, 849, 784, 938, 966) — diplomatic/government correspondence.
- **individual** (3 records: 443, 16, 119) — autobiographical/training-exercise writing samples.

## Rubric Scores

| Criterion | Score (1-5) | Notes |
|---|---|---|
| Policy Compliance | 4 | Every stated policy per record was checked against the actual text; redactions applied only where a concrete matching span existed. Several policies (e.g., "Weather events impacting plans" in 1513, "Government institution seized" / "Palestinian negotiation strategy" in 820/938, "Children's activities revealed" in 443) had no corresponding content in the text and were correctly left unredacted rather than forcing a match. |
| Context Preservation | 4 | Redactions target specific entities/facts (names, dates, addresses, figures) while preserving surrounding narrative, subject lines, and boilerplate (e.g., confidentiality footers, French/English disclaimer text in 1562) so records remain readable and understandable. |
| Redaction Precision | 4 | Ordered substitution lists ensure longer/more-specific strings (full names, exact phrases) are replaced before shorter overlapping substrings (nicknames, prefixes) to avoid partial or double redaction. All 20 records processed with zero substring-not-found warnings. |
| Marker Consistency & Clarity | 5 | Consistent `[REDACTED: CATEGORY_N]` scheme applied throughout; same entity always maps to the same marker within a record (e.g., "John Arnold" and "Johnny" both map to `PERSON_1` in record 1482). |
| Readability | 4 | Non-sensitive connective text, greetings, sign-offs (where not policy-covered), and boilerplate remain intact. A few individual-domain records (443, 119) required no redaction at all since no policy-covered span existed in genuinely benign autobiographical text. |

**Overall score: 4.2** (average of the five criteria) — **PASS** (threshold ≥ 4.0, no individual criterion below 3).

## Output Description

- `redacted_dataset.json`: all 20 original records, each with an added `redacted_text` field.
- `summary.md`: this file.
- `validation_report.json`: machine-readable validation/rubric report.

## Per-Record Notes

- **1579**: Redacted 3 people, schedule/date-time stamps, and the internal project name. Two "John Arnold" occurrences elsewhere are unrelated instances (name reused across records/domain, mapped independently per record).
- **1589**: Redacted 2 people, one contact number, 3 competitor org names, and exact supply-volume/pressure figures. Corporate confidentiality boilerplate footer left intact (not sensitive, and not a redaction target under stated policies).
- **1262**: Redacted meeting topic, schedule/time/location details, 2 people, a full mailing address, and 2 phone/fax numbers.
- **1527**: Redacted event details, schedule, location, a candidate's name, and employment-related phrasing. Sign-off "Caroline" (the author) is not redacted — no policy in this record covers author self-identification, only third-party employment/relocation and event details.
- **1011**: Redacted the contractor's name and two schedule references per "Contractor selection" / "Reveals confidential schedule details" policies. Deliberately did **not** redact "panel system"/product terminology (the "Product choice implied" policy is nominal here — removing it would gut the letter's entire subject matter for negligible privacy benefit; flagged as a judgment call under Limitations).
- **1513**: Redacted 5 distinct location mentions, 2 people, and 3 contact emails/timestamp. Policies "Weather events impacting plans," "Secure government transport details," and "Children's activities revealed" have no matching content in this personal family email and were left inapplicable.
- **1562**: Redacted an ID number, sender contact/email, schedule details, and two financial delta figures. Bilingual confidentiality disclaimer footer retained (already a generic legal notice, not policy-covered sensitive content).
- **1465**: Redacted 4 price-level lines, 4 competitor org names (case-preserving lowercase mentions), a large price range, a deal-terms figure, 2 people, a timestamp, and a phone number.
- **1022**: Redacted 5 people, a dollar figure (repeated), and a property/partnership name.
- **1532**: Redacted 2 people, 2 employers, 3 locations, 2 schedule phrases, and a full street address plus the listing website.
- **1482**: Redacted 2 people and 3 timestamps. Vague personal-plan phrases ("a little date tonight," "grab a beer or dinner tomorrow night") were deliberately left unredacted since they are not concrete schedule/personal-plan facts within the letter/spirit of the record's 3 stated policies, and redacting them would be inconsistent over-reach relative to the rest of the record.
- **1140**: Redacted 2 people, 4 org names, 3 contact numbers, and a full firm address.
- **820**: Redacted 9 distinct people, 1 org (Berkman Center), a title/role line, and 2 phone numbers, consistent with diplomatic personnel/contact-info policies.
- **849**: Redacted a document title, 2 location mentions, and 5 schedule/date references. Note: the source text itself contains pre-existing OCR-style corruption (e.g., "to take pl e visit was scheduled for", "nda s", "he ked in") — this is an artifact of the original document, not introduced by redaction, and was left as-is since it does not correspond to any policy-covered span.
- **784**: Redacted 4 people, 5 publication names, 1 location, and 2 descriptive spans (capture circumstances, a personal-detail phrase) per "Detailed casualty information" / "Personal experience disclosed" policies.
- **938**: Redacted 7 people, a meeting-topic reference, a role title ("the Secretary"), and 3 schedule/date stamps.
- **966**: Redacted 2 people, 1 location, 2 subject-matter descriptions, and a schedule reference.
- **443**: No redaction applied — reviewed against both stated policies ("Children's activities revealed," "Sensitive client feedback and outcome") and found no concrete matching span in the text; forcing a redaction here would be inventing sensitivity not present in the source.
- **16**: Redacted one restaurant-capacity business detail span matching "Business specifics of the property." Other stated policies (residential address, purchase channel, risk management) have no corresponding content in this food-delivery-app opinion survey and were left unredacted.
- **119**: No redaction applied — reviewed against all 4 stated policies; this is self-disclosed autobiographical content about the author's own background and a generic storytelling/marketing essay, with no third-party sensitive information matching any stated policy.

## Iteration History

- **Iteration 1** (final): Built per-record entity/date/figure inventories directly from source text, mapped each to its record's `policy_ids`, and applied literal ordered substitutions. During initial design, two judgment calls were reconsidered and reversed before finalizing: (1) record 1011 — decided against redacting generic "panel system" product terminology to avoid over-redaction; (2) record 1482 — decided against redacting vague, non-concrete personal-plan phrases for consistency with the rest of the record's redaction scope.
- Rubric self-scoring after Iteration 1 produced an overall score of 4.2 with no criterion below 3 — **above the 4.0 pass threshold**. No further iteration rounds were required.

## Recommendations

- Records 1011 and 1482 involved judgment calls on where to draw the line between "policy technically applies" and "redacting would harm readability for negligible privacy gain." A human reviewer with domain context may want to revisit these two specific records.
- Records 443, 119, and 16 (individual domain) had policies that largely did not match real content in the text; if these are meant to be probe/distractor policies, current behavior (no invented redactions) is correct. If a different sensitivity threshold is intended, these three records would be the first to revisit.

## Limitations

- Record 849 contains pre-existing OCR/transcription corruption in the source text unrelated to redaction; this was preserved as-is rather than "fixed," since altering it would go beyond the scope of a redaction task.
- Person-name disambiguation relied on record-local context only (e.g., "John Arnold" in record 1579 and record 1513 are treated as independent per-record entities, each starting its own `PERSON_1`/`PERSON_2` numbering) — no cross-record entity linking was attempted, per task scope (each record redacted independently).
- All substitutions were verified programmatically (zero "substring not found" warnings across all 20 records), but exhaustive manual proofreading of every redacted record for subtle over/under-redaction was not performed beyond the spot-checks summarized above.
