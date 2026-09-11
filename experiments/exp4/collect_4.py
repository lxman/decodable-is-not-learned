# experiments/exp4/collect_4.py
"""Experiment 4's per-load pipeline (design `experiment-4-design.md`
§3.1-§3.3, §3.8; Task 3): render + position rule (2c's `screen`, 2n's
comma-only BOS render), the activation collector (2f's `collect_items`
with the site-selection-before-`.cpu()` and float32-then-fp16 pooling
deltas), the k-NN/pooled set-table builders and the global bank
(metric_4, pure numpy), the per-reference overlap tables and alignment
scalars, the write+re-read persistence (`write_load_4`), the whole-load
orchestration (`process_model_4`), the reference-table reader
(`load_ref_tables_4`) and the reference-to-reference ceiling
(`cross_reference_4`).

Storage layout, a Task 3 design decision the brief's Interfaces block
names but does not fully pin (battery_4's `load_record_4` carries
exactly four sha fields — `sets_sha256`, `global_sha256`,
`attested_sha256`, `activation_sha256` — so every artifact this module
writes has to fold into one of those four groups):

- `sets/<rung>.npz` (COMMITTED — git-tracked, small): array `sets`
  uint16 `[n_sites, 500, k]`, the model's OWN prompt-end k-NN sets;
  plus, when references are being aligned against, one `overlap_<ref>`
  uint8 `[n_sites, 500]` array per reference (§3.8's "per-item overlaps
  at the prompt-end position ... committed" — folded into the same
  file/sha as the sets they were computed from, since the record has
  no separate overlaps sha).
- `attested/<rung>.npz` (sha-attested, gitignored): `question_end`
  and `pooled` k-NN set tables, uint16 `[n_sites, 500, k]` each.
- `activations/<rung>.npz` (sha-attested, gitignored, deleted after
  the re-read when `keep_activations=False`): raw `X` fp16
  `[500, n_sites, 2, d]` and `P` fp16 `[500, n_sites, d]`.
- `global.npz` (COMMITTED, reference-stage keys only — a `(traj,
  step)` sweep unit never gets one): array `sets` uint16
  `[n_sites, 17000, k]`, the bank order as a `order` array of
  `"<rung>:<i>"` strings.
- `align.json`: `{rung: {ref: {...align_scalars_4 keys...}}}`.

`align_scalars_4`'s `refs` argument therefore carries, per reference,
whichever of `sets_prompt_end` (always — the only universally
COMMITTED artifact), `sets_question_end`/`sets_pooled` (from the
reference's attested file, when present) and `activations_prompt_end`
(from the reference's activations file, when present — resolution 7:
CKA only when it exists) a caller could assemble; a missing piece
degrades its own output key to `None` rather than refusing the whole
call.

`load_ref_tables_4`'s literal return (`{ref: {"sets": {rung: ...},
"sites": [...], "n_hidden": int, "record": rec}}`) is the brief's
minimum; this build's implementation adds `sets_question_end`/
`sets_pooled` dicts alongside `sets` (loaded from `attested/<rung>.npz`
when the file exists) since `process_model_4`/`cross_reference_4` need
that data from the SAME loader call and there is nowhere else for it
to come from without a second reader for the same files."""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

EXP4 = Path(__file__).resolve().parent
EXPERIMENTS = EXP4.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2c.run import screen  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2i.run._common_2i import release as _release  # noqa: E402
from experiments.exp2n import battery_2n as bn  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402


# --------------------------------------------------------------- render

def render_prompts_4(family: str, cap: dict) -> list:
    """2c's `_render_prompt` over `cap["eval_items"]` with `cap["shots"]`
    (2f/2c's collector, verbatim); the comma family additionally gets
    2n's `<|begin_of_text|>` prefix (`RENDER_4[family] == "bos"`)."""
    shots = [tuple(s) for s in cap["shots"]]
    prompts = [screen._render_prompt(it["question"], shots) for it in cap["eval_items"]]
    if battery_4.RENDER_4[family] == "bos":
        prompts = bn.render_2n(prompts)
    return prompts


