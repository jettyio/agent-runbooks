---
theme: default
title: "The Verification Gap in AI Agents"
transition: slide-left
highlighter: shiki
lineNumbers: false
css: unocss
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,400;0,600;0,700;1,400;1,600&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --bg: #0f0f0f;
  --text: #e8e4df;
  --accent: #d4a574;
  --green: #8fad91;
  --muted: #5a5550;
  --surface: #1a1a18;
  --border: #2e2e2a;
  --font-serif: 'Cormorant', Georgia, serif;
  --font-sans: 'IBM Plex Sans', sans-serif;
  --font-mono: 'IBM Plex Mono', monospace;
}

.slidev-layout {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--font-sans) !important;
}

h1, h2 {
  font-family: var(--font-serif) !important;
  font-weight: 600 !important;
  letter-spacing: -0.01em !important;
  color: var(--text) !important;
}

h3 {
  font-family: var(--font-sans) !important;
  font-weight: 500 !important;
  color: var(--accent) !important;
}

ul, ol { line-height: 1.75 !important; }
li + li { margin-top: 0.5rem !important; }

code { font-family: var(--font-mono) !important; }
</style>

---
layout: cover
class: text-center
---

<div style="color: #5a5550; font-family: 'IBM Plex Sans', sans-serif; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 2rem;">Engineering Keynote · 2026</div>

<h1 style="font-family: 'Cormorant', Georgia, serif; font-size: 3.8rem; font-weight: 700; color: #e8e4df; line-height: 1.1; margin-bottom: 0.5rem;">The Verification Gap<br>in AI Agents</h1>

<div style="width: 3rem; height: 2px; background: #d4a574; margin: 1.25rem auto;"></div>

<p style="color: #8fad91; font-size: 1.1rem; font-weight: 300;">Agents act confidently. We need to know when they're wrong.</p>

<!-- 
Open with the core provocation: agents are now capable enough to act — but are we capable enough to know when they fail? 
The stakes: unreliable agents don't fail loudly, they fail quietly. That silence is the engineering problem this talk addresses.
-->

---
layout: statement
---

<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #0f0f0f;">
<div style="text-align: center; max-width: 22rem;">
<h1 style="font-family: 'Cormorant', Georgia, serif; font-size: 2.6rem; font-weight: 600; color: #e8e4df; line-height: 1.2;">Agents don't crash.<br>They hallucinate<br><em style="color: #d4a574;">and keep going.</em></h1>
<div style="width: 2rem; height: 1px; background: #2e2e2a; margin: 1.5rem auto;"></div>
<p style="color: #5a5550; font-size: 0.9rem; font-weight: 300; letter-spacing: 0.05em;">Traditional software panics. Agents produce plausible output — regardless of correctness.</p>
</div>
</div>

<!--
The contrast: deterministic software throws an exception or returns a nil. An LLM-based agent produces a confident, grammatically correct response even when it's completely wrong. The absence of a failure signal is itself the danger — engineers trained on systems that fail loudly are not equipped for systems that fail silently.
-->

---
layout: default
---

<h1 style="font-family: 'Cormorant', Georgia, serif; font-size: 2.2rem; color: #e8e4df; margin-bottom: 1.5rem;">What do agents actually get wrong?</h1>

<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem; margin-top: 1rem;">

<div style="background: #1a1a18; border: 1px solid #2e2e2a; border-top: 2px solid #d4a574; padding: 1.25rem; border-radius: 2px;">
<div style="color: #d4a574; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.75rem;">Factual</div>
<p style="color: #e8e4df; font-size: 0.95rem; line-height: 1.6;">Hallucinated facts, fabricated citations, confident claims with no grounding</p>
</div>

<div style="background: #1a1a18; border: 1px solid #2e2e2a; border-top: 2px solid #8fad91; padding: 1.25rem; border-radius: 2px;">
<div style="color: #8fad91; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.75rem;">Action</div>
<p style="color: #e8e4df; font-size: 0.95rem; line-height: 1.6;">Wrong tool selected, correct tool with wrong parameters, misread tool output</p>
</div>

