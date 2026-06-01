# Northwind — Strategy Deck (SAMPLE)

> **This is a fictional sample input for the `deck-generator` runbook.** "Northwind" is a made-up company — *the open registry of data-pipeline recipes* — used only to demonstrate every slide template. Replace it with your own content in the same format. Each `## Slide` block is tagged with a `[type:]` that selects a layout (see the runbook's Template Catalog). Compile with: `INPUT_MD=sample-deck.md` → `deck.html` + `deck.pdf`.

---

## Slide 1 — Cover

[type: cover-dark]
[brand: NORTHWIND] [page: 01 / 16]

**Eyebrow:** Strategy 2026 · For the leadership team

**Headline:** Turn recipes into a **registry** and the registry into a **moat**.

**Lede:** Northwind's 2026 Playing-to-Win cascade — one winning aspiration, where we play, how we win, the capabilities and systems behind it, the customers we serve, the loop we must prove, and a 12-month goal set.

**Footer:** SOURCE: STRATEGY.md · sample deck · template showcase

---

## Slide 2 — The Playing-to-Win Cascade

[type: ptw-cascade]
[palette: lavender]
[brand: NORTHWIND] [page: 02 / 16]

**Eyebrow (lavender):** The cascade · five integrated choices

**Headline:** Read top to bottom — each choice constrains the next.

**The five boxes:**

- **Box 1 · Winning Aspiration** — *What is our winning aspiration?*
  To be **THE** place teams go to find, share, and run reliable data-pipeline recipes.

- **Box 2 · Where to Play** — *Where will we play?*
  - Customers: pipeline **Builders** (data engineers) · **Operators** in analytics teams · **Enterprise** platform leads
  - Product: managed recipe runtime · open recipe format · a public registry
  - Geography: English-speaking data hubs
  - Channels: direct-to-developer · cloud marketplaces

- **Box 3 · How to Win** — *How will we win?*
  **Differentiation through simplicity and an open format.**
  - Sensible defaults for any pipeline
  - **Self-tuning recipes** — recipes that improve from their own run history
  - Tool-agnostic — any warehouse, any orchestrator
  - A network of builders, used by operators

- **Box 4 · Capabilities** — *What capabilities must be in place?*
  - A strong product-led-growth motion
  - Sub-five-minute self-onboarding
  - A pragmatic product + data engineering team
  - A network of recipe authors

- **Box 5 · Management Systems** — *What systems are required?*
  - Growth metrics — engagement · onboarding · propagation
  - A mature release process
  - A CRM for core contributors
  - Public leaderboards

**Footer:** Playing-to-Win framework (Lafley & Martin)

---

## Slide 3 — Where to Play

[type: seq-strip]
[brand: NORTHWIND] [page: 03 / 16]

**Eyebrow:** Where to Play — three customers, sequenced

**Headline:** Builders first to seed the registry. Operators next to consume it. Enterprise deferred.

**Sequencing strip:**

- **01 · LEAD · H1 — Builders** [lead]
  ~120K data engineers · CLI-native · minutes to value. Our format fits how they already work.
  ▍ **WIN:** the registry is the obvious place to find & fork recipes

- **02 · PROSECUTE · H2 — Operators** [prosecute]
  ~2M analysts · need OAuth + a one-click run, not YAML. The registry is what makes this surface possible.
  ▍ **WIN:** ≥100 paying operator teams by month 12

- **03 · DEFER · REVISIT M12 — Enterprise** [defer]
  ~20K platform leads · long procurement. Real, but the wrong cycle.
  ▍ **PHASE-3 WIN:** two named logos with published metrics

**Why notes:**
- ▍ **WHY BUILDERS FIRST** — product fit is closest; the registry is what makes the operator phase viable. Supply before demand.
- ▍ **WHY OPERATORS SECOND** — same primitive, new audience; the H1 supply becomes H2 demand.
- ▍ **WHY ENTERPRISE DEFERRED** — they show up after a builder demo; compound the first two phases and reopen at month 12.

**Footer:** Customers detailed on slides 07–09

---

## Slide 4 — How We Win

[type: titlebar]
[palette: lavender]
[brand: NORTHWIND] [page: 04 / 16]

**Eyebrow (lavender):** How to Win — the differentiator that compounds

**Headline:** *Self-tuning recipes* — the hook that turns "I tried it once" into "this is how we work."

**Cards (cols-3):**
- ▍ **EVALS IN THE RECIPE** — Pass/fail checks live in the same file as the pipeline, not in a separate tool.
- ▍ **MANAGED RUNS** — Re-run a recipe against fresh data with one command; results stream back. No infra to babysit.
- ▍ **THE TUNE STEP** — Reads past runs, spots the failure pattern, proposes an edit, and re-checks that it improved.

**Callout (lavender):** No competitor combines an open recipe format, a managed runtime, **and** a self-tuning loop. The combination is the moat.

**Footer:** Source: how-to-win.md

---

## Slide 5 — The Loop We Must Prove

[type: flywheel]
[palette: lavender]
[brand: NORTHWIND] [page: 05 / 16]

**Eyebrow (lavender):** The only thing the first phase has to prove

**Headline:** It isn't *"can we get 1,000 recipes?"* — it's *"can one public recipe create the next author?"*

**Flywheel ring (6 nodes, clockwise, the 6th loops back to the 1st):**
1. **Publish** — an author seeds it
2. **Fork** — a builder copies it
3. **Run** — first value lands
4. **Remix** — builder adapts it
5. **Share** — a public result
6. **Publish** — their own → loops back to ①

**Center hub:** ↻ *Does the loop close?* — one public recipe → the next author publishing their own.

**Legend:** **Fork** copy another's recipe · **Run** execute it · **Remix** adapt it · **Share** make a result public · **Publish** add a recipe to the registry

**Closing callout (lavender):** If the ring doesn't close, this is a content library — **not a network.**

**Footer:** Phase-1 metrics group these into Supply · Demand · Value · Remix · Distribution · Discovery

---

## Slide 6 — 12-Month Win Condition

[type: cards-dark]
[palette: amber]
[brand: NORTHWIND] [page: 06 / 16]

**Eyebrow (amber):** By next spring — what success looks like

**Headline:** Three phases. *One win each.*

**Cards (cols-3, dark):**
- **PHASE 1 · BUILDERS** [lavender] — **The registry sparks.** Authors publish · strangers fork & run · the first loop stages fire.
- **PHASE 2 · OPERATORS** [amber] — **The loop closes.** New authors emerge from public traffic · the operator surface ships into a working network.
- **PHASE 3 · TRANSITION** [sage] — **The team has options.** ≥100 paying operator teams cleared · raise / sell / compound.

**Footer:** Translated into per-phase goals on slides 10–11

---

## Slide 7 — Customer 1 · The Builder

[type: persona-hero]
[palette: lavender]
[brand: NORTHWIND] [page: 07 / 16]

**Persona:** initials "DB" · badge "01 · BUILDER" · caption "Dana · 33 · senior data eng · ships nightly"

**Tag:** 01 · LEAD · H1

**Headline:** The *Builder*.

**Lede:** Data engineers and 2–5 person platform teams who already live in the CLI and the warehouse. They write recipes for themselves and their org. Their language: "DAG," "backfill," "schema drift," "SLA."

**Pulses:** 120K reachable · ~400 power authors · GitHub / dbt Slack / HN · $20–200/mo wallet

**Cards (cols-2):**
- ▍ **HARD REQUIREMENTS** — under 5-min first run · generous free tier · open format · readable run logs
- ▍ **THREE TO WIN** — three named OSS authors in the data-tooling community

**Callout (lavender):** **Still broad.** Tighten on the first 50 target authors: who publishes, why, and what keeps them coming back.

**Footer:** Source: customer-research.md

---

## Slide 8 — Customer 2 · The Operator

[type: persona-hero]
[palette: amber]
[brand: NORTHWIND] [page: 08 / 16]

**Persona:** initials "MO" · badge "02 · OPERATOR" · caption "Morgan · 39 · analytics lead · allergic to YAML"

**Tag:** 02 · PROSECUTE · H2

**Headline:** The Operator.

**Lede:** Analysts and ops leads who know pipelines multiply their output but don't want to maintain them. They live in the BI tool and the spreadsheet — not the terminal. Entry via the analyst-who-codes-a-little bridge.

**Pulses:** 2M reachable · 300K high-intent · YouTube / newsletters / community · $30–100/mo floor

**Cards (cols-2):**
- ▍ **HARD REQUIREMENTS (TIGHTER)** — under 3-min first result · OAuth, not keys · readable receipts · pricing on the page
- ▍ **THREE TO WIN** — three named analytics-influencer voices

**Callout (amber):** **The bridge.** Halfway between Builder and Operator: forks recipes for the team but runs analytics, not infra. Phase-1 supply becomes their Phase-2 demand.

**Footer:** Source: customer-research.md

---

## Slide 9 — Customer 3 · The Enterprise Lead (deferred)

[type: persona-hero]
[palette: sage]
[brand: NORTHWIND] [page: 09 / 16]

**Persona:** initials "EL" · badge "03 · ENTERPRISE" · caption "Eli · 41 · platform lead · owns the SLA"

**Tag:** 03 · DEFERRED · PHASE 3

**Headline:** The Enterprise Lead

**Lede:** Platform leads inside orgs already running pipelines in production. Has personally absorbed the "swap a source, ship a silent regression" tax. Has the capital to bring tools in — and is immunized against top-down sales.

**Callout (sage):** **Why deferred.** Real customer, wrong cycle. SOC 2 is a long tail; the enterprise tier is mostly paper without it. They show up after a builder demo — compound the first two phases and reopen at month 12.

**Pulses:** 20K reachable · 5K active · peer referral · long procurement

**Cards (cols-2):**
- ▍ **PHASE-3 REQUIREMENTS** — SOC 2 Type II · 30-min eval on a real workload · visible pricing · no "contact sales" wall
- ▍ **PHASE-3 THREE TO WIN** — three named data-platform thought leaders

**Footer:** Source: customer-research.md

---

## Slide 10 — Phase Overview · 12 Months

[type: month-bar]
[brand: NORTHWIND] [page: 10 / 16]

**Eyebrow:** 12 months at a glance — phases and decision gates

**Headline:** Builders → Operators → (Enterprise revisit). The phase shape; the ships are the team's to draw.

**Month bar:** M1–M4 → Phase 1 (p1) · M5–M10 → Phase 2 (p2) · M11–M12 → Phase 3 (p3)

**Decision-gate cards (cols-3):**
- **PHASE 1 · M1–4 · BUILDERS** [lavender-bg] — Owners named Week 1. Fast tests resolve by Week 8; operator research signed by M4.
- **PHASE 2 · M5–10 · OPERATORS** [amber-bg] — Operator-surface investment opens at M5. The M6 checkpoint confirms trajectory and commits staffing.
- **PHASE 3 · M11–12 · TRANSITION** [sage-bg] — M11 review on paying teams decides scale / hold / sunset — and whether Enterprise reopens.

**Footer:** Phase 1 = lavender · Phase 2 = amber · Phase 3 = sage

---

## Slide 11 — Phase 1 · Proofs

[type: cards]
[palette: lavender]
[brand: NORTHWIND] [page: 11 / 16]

**Eyebrow (lavender):** Phase 1 · months 1–4 · BUILDERS LEAD

**Headline:** Six proofs — each tests a stage of the loop.

**Cards (cols-3):**
- ▍ **SUPPLY** — *Can we create credible supply?* Authors committed · % recipes from outside authors
- ▍ **DEMAND** — *Do strangers care?* Visitor → free-account conversion · signup → first run under 5 min
- ▍ **VALUE** — *Did the recipe work?* Successful first-run rate · eval pass rate
- ▍ **REMIX** — *Does it behave like a network?* Forks per recipe · fork → public remix
- ▍ **DISTRIBUTION** — *Do recipes travel?* Share-link traffic · % signups from outside domains
- ▍ **DISCOVERY** — *Are we the place to look?* Direct traffic · "pipeline recipes" search position

**Footer:** Features & instrumentation proposed by the product team

---

## Slide 12 — Competitive Matrix

[type: matrix]
[brand: NORTHWIND] [page: 12 / 16]

**Eyebrow:** Competitive landscape · 6 capabilities × 4 rivals

**Headline:** No rival has the *combination* — but each leg has a strong competitor.

**Legend:** ● strong · ◐ partial · ○ none/absent · "Northwind" is the owned column

**Matrix:**

| Capability | Northwind | Rival A | Rival B | Rival C |
|---|:--:|:--:|:--:|:--:|
| **Open recipe format** | ● | ◐ | ○ | ◐ |
| **Managed runtime** | ● | ● | ○ | ◐ |
| **Self-tuning loop** | ● | ○ | ● | ○ |
| **Run observability** | ● | ◐ | ● | ◐ |
| **Public registry** | ◐ | ○ | ○ | ● |
| **Operator surface** | ○ | ◐ | ○ | ● |

**Callout:** Northwind is the only column that is ● across the first three rows together. The moat is the *bundle*.

**Footer:** Source: competitive-analysis.md · confidence-flagged

---

## Slide 13 — How the Recipe Improves

[type: compare]
[palette: lavender]
[brand: NORTHWIND] [page: 13 / 16]

**Eyebrow (lavender):** The tune step, concretely

**Headline:** Before and after one self-tuning pass.

**Comparison table:**

| Stage | Before | After |
|---|---|---|
| **Eval pass rate** | 62% | 84% |
| **Schema-drift handling** | manual fix | auto-detected + flagged |
| **Run cost** | baseline | −18% (cheaper model on safe steps) |
| **Time to green** | 3 days | 40 minutes |

**Callout (lavender):** The diff is the proof: recipes are living artifacts, not snapshots.

**Footer:** Illustrative figures · sample deck

---

## Slide 14 — What We're NOT Doing

[type: titlebar]
[brand: NORTHWIND] [page: 14 / 16]

**Eyebrow:** Playing-to-Win discipline · the deliberate no's

**Headline:** What we're deliberately *not* doing — by phase.

**Cards (cols-2):**
- ▍ **DURING PHASE 1** [lavender-accent] — *While we seed the registry, we are **not**:*
  - Buying distribution — no paid sponsorships; content is the only awareness engine
  - Building the operator surface yet — that's Phase 2
  - Building enterprise tiers — those need Enterprise customers
  - Localizing — English-only this cycle
- ▍ **DURING PHASE 2** [amber-accent] — *While we prosecute the operator surface, we are **not**:*
  - Chasing Enterprise — reopens only at month 12
  - Putting SOC 2 on the critical path — runs in the background
  - Racing on connector count — depth on a few, not breadth
  - Splitting the brand — one brand, one clean URL

**Footer:** If a proposal lands in either column, the answer this cycle is **no**.

---

## Slide 15 — The Window

[type: pull-quote-dark]
[palette: amber]
[brand: NORTHWIND] [page: 15 / 16]

**Eyebrow (amber):** Why now

**Pull-quote:** The window to win the registry is *12 months* — before an incumbent bundles it into a feature.

**Footer:** Sample deck · pull-quote template

---

## Slide 16 — Closing

[type: closing]
[brand: NORTHWIND] [page: 16 / 16]

**Eyebrow (amber):** The cascade in one sentence

**Headline:** Win the registry. *Authors first.* Then the operator surface. Then the team chooses.

**Lede:** Strategy refreshed this quarter · re-cascade at the 90 / 180 / 360-day checkpoints. The cascade sets the bar; the team proposes the features that clear it.

**Index footer:**
| Topic | Reference |
|---|---|
| **▍ Cascade** | `STRATEGY.md` |
| **▍ Research** | `customer-research.md` |
| **▍ Competitive** | `competitive-analysis.md` |
| **▍ Format** | `deck-generator/RUNBOOK.md` |

**Footer:** Northwind (fictional) · template showcase for the deck-generator runbook
