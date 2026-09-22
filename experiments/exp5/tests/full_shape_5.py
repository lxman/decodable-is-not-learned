"""Synthetic full-shape Exp 5 trees in the PRODUCTION layout: the stage
runners (`finals_5.run`, `sweep_5.run`) driven by fake loaders whose loss
is a smooth per-size curve and whose counts are a mode-controlled
function of the LOSS (so two models at equal loss read equal counts
under MATCHED), plus the power record via `power_5.main` and a projection
stub. Every record is written by the same code the campaign runs."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP5 = Path(__file__).resolve().parents[1]
if str(EXP5.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP5.parent.parent))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import power_5 as pw  # noqa: E402
from experiments.exp5.run import finals_5 as fin  # noqa: E402
from experiments.exp5.run import sweep_5 as sw  # noqa: E402
from experiments.exp5.tests import fakes_5 as fk  # noqa: E402

SIZES_W = ("1b", "1.4b", "2.8b", "6.9b")
AVAIL_W = tuple(range(1000, 33000, 1000)) + (143000,)
# Widened from the design's four-point second spine gap (1000, 4000): at
# (1000, 4000) the 6.9b x 1.4b crossing resolves in exactly ONE bisection
# probe on this loss curve (empirically verified, `experiments/exp5/
# PROGRESS.md` Task 5 entry) — a single-element `bisected` list is not a
# fixture the refusal test can catch a REVERSED-order tamper on. (1000,
# 6000) reliably needs >= 2 probes for every mode while leaving every
# other search/verdict outcome unchanged (checked across all five modes).
SPINE_W = (1000, 6000, 16000, 32000, 143000)
BASE_W = {"1b": 2.8, "1.4b": 2.6, "2.8b": 2.4, "6.9b": 2.2}
LIVE_RUNGS_W = ("antonym", "antonym6", "arith_next", "add_base8", "sub_base8", "add3_mid",
                "sub3_mid", "odd6", "count_div13")
MODES = ("MATCHED", "LARGE-AHEAD", "SMALL-AHEAD", "MIXED", "UNDETERMINED")


def loss_w(size, step):
    return BASE_W[size] + 20.0 / (step ** 0.5)


def _noise(size, step, rung, amp):
    h = int(hashlib.sha256(f"{size}/{step}/{rung}".encode()).hexdigest()[:8], 16)
    return int(round((h / 0xFFFFFFFF - 0.5) * 2 * amp))


def count_fn_for(mode, amp=6):
    order = {s: i for i, s in enumerate(SIZES_W)}

    def g(loss, rung):
        # a rung's count as a function of loss: rises as loss falls below a threshold
        thr = {"antonym": 3.0, "antonym6": 3.0, "arith_next": 2.95, "add_base8": 2.9,
               "sub_base8": 2.9, "add3_mid": 2.85, "sub3_mid": 2.85, "odd6": 2.8, "count_div13": 2.8}
        return int(min(480, max(0, 400 * (thr[rung] - loss)))) if rung in thr else 0

    def f(size, step, rung):
        if mode == "UNDETERMINED" and rung not in ("antonym", "antonym6"):
            return 0
        base = g(loss_w(size, step), rung)
        off = 0
        if mode == "LARGE-AHEAD":
            off = 40 * order[size]
        elif mode == "SMALL-AHEAD":
            # A smaller magnitude than LARGE-AHEAD's/MIXED's: the offset here
            # is SUBTRACTIVE on every read (the small model's own final
            # included, scaled by its own order), so it crushes counts toward
            # zero rather than merely lifting them — at 40 too few cells
            # survive above the floor to clear MIN_LIVE_CELLS_5 (empirically
            # 18, need >= 20). 32 keeps 21 live cells / 7 rungs with a clean
            # all-negative sign and T/p comfortably past the bar (checked
            # across a magnitude sweep, `experiments/exp5/PROGRESS.md`).
            off = -32 * order[size]
        elif mode == "MIXED":
            off = (40 if LIVE_RUNGS_W.index(rung) % 2 == 0 else -40) * order[size] if rung in LIVE_RUNGS_W else 0
        return int(min(500, max(0, base + off + _noise(size, step, rung, amp))))
    return f


def apply_shrink(monkeypatch):
    monkeypatch.setattr(b5, "SIZES_5", SIZES_W)
    monkeypatch.setattr(b5, "PAIRS_5", tuple((s, L) for i, s in enumerate(SIZES_W) for L in SIZES_W[i + 1:]))
    monkeypatch.setattr(b5, "SMALL_SIDES_5", SIZES_W[:-1])
    monkeypatch.setattr(b5, "LARGE_SIDES_5", SIZES_W[1:])
    monkeypatch.setattr(b5, "SPINE_5", SPINE_W)
    monkeypatch.setattr(b5, "GATE1_INTERIOR_5", {})
    monkeypatch.setattr(b5, "GATE1_REFERENT_SOURCE_5", {})
    monkeypatch.setattr(b5, "FROZEN_SHA256_5", {})
    monkeypatch.setattr(b5, "IMPORTED_SHA256_5", {})
    monkeypatch.setattr(b5, "check_imports_5", lambda: None)   # pinned at Task 6; a no-op here
    monkeypatch.setattr(b5, "S11_STEP_5", 31000)
    monkeypatch.setattr(pw, "N_SIM_5", 30)


def write_world_5(root: Path, mode: str, *, monkeypatch) -> dict:
    """Runs the two stages with fakes into `root`; returns the handles the
    analyzer needs injected (manifest, slice, host meta)."""
    assert mode in MODES
    apply_shrink(monkeypatch)
    battery = bt.load_battery()
    man = fk.synthetic_manifest(SIZES_W, AVAIL_W)
    loaders, state = fk.make_loaders(battery, loss_fn=loss_w, count_fn=count_fn_for(mode),
                                     pythia_2c_count_fn=count_fn_for(mode), loss_2c_fn=loss_w)
    sl = fk.small_slice()
    prereg = dict(tag_exists=lambda t: True, blob_sha=lambda t, r: bg.sha256_file(b5.REPO / r))
    common = dict(root=root, cache_root=root, device="cuda", loaders=loaders, manifest=man, sl=sl,
                  host_meta=fk.fake_host(), git_sha="g1", **prereg)
    fin.run(**common)
    pw.main(root)                                    # ONCE, from the synthetic finals
    (root / "projection.md").write_text("# projection (synthetic)\n")
    # Every size the production campaign sweeps (run/campaign_5.sh runs sweep_5
    # for EVERY size, the smallest last — S11 only). Freeze F-1: the worlds
    # swept SIZES_W[1:] alone, so the smallest size's sweep was never
    # exercised and its eight stray spine units never reached gate 4.
    for size in SIZES_W[1:] + SIZES_W[:1]:
        sw.run(size=size, seal_check=lambda r, **k: {"failures": []}, projection_commit="p1",
               is_ancestor=lambda a, b: True, power_present=True, **common)
    return {"manifest": man, "sl": sl, "battery": battery, "state": state, "host_meta": fk.fake_host()}
