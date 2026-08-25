# experiments/exp2h/analyze_2h.py
"""Exp 2h frozen analysis (design §3-§6): the sampler confirmation on
6.9b. A thin delta on `experiments/exp2g`'s analyzer shape — the
primary predictor is battery_2h's real per-item SAMPLED count at 1b
(not the probe), the outcome is 6.9b's grid, and the tree has no
twin/SURFACE terminal (§3.3: the untrained twin's sampled counts are
all-zero by construction — exp3's twin referent, 0 verified in
576,000 — so a twin arm is vacuous and dropped, not silently absorbed).
2g's own sealed predictor (`PREDICTOR_2G_SHA`) is the NAMED COMPETITOR
here, printed with the same statistic, plus the two beyond-each-other
partial concordances. Every input re-asserted against a pin; every
loader refusal COLLECTED and delivered as INSUFFICIENT_DATA with the
reason verbatim (lesson 8, carried from 2g); the verdict tree
mechanical (§3.3); the secondaries printed, non-gating.

Tree: INSUFFICIENT_DATA → CONFIRMED (p_strat < .01 ∧ T ≥ .10) →
NOT-CONFIRMED (everything else; 'detected below the effect bar' and
'inverted' named inside it, as 2g)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

EXP2H = Path(__file__).resolve().parent
if str(EXP2H.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2H.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st2d  # noqa: E402
from experiments.exp2g import analyze_2g as an2g  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import labels_2g as lb  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402

RESULTS = EXP2H / "results"
REFERENTS_PATH_2H = EXP2H / "referents_2h.json"
POWER_PATH_2H = EXP2H / "power_2h.json"

# checkpoints_2h.json — generated + pinned by battery_2h's __main__ (Task 1)
CHECKPOINTS_2H_SHA256 = \
    "c5cd292cbf0d26a6968c5852d8bbf7f872d4b78fd8c7352a8a3e9e11be67cf60"
# referents_2h.json — built and pinned by this task (make_referents_2h.py)
REFERENTS_2H_SHA256 = \
    "cd06f8e7e9f6749d1b4d57e748e3f75d754728b6fb369f954e1118419b9b4d49"
# power_2h.json — POWERED: P(CONFIRMED | D_true = 0.15) = 0.979 against
# the bar 0.75; null false-CONFIRMED rate 0.000; null SD of T 0.0209
# (Task 3, power_2h.main() run 2026-08-24)
POWER_2H_SHA256 = \
    "1c1738626b3c21e59430ecc096a8c32962ebd5bbe06fb44d6b766415443d3dcd"

WORLDS = ("INSUFFICIENT_DATA", "CONFIRMED", "NOT-CONFIRMED")
ALPHA, T_BAR = st.ALPHA, st.T_BAR
N_PERM, N_BOOT = st.N_PERM, st.N_BOOT

collect = an2g.collect   # fully generic (thunk, label) -> (value, failures); no 2g globals


def collect_total(thunk, label):
    """`analyze_2g.collect` with the exception surface widened to the
    shapes a killed / torn / hand-edited tree actually presents and 2g's
    four-name tuple does not catch: `TypeError`/`AttributeError` (a JSON
    record that parses but is a list/str/number where a dict is
    expected, so `rec.get(...)` or `list(rec["rungs"])` explodes) and
    `OSError` (a DIRECTORY where the runner writes a file —
    `IsADirectoryError` is not a `FileNotFoundError`).

    FREEZE F-1, the 2d F-1 class one level over: on nine such trees the
    frozen verdict RAISED instead of delivering INSUFFICIENT_DATA, i.e.
    §6's first terminal was unreachable from those trees. Widening is
    additive and one-directional — every caught failure still lands in
    `failures` verbatim and the verdict is INSUFFICIENT_DATA; nothing
    that would have produced a verdict can now produce a different one,
    and no accepted dial is touched."""
    try:
        return thunk(), []
    except (ValueError, KeyError, RuntimeError, TypeError, AttributeError,
            OSError) as e:
        return None, [f"{label}: {type(e).__name__}: {e}"]


KNOWN_INPUTS_CAVEAT_2H = (
    "Known to the designer before any 6.9b checkpoint loaded: 2c's committed m4 "
    "counts at 6.9b final weights (which fix R_69 and bound each rung's number "
    "of positive-outcome items from below); 2d's committed per-item sampled "
    "counts at 410m/1b (main tier, seed 0, 64 draws per item, on disk since "
    "2026-08-22) — the primary predictor and its replication; 2g's entire "
    "closed verdict, including the sampler's per-rung concordances at 2.8b — "
    "the probe competitor is 2g's own sealed table (tag "
    "exp2g-predictor-sealed), historically prior to any 6.9b checkpoint sweep "
    "in this program. Not known to anyone: any quantity at any 6.9b "
    "intermediate checkpoint — the per-item verify bits, the trajectories, the "
    "first-clear steps. Both predictors were fixed before the first checkpoint "
    "of any sweep in this experiment loaded (design §2).")

LICENSED = {
    "CONFIRMED": ("sampled reachability at 1b, fixed before any 6.9b checkpoint was "
                  "loaded, forecasts the order in which 6.9b's training makes 2c's "
                  "rising items emittable, through difficulty strata, with the probe "
                  "adding nothing beyond it — together with 2g's 2.8b record this "
                  "stands at the reversal case's standing: two sealed outcomes, two "
                  "resolution steps, one committed predictor"),
    "NOT-CONFIRMED": ("2g's secondary is demoted to exploratory in the essay and "
                      "experiments.md; the output-channel sentence is softened to one "
                      "sealed outcome; not detected at this resolution, blind region "
                      "stated"),
    "INSUFFICIENT_DATA": "nothing; the record states which referent failed",
}


def load_power_2h(path=POWER_PATH_2H, *, sha_pin=POWER_2H_SHA256) -> dict:
    """The committed power record (Task 3): sha-pinned, declared_status
    + declaration required, attached to the verdict via collect()."""
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"power record {path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    for k in ("declared_status", "declaration"):
        if k not in rec:
            raise ValueError(f"power record {path} missing {k!r}")
    return {"declared_status": rec["declared_status"], "declaration": rec["declaration"],
            "n_sim": rec.get("n_sim"), "sha256": got}


# ------------------------------------------------------- the prereg tag

def require_prereg_2h(*, tag_exists=None) -> dict:
    """No stage-1 predictor build/seal for 2h (design §7): both
    predictors — the sampler primary (2d's committed draws) and the
    probe competitor (2g's already-sealed predictor.json,
    `bh.PREDICTOR_2G_SHA`) — were fixed before this experiment's
    design was written. What gates the 6.9b sweep is the freeze tag
    alone (Task 3's runner refuses without it); the analyzer
    re-asserts the same tag before trusting any sweep record."""
    tag_exists = tag_exists or pr.git_tag_exists
    if not tag_exists(bh.PREREG_TAG_2H):
        raise RuntimeError(f"refusing: the preregistration tag {bh.PREREG_TAG_2H!r} does "
                           f"not exist — the design must be frozen and tagged before any "
                           f"6.9b checkpoint contact")
    return {"tag": bh.PREREG_TAG_2H}


# -------------------------------------------------------------- gate 1

def gate1_failures_69(rec: dict) -> list:
    """Mirrors `analyze_2g.gate1_failures`'s pattern with the 6.9b/2h
    pins: counts vs FINAL_COUNT_PIN_69 on all 34 rungs, digest
    equality between the two loader paths, zero continuation diffs,
    and the freeze tag stamped on the record (2h's stand-in for 2g's
    predictor-seal check — there is no predictor seal here, design
    §7)."""
    bad = []
    rungs = tuple(bt.RUNGS)
    if rec.get("size") != bh.SIZE:
        bad.append(f"gate 1 {bh.SIZE}: record is for {rec.get('size')!r}")
    if list(rec.get("rungs", [])) != list(rungs):
        bad.append(f"gate 1 {bh.SIZE}: rung list is not the full 34-rung sweep set")
    if rec.get("model_sha") != an2g.pythia_sha(bh.SIZE):
        bad.append(f"gate 1 {bh.SIZE}: model_sha is not 2c's pinned main")
    counts = rec.get("counts_2c_path", {})
    for r in rungs:
        if r not in counts:
            bad.append(f"gate 1 {bh.SIZE}: no count for {r}")
        elif counts[r] != bh.FINAL_COUNT_PIN_69[r]:
            bad.append(f"gate 1 {bh.SIZE}/{r}: 2c's loader gives {counts[r]}, m4 committed "
                       f"{bh.FINAL_COUNT_PIN_69[r]} — the stack drifted")
    da, db = rec.get("digest_2c_path"), rec.get("digest_2h_path")
    if not da or not db or da != db:
        bad.append(f"gate 1 {bh.SIZE}: tensor digest through 2h's loader ({db}) ≠ through "
                   f"2c's ({da}) — the checkpoint loader path is not the production path")
    cd = rec.get("continuation_diffs_2h_path", {})
    for r in rungs:
        if cd.get(r) != 0:
            bad.append(f"gate 1 {bh.SIZE}/{r}: {cd.get(r)} continuation diffs between the "
                       f"two loader paths")
    if rec.get("prereg_tag") != bh.PREREG_TAG_2H:
        bad.append(f"gate 1 {bh.SIZE}: prereg_tag {rec.get('prereg_tag')!r} is not "
                   f"{bh.PREREG_TAG_2H!r}")
    return bad


# ------------------------------------------------------- step records

def load_sweep_69(root, battery, verify_fn, *, manifest, seal_sha, steps=None,
                  rungs=None) -> dict:
    """Mirrors `analyze_2g.load_sweep`'s body for the single 6.9b size
    (`bg.trained_steps`/`bg.sweep_rungs`/`ck.entry_for` are all bound
    to exp2g-only globals lacking a 6.9b key, so this reads through
    `battery_2h`'s own paths/manifest instead); re-derives every
    per-step-per-rung record through `analyze_2g.step_record_failures`
    UNCHANGED (its `pythia_sha`/`FINAL_STEP` reads both work at 6.9b —
    verified at the call site, not assumed: `PYTHIA_SHAS` carries a
    "6.9b" key and 143000 == 143000 regardless of which module's
    constant supplies it)."""
    steps = tuple(steps) if steps is not None else bh.GRID_69
    rungs = tuple(rungs) if rungs is not None else tuple(bt.RUNGS)
    out = {}
    for step in steps:
        entry = bh.entry_69(manifest, step)
        out[step] = {}
        for rung in rungs:
            p = bh.record_path_2h(root, step, rung)
            if not p.is_file():
                raise FileNotFoundError(f"sweep record missing: {p}")
            rec = json.loads(p.read_text())
            bad = an2g.step_record_failures(rec, size=bh.SIZE, step=step, rung=rung,
                                            cap=battery[rung], entry=entry,
                                            verify_fn=verify_fn, seal_sha=seal_sha)
            if bad:
                raise ValueError("; ".join(bad))
            out[step][rung] = rec
        if step != bh.FINAL_STEP_69:
            cp = bh.checkpoint_record_path_2h(root, step)
            if not cp.is_file():
                raise FileNotFoundError(f"checkpoint record missing: {cp}")
            crec = json.loads(cp.read_text())
            for name, want in entry["lfs_sha256"].items():
                if crec.get("sha256", {}).get(name) != want:
                    raise ValueError(f"{bh.SIZE}/step{step}: downloaded {name} sha "
                                     f"{crec.get('sha256', {}).get(name)} ≠ manifest {want}")
            if crec.get("loading_info", {}) != {"missing_keys": 0, "unexpected_keys": 0,
                                                 "mismatched_keys": 0}:
                raise ValueError(f"{bh.SIZE}/step{step}: loading info not empty")
    return out


# ------------------------------------------------------------ outcomes

def outcomes_69(sweep: dict, *, rungs=None) -> dict:
    """`analyze_2g.outcomes`'s body with `bg.trained_steps(size)`
    replaced by `battery_2h.trained_steps_69()` (2g's is bound to
    `bg.GRID`, which has no "6.9b" key)."""
    steps = bh.trained_steps_69()
    rungs = tuple(rungs) if rungs is not None else tuple(bt.RUNGS)
    out = {}
    for rung in rungs:
        bits = {s: [int(b) for b in sweep[s][rung]["bits"]] for s in sweep}
        y, first, last, stab = [], [], [], []
        for i in range(bt.N_ITEMS):
            hits = [s for s in steps if bits[s][i]]
            y.append(len(hits))
            first.append(hits[0] if hits else None)
            last.append(hits[-1] if hits else None)
            st_ = None
            for k, s in enumerate(steps):
                if all(bits[t][i] for t in steps[k:]):
                    st_ = s
                    break
            stab.append(st_)
        out[rung] = {"y": y, "first": first, "last": last, "stab": stab,
                     "n_pos": int(sum(1 for v in y if v > 0)),
                     "counts_by_step": {int(s): int(sweep[s][rung]["correct"])
                                        for s in sweep}}
    return out


def rung_level_69(out: dict, floors: dict, *, rungs=None) -> dict:
    """`analyze_2g.rung_level`'s body with `bg.trained_steps(size)` /
    `bg.FINAL_STEP` replaced by 2h's own (same value, 143000, but read
    from `battery_2h` rather than the exp2g-only-bound global)."""
    steps = bh.trained_steps_69()
    rungs = tuple(rungs) if rungs is not None else tuple(out)
    res = {}
    for rung in rungs:
        c = out[rung]["counts_by_step"]
        clears = [s for s in steps
                  if st2d.binomial_bar(c[s], bt.N_ITEMS, floors[rung])["significant"]]
        final = bh.FINAL_STEP_69 in clears
        res[rung] = {"s_star": clears[0] if clears else None,
                     "clears": clears, "final_clears": final,
                     "transient_clears": ([] if final else clears)}
    return res


# ------------------------------------------------------------- primary

def primary_2h(pred: dict, out: dict, strata: dict, *, size_pred, rungs, n_perm=N_PERM,
              seed=st.PERM_SEED, n_boot=N_BOOT, rule="cv", y_key="y", keep=None) -> dict:
    """`analyze_2g.primary`'s body with the twin arm DROPPED (design
    §3.3: no twin/SURFACE terminal — the untrained sampled count is
    all-zero by construction, so a twin arm is vacuous, not silently
    dropped). Reuses `analyze_2g.cells_for` directly — it is a pure
    function of its (pred, out, strata) arguments, not bound to any
    exp2g-only global."""
    cells, thin = an2g.cells_for(pred, out, strata, rungs=rungs, size_pred=size_pred,
                                 mode="trained", rule=rule, y_key=y_key, keep=keep)
    if not cells:
        raise ValueError("primary_2h: no eligible rung")
    strat = st.perm_test(cells, n_perm=n_perm, seed=seed)
    raw_cells, _ = an2g.cells_for(pred, out, strata, rungs=rungs, size_pred=size_pred,
                                  mode="trained", rule=rule, one_stratum=True, y_key=y_key,
                                  keep=keep)
    raw = st.perm_test(raw_cells, n_perm=n_perm, seed=seed)
    per_rung = {}
    for c in cells:
        per_rung[c["rung"]] = {**strat["per_rung"][c["rung"]],
                               "ci": st.bootstrap_d(c["x"], c["y"], c["strata"],
                                                    n_boot=n_boot),
                               "raw_d": raw["per_rung"][c["rung"]]["d"]}
    return {"stratified": strat, "raw": raw, "pooled_d": st.pooled_d(cells),
            "per_rung": per_rung, "eligible": [c["rung"] for c in cells], "thin": thin,
            "size_pred": size_pred, "rule": rule, "y_key": y_key,
            "alpha": ALPHA, "t_bar": T_BAR}


def verdict_tree_2h(failures, prim) -> dict:
    if failures:
        return {"verdict": "INSUFFICIENT_DATA",
                "reason": f"{len(failures)} referent/loader failure(s): "
                          f"{list(failures)[:5]}"}
    T, p = prim["stratified"]["T"], prim["stratified"]["p"]
    if p < ALPHA and T >= T_BAR:
        return {"verdict": "CONFIRMED",
                "reason": f"T = {T:.4f} ≥ {T_BAR}, p = {p:.4g} < {ALPHA}"}
    notes = []
    if p < ALPHA and T < T_BAR:
        notes.append(f"detected below the effect bar (T = {T:.4f} < {T_BAR}, p = {p:.4g})")
    if T < 0:
        hi = prim["stratified"].get("n_perm", 0)
        p_inv = (1 + hi - prim["stratified"].get("n_ge", 0)) / (1 + hi) if hi else None
        notes.append(f"inverted (T = {T:.4f}; one-sided p for T_perm ≤ T_obs ≈ {p_inv})")
    return {"verdict": "NOT-CONFIRMED",
            "reason": (f"stratified p = {p:.4g}, T = {T:.4f}"
                       + ("; " + "; ".join(notes) if notes else ""))}


# ---------------------------------------------------------- helpers

def _scores_predictor(counts: dict, size: str, rungs) -> dict:
    """Wraps a {rung: [counts]} dict (from `battery_2h.sampler_counts`)
    into the {"cells": {rung: {size: {"trained": {"scores":...,
    "eval_rule": {"scores":...}}}}}} shape `analyze_2g.cells_for` /
    `predictor_2g.cell_scores` expect — no "untrained" key: 2h's
    primary never takes the twin branch (design §3.3)."""
    return {"cells": {r: {size: {"trained": {"scores": [float(c) for c in counts[r]],
                                             "eval_rule": {"scores": [float(c) for c in counts[r]]}}}}
                      for r in rungs}}


def _median_bucket(scores) -> list:
    arr = np.asarray(scores, dtype=np.float64)
    med = float(np.median(arr))
    return [int(v > med) for v in arr]


def _primary_core(sweep, floors, strata, *, n_perm, n_boot) -> tuple:
    """Outcomes → the rung-level table → the sampled predictor → the
    primary, as ONE unit so `run()` can put the whole computation behind
    a refusal (freeze F-1 / the 2d F-1 standard: the frozen verdict must
    deliver its own terminal from every tree it can be handed, including
    the ones where `primary_2h` finds no eligible rung or `perm_test`
    finds no informative pair). Order and arguments are unchanged from
    the inline block this replaces."""
    out = outcomes_69(sweep, rungs=tuple(bt.RUNGS))
    rl = rung_level_69(out, floors, rungs=tuple(bt.RUNGS))
    samp = bh.sampler_counts("1b", bh.R_69)
    sp = _scores_predictor(samp, "1b", bh.R_69)
    prim = primary_2h(sp, out, strata, size_pred="1b", rungs=bh.R_69, n_perm=n_perm,
                      n_boot=n_boot)
    return out, rl, samp, sp, prim


# ----------------------------------------------------------------- run

def _git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=bg.REPO,
                          capture_output=True, text=True).stdout.strip()


def run(root=EXP2H, *, write=False, n_perm=N_PERM, n_boot=N_BOOT, tag_exists=None,
        manifest_sha=CHECKPOINTS_2H_SHA256, referents_sha=REFERENTS_2H_SHA256,
        power_sha=POWER_2H_SHA256, out_path=None) -> dict:
    failures = []
    _, f = collect(bg.check_frozen_imports_2g, "upstream frozen imports")
    failures += f
    _, f = collect(bh.check_frozen_2h, "frozen 2g imports")
    failures += f
    prereg, f = collect(lambda: require_prereg_2h(tag_exists=tag_exists), "prereg tag")
    failures += f
    manifest, f = collect(lambda: bh.load_manifest_69(bh.CHECKPOINTS_PATH_69,
                                                       sha_pin=manifest_sha),
                          "checkpoint manifest")
    failures += f
    if referents_sha is not None:
        from experiments.exp2h import make_referents_2h as mkh
        mf, f = collect(lambda: mkh.check_referents(REFERENTS_PATH_2H, sha_pin=referents_sha),
                        "referent manifest")
        failures += f + (mf or [])
    power = None
    if power_sha is not None:
        power, f = collect(lambda: load_power_2h(sha_pin=power_sha), "power record")
        failures += f
    battery, f = collect(bg.load_battery, "battery")
    failures += f
    floors, f = collect(bg.load_floors, "2d floors")
    failures += f
    # collect_total: the 34 committed m4 records are pinned by the referent
    # manifest but parsed unpinned here, so a non-dict record would raise
    # AttributeError outside 2g's four-name tuple (freeze F-1).
    g, f = collect_total(lambda: bh.check_rung_set_69(floors) if floors is not None else
                         (_ for _ in ()).throw(ValueError("2d floors missing")), "rung set")
    failures += f
    gates = {"rung_set": g}
    lg, f = collect(lambda: lb.check_label_gates({r: battery[r] for r in bg.PREDICTOR_RUNGS})
                    if battery is not None else
                    (_ for _ in ()).throw(ValueError("battery missing")), "label gates")
    failures += f
    gates["labels"] = lg
    verify_fn, f = collect(a2d.load_verify, "verify criterion")
    failures += f
    pred, f = collect(lambda: pr.load_predictor(bg.predictor_path(bg.EXP2G),
                                                sha_pin=bh.PREDICTOR_2G_SHA),
                      "probe predictor")
    failures += f
    strata = sg.from_json(pred["strata"]) if pred else None
    if pred:
        gates["strata"] = sg.check_strata_pins(strata)

    # gate 1 and the sweep — every read here is of a file the RUNNER
    # writes, so every one goes through collect_total (freeze F-1).
    g1p = bh.gate1_path_2h(root)
    if bh.halt_marker_path_2h(root).exists():
        halted, f = collect_total(
            lambda: bh.halt_marker_path_2h(root).read_text().strip()[:200],
            f"gate 1 {bh.SIZE} halt marker")
        failures += f
        if not f:
            failures.append(f"gate 1 {bh.SIZE}: the runner halted ({halted})")
    if not g1p.is_file():
        failures.append(f"gate 1 {bh.SIZE}: record missing ({g1p})")
        gate1 = None
    else:
        gate1, f = collect_total(lambda: json.loads(g1p.read_text()),
                                 f"gate 1 {bh.SIZE} record")
        failures += f
        if gate1 is not None:
            gbad, f = collect_total(lambda: gate1_failures_69(gate1),
                                    f"gate 1 {bh.SIZE} re-derivation")
            failures += f + (gbad or [])
    seal_sha = bh.PREDICTOR_2G_SHA if pred else None
    _sweep_ready = bool(manifest) and battery is not None and verify_fn is not None and \
        seal_sha is not None
    sweep, f = collect_total(lambda: load_sweep_69(root, battery, verify_fn, manifest=manifest,
                                                   seal_sha=seal_sha) if _sweep_ready else
                             (_ for _ in ()).throw(ValueError("manifest, battery, verify "
                                                              "criterion or predictor missing")),
                             f"sweep {bh.SIZE}")
    failures += f

    # the primary, behind the same refusal (freeze F-1): "no eligible
    # rung" / "no informative pair" are ValueErrors on a tree the
    # analyzer can be handed, and must reach INSUFFICIENT_DATA, not raise.
    core = None
    if not failures:
        core, f = collect_total(lambda: _primary_core(sweep, floors, strata, n_perm=n_perm,
                                                      n_boot=n_boot), f"primary {bh.SIZE}")
        failures += f

    referents = {"failures": list(failures), "gates": gates,
                 "manifest_sha256": manifest_sha, "prereg": prereg,
                 "gate1": {k: v for k, v in (gate1 if isinstance(gate1, dict) else {}).items()
                           if k not in ("timing",)},
                 "power": power}
    if failures:
        tree = verdict_tree_2h(failures, None)
        v = {"verdict": tree["verdict"], "reason": tree["reason"],
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2H,
             "licensed_sentence": LICENSED["INSUFFICIENT_DATA"], "referents": referents,
             "primary": None, "secondaries": None, "git_sha": _git_sha()}
    else:
        out, rl, samp, sp, prim = core
        tree = verdict_tree_2h([], prim)

        # every secondary is non-gating (§6.4 style, carried from 2g) — a
        # failure here must not lose an already-computed verdict, so the
        # widened surface applies here too (freeze F-1).
        sec, sec_failures = {}, []

        def _sec(name, thunk):
            val, f = collect_total(thunk, name)
            if f:
                sec[name] = {"failed": f[0]}
                sec_failures.extend(f)
            else:
                sec[name] = val

        def _probe_competitor():
            r = primary_2h(pred, out, strata, size_pred=bg.PRIMARY_SIZE, rungs=bh.R_69,
                          n_perm=n_perm, n_boot=n_boot)
            r["tree"] = verdict_tree_2h([], r)
            return r
        _sec("probe_competitor", _probe_competitor)

        def _probe_beyond_sampler():
            # does the probe forecast beyond what the sampler already
            # conveys? composite strata = base stratum | sampler's own
            # binary bucket (v > 0) — 2g's own construction, direction
            # unchanged (it always conditioned on the SAMPLER's bucket)
            sx = {r: {"strata": [f"{s}|{int(c > 0)}"
                                 for s, c in zip(strata[r]["strata"], samp[r])]}
                  for r in bh.R_69}
            return primary_2h(pred, out, sx, size_pred=bg.PRIMARY_SIZE, rungs=bh.R_69,
                              n_perm=n_perm, n_boot=n_boot)
        _sec("probe_beyond_sampler", _probe_beyond_sampler)

        def _sampler_beyond_probe():
            # the mirror direction (2h's own — 2g never needed it since
            # the probe was 2g's primary): does the sampler forecast
            # beyond what the probe already conveys? composite strata =
            # base stratum | the probe's own median-split bucket (the
            # probe's scores are continuous log-probabilities with no
            # natural zero cut, unlike the sampler's raw count)
            sx = {}
            for r in bh.R_69:
                probe_scores = pr.cell_scores(pred, r, bg.PRIMARY_SIZE, "trained", rule="cv")
                buckets = _median_bucket(probe_scores)
                sx[r] = {"strata": [f"{s}|{b}" for s, b in zip(strata[r]["strata"], buckets)]}
            return primary_2h(sp, out, sx, size_pred="1b", rungs=bh.R_69, n_perm=n_perm,
                              n_boot=n_boot)
        _sec("sampler_beyond_probe", _sampler_beyond_probe)

        def _rep410m():
            samp410 = bh.sampler_counts("410m", bh.R_69)
            sp410 = _scores_predictor(samp410, "410m", bh.R_69)
            r = primary_2h(sp410, out, strata, size_pred="410m", rungs=bh.R_69, n_perm=n_perm,
                          n_boot=n_boot)
            r["tree"] = verdict_tree_2h([], r)
            return r
        _sec("replication_410m", _rep410m)

        def _first_correct_outcome():
            last_step = max(bh.trained_steps_69())
            first = {r: {"y": [0 if fc is None else (last_step + 1 - fc)
                               for fc in out[r]["first"]], "n_pos": out[r]["n_pos"]}
                     for r in bh.R_69}
            r = primary_2h(sp, first, strata, size_pred="1b", rungs=bh.R_69, n_perm=n_perm,
                          n_boot=n_boot)
            r["note"] = ("y = (last trained step + 1 − first-correct step), 0 for never; "
                        "monotone in earliness")
            return r
        _sec("first_correct_outcome", _first_correct_outcome)

        def _beyond_410m_1b():
            # design §5's one exploratory texture: 1b-beyond-410m,
            # partial concordance in strata of the 410m count — the
            # closest committed thing to a model-specific signal
            samp410 = bh.sampler_counts("410m", bh.R_69)
            sx = {r: {"strata": [f"{s}|{int(c > 0)}"
                                 for s, c in zip(strata[r]["strata"], samp410[r])]}
                  for r in bh.R_69}
            return primary_2h(sp, out, sx, size_pred="1b", rungs=bh.R_69, n_perm=n_perm,
                              n_boot=n_boot)
        _sec("beyond_410m_1b", _beyond_410m_1b)

        def _rung_level_sec():
            table = {r: {"s_star": rl[r]["s_star"],
                        "mean_sampler_rate_1b": float(np.mean(samp[r]) / 64.0),
                        "counts_by_step": out[r]["counts_by_step"]} for r in bh.R_69}
            xs = [table[r]["mean_sampler_rate_1b"] for r in bh.R_69]
            ys = [table[r]["s_star"] or 10 ** 9 for r in bh.R_69]
            from scipy.stats import spearmanr
            return {"note": "descriptive by design: eight rungs across five family blocks",
                   "table": table, "spearman_point": float(spearmanr(xs, ys).statistic)}
        _sec("rung_level", _rung_level_sec)

        _sec("flat_rungs", lambda: {r: {"s_star": rl[r]["s_star"],
                                        "transient_clears": rl[r]["transient_clears"],
                                        "counts_by_step": out[r]["counts_by_step"]}
                                    for r in bt.RUNGS if r not in bh.R_69})
        _sec("step0_counts", lambda: {r: out[r]["counts_by_step"].get(0) for r in bt.RUNGS})

        sec["failures"] = sec_failures
        v = {"verdict": tree["verdict"], "reason": tree["reason"],
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2H,
             "licensed_sentence": LICENSED[tree["verdict"]], "referents": referents,
             "primary": prim, "rung_level": rl, "secondaries": sec,
             "n_perm": n_perm, "git_sha": _git_sha()}
    if write:
        outp = Path(out_path or RESULTS / "verdict.json")
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(v, indent=1, default=_jsonable))
    return v


def _jsonable(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


if __name__ == "__main__":
    v = run(write="--write" in sys.argv)
    print(json.dumps({k: v[k] for k in ("verdict", "reason")}, indent=1))
    if v["primary"]:
        print(json.dumps({"T": v["primary"]["stratified"]["T"], "p": v["primary"]["stratified"]["p"],
                          "raw_p": v["primary"]["raw"]["p"],
                          "per_rung": {r: d["d"] for r, d in v["primary"]["per_rung"].items()}},
                         indent=1))
