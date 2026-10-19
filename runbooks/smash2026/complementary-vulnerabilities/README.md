# Complementary Vulnerabilities: Auditing and Governing Clinician-LLM Error Overlap

Mohsen Amoei, Kathleen Fraser, Dan Poenaru · SMASH 2026 (Poster) · [Paper](https://drive.google.com/file/d/1_bJ_5DA5k0V2X1XuuxliKg5WdLPq1SMP/view?usp=sharing)

> But a second reasoner reduces error only insofar as it fails differently from the first. We say that a clinician and a model have complementary vulnerabilities to the extent that they break down through different mechanisms and on different cases. We therefore propose a predeployment audit in which each site measures error overlap on its own cases.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

On 36 MedQA cases, wrong AI suggestions cut the proxy clinician's accuracy from 70% to 50%. Double-fault rate 3%, Yule's Q +0.30.

- Both readers are LLMs: Claude Haiku stands in for the clinician and Claude Sonnet is the model under audit.
- 36 exam questions, far below the roughly 1,000 adjudicated cases the paper recommends.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
