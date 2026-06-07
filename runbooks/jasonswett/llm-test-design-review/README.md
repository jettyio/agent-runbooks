# jasonswett/llm-test-design-review — demo payload

A launch payload for the `jasonswett/llm-test-design-review` runbook: the runbook, a
`manifest.json`, and three worked examples — each a real production run that reviews an
RSpec file and reports design-quality violations with fixes.

```
llm-test-design-review/
  RUNBOOK.md                        # the runbook (v1.0.0)
  manifest.json                     # directory metadata: cta, example_outputs[], inputs[], secrets[], meta
  README.md                         # this file
  examples/
    orders-request-spec/            # Ruby/RSpec — request spec (6 findings)
      order_request_spec.rb  input.json  trajectory.json  thumbnail.png
      expected/  review.md (primary) · findings.json · summary.md · validation_report.json
    dashboard-system-spec/          # Ruby/RSpec — system spec (8 findings)
      dashboard_system_spec.rb  input.json  trajectory.json  thumbnail.png  expected/ …
    caching-model-spec/             # Ruby/RSpec — model spec (3 findings)
      caching_model_spec.rb  input.json  trajectory.json  thumbnail.png  expected/ …
```

## Attribution

This runbook is a **conversion, with attribution, of Jason Swett's `test-design-review`
skill** — [github.com/jasonswett/llm-skills](https://github.com/jasonswett/llm-skills/blob/main/test-design-review/SKILL.md).
The review guidelines (tests as executable specifications; assert ends not means; avoid
arbitrariness; one level of abstraction; etc.) are his work. This runbook wraps them in an
executable review process with structured, auditable outputs. The source repo does **not**
carry an explicit license — see "Note" below.

## What it does

Given test code (an RSpec/test file or a diff), the runbook reviews it against the
guideline catalog and, for **each violation**, reports: the guideline id, the offending
code with its location, why it violates the guideline, and a concrete fix — grouped by
guideline (`review.md`) and as structured `findings.json`. A clean file yields `[]`.

## The gallery: three RSpec specs with planted smells

The inputs are **synthetic samples** (a fictional orders app — deliberately *not* Jason's
own examples), each seeded with known test-design smells:

| # | Spec | Planted smells | Findings | Recall | Trajectory |
|---|------|---------------|----------|--------|-----------|
| 1 | request spec | `described_class`, vague `"works"`, `.last`, redundant `be_successful`, `have_received` mock | 6 | 4/5 | `d0436129` |
| 2 | system spec | code-token describe, forward reference, dense setup, `have_current_path`, `instance_variable_set`, cargo-culted `wait: 3` | 8 | 5/6 | `78d5514b` |
| 3 | model spec | caching-mechanism assertion (`Rails.cache.read`), `json_output` coupling | 3 | 2/2 | `cdfa87cc` |

**Across the three: 11/13 planted violations caught (~85% recall)**, all `overall_passed:
true`. The few "extra" findings beyond the planted set were legitimate (e.g. stubbing
`PaymentGateway.new` flagged as coupling to instantiation internals). Treat the runbook as
a strong first-pass reviewer, not an exhaustive linter.

## Reproduce (example 1)

```bash
TOKEN="$(grep '^JETTY_API_TOKEN_JON_RUNBOOKS=' .env | cut -d= -f2-)"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  --form-string 'init_params={"vars":{"focus_guideline":""}}' \
  -F "files=@runbooks/jasonswett/llm-test-design-review/examples/orders-request-spec/order_request_spec.rb" \
  "https://flows-api.jetty.io/api/v1/run/jon-runbooks/llm-test-design-review"
```

## Note on licensing

The source repo (`jasonswett/llm-skills`) has **no explicit license**, so it is
all-rights-reserved by default. This runbook is published here as an **attributed
derivative** (the standard skills→agent-runbooks conversion pattern, with an `origin` link
back to the source). Before featuring it on the public directory, it's worth a courtesy
heads-up to / OK from Jason Swett.