<div style="background: #1a1a18; border: 1px solid #2e2e2a; border-top: 2px solid #5a5550; padding: 1.25rem; border-radius: 2px;">
<div style="color: #a09590; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.75rem;">Compounding</div>
<p style="color: #e8e4df; font-size: 0.95rem; line-height: 1.6;">Each step builds on a flawed prior step — errors amplify across a multi-step pipeline</p>
</div>

</div>

<p style="color: #5a5550; font-size: 0.85rem; margin-top: 1.5rem;">These categories aren't independent. Compounding is what makes the other two dangerous at scale.</p>

<!--
Engineering audience needs this taxonomy to reason about where to put mitigations. Factual errors are annoying. Action errors can be destructive. Compounding errors are what turn a 5% error rate per step into a 40% failure rate across an 8-step pipeline.
-->

---
layout: default
---

<h1 style="font-family: 'Cormorant', Georgia, serif; font-size: 2.2rem; color: #e8e4df; margin-bottom: 1rem;">Compounding: one bad step multiplies</h1>

<div style="display: flex; align-items: center; gap: 0; margin: 1.5rem 0 1rem;">

<div style="background: #1a1a18; border: 1px solid #2e2e2a; padding: 0.75rem 1rem; border-radius: 2px; text-align: center; min-width: 7rem;">
<div style="color: #8fad91; font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase;">Retrieve</div>
<div style="color: #e8e4df; font-size: 0.85rem; margin-top: 0.3rem;">wrong doc</div>
</div>

<div style="color: #d4a574; font-size: 1.2rem; padding: 0 0.5rem;">→</div>

<div style="background: #1a1a18; border: 1px solid #2e2e2a; padding: 0.75rem 1rem; border-radius: 2px; text-align: center; min-width: 7rem; border-color: #5a5550;">
<div style="color: #a09590; font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase;">Summarize</div>
<div style="color: #a09590; font-size: 0.85rem; margin-top: 0.3rem;">wrong facts</div>
</div>

<div style="color: #d4a574; font-size: 1.2rem; padding: 0 0.5rem;">→</div>

<div style="background: #1a1a18; border: 1px solid #2e2e2a; padding: 0.75rem 1rem; border-radius: 2px; text-align: center; min-width: 7rem; border-color: #5a5550;">
<div style="color: #a09590; font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase;">Draft</div>
<div style="color: #a09590; font-size: 0.85rem; margin-top: 0.3rem;">wrong answer</div>
</div>

<div style="color: #d4a574; font-size: 1.2rem; padding: 0 0.5rem;">→</div>

<div style="background: #2a1a10; border: 1px solid #d4a574; padding: 0.75rem 1rem; border-radius: 2px; text-align: center; min-width: 7rem;">
<div style="color: #d4a574; font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase;">Action</div>
<div style="color: #d4a574; font-size: 0.85rem; margin-top: 0.3rem;">taken on bad data</div>
</div>

</div>

<div style="background: #141410; border-left: 3px solid #d4a574; padding: 1rem 1.25rem; margin-top: 1rem;">
<p style="color: #e8e4df; font-size: 0.95rem; margin: 0;">With <strong style="color: #d4a574;">90% accuracy per step</strong>, a 5-step pipeline reaches <strong style="color: #d4a574;">~59% end-to-end accuracy</strong>. The longer the chain, the higher the blast radius.</p>
</div>

<p style="color: #5a5550; font-size: 0.85rem; margin-top: 1rem;">The error doesn't announce itself at step 1. It propagates silently — and takes irreversible action at step 4.</p>

<!--
The multiplication math: 0.9^5 = 0.59. Engineers understand this from distributed systems — each hop in a network is a point of failure. Apply the same thinking to agent pipelines. The failure at step 1 is invisible to step 4; it just looks like valid input.
-->

---
layout: section
---

<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #0f0f0f;">
<div>
<div style="color: #5a5550; font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 1rem;">The core problem</div>
<h1 style="font-family: 'Cormorant', Georgia, serif; font-size: 4rem; font-weight: 700; color: #e8e4df; border-left: 4px solid #d4a574; padding-left: 1.5rem; line-height: 1.15;">The Verification<br>Gap</h1>
<p style="color: #8fad91; margin-top: 1.5rem; padding-left: 1.75rem; font-size: 1rem; max-width: 30ch; line-height: 1.6;">The distance between what an agent <em>believes</em> it did and what it <em>actually</em> did.</p>
</div>
</div>

