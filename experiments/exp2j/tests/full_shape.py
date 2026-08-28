# experiments/exp2j/tests/full_shape.py
"""Synthetic 2j worlds: a complete 2i tree (2i's production layout,
provenance-valid) with x_B draws and the 7B outcome generated under a
CONTROLLED mechanism, plus a 2j power record and a synthetic 2i
verdict.json carrying the world's own re-derived pins.

  residual    — every item i emits its answer with an item-specific
                probability q_i; a rung-level HABIT distribution over
                answer strings supplies the wrong-target draws; y is
                ordered by q_i  → x_B forecasts beyond π/L/R/O (RESIDUAL)
  absorbed    — the answer draws come from the habit alone (item i's
                count is high iff a_i is a habit string), y is ordered
                by the habit weight of a_i → x_B forecasts, but nothing
                survives conditioning on π (ABSORBED)
  independent — y independent of everything (ABSORBED via no forecast)

x_A is the REAL committed 2d table (never synthesized), as in 2i's
worlds; the 2g/2h trees are the real committed ones."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP2J = Path(__file__).resolve().parents[1]
if str(EXP2J.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2J.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i.run import endpoint_2i as ep  # noqa: E402
from experiments.exp2i.run.sample_2i import write_draws  # noqa: E402
from experiments.exp2i.tests import full_shape as fs2i  # noqa: E402
from experiments.exp2j import analyze_2j as an  # noqa: E402
from experiments.exp2j import functionals_2j as fn  # noqa: E402

RUNGS_CAP = tuple(bi.STRATA_RUNGS)
N_POS_FIRING = 200


# build finding, ledgered (PROGRESS.md): a CONTINUOUS habit distribution
# (gamma(0.5, 1.0) over every distinct answer, the brief's literal draft)
# leaves W2 landing RESIDUAL, not ABSORBED — pi's bucket rule is a single
# MEDIAN split, and a continuous habit weight still varies substantially
# within each half, so beyond_all's T stayed at .24-.39 (T_BAR .10) at
# every gamma shape tried (.5/.2/.1/.05, via a fast debug harness — its
# rung-iteration order differs from THIS function's, so its specific
# numbers do not reproduce here; see PROGRESS.md). Swapping in a
# two-level (bimodal) habit weight for the non-'residual' worlds — half
# the distinct answers 'hot' at 10x the other half's weight, +/-2%
# noise so ties never degenerate the bucket — makes pi (an average over
# ~32,000 draws) an almost noise-free readout of hot/cold membership,
# so its median split matches the habit partition closely. Verified
# through THIS module's own write_world_2j/run_world at n_perm=200,
# n_boot=20, seed 0 (PROGRESS.md carries the full table): at the
# shipped dial (hot_ratio=10) beyond_all drops to T .0620 (< T_BAR,
# does not fire) while within_alone still fires at T .2777 and
# alone['pi'] at T .6449; hot_ratio 30 and 100 verify the same way
# (beyond_all T .0327 / .0398), all with comfortable margin under
# T_BAR. Final: hot_ratio=10.0, hot_frac=0.5, weight_noise=0.02.
# 'residual' keeps the original continuous gamma (unaffected — W1 was
# never the world in question).
_HOT_RATIO, _HOT_FRAC, _WEIGHT_NOISE = 10.0, 0.5, 0.02


def _draws_for_rung(rng, cap, world):
    """Returns (rows, latent) — rows in 2d's format; latent orders y."""
    n = bt.N_ITEMS
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    distinct = sorted(set(answers))
    if world == "residual":
        habit_w = rng.gamma(0.5, 1.0, size=len(distinct))
    else:
        is_hot = rng.random(len(distinct)) < _HOT_FRAC
        level = np.where(is_hot, _HOT_RATIO, 1.0)
        habit_w = level * (1 + _WEIGHT_NOISE * rng.normal(size=len(distinct)))
        habit_w = np.clip(habit_w, 1e-8, None)
    habit_w /= habit_w.sum()
    habit_of = {a: w for a, w in zip(distinct, habit_w)}
    q = rng.beta(0.5, 2.0, size=n)                     # item-specific competence
    rows, latent = [], np.zeros(n)
    for i in range(n):
        draws = []
        for _ in range(bi.DRAWS_PER_ITEM):
            if world == "residual" and rng.random() < q[i]:
                draws.append(f" {answers[i]}")
            else:
                draws.append(f" {distinct[rng.choice(len(distinct), p=habit_w)]}")
        rows.append({"item": i, "draws": {"0": draws}})
        if world == "residual":
            latent[i] = q[i] + 0.01 * rng.normal()
        elif world == "absorbed":
            latent[i] = habit_of[answers[i]] + 1e-4 * rng.normal()
        else:
            latent[i] = rng.normal()
    return rows, latent