def positions_4(tok, prompts) -> list:
    """`screen._position_indices` per prompt: `(question_end, prompt_end)`
    token indices, matching `battery_4.POSITIONS_4`'s order."""
    return [screen._position_indices(tok, p) for p in prompts]


# ------------------------------------------------------------- collect

def _stacked_sites(hidden_states, sites):
    """Site-selected stack of the `hidden_states` tuple, without ever
    materialising the full layer stack on the host (design §3.1,
    resolution 2): a real torch model's hidden states are stacked and
    fancy-indexed ON DEVICE (`torch.stack(...)[sites]`), so only the
    site subset is later moved to CPU per batch item. The test shim
    (`fakes_4.FakeModel`) is already host-resident numpy with no torch
    tensors to defer, so its layers are simply selected then stacked
    with numpy — an equivalent result by the property that matters
    (only `sites`, never all layers, is ever assembled)."""
    is_torch = False
    try:
        import torch
        is_torch = torch.is_tensor(hidden_states[0])
    except ImportError:
        pass
    if is_torch:
        import torch
        return torch.stack(hidden_states, dim=0)[sites]
    return np.stack([np.asarray(hidden_states[i]) for i in sites], axis=0)


def _to_numpy(x):
    if hasattr(x, "cpu"):
        x = x.cpu()
    if hasattr(x, "numpy"):
        return np.asarray(x.numpy())
    return np.asarray(x)


def collect_rung_4(model, tok, family, cap, *, sites, batch_size, device, key=None) -> dict:
    """2f's `collect_items` loop with Task 3's deltas: item-file order,
    right padding, `add_special_tokens=False`, `output_hidden_states=
    True`, sites selected before `.cpu()`, the pooled variant (the
    attention-mask-weighted mean over valid tokens, float32 then fp16).
    `key`, when given, pins `batch_size` to `battery_4.BATCH_4[key]`
    (the family-native key for a reference/endpoint/init/ladder unit,
    or the trajectory name for a sweep step) — the batch composition
    is part of the instrument (design §3.1: a valid position's fp16
    residual can move by an ulp when its batch-mates change)."""
    import torch

    if key is not None:
        want = battery_4.BATCH_4[key]
        if int(batch_size) != int(want):
            raise ValueError(
                f"collect_rung_4: batch_size {batch_size} != the pinned {want} for {key!r}")

    prompts = render_prompts_4(family, cap)
    old_side = tok.padding_side
    tok.padding_side = "right"
    X_chunks, P_chunks = [], []
    try:
        for i in range(0, len(prompts), batch_size):
            chunk = prompts[i:i + batch_size]
            enc = tok(chunk, return_tensors="pt", padding=True,
                      add_special_tokens=False).to(device)
            with torch.no_grad():
                out = model(**enc, output_hidden_states=True)
            hs = _stacked_sites(out.hidden_states, sites)          # [n_sites, B, T, d]
            attn = enc["attention_mask"]
            positions = positions_4(tok, chunk)
            for b, (q_idx, p_idx) in enumerate(positions):
                hs_b = _to_numpy(hs[:, b, :, :]).astype(np.float32)  # [n_sites, T, d]
                sel = hs_b[:, [q_idx, p_idx], :].astype(np.float16)  # [n_sites, 2, d]
                X_chunks.append(sel)
                mask_b = _to_numpy(attn[b]).astype(np.float32)       # [T]
                valid = float(mask_b.sum())
                pooled = (hs_b * mask_b[:, None]).sum(axis=1) / valid  # [n_sites, d]
                P_chunks.append(pooled.astype(np.float16))
    finally:
        tok.padding_side = old_side
    X = np.stack(X_chunks).astype(np.float16)   # [n, n_sites, 2, d]
    P = np.stack(P_chunks).astype(np.float16)   # [n, n_sites, d]
    return {"X": X, "P": P}


# ---------------------------------------------------------- set tables

