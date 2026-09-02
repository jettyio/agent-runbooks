# Policy-Based Text Redaction — Results

## Overview
- **Date**: 2026-09-02
- **Input**: `/app/assets/fc8a7a86.00.json` — 10 records spanning healthcare (4: HC-101, HC-102, HC-103, HC-104), education (3: ED-201, ED-202, ED-203), and legal (3: LG-301, LG-302, LG-303) domains
- **Iterations**: 1 (redaction was authored per-record against each record's specific stated policies and passed the rubric threshold on the first pass; no re-work rounds were needed)

## Rubric Scores

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Policy Compliance | 5/5 | Every span covered by a record's stated policy bullets (PHI, schedule/appointment details, staff/party/witness/minor identity, financial figures, personal contact info, disciplinary/academic records, privileged strategy) is redacted, including repeat mentions under different forms (e.g. full name then first name only, "Thursday" recurring after the full date). Verified programmatically against a leak list of every sensitive term from the source texts — no leaks found. |
| 2 | Context Preservation | 5/5 | Greetings, sign-offs, institution/employer names, job-role descriptions, and explicitly non-sensitive general-policy statements (e.g. "late field logs lose one letter grade per week," "that is public information you may share with anyone") are left intact, preserving document flow and intent. |
| 3 | Redaction Precision | 4/5 | Nearly all redactions are scoped to the minimal sensitive token (a name, date, dollar figure, or phone number). Two legal-memo records (LG-301, LG-303) have a couple of full-sentence `[REDACTED: PRIVILEGED_STRATEGY]` blocks because the entire sentence *is* a case-strength assessment or piece of legal advice, not an isolated detail inside a longer sentence — a narrower span would misrepresent the sentence as non-strategic. This is a defensible but slightly broader-than-minimal redaction, so it's marked down slightly rather than scored a full 5. |
| 4 | Marker Consistency | 5/5 | Each entity maps to exactly one category marker throughout its record, and records with 2+ distinct people/parties use numbered markers (`STAFF_1`/`STAFF_2`/`STAFF_3`, `MINOR_1`/`MINOR_2`, `EMPLOYEE_1`/`EMPLOYEE_2`, `WITNESS_1`/`WITNESS_2`) so who-said-what-to-whom stays traceable without re-identifying anyone. |
| 5 | Readability | 5/5 | Every redacted record was re-read in place of the original spans; sentences remain grammatically sound (e.g. "switching him from [REDACTED: MEDICATION] to [REDACTED: MEDICATION]," "scheduled for [REDACTED: SCHEDULE]") and the documents read as coherent, if de-identified, versions of the originals. |
| | **Overall** | **4.8/5** | |

## Output Description
Each record's `redacted_text` was hand-authored directly against that record's own `policy` bullets rather than run through a generic pattern-matching pass — this let categories track exactly what each record's policy_ids named (e.g. HC-104 has no "staff identity" policy, so its treating physician's name was deliberately left unredacted, while HC-101 and HC-103 do have that policy and redact clinician names). Institutional identifiers (hospital, school, and company names) were kept throughout, since none of the ten records' policies flag organization identity — only person names, contact/location details, schedules, financial figures, and the specific categories of sensitive content (PHI, disciplinary records, academic performance, privileged legal strategy) named in each record's own policy bullets were redacted.

## Per-Record Notes
- **LG-301** and **LG-303** score slightly lower on Redaction Precision: both contain sentences where a legal-strength assessment and the advice built on it are inseparable from the sentence structure, so the whole clause (not just a name or figure) was replaced with `[REDACTED: PRIVILEGED_STRATEGY]`. This was a deliberate choice — narrowing the span further would have left a strategic judgment ("weak on damages," "expect he will return the full deposit") exposed in plain text, which is exactly what the privileged-strategy policy prohibits.
- All other records (HC-101–104, ED-201–203, LG-302) scored uniformly well across all five criteria with no notable weaknesses.

## Iteration History
- **Round 1 (final)**: Parsed each record's policy bullets individually, built a per-record entity→marker map (numbering markers when a record named 2+ distinct people/parties), and hand-redacted each record's text preserving structure, greetings, and non-policy-flagged general statements. Verified with an automated leak check (searching for every sensitive name, number, date, and address from the source text inside the corresponding `redacted_text`) — zero leaks detected on the first pass, so no further rounds were needed.

## Recommendations
- If further iteration were pursued, the two `PRIVILEGED_STRATEGY` full-sentence redactions in LG-301/LG-303 could be split into smaller phrase-level redactions (e.g. redacting just "strong on liability but weak on damages" rather than the full clause) to push Redaction Precision closer to a full 5, at a small risk of leaving a fragment of the assessment's tone visible.
- Upstream, policies that mix identity categories (e.g. "Staff identity" using healthcare-style clinician language even when applied to school staff) could be worded more generically across domains to reduce the need for domain-specific interpretation when deciding whether a rule extends to non-obvious roles (e.g. whether "witness" also covers a listed corroborating coworker who wasn't in a lawsuit).

## Limitations
- The rubric does not score whether the *choice* of category label (e.g. `PHI` vs. a more specific `PHARMACY_LOCATION`) is optimal — labels were chosen for clarity and consistency but a different reasonable labeling scheme could also satisfy Marker Consistency.
- Several redaction decisions were judgment calls where a record's policy bullets were silent on a borderline detail (e.g. whether "insurance changed in September" in HC-101 counts as a schedule detail, or whether a pharmacy name in HC-104 falls under PHI treatment-plan disclosure absent an explicit "physical location" policy for that record). These were resolved by hewing to the literal scope of each record's stated policy bullets rather than by a domain-wide default, and a human reviewer familiar with the underlying compliance intent may reasonably redraw a few of these boundaries.
