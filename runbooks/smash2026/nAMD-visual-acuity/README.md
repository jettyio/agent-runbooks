# Visual Acuity Improvement Prediction in Neovascular Age-Related Macular Degeneration

Hadi Moazen, Mélanie Hébert, Alaa Eddine Ayadi, Ali Dirani, Audrey Durand · SMASH 2026 (Poster) · [Paper](https://drive.google.com/file/d/1h81k0dJvGwdnHFxP-kYIcjuwFZgX_n1d/view)

> We proposed a predictive pipeline that automates the extraction of clinical OCT biomarkers using fine-tuned DL models. The combination of these automated biomarkers with baseline best-corrected visual acuity serves as inputs for an interpretable classifier.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

For a simulated patient with BCVA 50 and SRF present, the model gives a 51% chance of gaining 10 or more letters. A misread SRF flag lowers it to 33%.

- The 1,203 eyes are simulated from the paper's reported marginals.
- Not for clinical use.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