<!--
Section break. Let this land. The verification gap is the central concept: it exists in every agent system, and most teams haven't named it, let alone engineered against it. Give the audience a moment to recognize the pattern in their own systems.
-->

---
layout: two-cols
---

<h1 style="font-family: 'Cormorant', Georgia, serif; font-size: 1.9rem; color: #e8e4df; margin-bottom: 1.25rem; grid-column: 1 / -1;">What agents report vs. what happened</h1>

<div style="background: #1a1a18; border: 1px solid #2e2e2a; border-top: 2px solid #8fad91; padding: 1.25rem; border-radius: 2px; height: calc(100% - 5rem);">
<div style="color: #8fad91; font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.75rem;">Agent output</div>
<p style="color: #e8e4df; font-size: 0.95rem; font-style: italic; line-height: 1.6;">"I searched the customer database and found 3 matching records."</p>
<hr style="border: none; border-top: 1px solid #2e2e2a; margin: 1rem 0;">
<p style="color: #e8e4df; font-size: 0.95rem; font-style: italic; line-height: 1.6;">"The API call succeeded."</p>
<hr style="border: none; border-top: 1px solid #2e2e2a; margin: 1rem 0;">
<p style="color: #e8e4df; font-size: 0.95rem; font-style: italic; line-height: 1.6;">"I updated the record as requested."</p>
</div>

::right::

<div style="background: #1a1a18; border: 1px solid #2e2e2a; border-top: 2px solid #d4a574; padding: 1.25rem; border-radius: 2px; height: calc(100% - 5rem); margin-left: 2rem;">
<div style="color: #d4a574; font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.75rem;">What actually happened</div>
<p style="color: #a09590; font-size: 0.95rem; line-height: 1.6;">Tool returned an error. Agent interpreted the empty response as zero results — and proceeded.</p>
<hr style="border: none; border-top: 1px solid #2e2e2a; margin: 1rem 0;">
<p style="color: #a09590; font-size: 0.95rem; line-height: 1.6;">Rate-limited. Agent read the 429 body as a success payload.</p>
<hr style="border: none; border-top: 1px solid #2e2e2a; margin: 1rem 0;">
<p style="color: #a09590; font-size: 0.95rem; line-height: 1.6;">Updated the wrong record ID — parameters hallucinated from context.</p>
</div>

<!--
Left column: agent's confident narration. Right column: ground truth. The gap between these columns is the verification gap. Engineers recognize this from distributed systems — it's the same class of problem as phantom reads or acknowledgment loss. The agent's self-report is not a ground truth; it's a hypothesis.
-->

---
layout: default
---

<h1 style="font-family: 'Cormorant', Georgia, serif; font-size: 2.2rem; color: #e8e4df; margin-bottom: 1.5rem;">Three verification strategies engineers can ship</h1>

<div style="display: flex; flex-direction: column; gap: 1rem;">

<div style="background: #1a1a18; border: 1px solid #2e2e2a; padding: 1rem 1.25rem; border-radius: 2px; display: flex; align-items: flex-start; gap: 1rem;">
<div style="color: #d4a574; font-family: 'Cormorant', serif; font-size: 1.5rem; font-weight: 700; min-width: 1.5rem;">1</div>
<div>
<div style="color: #d4a574; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.3rem;">Assertion layers</div>
<p style="color: #e8e4df; font-size: 0.9rem; margin: 0; line-height: 1.6;">Validate structured output schemas after every tool call. Fail fast before the result propagates downstream.</p>
</div>
</div>

