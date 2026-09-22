# experiments/exp5/tests/fakes_5.py
"""Fake loaders for the runner tests: no torch, no network. A fake model is
a dict {"size", "step", "digest"}; the fake runner answers exactly
`count_fn(size, step, rung)` items per rung correctly (the first k eval
items) and " zzz" for the rest, so every rung record re-verifies; the
fake loss is `loss_fn(size, step)`."""
from __future__ import annotations

import hashlib

from experiments.exp2d import battery_2d as bt
from experiments.exp5 import battery_5 as b5


class FakeRunner:
    def __init__(self, battery, count_fn, size, step, raise_on=None):
        self.by_prompt = {}
        h = bt.harness_2c()
        for r, cap in battery.items():
            shots = [tuple(s) for s in cap["shots"]][:bt.N_SHOTS]
            for i, it in enumerate(cap["eval_items"]):
                self.by_prompt[h.render_prompt(it["question"], shots)] = (r, i, it["answer"])
        self.count_fn, self.size, self.step, self.raise_on = count_fn, size, step, raise_on

    def generate(self, prompts, max_new_tokens):
        out = []
        for p in prompts:
            r, i, ans = self.by_prompt[p]
            if self.raise_on == r:
                raise RuntimeError(f"fake failure inside {r}")
            out.append(f" {ans}\n\nQ:" if i < self.count_fn(self.size, self.step, r) else " zzz")
        return out


def make_loaders(battery, *, loss_fn, count_fn, digest_fn=None, pythia_2c_digest=None,
                 pythia_2c_count_fn=None, loss_2c_fn=None, raise_on=None, n_params=1000):
    digest_fn = digest_fn or (lambda size, step: hashlib.sha256(f"d-{size}-{step}".encode()).hexdigest())
    state = {"loaded": [], "freed": [], "released": 0, "prefetched": []}

    def checkpoint(size, step, entry, *, cache_root, device):
        state["loaded"].append((size, step))
        info = {"size": size, "step": int(step), "revision": entry["revision"],
                "commit": entry["commit"], "kind": entry["kind"], "files": list(entry["files"]),
                "sha256": dict(entry["lfs_sha256"]),
                "config_source": f"{b5.REPO_OF_5[size]}@{b5.MAIN_SHA_5[size]}",
                "tokenizer_source": f"{b5.REPO_OF_5[size]}@{b5.MAIN_SHA_5[size]}",
                "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0},
                "download_seconds": 0.1, "transport": "fake"}
        return {"size": size, "step": int(step), "digest": digest_fn(size, step), "path": "b"}, info

    def pythia_2c(size, device):
        m = {"size": size, "step": b5.FINAL_STEP_5, "path": "a",
             "digest": pythia_2c_digest or digest_fn(size, b5.FINAL_STEP_5)}
        return m, dict(m)          # the fake "model" IS its info dict (digest/runner read it)

    def runner(tok, model):
        if model.get("path") == "a" and pythia_2c_count_fn is not None:
            return FakeRunner(battery, pythia_2c_count_fn, model["size"], model["step"])
        return FakeRunner(battery, count_fn, model["size"], model["step"], raise_on=raise_on)

    def loss(model, sl, *, batch_size, device):
        fn = loss_2c_fn if (model.get("path") == "a" and loss_2c_fn is not None) else loss_fn
        v = float(fn(model["size"], model["step"]))
        n_docs = len(sl["offsets"]) - 1
        per_set = {name: {"loss": v, "n_tokens": 0} for name in sl["set_names"]}
        for d in range(n_docs):
            per_set[sl["set_names"][int(sl["set_index"][d])]]["n_tokens"] += \
                int(sl["offsets"][d + 1] - sl["offsets"][d] - 1)
        return {"loss": v, "n_scored": sl["meta"]["n_scored"], "n_docs": n_docs, "per_set": per_set,
                "per_doc_loss": [v] * n_docs, "finite": True, "n_nonfinite": 0,
                "batch_size": batch_size, "pad_id": b5.PAD_ID_5, "logits_dtype": "float16",
                "log_softmax_dtype": "float32", "accumulation": "fake", "slice_sha256": sl["sha256"],
                "seconds": 0.0}

    def free(size, step, cache_root):
        state["freed"].append((size, step))

    def prefetch(size, entry, cache_root):
        state["prefetched"].append((size, entry["revision"]))

    return {"checkpoint": checkpoint, "pythia_2c": pythia_2c, "tokenizer": lambda size: object(),
            "runner": runner, "digest": lambda m: m["digest"], "free": free, "loss": loss,
            "release": lambda m: state.__setitem__("released", state["released"] + 1),
            "n_params": lambda m: n_params, "prefetch": prefetch}, state


def small_slice():
    """A 3-document slice with a sha, enough for the fake loss."""
    import numpy as np
    return {"ids": np.zeros(200, np.int32), "offsets": np.array([0, 70, 140, 200]),
            "set_index": np.array([0, 1, 0], np.int16), "set_names": ["A", "B"],
            "meta": {"n_scored": 197, "n_docs": 3}, "sha256": "slice-fake"}


def synthetic_manifest(sizes, available):
    out = {}
    for size in sizes:
        entries = {}
        for s in available:
            rev = "main" if s == b5.FINAL_STEP_5 else f"step{s}"
            entries[str(s)] = {"revision": rev, "commit": (b5.MAIN_SHA_5[size] if rev == "main" else f"c{s}"),
                               "kind": "safetensors-single", "files": ["model.safetensors"],
                               "lfs_sha256": {"model.safetensors": f"sha-{size}-{s}"},
                               "lfs_size": {"model.safetensors": 1}}
        out[size] = {"size": size, "repo": b5.REPO_OF_5[size], "main_commit": b5.MAIN_SHA_5[size],
                     "entries": entries, "excluded": {}, "available": sorted(available),
                     "step0": None, "final_duplicates": [], "hub_step143000": {}, "n_revisions": 0}
    return out


def fake_host(device="cuda"):
    return {"stack": {"torch": "2.12.1+cu130", "transformers": "5.13.0", "numpy": "2.4.6",
                      "safetensors": "0.8.0", "tokenizers": "0.22.2", "huggingface_hub": "1.22.0"},
            "device": device, "gpu": "fake", "python": "3.11.16",
            "transports": {"classic_mbps": 11.0, "xet_mbps": 300.0, "used": "xet"},
            "hf_hub_disable_xet": None}
