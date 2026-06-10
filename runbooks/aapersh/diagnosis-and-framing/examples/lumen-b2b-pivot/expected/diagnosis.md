# Strategic Diagnosis — Lumen (Consumer Meditation & Sleep App)

## Executive Read

Lumen is a consumer subscription app with $6.5M ARR and 78,000 paying subscribers that has hit a structurally precarious plateau: monthly churn of 8.5% and a trial-to-paid conversion rate that has deteriorated 31% year-over-year have compressed LTV/CAC to roughly 1.45x — far below the 3x floor required for a paid-acquisition-dependent model to compound. The decision at hand is whether to redirect engineering and commercial resources into a B2B corporate-wellness product (chasing two inbound employer LOIs) or to fix the consumer funnel first. The single most important implication is this: **the B2B opportunity is real but premature — Lumen's unit economics are too broken to fund the 6–12-month infrastructure build a credible enterprise product requires, and chasing the LOIs without fixing retention will produce two half-finished products and accelerate cash burn.** The binding constraint is retention, not acquisition.

---

## 1. Situation Assessment

*Establishes the fact-based baseline before any recommendation.*

### Fact Base

| Area | Evidence (fact) | Interpretation | Confidence |
|---|---|---|---|
| Financial | $6.5M ARR; 78,000 paying subscribers; implied ARPU ~$83/year (~$6.94/month) | Revenue is small relative to the platform investment needed for B2B; ARPU is at the low end for a wellness subscription, limiting pricing headroom | High |
| Financial — unit economics | Blended CAC $42; stated LTV $61 (compressing); LTV/CAC ≈ 1.45x | At 1.45x, paid acquisition economics are marginally profitable at best and deteriorating; healthy SaaS requires ≥3x | High |
| Customer — churn | Monthly subscriber churn 8.5%; implied average subscriber lifespan ~11.8 months | A new subscriber pays back CAC in ~6 months but churn erodes the tail entirely — LTV compression is driven primarily by churn, not pricing | High |
| Customer — conversion | Free-trial-to-paid conversion 4.2%, down from 6.1% one year ago (−31% YoY) | Activation/value-demonstration is degrading; the product is losing fewer casual sign-ups into paid plans, suggesting either content fatigue, onboarding friction, or increased competition for a similar price point | Medium |
| Acquisition | ~80% of acquisition from Meta + TikTok paid ads; 1.1M total installs, 78,000 paying (7.1% install-to-paid) | Heavy paid dependence with no significant organic moat; if CAC continues rising (typical on saturating ad platforms), economics worsen further | High |
| Competitive / market | No community or social features; 400 audio sessions; major competitors (Calm, Headspace) have 10x+ content libraries and established brand | Content depth and social retention loops are absent; differentiation is thin and eroding | Medium |
| Operating | 20 months of runway; 40 employees | Modest buffer; insufficient to build enterprise-grade B2B infrastructure (SSO, admin console, seat management, reporting) without either a raise or deep reallocation from consumer | High |
| B2B signal | Two inbound employer LOIs; zero B2B infrastructure exists | Genuine demand signal, but unvalidated on price, volume, and deal complexity; infrastructure gap is 6–12 months of engineering minimum | Medium |

*Note: stated LTV $61 vs. implied revenue-based LTV ~$82 (at $6.94/mo × 11.8 mo) suggests LTV is calculated net of COGS/support, not gross revenue — this is the correct basis for LTV/CAC. All LTV/CAC analysis uses the stated $61 figure.*

### Momentum Signals