<div style="background: #1a1a18; border: 1px solid #2e2e2a; padding: 1rem 1.25rem; border-radius: 2px; display: flex; align-items: flex-start; gap: 1rem;">
<div style="color: #8fad91; font-family: 'Cormorant', serif; font-size: 1.5rem; font-weight: 700; min-width: 1.5rem;">2</div>
<div>
<div style="color: #8fad91; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.3rem;">Human-in-the-loop checkpoints</div>
<p style="color: #e8e4df; font-size: 0.9rem; margin: 0; line-height: 1.6;">Gate irreversible, high-blast-radius actions on human confirmation. Automate everything else freely.</p>
</div>
</div>

<div style="background: #1a1a18; border: 1px solid #2e2e2a; padding: 1rem 1.25rem; border-radius: 2px; display: flex; align-items: flex-start; gap: 1rem;">
<div style="color: #a09590; font-family: 'Cormorant', serif; font-size: 1.5rem; font-weight: 700; min-width: 1.5rem;">3</div>
<div>
<div style="color: #a09590; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.3rem;">Audit trails</div>
<p style="color: #e8e4df; font-size: 0.9rem; margin: 0; line-height: 1.6;">Log inputs, tool calls with parameters, responses, and actions taken. Make failures diagnosable after the fact.</p>
</div>
</div>

</div>

<!--
Three concrete patterns — engineers can ship any of these in a week. Present them as a layered defense, not a menu. Assertion layers catch errors early. Checkpoints contain blast radius. Audit trails make the rest diagnosable. Together they close the verification gap.
-->

---
layout: default
---

<h1 style="font-family: 'Cormorant', Georgia, serif; font-size: 2.2rem; color: #e8e4df; margin-bottom: 1.25rem;">Assertion layers: catch the gap at the seam</h1>

```python {all|6-9|11-14}
from pydantic import BaseModel, ValidationError
from typing import Any

class SearchResult(BaseModel):
    records: list[dict[str, Any]]
    total_count: int
    query_echoed: str          # verify the tool heard what we asked

def verified_search(agent_tool_call) -> SearchResult:
    raw = call_search_tool(agent_tool_call)
    try:
        result = SearchResult.model_validate(raw)
    except ValidationError as e:
        raise AgentVerificationError("search tool output failed schema") from e
    return result                # only reaches downstream if valid
```

<div style="background: #141410; border-left: 3px solid #d4a574; padding: 0.85rem 1.1rem; margin-top: 1.25rem;">
<p style="color: #e8e4df; font-size: 0.875rem; margin: 0; line-height: 1.6;">Pattern: <strong style="color: #d4a574;">call → validate → proceed or escalate</strong>. This is defensive programming applied to agent outputs — not new ideas, new targets.</p>
</div>

<!--
Walk through the code. The key insight: the agent's tool call output is an untrusted boundary — treat it like user input. Pydantic schema validation is the assertion layer. If the tool returns something that doesn't match the expected shape, fail fast and escalate rather than silently passing garbage downstream.
-->

---
layout: default
---

<h1 style="font-family: 'Cormorant', Georgia, serif; font-size: 2.2rem; color: #e8e4df; margin-bottom: 1.5rem;">When to put a human in the loop — and where</h1>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem;">

<div style="background: #0f1a10; border: 1px solid #8fad91; padding: 1.1rem; border-radius: 2px;">
<div style="color: #8fad91; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.6rem;">Automate freely</div>
<p style="color: #e8e4df; font-size: 0.9rem; line-height: 1.6; margin: 0;">Reversible · Low blast radius<br><span style="color: #5a5550;">Read ops, drafts, lookups, summaries</span></p>
</div>

<div style="background: #1a1008; border: 1px solid #d4a574; padding: 1.1rem; border-radius: 2px;">
<div style="color: #d4a574; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.6rem;">Mandatory checkpoint</div>
<p style="color: #e8e4df; font-size: 0.9rem; line-height: 1.6; margin: 0;">Irreversible · High blast radius<br><span style="color: #5a5550;">Sends, deletes, payments, publishes</span></p>
</div>

</div>

<div style="background: #1a1a18; border: 1px solid #2e2e2a; padding: 1rem 1.25rem; border-radius: 2px;">
<p style="color: #e8e4df; font-size: 0.9rem; margin: 0; line-height: 1.6;"><strong style="color: #a09590;">Middle ground:</strong> set a configurable threshold — reversibility score + estimated blast radius → auto-approve or escalate. Make the threshold explicit in your agent's configuration, not buried in code.</p>
</div>

