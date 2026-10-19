# Diagnosing Low-Confidence Patient Profiles via Localized Harmful Covariate Shift Detection

Olivier Lefebvre, Hakima Laribi, Dan Poenaru, Martin Vallières · SMASH 2026 (Poster) · [Paper](https://doi.org/10.48550/arXiv.2610.19178)

> MED3pa first discovers interpretable low-confidence patient profiles, and Detectron is then applied within each profile to test whether its degradation is associated with a detectable harmful covariate shift. An injected age shift, undetectable at the population level, was nonetheless localized to specific degraded profiles …

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

The age shift was missed at population level (p = 0.19). Two of five profiles were flagged; in the largest, AUC fell from 0.69 to 0.64.

- A synthetic MIMIC-like cohort replaces MIMIC-IV.
- Detectron is simplified; borderline profiles change with the seed.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
