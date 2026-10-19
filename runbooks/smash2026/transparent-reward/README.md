# Towards Transparent Reward Design in Clinical Reinforcement Learning

Caro Strickland, Baptiste Bonin, Audrey Durand · SMASH 2026 (Spotlight) · [Paper](https://drive.google.com/file/d/1NuHr7dRpH-Qh5nYx7jZ9j1t1NRRW5bXk/view?usp=sharing)

> Using automated insulin dosing as a testbed, we show that conventionally trained policies occupy one such undisclosed point on a tradeoff surface, producing clinically consequential failure modes invisible to standard metrics. We construct an approximate Pareto frontier through preference-conditioned RL and show that it recovers policies with similar aggregate performance but different risk profiles across three simulated patients.

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

For child#001, two dosing rules within 3 points of time-in-range differ by 64.0 points in time hypoglycaemic. The paper's weights pick a rule at 16.4% hypo.

- 48 simple dosing rules replace trained RL policies.
- Simulated patients; not clinical guidance.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
