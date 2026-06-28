#!/usr/bin/env python3
"""Generate pelican-ICP assets via Replicate (uses curl for TLS). Usage:
  gen.py recraft <out.png> [style] <<<"PROMPT"
  gen.py nano    <out.png> <ref1.png[,ref2.png]> <<<"PROMPT"
"""
import os, sys, json, time, base64, subprocess, tempfile

KEY = os.environ["REPLICATE_API_KEY"]
API = "https://api.replicate.com/v1"

def curl(args):
    r = subprocess.run(["curl", "-sS"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        print("curl err", r.returncode, r.stderr[:1000]); sys.exit(1)
    return r.stdout

def data_uri(path):
    b = open(path, "rb").read()
    return "data:image/png;base64," + base64.b64encode(b).decode()

def post(url, payload, wait=True):
    f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(payload, f); f.close()
    args = ["-X", "POST", url,
            "-H", f"Authorization: Bearer {KEY}",
            "-H", "Content-Type: application/json"]
    if wait:
        args += ["-H", "Prefer: wait"]
    args += ["--data", f"@{f.name}"]
    out = curl(args)
    os.unlink(f.name)
    return json.loads(out)

def get(url):
    out = curl([url, "-H", f"Authorization: Bearer {KEY}"])
    return json.loads(out)

def poll(pred):
    url = pred["urls"]["get"]
    for _ in range(150):
        if pred.get("status") in ("succeeded", "failed", "canceled"):
            return pred
        time.sleep(2)
        pred = get(url)
    return pred

def extract_url(out):
    if isinstance(out, str): return out
    if isinstance(out, list) and out:
        return out[0] if isinstance(out[0], str) else out[0].get("url")
    if isinstance(out, dict): return out.get("url")
    return None

def main():
    engine, outpath = sys.argv[1], sys.argv[2]
    prompt = sys.stdin.read().strip()
    if engine == "recraft":
        url = f"{API}/models/recraft-ai/recraft-v3/predictions"
        style = sys.argv[3] if len(sys.argv) > 3 else "vector_illustration"
        payload = {"input": {"prompt": prompt, "style": style, "size": "1024x1024"}}
    elif engine == "nano":
        url = f"{API}/models/google/nano-banana/predictions"
        refs = [data_uri(p) for p in sys.argv[3].split(",")]
        payload = {"input": {"prompt": prompt, "image_input": refs, "output_format": "png"}}
    else:
        print("unknown engine"); sys.exit(1)

    pred = post(url, payload)
    if "urls" not in pred:
        print("BAD RESPONSE", json.dumps(pred)[:1500]); sys.exit(1)
    pred = poll(pred)
    if pred.get("status") != "succeeded":
        print("FAILED", pred.get("status"), json.dumps(pred.get("error")), json.dumps(pred.get("logs",""))[:1200]); sys.exit(1)
    u = extract_url(pred["output"])
    if not u:
        print("no output url", json.dumps(pred["output"])[:500]); sys.exit(1)
    curl(["-o", outpath, u])
    print("OK", outpath, "|", u)

if __name__ == "__main__":
    main()
