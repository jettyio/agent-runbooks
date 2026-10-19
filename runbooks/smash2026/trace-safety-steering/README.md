# TRACE: Temporal Risk Assessment and Concept Editing for Safer Language Generation

Ankur Garg, Xuemin Yu, Hassan Sajjad, Samira Ebrahimi Kahou · SMASH 2026 (Poster) · [Paper](https://github.com/agarg-dev/TRACE/blob/0d45d7e5a5e30399eeafd0e2a41c55ae8ae8288d/TRACE.pdf) · [Full version](https://arxiv.org/abs/2610.15365)

> TRACE learns a codebook of recurring activation patterns and assigns each token activation to its nearest codebook vector, defining a latent concept. During steering, activations assigned to harmful concepts are steered along directions defined by nearby benign targets.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

Streaming F1 0.96 for TRACE vs 0.61 for DiffMean. Steering lowers the attack-success analog from 0.94 to 0.18 with no change in refusals; a global refusal direction reaches 0.00 but adds 0.46 refusals.

- Activations are simulated; no language model is run.
- The codebook and GRU detector are simplified stand-ins for the paper's trained components.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
