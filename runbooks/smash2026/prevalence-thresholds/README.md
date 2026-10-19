# Prevalence, Thresholds, and Subgroup Performance Gaps in Clinical Prediction Models Across Five Public Datasets

Zavash Ghorbanpourbaboli, Arina Afshar, Elham Jangravi, Mohammed Ayoub Alaoui Mhamdi, Russell Butler · SMASH 2026 (Poster) · [Paper](https://drive.google.com/file/d/1MnK-mFUFDe2Josf706Rgn4RxZMB6df3M/view?usp=sharing)

> Clinical prediction models are commonly compared across demographic subgroups, but a raw performance gap is not a fixed property of a model. Observed gaps should prompt investigation of metric choice, prevalence, threshold, sample composition, measured case mix, and uncertainty rather than being treated alone as proof of discrimination, fairness, or equivalence.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

With the paper's specification, the Diabetes-130 youngest-minus-oldest sensitivity gap is +0.120 [−0.057, +0.235]; the paper reports +0.104. 19 of 36 alternative analysis choices give a negative gap.

- Model hyperparameters and variable encodings are this runbook's; the predictor set and age bands follow the paper.
- No fairness verdict is implied.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
