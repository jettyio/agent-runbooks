# From Extraction Accuracy to Clinical Usefulness: A Human-Centered Evaluation Framework for Source-Traceable Patient Summaries

Alissa Taylor · SMASH 2026 (Poster) · [Paper](https://drive.google.com/file/d/10P_qlRn02fwt-f2id3gu_oRUfPCTcpgr/view?usp=sharing) · [Poster](https://drive.google.com/file/d/1A4N0VZEXDosqmlJZZc1wSjLLjtV0m9p1/view?usp=sharing)

> A fact can be extracted correctly and still mislead if it is presented without temporal context, detached from its source, merged with conflicting information, or rewritten in a way that changes perceived urgency, certainty, or relevance. The framework combines deterministic checks, review of clinical meaning, and task-based evaluation of how users interpret and verify summaries …

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

An LLM judge scored a summary 9/10 while the contradiction gate blocked it: two conflicting HbA1c values (7.2% and 8.1%) had been reduced to one.

- The patient pack is synthetic, written for this runbook.
- Gates are simplified lexical checks.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
