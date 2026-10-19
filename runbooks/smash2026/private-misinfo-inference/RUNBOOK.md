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
    skill_name: smash-13-private-claim-check
    confidence: high
---

# Private Claim Check: Score a Health Claim the Server Never Sees (SMASH 2026 · Paper #13)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"Privacy-Preserving Text Inference for Health-Misinformation Classification and Semantic Retrieval"** (Jasleen Kaur, Chloe Cachet, Koray Karabina, Jean Belo Klamti, Philippe Lamontagne).
Read the paper: https://arxiv.org/abs/2610.20796

The paper's claims:
1. A logistic-regression misinformation classifier on fused text features (BioBERT + PCA-256 MPNet + SVD-300
   TF-IDF, 1,324-d) can be evaluated on **CKKS-encrypted** feature vectors: the server computes `z = x̃ᵀw + b` on
   the ciphertext, the client decrypts and applies the sigmoid. Plaintext and ciphertext inference give
   **identical** accuracy and F1 on CoAID.
2. Encrypted semantic retrieval is practical once similarity scores are **SIMD-packed** into one ciphertext rather
   than returned one ciphertext per database item.

The participant brings **their own health claims**. The run trains the paper's classifier recipe on the public
CoAID dataset, scores the participant's claims in plaintext and under encryption, checks the whole test split
under encryption, benchmarks latency/ciphertext size at the paper's parameters, and runs naive vs packed encrypted
retrieval of the most similar CoAID items. Output: a shareable **result card**.

Target wall-clock: **under 4 minutes.** The experiment itself takes ~15–30 s (4.3 MB CoAID + 30 MB embedder).

### The method, as implemented
- **Data.** CoAID news (GitHub `cuilimeng/CoAID`, releases 05-01/07-01/09-01/11-01-2020, `NewsFake`/`NewsReal`):
  text = title + news title + first 2,000 characters of content (`text_field = title+content`) or title only;
  exact duplicates removed; stratified 80/20 split (seed 42) → test 1,080 items (183 fake), close to the paper's
  1,081 (184).
