# Gated Knowledge-Guided Prototype Transfer for Zero-Support Medical Vision Language Model

Sumaiya Fazal, Rizwan Qureshi, Laleh Behjat, Samira Ebrahimi Kahou · SMASH 2026 (Poster) · [Paper](https://drive.google.com/file/d/1TNzjU8LBvL9_Vo73FUBv9Oouxrt2rDfI/view?usp=sharing)

> We introduce gated Knowledge-Guided Prototype Transfer (KGPT), a pre-repulsion module that transfers supported-class visual residuals to missing classes using VLM similarity and an ontology-based clinical distance. A validation-free evidence gate scales transfer based on semantic relevance and residual agreement, thereby limiting unsupported extrapolation.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

Ungated transfer made a missing grade worse in 46–50% of support draws. The gate cut that to 16% and added +2.37 points of missing-class recall.

- Synthetic embeddings stand in for MESSIDOR with FLAIR features.
- SS-Text+ is approximated with a shrinkage-plus-repulsion prototype.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
