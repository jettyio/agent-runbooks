Query: "Metastatic renal cell carcinoma, second-line therapy after progression" logged at 14:15.

Attack: diagnosis recovered top-1 in 95% of patient queries (chance 1.7%), timestamp join correct 100%,
yielding 20/21 full (patient, working-diagnosis) records. Your query linked to patient MRN-63849 at the 14:00
appointment, working diagnosis correctly inverted to "metastatic renal cell carcinoma". Quantization (b=4)
did not protect: quantized attacker also achieved 95%.

nDCG@10 on SciFact (5,183 docs, potion-base-8M embedder):
  b=2: 0.016 (collapses), b=3: 0.398, b=4: 0.490 (97% of float), b=6: 0.507, b=8: 0.507, float: 0.506

Encrypted retrieval (CKKS, b=4): 20/20 exact integer scores, 20/20 top-1 match, PIR fetch byte-exact.
Server time: 14.78 s for 5,183 docs; 1M-document extrapolation ≈ 48 min (no proofs, single CPU).

Headline: 20 of 21 synthetic patient records rebuilt from the provider's query log; b=4 quantization
retains 97% of float nDCG@10 while encrypted retrieval stays exact.