def set_tables_4(X, k: int = metric_4.K_4) -> np.ndarray:
    """`metric_4.knn_sets` per (site, position) on `X[:, s, p, :]`.
    `X`: `[n, n_sites, 2, d]` -> `uint16 [n_sites, 2, n, k]`."""
    X = np.asarray(X)
    n, n_sites, n_pos, d = X.shape
    out = np.zeros((n_sites, n_pos, n, k), dtype=np.uint16)
    for s in range(n_sites):
        for p in range(n_pos):
            out[s, p] = metric_4.knn_sets(X[:, s, p, :].astype(np.float32), k=k)
    return out


def pooled_sets_4(P, k: int = metric_4.K_4) -> np.ndarray:
    """`P`: `[n, n_sites, d]` -> `uint16 [n_sites, n, k]`."""
    P = np.asarray(P)
    n, n_sites, d = P.shape
    out = np.zeros((n_sites, n, k), dtype=np.uint16)
    for s in range(n_sites):
        out[s] = metric_4.knn_sets(P[:, s, :].astype(np.float32), k=k)
    return out


def global_sets_4(X_by_rung: dict, k: int = metric_4.K_4):
    """The bank of every rung's position-1 (prompt-end) rows, in
    `battery_4.RUNGS` order. Returns `(uint16 [n_sites, total, k],
    order)` where `order[i] == (rung, item_index)` for bank row i."""
    order = []
    rows = []
    n_sites = None
    for rung in battery_4.RUNGS:
        if rung not in X_by_rung:
            continue
        X = np.asarray(X_by_rung[rung])
        n, n_s, n_pos, d = X.shape
        if n_sites is None:
            n_sites = n_s
        elif n_s != n_sites:
            raise ValueError(f"global_sets_4: {rung} has {n_s} sites, expected {n_sites}")
        rows.append(X[:, :, 1, :])
        order.extend((rung, i) for i in range(n))
    if not rows:
        raise ValueError("global_sets_4: X_by_rung is empty")
    bank = np.concatenate(rows, axis=0).astype(np.float32)   # [total, n_sites, d]
    total = bank.shape[0]
    out = np.zeros((n_sites, total, k), dtype=np.uint16)
    for s in range(n_sites):
        out[s] = metric_4.knn_sets(bank[:, s, :], k=k)
    return out, order


# -------------------------------------------------------------- overlap

def overlap_table_4(sets_m, sets_q, pairing) -> np.ndarray:
    """`sets_m`: `[n_sites, n, k]`, `sets_q`: `[n_sites_q, n, k]`,
    `pairing[i]` = the q-site paired with m-site i (length `n_sites`).
    Returns `uint8 [n_sites, n]`."""
    sets_m = np.asarray(sets_m)
    sets_q = np.asarray(sets_q)
    n_sites = sets_m.shape[0]
    if len(pairing) != n_sites:
        raise ValueError(f"overlap_table_4: pairing length {len(pairing)} != n_sites {n_sites}")
    n = sets_m.shape[1]
    out = np.zeros((n_sites, n), dtype=np.uint8)
    for i, j in enumerate(pairing):
        out[i] = metric_4.overlap_counts(sets_m[i], sets_q[j])
    return out


# ------------------------------------------------------------ alignment

def _max_over_pairs(sets_m_all, sites_m, sets_q_all, sites_q, k: int):
    """Huh et al.'s reading (design §5 S5(a)): the maximum, over the
    FULL cross product of M's sites and Q's sites (not the fixed
    depth-matched pairing), of the per-pair mutual-k-NN mean over
    items. Returns `(max_mean, [layer_m, layer_q])` — the winning
    pair's HIDDEN-STATE LAYER INDICES (not array positions)."""
    sets_m_all = np.asarray(sets_m_all)
    sets_q_all = np.asarray(sets_q_all)
    n_sites_m, n_sites_q = sets_m_all.shape[0], sets_q_all.shape[0]
    best, best_pair = -1.0, None
    for i in range(n_sites_m):
        for j in range(n_sites_q):
            mean = float(metric_4.overlap_counts(sets_m_all[i], sets_q_all[j]).mean()) / k
            if mean > best:
                best, best_pair = mean, [int(sites_m[i]), int(sites_q[j])]
    return best, best_pair


