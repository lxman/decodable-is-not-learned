"""The Exp 5 loss slice (design §3.1, dial c; B-2) and the slice loss.

Build-time (Mac, once, committed): the Pile-validation file at its pinned
dataset revision, sha-checked; documents in file order, streamed from
the zstd stream; 2c's pinned Pythia tokenizer, no specials, truncation at
2048; documents under 64 tokens skipped and counted; accumulated until
EXACTLY 2^21 scored tokens (the crossing document truncated to fill).
`slice_5.npz` is byte-deterministic (numpy's savez_compressed zeroes the
zip timestamps) and re-derived cold by `verify_referents_5`.

Run-time (the host): `slice_loss_5` consumes the committed token ids only
— the host never tokenizes. Batches of LOSS_BATCH_5 documents in slice
order, right-padded with PAD_ID_5, attention-masked; fp16 logits → fp32
log-softmax → the target's −log p; the first token of each document
unscored; per-document sums in float64 on the CPU, in slice order, so
the value is a deterministic function of the weights on a host."""
from __future__ import annotations

import hashlib
import io
import json
import sys
import time
from pathlib import Path

EXP5 = Path(__file__).resolve().parent
REPO = EXP5.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
import numpy as np  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402

SLICE_CACHE_5 = Path.home() / "emergence-lab" / "pile_val_5"
_META_KEYS = ("n_docs", "n_read", "n_skipped", "n_scored", "last_doc_truncated", "max_tokens",
              "min_tokens", "tokenizer", "source")


# ------------------------------------------------------------ the file

def slice_file_path_5(cache_root=SLICE_CACHE_5) -> Path:
    """NETWORK once (a dataset file, not a model): the pinned val file
    into `cache_root`, then sha256 and size against the pins."""
    from huggingface_hub import hf_hub_download
    p = Path(hf_hub_download(b5.SLICE_DATASET_5, b5.SLICE_FILE_5, repo_type="dataset",
                             revision=b5.SLICE_REVISION_5, cache_dir=str(cache_root)))
    verify_slice_file_5(p)
    return p.resolve()


def verify_slice_file_5(path) -> dict:
    p = Path(path)
    size = p.stat().st_size
    if size != b5.SLICE_FILE_SIZE_5:
        raise ValueError(f"{p}: {size} bytes, pinned {b5.SLICE_FILE_SIZE_5}")
    sha = bg.sha256_file(p)
    if sha != b5.SLICE_FILE_SHA256_5:
        raise ValueError(f"{p}: sha256 {sha}, pinned {b5.SLICE_FILE_SHA256_5}")
    return {"path": str(p), "size": size, "sha256": sha}


def iter_documents_5(path):
    import zstandard as zstd
    with open(path, "rb") as fh:
        reader = zstd.ZstdDecompressor().stream_reader(fh)
        with io.TextIOWrapper(reader, encoding="utf-8") as text:
            for line in text:
                if not line.strip():
                    continue
                rec = json.loads(line)
                yield rec["text"], rec["meta"]["pile_set_name"]


# --------------------------------------------------------- the tokenizer

def load_slice_tokenizer_5():
    """2c's pinned Pythia tokenizer (`models.load_tokenizer`, at
    PYTHIA_SHAS["2.8b"]) — NETWORK for the tokenizer files if not cached."""
    from models import load_tokenizer
    return load_tokenizer(b5.TOKENIZER_SIZE_5)


def tokenizer_pins_5(tok) -> dict:
    """No BOS/EOS added by the tokenizer's post-processor on a plain
    render; eos id == PAD_ID_5. Refuses otherwise."""
    a = tok("Q: 1\nA:", add_special_tokens=True)["input_ids"]
    b = tok("Q: 1\nA:", add_special_tokens=False)["input_ids"]
    if a != b:
        raise ValueError("the tokenizer adds special tokens on a plain render")
    if tok.eos_token_id != b5.PAD_ID_5:
        raise ValueError(f"eos id {tok.eos_token_id} != PAD_ID_5 {b5.PAD_ID_5}")
    return {"adds_specials": False, "eos_id": int(tok.eos_token_id), "pad_id": b5.PAD_ID_5,
            "size": b5.TOKENIZER_SIZE_5, "revision": b5.MAIN_SHA_5[b5.TOKENIZER_SIZE_5]}


