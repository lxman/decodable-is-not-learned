# experiments/exp4c/collect_4c.py
"""Experiment 4c's per-load wrapper (design `experiment-4c-design.md`
Task 3 brief step 3): `experiments/exp4/collect_4.py`'s
`process_model_4` (lines 623-742) reused with exactly the deltas the
brief names:

(i) the batch pin is `battery_4c.BATCH_4C`, not `battery_4.BATCH_4`
(the frozen table does not know 4c's keys — `pythia_6.9b`,
`olmo2_13b`, `endpoint_olmo2_13b`), checked here BEFORE the per-rung
loop; `collect_4.collect_rung_4` is always called with `key=None` so
it never re-checks against the wrong table.

(ii) no CKA: `ref_activation_paths` is dropped entirely (this module
never reads an `activations/<rung>.npz` off a reference), so the
`activations_prompt_end` a candidate offers a reference is always
`None` — `cka_prompt_end` comes back `None` on every call.

(iii) no global bank, ever: neither a sweep unit nor the 13B thin
endpoint (`battery_4c.THIN_ENDPOINT_KEY_4C`, a str key that would read
as "reference-stage" under exp4's own `is_reference_stage_key` test)
gets one — `X_by_rung` is never built and `write_load_4` always gets
`global_sets=None`.

(iv) `render`/`prereg_tag` come from `battery_4c.RENDER_4C`/
`battery_4c.PREREG_TAG_4C`, not exp4's own tables.

(v) `keep_activations=False` is hard-coded at the one `write_load_4`
call (not a caller-supplied argument — 4c never keeps an activations
file). The activation shas are still computed inside `write_load_4`
before the files are deleted, so `rec["activation_sha256"]` is never
empty even though nothing survives on disk.

Everything else — the `model_box` one-element-list contract
(ratification open item 1: the box is emptied by `.pop()` before the
first forward pass, so the runner's own reference is gone and only
this frame names the weights until `release_model()` runs), the
`release_model()` placement right after the last forward pass, and
`stack_record_4`'s numpy-version stamping — is unchanged from exp4's
own `process_model_4`.

Zero model contact, zero network: this module only ever receives an
already-loaded model through `model_box`."""
from __future__ import annotations

import sys
import json
import time

import numpy as np
from pathlib import Path

EXP4C = Path(__file__).resolve().parent
EXPERIMENTS = EXP4C.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp4 import _threads_4  # noqa: F401,E402 (thread pin, before numpy)
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402
from experiments.exp4c import battery_4c  # noqa: E402

_release = collect_4._release


def stamp_dtypes_4c(root, key_or_unit, rec, *, forward_dtype, x_dtype, load_dtype) -> dict:
    """AMENDMENT 2026-09-20: `battery_4.load_record_4` (frozen, Exp 4)
    copies a fixed key set, so the three MEASURED dtype fields are
    stamped onto the record AFTER `collect_4.write_load_4` returns and
    the record is written back in the writer's own format
    (`json.dumps(rec, indent=1)` to `_load.json`). Every 4c record
    carries them; `battery_4c.load_record_failures_4c` requires them."""
    rec = dict(rec)
    rec["forward_dtype"] = forward_dtype
    rec["x_dtype"] = x_dtype
    rec["load_dtype"] = load_dtype
    d = battery_4.key_dir_4(root, key_or_unit)
    (d / "_load.json").write_text(json.dumps(rec, indent=1))
    return rec


def _to_f32_numpy_4c(x):
    """`collect_4._to_numpy` with one step first: a bfloat16 tensor is
    upcast to float32 ON THE TENSOR SIDE (numpy has no bfloat16 — the
    rehearsal of 2026-09-20 crashed exactly there). Any other input goes
    through the frozen helper unchanged, then to float32."""
    if str(getattr(x, "dtype", "")) == "torch.bfloat16":
        x = x.float()
    return collect_4._to_numpy(x).astype(np.float32)


