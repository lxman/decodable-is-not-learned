"""Synthetic full-shape Exp 5b trees in the PRODUCTION layout (plan B-11):
an Experiment 5 world (`full_shape_5.write_world_5`) with its verdict
written by `analyze_5.run(write=True)`, the 5b power record ONCE from
that world's cells, a projection stub, then the 5b runner with fake
loaders into a SEPARATE root. The Experiment 5 world's count function
is wrapped so its S11 read mirrors the final (the anneal's flat end),
which makes the 5b re-read of that step byte-identical; two custom
Experiment-5-side modes (SIGN-ONLY, CONCENTRATED) are injected by
monkeypatching `full_shape_5.count_fn_for`/`MODES`."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXP5B = Path(__file__).resolve().parents[1]
if str(EXP5B.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP5B.parent.parent))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp5 import analyze_5 as an5  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import stats_5 as ss  # noqa: E402
from experiments.exp5.tests import fakes_5 as fk  # noqa: E402
from experiments.exp5.tests import full_shape_5 as fs  # noqa: E402
from experiments.exp5b import analyze_5b as an  # noqa: E402
from experiments.exp5b import battery_5b as b5b  # noqa: E402
from experiments.exp5b import power_5b as pw5b  # noqa: E402
from experiments.exp5b.run import units_5b as un  # noqa: E402

WINDOW_W = (31000, 30000, 29000)        # Experiment 5's shrunk S11 step first (fs.apply_shrink: 31000)
# 5b mode → (Experiment 5 world mode, Experiment 5 noise amplitude, small-side wobble amplitude)
MODES_5B = {"SURVIVES": ("LARGE-AHEAD", 6, 6), "INSIDE": ("MATCHED", 6, 6),
            "SIGN-ONLY": ("SIGN-ONLY", 2, 2), "SIZE-ONLY": ("CONCENTRATED", 6, 6),
            "UNDETERMINED": ("UNDETERMINED", 6, 6)}
_THR = {"antonym": 3.0, "antonym6": 3.0, "arith_next": 2.95, "add_base8": 2.9, "sub_base8": 2.9,
        "add3_mid": 2.85, "sub3_mid": 2.85, "odd6": 2.8, "count_div13": 2.8}   # full_shape_5's inner g, verbatim


def _g(loss, rung):
    return int(min(480, max(0, 400 * (_THR[rung] - loss)))) if rung in _THR else 0


def count_fn_5b_world(mode, amp, orig_count_fn_for):
    """The Experiment 5 world's count function: the standard modes through
    `full_shape_5.count_fn_for` (amp threaded), the two custom modes here;
    every mode's S11 read mirrors the final."""
    order = {s: i for i, s in enumerate(fs.SIZES_W)}
    if mode == "SIGN-ONLY":
        def base(size, step, rung):
            off = 2 * order[size] if rung in fs.LIVE_RUNGS_W else 0
            return int(min(500, max(0, _g(fs.loss_w(size, step), rung) + off + fs._noise(size, step, rung, amp))))
    elif mode == "CONCENTRATED":
        def base(size, step, rung):
            off = 40 * order[size] if rung == "antonym" else 0
            return int(min(500, max(0, _g(fs.loss_w(size, step), rung) + off + fs._noise(size, step, rung, amp))))
    else:
        base = orig_count_fn_for(mode, amp)

    def f(size, step, rung):
        return base(size, b5.FINAL_STEP_5 if int(step) == b5.S11_STEP_5 else step, rung)
    return f


def member_count_fn_5b(exp5_count_fn, wobble, reread_delta=None):
    """Box B's count function: the final and the re-read member exactly as
    the Experiment 5 world read them (+ an optional per-rung delta on the
    final, for the tolerance tests); the two NEW members = the final's
    count plus a deterministic wobble."""
    reread_delta = reread_delta or {}

    def f(size, step, rung):
        step = int(step)
        if step == b5.FINAL_STEP_5:
            return int(min(500, max(0, exp5_count_fn(size, step, rung) + reread_delta.get(rung, 0))))
        if step == b5b.WINDOW_STEPS_5B[0]:
            return exp5_count_fn(size, step, rung)
        return int(min(500, max(0, exp5_count_fn(size, b5.FINAL_STEP_5, rung)
                                + fs._noise(size, step, rung, wobble))))
    return f


