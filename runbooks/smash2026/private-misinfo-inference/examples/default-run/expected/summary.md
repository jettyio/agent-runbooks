Run: hybrid features (TF-IDF→SVD300 + potion-base-8M, 556-d), title+content text, N=8192, seed=42, C=1.0.

Accuracy / macro-F1: 0.944 / 0.896 (paper full hybrid: 0.971 / 0.950; gap due to no BioBERT block).
TF-IDF alone: 0.944 / 0.895 — static embedder adds negligible lift without BioBERT.

Encrypted agreement: 1080/1080 test labels identical between plaintext and CKKS inference; max logit diff 6.02e-06.

Claims: 3/6 flagged fake — hot-water flush (p=1.000), 5G-spreads-coronavirus (p=1.000), Italian-doctors photo caption (p=0.999). Three true/accurate claims (vaccine trials, handwashing) scored near zero (p<0.002).

Latency at N=32,768: 149.2 ms, 2.24 MB per query (paper: ~122.4 ms, 2.133 MB on Apple M4).

Retrieval over 5168 CoAID titles: SIMD-packed 1.282 s vs naive extrapolated 33.9 s → 26x speed-up; top-5 neighbours identical for all 6 claims (paper: 42.6x over 7,128 items).
