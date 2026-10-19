# When Engagement Is Not Enough: What Should AI Optimize in Gamified Education?

Takuji Takemoto · SMASH 2026 (Poster) · [Paper](https://drive.google.com/file/d/1L1jl5c3v9hjZtZ1QofMdEY-6dHQ-uJSn/view?usp=sharing)

> In crossover STEAM education (n = 49), interest favored gamified instruction (dz = 0.64), whereas perceived expression acquisition favored conventional instruction (dz = -0.55). In disaster education (n = 37), engagement was high and perceived knowledge and competence increased, but intention changed little.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

With equal weights the gamified condition wins 55% of resamples. The verdict flips once learning gets more than 51% of the weight.

- Learners are simulated from the paper's summary statistics.
- Persistence is an assumed value; the paper's follow-up data are not modelled.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
