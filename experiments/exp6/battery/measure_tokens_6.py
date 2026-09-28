# experiments/exp6/battery/measure_tokens_6.py
"""Token lengths of every answer and prompt under every tokenizer the
experiment will score with — TOKENIZER FILES ONLY, no weight, run once
at the build into a cache outside the HF cache (HF_HUB_CACHE must be
set by the caller). Writes `token_lengths_6.json`; the budgets of
verify_6 are checked against it by the tests.

    HF_HUB_CACHE=<scratch dir> PYTHONDONTWRITEBYTECODE=1 \
        ~/emergence-lab/.venv/bin/python -m experiments.exp6.battery.measure_tokens_6
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "token_lengths_6.json"


def tokenizer_revisions() -> dict:
    """name -> {repo, commit}: the revision each model is scored at,
    read from the frozen, sha-pinned manifests of the experiments that
    first scored it (the predictors' and the four stage-1 endpoints)."""
    import sys
    from experiments.exp6 import verify_6 as v6
    v6.harness_2c()                          # puts exp2b on sys.path for `models`
    from models import PYTHIA_SHAS
    from experiments.exp2i import battery_2i as bi
    from experiments.exp2l import battery_2l as bl
    from experiments.exp2m import battery_2m as bm
    from experiments.exp2n import battery_2n as bn
    m_i = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    m_l = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    m_m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
    m_n = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
    return {
        "pythia_1b": {"repo": "EleutherAI/pythia-1b", "commit": PYTHIA_SHAS["1b"]},
        "pythia_410m": {"repo": "EleutherAI/pythia-410m",
                        "commit": PYTHIA_SHAS["410m"]},
        "olmo2_1b": {"repo": bi.REPO_1B,
                     "commit": bi.entry_1b_endpoint(m_i)["commit"]},
        "olmo2_7b": {"repo": bi.REPO_7B,
                     "commit": bi.entry_7b(m_i, bi.ENDPOINT_STEP_7B)["commit"]},
        "olmo2_13b": {"repo": bl.REPO_13B,
                      "commit": bl.entry_13b(m_l, bl.ENDPOINT_STEP_13B)["commit"]},
        "smollm3_3b": {"repo": bm.REPO_CKPT,
                       "commit": bm.entry_3b(m_m, bm.ENDPOINT_STEP_2M)["commit"]},
        "comma_7b": {"repo": bn.REPO_COMMA,
                     "commit": bn.entry_comma(m_n, bn.ENDPOINT_STEP_2N)["commit"]},
    }


def measure(out: Path = OUT) -> dict:
    if not os.environ.get("HF_HUB_CACHE"):
        raise SystemExit("set HF_HUB_CACHE to a scratch directory: this tool "
                         "must not write into the HF cache")
    from transformers import AutoTokenizer

    from experiments.exp6 import battery_6 as b6
    from experiments.exp6 import verify_6 as v6
    h = v6.harness_2c()
    revs = tokenizer_revisions()
    toks = {name: AutoTokenizer.from_pretrained(r["repo"], revision=r["commit"])
            for name, r in revs.items()}
    rungs = {}
    for rung in b6.ALL_RUNGS_6:
        cap = b6.load_item_file_6(rung)
        shots = [tuple(s) for s in cap["shots"]][:b6.N_SHOTS]
        rec = {"items_sha256": cap["items_sha256"],
               "budget": b6.max_new_tokens_6(rung),
               "answer_tokens_max": {}, "prompt_tokens_max": {}}
        for name, tok in toks.items():
            rec["answer_tokens_max"][name] = max(
                len(tok(" " + str(it["answer"]), add_special_tokens=False)["input_ids"])
                for it in cap["eval_items"])
            rec["prompt_tokens_max"][name] = max(
                len(tok(h.render_prompt(it["question"], shots),
                        add_special_tokens=False)["input_ids"])
                for it in cap["eval_items"])
        rungs[rung] = rec
    import transformers
    out_rec = {"note": "tokenizer files only; no weight loaded",
               "transformers": transformers.__version__,
               "tokenizers": revs, "rungs": rungs}
    Path(out).write_text(json.dumps(out_rec, indent=1, sort_keys=True) + "\n")
    return out_rec


if __name__ == "__main__":
    r = measure()
    for rung, rec in r["rungs"].items():
        print(f"{rung:18s} budget {rec['budget']:2d}  answer max "
              f"{max(rec['answer_tokens_max'].values()):2d}  prompt max "
              f"{max(rec['prompt_tokens_max'].values()):4d}")
    sys.exit(0)