def tokenizer_json_shas_5(cache_root=SLICE_CACHE_5) -> dict:
    """NETWORK (seven small files): sha256 of `tokenizer.json` at every
    size's pinned main commit; the build asserts they are all equal and
    pins the value as battery_5.TOKENIZER_JSON_SHA256_5."""
    from huggingface_hub import hf_hub_download
    out = {}
    for size in b5.SIZES_5:
        p = hf_hub_download(b5.REPO_OF_5[size], "tokenizer.json", revision=b5.MAIN_SHA_5[size],
                            cache_dir=str(Path(cache_root) / "tokenizers"))
        out[size] = bg.sha256_file(p)
    return out


# ------------------------------------------------------------- the slice

def build_slice_5(tok, path, *, n_scored=b5.SLICE_N_SCORED_5, max_tokens=b5.SLICE_MAX_TOKENS_5,
                  min_tokens=b5.SLICE_MIN_TOKENS_5) -> dict:
    ids_all, offsets, set_idx, set_names = [], [0], [], []
    name_index = {}
    n_read = n_skipped = total = 0
    last_truncated = None
    done = False
    for text, set_name in iter_documents_5(path):
        n_read += 1
        ids = list(tok(text, add_special_tokens=False, truncation=True,
                       max_length=max_tokens)["input_ids"])
        if len(ids) < min_tokens:
            n_skipped += 1
            continue
        scored = len(ids) - 1
        if total + scored >= n_scored:
            keep = n_scored - total + 1
            if keep < len(ids):
                last_truncated = {"doc_index": len(set_idx), "from": len(ids), "to": keep}
                ids = ids[:keep]
            scored = len(ids) - 1
            done = True
        ids_all.extend(int(i) for i in ids)
        offsets.append(len(ids_all))
        set_idx.append(name_index.setdefault(set_name, len(name_index)))
        if len(set_names) < len(name_index):
            set_names.append(set_name)
        total += scored
        if done:
            break
    if total != n_scored:
        raise ValueError(f"the file ran out at {total} scored tokens, {n_scored} wanted")
    meta = {"n_docs": len(set_idx), "n_read": n_read, "n_skipped": n_skipped, "n_scored": total,
            "last_doc_truncated": last_truncated, "max_tokens": int(max_tokens),
            "min_tokens": int(min_tokens),
            "tokenizer": getattr(tok, "_pins_5", None),
            "source": {"dataset": b5.SLICE_DATASET_5, "revision": b5.SLICE_REVISION_5,
                       "file": b5.SLICE_FILE_5, "sha256": b5.SLICE_FILE_SHA256_5}}
    return {"ids": np.asarray(ids_all, dtype=np.int32), "offsets": np.asarray(offsets, np.int64),
            "set_index": np.asarray(set_idx, np.int16), "set_names": list(set_names), "meta": meta}