- **Client features.** TF-IDF (1–2-grams) → truncated SVD (`svd_dim`, paper 300) and/or a 256-d static sentence
  embedding (model2vec `potion-base-8M`, stand-in for the paper's PCA-256 MPNet). Standardized on the client.
  **Substitution:** the paper's 768-d BioBERT block is not reproduced (no torch/GPU), so the hybrid is 556-d.
- **Model.** L2 logistic regression (`C`). Ablation in plaintext over TF-IDF / embedding / hybrid.
- **Encrypted inference.** TenSEAL CKKS, scale 2^40, moduli [60, 40, 60] (N = 8,192) or [60, 40, 40, 60]
  (N = 16,384 / 32,768; the paper uses N = 32,768). Client encrypts x; server returns `Enc(x)·w + b`; client
  decrypts z, computes p = σ(z). Run on the whole test split (capped at 400 items when N = 32,768) and every claim.
- **Encrypted retrieval.** Database = unique CoAID titles embedded (256-d, unit norm). Naive: one encrypted dot
  product (one ciphertext) per item, timed on 200 items and extrapolated; packed: one `Enc(q)·DBᵀ` per
  N/2-item shard. ISCC-SCT fingerprints, Ridge late fusion and STS-B are **not** reproduced.

### Paper headline numbers (quote exactly)
- Full hybrid: accuracy **0.971**, macro-F1 **0.950** (F1-fake 0.918, F1-real 0.983); TF-IDF alone 0.942 / 0.904;
  MPNet alone 0.938 / 0.899; BioBERT alone 0.944 / 0.905. Test set of 1,081 samples, 184 fake and 897 real.
- "Plaintext and ciphertext-based inference produced identical accuracy and F1 scores for every feature configuration."
- "The hybrid model required approximately 122.4 ms and 2.133 MB of communication per query."
- Retrieval over 7,128 items: naive 221.049 s → SIMD-packed 5.186 s (42.6×); communication 6.11 GB → 2.13 MB.
- CKKS: N = 32,768, coefficient moduli [60, 40, 40, 60], scale 2^40, Apple M4 MacBook Air.

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
| Your claims | `{{claims}}` | — | Up to 10 health claims separated by `\|` (blank = 6 built-in examples, true and false). Scored under encryption |
| Features | `{{features}}` | `hybrid` | `hybrid` (TF-IDF→SVD + embedding), `tfidf`, or `embed` |
| Training text | `{{text_field}}` | `title+content` | `title+content` (paper-like) or `title` (short, closer to what people paste) |
| SVD dimensions | `{{svd_dim}}` | `300` | TF-IDF truncated-SVD size (paper: 300) |
| CKKS ring size | `{{poly_modulus_degree}}` | `8192` | `8192`, `16384` or `32768` (paper). Used for the test-split and retrieval runs; the latency benchmark always covers all three |
| Retrieval database size | `{{retrieval_db_size}}` | `0` | Number of CoAID titles to search (0 = all ~5,200) |
| Regularization C | `{{C}}` | `1.0` | Inverse L2 strength of the logistic regression |
| Embedder | `{{embedder}}` | `minishlab/potion-base-8M` | model2vec static embedder (30 MB) |
| Seed | `{{seed}}` | `42` | Train/test split seed |

## Dependencies

numpy, pandas, scikit-learn, matplotlib (preinstalled in `python312-uv`), plus `tenseal` (0.3.18) and `model2vec`
installed in Step 1 (~10–30 s). Downloads: 8 CoAID CSVs from raw.githubusercontent.com (4.3 MB) and the embedder
from Hugging Face (30 MB).

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, pandas, sklearn, matplotlib" 2>/dev/null || uv pip install --system -q numpy pandas scikit-learn matplotlib
python -c "import tenseal, model2vec" 2>/dev/null || uv pip install --system -q tenseal==0.3.18 model2vec
```

Write `/app/work/params.json`. Strings for text values, JSON numbers for the rest; if a value still looks like an
unsubstituted `{{…}}` placeholder use the table default (`claims` → `""`). Validate: `features` ∈ {hybrid, tfidf,
embed}; `text_field` ∈ {title+content, title}; `poly_modulus_degree` ∈ {8192, 16384, 32768}; clamp `svd_dim` to
[20, 600], `retrieval_db_size` to 0 or [200, 6000], `C` to [0.001, 100]. Keep at most 10 claims, each ≤ 300
characters; escape quotes for JSON. Record any change as a caveat. `n_encrypted_eval` and `naive_items` are fixed
budget settings.

```json
{"claims": "{{claims}}", "features": "{{features}}", "text_field": "{{text_field}}", "svd_dim": {{svd_dim}},
 "poly_modulus_degree": {{poly_modulus_degree}}, "retrieval_db_size": {{retrieval_db_size}}, "C": {{C}},
 "embedder": "{{embedder}}", "seed": {{seed}}, "n_encrypted_eval": 0, "naive_items": 200, "runbook_url": ""}
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

Expected: 15–30 s at N = 8,192 (≈ 60–90 s at N = 32,768). Ends with a `done:` line (accuracy/macro-F1, encrypted
labels identical, claims flagged, packed-retrieval speed-up). If a download fails, retry once.

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4). Each findings paragraph ≤ 70 words; bold the one number that matters.

- **headline** (≤ 30 words): a finding with 1–2 numbers copied from `results.json`, e.g. `encrypted.labels_identical`
  of `encrypted.n`, `retrieval.speedup`, or a striking claim result. Write numbers without thousands separators
  in the headline (`1080`, not `1,080`) and avoid scientific notation there (the validator parses digits).
- **idea**: plain-language version of the two claims above (why the text is sensitive; what the server computes;
  why packing matters).
- **findings**: (1) accuracy/macro-F1 of the chosen `features` vs the paper's row (`ablation`; TF-IDF row is the
  like-for-like comparison) and the test split vs 1,081/184; (2) encryption is lossless: `labels_identical`,
  `max_abs_logit_diff`, and each claim's `label_enc`, `p_fake_enc`, `abs_diff`; name which of the participant's
  claims were flagged; mention the nearest CoAID items for one claim (`retrieved`, with their CoAID labels) if
  telling; (3) cost: N = 32,768 row of `latency_bench` vs 122.4 ms / 2.133 MB; `retrieval` naive vs packed vs
  221.049 s → 5.186 s and `same_top5`.
- **Never** present the output as a fact-check. “Fake” means “resembles the CoAID fake class”; CoAID labels
  partly encode the source and writing style (see `top_terms`). If a true claim is flagged or a false one passes,
  say so plainly.
- **try_next**: 2–3 contrasting runs with exact values, using only the keys `claims, features, text_field, svd_dim,
  poly_modulus_degree, retrieval_db_size, C, embedder, seed`. Good contrasts: `text_field` `title` with false-cure
  claims (style vs truth); `poly_modulus_degree` 32768; `features` `tfidf`; the same claim reworded as a social post.
