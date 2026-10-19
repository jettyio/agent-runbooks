# Implementing Ambient Artificial Intelligence (AI) Scribes in Hospital-based Specialty Care: A Mixed-Methods Evaluation on Administrative Burden and Clinical Workflows

Nishila Mehta, Emily Ha, Andrew Gordon, Rodica Balaci, Onil Bhattacharya, Geetha Mukerji · SMASH 2026 (Poster) · [Paper](https://drive.google.com/file/d/1I4e3YIe7SLrZE1yJefyni5q4t2k4JwKW/view?usp=sharing)

> Among 17 mid-pilot survey respondents, while 52% reported the AI scribe was easy to use, 88% reported that AI generated notes required substantial editing … These interim findings suggest that the implementation of an AI scribe is feasible in hospital-based ambulatory care but may not independently reduce documentation burden …

This runbook reruns part of the paper's analysis on Jetty in a few minutes. Change the inputs in `RUNBOOK.md`'s Parameters table to try your own.

## Default run

Generic scribe drafts needed 78% of words edited. At the paper's median usage of 0.94% of encounters, a promised 4,550 clinic hours a month becomes 6.6.

- Transcripts, scribe and reviewing specialist are all simulated with LLMs.
- Time figures rest on this runbook's stated assumptions, not measured use.

Result card: [`examples/default-run/expected/result_card.html`](examples/default-run/expected/result_card.html)
