System screened: ChatDev (paper preset) + mini ChatDev-shaped chain (5 traces, prompt verification, drop memory, 2 review rounds)

Stage-2 risk profile for ChatDev (LLM screen): 6 Low · 6 Mid · 2 High
LLM screen agreed with paper's Table 2 authors on 9/14 modes; scored 8/14 correctly anticipated against paper's 30 traces — matching the authors' own result.

Main ChatDev miss replicated: FM-3.2 (no/incomplete verification) rated Low, yet appeared in 11/30 paper traces.
LLM outperformed authors on FM-1.4 (loss of history): rated Low (correctly, 2/30 traces) vs authors' High.

Mini-MAS Stage 3: 2/14 correctly anticipated — screen heavily over-estimated failures; most High/Mid modes never appeared.
Verification finding: 3 of 5 mini traces declared done by agents; hidden unit tests still caught failures (88% pass rate overall).
Confirms paper's conclusion: role-prompting does not substitute for formal, mechanical verification.