def write_slice_5(path, sl: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(Path(path), ids=sl["ids"], offsets=sl["offsets"],
                        set_index=sl["set_index"],
                        set_names=np.asarray(sl["set_names"], dtype="U64"),
                        meta=np.asarray(json.dumps(sl["meta"], sort_keys=True), dtype="U"))


def load_slice_5(path=b5.SLICE_PATH_5, *, sha_pin) -> dict:
    p = Path(path)
    got = bg.sha256_file(p)
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{p} hashes to {got}, pinned {sha_pin}")
    with np.load(p, allow_pickle=False) as z:
        sl = {"ids": z["ids"].astype(np.int32), "offsets": z["offsets"].astype(np.int64),
              "set_index": z["set_index"].astype(np.int16),
              "set_names": [str(s) for s in z["set_names"]],
              "meta": json.loads(str(z["meta"]))}
    sl["sha256"] = got
    n = int((sl["offsets"][1:] - sl["offsets"][:-1] - 1).sum())
    if n != sl["meta"]["n_scored"] or len(sl["offsets"]) != sl["meta"]["n_docs"] + 1:
        raise ValueError(f"{p}: arrays disagree with meta ({n} scored, {len(sl['offsets']) - 1} docs)")
    return sl


def slice_equal_5(a: dict, b: dict) -> list:
    diffs = []
    for k in ("ids", "offsets", "set_index"):
        if not np.array_equal(np.asarray(a[k]), np.asarray(b[k])):
            diffs.append(k)
    if list(a["set_names"]) != list(b["set_names"]):
        diffs.append("set_names")
    for k in _META_KEYS:
        if k == "tokenizer":
            continue
        if a["meta"].get(k) != b["meta"].get(k):
            diffs.append(f"meta.{k}")
    return diffs


# ------------------------------------------------------------- the loss

def slice_batches_5(sl: dict, batch_size: int):
    offsets = sl["offsets"]
    n_docs = len(offsets) - 1
    for b in range(0, n_docs, batch_size):
        docs = list(range(b, min(b + batch_size, n_docs)))
        lens = [int(offsets[d + 1] - offsets[d]) for d in docs]
        T = max(lens)
        ids = np.full((len(docs), T), b5.PAD_ID_5, dtype=np.int64)
        mask = np.zeros((len(docs), T), dtype=np.int64)
        for j, d in enumerate(docs):
            ids[j, :lens[j]] = sl["ids"][offsets[d]:offsets[d + 1]]
            mask[j, :lens[j]] = 1
        yield docs, ids, mask


def loss_from_per_doc_5(sl: dict, per_doc_sums, per_doc_n) -> dict:
    """The pure aggregation: token-weighted mean over all scored tokens,
    per-set means, per-document means (rounded to 1e-6 for the record)."""
    sums = np.asarray(per_doc_sums, dtype=np.float64)
    ns = np.asarray(per_doc_n, dtype=np.int64)
    set_index = np.asarray(sl["set_index"])
    per_set = {}
    for k, name in enumerate(sl["set_names"]):
        m = set_index == k
        n_k = int(ns[m].sum())
        per_set[name] = {"loss": float(sums[m].sum() / n_k) if n_k else None, "n_tokens": n_k}
    n = int(ns.sum())
    return {"loss": float(sums.sum() / n), "n_scored": n, "n_docs": int(len(ns)),
            "per_set": per_set,
            "per_doc_loss": [round(float(s / c), 6) if c else None for s, c in zip(sums, ns)]}


def slice_loss_5(model, sl: dict, *, batch_size=b5.LOSS_BATCH_5, device: str) -> dict:
    """MODEL CONTACT. See the module docstring for the pins."""
    import torch
    t0 = time.time()
    n_docs = len(sl["offsets"]) - 1
    sums = np.zeros(n_docs, dtype=np.float64)
    ns = np.zeros(n_docs, dtype=np.int64)
    n_nonfinite = 0
    with torch.no_grad():
        for docs, ids, mask in slice_batches_5(sl, batch_size):
            x = torch.from_numpy(ids).to(device)
            m = torch.from_numpy(mask).to(device)
            logits = model(input_ids=x, attention_mask=m).logits          # fp16 [B, T, V]
            logp = torch.log_softmax(logits[:, :-1, :].float(), dim=-1)  # fp32
            tgt = x[:, 1:]
            nll = -logp.gather(-1, tgt.unsqueeze(-1)).squeeze(-1)        # fp32 [B, T-1]
            valid = m[:, 1:].bool()
            nll = torch.where(valid, nll, torch.zeros_like(nll))
            n_nonfinite += int((~torch.isfinite(nll)).sum().item())
            nll_cpu = nll.double().cpu().numpy()
            v_cpu = valid.cpu().numpy()
            for j, d in enumerate(docs):
                sums[d] = float(nll_cpu[j][v_cpu[j]].sum())
                ns[d] = int(v_cpu[j].sum())
            del logits, logp, nll
    out = loss_from_per_doc_5(sl, sums, ns)
    out.update({"finite": n_nonfinite == 0, "n_nonfinite": int(n_nonfinite),
                "batch_size": int(batch_size), "pad_id": b5.PAD_ID_5,
                "logits_dtype": "float16", "log_softmax_dtype": "float32",
                "accumulation": "float64 per document on the CPU, slice order",
                "slice_sha256": sl.get("sha256"), "seconds": round(time.time() - t0, 1)})
    return out


if __name__ == "__main__":
    # BUILD, once: download + verify the file, pin the tokenizer, build + write the slice.
    path = slice_file_path_5()
    tok = load_slice_tokenizer_5()
    pins = tokenizer_pins_5(tok)
    tok._pins_5 = pins
    shas = tokenizer_json_shas_5()
    if len(set(shas.values())) != 1:
        raise SystemExit(f"tokenizer.json differs across sizes: {shas}")
    sl = build_slice_5(tok, path)
    write_slice_5(b5.SLICE_PATH_5, sl)
    print("tokenizer.json sha256 (all seven sizes):", next(iter(shas.values())))
    print("slice meta:", json.dumps(sl["meta"], sort_keys=True))
    print("slice_5.npz sha256:", bg.sha256_file(b5.SLICE_PATH_5),
          f"({b5.SLICE_PATH_5.stat().st_size / 1e6:.1f} MB)")
