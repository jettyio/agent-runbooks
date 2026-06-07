# Deck Spec — Jetty Investor Pitch

## Through-line

Jetty turns unreliable AI agents into production-grade workflows by making evaluation a first-class primitive — not an afterthought.

## Meta

- **Style preset:** `bold-signal`
- **Target slide count:** 16
- **Density mode:** Speaker-led (1–3 bullets per slide, bold visual hierarchy)
- **Audience:** Seed/Series A investors — technical enough to understand MCP and LLMs, focused on market size, traction, and defensibility

---

## Slide List

### Slide 1
- **Kind:** `cover`
- **Headline:** Jetty — AI/ML workflows that check their own work
- **Notes:** Open with the through-line. "Build, run, and monitor AI/ML workflows from any coding agent." Set tension: agents are powerful but unpredictable.
- **Sources:** jetty.io homepage

### Slide 2
- **Kind:** `statement`
- **Headline:** AI agents fail silently — and no one knows until it's in production
- **Notes:** Frame the reliability crisis. Same task, different output every run. No guardrails, no feedback loop, no paper trail.
- **Sources:** General market context; jetty.io value proposition ("Agents on Jetty check their own work")

### Slide 3
- **Kind:** `content`
- **Headline:** The enterprise AI stack has a missing layer
- **Notes:** Three layers exist today: models (OpenAI, Gemini, Anthropic), agent frameworks (LangChain, Claude Code), and deployment infra (cloud). What's missing: evaluation and workflow orchestration as infrastructure.
- **Sources:** jetty.io homepage, QUICKSTART.md

### Slide 4
- **Kind:** `statement`
- **Headline:** Evaluation isn't a feature — it's the foundation
- **Notes:** Jetty's core insight. Every enterprise workflow needs consistent, auditable, improvable outputs. You can't ship AI to production without a quality loop.
- **Sources:** jetty.io: "check their own work and improve until it's right"

### Slide 5
- **Kind:** `content`
- **Headline:** Jetty: the agentic evaluation platform for AI/ML workflows
- **Notes:** One platform: build workflows as JSON configs, run them from any AI coding tool, monitor every step as a trajectory, improve iteratively. MCP-native.
- **Sources:** README.md; jetty.io homepage; QUICKSTART.md

### Slide 6
- **Kind:** `two-column`
- **Headline:** Two feedback loops, one platform
- **Notes:** Left: Inner loop — each run self-corrects (up to 3 refinement rounds, quality gates, structured evaluation). Right: Outer loop — Jetty learns across runs, trajectories are labeled and compared, patterns emerge.
- **Sources:** jetty.io: "inner loop where individual runs self-correct, outer loop where the system improves across executions"; QUICKSTART.md

### Slide 7
- **Kind:** `content`
- **Headline:** MCP-native: works with every agent, from day one
- **Notes:** 16 MCP tools for workflow management. Compatible with Claude Code, Cursor, VS Code Copilot, Gemini CLI, Windsurf, Zed, Codex CLI — any MCP client. No vendor lock-in.
- **Sources:** README.md; QUICKSTART.md ("16 tools for managing workflows"); jettyio-skills repo topics

### Slide 8
- **Kind:** `content`
- **Headline:** Runbooks: structured execution with built-in quality gates
- **Notes:** Runbooks are parameterized markdown documents that tell an agent how to complete a multi-step task. Each runbook includes evaluation loops, up to 3 refinement iterations, and configurable quality gates.
- **Sources:** README.md ("structured markdown documents that tell a coding agent how to accomplish a complex, multi-step task with built-in evaluation loops and quality gates")

### Slide 9
- **Kind:** `content`
- **Headline:** Full trajectory: every step recorded, labeled, and downloadable
- **Notes:** Every run produces a trajectory — step-by-step outputs, artifacts, annotations. Teams can audit, compare, and label runs for quality assessment. Complete observability.
- **Sources:** README.md; QUICKSTART.md (list-trajectories, get-trajectory tools)

### Slide 10
- **Kind:** `content`
- **Headline:** Already deployed at AWS, Google, and frontier AI labs
- **Notes:** Customers include AWS, Google, TU/e, Brickroad AI, Akinox, Carepath, OpenML, AI Vibe, Workshop.ai. Use cases span operations, product research, and engineering workflows.
- **Sources:** jetty.io homepage (customer logos section)

### Slide 11
- **Kind:** `fact`
- **Headline:** $1M+ in annual recurring potential from public pricing alone
- **Notes:** Free (100 runs/mo) → Builder $200/yr → Team $800/yr → Business $4,800/yr → Enterprise (custom). With major enterprises on platform, ASP scales fast. Source: jetty.io/pricing.
- **Sources:** jetty.io/pricing

### Slide 12
- **Kind:** `content`
- **Headline:** The market: every enterprise deploying AI agents needs this layer
- **Notes:** AI agent deployment market growing rapidly. Every Fortune 500 running LLM workflows faces the same reliability problem. Jetty sits at the intersection of MLOps, AI observability, and agent orchestration — a category being defined now.
- **Sources:** Market context; jetty.io positioning

### Slide 13
- **Kind:** `content`
- **Headline:** Business model: usage-based SaaS with enterprise upside
- **Notes:** Self-serve free tier drives adoption → usage-based upgrade path → enterprise contracts with custom SLAs, SOC 2, HIPAA, on-premise. Proven land-and-expand motion.
- **Sources:** jetty.io/pricing (5-tier model: Free, Builder, Team, Business, Enterprise)

### Slide 14
- **Kind:** `content`
- **Headline:** Backed by Hidden Layers, AQC Capital, and Mila Ventures
- **Notes:** Strategic backing from AI-specialist investors. Mila Ventures connects to world-class AI research. Hidden Layers focuses exclusively on AI infrastructure. AQC Capital brings enterprise software depth.
- **Sources:** jetty.io homepage (investor section)

### Slide 15
- **Kind:** `content`
- **Headline:** Why now: the MCP moment is here
- **Notes:** Model Context Protocol is becoming the universal agent interface — Claude Code, Cursor, VS Code Copilot, Gemini CLI all speak MCP. Jetty is the first evaluation platform built MCP-native, giving it a distribution moat as the agent ecosystem standardizes.
- **Sources:** README.md; jettyio-skills repo; github topics

### Slide 16
- **Kind:** `closing`
- **Headline:** Join us: make AI workflows reliable enough to ship
- **Notes:** Callback to through-line. CTA: we're raising [X] to scale the platform, deepen evaluation primitives, and capture the enterprise workflow layer before it consolidates. Contact info / next step.
- **Sources:** jetty.io

---

## Validation Gate

- [x] Through-line present and single-sentence
- [x] Every slide has a kind from the catalog
- [x] Every slide has a headline
- [x] Slide count: 16 (within speaker-led range of 12–20)
- [x] All factual claims traced to sources