def collect_rung_4c_fp32(model, tok, family, cap, *, sites, batch_size, device) -> dict:
    """AMENDMENT 2026-09-20: `collect_4.collect_rung_4`'s body with the
    fp16 storage casts removed — `X`/`P` returned in float32. Used only
    for keys whose `battery_4c.X_DTYPE_4C` is float32 (the bf16-forward
    OLMo-2 13B path): the fp16 forward overflowed on these checkpoints,
    so fp16 storage of the same activations would too. Same prompts,
    padding side, `add_special_tokens=False`, site selection before
    `.cpu()`, mask-weighted pooling — `test_collect_rung_4c_fp32_equals_
    the_frozen_collector_after_an_fp16_cast` proves the equality."""
    import torch

    prompts = collect_4.render_prompts_4(family, cap)
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
            hs = collect_4._stacked_sites(out.hidden_states, sites)          # [n_sites, B, T, d]
            attn = enc["attention_mask"]
            positions = collect_4.positions_4(tok, chunk)
            for b, (q_idx, p_idx) in enumerate(positions):
                hs_b = _to_f32_numpy_4c(hs[:, b, :, :])                        # [n_sites, T, d] fp32
                X_chunks.append(hs_b[:, [q_idx, p_idx], :])                    # [n_sites, 2, d] fp32
                mask_b = collect_4._to_numpy(attn[b]).astype(np.float32)       # [T]
                valid = float(mask_b.sum())
                P_chunks.append((hs_b * mask_b[:, None]).sum(axis=1) / valid)   # [n_sites, d] fp32
    finally:
        tok.padding_side = old_side
    X = np.stack(X_chunks).astype(np.float32)   # [n, n_sites, 2, d]
    P = np.stack(P_chunks).astype(np.float32)   # [n, n_sites, d]
    return {"X": X, "P": P}


def collect_rung_for_4c(model, tok, family, cap, *, key, sites, batch_size, device) -> dict:
    """The one collector entry for a 4c key: `battery_4c.X_DTYPE_4C[key]`
    float16 -> the FROZEN `collect_4.collect_rung_4` itself (`key=None`,
    4c's batch pin is checked by `process_model_4c`); float32 -> this
    module's `collect_rung_4c_fp32`. The returned `X` dtype is asserted
    against the pin."""
    k = battery_4c.dtype_key_4c(key)
    want = battery_4c.X_DTYPE_4C[k]
    if want == "float16":
        out = collect_4.collect_rung_4(model, tok, family, cap, sites=sites,
                                       batch_size=batch_size, device=device, key=None)
    elif want == "float32":
        out = collect_rung_4c_fp32(model, tok, family, cap, sites=sites,
                                   batch_size=batch_size, device=device)
    else:  # pragma: no cover - the pin table holds only these two
        raise ValueError(f"{k}: X dtype pin {want!r}")
    if str(out["X"].dtype) != want:
        raise ValueError(f"{k}: collected X dtype {out['X'].dtype} != the pinned {want!r}")
    return out