- **caveats**: feature substitutions (no BioBERT, static embedder instead of MPNet, 556-d not 1,324-d); retrieval
  without ISCC-SCT/STS-B; honest-but-curious threat model; timings on one CPU, naive retrieval extrapolated.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: settings, accuracy/macro-F1 vs paper, encrypted agreement, each
claim's label, latency/size at N = 32,768, retrieval speed-up, headline).

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
python3 - "{{results_dir}}" "claims,features,text_field,svd_dim,poly_modulus_degree,retrieval_db_size,C,embedder,seed" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} claims,features,text_field,svd_dim,poly_modulus_degree,retrieval_db_size,C,embedder,seed 300 checklist.json
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
"""Private claim check — SMASH 2026 paper #13 (Kaur, Cachet, Karabina, Klamti, Lamontagne; NRC Canada).

Re-implements the paper's client-server pipeline on the public CoAID dataset:
  1. train an L2 logistic regression on fused features: TF-IDF -> truncated SVD(300) (as in the paper) plus a
     small static sentence embedding (model2vec potion-base-8M, 256-d; stand-in for the paper's PCA-256 MPNet;
     the paper's 768-d BioBERT block is not reproduced);
  2. the client standardizes and CKKS-encrypts each feature vector; the server evaluates z = x.w + b on the
     ciphertext; the client decrypts z and applies the sigmoid (paper Eq. 1). Run on the whole test split and on
     the participant's own health claims, comparing plaintext and ciphertext logits;
  3. per-query latency and ciphertext size at the paper's CKKS parameters (N = 32,768) and smaller rings;
  4. encrypted semantic retrieval of the nearest CoAID items to each claim: naive (one ciphertext per database
     item) vs SIMD-packed (one matrix-vector product), the paper's 42.6x optimisation.

usage: python experiment.py params.json outdir
"""
import glob, io, json, os, sys, time, urllib.request
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
SEED = int(P.get("seed", 42))
INK, ACC, BLUE, MUTED, GOOD = "#1f2a44", "#d9480f", "#1971c2", "#868e96", "#2b8a3e"
RAW = "https://raw.githubusercontent.com/cuilimeng/CoAID/master"
FILES = [(d, f) for d in ["05-01-2020", "07-01-2020", "09-01-2020", "11-01-2020"]
         for f in ["NewsFakeCOVID-19", "NewsRealCOVID-19"]]
DEFAULT_CLAIMS = ("Drinking hot water every 15 minutes flushes the coronavirus into the stomach where acid kills it | "
                  "COVID-19 vaccines were tested in phase 3 clinical trials with tens of thousands of volunteers | "
                  "5G mobile networks spread the coronavirus | "
                  "Washing your hands with soap for 20 seconds helps prevent the spread of COVID-19 | "
                  "Says a photo shows doctors in Italy hugging after curing their last coronavirus patient | "
                  "A Facebook post says washing your hands with soap for 20 seconds helps prevent COVID-19")
# Paper Table 1 (accuracy, macro-F1) quoted exactly
PAPER_T1 = {"tfidf": ("TF-IDF", 0.942, 0.904), "embed": ("MPNet", 0.938, 0.899), "hybrid": ("Full hybrid", 0.971, 0.950)}


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def fetch(url, tries=3):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception as ex:
            if k == tries - 1:
                raise
            log(f"retry {url.split('/')[-1]}: {ex}"); time.sleep(2)


def load_coaid():
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(8) as ex:
        blobs = list(ex.map(lambda df: fetch(f"{RAW}/{df[0]}/{df[1]}.csv"), FILES))
    rows = []
    for (d, f), b in zip(FILES, blobs):
        x = pd.read_csv(io.BytesIO(b)); x["label"] = int("Fake" in f); x["release"] = d; rows.append(x)
    df = pd.concat(rows, ignore_index=True)
    return df, sum(len(b) for b in blobs)


def ckks_ctx(N):
    import tenseal as ts
    cm = [60, 40, 60] if N <= 8192 else [60, 40, 40, 60]  # paper: N = 32,768, [60, 40, 40, 60], scale 2^40
    ctx = ts.context(ts.SCHEME_TYPE.CKKS, N, coeff_mod_bit_sizes=cm); ctx.global_scale = 2 ** 40
    ctx.generate_galois_keys()
    return ctx, cm