def align_scalars_4(sets_m_pos: dict, sets_m_pooled, X_m, refs: dict, pairing_by_ref: dict,
                    k: int = metric_4.K_4, *, sites_m=None) -> dict:
    """Per reference: `knn_prompt_end`/`knn_question_end`/`knn_pooled`
    (per-site mean overlap fraction under the fixed depth-matched
    pairing, `None` when the reference side is unavailable);
    `knn_max_over_pairs_{prompt_end,pooled}` + `knn_argmax_pair_
    {prompt_end,pooled}` — Huh's full-cross-product maximum (design §5
    S5(a); `_max_over_pairs`, independent of `pairing_by_ref`'s
    depth-matched pairing), `None` when `sites_m` or the reference's
    `sites_q` is not given; and `cka_prompt_end` (per site, `None`
    unless `refs[ref]["activations_prompt_end"]` is given —
    resolution 7)."""
    out = {}
    for ref, data in refs.items():
        pairing = pairing_by_ref[ref]
        sites_q = data.get("sites_q")
        entry = {}

        ov_pe = overlap_table_4(sets_m_pos["prompt_end"], data["sets_prompt_end"], pairing)
        entry["knn_prompt_end"] = (ov_pe.astype(np.float64) / k).mean(axis=1).tolist()
        if sites_m is not None and sites_q is not None:
            mx, arg = _max_over_pairs(sets_m_pos["prompt_end"], sites_m, data["sets_prompt_end"],
                                      sites_q, k)
            entry["knn_max_over_pairs_prompt_end"] = mx
            entry["knn_argmax_pair_prompt_end"] = arg
        else:
            entry["knn_max_over_pairs_prompt_end"] = None
            entry["knn_argmax_pair_prompt_end"] = None

        qe = data.get("sets_question_end")
        if qe is not None:
            ov_qe = overlap_table_4(sets_m_pos["question_end"], qe, pairing)
            entry["knn_question_end"] = (ov_qe.astype(np.float64) / k).mean(axis=1).tolist()
        else:
            entry["knn_question_end"] = None

        pooled = data.get("sets_pooled")
        if pooled is not None and sets_m_pooled is not None:
            ov_p = overlap_table_4(sets_m_pooled, pooled, pairing)
            entry["knn_pooled"] = (ov_p.astype(np.float64) / k).mean(axis=1).tolist()
            if sites_m is not None and sites_q is not None:
                mx, arg = _max_over_pairs(sets_m_pooled, sites_m, pooled, sites_q, k)
                entry["knn_max_over_pairs_pooled"] = mx
                entry["knn_argmax_pair_pooled"] = arg
            else:
                entry["knn_max_over_pairs_pooled"] = None
                entry["knn_argmax_pair_pooled"] = None
        else:
            entry["knn_pooled"] = None
            entry["knn_max_over_pairs_pooled"] = None
            entry["knn_argmax_pair_pooled"] = None

        act = data.get("activations_prompt_end")
        if act is not None and X_m is not None:
            cka = []
            for i, j in enumerate(pairing):
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", category=RuntimeWarning)
                        cka.append(metric_4.linear_cka_unbiased(
                            np.asarray(X_m[:, i, :], dtype=np.float64),
                            np.asarray(act[:, j, :], dtype=np.float64)))
                except ValueError:
                    # A degenerate kernel is a real, expected event at
                    # the embedding-layer site (site 0 is always in
                    # `sites_4`'s family): every rendered prompt ends
                    # with the identical "\nA:" cue, so the prompt-end
                    # TOKEN is the same across every item in a rung,
                    # making its layer-0 embedding row constant and
                    # its Gram matrix's HSIC(K, K) exactly zero — not
                    # a fixture artifact, a property of the site.
                    # `cka_prompt_end` is a per-site sensitivity (§3.2);
                    # one degenerate site does not void the others.
                    cka.append(None)
            entry["cka_prompt_end"] = cka
        else:
            entry["cka_prompt_end"] = None

        out[ref] = entry
    return out


