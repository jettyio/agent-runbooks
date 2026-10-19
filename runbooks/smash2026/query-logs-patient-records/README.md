# Query Logs Are Patient Records: An Unguarded Attack Surface in Clinical RAG, and a Privacy-Preserving Pipeline

Louis Tremblay Thibault, Sofiane Azogagh, Marc-Olivier Killijian, Ulrich Aïvodji · SMASH 2026 (Poster) · [Paper](https://arxiv.org/pdf/2609.36376)

> In privacy-sensitive applications, the server observes the query and controls which evidence is returned, creating both confidentiality and integrity risks. Our protocol reduces private and verifiable retrieval to multiplication of a committed matrix by an encrypted vector and uses low-bit quantization to make this computation practical.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

An insider rebuilt 20 of 21 synthetic patient records from the query log. Under encryption, retrieval stayed exact and 4-bit embeddings kept 97% of float nDCG@10.

- The clinic, patients and queries are synthetic.
- The paper's succinct proofs are not reproduced, and timings come from one sandbox CPU.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
