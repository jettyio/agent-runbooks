# MASQ: The Multi-Agent System Questionnaire

Nils Kiele, Niki Mehri, Aaron Arellano, Samira Ebrahimi Kahou · SMASH 2026 (Poster) · [Paper](https://drive.google.com/file/d/1Rp0p5g3H-GnNNV-2aCJPC3Ke3VbRcm0C/view?usp=sharing)

> We introduce the multi-agent system questionnaire (MASQ), a three-stage screening framework that connects system design choices to plausible miscoordination risks and their observable manifestations. Stage 3 guides researchers in examining MAS execution traces for evidence of anticipated and unanticipated miscoordination.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

An LLM filling in MASQ for ChatDev anticipated 8 of 14 failure modes, the same count as the authors. In a small ChatDev-style chain, 3 of 5 tasks declared done failed hidden tests.

- Stage 2 ratings are an LLM applying the paper's rule, not the authors' labels.
- Five traces give coarse rates.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
