# Towards Robust, Performance-Based Contamination Detection for LLMs

Allenna Tang, Jackie Cheung · SMASH 2026 (Poster) · [Paper](https://drive.google.com/file/d/1eG9T_MAj1dUJLBNzRlAUpSu32xIt5zom/view?usp=sharing)

> Our evasion is an argmax-preserving logit transform that makes signals on contaminated items resemble those on unseen items, while leaving every benchmark answer unchanged. We then introduce a detector based on Item Response Theory (IRT) residuals, which calibrates item difficulty on a population of 102 LLMs and flags items where a model outperforms its estimated ability. Because it reads only binary responses, its AUROC is exactly unchanged under the evasion.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

The evasion drops the confidence detectors from 1.00 to 0.52 AUROC without changing an answer. The IRT residual detector stays at 0.73.

- Items, models and token probabilities are simulated.
- The sandbagging analysis is an extension of the paper.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