def short(s, n):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def main():
    import tenseal as ts
    from model2vec import StaticModel
    res = {"params": P}
    text_field = str(P.get("text_field", "title+content"))
    features = str(P.get("features", "hybrid"))
    if features not in PAPER_T1:
        features = "hybrid"
    svd_dim = int(P.get("svd_dim", 300))
    N = int(P.get("poly_modulus_degree", 8192))
    if N not in (8192, 16384, 32768):
        N = 8192
    claims = [c.strip() for c in str(P.get("claims", "") or DEFAULT_CLAIMS).replace("\n", "|").split("|") if c.strip()][:10]

    # ---------------- data
    df, nbytes = load_coaid()
    if text_field == "title":
        df["text"] = df["title"].fillna("")
    else:
        df["text"] = (df["title"].fillna("") + " " + df["newstitle"].fillna("") + " " + df["content"].fillna("").str[:2000]).str.strip()
    n_raw = len(df)
    df = df[df["text"].str.len() > 0].drop_duplicates("text").reset_index(drop=True)
    tr, te = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=SEED)
    log(f"CoAID news: {n_raw} rows ({nbytes / 1e6:.1f} MB) -> {len(df)} unique; test {len(te)} ({int(te.label.sum())} fake)")

    # ---------------- client-side feature extraction (fit on train only)
    tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, max_features=50000)
    Xtr_t = tfidf.fit_transform(tr["text"]); Xte_t = tfidf.transform(te["text"])
    svd = TruncatedSVD(svd_dim, random_state=SEED); Ttr = svd.fit_transform(Xtr_t); Tte = svd.transform(Xte_t)
    t = time.time(); m2v = StaticModel.from_pretrained(str(P.get("embedder", "minishlab/potion-base-8M")))
    Etr = np.asarray(m2v.encode(tr["text"].tolist())); Ete = np.asarray(m2v.encode(te["text"].tolist()))
    log(f"features: TF-IDF {Xtr_t.shape[1]} terms -> SVD {svd_dim}; embedder {Etr.shape[1]}-d ({time.time() - t:.1f} s)")

    def fuse(T, E, which):
        return {"tfidf": T, "embed": E, "hybrid": np.hstack([T, E])}[which]
    ablation = {}
    models = {}
    for which in ["tfidf", "embed", "hybrid"]:
        A, B = fuse(Ttr, Etr, which), fuse(Tte, Ete, which)
        sc = StandardScaler().fit(A)
        clf = LogisticRegression(C=float(P.get("C", 1.0)), max_iter=5000).fit(sc.transform(A), tr["label"])
        pred = clf.predict(sc.transform(B))
        ablation[which] = {"dim": int(A.shape[1]), "accuracy": accuracy_score(te["label"], pred),
                           "macro_f1": f1_score(te["label"], pred, average="macro"),
                           "f1_fake": f1_score(te["label"], pred, pos_label=1), "f1_real": f1_score(te["label"], pred, pos_label=0)}
        models[which] = (sc, clf)
    sc, clf = models[features]
    w, b = clf.coef_[0], float(clf.intercept_[0])
    Xte = sc.transform(fuse(Tte, Ete, features))
    z_plain = Xte @ w + b
    log("plaintext: " + ", ".join(f"{k} acc {v['accuracy']:.3f} F1 {v['macro_f1']:.3f}" for k, v in ablation.items()))

    # ---------------- encrypted inference on the whole test split (server sees only ciphertexts)
    ctx, cm = ckks_ctx(N)
    wl = w.tolist()
    n_enc = len(Xte) if int(P.get("n_encrypted_eval", 0) or 0) <= 0 else min(len(Xte), int(P["n_encrypted_eval"]))
    if N == 32768:  # ~65 ms per claim: cap the encrypted pass to stay inside the time budget
        n_enc = min(n_enc, 400)
    t_enc = t_srv = t_dec = 0.0; z_enc = np.empty(n_enc)
    for i in range(n_enc):
        t0 = time.time(); c = ts.ckks_vector(ctx, Xte[i].tolist()); t1 = time.time()
        r = c.dot(wl) + b; t2 = time.time()
        z_enc[i] = r.decrypt()[0]; t3 = time.time()
        t_enc += t1 - t0; t_srv += t2 - t1; t_dec += t3 - t2
    y = te["label"].values[:n_enc]
    pred_p, pred_e = (z_plain[:n_enc] >= 0).astype(int), (z_enc >= 0).astype(int)
    enc = {"n": n_enc, "poly_modulus_degree": N, "coeff_mod_bit_sizes": cm, "scale_bits": 40,
           "max_abs_logit_diff": float(np.abs(z_enc - z_plain[:n_enc]).max()),
           "mean_abs_logit_diff": float(np.abs(z_enc - z_plain[:n_enc]).mean()),
           "labels_identical": int((pred_p == pred_e).sum()), "accuracy_plain": accuracy_score(y, pred_p),
           "accuracy_enc": accuracy_score(y, pred_e), "macro_f1_plain": f1_score(y, pred_p, average="macro"),
           "macro_f1_enc": f1_score(y, pred_e, average="macro"), "total_he_sec": t_enc + t_srv + t_dec,
           "per_query_ms": 1000 * (t_enc + t_srv + t_dec) / n_enc,
           "split_ms": {"encrypt": 1000 * t_enc / n_enc, "server": 1000 * t_srv / n_enc, "decrypt": 1000 * t_dec / n_enc}}
    log(f"encrypted test split (N={N}): {enc['labels_identical']}/{n_enc} labels identical, "
        f"max |dz| {enc['max_abs_logit_diff']:.2e}, {enc['per_query_ms']:.1f} ms/query")

    # ---------------- the participant's claims, plaintext vs ciphertext
    Tc = svd.transform(tfidf.transform(claims)); Ec = np.asarray(m2v.encode(claims))
    Xc = sc.transform(fuse(Tc, Ec, features))
    claim_rows = []
    for i, ctext in enumerate(claims):
        zp = float(Xc[i] @ w + b)
        t0 = time.time(); c = ts.ckks_vector(ctx, Xc[i].tolist()); r = c.dot(wl) + b; ze = float(r.decrypt()[0]); dt = time.time() - t0
        claim_rows.append({"claim": ctext, "z_plain": zp, "z_enc": ze, "abs_diff": abs(zp - ze),
                           "p_fake_plain": 1 / (1 + np.exp(-zp)), "p_fake_enc": 1 / (1 + np.exp(-ze)),
                           "label_plain": "fake" if zp >= 0 else "real", "label_enc": "fake" if ze >= 0 else "real",
                           "ms": 1000 * dt, "query_bytes": len(c.serialize()), "reply_bytes": len(r.serialize())})

    # what the linear model learned, in TF-IDF term space (exact: the SVD + scaler are linear)
    term_w = None
    if features in ("tfidf", "hybrid"):
        wt = w[:svd_dim] / sc.scale_[:svd_dim]
        term_w = svd.components_.T @ wt
        vocab = np.array(tfidf.get_feature_names_out())
        o = np.argsort(term_w)
        top_terms = {"fake": [(vocab[j], float(term_w[j])) for j in o[::-1][:10]],
                     "real": [(vocab[j], float(term_w[j])) for j in o[:10]]}
    else:
        top_terms = None

    # ---------------- latency / size at the paper's parameters and smaller rings
    bench = []
    reps = max(10, 3 * len(claims))
    for Nb in [8192, 16384, 32768]:
        cx, cmb = (ctx, cm) if Nb == N else ckks_ctx(Nb)
        ts_ = []
        for k in range(reps):
            x = Xte[k % len(Xte)].tolist()
            t0 = time.time(); c = cx and ts.ckks_vector(cx, x); r = c.dot(wl) + b; _ = r.decrypt(); ts_.append(time.time() - t0)
        bench.append({"N": Nb, "coeff_mod_bit_sizes": cmb, "ms": 1000 * float(np.median(ts_)),
                      "query_MB": len(c.serialize()) / 1e6, "reply_MB": len(r.serialize()) / 1e6,
                      "comm_MB": (len(c.serialize()) + len(r.serialize())) / 1e6})
    log("per-query latency: " + ", ".join(f"N={x['N']}: {x['ms']:.1f} ms, {x['comm_MB']:.2f} MB" for x in bench))

    # ---------------- encrypted retrieval: naive vs SIMD-packed
    db_text = df["title"].fillna("").tolist()
    db_label = df["label"].values
    seen, keep = set(), []
    for i, s in enumerate(db_text):  # unique titles only (duplicates create exact ties)
        k = " ".join(s.lower().split())
        if len(k) > 15 and k not in seen:
            seen.add(k); keep.append(i)
    db_n = int(P.get("retrieval_db_size", 0) or 0)
    if 0 < db_n < len(keep):
        keep = sorted(np.random.default_rng(SEED).choice(keep, db_n, replace=False).tolist())
    DB = np.asarray(m2v.encode([db_text[i] for i in keep]), dtype=np.float64)
    DB /= np.linalg.norm(DB, axis=1, keepdims=True)
    Qc = Ec / np.linalg.norm(Ec, axis=1, keepdims=True)
    slots = N // 2
    shards = [DB[i:i + slots].T.tolist() for i in range(0, len(DB), slots)]
    t_plain = t_pack = 0.0; pack_bytes = 0; same_top5 = 0; retrieved = []; max_score_err = 0.0
    for i in range(len(claims)):
        t0 = time.time(); sp = DB @ Qc[i]; t_plain += time.time() - t0
        t0 = time.time(); c = ts.ckks_vector(ctx, Qc[i].tolist()); outs = [c.matmul(s) for s in shards]
        se = np.concatenate([np.array(o.decrypt()) for o in outs]); t_pack += time.time() - t0
        pack_bytes = len(c.serialize()) + sum(len(o.serialize()) for o in outs)
        tp, tq = np.argsort(-sp)[:5], np.argsort(-se)[:5]
        same_top5 += int(set(tp) == set(tq))
        max_score_err = max(max_score_err, float(np.abs(se - sp).max()))
        retrieved.append([{"title": short(db_text[keep[j]], 140), "label": "fake" if db_label[keep[j]] else "real",
                           "cos": float(sp[j])} for j in tq[:3]])
    n_naive = min(int(P.get("naive_items", 200)), len(DB))
    c = ts.ckks_vector(ctx, Qc[0].tolist())
    t0 = time.time(); naive_ct = [c.dot(DB[j].tolist()) for j in range(n_naive)]; t_naive_srv = time.time() - t0
    t0 = time.time(); _ = [o.decrypt() for o in naive_ct]; t_naive_dec = time.time() - t0
    naive_item_bytes = len(naive_ct[0].serialize())
    per_item = (t_naive_srv + t_naive_dec) / n_naive
    naive_full = per_item * len(DB) + 1e-3
    pack_q = t_pack / len(claims)
    retr = {"db_items": len(DB), "dim": int(DB.shape[1]), "naive_measured_items": n_naive,
            "plain_sec": t_plain / len(claims), "packed_sec": pack_q, "naive_sec_extrapolated": naive_full,
            "speedup": naive_full / pack_q, "packed_comm_MB": pack_bytes / 1e6,
            "naive_comm_MB": (len(c.serialize()) + naive_item_bytes * len(DB)) / 1e6,
            "same_top5": same_top5, "n_claims": len(claims), "n_ciphertexts_packed": len(shards),
            "max_score_err": max_score_err, "naive_sec_at_7128": per_item * 7128}
    log(f"retrieval over {len(DB)} items: packed {pack_q:.3f} s vs naive ≈ {naive_full:.1f} s "
        f"({retr['speedup']:.0f}x); top-5 identical {same_top5}/{len(claims)}")

    res.update(n_rows_raw=n_raw, n_unique=len(df), n_train=len(tr), n_test=len(te), n_test_fake=int(te.label.sum()),
               download_MB=nbytes / 1e6, text_field=text_field, features=features, svd_dim=svd_dim,
               feature_dim=int(Xte.shape[1]), embed_dim=int(Etr.shape[1]), ablation=ablation, encrypted=enc,
               claims=claim_rows, top_terms=top_terms, latency_bench=bench, retrieval=retr, retrieved=retrieved)
    res["n_claims_fake"] = sum(r["label_enc"] == "fake" for r in claim_rows)
    res["claims_max_abs_logit_diff"] = max(r["abs_diff"] for r in claim_rows)
    figures(res)
    card(res)
    res["runtime_sec"] = round(time.time() - T0, 1)
    (OUT / "results.json").write_text(json.dumps(res, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    a = ablation[features]
    log(f"done: {features} acc {a['accuracy']:.3f} / macro-F1 {a['macro_f1']:.3f}; encrypted labels identical "
        f"{enc['labels_identical']}/{enc['n']}; claims flagged fake {res['n_claims_fake']}/{len(claim_rows)}; "
        f"packed retrieval {retr['speedup']:.0f}x faster than naive")


def figures(res):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans"})
    # 1. claims
    cl = res["claims"]
    fig, ax = plt.subplots(figsize=(6.4, 0.9 + 0.62 * len(cl)))
    ys = np.arange(len(cl))[::-1]
    for yv, r in zip(ys, cl):
        ax.barh(yv, r["p_fake_plain"], color=ACC if r["label_plain"] == "fake" else BLUE, height=0.55, alpha=0.85)
        ax.plot(r["p_fake_enc"], yv, "D", color=INK, ms=6, mfc="white", mew=1.6, clip_on=False, zorder=5)
        ax.text(1.05, yv, f"{r['p_fake_enc']:.3f}\n|Δz| {r['abs_diff']:.0e}", va="center", fontsize=7.5, color=INK)
        ax.text(0.0, yv + 0.38, short(r["claim"], 88), fontsize=7.5, color=INK, va="bottom", zorder=4,
                bbox=dict(fc="white", ec="none", pad=0.6))
    ax.axvline(0.5, color=INK, ls="--", lw=1)
    ax.set_yticks([]); ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.6, len(cl) - 0.1)
    ax.set_xlabel("P(fake): bar = plaintext model, ◇ = decrypted from the encrypted score")
    ax.spines["left"].set_visible(False)
    fig.tight_layout(); fig.subplots_adjust(right=0.83); fig.savefig(OUT / "fig_claims.png", dpi=160); plt.close(fig)

    # 2. what the model learned
    if res["top_terms"]:
        tt = res["top_terms"]
        items = [(t, v) for t, v in tt["fake"][:9]] + [(t, v) for t, v in tt["real"][:9]][::-1]
        items.sort(key=lambda x: x[1])
        fig, ax = plt.subplots(figsize=(6.4, 3.8))
        ax.barh(range(len(items)), [v for _, v in items], color=[ACC if v > 0 else BLUE for _, v in items])
        ax.set_yticks(range(len(items))); ax.set_yticklabels([t for t, _ in items], fontsize=8)
        ax.axvline(0, color=INK, lw=1)
        ax.set_xlabel("effective weight on the term's TF-IDF value  (← real · fake →)")
        fig.tight_layout(); fig.savefig(OUT / "fig_terms.png", dpi=160); plt.close(fig)

    # 3. cost: per-query latency/comm vs ring size, and retrieval naive vs packed
    bench, rt = res["latency_bench"], res["retrieval"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1, 1.15]})
    xs = np.arange(len(bench))
    a1.bar(xs, [x["ms"] for x in bench], color=[MUTED, MUTED, ACC], width=0.6)
    for i, x in enumerate(bench):
        a1.text(i, x["ms"] * 1.03, f"{x['ms']:.0f} ms\n{x['comm_MB']:.2f} MB", ha="center", fontsize=7)
    a1.axhline(122.4, color=INK, ls="--", lw=1); a1.text(-0.4, 122.4 * 1.04, "paper 122.4 ms (N = 32,768)", fontsize=7)
    a1.set_xticks(xs); a1.set_xticklabels([f"N={x['N'] // 1024}k" for x in bench]); a1.set_ylabel("ms per encrypted claim")
    a1.set_ylim(0, max(140, max(x["ms"] for x in bench) * 1.35)); a1.set_title("classification", fontsize=9)
    labs = ["plaintext", "naive\n(1 ct / item)", "SIMD-packed"]
    vals = [rt["plain_sec"], rt["naive_sec_extrapolated"], rt["packed_sec"]]
    a2.bar(range(3), vals, color=[MUTED, ACC, BLUE], width=0.6); a2.set_yscale("log")
    for i, v in enumerate(vals):
        a2.text(i, v * 1.3, f"{v * 1000:.2f} ms" if v < 0.01 else f"{v:.3g} s", ha="center", fontsize=7.5)
    a2.plot([1, 2], [221.049, 5.186], "D", color=INK, ms=6, label="paper (7,128 items)")
    a2.set_xticks(range(3)); a2.set_xticklabels(labs, fontsize=8); a2.set_ylabel("s per retrieval query")
    a2.set_ylim(min(vals) / 3, max(vals + [221.049]) * 6)
    a2.set_title(f"retrieval over {rt['db_items']:,} items", fontsize=9); a2.legend(frameon=False, fontsize=7, loc="upper left")
    fig.tight_layout(); fig.savefig(OUT / "fig_cost.png", dpi=160); plt.close(fig)


