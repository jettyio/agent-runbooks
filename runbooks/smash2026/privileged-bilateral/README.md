# Two for One: Privileged Bilateral Learning for Monocular Retinal Disease Classification

Lisa Y.W. Tang · SMASH 2026 (Spotlight) · [Paper](https://drive.google.com/file/d/1RKzJvGv1_Avf2kqHYQFnlwnWD78wedUW/)

> We thus propose a privileged learning framework in which a teacher model has access to bilateral CFP images during training and learns representations informed by information from both eyes, while the student is trained to transfer this knowledge from the bilateral teacher using only a single-eye image as input. At inference, the student operates exclusively on this single-eye input and does not require the contralateral image.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

The student beat the single-eye baseline in 8 of 10 simulated cohorts (mean +0.024 AUROC). On the one split shown in detail it scored slightly lower (0.711 vs 0.702).

- Simulated eye features replace fundus photographs.
- A small MLP replaces RETFound-Green.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