# ------------------------------------------------------------- storage

def reference_halt_marker_path(root) -> Path:
    """`battery_4.py` has no reference-stage-wide halt marker helper
    (only `halt_marker_path(root, traj)`, the per-trajectory sweep
    one) — added here per Task 3 resolution 4 rather than editing the
    frozen battery module for a path it doesn't define."""
    return Path(root) / "results" / "reference" / "HALTED"


def _sets_p(d: Path, rung: str) -> Path:
    return d / "sets" / f"{rung}.npz"


def _attested_p(d: Path, rung: str) -> Path:
    return d / "attested" / f"{rung}.npz"


def _activations_p(d: Path, rung: str) -> Path:
    return d / "activations" / f"{rung}.npz"


def _global_p(d: Path) -> Path:
    return d / "global.npz"


def _align_p(d: Path) -> Path:
    return d / "align.json"


def _load_p(d: Path) -> Path:
    return d / "_load.json"


def write_load_4(root, key_or_unit, *, record_fields, sets_by_rung, overlaps_by_rung,
                 attested_by_rung, activations_by_rung, global_sets, align,
                 keep_activations) -> dict:
    """Writes every artifact of one load, re-reading `sets/<rung>.npz`,
    `attested/<rung>.npz`, `activations/<rung>.npz` (when written) and
    `global.npz` (when given) and asserting byte-for-byte array
    equality against the in-memory arrays BEFORE returning (resolution
    6); activations are deleted only after that assertion, and their
    now-empty directory is removed too when nothing was kept."""
    d = battery_4.key_dir_4(root, key_or_unit)
    sets_sha, attested_sha, activation_sha = {}, {}, {}

    for rung in battery_4.RUNGS:
        sp = _sets_p(d, rung)
        sp.parent.mkdir(parents=True, exist_ok=True)
        arrays = {"sets": np.asarray(sets_by_rung[rung])}
        ov = (overlaps_by_rung or {}).get(rung) or {}
        for ref, arr in ov.items():
            arrays[f"overlap_{ref}"] = np.asarray(arr)
        np.savez_compressed(sp, **arrays)
        with np.load(sp) as z:
            if not np.array_equal(z["sets"], arrays["sets"]):
                raise ValueError(f"write_load_4: {sp} sets re-read mismatch")
            for name, arr in arrays.items():
                if name == "sets":
                    continue
                if not np.array_equal(z[name], arr):
                    raise ValueError(f"write_load_4: {sp} {name} re-read mismatch")
        sets_sha[rung] = bg.sha256_file(sp)

        at = (attested_by_rung or {}).get(rung) or {}
        ap = _attested_p(d, rung)
        ap.parent.mkdir(parents=True, exist_ok=True)
        arrays_a = {}
        if at.get("question_end") is not None:
            arrays_a["question_end"] = np.asarray(at["question_end"])
        if at.get("pooled") is not None:
            arrays_a["pooled"] = np.asarray(at["pooled"])
        np.savez_compressed(ap, **arrays_a)
        with np.load(ap) as z:
            for name, arr in arrays_a.items():
                if not np.array_equal(z[name], arr):
                    raise ValueError(f"write_load_4: {ap} {name} re-read mismatch")
        attested_sha[rung] = bg.sha256_file(ap)

        act = (activations_by_rung or {}).get(rung)
        if act is not None:
            acp = _activations_p(d, rung)
            acp.parent.mkdir(parents=True, exist_ok=True)
            X_arr, P_arr = np.asarray(act["X"]), np.asarray(act["P"])
            np.savez_compressed(acp, X=X_arr, P=P_arr)
            with np.load(acp) as z:
                if not np.array_equal(z["X"], X_arr) or not np.array_equal(z["P"], P_arr):
                    raise ValueError(f"write_load_4: {acp} re-read mismatch")
            activation_sha[rung] = bg.sha256_file(acp)
            if not keep_activations:
                acp.unlink()
        else:
            activation_sha[rung] = None

    if not keep_activations:
        act_dir = d / "activations"
        if act_dir.is_dir():
            try:
                act_dir.rmdir()
            except OSError:
                pass

    global_sha = None
    if global_sets is not None:
        arr, order = global_sets
        arr = np.asarray(arr)
        order_arr = np.array([f"{r}:{i}" for r, i in order])
        gp = _global_p(d)
        gp.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(gp, sets=arr, order=order_arr)
        with np.load(gp) as z:
            if not np.array_equal(z["sets"], arr) or not np.array_equal(z["order"], order_arr):
                raise ValueError(f"write_load_4: {gp} re-read mismatch")
        global_sha = bg.sha256_file(gp)

    ap = _align_p(d)
    ap.parent.mkdir(parents=True, exist_ok=True)
    ap.write_text(json.dumps(align, indent=1))

    rec = battery_4.load_record_4(key=key_or_unit, sets_sha=sets_sha, global_sha=global_sha,
                                  attested_sha=attested_sha, activation_sha=activation_sha,
                                  **record_fields)
    _load_p(d).parent.mkdir(parents=True, exist_ok=True)
    _load_p(d).write_text(json.dumps(rec, indent=1))
    return rec


