# From Canon to Nikon: Camera Domain Shift and Potential Equity Implications in Retinal AI

Lisa Y.W. Tang · SMASH 2026 (Poster) · [Paper](https://drive.google.com/file/d/1cEMU7Sho9vz6uA6rD2xq78R9KDpaOwuK/view?usp=sharing)

> In a Brazilian cohort of 8,524 patients, retinal images acquired with the Nikon NF5050 were more than twice as likely to have inadequate image quality compared with those acquired with the Canon CR-2, despite refurbished Canon systems costing more than twice as much as Nikon systems. We find that camera-associated performance differences vary substantially across tasks, and that neither higher input resolution nor classifier choice consistently mitigates cross-camera variation.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

With R$1,900,000 for 40 sites, all-Nikon covers every site and misses 955 cases a year, against 2,431 for all-Canon on 20 sites. Diabetic retinopathy AUROC holds across cameras (0.940 vs 0.946).

- Model performance is transcribed from the paper's Table 4; the screening calculator is an extension.
- Camera type is confounded with case mix and site in the source cohort.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