def apply_shrink_5b(monkeypatch):
    fs.apply_shrink(monkeypatch)
    monkeypatch.setattr(b5b, "WINDOW_STEPS_5B", WINDOW_W)
    monkeypatch.setattr(b5b, "FROZEN_SHA256_5B", {})
    monkeypatch.setattr(b5b, "IMPORTED_SHA256_5B", {})
    monkeypatch.setattr(b5b, "check_imports_5b", lambda: None)
    monkeypatch.setattr(b5b, "EXP5_VERDICT_PIN_5B", None)
    monkeypatch.setattr(pw5b, "N_SIM_5B", 30)


def _inj():
    return dict(tag_exists=lambda t: True,
                blob_sha=lambda t, r: bg.sha256_file(b5b.REPO / r) if (b5b.REPO / r).is_file() else None)


def write_world_5b(root: Path, mode: str, *, monkeypatch, wobble=None, reread_delta=None,
                   loss_delta_final=0.0, halt_on_digest=True, digest_fn_b=None, nonfinite_at=()) -> dict:
    assert mode in MODES_5B
    exp5_mode, amp, w_default = MODES_5B[mode]
    apply_shrink_5b(monkeypatch)
    orig_cf = fs.count_fn_for
    monkeypatch.setattr(fs, "MODES", tuple(fs.MODES) + ("SIGN-ONLY", "CONCENTRATED"))
    monkeypatch.setattr(fs, "count_fn_for", lambda m, amp_=amp: count_fn_5b_world(m, amp_, orig_cf))
    root5, root5b = Path(root) / "exp5", Path(root) / "exp5b"
    w5 = fs.write_world_5(root5, exp5_mode, monkeypatch=monkeypatch)
    inj5 = dict(_inj(), blobs_bound=lambda t, p, **k: [], projection_commit="p1", is_ancestor=lambda a, b: True,
                seal_tag_commit="s1", power_gate="full", manifest=w5["manifest"], sl=w5["sl"],
                referents_sha=False, imports_pinned=False, frozen_check=lambda: None, n_sample=200, n_boot=100)
    v5 = an5.run(root=root5, write=True, **inj5)
    assert v5["failures"] == [], v5["failures"][:3]
    # the S11 mirror must not have touched any window (B-11's safety assertion)
    for c in v5["cells"]:
        assert b5.S11_STEP_5 not in (list(c["bracket"]) + list(c["b_minus_steps"]) + list(c["b_plus_steps"]))
    orig_pre = b5b.require_prereg_5b
    present = tuple(rel for rel in b5b.INSTRUMENT_BLOBS_5B if (b5b.REPO / rel).is_file())
    monkeypatch.setattr(b5b, "require_prereg_5b",
                        lambda *, tag_exists=None, blob_sha=None, blobs=present:
                        orig_pre(tag_exists=tag_exists, blob_sha=blob_sha, blobs=blobs))
    pw5b.main(root5b, exp5_root=root5, verdict_sha=False, **_inj())
    (root5b / "projection.md").write_text("# projection (synthetic)\n")
    exp5_cf = fs.count_fn_for(exp5_mode)
    cf_b = member_count_fn_5b(exp5_cf, w_default if wobble is None else wobble, reread_delta)
    loaders_b, state_b = fk.make_loaders(w5["battery"], loss_fn=lambda s, st: fs.loss_w(s, st)
                                         + (loss_delta_final if int(st) == b5.FINAL_STEP_5 else 0.0),
                                         count_fn=cf_b, digest_fn=digest_fn_b, nonfinite_at=nonfinite_at)
    for size in reversed(b5.SMALL_SIDES_5):
        un.run(size=size, root=root5b, exp5_root=root5, cache_root=root5b, device="cuda", loaders=loaders_b,
               manifest=w5["manifest"], sl=w5["sl"], host_meta=fk.fake_host(), git_sha="g2",
               verdict_sha=False, projection_commit="p2", is_ancestor=lambda a, b: True, power_present=True,
               halt_on_digest=halt_on_digest, **_inj())
    return {"root5": root5, "root5b": root5b, "manifest": w5["manifest"], "sl": w5["sl"],
            "battery": w5["battery"], "inj5": inj5, "v5": v5, "state_b": state_b}


def run_5b(w: dict, **over) -> dict:
    kw = dict(root=w["root5b"], exp5_root=w["root5"], write=False, n_sample=200, n_boot=100,
              manifest=w["manifest"], sl=w["sl"], verdict_sha=False, exp5_kwargs=w["inj5"],
              projection_commit="p2", prereg_commit="t2", is_ancestor=lambda a, b: True,
              referents_sha=False, imports_pinned=False, frozen_check=lambda: None, power_gate="full",
              **_inj())
    kw.update(over)
    return an.run(**kw)
