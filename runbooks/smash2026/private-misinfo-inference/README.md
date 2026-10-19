# Privacy-Preserving Text Inference for Health-Misinformation Classification and Semantic Retrieval

Jasleen Kaur, Chloe Cachet, Koray Karabina, Jean Belo Klamti, Philippe Lamontagne · SMASH 2026 (Poster) · [Paper](https://arxiv.org/abs/2610.20796)

> We design a privacy-preserving text inference framework based on CKKS homomorphic encryption for health-misinformation classification and semantic retrieval. The hybrid classifier achieved an accuracy of 0.971 and a macro-F1 score of 0.950, with identical reported metrics under plaintext and ciphertext-based inference.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

All 1,080 encrypted predictions matched plaintext. Accuracy 0.944, macro-F1 0.896 on CoAID; SIMD packing made encrypted retrieval 26 times faster.

- A small static embedder replaces BioBERT and MPNet.
- ISCC-SCT fingerprints and late-fusion retrieval are not reproduced.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
