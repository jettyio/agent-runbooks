# Tracing Bias Propagation Across Subgroups in Federated Learning

Tirathraj Ramburn, Afaf Taïk, Farnoosh Ghadiri · SMASH 2026 (Spotlight) · [Paper](https://drive.google.com/file/d/1aA6Fac9mYYJa1VoylGh4o3GgjQjDeobk/view?usp=sharing)

> We show that the impact of false-negative errors on recipient client–subgroup pairs can be predicted from the global model's curvature together with source and recipient-group feature summaries, without retraining a model for each possible error. Notably, a non-target subgroup can experience the largest degradation.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

Mislabelling 30% of A1-B3's positives hurts A1-B4 most, 17.1% more than A1-B3 itself. The closed-form prediction matches the retrained ranking at Spearman 0.980.

- Synthetic data from the paper's generator.
- Logistic regression only, as in the paper.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