| Signal | Direction | Why It Matters |
|---|---|---|
| Net new paying subscribers (3 consecutive flat quarters) | Flat | Gross adds ≈ churned subscribers each month (~6,600/month at 8.5% churn on 78K base) — the top of the funnel is not compounding |
| Trial-to-paid conversion (4.2% vs 6.1% one year ago) | Deteriorating | Activation efficiency is declining; the same traffic produces fewer subscribers, amplifying CAC pressure |
| LTV/CAC ratio (compressing as churn rises) | Deteriorating | Unit economics are moving in the wrong direction; continued paid acquisition at this ratio is value-destructive |
| Runway (20 months) | Flat / declining | No buffer for a multi-quarter B2B build without compromising consumer product investment |
| B2B inbound demand | Improving | Two unsolicited LOIs suggest genuine employer interest; this is a pull signal, not a push hypothesis |
| Content library (400 sessions, no social) | Flat / stagnant | No evidence of content velocity or community investment; retention-driving features are absent |

### Strategic Issues

1. **Retention is structurally broken.** At 8.5% monthly churn, the business cannot compound regardless of how much it spends on acquisition. This is the most pressing issue.
2. **Paid acquisition dependency with marginal unit economics.** 80% reliance on Meta/TikTok with a 1.45x LTV/CAC ratio means the acquisition engine is one platform-policy or CPM change away from turning cash-negative.
3. **Two competing strategic bets, insufficient resources for both.** The B2B pivot requires product infrastructure that doesn't exist; building it consumes the same engineering capacity needed to fix consumer churn and conversion.

### Open Questions

- What is driving churn? (content exhaustion, price sensitivity, competitor switching, low engagement post-trial?) — without root-cause data, any churn fix is speculative.
- What drove the trial-to-paid conversion decline from 6.1% to 4.2%? (onboarding change, pricing test, competitive alternatives, ad targeting shift?)
- What are the LOI employers actually willing to pay per seat per year, and what minimum feature set do they require before signing a contract?
- What is the organic/referral share of new subscriber acquisition? (the 20% non-paid bucket matters for long-term economics)
- What does cohort retention look like at 30/60/90 days? (helps isolate whether churn is acute in the first 90 days or gradual)

---

## 2. Growth Barrier Diagnosis

*Isolates the constraint that actually binds — not a list of initiatives.*

### Growth Gap

Lumen needs roughly 10–15% net subscriber growth per quarter to justify continued paid acquisition investment and to support a fundraise or B2B pivot from a position of strength. Current trajectory: 0% net subscriber growth for 3 consecutive quarters. At 8.5% monthly churn, Lumen must acquire approximately 6,600 new paid subscribers per month just to hold flat — at $42 CAC, that requires roughly $277K/month ($3.3M/year) in paid acquisition spend, which is ~51% of ARR. This is the treadmill: almost no ARR is compounding; most of it is recirculating through the acquisition engine.

### Driver Tree

```
Net Subscriber Growth
├── Gross New Subscribers
│   ├── Traffic (installs): 1.1M total, ~80% paid
│   ├── Trial Start Rate: not stated (assumption: high; most installs trial)
│   └── Trial-to-Paid Conversion: 4.2% ← DECLINING (was 6.1%)
│       ├── Onboarding effectiveness
│       ├── Content relevance in first 7 days
│       └── Price/value perception at paywall
└── Retained Subscribers
    └── Monthly Churn: 8.5% ← THE CONSTRAINT
        ├── Engagement depth (sessions/week after day 30)
        ├── Content freshness / library breadth
        ├── Social / accountability loops (absent)
        └── Competitive switching (no switching costs)
```

The growth equation breaks at **churn**. Even if trial-to-paid conversion fully recovered to 6.1%, monthly gross adds would increase by ~45% (~3,000 additional paid subs/month) — but at 8.5% monthly churn, that improvement would be absorbed within 2–3 months without a corresponding retention improvement.

### Barrier Assessment