def ref_activation_paths_4(root, refs) -> dict:
    """`{ref: {rung: path to that reference's activations/<rung>.npz}}`
    for every `ref` in `refs` — the `ref_activation_paths` argument
    every real `process_model_4` caller threads through so CKA (§3.2)
    actually runs against the references' kept activations, not just
    inside `cross_reference_4`. `ref` is always a reference-stage str
    key, so `battery_4.activations_path` (which resolves through
    `reference_dir`) applies directly. A path is handed over whether
    or not the file currently exists on disk — `process_model_4`/
    `align_scalars_4` check `.is_file()` themselves and degrade to
    `None` for that reference/rung when it doesn't (e.g. a first unit,
    where `keep_activations=False` — never a reference, though: every
    reference is `keep_activations=True`)."""
    return {ref: {rung: battery_4.activations_path(root, ref, rung) for rung in battery_4.RUNGS}
           for ref in (refs or ())}


def load_ref_tables_4(root, ref_keys) -> dict:
    """Per reference key: the committed prompt-end `sets` (sha-checked
    against `_load.json`'s `sets_sha256`, refusing on drift), plus
    `sets_question_end`/`sets_pooled` read from `attested/<rung>.npz`
    when that (gitignored) file is present, `sites`/`n_hidden`/`record`
    from `_load.json`."""
    out = {}
    for ref in ref_keys:
        d = battery_4.reference_dir(root, ref)
        rec = json.loads((d / "_load.json").read_text())
        sets_sha = rec.get("sets_sha256") or {}
        sets_pe, sets_qe, sets_pool = {}, {}, {}
        for rung in battery_4.RUNGS:
            sp = _sets_p(d, rung)
            got = bg.sha256_file(sp)
            want = sets_sha.get(rung)
            if want is not None and got != want:
                raise ValueError(f"load_ref_tables_4: {sp} sha256 {got} != recorded {want}")
            with np.load(sp) as z:
                sets_pe[rung] = z["sets"]
            ap = _attested_p(d, rung)
            if ap.is_file():
                with np.load(ap) as z:
                    if "question_end" in z.files:
                        sets_qe[rung] = z["question_end"]
                    if "pooled" in z.files:
                        sets_pool[rung] = z["pooled"]
        out[ref] = {"sets": sets_pe, "sets_question_end": sets_qe, "sets_pooled": sets_pool,
                    "sites": list(rec.get("sites") or []), "n_hidden": rec.get("n_hidden"),
                    "record": rec}
    return out


def _pairing_positions(sites_m, n_hidden_m, sites_q, n_hidden_q) -> list:
    """`metric_4.depth_pairs` returns, per m-site, the paired q-site as
    a hidden-state LAYER INDEX (an element of `sites_q`), not its
    position within that list — but `overlap_table_4`/the stored set
    tables are indexed by POSITION (array dim 0 is site order, not
    layer number). Converts."""
    layers = metric_4.depth_pairs(sites_m, n_hidden_m, sites_q, n_hidden_q)
    sites_q = list(sites_q)
    return [sites_q.index(l) for l in layers]