def card(res):
    f = res["features"]; a = res["ablation"][f]; e = res["encrypted"]; rt = res["retrieval"]
    b32 = next(x for x in res["latency_bench"] if x["N"] == 32768)
    tiles = [
        {"label": f"CoAID test ({res['n_test']:,} items)", "value": f"{a['accuracy']:.3f} / {a['macro_f1']:.3f}",
         "sub": f"accuracy / macro-F1, {f} features ({res['feature_dim']}-d); paper hybrid 0.971 / 0.950", "tone": "neutral"},
        {"label": "Encrypted = plaintext", "value": f"{e['labels_identical']:,} / {e['n']:,}",
         "sub": f"identical labels; max logit error {e['max_abs_logit_diff']:.1e}", "tone": "good"},
        {"label": "Your claims flagged “fake”", "value": f"{res['n_claims_fake']} / {len(res['claims'])}",
         "sub": "scored without the server ever seeing the text", "tone": "accent"},
        {"label": "SIMD packing speed-up", "value": f"{rt['speedup']:.0f}×",
         "sub": f"{rt['naive_sec_extrapolated']:.1f} s → {rt['packed_sec']:.2f} s over {rt['db_items']:,} items (paper 42.6×)", "tone": "neutral"},
    ]
    compare = []
    for k in ["tfidf", "embed", "hybrid"]:
        name, pa, pf = PAPER_T1[k]
        ours = {"tfidf": f"TF-IDF→SVD{res['svd_dim']}", "embed": f"potion-base-8M ({res['embed_dim']}-d)",
                "hybrid": f"TF-IDF→SVD + potion ({res['ablation']['hybrid']['dim']}-d)"}[k]
        compare.append({"metric": f"Acc / macro-F1: {name} (paper) vs {ours}", "paper": f"{pa} / {pf}",
                        "yours": f"{res['ablation'][k]['accuracy']:.3f} / {res['ablation'][k]['macro_f1']:.3f}",
                        "note": "no BioBERT block; MPNet replaced by a static embedder" if k != "tfidf" else "same recipe"})
    compare += [
        {"metric": "Test split", "paper": "1,081 samples (184 fake, 897 real)", "yours": f"{res['n_test']:,} ({res['n_test_fake']} fake)", "note": f"deduplicated CoAID news, {res['text_field']}"},
        {"metric": "Plaintext vs ciphertext predictions", "paper": "identical accuracy and F1 scores for every feature configuration",
         "yours": f"{e['labels_identical']}/{e['n']} labels identical", "note": f"N = {e['poly_modulus_degree']:,}"},
        {"metric": "Per-query cost at N = 32,768", "paper": "approximately 122.4 ms and 2.133 MB", "yours": f"{b32['ms']:.1f} ms, {b32['comm_MB']:.2f} MB",
         "note": f"{res['feature_dim']}-d vs 1,324-d vector; different CPU"},
        {"metric": "Retrieval naive → SIMD-packed", "paper": "221.049 s → 5.186 s (42.6×), 6.11 GB → 2.13 MB",
         "yours": f"{rt['naive_sec_extrapolated']:.1f} s → {rt['packed_sec']:.2f} s ({rt['speedup']:.0f}×), {rt['naive_comm_MB'] / 1e3:.2f} GB → {rt['packed_comm_MB']:.2f} MB",
         "note": f"{rt['db_items']:,} items, {rt['dim']}-d, N = {e['poly_modulus_degree']:,}; naive extrapolated from {rt['naive_measured_items']}"},
    ]
    figs = [{"path": "fig_claims.png", "title": "Your claims, scored on ciphertext",
             "caption": "Bars: the model's probability that a claim resembles CoAID's “fake” class, computed in the clear. Diamonds: the same "
                        "probability from the encrypted score the server returned (client decrypts, applies the sigmoid). |Δz| = logit difference."}]
    if res["top_terms"]:
        figs.append({"path": "fig_terms.png", "title": "What the classifier actually keys on",
                     "caption": "Exact term weights obtained by pushing the logistic-regression weights back through the scaler and SVD. "
                                "Many cues are about source and format (fact-check phrasing vs agency article titles), not medical truth."})
    figs.append({"path": "fig_cost.png", "title": "What encryption costs",
                 "caption": "Left: median time per encrypted claim (encrypt + server dot product + decrypt) by CKKS ring size; the paper uses "
                            "N = 32,768. Right: encrypted similarity search returning one ciphertext per item (naive) vs all scores packed into one ciphertext."})
    inputs = {"claims": f"{len(res['claims'])} of yours", "features": f"{f} ({res['feature_dim']}-d)", "text": res["text_field"],
              "SVD dims": res["svd_dim"], "CKKS ring N": f"{e['poly_modulus_degree']:,}", "seed": res["params"].get("seed", 42)}
    Path(OUT / "card_data.json").write_text(json.dumps({
        "paper": {"num": 13, "title": "Privacy-Preserving Text Inference for Health-Misinformation Classification and Semantic Retrieval",
                  "authors": "Jasleen Kaur, Chloe Cachet, Koray Karabina, Jean Belo Klamti, Philippe Lamontagne", "url": "https://arxiv.org/abs/2610.20796",
                  "affiliation": "National Research Council of Canada · Florida Atlantic University"},
        "inputs": inputs, "tiles": tiles, "figures": figs, "compare": compare,
        "runbook": {"name": "smash-13-private-claim-check", "url": P.get("runbook_url", "")}}, indent=2))


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
