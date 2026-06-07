# Deck Spec: The Verification Gap in AI Agents

## Through-line
AI agents can act confidently and fail silently — the engineering discipline of verification is what separates reliable agents from risky ones.

## Meta
- **Style preset:** `dark-botanical`
- **Target slide count:** 11
- **Density mode:** Speaker-led
- **Audience:** Engineers building or deploying AI agents

---

## Slide List

### Slide 1
- **Kind:** `cover`
- **Headline:** The Verification Gap in AI Agents
- **Notes:** Open with the provocation: agents are now capable enough to act — but are we capable enough to know when they're wrong? Set the stakes: unreliable agents don't fail loudly, they fail quietly.
- **Sources:** Talk brief (conference keynote premise)

---

### Slide 2
- **Kind:** `statement`
- **Headline:** Agents don't crash. They hallucinate and keep going.
- **Notes:** Traditional software panics or throws exceptions. Agents produce plausible-sounding output regardless of correctness. The absence of a failure signal is itself the danger.
- **Sources:** Talk brief; contrast with deterministic software failure modes

---

### Slide 3
- **Kind:** `content`
- **Headline:** What do agents actually do wrong?
- **Notes:** Three failure categories: factual errors (hallucination), action errors (wrong tool call or wrong parameters), and compounding errors (each step builds on a flawed prior step). Engineering audience needs this taxonomy to reason about mitigations.
- **Sources:** Talk brief; general knowledge of LLM failure modes

---

### Slide 4
- **Kind:** `fact`
- **Headline:** Compounding errors: one bad step multiplies
- **Notes:** Show how a single incorrect retrieval upstream corrupts every downstream action in a multi-step pipeline. Illustrate with a schematic chain where error propagates. The longer the chain, the higher the blast radius.
- **Sources:** Talk brief; compound failure dynamics in multi-step LLM pipelines

---

### Slide 5
- **Kind:** `section`
- **Headline:** The Verification Gap
- **Notes:** Transition marker. Introduce the central concept: the gap between what an agent believes it did and what it actually did. Pause here — let the concept land.
- **Sources:** Talk brief

---

### Slide 6
- **Kind:** `two-column`
- **Headline:** What agents report vs. what actually happened
- **Notes:** Left column: what the agent's output claims ("I searched the database and found 3 matches"). Right column: what actually occurred (tool returned an error; agent interpreted silence as empty result). Gap = verification gap. Engineers know this pattern from distributed systems — it's the same class of problem as silent data corruption.
- **Sources:** Talk brief; analogous to distributed systems phantom reads / acknowledgment gaps

---

### Slide 7
- **Kind:** `content`
- **Headline:** Three verification strategies engineers can ship today
- **Notes:** (1) Assertion layers — structured output schemas + post-action checks. (2) Human-in-the-loop checkpoints — don't automate irreversible actions without a confirmation gate. (3) Audit trails — log inputs, tool calls, outputs, and intermediate state so failures are diagnosable after the fact.
- **Sources:** Talk brief; current engineering practice in LLM agent deployment

---

### Slide 8
- **Kind:** `code`
- **Headline:** Assertion layers: catch the gap at the seam
- **Notes:** Show a minimal Python snippet: after a tool call, validate the output matches a Pydantic schema before passing it downstream. The pattern is: call → validate → proceed or escalate. Point out this is just defensive programming applied to agent outputs.
- **Sources:** Talk brief; Pydantic + LLM tool-call validation patterns

---

### Slide 9
- **Kind:** `content`
- **Headline:** When to put a human in the loop — and where
- **Notes:** Not every step needs a human. The heuristic: gate on irreversibility and blast radius. Irreversible + high blast radius = mandatory checkpoint. Reversible + low blast radius = automate freely. Middle ground = configurable threshold. Give engineers the decision rule, not just the platitude.
- **Sources:** Talk brief; risk-based human-in-the-loop design

---

### Slide 10
- **Kind:** `content`
- **Headline:** Audit trails are not optional: the post-mortem you'll need
- **Notes:** Without a trace of what the agent did and with what inputs, debugging failures is guesswork. Log: the prompt sent, tools called with parameters, tool responses received, model outputs, final action taken. This is standard observability practice — apply it to agents.
- **Sources:** Talk brief; observability principles applied to agent systems

---

### Slide 11
- **Kind:** `closing`
- **Headline:** Close the gap — before your agent closes it for you
- **Notes:** Call back to the through-line: agents act confidently and can fail silently. The discipline of verification — assertions, checkpoints, audit trails — is what engineers contribute. Own the verification layer or inherit the blast radius. Leave engineers with one call to action: before shipping an agent to production, ask "how will I know when this is wrong?"
- **Sources:** Talk brief

---

## Validation Gate
- [x] Through-line is one sentence
- [x] Every slide has a kind from the catalog and a headline
- [x] Slide count: 11 (within 10–12 range)