def write_world_2j(root, *, world="residual", missing=None, seed=0,
                   power_status="POWERED", wrong_pin=False) -> dict:
    root = Path(root)
    rng = np.random.default_rng(seed)
    bat, man, verify = fs2i.battery(), fs2i.manifest(), fs2i.verify_fn()
    x_a = fs2i.x_a_real()
    entry_1b = bi.entry_1b_endpoint(man)

    x_b, latent = {}, {}
    for r in bt.RUNGS:
        cap = bat[r]
        if r in RUNGS_CAP:
            rows, lat = _draws_for_rung(rng, cap, world)
            latent[r] = lat
        else:
            rows = [{"item": i, "draws": {"0": ["zzz"] * bi.DRAWS_PER_ITEM}} for i in range(bt.N_ITEMS)]
        write_draws(bi.predictor_draws_path(root, r), rows)
        bits = fn.verified_bits(rows, cap, verify)
        x_b[r] = fn.counts_from_bits(bits)
        fs2i._w(bi.predictor_record_path(root, r), fs2i.predictor_record_2i(r, cap, entry_1b, sum(x_b[r])))
    psha = "WORLD-PREDICTOR-SEAL"
    fs2i._w(bi.predictor_seal_path(root),
            {"files": {}, "counts": {r: list(x_b[r]) for r in bt.RUNGS}, "sha256": psha,
             "tag": bi.PREDICTOR_SEAL_TAG,
             "sampling": {"size": bi.SIZE_PRED, "repo": bi.REPO_1B, "revision": bi.REV_1B_ENDPOINT,
                          "commit": entry_1b["commit"], "seed": bi.SAMPLING_SEED,
                          "draws_per_item": bi.DRAWS_PER_ITEM, "temperature": 1.0,
                          "dtype": a2d.SAMPLING_DTYPE, "stream_namespace": "exp3",
                          "stream_formula": "f"}})
    n_tr = len(bi.trained_steps_7b())
    fs2i._w(bi.power_path(root), {"A": {"declared_status": "POWERED", "declaration": "x",
                                        "rungs": list(RUNGS_CAP), "n_trained_steps": n_tr},
                                  "B": {"declared_status": "POWERED", "declaration": "x",
                                        "rungs": list(RUNGS_CAP), "n_trained_steps": n_tr}})
    # ---- sweep from the latent (2i's builder, verbatim shape)
    steps = bi.trained_steps_7b()
    first = {}
    for r in bt.RUNGS:
        if r in RUNGS_CAP:
            order = np.argsort(-latent[r])
            first[r] = {int(i): steps[int(rank * n_tr / N_POS_FIRING)]
                        for rank, i in enumerate(order[:N_POS_FIRING])}
        else:
            first[r] = {}
    entry_stage1 = bi.entry_7b(man, bi.ENDPOINT_STEP_7B)
    entry_main = bi.entry_main(man, bi.REPO_7B)
    stage1_from_sweep = {}
    for step in steps:
        entry = bi.entry_7b(man, step)
        fs2i._w(bi.checkpoint_record_path(root, step),
                {"sha256": dict(entry.get("lfs_sha256", {})),
                 "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}})
        for r in bt.RUNGS:
            cap = bat[r]
            bits = [int(i in first[r] and step >= first[r][i]) for i in range(bt.N_ITEMS)]
            conts = [f" {it['answer']}" if b else " zzz" for b, it in zip(bits, cap["eval_items"])]
            rec = {"rung": r, "size": bi.SIZE_OUT, "family": bi.FAMILY, "step": step,
                   "commit": entry["commit"], "items_sha256": cap["items_sha256"], "n": bt.N_ITEMS,
                   "correct": sum(bits), "bits": bits, "continuations": conts,
                   "predictor_sha": psha, "seal_tag": bi.ENDPOINT_SEAL_TAG,
                   "answer_type": cap["answer_type"]}
            fs2i._w(bi.record_path(root, step, r), rec)
            if step == bi.ENDPOINT_STEP_7B:
                stage1_from_sweep[r] = rec
    for r in bt.RUNGS:
        cap = bat[r]
        fs2i._w(bi.record_path(root, bi.TWIN, r),
                {"rung": r, "size": bi.SIZE_OUT, "family": bi.FAMILY, "step": bi.TWIN, "commit": None,
                 "kind": "from_config", "items_sha256": cap["items_sha256"], "n": bt.N_ITEMS,
                 "correct": 0, "bits": [0] * bt.N_ITEMS, "continuations": [" zzz"] * bt.N_ITEMS,
                 "predictor_sha": psha, "seal_tag": bi.ENDPOINT_SEAL_TAG,
                 "answer_type": cap["answer_type"]})
    stage1_correct = {}
    for r in bt.RUNGS:
        cap = bat[r]
        sw = stage1_from_sweep[r]
        ev = {"bits": list(sw["bits"]), "correct": sw["correct"], "continuations": list(sw["continuations"])}
        stage1_correct[r] = ev["correct"]
        ckpt = {"revision": entry_stage1["revision"], "commit": entry_stage1["commit"],
                "kind": entry_stage1["kind"], "files": list(entry_stage1.get("files", [])),
                "weight_sha256": "D", "config_source": "cs", "tokenizer_source": "ts"}
        fs2i._w(bi.endpoint_record_path(root, "stage1_final", r),
                ep.item_record_2i(rung=r, family=bi.FAMILY, size=bi.SIZE_OUT, which="stage1_final",
                                  cap=cap, ev=ev, ckpt=ckpt,
                                  seal={"tag": bi.PREDICTOR_SEAL_TAG, "sha256": psha}, t_s=0.0))
        ckpt_main = {"revision": entry_main["revision"], "commit": entry_main["commit"],
                     "kind": entry_main["kind"], "files": list(entry_main.get("files", [])),
                     "weight_sha256": "D", "config_source": "cs", "tokenizer_source": "ts"}
        ev0 = {"bits": [0] * bt.N_ITEMS, "correct": 0, "continuations": [" zzz"] * bt.N_ITEMS}
        fs2i._w(bi.endpoint_record_path(root, "main", r),
                ep.item_record_2i(rung=r, family=bi.FAMILY, size=bi.SIZE_OUT, which="main", cap=cap,
                                  ev=ev0, ckpt=ckpt_main,
                                  seal={"tag": bi.PREDICTOR_SEAL_TAG, "sha256": psha}, t_s=0.0))
    rs = bi.rung_set_from_counts(stage1_correct, fs2i.floors())
    fs2i._w(bi.rung_set_path(root), {**rs, "endpoint_file_sha256": {}})
    fs2i._w(bi.gate1_path(root),
            {"rungs": list(bt.RUNGS), "bit_diffs": {r: 0 for r in bt.RUNGS},
             "continuation_diffs": {r: 0 for r in bt.RUNGS},
             "continuations_compared": {r: bt.N_ITEMS for r in bt.RUNGS},
             "digest_sweep": "D" * 64, "digest_endpoint": "D" * 64,
             "commit_sweep": entry_stage1["commit"], "commit_endpoint": entry_stage1["commit"],
             "prereg_tag": bi.PREREG_TAG})
    # ---- 2j's own power record (root_2j == root)
    r_cap = tuple(rs["R_CAP"])
    fs2i._w(root / "results" / "power_2j.json",
            {"primary": {"declared_status": power_status, "declaration": "x", "rungs": list(r_cap),
                         "n_trained_steps": n_tr}, "shape_note": "x"})
    # ---- the world's own 2i pins: re-derived through 2i's code on the world's bytes
    sweep = an2i.load_sweep_7b(root, bat, verify, manifest=man, predictor_sha=psha)
    out = an2i.outcomes_7b(sweep, rungs=tuple(bt.RUNGS))
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred2g["strata"])
    py = an.load_pythia_outcomes(bat, verify)
    x_a_full = bi.sampler_counts_pythia("1b", tuple(sorted(set(r_cap) | set(bg.R_28) | set(bh.R_69))))
    red = an.rederive_2i(x_a_full, x_b, out, strata, r_cap, py, n_perm=20, n_boot=5)
    pins = {k: v["stratified"]["T"] for k, v in red.items()}
    if wrong_pin:
        pins["B"] = 0.123456
    v2i = {"tests": {"A": red["A"], "B": red["B"]},
           "secondaries": {"within_alone": red["within_alone"],
                           "cross_beyond_within": red["cross_beyond_within"],
                           "reverse_direction": {"vs_2.8b": red["reverse_2.8b"],
                                                 "vs_6.9b": red["reverse_6.9b"]}}}
    vpath = root / "results" / "verdict.json"
    fs2i._w(vpath, json.loads(json.dumps(an2i._json_safe(v2i), default=an2i._jsonable)))
    if missing == "predictor_draws":
        bi.predictor_draws_path(root, "antonym").unlink()
    if missing == "power":
        (root / "results" / "power_2j.json").unlink()
    if missing == "verdict_2i":
        vpath.unlink()
    if missing == "halt":
        bi.halt_marker_path(root).write_text("synthetic halt\n")

    def blob_sha(tag, rel):
        p = bi.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    return {"tag_exists": lambda t: True, "blob_sha": blob_sha,
            "blobs_bound": lambda tag, paths, repo_root=None: [],
            "pins_2i": pins, "verdict_2i_path": vpath}


def run_world(root, seal, *, n_perm=200, n_boot=20) -> dict:
    return an.run(root_2i=root, root_2j=root, n_perm=n_perm, n_boot=n_boot,
                  referents_sha=False, **seal)


def world_specs() -> list:
    return [
        ("W1 RESIDUAL", dict(world="residual"), "RESIDUAL"),
        ("W2 ABSORBED habit", dict(world="absorbed"), "ABSORBED"),
        ("W3 ABSORBED independent", dict(world="independent"), "ABSORBED"),
        ("W4 ABSORBED underpowered", dict(world="independent",
                                          power_status="DECLARED UNDERPOWERED IN ADVANCE"), "ABSORBED"),
        ("W5 INSUFFICIENT missing x_B draws", dict(world="residual", missing="predictor_draws"),
         "INSUFFICIENT_DATA"),
        ("W6 INSUFFICIENT missing power", dict(world="residual", missing="power"), "INSUFFICIENT_DATA"),
        ("W7 INSUFFICIENT missing 2i verdict", dict(world="residual", missing="verdict_2i"),
         "INSUFFICIENT_DATA"),
        ("W8 INSUFFICIENT comparison pin mismatch", dict(world="residual", wrong_pin=True),
         "INSUFFICIENT_DATA"),
        ("W9 INSUFFICIENT halted", dict(world="residual", missing="halt"), "INSUFFICIENT_DATA"),
    ]