| Driver | Evidence | Impact | Confidence | Root Cause vs Symptom |
|---|---|---|---|---|
| Monthly churn 8.5% | Stated fact; implies avg. lifespan 11.8 months; LTV $61 and compressing | Critical — this is what makes the growth equation zero-sum | High | Root cause (structural) — content exhaustion and absence of social/habit loops are the likely mechanisms; churn itself is the constraint |
| Trial-to-paid conversion decline (4.2% from 6.1%) | Stated fact (−31% YoY) | High — every conversion point lost ≈ 740 fewer paid subs/quarter on current trial volume | Medium | Symptom — likely driven by content/onboarding fatigue or competitive pricing alternatives; root cause unknown without cohort data |
| LTV/CAC compression | Derived: LTV $61 / CAC $42 = 1.45x, declining | High — makes further paid acquisition investment increasingly irrational | High | Symptom of high churn and flat ARPU, not an independent root cause |
| Paid acquisition concentration (80% Meta/TikTok) | Stated fact | Medium now, high risk — concentration creates fragility; no organic flywheel built | Medium | Root cause of fragility, but not the current growth constraint |
| No social / community features | Stated (absent) | Medium — social loops are the primary retention mechanism in habit-based apps | Medium | Root cause of churn (hypothesis — requires validation) |

### Binding Constraint

**Monthly subscriber churn at 8.5% is the single binding constraint.** It directly determines LTV, which directly determines the maximum sustainable CAC, which determines whether paid acquisition compounds or merely treads water. Every other problem (conversion decline, paid concentration, B2B readiness) is either a symptom of poor retention or secondary to it. Fixing acquisition without fixing retention is adding water to a leaking bucket.

### Recommended Actions

1. **Diagnose churn root cause immediately (30 days).** Run exit surveys and analyze engagement data to determine whether churn is driven by content exhaustion (day 30–90 cliff), price sensitivity, or competitive switching. This is a prerequisite — the fix differs materially depending on the cause.
2. **Instrument and optimize the trial experience (30–60 days).** The conversion decline from 6.1% to 4.2% is recent (one year); something changed. A/B test onboarding flows, paywall positioning, and trial length to recover lost conversion before scaling acquisition spend further.
3. **Run a minimum-viable B2B pilot with one LOI employer, capped at one engineer-month (60–90 days).** This validates LOI price/volume assumptions and preserves optionality without diverting the consumer fix. Do not build full infrastructure yet.

---

## 3. Assumption Audit

*Surfaces the load-bearing beliefs and turns the weak ones into tests.*

### Strategy Being Tested

The B2B pivot hypothesis: Lumen redirects meaningful engineering and commercial resources to build a corporate-wellness product (admin console, SSO, seat management, reporting) to convert the two employer LOIs into paying contracts and establish a new, higher-LTV revenue stream — while consumer product investment is reduced or frozen.

### Assumption Register

| Assumption | Category | Importance | Evidence Strength | Risk |
|---|---|---|---|---|
| The two employer LOIs will convert to paid contracts at commercially viable ACV (≥$50K/year each) | Market | Critical | Weak — LOIs signal interest, not commitment or price tolerance | High — LOIs often don't convert, especially when product gaps are disclosed |
| Building minimum enterprise infrastructure (SSO, admin, reporting) takes ≤6 months and ≤3–4 engineers | Operational | Critical | Weak — no scoping data; enterprise auth/admin is consistently underestimated | High — scope creep and compliance requirements routinely double estimates |
| Consumer churn and conversion problems are self-correcting or tolerable while B2B is built | Customer | Critical | Very weak — all trend data points opposite direction | Very high — consumer base will erode further during a 6–12 month diversion |
| B2B corporate-wellness has meaningfully better unit economics (higher LTV, lower churn) than consumer | Economic | High | Medium — B2B wellness contracts typically run 1–3 years; but Lumen has no benchmark data for its own product | Medium — true for the category but unvalidated for Lumen's specific product/price point |
| Lumen's consumer content library is sufficient for corporate-wellness use cases without significant additions | Market | High | Weak — enterprise buyers typically require structured programs, reporting, and curated tracks not needed for consumer | High — content gaps could block or delay LOI conversion |
| Lumen can hire/develop B2B sales capability within 20 months of runway | Organizational | High | Weak — no current B2B sales motion; 40 employees, consumer-focused | High — B2B sales cycles for corporate wellness are 3–9 months; a first close may not arrive before runway pressure |
| Fixing consumer churn is achievable within 2–3 quarters with focused investment | Customer | High | Medium — root cause unknown, but engagement-loop and content improvements have worked for comparable apps | Medium — depends entirely on root cause, which is not yet diagnosed |
| The organic demand signal (inbound LOIs) will hold if Lumen takes 6–9 months to build infrastructure | Market | Medium | Weak — buyers explore multiple vendors simultaneously; delay risks losing the LOI window | Medium |