def process_model_4c(model_box, tok, *, key_or_unit, family, info, root, battery, ref_tables,
                     batch_size, device, sites, refs, committed_digest, stack, git_sha,
                     release_model=None) -> dict:
    """The whole per-load pipeline over all 34 rungs, `collect_4.
    process_model_4`'s body with this module's docstring's deltas
    (i)-(v). `key_or_unit` is a `(traj, step)` pair (a sweep unit,
    `step` including `battery_4c.INIT_STEP_4C`) or
    `battery_4c.THIN_ENDPOINT_KEY_4C` (the 13B thin endpoint, a str
    key — but still never gets a global bank, unlike an exp4 reference-
    stage str key)."""
    if not isinstance(model_box, list) or len(model_box) != 1:
        raise TypeError("process_model_4c: model_box must be a one-element list holding the "
                        "model (ratification open item 1), not the model itself")
    model = model_box.pop()
    t0 = time.time()
    n_hidden = info["n_hidden"]
    key_for_batch = key_or_unit[0] if isinstance(key_or_unit, (tuple, list)) else key_or_unit

    want_batch = battery_4c.BATCH_4C[key_for_batch]
    if int(batch_size) != int(want_batch):
        raise ValueError(f"process_model_4c: batch_size {batch_size} != the pinned "
                         f"{want_batch} for {key_for_batch!r}")
    # amendment 2026-09-20: the loader's MEASURED forward dtype must be the
    # pinned one before a single forward pass — a unit run under the wrong
    # dtype is refused here, never written.
    want_fwd = battery_4c.FORWARD_DTYPE_4C[battery_4c.dtype_key_4c(key_for_batch)]
    got_fwd = info.get("forward_dtype")
    if got_fwd != want_fwd:
        raise ValueError(f"process_model_4c: {key_for_batch!r} info forward_dtype {got_fwd!r} != "
                         f"the pinned {want_fwd!r}")
    x_dtype_seen = None

    pairing_by_ref = {}
    for ref in (refs or ()):
        rt = ref_tables[ref]
        pairing_by_ref[ref] = collect_4._pairing_positions(sites, n_hidden, rt["sites"],
                                                            rt["n_hidden"])

    sets_by_rung, overlaps_by_rung, attested_by_rung, activations_by_rung = {}, {}, {}, {}
    align_by_rung = {}
    d_hidden = None

    for rung in battery_4.RUNGS:
        cap = battery[rung]
        collected = collect_rung_for_4c(model, tok, family, cap, key=key_for_batch, sites=sites,
                                        batch_size=batch_size, device=device)
        X, P = collected["X"], collected["P"]
        d_hidden = X.shape[-1]
        x_dtype_seen = str(X.dtype)                                 # measured, not the pin
        sets = collect_4.set_tables_4(X, k=metric_4.K_4)          # [n_sites, 2, n, k]
        pooled = collect_4.pooled_sets_4(P, k=metric_4.K_4)        # [n_sites, n, k]

        sets_by_rung[rung] = sets[:, 1, :, :]
        attested_by_rung[rung] = {"question_end": sets[:, 0, :, :], "pooled": pooled}
        activations_by_rung[rung] = {"X": X, "P": P}

        if refs:
            sets_m_pos = {"question_end": sets[:, 0, :, :], "prompt_end": sets[:, 1, :, :]}
            ref_data, ov = {}, {}
            for ref in refs:
                rt = ref_tables[ref]
                ref_data[ref] = {"sets_prompt_end": rt["sets"][rung],
                                 "sets_question_end": rt.get("sets_question_end", {}).get(rung),
                                 "sets_pooled": rt.get("sets_pooled", {}).get(rung),
                                 # (ii): no CKA — a reference never offers activations here.
                                 "activations_prompt_end": None, "sites_q": rt["sites"]}
                ov[ref] = collect_4.overlap_table_4(sets[:, 1, :, :], rt["sets"][rung],
                                                    pairing_by_ref[ref])
            align_by_rung[rung] = collect_4.align_scalars_4(
                sets_m_pos, pooled, None, ref_data, pairing_by_ref, k=metric_4.K_4, sites_m=sites)
            overlaps_by_rung[rung] = ov
        else:
            align_by_rung[rung] = {}

    # The last forward pass has happened. Unlike exp4's own
    # `process_model_4`, there is no global bank to wait for (iii) —
    # everything left is the write, host-side numpy already. The
    # weights go now.
    model = None
    del model
    if release_model is not None:
        release_model()

    record_fields = dict(family=family, info=info, sites=list(sites), d=int(d_hidden),
                         render=battery_4c.RENDER_4C[family], batch_size=int(batch_size),
                         refs=list(refs or ()),
                         pairing={r: list(p) for r, p in pairing_by_ref.items()},
                         committed_digest=committed_digest, seconds=time.time() - t0,
                         stack=collect_4.stack_record_4(stack), git_sha=git_sha,
                         threads_pinned=_threads_4.threads_pinned_4(),
                         prereg_tag=battery_4c.PREREG_TAG_4C)
    rec = collect_4.write_load_4(root, key_or_unit, record_fields=record_fields,
                                 sets_by_rung=sets_by_rung, overlaps_by_rung=overlaps_by_rung,
                                 attested_by_rung=attested_by_rung,
                                 activations_by_rung=activations_by_rung, global_sets=None,
                                 align=align_by_rung, keep_activations=False)
    return stamp_dtypes_4c(root, key_or_unit, rec, forward_dtype=got_fwd, x_dtype=x_dtype_seen,
                           load_dtype=info.get("load_dtype"))


def real_loaders_4c() -> dict:
    """MODEL CONTACT — never executed by a test."""
    return {"step": battery_4c.load_step_4c, "thin": battery_4c.load_thin_endpoint_4c,
            "free_step": battery_4c.free_step_4c, "release": _release}