def family_of_traj_4(traj: str) -> str:
    """The model family of a raw trajectory name (`"pythia_2.8b"` etc,
    as used by a sweep `(traj, step)` unit and the reference stage's
    first-grid-point units) — read off `FAMILY_OF_KEY_4`'s
    `endpoint_<traj>` entry rather than duplicating that mapping, since
    every trajectory point shares its endpoint's family by
    construction."""
    return battery_4.FAMILY_OF_KEY_4[f"endpoint_{traj}"]


def non_pythia_refs_4() -> tuple:
    """The three references the Pythia ladder aligns against (design
    §3.7 stage (5)) — `REFS_FOR_4` is keyed by trajectory name, not by
    ladder size, so the ladder's own reference set is derived here."""
    return tuple(r for r in battery_4.REFERENCES_4 if battery_4.FAMILY_OF_KEY_4[r] != "pythia")


def _load_activations_prompt_end(root, key_or_unit, rung):
    d = battery_4.key_dir_4(root, key_or_unit)
    p = _activations_p(d, rung)
    if not p.is_file():
        return None
    with np.load(p) as z:
        return np.asarray(z["X"])[:, :, 1, :].astype(np.float32)


# --------------------------------------------------------- orchestration

def process_model_4(model, tok, *, key_or_unit, family, info, root, battery, ref_tables,
                    ref_activation_paths, batch_size, device, keep_activations, sites, refs,
                    committed_digest, stack, git_sha) -> dict:
    """The whole per-load pipeline over all 34 rungs: collect, build
    the model's own set/pooled tables, align against every reference in
    `refs` (using `ref_tables`, plus `ref_activation_paths[ref][rung]`
    — a path to that reference's `activations/<rung>.npz` — for CKA
    when given and present on disk), write everything, and (only for a
    reference-stage str key — a sweep `(traj, step)` unit never gets
    one, matching `reference_seal_paths_4`) the global bank."""
    t0 = time.time()
    n_hidden = info["n_hidden"]
    key_for_batch = key_or_unit[0] if isinstance(key_or_unit, (tuple, list)) else key_or_unit
    is_reference_stage_key = isinstance(key_or_unit, str)

    pairing_by_ref = {}
    for ref in (refs or ()):
        rt = ref_tables[ref]
        pairing_by_ref[ref] = _pairing_positions(sites, n_hidden, rt["sites"], rt["n_hidden"])

    sets_by_rung, overlaps_by_rung, attested_by_rung, activations_by_rung = {}, {}, {}, {}
    align_by_rung = {}
    X_by_rung = {} if is_reference_stage_key else None
    X, d_hidden = None, None

    for rung in battery_4.RUNGS:
        cap = battery[rung]
        collected = collect_rung_4(model, tok, family, cap, sites=sites, batch_size=batch_size,
                                   device=device, key=key_for_batch)
        X, P = collected["X"], collected["P"]
        d_hidden = X.shape[-1]
        sets = set_tables_4(X, k=metric_4.K_4)          # [n_sites, 2, n, k]
        pooled = pooled_sets_4(P, k=metric_4.K_4)        # [n_sites, n, k]

        sets_by_rung[rung] = sets[:, 1, :, :]
        attested_by_rung[rung] = {"question_end": sets[:, 0, :, :], "pooled": pooled}
        activations_by_rung[rung] = {"X": X, "P": P}

        if refs:
            sets_m_pos = {"question_end": sets[:, 0, :, :], "prompt_end": sets[:, 1, :, :]}
            ref_data, ov = {}, {}
            for ref in refs:
                rt = ref_tables[ref]
                act = None
                if ref_activation_paths and ref_activation_paths.get(ref):
                    p = ref_activation_paths[ref].get(rung)
                    if p is not None and Path(p).is_file():
                        with np.load(p) as z:
                            act = np.asarray(z["X"])[:, :, 1, :].astype(np.float32)
                ref_data[ref] = {"sets_prompt_end": rt["sets"][rung],
                                 "sets_question_end": rt.get("sets_question_end", {}).get(rung),
                                 "sets_pooled": rt.get("sets_pooled", {}).get(rung),
                                 "activations_prompt_end": act, "sites_q": rt["sites"]}
                ov[ref] = overlap_table_4(sets[:, 1, :, :], rt["sets"][rung], pairing_by_ref[ref])
            X_m = X[:, :, 1, :].astype(np.float32)
            align_by_rung[rung] = align_scalars_4(sets_m_pos, pooled, X_m, ref_data,
                                                  pairing_by_ref, k=metric_4.K_4, sites_m=sites)
            overlaps_by_rung[rung] = ov
        else:
            align_by_rung[rung] = {}

        if X_by_rung is not None:
            X_by_rung[rung] = X

    global_sets = global_sets_4(X_by_rung, k=metric_4.K_4) if X_by_rung is not None else None

    record_fields = dict(family=family, info=info, sites=list(sites), d=int(d_hidden),
                         render=battery_4.RENDER_4[family], batch_size=int(batch_size),
                         refs=list(refs or ()), pairing={r: list(p) for r, p in pairing_by_ref.items()},
                         committed_digest=committed_digest, seconds=time.time() - t0,
                         stack=dict(stack), git_sha=git_sha, prereg_tag=battery_4.PREREG_TAG_4)
    return write_load_4(root, key_or_unit, record_fields=record_fields, sets_by_rung=sets_by_rung,
                        overlaps_by_rung=overlaps_by_rung, attested_by_rung=attested_by_rung,
                        activations_by_rung=activations_by_rung, global_sets=global_sets,
                        align=align_by_rung, keep_activations=keep_activations)