### Load-Bearing Assumptions

1. **The LOIs will convert at ACV and volume that justify the infrastructure investment.** This is the load-bearing assumption for the B2B hypothesis. If the two employers are price-sensitive, want deeply customized products, or are in long-cycle procurement processes, the LOI signal is noise. Without a validated price point and deal structure, building the infrastructure is speculative. *Why it carries the strategy's weight:* the entire B2B investment case rests on these two deals; there is no pipeline beyond them.

2. **Consumer churn can be meaningfully reduced within 6–9 months through product changes.** This is the load-bearing assumption for the consumer-first hypothesis. If churn is driven by something structural (the product category has inherently low long-term engagement; heavy users switch to free alternatives) rather than something fixable (poor onboarding, content staleness, missing social features), then doubling down on consumer also has a low ceiling. *Why it carries the strategy's weight:* if this assumption fails, neither path produces a fundable outcome within 20 months.

### Test Plan

| Assumption | Test | Data Needed | Owner | Decision Trigger |
|---|---|---|---|---|
| LOIs convert at viable ACV | Run a 2-week structured discovery with each LOI employer: share a prototype/mockup of the admin experience, present pricing at $8–12/seat/month, and request a signed pilot agreement or Letter of Intent with price term | Employer headcount, budget authority confirmation, procurement timeline, minimum feature requirements for a pilot signature | CEO / Head of Partnerships | If neither employer will commit to a pilot agreement at ≥$8/seat/month within 30 days → treat LOIs as unvalidated interest and defer B2B build; if one signs → allocate 1 engineer to minimum viable admin build |
| Consumer churn root cause is fixable | Instrument a 30-day exit survey (triggered at cancellation) and analyze engagement cohorts: sessions/week at day 7, 30, 60 vs. churn probability; identify the day-X cliff | Exit survey responses (n≥200), engagement logs by cohort, cancellation reason codes | Head of Product / Data | If ≥40% of churners cite "ran out of content I wanted" or "stopped using it" → content depth and social loops are the fix; if ≥30% cite price → pricing/packaging test; if ≥30% cite competitor → differentiation/feature gap; each outcome maps to a distinct roadmap priority within 2 weeks of data |

---

## 4. Framed Recommendation

**Verdict:** Test first

Lumen should not make an all-or-nothing choice between B2B and consumer until two empirical tests are complete: a 30-day LOI validation with both employers (structured discovery, prototype demo, and a request for a pilot commitment at a stated price) and a 30-day churn root-cause diagnosis using exit surveys and engagement cohort analysis. These two tests cost roughly one sprint of PM/analyst time and one week of CEO/partnerships time — far less than the cost of a misinformed 6-month bet. The current evidence does not support redirecting engineering resources to B2B infrastructure: the LOIs are unvalidated signals, the infrastructure gap is large, and consumer unit economics are deteriorating in a way that will not resolve itself. The verdict shifts to **Redesign (B2B-led)** if both LOI employers commit to a pilot at ≥$8/seat/month within 30 days, or to **Proceed (consumer fix)** if the churn analysis surfaces a concrete, addressable root cause (content exhaustion, onboarding friction) and the LOIs stall. In either case, the consumer retention problem must be addressed — the enterprise product cannot be built on a collapsing consumer base, and the consumer business cannot survive its current unit economics without a structural retention improvement.
