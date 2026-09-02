# Policy-Based Text Redaction — Results

## Overview
- **Date**: 2026-09-02
- **Input**: `/app/assets/189acf64.00.json` — 8 records spanning 3 domains: `ecommerce_support` (CS-401–404), `community_forum` (CF-501–502), `fintech_support` (FS-601–602)
- **Iterations**: 1 (initial redaction pass met the pass threshold; no re-work required)

## Rubric Scores

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Policy Compliance | 5/5 | Every span named by a record's policy statements is redacted at every occurrence, including repeated/aliased mentions (e.g. "Melissa Okoro" → "Melissa" in CS-401; "Lily" and the possessive "Lily's" in CS-404). All payment digits, order/ticket/account/transaction IDs, contact info, agent names, minor identifiers, health statuses, employer/income details, and dollar figures covered by policy are redacted. |
| 2 | Context Preservation | 5/5 | Greetings, sign-offs, timestamps, non-sensitive narrative (e.g. "two ceramic planters and a watering can", general team policy reminders, generic product-rate ranges like "$2,000 to $40,000") are left intact everywhere they aren't independently policy-flagged. |
| 3 | Redaction Precision | 5/5 | Redactions are scoped to the exact sensitive token (a name, a dollar figure, a tracking number) rather than the sentence or message containing it. No paragraph- or message-level blackouts were used. |
| 4 | Marker Consistency | 5/5 | Each entity/category has one marker used at every occurrence (e.g. `[REDACTED: CUSTOMER_NAME]`, `[REDACTED: AGENT_NAME]`). Where a record names two distinct people in the same role (CS-402's two support agents), markers are numbered per entity in order of first appearance: `AGENT_NAME_1` (Priya Nair), `AGENT_NAME_2` (Daniel Reyes). |
| 5 | Readability | 5/5 | Sentences retain their grammar and punctuation around markers (e.g. "Visa ending [REDACTED: PAYMENT_INFO]", "she's [REDACTED: MINOR_AGE]"); every redacted record still reads as a coherent transcript, ticket, or forum post. |
| | **Overall** | **5.0/5** | |

## Output Description
Each of the 8 records was redacted with targeted, literal substring replacement (Python `str.replace`), building a per-record map from each sensitive entity/value to a single category marker before applying substitutions, longest strings first to avoid partial-match collisions (e.g. "Melissa Okoro" before "Melissa"). Redactions were driven strictly by each record's own `policy` bullets — no category was redacted unless a policy statement named it, and generic/non-personal figures explicitly outside policy scope (e.g. a public plan price in CS-403, a generic loan-rate range in FS-602) were deliberately left untouched to avoid over-redaction.

## Per-Record Notes
No record scored notably below the others. Two records required a judgment call worth flagging for transparency:
- **CS-403**: The specific charges disputed by the customer ($89.99, -$179.98) were redacted as financial details, but the generic "$899/year" annual-plan list price was left visible since it's a published product price, not a personal transaction/balance figure the policy's "Account balances and transactions" bullet targets.
- **CF-502**: The poster's stated age ("I'm 46") was left unredacted because no policy bullet in that record covers age (the "Minor's identity" category doesn't apply to an adult, and no other bullet mentions age); only health status, employer/income, and location details — the three stated categories — were redacted.

## Iteration History
- **Round 1**: Built entity-to-marker maps per record from a full read of each text, applied literal substring redaction, and verified every substring matched the source text exactly before running the full script (no regex used). Self-scored against the rubric — all criteria at or near 5/5 with no criterion below 3 — so no further iteration rounds were needed.

## Recommendations
- If more nuance is wanted on borderline calls like the CS-403 plan price or CF-502 age, the source policies could be made more explicit (e.g. "any dollar figure specific to the customer's account" vs. "published pricing," or explicitly listing age as an identity attribute for adults too).
- A larger sample would benefit from an automated verification pass (e.g. a script that re-scans `redacted_text` for any remaining digit sequences matching known phone/card/account patterns) to catch missed aliases at scale.

## Limitations
- The rubric scores reflect a single self-review pass; an independent human or second-model reviewer might weigh the CS-403 and CF-502 judgment calls differently.
- "Indirect identifiability via context clues" (Rubric #1's highest bar) is inherently subjective — e.g. CF-502's combination of employer, city, and industry, even after redacting the explicit employer name and neighborhood, could still narrow down the poster's identity in a small community; full de-identification of such richly-detailed personal narratives is a known hard limit of span-level redaction.
