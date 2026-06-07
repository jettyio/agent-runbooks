---
theme: default
title: "Jetty — AI/ML Workflows That Check Their Own Work"
transition: slide-left
lineNumbers: false
fonts:
  sans: Space Grotesk
  serif: Archivo Black
  mono: Space Mono
---

# Jetty

**AI/ML workflows that check their own work**

<div class="accent-bar"></div>

Build · Run · Monitor — from any AI coding agent

<!-- 
Open with energy. The big bet: AI agents are everywhere but no one trusts them in production.
Jetty fixes the reliability gap. Through-line: evaluation as infrastructure.
-->

---
layout: statement
---

# AI agents fail silently — and no one knows until it's in production

<!-- 
Frame the pain hard. Same task, different output every run. No paper trail, no feedback loop, no way to debug or improve. This is why enterprises stall on AI deployment.
-->

---
layout: default
---

# The enterprise AI stack has a missing layer

<div class="accent-bar"></div>

The stack exists — the glue doesn't:

- **Models** are deployed: GPT-4o, Claude, Gemini
- **Agent frameworks** are proliferating: Claude Code, Cursor, LangChain
- **Cloud infra** is ready: AWS, GCP, Azure

**What's missing:** a layer that evaluates, orchestrates, and systematically improves AI workflows before they reach users

<!-- 
Three layers the audience knows cold. Draw the gap explicitly: no one owns the evaluation + workflow orchestration layer at scale. That's Jetty's territory.
-->

---
layout: statement
---

# Evaluation isn't a feature — it's the foundation

<!-- 
Core thesis. You can't ship AI to production without knowing whether it worked. Every other layer (observability, MLOps) presupposes this. Jetty makes it the starting point.
-->

---
layout: default
---

# Jetty: the agentic evaluation platform for AI/ML workflows

<div class="accent-bar"></div>

One platform for the full workflow lifecycle:

- **Build** — define workflows as versioned JSON configs with typed inputs and modular steps
- **Run** — execute synchronously or async from any MCP-compatible agent
- **Monitor** — every step recorded as a trajectory with artifacts and annotations
- **Improve** — iterative refinement with built-in quality gates

<!-- 
The product in one slide. MCP-native is the key technical differentiator — say it clearly. This isn't another LangChain wrapper; it's infrastructure that plugs into every agent ecosystem at once.
-->

---
layout: two-cols
---

# Two feedback loops, one platform

<div class="accent-bar"></div>

### Inner loop
Each run self-corrects:
- Quality gates evaluate each step
- Up to 3 refinement iterations per run
- Structured evaluation criteria baked in
- Run fails fast or improves to threshold

::right::

### Outer loop
The system improves across runs:
- Every trajectory labeled and indexed
- Compare runs across models and configs
- Patterns surface automatically
- Teams build institutional knowledge

<!-- 
This is the defensible moat: the dual-loop architecture. Inner loop = reliability. Outer loop = continuous improvement. Together they create a compounding advantage that raw LLM calls can never replicate.
-->

---
layout: default
---

# MCP-native: works with every agent, from day one

<div class="accent-bar"></div>

16 MCP tools for workflow management — no custom integrations required:

- **Claude Code** · **Cursor** · **VS Code Copilot**
- **Gemini CLI** · **Windsurf** · **Zed** · **Codex CLI**
- Any MCP-compatible agent (the standard is winning)

MCP is becoming the universal agent interface. Jetty was built for this moment.

<!-- 
Distribution moat: being MCP-native means Jetty distributes through every agent tool that adopts the standard. No bespoke SDK per platform, no waiting for partnerships. The network effect compounds as MCP adoption grows.
-->

---
layout: default
---

# Runbooks: structured execution with built-in quality gates

<div class="accent-bar"></div>

Runbooks are parameterized markdown documents that tell an agent *how* to complete a complex task:

- Step-by-step execution with explicit quality checkpoints
- Up to 3 refinement iterations per gate
- Parameterized inputs — run the same workflow with different data
- Secrets resolved through a secure 3-tier fallback system

*"A structured markdown document that tells a coding agent how to accomplish a complex, multi-step task with built-in evaluation loops."* — jetty.io

<!-- 
Runbooks are the unit of work. They make AI tasks auditable, reproducible, and improvable. This is what separates Jetty from ad-hoc prompting.
-->

---
layout: default
---

# Full trajectory: every step recorded, labeled, downloadable

<div class="accent-bar"></div>

Every workflow run produces a complete trajectory:

- Step-by-step outputs captured in sequence
- Artifacts attached and downloadable
- Annotations and quality labels per run
- Ask any question about any prior run, instantly

No more "what did the agent actually do?" — full observability at every depth.

<!-- 
Observability is table stakes for enterprise. Jetty's trajectory system is what lets teams inspect, audit, and compare AI workflow outputs. This is the compliance and debugging story.
-->

---
layout: default
---

# Already deployed at AWS, Google, and frontier AI labs

<div class="accent-bar"></div>

Customers spanning research and enterprise:

- **AWS** · **Google** · **TU/e** (Eindhoven)
- **Brickroad AI** · **Akinox** · **Carepath**
- **OpenML** · **AI Vibe** · **Workshop.ai**

Use cases: operations automation, competitor research, engineering audits, document processing

<!-- 
Name the logos. AWS and Google signal enterprise-readiness immediately. The mix of research (TU/e, OpenML) and commercial customers shows breadth. Mention the use case variety to show the platform is general, not niche.
-->

---
layout: fact
---

# 5-tier SaaS · Free → Enterprise

<div class="accent-bar"></div>

**Free** — 100 runs/mo, self-serve adoption

**Builder** — $200/yr, 10,000 runs/mo

**Team** — $800/yr, 350,000 runs/mo, 15 seats

**Business** — $4,800/yr, 1M runs/mo, 50 seats

**Enterprise** — Custom · SOC 2 · HIPAA · on-premise

<!-- 
Usage-based model with land-and-expand motion. The free tier seeds adoption; enterprise contracts deliver ARR. SOC 2 and HIPAA unlock regulated industries — healthcare, finance, government.
-->

---
layout: default
---

# The market: every enterprise deploying AI agents needs this layer

<div class="accent-bar"></div>

The evaluation and orchestration gap is universal:

- Every team running LLM workflows faces the same reliability problem
- MLOps, AI observability, and agent orchestration are merging into one category
- The window to define that category is open — and closing

Jetty sits at the intersection and is building the standard before it's set.

<!-- 
Frame the TAM as the universe of enterprises adopting AI agents — potentially every knowledge-work company. The category is being defined now. Jetty's MCP-native position and early customer base make it a credible standard-setter.
-->

---
layout: default
---

# Go-to-market: agent ecosystem as the distribution channel

<div class="accent-bar"></div>

**Wedge:** MCP integration puts Jetty in every agent's toolbox at install

**Land:** Self-serve free tier — developers adopt, workflows proliferate

**Expand:** Teams, departments, then enterprise contracts with custom SLAs

**Moat:** Trajectory data accumulates; switching cost grows with every labeled run

<!-- 
The GTM is product-led, not sales-led — critical for this market. MCP surfacing in Claude Code, Cursor, etc. means developers find Jetty organically. The trajectory library creates lock-in without friction.
-->

---
layout: default
---

# Backed by Hidden Layers, AQC Capital, and Mila Ventures

<div class="accent-bar"></div>

Strategic alignment across AI infrastructure and enterprise software:

- **Hidden Layers** — AI infrastructure specialist fund
- **Mila Ventures** — connected to world-class AI research (Yoshua Bengio's lab)
- **AQC Capital** — enterprise software depth and network

<!-- 
Investor quality signals credibility. Mila is the Bengio connection — world-leading AI research. Hidden Layers is a focused AI infra thesis investor. AQC brings enterprise GTM experience.
-->

---
layout: default
---

# Why now: the MCP moment is here

<div class="accent-bar"></div>

The agent protocol is standardizing — fast:

- Claude Code, Cursor, VS Code Copilot, Gemini CLI all speak MCP
- Every AI coding tool is becoming an agent runtime
- The team that owns the evaluation layer for MCP owns the reliability primitive for all of them

First-mover advantage is measured in months, not years.

<!-- 
Urgency slide. MCP adoption is accelerating across every major AI coding tool. Jetty is MCP-native from day one — this is a timing advantage that compounds. Comparable to owned the API layer before REST was ubiquitous.
-->

---
layout: end
---

# Join us: make AI workflows reliable enough to ship

<div class="accent-bar"></div>

Jetty turns unreliable AI agents into production-grade workflows — by making evaluation a first-class primitive.

**We're raising to:**
- Scale evaluation infrastructure and trajectory storage
- Deepen enterprise compliance (SOC 2, HIPAA, on-premise)
- Capture the workflow layer before it consolidates

**jetty.io** · contact@jetty.io

<!-- 
Close with the through-line callback, clear use of funds, and a single CTA. Leave them with the image of evaluation-as-infrastructure as the durable idea.
-->
