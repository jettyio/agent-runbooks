---
version: "1.0.0"
evaluation: programmatic
evals_version: 2
agent: claude-code
model: anthropic/claude-haiku-5.5
model_provider: openrouter
snapshot: python312-uv
primary_outputs:
  - result_card.html
origin:
  attribution:
    collection_or_org: jon-smash2026
    skill_name: smash-04-query-log-privacy
    confidence: high
---

# Your Query Is a Patient Record: Attack It, Then Encrypt It (SMASH 2026 · Paper #4)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"Query Logs Are Patient Records: An Unguarded Attack Surface in Clinical RAG, and a Privacy-Preserving Pipeline"** (Louis Tremblay Thibault, Sofiane Azogagh, Marc-Olivier Killijian, Ulrich Aïvodji).
Read the paper: https://arxiv.org/pdf/2609.36376

The paper's claims:
1. **The query log is a patient record.** A clinical RAG provider sees each query embedding. Embeddings are
   invertible to text, and the timestamp cross-referenced with the appointment schedule attaches a patient to the
   working diagnosis. Encryption at rest/in transit and contracts do not cover this inference-time window.
2. **Both retrieval rounds are one primitive.** Scoring (document-embedding matrix × encrypted query) and fetching
   (document-content matrix × encrypted one-hot selection, i.e. PIR) are both *public matrix × encrypted vector*.
   Under FHE the server learns neither the query nor which document it returned, and retrieval is exact.
3. **Quantization is nearly free.** Embeddings quantized to b = 4 bits keep 97% (SciFact) / 95% (NFCorpus) of
   float nDCG@10 for BGE-large; b = 2 collapses.

The participant brings **their own clinical query** and a time of day. The run:
(A) replays a synthetic clinic day and shows what an insider recovers from the provider's log, with the
participant's query added; (B) runs the paper's two-round encrypted retrieval for real (TenSEAL CKKS) on a public
biomedical corpus (BEIR SciFact or NFCorpus), checking that encrypted top-1 == plaintext top-1, sweeping the
quantization bit-width, timing both rounds and extrapolating to 1M documents. Output: a shareable **result card**.

Target wall-clock: **under 4 minutes.** The experiment itself takes ~15–30 s (download ~3 MB corpus + 30 MB embedder).

### The method, as implemented
- **Attack (synthetic).** Appointments in 20-minute slots (08:00–12:00, 13:00–17:00), each with a working diagnosis
  drawn from 60 conditions; the clinician logs a query 1…`query_lag_max_min` minutes after the visit starts (90% of
  visits), plus 2 unrelated background queries. The insider inverts each embedding by nearest neighbour over a
  dictionary of the 60 diagnoses phrased with *different* templates (4 per diagnosis), then joins to the appointment
  in progress at that timestamp. Also repeated on b-bit-quantized embeddings.
- **Quantization.** Global symmetric scalar quantization, scale at the `clip_percentile` of |x| over the corpus,
  integers in ±(2^(b−1) − 1), applied to documents and query (the paper does not specify its scheme; this is ours).
- **Round 1.** Client encrypts the integer query (CKKS, N = 8192, moduli [60, 40, 60], scale 2^40); server computes
  `Enc(q) · Aᵀ` per 4,096-document shard (TenSEAL `matmul`); client decrypts, rounds to integers, takes argmax.
- **Round 2 (PIR).** Client encrypts the one-hot selection vector (all shards, so the server cannot tell which);
  server computes `Enc(e_i*) · D` with D = document bytes (title + abstract, 2,048 bytes, 2 bytes per slot); client
  decrypts and decodes the text.
- **Not reproduced:** the succinct proofs / verifiable FHE (corpus certification), the paper's embedders
  (BGE-large, Cohere v3) and its 48-core server.

### Paper headline numbers (quote exactly)
- Table 1, nDCG@10: SciFact BGE-large b=2 **0.002**, b=4 **0.713**, b=6 0.736, b=8 0.735, float **0.735**;
  Cohere v3 0.033 / 0.719 / 0.721 / 0.719 / 0.718. NFCorpus BGE-large 0.008 / 0.353 / 0.370 / 0.370 / 0.370;
  Cohere v3 0.053 / 0.381 / 0.387 / 0.388 / 0.387.
- "At b = 4 the conventionally trained BGE-large embedder retains 97% (SciFact) and 95% (NFCorpus)".
- "an end-to-end verified private query costs 4.3–8.7 seconds of server time, under two cents".
- "a corpus of one million documents is of roughly 19 minutes and $2.22 per query" (48-core AWS EC2).
- Example: "Metastatic renal cell carcinoma, second-line therapy after progression" at 2:15pm is "a working
  diagnosis for the 2:15pm appointment".

## REQUIRED OUTPUT FILES (MANDATORY)

All in `{{results_dir}}`:

| File | Description |
|---|---|
| `result_card.html` | **Primary output.** Self-contained, shareable one-page result card |
| `results.json` | All computed numbers (written by `experiment.py`) |
| `card_data.json` | Numbers/figures for the card (written by `experiment.py`) |
| `narrative.json` | Your interpretation of this run (Step 4) |
| `fig_*.png` | Figures (written by `experiment.py`) |
| `summary.md` | 5–10 line plain-text summary |
| `validation_report.json` | Evals v2 report: steps, code checks, checklist (see Write Validation Report) |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Your clinical query | `{{your_query}}` | `Metastatic renal cell carcinoma, second-line therapy after progression` | The question a clinician might type into a literature assistant. Added to the synthetic log and run through the encrypted pipeline |
| Logged at | `{{your_query_time}}` | `14:15` | Time of day (HH:MM) the query is logged; the insider joins it to the appointment in progress |
| Corpus | `{{corpus}}` | `scifact` | `scifact` (5,183 abstracts) or `nfcorpus` (3,633 docs), the paper's two BEIR corpora |
| Corpus size | `{{corpus_size}}` | `0` | Cap on documents (0 = all). Capping keeps every judged-relevant doc, so nDCG rises |
| Bit-widths | `{{bit_widths}}` | `2,3,4,6,8` | Quantization bit-widths for the nDCG@10 sweep (each 2–12) |
| Encrypted bit-width | `{{he_bits}}` | `4` | b used in the encrypted run (paper's operating point: 4) |
| Clip percentile | `{{clip_percentile}}` | `99.9` | Percentile of \|x\| that sets the quantization scale; `100` = max-abs (no clipping) |
| Embedder | `{{embedder}}` | `minishlab/potion-base-8M` | model2vec static embedder (30 MB). `minishlab/potion-retrieval-32M` is stronger but a 129 MB download |
| Appointments | `{{n_appointments}}` | `24` | Booked 20-minute slots in the synthetic clinic day (4–24) |
| Lookup lag | `{{query_lag_max_min}}` | `15` | Max minutes between visit start and the clinician's query; beyond the slot length the join starts to mislink |
| Seed | `{{seed}}` | `7` | Random seed for the synthetic clinic and query sample |

## Dependencies

numpy and matplotlib (preinstalled in `python312-uv`), plus `tenseal` (0.3.18, CKKS homomorphic encryption) and
`model2vec` (static embeddings, no torch), installed in Step 1 (~10–30 s). Downloads at run time: the BEIR corpus
zip (~2.5–2.8 MB, UKP server, with a Hugging Face parquet fallback) and the embedder (30 MB from Hugging Face).

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, matplotlib" 2>/dev/null || uv pip install --system -q numpy matplotlib
python -c "import tenseal, model2vec" 2>/dev/null || uv pip install --system -q tenseal==0.3.18 model2vec
python -c "import pandas, pyarrow" 2>/dev/null || uv pip install --system -q pandas pyarrow   # only for the parquet fallback
```

Write `/app/work/params.json`. Use strings for text values and JSON numbers for the rest; if a value still looks
like an unsubstituted `{{…}}` placeholder use the table default. Clamp: `corpus_size` to 0 or [500, 5183],
`he_bits` to [2, 10], `clip_percentile` to [90, 100], `n_appointments` to [4, 24], `query_lag_max_min` to [1, 120];
`corpus` must be `scifact` or `nfcorpus`; `your_query_time` must be HH:MM (else `14:15`); truncate `your_query` to
300 characters. Record any clamp or substitution as a caveat. `n_check_queries` is a fixed budget setting.

```json
{"your_query": "{{your_query}}", "your_query_time": "{{your_query_time}}", "corpus": "{{corpus}}",
 "corpus_size": {{corpus_size}}, "bit_widths": "{{bit_widths}}", "he_bits": {{he_bits}},
 "clip_percentile": {{clip_percentile}}, "embedder": "{{embedder}}", "n_appointments": {{n_appointments}},
 "query_lag_max_min": {{query_lag_max_min}}, "seed": {{seed}}, "n_check_queries": 20, "runbook_url": ""}
```

## Step 2: Get the code (extract it, don't retype it)

The tested implementation of the method is embedded in the **Appendix** at the end of this runbook. Do not
rewrite, "improve", or re-derive it. **Always run the command below first, exactly as written.** It copies the
files out of this runbook's text (which the sandbox exposes to running processes) in about a second, and it is
far faster and more reliable than retyping several hundred lines. Do not skip it on the assumption that it
won't work: run it and read its output.

```bash
cd /app/work && cat > extract.py <<'PYEOF'
"""Extract the runbook's embedded files without retyping them.

The runbook text reaches the agent as one command-line argument, so it is readable from /proc.
Every embedded file sits under a heading "### `/app/work/<name>`" followed by one fenced block.
Exits non-zero if any requested file can't be found, so the caller falls back to writing it by hand.

usage: python3 extract.py <name> [<name> ...]   (writes /app/work/<name>)
"""
import ast, glob, re, sys
from pathlib import Path

want = sys.argv[1:]
cands = []
for p in glob.glob("/proc/[0-9]*/cmdline"):
    try:
        s = Path(p).read_bytes().decode("utf-8", "ignore")
    except OSError:
        continue
    if all(f"### `/app/work/{w}`" in s for w in want):
        cands.append(s)
if not cands:
    sys.exit("runbook text not found in /proc; write the files by hand")
# The agent's own argv holds the raw text; wrapper shells hold a shell-quoted copy, so prefer the shortest
# and undo shell single-quote escaping as a fallback.
best = min(cands, key=len).replace("'\"'\"'", "'")
ok = True
for w in want:
    m = re.search(r"### `/app/work/" + re.escape(w) + r"`\s*\n+```[a-z]*\n(.*?)\n```\n", best, re.S)
    if not m or len(m.group(1)) < 50:
        print(f"MISSING {w}"); ok = False; continue
    code = m.group(1) + "\n"
    if w.endswith(".py"):
        try:
            ast.parse(code)
        except SyntaxError as e:
            print(f"MISSING {w} (extracted text does not parse: {e})"); ok = False; continue
    Path("/app/work", w).write_text(code)
    print(f"extracted {w}: {code.count(chr(10))} lines")
sys.exit(0 if ok else 1)
PYEOF
python3 extract.py experiment.py render_card.py validate.py
```

If it exits non-zero or prints `MISSING`, write each missing file from the Appendix **exactly as given**, one
heredoc per file (quoted delimiter, e.g. `cat > experiment.py <<'PYEOF'`). If a later step fails, fix only
environment problems (missing package, network retry), never the methodology.

## Step 3: Run the experiment

```bash
cd /app/work && export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 SMASH_CPUS=4 && timeout 300 python -W ignore experiment.py params.json {{results_dir}}
```

Expected: 15–40 s. Ends with a `done:` line (attack recovery, nDCG retention at the encrypted bit-width, encrypted
top-1 matches, server seconds, 1M-doc extrapolation). If a download fails, retry once; if the embedder named in
`embedder` cannot be loaded, fall back to `minishlab/potion-base-8M` and say so in a caveat.

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4). Each findings paragraph ≤ 70 words; bold the one number that matters.

- **headline** (≤ 30 words): a finding, with 1–2 numbers copied from `results.json`: typically
  `attack.records_recovered` of `attack.n_patient_queries` and the b = `he_bits` retention
  (`quant_sweep[].retain`), or, if `he_bits` ≤ 2, that the encrypted run is exact but retrieval has collapsed.
- **idea**: the three claims above in plain language.
- **findings**: (1) the attack: `attack.dx_top1` (vs `chance_top1`), `link_acc`, where the participant's query
  (`attack.your_query`: `top3`, `linked_patient`, `appointment`) landed, and that quantization does not protect
  (`dx_top1_quantized`); if `link_acc` is low, explain the lookup lag vs the 20-minute slot (`lag_sweep`).
  (2) quantization: nDCG@10 at `he_bits` vs `ndcg10_float` and the b = 2 value, vs the paper's Table 1 for the same
  corpus; say the absolute level differs because the embedder differs. (3) encrypted retrieval: `top1_match`/`n_check`,
  `scores_exact`, `pir_fetch_exact`, `server_sec_total` vs `plain_score_sec`, `server_min_1M` vs the paper's ~19 min,
  and what the retrieved document was (`your_query_retrieval.top_doc_title`).
- **try_next**: 2–3 contrasting runs with exact values using only the keys `your_query, your_query_time, corpus,
  corpus_size, bit_widths, he_bits, clip_percentile, embedder, n_appointments, query_lag_max_min, seed`. Good
  contrasts: `he_bits` 2 (exact but useless), `query_lag_max_min` 45 (join mislinks), `corpus` `nfcorpus`,
  `clip_percentile` 100 (naive scaling hurts at b = 4).
- **caveats**: synthetic clinic and patients; dictionary inversion is a lower bound on a trained inverter; no
  verifiable proofs (corpus certification not reproduced) and different hardware, so timing is indicative;
  our quantization scheme and small embedder; any substitutions you made. Never imply a real patient was exposed.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: query and time, attack recovery and linkage, nDCG@10 by bit-width,
encrypted exactness, server time and 1M extrapolation, headline).

## Writing style for narrative.json

These rules apply to every field and override any longer limits stated earlier in this runbook. Let the paper
and the numbers speak; the card is not the place for commentary.

- **Length:** `headline` one sentence; `idea` 1–3 bullets of at most 30 words; `findings` 1–2 paragraphs of at
  most 60 words each; `caveats` 1–2 bullets of at most 20 words. Cut anything the tiles, figures or tables
  already show.
- **Plain statements of what was measured.** Write "Sensitivity gap −0.284 [−0.354, −0.218]; the paper reports
  +0.088", not an interpretation of what it means for the field.
- **Avoid:** em-dash asides; "not X, but Y" framings; colon-then-reveal sentences; rhetorical questions; words
  such as *crucially, notably, strikingly, remarkably, collapses, illustrating, underscores, highlights, delve,
  powerful, key insight, worth noting*; exclamation marks; restating the method before the result.
- Use the paper's own terms for its concepts. Quote the paper's numbers exactly.

## Code Checks

Jetty runs these checks itself in the sandbox after the agent finishes, so they cannot be skipped or
misreported. `validate.py` (see Write Validation Report) runs the same checks first so you can fix problems before you stop.

### outputs-exist — Result card, numbers, narrative and summary were written

```bash
cd {{results_dir}} && for f in result_card.html results.json card_data.json narrative.json summary.md; do test -s "$f" || { echo "missing or empty: $f"; exit 1; }; done; echo "all 5 outputs present"
```

### results-valid — Experiment numbers are valid JSON and the experiment stayed within its time budget

```bash
python3 - "{{results_dir}}" 300 <<'PY'
import json, sys
from pathlib import Path
R, budget = Path(sys.argv[1]), float(sys.argv[2])
res = json.loads((R / "results.json").read_text())
json.loads((R / "card_data.json").read_text())
rt = float(res.get("runtime_sec", 0))
if rt > budget:
    sys.exit(f"experiment took {rt}s, budget {budget}s")
print(f"results.json and card_data.json parse; experiment {rt}s within {budget:.0f}s")
PY
```

### narrative-complete — The narrative is complete and within the length limits

```bash
python3 - "{{results_dir}}" <<'PY'
import json, sys
from pathlib import Path
n = json.loads((Path(sys.argv[1]) / "narrative.json").read_text())
problems = []
if not str(n.get("headline", "")).strip(): problems.append("no headline")
if len(str(n.get("headline", "")).split()) > 45: problems.append("headline over 45 words")
if not 1 <= len(n.get("idea", [])) <= 3: problems.append(f"idea has {len(n.get('idea', []))} bullets, need 1-3")
if not 1 <= len(n.get("findings", [])) <= 2: problems.append(f"{len(n.get('findings', []))} findings, need 1-2")
if any(len(f.split()) > 70 for f in n.get("findings", [])): problems.append("a findings paragraph is over 60 words")
if not 2 <= len(n.get("try_next", [])) <= 3: problems.append(f"{len(n.get('try_next', []))} try_next, need 2-3")
if not 1 <= len(n.get("caveats", [])) <= 2: problems.append(f"{len(n.get('caveats', []))} caveats, need 1-2")
if problems: sys.exit("; ".join(problems))
print("headline, %d idea bullets, %d findings, %d try_next, %d caveats" % (len(n["idea"]), len(n["findings"]), len(n["try_next"]), len(n["caveats"])))
PY
```

### try-next-valid — Every try-next suggestion uses only this runbook's parameters

```bash
python3 - "{{results_dir}}" "your_query,your_query_time,corpus,corpus_size,bit_widths,he_bits,clip_percentile,embedder,n_appointments,query_lag_max_min,seed" <<'PY'
import json, sys
from pathlib import Path
allowed = set(sys.argv[2].split(","))
n = json.loads((Path(sys.argv[1]) / "narrative.json").read_text())
bad = sorted({k for t in n.get("try_next", []) for k in (t.get("params") or {}) if k not in allowed})
empty = [t.get("label", "?") for t in n.get("try_next", []) if not t.get("params")]
if bad or empty: sys.exit(f"unknown parameters: {bad}; suggestions without params: {empty}")
print("all try_next parameters are declared runbook parameters")
PY
```

### headline-grounded — Every number in the headline appears in the run's results

```bash
python3 - "{{results_dir}}" <<'PY'
import json, re, sys
from pathlib import Path
R = Path(sys.argv[1])
blob = (R / "results.json").read_text() + (R / "card_data.json").read_text()
vals = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?", blob)]
head = json.loads((R / "narrative.json").read_text())["headline"]
nums = re.findall(r"(?<![\w.−-])[−-]?\d[\d,]*(?:\.\d+)?(?![\w-])", head)
missing = []
for n in nums:
    s = n.replace("−", "-").replace(",", ""); v = float(s); dec = len(s.split(".")[1]) if "." in s else 0
    tol = 0.5 * 10 ** (-dec) + 1e-9
    if not any(abs(abs(x) - abs(v)) <= tol or abs(abs(x * 100) - abs(v)) <= max(tol, 0.5) for x in vals):
        missing.append(n)
if missing: sys.exit(f"headline numbers not found in results: {missing}")
print(f"{len(nums)} headline number(s) all grounded in results")
PY
```

### card-integrity — The card embeds its figures, shows the headline, and contains no NaN

```bash
python3 - "{{results_dir}}" <<'PY'
import html, json, re, sys
from pathlib import Path
R = Path(sys.argv[1])
card = (R / "result_card.html").read_text()
text = re.sub(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+", "", card)
head = json.loads((R / "narrative.json").read_text())["headline"]
problems = []
if card.count("data:image/png;base64") < 1: problems.append("no embedded figures")
if re.search(r"\bNaN\b|\bnan%|\bInfinity\b", text): problems.append("NaN/Infinity in card text")
if len(card) > 5_000_000: problems.append(f"card is {len(card) // 1024} KB")
plain = html.unescape(re.sub(r"<[^>]+>", "", text))
if re.sub(r"[*`]", "", head)[:40] not in plain: problems.append("headline not on card")
if problems: sys.exit("; ".join(problems))
print(f"card {len(card) // 1024} KB, {card.count('data:image/png;base64')} figures, headline present")
PY
```

## Checklist

- [ ] The headline states this run's finding with its numbers, not a description of the method
- [ ] Paper numbers are quoted exactly and any disagreement with the paper is stated plainly
- [ ] Caveats say what is synthetic, reconstructed or an extension of the paper
- [ ] Each try-next suggestion would plausibly give a contrasting result

## Write Validation Report

Judge the four Checklist items honestly against your outputs and write them to `/app/work/checklist.json` as a
list, using the checklist ids Jetty gives you (one entry per item):

```json
[{"id": "<checklist id>", "status": "pass", "message": "one line on why"}]
```

Then write the report and self-check in one command:

```bash
cd /app/work && python3 validate.py {{results_dir}} your_query,your_query_time,corpus,corpus_size,bit_widths,he_bits,clip_percentile,embedder,n_appointments,query_lag_max_min,seed 300 checklist.json
```

`validate.py` writes `{{results_dir}}/validation_report.json` in the v2 shape Jetty reads (`version: 2`, one
`step` entry per runbook step, one `code_check` entry per check above, one `checklist` entry per item). Jetty
replaces the `code_check` entries with its own independent run of the same checks. Do not write the report by hand.

## Iteration (up to 2 rounds)

If `validate.py` prints any `FAIL`, fix the named problem (usually a headline number that does not match
`results.json`, or an unknown `try_next` key), re-render the card (Step 5) and rerun the command above. Never
rerun the experiment just to change the narrative.

## Appendix: code

These files are extracted verbatim in Step 2.

### `/app/work/experiment.py`

```python
"""Query logs are patient records — SMASH 2026 paper #4 (Tremblay Thibault, Aïvodji, Azogagh, Killijian).

Two halves, both run for real:
  A. The attack. A synthetic clinic day (appointments) and the retrieval provider's log (timestamp + query
     embedding). An insider inverts each logged embedding with a nearest-neighbour dictionary attack and joins it to
     the appointment schedule by timestamp: the log becomes a list of (patient, working diagnosis) pairs.
  B. The defence. Both retrieval rounds as plaintext-matrix x encrypted-vector products under CKKS homomorphic
     encryption (TenSEAL) on a real public biomedical corpus (BEIR SciFact or NFCorpus): Round 1 scores the
     encrypted, b-bit-quantized query against every document; Round 2 fetches the top document with an encrypted
     one-hot selection vector (private information retrieval). Plus nDCG@10 vs quantization bit-width, an
     exactness check (encrypted scores == plaintext integer scores), timing and a 1M-document extrapolation.
Not reproduced: the succinct proofs / verifiable FHE (corpus certification) and the paper's 48-core server.

usage: python experiment.py params.json outdir
"""
import io, json, os, sys, time, zipfile, urllib.request
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
SEED = int(P.get("seed", 7))
rng = np.random.default_rng(SEED)
INK, ACC, BLUE, MUTED, GOOD = "#1f2a44", "#d9480f", "#1971c2", "#868e96", "#2b8a3e"

# Paper Table 1 (nDCG@10 by bit-width) and cost figures, quoted exactly.
PAPER_NDCG = {"scifact": {"BGE-large": {2: 0.002, 4: 0.713, 6: 0.736, 8: 0.735, "float": 0.735},
                          "Cohere v3": {2: 0.033, 4: 0.719, 6: 0.721, 8: 0.719, "float": 0.718}},
              "nfcorpus": {"BGE-large": {2: 0.008, 4: 0.353, 6: 0.370, 8: 0.370, "float": 0.370},
                           "Cohere v3": {2: 0.053, 4: 0.381, 6: 0.387, 8: 0.388, "float": 0.387}}}
PAPER_RETAIN_B4 = {"scifact": "97%", "nfcorpus": "95%"}
CORPUS_DOCS = {"scifact": 5183, "nfcorpus": 3633}


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def fetch(url, tries=2):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return r.read()
        except Exception as ex:  # network hiccup: retry once
            if k == tries - 1:
                raise
            log(f"retry {url}: {ex}")


# ------------------------------------------------------------------ synthetic clinic (attack)
# (working diagnosis, specialty). The attacker's dictionary is built from these names with *different* phrasings
# than the clinician's queries, so inversion is a genuine nearest-neighbour match, not string lookup.
DX = [("metastatic renal cell carcinoma", "oncology"), ("HER2-positive breast cancer", "oncology"),
      ("non-small cell lung cancer with EGFR mutation", "oncology"), ("multiple myeloma", "oncology"),
      ("pancreatic adenocarcinoma", "oncology"), ("glioblastoma", "oncology"), ("metastatic melanoma", "oncology"),
      ("chronic lymphocytic leukemia", "oncology"), ("major depressive disorder", "psychiatry"),
      ("bipolar disorder", "psychiatry"), ("schizophrenia", "psychiatry"), ("anorexia nervosa", "psychiatry"),
      ("opioid use disorder", "psychiatry"), ("alcohol use disorder", "psychiatry"),
      ("post-traumatic stress disorder", "psychiatry"), ("HIV infection", "infectious disease"),
      ("chronic hepatitis C", "infectious disease"), ("syphilis", "infectious disease"),
      ("latent tuberculosis", "infectious disease"), ("Lyme disease", "infectious disease"),
      ("type 1 diabetes", "endocrinology"), ("type 2 diabetes", "endocrinology"), ("Graves disease", "endocrinology"),
      ("Cushing syndrome", "endocrinology"), ("heart failure with reduced ejection fraction", "cardiology"),
      ("atrial fibrillation", "cardiology"), ("hypertrophic cardiomyopathy", "cardiology"),
      ("pulmonary arterial hypertension", "cardiology"), ("multiple sclerosis", "neurology"),
      ("Parkinson disease", "neurology"), ("early-onset Alzheimer disease", "neurology"), ("epilepsy", "neurology"),
      ("amyotrophic lateral sclerosis", "neurology"), ("Huntington disease", "neurology"),
      ("rheumatoid arthritis", "rheumatology"), ("systemic lupus erythematosus", "rheumatology"),
      ("ankylosing spondylitis", "rheumatology"), ("Crohn disease", "gastroenterology"),
      ("ulcerative colitis", "gastroenterology"), ("alcoholic cirrhosis", "gastroenterology"),
      ("celiac disease", "gastroenterology"), ("chronic kidney disease stage 4", "nephrology"),
      ("polycystic kidney disease", "nephrology"), ("ectopic pregnancy", "obstetrics"),
      ("preeclampsia", "obstetrics"), ("polycystic ovary syndrome", "gynecology"), ("endometriosis", "gynecology"),
      ("infertility", "gynecology"), ("erectile dysfunction", "urology"), ("prostate cancer", "urology"),
      ("COPD exacerbation", "pulmonology"), ("cystic fibrosis", "pulmonology"), ("idiopathic pulmonary fibrosis", "pulmonology"),
      ("sickle cell disease", "hematology"), ("hemophilia A", "hematology"), ("psoriasis", "dermatology"),
      ("gender dysphoria", "endocrinology"), ("obesity", "endocrinology"), ("migraine", "neurology"),
      ("sleep apnea", "pulmonology")]
CLIN_TPL = ["{dx}, second-line therapy after progression", "first-line management of {dx} in a {age}-year-old",
            "{dx} with {comorb}: which treatment options?", "diagnostic workup for suspected {dx}",
            "drug interactions between {drug} and treatment for {dx}", "{dx} in pregnancy: what is safe?",
            "long-term outcomes of {dx}", "latest guideline recommendations for {dx}",
            "{dx} refractory to standard therapy, next steps", "managing {dx} in a patient with renal impairment"]
ATK_TPL = ["{dx}", "treatment of {dx}", "{dx} diagnosis and management", "{dx} clinical guidelines"]
COMORB = ["chronic kidney disease", "obesity", "atrial fibrillation", "hypertension", "liver disease", "depression"]
DRUGS = ["warfarin", "methotrexate", "lithium", "tacrolimus", "amiodarone", "an SSRI"]
BACKGROUND = ["recent advances in CRISPR gene therapy", "statistics refresher: number needed to treat",
              "vitamin D supplementation in healthy adults", "burnout among primary care physicians"]


def clock(minutes):
    return f"{int(minutes // 60):02d}:{int(minutes % 60):02d}"


def parse_clock(s):
    try:
        h, m = str(s).strip().split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return 14 * 60 + 15


def clinic_day(n_appt, slot, lag_max):
    """Appointment slots 08:00-12:00 and 13:00-17:00; each patient gets a working diagnosis. The clinician queries
    the provider during or after the visit (lag uniform in [1, lag_max] min); a few background queries are mixed in."""
    starts = [8 * 60 + k * slot for k in range(int(240 // slot))] + [13 * 60 + k * slot for k in range(int(240 // slot))]
    starts = sorted(rng.choice(starts, size=min(n_appt, len(starts)), replace=False))
    dx_idx = rng.choice(len(DX), size=len(starts), replace=False if len(starts) <= len(DX) else True)
    appts = [{"start": int(s), "patient": f"MRN-{rng.integers(10000, 99999)}", "dx": DX[i][0], "specialty": DX[i][1]}
             for s, i in zip(starts, dx_idx)]
    queries = []
    for k, a in enumerate(appts):
        if rng.random() < 0.9:  # most visits produce at least one lookup
            tpl = CLIN_TPL[rng.integers(len(CLIN_TPL))]
            text = tpl.format(dx=a["dx"], age=int(rng.integers(19, 88)), comorb=COMORB[rng.integers(len(COMORB))],
                              drug=DRUGS[rng.integers(len(DRUGS))])
            queries.append({"t": float(a["start"] + rng.uniform(1, lag_max)), "text": text, "true_appt": k, "true_dx": a["dx"]})
    for b in rng.choice(len(BACKGROUND), size=2, replace=False):
        queries.append({"t": float(rng.uniform(8 * 60, 17 * 60)), "text": BACKGROUND[b], "true_appt": None, "true_dx": None})
    return appts, sorted(queries, key=lambda q: q["t"])


def attribute(t, appts, slot):
    """The insider's join: the appointment in progress (or just finished) when the query arrived."""
    cand = [k for k, a in enumerate(appts) if a["start"] <= t]
    if not cand:
        return None
    k = cand[-1]
    return k if t - appts[k]["start"] <= slot * 2 else None


# ------------------------------------------------------------------ corpus
def load_beir(name):
    try:
        z = zipfile.ZipFile(io.BytesIO(fetch(f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{name}.zip")))
        corpus = [json.loads(l) for l in z.open(f"{name}/corpus.jsonl")]
        queries = {j["_id"]: j["text"] for j in map(json.loads, z.open(f"{name}/queries.jsonl"))}
        rows = [l.split("\t") for l in z.open(f"{name}/qrels/test.tsv").read().decode().splitlines()[1:]]
        src = "BEIR zip (UKP)"
    except Exception as ex:  # mirror: Hugging Face parquet (BeIR corpus/queries + mteb qrels)
        log(f"BEIR zip failed ({ex}); using Hugging Face parquet mirror")
        import pandas as pd
        hf = "https://huggingface.co/api/datasets"
        c = pd.read_parquet(io.BytesIO(fetch(f"{hf}/BeIR/{name}/parquet/corpus/corpus/0.parquet")))
        q = pd.read_parquet(io.BytesIO(fetch(f"{hf}/BeIR/{name}/parquet/queries/queries/0.parquet")))
        r = pd.read_parquet(io.BytesIO(fetch(f"{hf}/mteb/{name}/parquet/default/test/0.parquet")))
        corpus = [{"_id": str(a), "title": t or "", "text": x or ""} for a, t, x in zip(c["_id"], c["title"], c["text"])]
        queries = dict(zip(q["_id"].astype(str), q["text"]))
        rows = [[str(a), str(b), str(s)] for a, b, s in zip(r.iloc[:, 0], r.iloc[:, 1], r.iloc[:, 2])]
        src = "Hugging Face parquet mirror"
    qrels = {}
    for qid, did, s in rows:
        if int(float(s)) > 0:
            qrels.setdefault(qid, {})[did] = int(float(s))
    return corpus, queries, qrels, src


def ndcg10(S, qids, qrels, ids):
    top = np.argsort(-S, axis=1, kind="stable")[:, :10]
    out = []
    for i, q in enumerate(qids):
        rel = qrels[q]
        dcg = sum(rel.get(ids[j], 0) / np.log2(r + 2) for r, j in enumerate(top[i]))
        ideal = sorted(rel.values(), reverse=True)[:10]
        out.append(dcg / sum(v / np.log2(r + 2) for r, v in enumerate(ideal)))
    return float(np.mean(out))


def quantizer(D, clip_pct):
    """Global symmetric b-bit scalar quantization (our assumption; the paper does not specify its scheme): one scale
    for all dimensions, set at the clip_pct percentile of |x| over the corpus; values clipped to ±(2^(b-1) − 1)."""
    amax = float(np.percentile(np.abs(D), clip_pct)) if clip_pct < 100 else float(np.abs(D).max())

    def q(X, b):
        L = 2 ** (b - 1) - 1
        return np.clip(np.round(X / (amax / L)), -L, L).astype(np.int64)
    return q


def main():
    corpus_name = str(P.get("corpus", "scifact")).lower()
    if corpus_name not in CORPUS_DOCS:
        corpus_name = "scifact"
    bits = sorted({int(b) for b in str(P.get("bit_widths", "2,3,4,6,8")).replace(" ", "").split(",") if b and 2 <= int(b) <= 12})
    he_bits = int(P.get("he_bits", 4))
    clip_pct = float(P.get("clip_percentile", 99.9))
    embedder = str(P.get("embedder", "minishlab/potion-base-8M"))
    res = {"params": P}

    # ---------------- embedder
    from model2vec import StaticModel
    t = time.time(); model = StaticModel.from_pretrained(embedder); res["embedder_load_sec"] = round(time.time() - t, 1)
    def emb(texts):
        E = np.asarray(model.encode(list(texts)), dtype=np.float64)
        return E / np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)
    log(f"embedder {embedder} loaded in {res['embedder_load_sec']} s")

    # ---------------- A. the attack on a synthetic clinic day
    slot, lag_max = 20, float(P.get("query_lag_max_min", 15))
    appts, queries = clinic_day(int(P.get("n_appointments", 24)), slot, lag_max)
    your_q = str(P.get("your_query", "")).strip() or "Metastatic renal cell carcinoma, second-line therapy after progression"
    your_t = parse_clock(P.get("your_query_time", "14:15"))
    dict_texts, dict_dx = [], []
    for dx, _ in DX:
        for tpl in ATK_TPL:
            dict_texts.append(tpl.format(dx=dx)); dict_dx.append(dx)
    Dict = emb(dict_texts); dict_dx = np.array(dict_dx)
    Qlog = emb([q["text"] for q in queries] + [your_q])
    qfun_atk = quantizer(Dict, clip_pct)

    def invert(V):
        sims = V @ Dict.T
        out = []
        for row in sims:  # best phrasing per diagnosis, then rank diagnoses
            best = {}
            for j in np.argsort(-row):
                best.setdefault(dict_dx[j], float(row[j]))
                if len(best) >= 3:
                    break
            out.append(list(best.items()))
        return out
    inv_f = invert(Qlog)
    Vq = qfun_atk(Qlog, he_bits).astype(float); Vq /= np.maximum(np.linalg.norm(Vq, axis=1, keepdims=True), 1e-12)
    inv_q = invert(Vq)
    record = []
    for i, q in enumerate(queries):
        k = attribute(q["t"], appts, slot)
        rec = {"time": clock(q["t"]), "query": q["text"], "recovered_dx": inv_f[i][0][0], "sim": round(inv_f[i][0][1], 3),
               "top3": [d for d, _ in inv_f[i]], "recovered_dx_quantized": inv_q[i][0][0],
               "linked_patient": appts[k]["patient"] if k is not None else None,
               "true_dx": q["true_dx"], "true_patient": appts[q["true_appt"]]["patient"] if q["true_appt"] is not None else None}
        rec["dx_correct"] = rec["recovered_dx"] == q["true_dx"]
        rec["dx_top3"] = q["true_dx"] in rec["top3"]
        rec["link_correct"] = (k == q["true_appt"]) and k is not None
        rec["record_correct"] = rec["dx_correct"] and rec["link_correct"]
        record.append(rec)
    pq = [r for r in record if r["true_dx"]]
    k_you = attribute(your_t, appts, slot)
    you = {"time": clock(your_t), "query": your_q, "top3": [[d, round(s, 3)] for d, s in inv_f[-1]],
           "linked_patient": appts[k_you]["patient"] if k_you is not None else None,
           "appointment": clock(appts[k_you]["start"]) if k_you is not None else None,
           "recovered_dx_quantized": inv_q[-1][0][0]}
    # linkage sensitivity: how often the timestamp join picks the right patient as the lookup lag grows
    lag_sweep = []
    for lm in [5, 10, 15, 20, 30, 45, 60]:
        ok = n = 0
        for a_k, a in enumerate(appts):
            for _ in range(20):
                tt = a["start"] + rng.uniform(1, lm); n += 1; ok += attribute(tt, appts, slot) == a_k
        lag_sweep.append({"lag_max_min": lm, "link_acc": ok / n})
    res["attack"] = {"n_appointments": len(appts), "n_patient_queries": len(pq), "n_background_queries": len(record) - len(pq),
                     "dictionary_size": len(DX), "dictionary_phrasings": len(dict_texts),
                     "dx_top1": float(np.mean([r["dx_correct"] for r in pq])), "dx_top3": float(np.mean([r["dx_top3"] for r in pq])),
                     "dx_top1_quantized": float(np.mean([r["recovered_dx_quantized"] == r["true_dx"] for r in pq])),
                     "link_acc": float(np.mean([r["link_correct"] for r in pq])),
                     "records_recovered": int(sum(r["record_correct"] for r in pq)),
                     "chance_top1": 1 / len(DX), "background_falsely_linked": int(sum(r["linked_patient"] is not None for r in record if not r["true_dx"])),
                     "lag_sweep": lag_sweep, "record": record, "your_query": you}
    log(f"attack: diagnosis recovered {res['attack']['dx_top1']:.0%} (top-3 {res['attack']['dx_top3']:.0%}), "
        f"linked {res['attack']['link_acc']:.0%}; {res['attack']['records_recovered']}/{len(pq)} full (patient, diagnosis) records")

    # ---------------- B1. quantization vs retrieval quality on a real corpus
    corpus, qtext, qrels, src = load_beir(corpus_name)
    nmax = int(P.get("corpus_size", 0) or 0)
    if nmax and nmax < len(corpus):  # keep every judged-relevant doc, fill with others (deterministic)
        relevant = {d for r in qrels.values() for d in r}
        keep = [c for c in corpus if c["_id"] in relevant]
        others = [c for c in corpus if c["_id"] not in relevant]
        sel = rng.choice(len(others), size=max(0, nmax - len(keep)), replace=False) if nmax > len(keep) else []
        corpus = keep[:nmax] + [others[i] for i in sorted(sel)]
    ids = np.array([c["_id"] for c in corpus]); idset = set(ids)
    qids = [q for q in qrels if q in qtext and any(d in idset for d in qrels[q])]
    log(f"{corpus_name}: {len(corpus)} docs, {len(qids)} test queries ({src})")
    t = time.time()
    D = emb([(c.get("title") or "") + " " + (c.get("text") or "") for c in corpus]); Q = emb([qtext[q] for q in qids])
    res["embed_sec"] = round(time.time() - t, 2)
    S_float = Q @ D.T
    nd_float = ndcg10(S_float, qids, qrels, ids)
    qfun = quantizer(D, clip_pct); qmax = quantizer(D, 100.0)
    sweep = []
    for b in sorted(set(bits) | {he_bits}):
        Dq, Qq = qfun(D, b), qfun(Q, b)
        Sq = (Qq @ Dq.T).astype(float)
        nd = ndcg10(Sq, qids, qrels, ids)
        nd_max = ndcg10((qmax(Q, b) @ qmax(D, b).T).astype(float), qids, qrels, ids)
        top1_agree = float(np.mean(np.argmax(Sq, 1) == np.argmax(S_float, 1)))
        sweep.append({"bits": b, "ndcg10": nd, "retain": nd / nd_float, "ndcg10_maxabs": nd_max, "top1_agree_float": top1_agree})
    res.update(corpus=corpus_name, corpus_source=src, n_docs=len(corpus), n_test_queries=len(qids),
               ndcg10_float=nd_float, quant_sweep=sweep, dim=int(D.shape[1]), clip_percentile=clip_pct)
    sb = {s["bits"]: s for s in sweep}
    log("nDCG@10 float {:.3f}; ".format(nd_float) + ", ".join(f"b={s['bits']}: {s['ndcg10']:.3f}" for s in sweep))

    # ---------------- B2. encrypted two-round retrieval (CKKS)
    import tenseal as ts
    N = 8192
    t = time.time()
    ctx = ts.context(ts.SCHEME_TYPE.CKKS, N, coeff_mod_bit_sizes=[60, 40, 60]); ctx.global_scale = 2 ** 40
    ctx.generate_galois_keys(); keygen = time.time() - t
    slots = N // 2
    Dq = qfun(D, he_bits)
    chunks = [np.arange(i, min(i + slots, len(D))) for i in range(0, len(D), slots)]
    At = [Dq[c].T.tolist() for c in chunks]  # server's public matrix, column-sharded to fit the slots

    def round1(qint):
        t0 = time.time(); enc = ts.ckks_vector(ctx, qint.tolist()); t1 = time.time()
        outs = [enc.matmul(a) for a in At]; t2 = time.time()
        scores = np.concatenate([np.array(o.decrypt()) for o in outs]); t3 = time.time()
        return scores, {"encrypt": t1 - t0, "server": t2 - t1, "decrypt": t3 - t2,
                        "up_bytes": len(enc.serialize()), "down_bytes": sum(len(o.serialize()) for o in outs)}
    n_check = min(int(P.get("n_check_queries", 20)), len(qids))
    chk = rng.choice(len(qids), size=n_check, replace=False)
    exact = top1 = 0; tim = []; maxerr = 0.0
    for i in chk:
        qint = qfun(Q[i:i + 1], he_bits)[0]
        sc, tm = round1(qint); tim.append(tm)
        plain = (Dq @ qint).astype(float)
        maxerr = max(maxerr, float(np.abs(sc - plain).max()))
        exact += int(np.array_equal(np.round(sc), plain)); top1 += int(np.argmax(np.round(sc)) == np.argmax(plain))
    r1 = {k: float(np.mean([x[k] for x in tim])) for k in tim[0]}
    log(f"round 1 encrypted on {n_check} queries: exact {exact}/{n_check}, top-1 match {top1}/{n_check}, "
        f"server {r1['server']:.3f} s")

    # the participant's own query, both rounds
    qy = qfun(emb([your_q]), he_bits)[0]
    sc, tm_y = round1(qy); istar = int(np.argmax(np.round(sc)))
    plain_top = int(np.argmax(Dq @ qy)); float_top = int(np.argmax(D @ emb([your_q])[0]))
    DOC_BYTES = 2048
    def doc_bytes(c):
        b = ((c.get("title") or "") + "\n" + (c.get("text") or "")).encode("utf-8")[:DOC_BYTES]
        b = b + b"\0" * (DOC_BYTES - len(b))
        return np.frombuffer(b, dtype=">u2").astype(np.int64)  # two bytes per CKKS slot
    t = time.time()
    Dc = np.stack([doc_bytes(c) for c in corpus])
    rows = [np.arange(i, min(i + slots, len(D))) for i in range(0, len(D), slots)]
    Dlists = [Dc[r].tolist() for r in rows]; prep2 = time.time() - t
    t0 = time.time()
    sel = [ts.ckks_vector(ctx, (r == istar).astype(float).tolist()) for r in rows]; t1 = time.time()
    acc_ct = None
    for e_, m_ in zip(sel, Dlists):
        part = e_.matmul(m_); acc_ct = part if acc_ct is None else acc_ct + part
    t2 = time.time()
    got = np.clip(np.round(np.array(acc_ct.decrypt())), 0, 65535).astype(">u2").tobytes(); t3 = time.time()
    fetched = got.rstrip(b"\0").decode("utf-8", "ignore")
    truth = doc_bytes(corpus[istar]).astype(">u2").tobytes().rstrip(b"\0").decode("utf-8", "ignore")
    r2 = {"encrypt": t1 - t0, "server": t2 - t1, "decrypt": t3 - t2, "up_bytes": sum(len(e_.serialize()) for e_ in sel),
          "down_bytes": len(acc_ct.serialize()), "prep": prep2}
    title = (corpus[istar].get("title") or fetched.split("\n")[0])[:160]
    log(f"round 2 (PIR) fetched doc {istar} exactly: {fetched == truth}; server {r2['server']:.2f} s")

    n = len(D)
    per_doc = (r1["server"] + r2["server"]) / n
    ext = [{"n_docs": int(x), "server_sec": per_doc * x} for x in [1e3, 1e4, 1e5, 1e6]]
    res["encrypted"] = {"scheme": "CKKS (TenSEAL 0.3.18)", "poly_modulus_degree": N, "coeff_mod_bit_sizes": [60, 40, 60],
                        "scale_bits": 40, "keygen_sec": keygen, "he_bits": he_bits, "n_check": n_check,
                        "scores_exact": exact, "top1_match": top1, "max_abs_ckks_error": maxerr,
                        "round1": r1, "round2": r2, "server_sec_total": r1["server"] + r2["server"],
                        "client_sec_total": r1["encrypt"] + r1["decrypt"] + r2["encrypt"] + r2["decrypt"],
                        "comm_MB": (r1["up_bytes"] + r1["down_bytes"] + r2["up_bytes"] + r2["down_bytes"]) / 1e6,
                        "plain_score_sec": None, "extrapolation": ext, "server_min_1M": per_doc * 1e6 / 60,
                        "cpu_threads": os.cpu_count()}
    t = time.time(); _ = Dq @ qy; res["encrypted"]["plain_score_sec"] = time.time() - t
    res["your_query_retrieval"] = {"query": your_q, "top_doc_index": istar, "top_doc_title": title,
                                   "encrypted_top1_equals_plaintext_quantized": istar == plain_top,
                                   "encrypted_top1_equals_float": istar == float_top,
                                   "pir_fetch_exact": fetched == truth, "fetched_chars": len(fetched),
                                   "round1": tm_y}
    res["runtime_sec"] = round(time.time() - T0, 1)
    figures(res, sb, appts, record, you)
    card(res, sb)
    res["runtime_sec"] = round(time.time() - T0, 1)
    (OUT / "results.json").write_text(json.dumps(res, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    a, e = res["attack"], res["encrypted"]
    log(f"done: attack dx {a['dx_top1']:.0%}, records {a['records_recovered']}/{a['n_patient_queries']}; "
        f"nDCG@10 b={he_bits} retains {sb[he_bits]['retain']:.1%}; encrypted top-1 {e['top1_match']}/{e['n_check']}; "
        f"server {e['server_sec_total']:.2f} s for {n} docs; 1M docs ≈ {e['server_min_1M']:.0f} min")


def short(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


def figures(res, sb, appts, record, you):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans"})
    # 1. the reconstructed record
    rows = [r for r in record if r["true_dx"]]
    rows = rows[:14]
    lines = [(r["time"], r["linked_patient"] or "—", r["recovered_dx"], r["record_correct"], r["dx_correct"]) for r in rows]
    lines.append((you["time"], you["linked_patient"] or "(no appointment)", you["top3"][0][0], None, None))
    lines.sort(key=lambda x: x[0])
    fig, ax = plt.subplots(figsize=(6.4, 0.6 + 0.27 * len(lines)))
    ax.set_xlim(0, 1); ax.set_ylim(len(lines) - 0.5, -1.3); ax.axis("off")
    hx = [0.0, 0.11, 0.30, 0.94]
    for x, h in zip(hx, ["log time", "linked patient", "recovered working diagnosis", ""]):
        ax.text(x, -0.9, h, fontsize=8.5, color=MUTED, fontweight="bold")
    for i, (tm, pt, dx, ok, dxok) in enumerate(lines):
        yours = ok is None
        col = ACC if yours else INK
        if yours:
            ax.add_patch(plt.Rectangle((-0.01, i - 0.45), 1.0, 0.9, color="#fff4e6", zorder=0))
        ax.text(hx[0], i, tm, fontsize=8.5, color=col, va="center", family="DejaVu Sans Mono")
        ax.text(hx[1], i, pt, fontsize=8.5, color=col, va="center", family="DejaVu Sans Mono")
        ax.text(hx[2], i, short(dx, 52) + ("   ← your query" if yours else ""), fontsize=8.5, color=col, va="center",
                fontweight="bold" if yours else "normal")
        if not yours:
            ax.text(hx[3], i, "✓" if ok else ("~" if dxok else "✗"), fontsize=10, va="center",
                    color=GOOD if ok else (BLUE if dxok else ACC), fontweight="bold")
    fig.tight_layout(); fig.savefig(OUT / "fig_record.png", dpi=160); plt.close(fig)

    # 2. quantization
    sw = res["quant_sweep"]; c = res["corpus"]
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    xs = [s["bits"] for s in sw]
    ax.plot(xs, [s["ndcg10"] for s in sw], "o-", color=ACC, lw=2.2, label=f"your run ({res['params'].get('embedder', '').split('/')[-1]}, clip {res['clip_percentile']:g} pct)")
    ax.plot(xs, [s["ndcg10_maxabs"] for s in sw], "o--", color=ACC, alpha=0.45, lw=1.4, label="your run, max-abs scale (no clipping)")
    ax.axhline(res["ndcg10_float"], color=ACC, ls=":", lw=1)
    for name, col in [("BGE-large", INK), ("Cohere v3", MUTED)]:
        pts = PAPER_NDCG[c][name]
        ax.plot([2, 4, 6, 8], [pts[b] for b in [2, 4, 6, 8]], "s-", color=col, lw=1.4, ms=5, label=f"paper, {name}")
    ax.axvline(res["encrypted"]["he_bits"], color=BLUE, lw=1, ls="--")
    ax.text(res["encrypted"]["he_bits"] + 0.1, 0.02, "encrypted run", color=BLUE, fontsize=8)
    ax.set_xlabel("quantization bits per embedding dimension (b)"); ax.set_ylabel(f"nDCG@10 on {c}")
    ax.set_ylim(0, max(0.8, res["ndcg10_float"] + 0.1)); ax.set_xticks(sorted(set(xs) | {2, 4, 6, 8}))
    ax.legend(frameon=False, fontsize=7.5, loc="lower right")
    fig.tight_layout(); fig.savefig(OUT / "fig_quantization.png", dpi=160); plt.close(fig)

    # 3. cost vs corpus size
    e = res["encrypted"]
    fig, ax = plt.subplots(figsize=(6.4, 3.7))
    ex = e["extrapolation"]; xs = [x["n_docs"] for x in ex]
    ax.loglog(xs, [x["server_sec"] for x in ex], "-", color=ACC, lw=2, label="your run (dot = measured; line = linear extrapolation)")
    ax.loglog([res["n_docs"]], [e["server_sec_total"]], "o", color=ACC, ms=8)
    ax.add_patch(plt.Rectangle((CORPUS_DOCS["nfcorpus"], 4.3), CORPUS_DOCS["scifact"] - CORPUS_DOCS["nfcorpus"], 8.7 - 4.3,
                               color=INK, alpha=0.85, label="paper: 4.3–8.7 s verified (SciFact/NFCorpus)"))
    ax.loglog([1e6], [19 * 60], "D", color=INK, ms=7, label="paper: ~19 min at 1M docs (48 cores, proofs)")
    ax.loglog(xs, [max(e["plain_score_sec"], 1e-4) * x / res["n_docs"] for x in xs], ":", color=MUTED, label="unprotected scoring (plaintext)")
    for yv, lab in [(60, "1 min"), (3600, "1 hour")]:
        ax.axhline(yv, color=MUTED, lw=0.6); ax.text(1.0e3, yv * 1.3, lab, fontsize=7.5, color=MUTED)
    ax.set_ylim(3e-5, 2e4)
    ax.set_xlabel("documents in the licensed corpus"); ax.set_ylabel("server seconds per private query")
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=2)
    fig.tight_layout(); fig.savefig(OUT / "fig_cost.png", dpi=160); plt.close(fig)


def card(res, sb):
    a, e, y = res["attack"], res["encrypted"], res["your_query_retrieval"]
    hb = e["he_bits"]; c = res["corpus"]
    tiles = [
        {"label": "Patient records rebuilt from the log", "value": f"{a['records_recovered']} / {a['n_patient_queries']}",
         "sub": f"diagnosis recovered {a['dx_top1']:.0%} (chance {a['chance_top1']:.1%}), timestamp join right {a['link_acc']:.0%}", "tone": "accent"},
        {"label": f"nDCG@10 kept at b = {hb}", "value": f"{sb[hb]['retain']:.0%}",
         "sub": f"{sb[hb]['ndcg10']:.3f} vs {res['ndcg10_float']:.3f} float on {c}" + (f"; b = 2: {sb[2]['ndcg10']:.3f}" if 2 in sb else ""), "tone": "good"},
        {"label": "Encrypted = plaintext", "value": f"{e['top1_match']} / {e['n_check']}",
         "sub": f"top-1 identical; scores bit-exact in {e['scores_exact']}/{e['n_check']} after rounding", "tone": "good"},
        {"label": "Price of privacy (server)", "value": f"{e['server_sec_total']:.1f} s",
         "sub": f"vs {e['plain_score_sec'] * 1000:.1f} ms in the clear for {res['n_docs']:,} docs; ≈ {e['server_min_1M']:.0f} min at 1M (no proofs)", "tone": "neutral"},
    ]
    p = PAPER_NDCG[c]
    compare = [
        {"metric": f"nDCG@10 at b = 4 / float ({c})", "paper": f"BGE-large {p['BGE-large'][4]} / {p['BGE-large']['float']}; Cohere v3 {p['Cohere v3'][4]} / {p['Cohere v3']['float']}",
         "yours": f"{sb[4]['ndcg10']:.3f} / {res['ndcg10_float']:.3f}" if 4 in sb else "b = 4 not run", "note": "static model2vec embedder, so lower absolute nDCG"},
        {"metric": "Quality retained at b = 4", "paper": f"{PAPER_RETAIN_B4[c]} (BGE-large)", "yours": f"{sb[4]['retain']:.0%}" if 4 in sb else "—", "note": f"clip at {res['clip_percentile']:g}th pct of |x|"},
        {"metric": "nDCG@10 at b = 2", "paper": f"{p['BGE-large'][2]} (BGE-large), {p['Cohere v3'][2]} (Cohere v3): collapses",
         "yours": f"{sb[2]['ndcg10']:.3f}" if 2 in sb else "b = 2 not run", "note": ""},
        {"metric": "Server time per private query", "paper": "4.3–8.7 seconds (verified, SciFact/NFCorpus)",
         "yours": f"{e['server_sec_total']:.2f} s ({res['n_docs']:,} docs)", "note": "no proofs; TenSEAL CKKS, N = 8192"},
        {"metric": "1M-document corpus", "paper": "roughly 19 minutes and $2.22", "yours": f"≈ {e['server_min_1M']:.0f} min (linear extrapolation)", "note": "no verification; different hardware"},
        {"metric": "Retrieval exactness", "paper": "every document is scored … quality is not traded for privacy",
         "yours": f"top-1 match {e['top1_match']}/{e['n_check']}; PIR fetch exact: {'yes' if y['pir_fetch_exact'] else 'no'}", "note": ""},
    ]
    you = a["your_query"]
    inputs = {"your query": short(y["query"], 70), "logged at": you["time"], "corpus": f"{c} ({res['n_docs']:,} docs)",
              "bits (encrypted run)": hb, "clip percentile": res["clip_percentile"],
              "embedder": res["params"].get("embedder", "minishlab/potion-base-8M").split("/")[-1],
              "clinic day": f"{a['n_appointments']} appointments, lag ≤ {res['params'].get('query_lag_max_min', 15)} min"}
    Path(OUT / "card_data.json").write_text(json.dumps({
        "paper": {"num": 4, "title": "Query Logs Are Patient Records: An Unguarded Attack Surface in Clinical RAG, and a Privacy-Preserving Pipeline",
                  "authors": "Louis Tremblay Thibault, Sofiane Azogagh, Marc-Olivier Killijian, Ulrich Aïvodji", "url": "https://arxiv.org/pdf/2609.36376",
                  "affiliation": "École de Technologie Supérieure · Mila · EURECOM · UQAM"},
        "inputs": inputs, "tiles": tiles,
        "figures": [
            {"path": "fig_record.png", "title": "What an insider reads in the provider's log after one (synthetic) clinic day",
             "caption": f"Each logged query embedding is inverted by nearest-neighbour search over a {a['dictionary_size']}-diagnosis dictionary "
                        "and joined to the appointment schedule by timestamp. ✓ = right diagnosis and right patient; ~ = right diagnosis, "
                        f"wrong patient; ✗ = wrong diagnosis. Your query (orange) maps to *{you['top3'][0][0]}*. Synthetic schedule and patients."},
            {"path": "fig_quantization.png", "title": "How coarse can the encrypted embeddings be?",
             "caption": "Retrieval quality as each embedding dimension is rounded to b bits (needed to fit the cryptographic parameters). "
                        "Squares = the paper's Table 1; circles = this run on the same public corpus with a small static embedder."},
            {"path": "fig_cost.png", "title": "What privacy costs as the corpus grows",
             "caption": "Server time for both encrypted rounds (scoring + private fetch), measured on this corpus and extrapolated linearly. "
                        "The paper's numbers include succinct proofs of correct computation on a 48-core machine; ours do not."}],
        "compare": compare, "runbook": {"name": "smash-04-query-log-privacy", "url": P.get("runbook_url", "")}}, indent=2))


if __name__ == "__main__":
    main()
```

### `/app/work/render_card.py`

```python
"""Render a SMASH 2026 paper-playground result card (one self-contained HTML file).

usage: python render_card.py card_data.json narrative.json out.html

card_data.json  (written by the experiment script — numbers only)
  paper:   {num, title, authors, affiliation, url?}
  inputs:  {label: value}                         the participant's run settings
  tiles:   [{label, value, sub, tone}]            tone: accent|good|warn|neutral
  figures: [{path, title, caption}]               PNGs, embedded as base64
  compare: [{metric, paper, yours, note}]         paper-vs-your-run table (optional)
  runbook: {name, url}                            fork link (optional)
narrative.json  (written by the agent — words only)
  headline:  one sentence, the finding of THIS run
  idea:      [1-3 bullets] the paper's contribution in plain language
  abstract:  (optional) a verbatim abstract excerpt, shown instead of idea
  findings:  [2-4 short paragraphs] what this run shows, tied to the numbers
  try_next:  [{label, why, params}]               2-3 follow-up runs with exact parameter values
  caveats:   [bullets]
"""
import base64, html, json, sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text())
narr = json.loads(Path(sys.argv[2]).read_text())
base = Path(sys.argv[1]).parent
e = lambda s: html.escape(str(s))


def md_inline(s):
    """Escape, then allow **bold**, *italic* and `code` only."""
    import re
    s = e(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


p = data["paper"]
tiles = "".join(
    f'<div class="tile {e(t.get("tone", "neutral"))}"><div class="tl">{e(t["label"])}</div>'
    f'<div class="tv">{e(t["value"])}</div><div class="ts">{md_inline(t.get("sub", ""))}</div></div>'
    for t in data.get("tiles", []))
# Columns that fill every row: 4 tiles as 2x2, never 3 + 1 orphan.
n_tiles = len(data.get("tiles", []))
tile_cols = 2 if n_tiles == 4 else min(max(n_tiles, 1), 3)
inputs = "".join(f'<span class="chip"><b>{e(k)}</b> {e(v)}</span>' for k, v in data.get("inputs", {}).items())
figs = ""
for f in data.get("figures", []):
    fp = Path(f["path"]); fp = fp if fp.is_absolute() else base / fp
    if fp.exists():
        b64 = base64.b64encode(fp.read_bytes()).decode()
        figs += (f'<figure><figcaption class="ft">{e(f.get("title", ""))}</figcaption>'
                 f'<img alt="{e(f.get("title", ""))}" src="data:image/png;base64,{b64}">'
                 f'<figcaption>{md_inline(f.get("caption", ""))}</figcaption></figure>')
compare = ""
if data.get("compare"):
    rows = "".join(f'<tr><td>{md_inline(r["metric"])}</td><td>{md_inline(r["paper"])}</td>'
                   f'<td class="y">{md_inline(r["yours"])}</td><td class="n">{md_inline(r.get("note", ""))}</td></tr>'
                   for r in data["compare"])
    compare = (f'<section><h2>Paper vs. your run</h2><div class="tw"><table><thead><tr><th>Metric</th>'
               f'<th>Paper</th><th>Your run</th><th></th></tr></thead><tbody>{rows}</tbody></table></div></section>')
idea = "".join(f"<li>{md_inline(b)}</li>" for b in narr.get("idea", []))
abstract = narr.get("abstract", "")
findings = "".join(f"<p>{md_inline(x)}</p>" for x in narr.get("findings", []))
tries = "".join(
    f'<li><strong>{md_inline(t["label"])}</strong> — {md_inline(t.get("why", ""))}'
    f'<pre>{e(json.dumps(t.get("params", {}), ensure_ascii=False))}</pre></li>' for t in narr.get("try_next", []))
cav = "".join(f"<li>{md_inline(c)}</li>" for c in narr.get("caveats", []))
rb = data.get("runbook", {})
fork = (f'<a class="fork" href="{e(rb["url"])}">Fork this runbook on Jetty →</a>' if rb.get("url") else "")

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SMASH 2026 · #{e(p['num'])} · Result card</title>
<style>
:root{{--bg:#f6f4ef;--card:#fff;--ink:#1f2a44;--muted:#5c677d;--line:#e3dfd5;--accent:#d9480f;--good:#2b8a3e;--warn:#e67700;--chip:#efece4}}
@media (prefers-color-scheme:dark){{:root{{--bg:#11151f;--card:#1a2030;--ink:#e8ebf2;--muted:#9aa4b8;--line:#2c3447;--accent:#ff8a4c;--good:#69db7c;--warn:#ffc078;--chip:#232b3d}}
figure img{{background:#fff;border-radius:6px}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
main{{max-width:860px;margin:0 auto;padding:28px 16px 48px}}
.kicker{{font:600 12px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}}
h1{{font-size:clamp(22px,4vw,30px);line-height:1.2;margin:10px 0 6px}}.authors{{color:var(--muted);margin:0 0 18px}}.authors a{{color:var(--accent);text-underline-offset:3px}}
.headline{{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--accent);border-radius:10px;padding:16px 18px;font-size:18px;font-weight:600;margin:0 0 18px}}
.chips{{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 18px}}.chip{{background:var(--chip);border-radius:999px;padding:4px 10px;font-size:12.5px}}.chip b{{font-weight:600;color:var(--muted);margin-right:4px}}
.tiles{{display:grid;grid-template-columns:repeat(var(--cols),minmax(0,1fr));gap:10px;margin:0 0 22px}}
@media (max-width:560px){{.tiles{{grid-template-columns:1fr}}}}
.tile{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}}.tl{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}}
.tv{{font-size:26px;font-weight:700;margin:2px 0;font-variant-numeric:tabular-nums}}.ts{{font-size:12.5px;color:var(--muted)}}
.tile.accent .tv{{color:var(--accent)}}.tile.good .tv{{color:var(--good)}}.tile.warn .tv{{color:var(--warn)}}
section{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:0 0 16px}}
h2{{font-size:16px;margin:0 0 10px}}ul{{padding-left:20px;margin:0}}li{{margin:4px 0}}p{{margin:0 0 10px}}
figure{{margin:0 0 18px}}figure img{{width:100%;height:auto;display:block}}figcaption{{font-size:13px;color:var(--muted);margin-top:6px}}.ft{{font-weight:600;color:var(--ink);font-size:14px;margin:0 0 6px}}
.tw{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums}}th,td{{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}}th{{color:var(--muted);font-weight:600}}td.y{{font-weight:600}}td.n{{color:var(--muted);font-size:12.5px}}
pre{{background:var(--chip);border-radius:6px;padding:6px 8px;font-size:12px;white-space:pre-wrap;word-break:break-word;margin:4px 0 8px}}code{{background:var(--chip);border-radius:4px;padding:1px 4px;font-size:.92em}}
.fork{{display:inline-block;background:var(--ink);color:var(--bg);text-decoration:none;font-weight:600;border-radius:8px;padding:10px 14px;margin-top:6px}}
footer{{color:var(--muted);font-size:12.5px;margin-top:22px}}
.abs{{margin:0;padding-left:14px;border-left:3px solid var(--accent);color:var(--ink)}}
</style></head><body><main>
<div class="kicker">SMASH 2026 · Paper #{e(p['num'])} · Result card</div>
<h1>{e(p['title'])}</h1><p class="authors">{e(p['authors'])}{(' · ' + e(p['affiliation'])) if p.get('affiliation') else ''}{(f' · <a href="{e(p["url"])}">Read the paper</a>') if p.get('url') else ''}</p>
<div class="headline">{md_inline(narr['headline'])}</div>
<div class="chips">{inputs}</div>
<div class="tiles" style="--cols:{tile_cols}">{tiles}</div>
{f'<section><h2>From the abstract</h2><blockquote class="abs">{e(abstract)}</blockquote></section>' if abstract else f'<section><h2>The idea</h2><ul>{idea}</ul></section>'}
{f'<section><h2>What this run shows</h2>{findings}</section>' if findings else ''}
<section><h2>Evidence</h2>{figs}</section>
{compare}
<section><h2>Try next</h2><ul>{tries}</ul>{fork}</section>
<section><h2>Read this before sharing</h2><ul>{cav}</ul></section>
<footer>Generated by a Jetty runbook built from the authors' SMASH 2026 paper. Numbers on this card come from code run in a sandbox; the words were written by an AI agent reading those numbers. This is an interactive companion, not the authors' own results unless labelled “Paper”.</footer>
</main></body></html>"""
Path(sys.argv[3]).write_text(page)
print(f"wrote {sys.argv[3]} ({len(page) // 1024} KB)")
```

### `/app/work/validate.py`

```python
"""Self-check a SMASH paper-playground run and write validation_report.json (evals v2 shape).

Runs the same checks as the runbook's `## Code Checks` (which Jetty re-runs independently after the agent
exits and substitutes for these entries), adds one `step` entry per runbook step and the agent's checklist
judgements, and prints PASS/FAIL lines.

usage: python validate.py <results_dir> <param,param,...> <budget_sec> [checklist.json]
"""
import html, json, re, sys
from pathlib import Path

R = Path(sys.argv[1])
allowed = set(sys.argv[2].split(","))
budget = float(sys.argv[3])
checklist_path = Path(sys.argv[4]) if len(sys.argv) > 4 else None


def load(name):
    try:
        return json.loads((R / name).read_text())
    except Exception:
        return None


res, cdata, narr = load("results.json"), load("card_data.json"), load("narrative.json")
card = (R / "result_card.html").read_text() if (R / "result_card.html").exists() else ""


def c_outputs_exist():
    missing = [f for f in ["result_card.html", "results.json", "card_data.json", "narrative.json", "summary.md"]
               if not (R / f).exists() or (R / f).stat().st_size == 0]
    return not missing, f"missing or empty: {missing}" if missing else "all 5 outputs present"


def c_results_valid():
    if res is None or cdata is None:
        return False, "results.json or card_data.json does not parse"
    rt = float(res.get("runtime_sec", 0))
    return rt <= budget, f"experiment {rt}s (budget {budget:.0f}s)"


def c_narrative_complete():
    if narr is None:
        return False, "narrative.json does not parse"
    p = []
    if not str(narr.get("headline", "")).strip(): p.append("no headline")
    if len(str(narr.get("headline", "")).split()) > 45: p.append("headline over 45 words")
    if not 1 <= len(narr.get("idea", [])) <= 3: p.append(f"idea has {len(narr.get('idea', []))} bullets, need 1-3")
    if not 1 <= len(narr.get("findings", [])) <= 2: p.append(f"{len(narr.get('findings', []))} findings, need 1-2")
    if any(len(f.split()) > 70 for f in narr.get("findings", [])): p.append("a findings paragraph is over 60 words")
    if not 2 <= len(narr.get("try_next", [])) <= 3: p.append(f"{len(narr.get('try_next', []))} try_next, need 2-3")
    if not 1 <= len(narr.get("caveats", [])) <= 2: p.append(f"{len(narr.get('caveats', []))} caveats, need 1-2")
    return not p, "; ".join(p) or "complete and within the length limits"


def c_try_next_valid():
    if narr is None:
        return False, "narrative.json does not parse"
    bad = sorted({k for t in narr.get("try_next", []) for k in (t.get("params") or {}) if k not in allowed})
    empty = [t.get("label", "?") for t in narr.get("try_next", []) if not t.get("params")]
    ok = not bad and not empty
    return ok, "all try_next parameters are declared" if ok else f"unknown parameters: {bad}; without params: {empty}"


def c_headline_grounded():
    if narr is None or res is None:
        return False, "missing narrative or results"
    blob = json.dumps(res) + json.dumps(cdata or {})
    vals = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?", blob)]
    nums = re.findall(r"(?<![\w.−-])[−-]?\d[\d,]*(?:\.\d+)?(?![\w-])", narr.get("headline", ""))
    missing = []
    for n in nums:
        s = n.replace("−", "-").replace(",", ""); v = float(s); dec = len(s.split(".")[1]) if "." in s else 0
        tol = 0.5 * 10 ** (-dec) + 1e-9
        if not any(abs(abs(x) - abs(v)) <= tol or abs(abs(x * 100) - abs(v)) <= max(tol, 0.5) for x in vals):
            missing.append(n)
    return not missing, f"not found in results: {missing}" if missing else f"{len(nums)} headline number(s) grounded"


def c_card_integrity():
    if not card or narr is None:
        return False, "no card or narrative"
    text = re.sub(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+", "", card)
    plain = html.unescape(re.sub(r"<[^>]+>", "", text))
    p = []
    if card.count("data:image/png;base64") < 1: p.append("no embedded figures")
    if re.search(r"\bNaN\b|\bnan%|\bInfinity\b", text): p.append("NaN/Infinity in card text")
    if len(card) > 5_000_000: p.append(f"card is {len(card) // 1024} KB")
    if re.sub(r"[*`]", "", narr.get("headline", ""))[:40] not in plain: p.append("headline not on card")
    return not p, "; ".join(p) or f"card {len(card) // 1024} KB, {card.count('data:image/png;base64')} figures"


CODE_CHECKS = [  # ids and names match the runbook's ## Code Checks headings
    ("outputs-exist", "Result card, numbers, narrative and summary were written", c_outputs_exist),
    ("results-valid", "Experiment numbers are valid JSON and the experiment stayed within its time budget", c_results_valid),
    ("narrative-complete", "The narrative is complete and within the length limits", c_narrative_complete),
    ("try-next-valid", "Every try-next suggestion uses only this runbook's parameters", c_try_next_valid),
    ("headline-grounded", "Every number in the headline appears in the run's results", c_headline_grounded),
    ("card-integrity", "The card embeds its figures, shows the headline, and contains no NaN", c_card_integrity),
]
STEPS = [  # (id, name, evidence that the step happened)
    ("setup", "Set up the sandbox and parameters", Path("/app/work/params.json").exists() or res is not None),
    ("get-code", "Extract the tested code", Path("/app/work/experiment.py").exists() or res is not None),
    ("experiment", "Run the experiment", res is not None),
    ("interpret", "Write the narrative", narr is not None),
    ("render", "Render the result card and summary", bool(card) and (R / "summary.md").exists()),
]

checks = [{"kind": "step", "id": i, "name": n, "status": "pass" if ok else "fail"} for i, n, ok in STEPS]
for cid, name, fn in CODE_CHECKS:
    try:
        ok, msg = fn()
    except Exception as e:  # a check that crashes is an error, never a silent pass
        ok, msg = None, f"{type(e).__name__}: {e}"
    status = "pass" if ok else ("error" if ok is None else "fail")
    checks.append({"kind": "code_check", "id": cid, "name": name, "status": status, "message": str(msg)[:1000]})
    print(f"{'PASS' if ok else 'FAIL'} {cid}: {msg}")

if checklist_path and checklist_path.exists():
    for item in json.loads(checklist_path.read_text()):
        st = item.get("status", "skipped")
        st = st if st in ("pass", "fail", "skipped", "error") else "skipped"
        checks.append({"kind": "checklist", "id": str(item["id"]), "name": str(item.get("name") or item["id"]),
                       "status": st, "message": str(item.get("message", ""))[:1000]})
        print(f"{'PASS' if st == 'pass' else 'FAIL'} checklist {item['id']}: {item.get('message', '')}")
else:
    print("NOTE no checklist.json given; checklist items will be recorded as not reported")

gating = [c for c in checks if c["kind"] != "step"]
verdict = "fail" if any(c["status"] in ("fail", "error") for c in gating) else ("pass" if gating else "unknown")
(R / "validation_report.json").write_text(json.dumps({"version": 2, "verdict": verdict, "checks": checks}, indent=2))
print(json.dumps({"verdict": verdict, "passed": sum(c["status"] == "pass" for c in gating), "gating_checks": len(gating)}))
```