def cross_reference_4(root) -> dict:
    """No model contact: recomputes every reference's `align.json`
    against the other three, from each reference's own stored sets/
    attested/activations files — the ceiling (design §3.7 gate 0's
    partner: what the released lenses agree with each other about)."""
    ref_tables = load_ref_tables_4(root, battery_4.REFERENCES_4)
    out = {}
    for ref in battery_4.REFERENCES_4:
        others = [r for r in battery_4.REFERENCES_4 if r != ref]
        rt = ref_tables[ref]
        sites, n_hidden = rt["sites"], rt["n_hidden"]
        pairing_by_ref = {o: _pairing_positions(sites, n_hidden, ref_tables[o]["sites"],
                                                 ref_tables[o]["n_hidden"])
                          for o in others}
        align_by_rung = {}
        for rung in battery_4.RUNGS:
            sets_m_pos = {"question_end": rt["sets_question_end"].get(rung),
                          "prompt_end": rt["sets"][rung]}
            pooled_m = rt["sets_pooled"].get(rung)
            X_m = _load_activations_prompt_end(root, ref, rung)
            ref_data = {}
            for o in others:
                oth = ref_tables[o]
                ref_data[o] = {"sets_prompt_end": oth["sets"][rung],
                               "sets_question_end": oth["sets_question_end"].get(rung),
                               "sets_pooled": oth["sets_pooled"].get(rung),
                               "activations_prompt_end": _load_activations_prompt_end(root, o, rung),
                               "sites_q": oth["sites"]}
            align_by_rung[rung] = align_scalars_4(sets_m_pos, pooled_m, X_m, ref_data,
                                                  pairing_by_ref, k=metric_4.K_4, sites_m=sites)
        d = battery_4.reference_dir(root, ref)
        _align_p(d).write_text(json.dumps(align_by_rung, indent=1))
        out[ref] = align_by_rung
    return out


# ----------------------------------------------------------- loaders

def real_loaders_4() -> dict:
    """MODEL CONTACT — never executed by a test. `battery_4`'s own
    dispatchers plus 2i's `release`, the exact `loaders` shape every
    exp4 runner takes."""
    return {"key": battery_4.load_key_4, "step": battery_4.load_step_4,
            "free_step": battery_4.free_step_4, "release": _release}