<!--
Give engineers a decision rule, not just the platitude "add a human checkpoint." The heuristic is two axes: reversibility and blast radius. Use these two dimensions to build a policy table in your agent's config. The middle ground is real — give teams a way to dial it rather than hardcoding.
-->

---
layout: default
---

<h1 style="font-family: 'Cormorant', Georgia, serif; font-size: 2.2rem; color: #e8e4df; margin-bottom: 1.25rem;">Audit trails: the post-mortem you'll need</h1>

<p style="color: #8fad91; font-size: 0.9rem; margin-bottom: 1.25rem;">Without a trace, debugging an agent failure is guesswork. Log everything at the decision boundaries:</p>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">

<div style="background: #1a1a18; border: 1px solid #2e2e2a; padding: 1rem; border-radius: 2px;">
<ul style="color: #e8e4df; font-size: 0.9rem; line-height: 1.75; margin: 0; padding-left: 1.1rem;">
<li>Prompt sent (verbatim, with system context)</li>
<li>Tools called — name and exact parameters</li>
<li>Tool responses received (full payload)</li>
</ul>
</div>

<div style="background: #1a1a18; border: 1px solid #2e2e2a; padding: 1rem; border-radius: 2px;">
<ul style="color: #e8e4df; font-size: 0.9rem; line-height: 1.75; margin: 0; padding-left: 1.1rem;">
<li>Model output (raw, before parsing)</li>
<li>Final action taken — what, when, on what</li>
<li>Verification result at each assertion layer</li>
</ul>
</div>

</div>

<div style="background: #141410; border-left: 3px solid #8fad91; padding: 0.85rem 1.1rem; margin-top: 1.25rem;">
<p style="color: #e8e4df; font-size: 0.875rem; margin: 0; line-height: 1.6;">This is standard observability practice. Apply structured logging, trace IDs, and retention policies — the same discipline as a distributed service.</p>
</div>

<!--
Observability is not optional for production agents: it's how you replay failures, audit behavior for compliance, and build a feedback loop for improvement. The six data points listed are the minimum viable audit trail. Emphasize: without this, when something goes wrong (and it will), you're flying blind.
-->

---
layout: end
class: text-center
---

<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #0f0f0f;">
<div style="max-width: 28rem;">
<div style="color: #5a5550; font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 1.5rem;">The ask</div>
<h1 style="font-family: 'Cormorant', Georgia, serif; font-size: 2.6rem; font-weight: 600; color: #d4a574; line-height: 1.2; margin-bottom: 1.5rem;">Close the gap —<br>before your agent<br>closes it for you.</h1>
<div style="width: 2rem; height: 1px; background: #2e2e2a; margin: 0 auto 1.5rem;"></div>
<p style="color: #8fad91; font-size: 0.95rem; line-height: 1.7; margin-bottom: 1.5rem;">Before shipping an agent to production, ask one question:<br><em style="color: #e8e4df;">"How will I know when this is wrong?"</em></p>
<div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
<span style="background: #1a1a18; border: 1px solid #2e2e2a; color: #d4a574; font-size: 0.75rem; letter-spacing: 0.08em; padding: 0.4rem 0.85rem; border-radius: 2px;">Assertion layers</span>
<span style="background: #1a1a18; border: 1px solid #2e2e2a; color: #8fad91; font-size: 0.75rem; letter-spacing: 0.08em; padding: 0.4rem 0.85rem; border-radius: 2px;">Checkpoints</span>
<span style="background: #1a1a18; border: 1px solid #2e2e2a; color: #a09590; font-size: 0.75rem; letter-spacing: 0.08em; padding: 0.4rem 0.85rem; border-radius: 2px;">Audit trails</span>
</div>
</div>
</div>

<!--
Callback to the through-line: agents act confidently and can fail silently. The three strategies — assertion layers, checkpoints, audit trails — are the engineering discipline that separates reliable agents from risky ones. Leave the room with one question in their head: "How will I know when this is wrong?" Own the verification layer or inherit the blast radius.
-->
