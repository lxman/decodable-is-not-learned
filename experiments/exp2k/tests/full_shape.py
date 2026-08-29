# experiments/exp2k/tests/full_shape.py
"""Synthetic 2k worlds. The 2i tree is 2j's `write_world_2j(world=
"independent")` — a complete, provenance-valid 2i tree whose 7B
outcome y is independent of x_B and of the real x_A, with a
verdict.json carrying its own re-derived pins (A, B, within-alone,
cross-beyond-within, the reverse readings). 2k adds:

  * the k=256 tier at both sizes, whose SEED 0 IS THE REAL COMMITTED 2d
    ROW for the cell (so gate 1 passes byte for byte against the real
    2d files, and the comparison gate's x_A^(64) equals the real x_A)
    and whose seeds 1–3 are generated under a controlled mechanism:
      density   — item i emits its answer in seeds 1–3 with probability
                  q_i = strength · y_i / 21 (y from the world's own sweep)
                  → x_A^(256) forecasts y (DENSITY)
      null      — q_i independent of y (NOT-DENSITY, `null`)
      structured— density at a low strength, tuned so T lands in
                  [.03, .09] with p < .01 (NOT-DENSITY, `structured`)
  * the seal (through the REAL `seal_2k.seal_predictor`), a power record
    (literal status), and the 410m secondary re-derived into the
    world's verdict.json so the A410 comparison pin exists.

x_A's seed 0 is never synthesized; 2g/2h trees are the real committed
ones.

Ruling 1 (task-4 build): 2i's verdict.json carries the 410m cross
replication at `secondaries["replication_410m_cross"]` — the real key
`analyze_2k.pin_a410_from_record_2i` reads, with no fallback — so this
builder writes that key directly (the brief's draft used
`"cross_410m"`, superseded).

Ruling 3 (task-4 build): `analyze_2k.run()` is handed a test-only
`frozen_check` bypass (a one-line addition at the "2k frozen modules"
collect_total site, mirroring the `imports_pinned`/`referents_sha`
bypass pattern already there) because `battery_2k.check_frozen_2k`
refuses unconditionally until Task 5 pins `FROZEN_SHA256_2K` — without
the bypass every world would land INSUFFICIENT_DATA on that refusal
alone. `write_world_2k` returns `"frozen_check": lambda: None` so
`run_world`'s `**seal` expansion carries it through; Task 5 drops the
bypass here once the real pin lands."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np

EXP2K = Path(__file__).resolve().parents[1]
if str(EXP2K.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2K.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i.run.sample_2i import write_draws  # noqa: E402
from experiments.exp2i.tests import full_shape as fs2i  # noqa: E402
from experiments.exp2j.tests import full_shape as fs2j  # noqa: E402
from experiments.exp2k import analyze_2k as an  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2k.run import seal_2k  # noqa: E402

_TAG_OK = dict(tag_exists=lambda t: True,
               blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel),
               frozen_check=lambda: None)   # Task 5 drops frozen_check (the real pin then applies)
STRUCTURED_STRENGTH = 0.0015   # tuned at the build (ledger the landing T); see Step 6 / PROGRESS.md


def _restrict_r_cap_to_design(root) -> None:
    """Build finding, ledgered in PROGRESS.md: `fs2j.write_world_2j`'s
    `world="independent"` tree assigns every one of 2i's ELEVEN
    STRATA_RUNGS exactly N_POS_FIRING=200 positive items by the endpoint
    step (its `first[r]` builder applies to every `RUNGS_CAP` rung
    unconditionally, with no way to parameterize a subset), so its
    natural derived R_CAP is all eleven — two more (count_div13,
    median5, confirmed empirically at this build) than design §3.4's
    frozen nine (`battery_2k.R_CAP_DESIGN`), which `analyze_2k.
    load_2i_tree` refuses on unconditionally. Zero the two extra rungs'
    ENDPOINT_STEP_7B sweep record AND `stage1_final` endpoint record
    (both, so 2i's gate-1 byte-identity re-derivation still sees a
    consistent pair) and re-derive `rung_set.json` fresh through 2i's
    own `rung_set_from_counts` — a real world-construction fix, not a
    hand-edit of R_CAP itself, so `analyze_2i._check_rung_set_derivation`
    (which RE-DERIVES from the endpoint's own counts, never merely
    trusts the file) still passes."""
    battery, floors = fs2i.battery(), fs2i.floors()
    rs = json.loads(bi.rung_set_path(root).read_text())
    extra = sorted(set(rs["R_CAP"]) - set(bk.R_CAP_DESIGN))
    zero_bits = [0] * bt.N_ITEMS
    zero_conts = [" zzz"] * bt.N_ITEMS
    for r in extra:
        sw_path = bi.record_path(root, bi.ENDPOINT_STEP_7B, r)
        sw = json.loads(sw_path.read_text())
        sw["bits"], sw["correct"], sw["continuations"] = zero_bits, 0, zero_conts
        sw_path.write_text(json.dumps(sw))
        ep_path = bi.endpoint_record_path(root, "stage1_final", r)
        ep = json.loads(ep_path.read_text())
        ep["bits"], ep["correct"], ep["continuations"] = zero_bits, 0, zero_conts
        ep_path.write_text(json.dumps(ep))
    stage1_correct = {r: json.loads(bi.endpoint_record_path(root, "stage1_final", r).read_text())["correct"]
                      for r in bt.RUNGS}
    rs2 = bi.rung_set_from_counts(stage1_correct, floors)
    if tuple(sorted(rs2["R_CAP"])) != bk.R_CAP_DESIGN:
        raise AssertionError(f"world builder: re-derived R_CAP {sorted(rs2['R_CAP'])} != "
                             f"design's {list(bk.R_CAP_DESIGN)}")
    fs2i._w(bi.rung_set_path(root), {**rs2, "endpoint_file_sha256": {}})


def _tier_rows(rng, cap, committed, y, world, strength):
    n = bt.N_ITEMS
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    if world in ("density", "structured"):
        q = np.clip(strength * np.asarray(y, dtype=float) / 21.0, 0.0, 0.95)
    else:
        q = rng.uniform(0.0, 0.3, size=n)
    rows = []
    for i in range(n):
        draws = {"0": list(committed[i])}
        for s in (1, 2, 3):
            draws[str(s)] = [f" {answers[i]}" if rng.random() < q[i] else " zzz"
                             for _ in range(bk.DRAWS_PER_SEED)]
        rows.append({"item": i, "draws": draws})
    return rows


def write_world_2k(root, *, world="density", strength=1.0, seed=0, missing=None,
                   power_status="POWERED", wrong_pin=False) -> dict:
    root = Path(root)
    rng = np.random.default_rng(seed)
    seal2i = fs2j.write_world_2j(root, world="independent", seed=seed)
    _restrict_r_cap_to_design(root)
    bat, verify = fs2i.battery(), fs2i.verify_fn()
    man = fs2i.manifest()
    rs = json.loads(bi.rung_set_path(root).read_text())
    r_cap = tuple(sorted(rs["R_CAP"]))
    psha = json.loads(bi.predictor_seal_path(root).read_text())["sha256"]
    sweep = an2i.load_sweep_7b(root, bat, verify, manifest=man, predictor_sha=psha)
    out = an2i.outcomes_7b(sweep, rungs=r_cap)
    strength = STRUCTURED_STRENGTH if world == "structured" else strength
    # ---- the 2k tier, both sizes; seed 0 = the REAL committed row
    for size in bk.SIZES_2K:
        for r in r_cap:
            cap = bat[r]
            committed = bk.committed_by_item(bk.committed_rows(size, r))
            rows = _tier_rows(rng, cap, committed, out[r]["y"], world if size == "1b" else "null",
                              strength)
            write_draws(bk.tier_draws_path(root, size, r), rows)
            crec_p, cgz_p = bk.committed_record_path(size, r), bk.committed_draws_path(size, r)
            rec = bk.tier_record_2k(rung=r, size=size, cap=cap, rows=rows, verify_fn=verify,
                                    model_sha=bk.pythia_sha(size),
                                    stack={"torch": "n/a", "transformers": "n/a"}, git_sha="",
                                    seconds=0.0, committed_gz_sha=bg.sha256_file(cgz_p),
                                    committed_record_sha=bg.sha256_file(crec_p),
                                    gate1_items_compared=bt.N_ITEMS,
                                    gate1_draws_compared=bt.N_ITEMS * bk.DRAWS_PER_SEED)
            fs2i._w(bk.tier_record_path(root, size, r), rec)
    # ---- the seal through the REAL tool, the power record (literal)
    seal = seal_2k.seal_predictor(root, **_TAG_OK)
    fs2i._w(bk.power_path(root), {"primary": {"declared_status": power_status, "declaration": "x",
                                              "rungs": list(r_cap), "n_trained_steps": bi.n_trained_7b()},
                                  "predictor_sha256": seal["sha256"], "shape_note": "x", "note": "x"})
    # ---- the 410m comparison pin re-derived on the world's outcome
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred2g["strata"])
    x410 = bi.sampler_counts_pythia("410m", r_cap)
    a410 = an2i._run_test(x410, "410m", out, strata, r_cap, n_perm=20, n_boot=5)
    vpath = root / "results" / "verdict.json"
    v2i = json.loads(vpath.read_text())
    # `_restrict_r_cap_to_design` narrowed r_cap AFTER `write_world_2j`
    # already wrote `verdict.json`'s "A" test over its own (eleven-rung)
    # r_cap — re-derive "A" over the CORRECTED nine-rung r_cap so
    # `run()`'s own comparison gate (re-derived == on-disk == literal)
    # agrees; only T/per-rung d matter (`pin_a_from_record_2i`), both
    # permutation-independent, so n_perm here need not match `run()`'s.
    x_a64 = bi.sampler_counts_pythia("1b", r_cap)
    a_test = an2i._run_test(x_a64, "1b", out, strata, r_cap, n_perm=20, n_boot=5)
    v2i["tests"]["A"] = json.loads(json.dumps(an2i._json_safe(a_test), default=an2i._jsonable))
    # Ruling 1: the real key `pin_a410_from_record_2i` reads, no fallback.
    v2i["secondaries"]["replication_410m_cross"] = json.loads(json.dumps(an2i._json_safe(a410),
                                                                        default=an2i._jsonable))
    if wrong_pin:
        v2i["tests"]["A"]["stratified"]["T"] = 0.123456
    fs2i._w(vpath, v2i)
    pin_a = v2i["tests"]["A"]["stratified"]["T"]
    pin_a410 = v2i["secondaries"]["replication_410m_cross"]["stratified"]["T"]
    # ---- the deliberate breakages
    if missing == "tier_record":
        bk.tier_record_path(root, "1b", "antonym").unlink()
    if missing == "truncated_draws":
        p = bk.tier_draws_path(root, "410m", "odd6")
        p.write_bytes(p.read_bytes()[:-200])
    if missing == "halt":
        bk.halt_marker_path(root, "1b", "arith_next").write_text("{}")
    if missing == "gate1_diff":
        p = bk.tier_draws_path(root, "1b", "sub_base8")
        rows = bk.read_rows_2k(p)
        rows[3]["draws"]["0"][0] = rows[3]["draws"]["0"][0] + "!"
        write_draws(p, rows)
    if missing == "seal_counts":
        s = json.loads(bk.seal_path(root).read_text())
        s["counts"]["1b"]["antonym"][0] += 1
        # Ruling 5: touch counts_by_k too, not only the 256-draw counts.
        s["counts_by_k"]["1b"]["64"]["antonym"][0] += 1
        bk.seal_path(root).write_text(json.dumps(s, indent=1, sort_keys=True))
    if missing == "power":
        bk.power_path(root).unlink()
    if missing == "model_sha":
        p = bk.tier_record_path(root, "410m", "add3_mid")
        rec = json.loads(p.read_text())
        rec["model_sha"] = "0" * 40
        p.write_text(json.dumps(rec))
    if missing == "power_sha":
        p = bk.power_path(root)
        rec = json.loads(p.read_text())
        rec["predictor_sha256"] = "0" * 64
        p.write_text(json.dumps(rec))
    return {**{k: seal2i[k] for k in ("tag_exists", "blob_sha", "blobs_bound")},
            "pin_a": pin_a, "pin_a410": pin_a410, "verdict_2i_path": vpath,
            "frozen_check": lambda: None}


def run_world(root, seal, *, n_perm=200, n_boot=20) -> dict:
    return an.run(root_2i=root, root_2k=root, n_perm=n_perm, n_boot=n_boot, referents_sha=False,
                  imports_pinned=False, **seal)


def world_specs() -> list:
    return [
        ("W1 DENSITY", dict(world="density"), "DENSITY", None),
        ("W2 NOT-DENSITY null", dict(world="null"), "NOT-DENSITY", "null"),
        ("W3 NOT-DENSITY structured", dict(world="structured"), "NOT-DENSITY", "structured"),
        ("W4 NOT-DENSITY underpowered", dict(world="null", power_status="DECLARED UNDERPOWERED IN ADVANCE"),
         "NOT-DENSITY", "null"),
        ("W5 INSUFFICIENT missing tier record", dict(world="density", missing="tier_record"),
         "INSUFFICIENT_DATA", None),
        ("W6 INSUFFICIENT truncated draws", dict(world="density", missing="truncated_draws"),
         "INSUFFICIENT_DATA", None),
        ("W7 INSUFFICIENT halted", dict(world="density", missing="halt"), "INSUFFICIENT_DATA", None),
        ("W8 INSUFFICIENT gate-1 diff", dict(world="density", missing="gate1_diff"),
         "INSUFFICIENT_DATA", None),
        ("W9 INSUFFICIENT seal counts", dict(world="density", missing="seal_counts"),
         "INSUFFICIENT_DATA", None),
        ("W10 INSUFFICIENT wrong pin", dict(world="density", wrong_pin=True), "INSUFFICIENT_DATA", None),
        ("W11 INSUFFICIENT missing power", dict(world="density", missing="power"),
         "INSUFFICIENT_DATA", None),
        ("W12 INSUFFICIENT model sha", dict(world="density", missing="model_sha"),
         "INSUFFICIENT_DATA", None),
        ("W13 INSUFFICIENT power sha", dict(world="density", missing="power_sha"),
         "INSUFFICIENT_DATA", None),
    ]
