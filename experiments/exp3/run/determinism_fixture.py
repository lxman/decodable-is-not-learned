"""Gate 4's freeze artifact: MPS seeded-sampling determinism (design
§6.4, doc Open item 2).

Samples SYNTHETIC pinned prompts — invented strings, none of them a
committed item; the stream tag is a dedicated namespace so these
streams can never collide with campaign streams — through the exact
campaign path: pythia-410m trained, fp16, MPS, `sampler.sample_item`,
T = 1.0 untruncated, 12 new tokens, 16-row chunks.

Run twice in separate processes; the two outputs must be
byte-identical. The committed reference output lets the freeze session
(and the campaign preflight) re-run cold and detect any stack drift
since the build: torch/transformers versions are serialized INTO the
compared bytes on purpose.

    python -m experiments.exp3.run.determinism_fixture --out one.json
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

from experiments.exp3.sampler import sample_item  # noqa: E402

# Pinned synthetic prompts — 2c's rendering shape, invented content.
FIXTURE_PROMPTS = (
    "Q: Spell the string 'qzmvw' backwards.\nA:",
    "Q: Repeat the string 'blorfk'.\nA:",
    "Q: What is 999 minutes after 03:17?\nA:",
)
FIXTURE_RUNG = "determinism_fixture"   # dedicated stream namespace tag
FIXTURE_SEEDS = (0, 1)
FIXTURE_DRAWS = 8
FIXTURE_TOKENS = 12


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--size", default="410m")
    ap.add_argument("--dtype", default="float32",
                    choices=("float32", "float16"))
    a = ap.parse_args(argv)

    import torch
    import transformers

    from models import load_pythia  # noqa: PLC0415

    tok, model = load_pythia(a.size, untrained=False, device=a.device)
    if a.dtype == "float32":
        # The campaign dtype policy (PROGRESS.md 2026-08-15): batched
        # steps run fp32 — the fp16 batched-step path is broken on this
        # stack. Exact upcast of the same fp16 checkpoint values.
        model = model.to(torch.float32)
    out = {
        "stack": {"torch": torch.__version__,
                  "transformers": transformers.__version__,
                  "device": a.device, "size": a.size, "dtype": a.dtype},
        "prompts": list(FIXTURE_PROMPTS),
        "seeds": list(FIXTURE_SEEDS),
        "draws_per_seed": FIXTURE_DRAWS,
        "max_new_tokens": FIXTURE_TOKENS,
        "draws": {},
    }
    for i, prompt in enumerate(FIXTURE_PROMPTS):
        got = sample_item(model, tok, prompt, rung=FIXTURE_RUNG,
                          size=a.size, mode="trained", item_idx=i,
                          seeds=FIXTURE_SEEDS, draws_per_seed=FIXTURE_DRAWS,
                          max_new_tokens=FIXTURE_TOKENS)
        out["draws"][f"prompt{i}"] = {f"s{s}": got[s] for s in FIXTURE_SEEDS}

    p = Path(a.out)
    p.write_text(json.dumps(out, indent=1, sort_keys=True))
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
