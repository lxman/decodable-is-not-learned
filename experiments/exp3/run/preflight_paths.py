"""Per-size compute-path preflight (PROGRESS.md 2026-08-15: the fp16
batched-step corruption).

On this stack, fp16-MPS batched (rows>1) single-token cached steps
return garbage for every row but row 0 on real-model shapes — found at
build by verifying rows against batch-1 logits_to_keep=1 references.
The campaign therefore runs mass and sampling at FLOAT32 (the same
fp16 checkpoint values, upcast exactly), and THIS script is the gate
that proves the batched paths correct for each (size, dtype) tier
before any cell runs: on synthetic prompts, every row of a
heterogeneous-id batched step must match its batch-1 reference within
float tolerance, and the depth-1 prompt distribution must match a
batch-1 re-forward.

A tier that fails preflight must not run — there is no verdict branch
for "the arithmetic was wrong"; there is only not collecting garbage.

    python -m experiments.exp3.run.preflight_paths --size 410m --dtype float32
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXP3 = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP3.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# Synthetic prompts (invented content, never a committed item) and a
# heterogeneous whitespace-id chunk — the configuration that exposed
# the fp16 corruption.
PREFLIGHT_PROMPTS = (
    "Q: Spell the string 'wqxzt' backwards.\nA:",
    "Q: What is 999 minutes after 03:17?\nA:",
)
CHUNK = (186, 187, 188, 189, 190, 205, 206, 207, 208, 209,
         210, 211, 212, 213, 214, 215)
ROW_TOL = 1e-4     # fp32 rows match references to ~1e-6; garbage is O(1)


def verify_paths(model, tok, prompts=PREFLIGHT_PROMPTS, chunk=CHUNK,
                 tol=ROW_TOL) -> dict:
    """Every row of a batched cached step vs its batch-1 reference, and
    the keep1 prompt distribution vs a plain batch-1 re-forward."""
    import torch

    checks = []
    for prompt in prompts:
        enc = tok(prompt, return_tensors="pt").to(model.device)
        plen = enc["input_ids"].shape[1]
        with torch.no_grad():
            out = model(**enc, use_cache=True, logits_to_keep=1)
            p1 = torch.softmax(out.logits[0, -1].to("cpu", torch.float32), -1)
            ref1 = torch.softmax(
                model(input_ids=enc["input_ids"], logits_to_keep=1)
                .logits[0, -1].to("cpu", torch.float32), -1)
            d1 = float((p1 - ref1).abs().max())
            checks.append({"check": "prompt keep1 vs re-forward",
                           "prompt": prompt[:24], "max_diff": d1,
                           "ok": d1 <= tol})

            pkv = out.past_key_values
            pkv.batch_repeat_interleave(len(chunk))
            attn = torch.ones((len(chunk), plen + 1), device=model.device,
                              dtype=torch.long)
            st = model(input_ids=torch.tensor([[w] for w in chunk],
                                              device=model.device),
                       past_key_values=pkv, attention_mask=attn)
            worst, bad = 0.0, []
            for row, w in enumerate(chunk):
                p = torch.softmax(st.logits[row, -1].to("cpu", torch.float32),
                                  -1)
                full = torch.cat([enc["input_ids"],
                                  torch.tensor([[w]], device=model.device)], 1)
                ref = torch.softmax(
                    model(input_ids=full, logits_to_keep=1)
                    .logits[0, -1].to("cpu", torch.float32), -1)
                d = float((p - ref).abs().max())
                worst = max(worst, d)
                if d > tol:
                    bad.append({"row": row, "id": w, "max_diff": d})
            checks.append({"check": "batched step rows vs batch-1 refs",
                           "prompt": prompt[:24], "rows": len(chunk),
                           "worst_diff": worst, "bad_rows": bad,
                           "ok": not bad})
    return {"n_checks": len(checks),
            "all_ok": all(c["ok"] for c in checks),
            "checks": checks}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", required=True)
    ap.add_argument("--dtype", default="float32",
                    choices=("float32", "float16"))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    import torch

    from models import load_pythia  # noqa: PLC0415

    tok, model = load_pythia(a.size, untrained=False, device=a.device)
    if a.dtype == "float32":
        model = model.to(torch.float32)   # exact upcast of fp16 weights

    rep = verify_paths(model, tok)
    rep["size"], rep["dtype"], rep["device"] = a.size, a.dtype, a.device
    rep["torch"] = torch.__version__
    out = Path(a.out) if a.out else EXP3 / f"preflight_{a.size}_{a.dtype}.json"
    out.write_text(json.dumps(rep, indent=1))
    print(f"[preflight] {a.size}/{a.dtype}: "
          f"{'OK' if rep['all_ok'] else 'FAIL'} -> {out}")
    return 0 if rep["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
