SMASH 2026 #16 bias propagation, run with defaults (target A1-B3, flip 0.3, h=0, 4 clients, r_shift 0.25, 20 seeds).
Prediction vs retraining: Spearman 0.980 [0.974, 0.986], slope c 1.002 [0.982, 1.023] (paper: 0.975, 1.014 for A1-B3).
Labels changed: 45.5 per seed (0.379% of 12,000); every recipient mean decreased.
Most affected recipient: A1-B4 at 0.04201, 17.1% more than target A1-B3 (rank 2; paper reports 18.2%).
Audit matrix: 5 of 8 source errors have a different group as their top victim; 8 of 64 predicted cells are negative.
Headline: A1-B4 was hit hardest, 0.04201 vs 0.03588 for the flipped A1-B3 (17.1% more), with the closed-form prediction closely tracking the ranking.
