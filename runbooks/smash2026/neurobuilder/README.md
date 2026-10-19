# NeuroBuilder: Auditable Agentic Data Curation for Neuro-Foundation Models

Ghazaleh Ranjbaran, Mahta Ramezanian-Panahi, Blake Aaron Richards, Irina Rish · SMASH 2026 (Poster) · [Paper](https://drive.google.com/file/d/1JcxkbnVGhv_uG7abJyyeSVieJcvPzgCs/view?usp=sharing)

> We present NeuroBuilder, an agentic adaptation workflow that combines semantic reasoning with deterministic extraction, validation, provenance, and execution controls while reserving consequential decisions for researchers. TUEG received a full pass with zero fabricated events.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

The agent indexed 50 of 50 recordings and surfaced 7 of 7 planted conflicts. Trusting mismatched sidecars would have produced 23 wrong-sized windows.

- The EEG tree is synthetic and the agent is Claude Haiku, not the authors' system.
- Human checkpoints were auto-approved.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
