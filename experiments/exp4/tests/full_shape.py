# experiments/exp4/tests/full_shape.py
"""Synthetic exp4 trees for world-testing `analyze_4.run()` (Task 4
brief, resolution 5). Written THROUGH the production persistence and
scalar functions (`collect_4.set_tables_4`, `pooled_sets_4`,
`overlap_table_4`, `align_scalars_4`, `write_load_4`,
`battery_4.load_record_4`, `gate1_rederive_4`, `gate1_record_4`) from
synthetic activations -- NOT through the stage runners (Task 3's
tests own those). The outcome side is REAL: every trajectory's t_clear
index, R_M, flat_M and transient_M come from `battery_4.load_outcome_4`
reading the committed exp2g/2i/2m/2n sweep trees already on disk, so a
world's "leads"/"partial"/"follows" texture is laid on top of the real
committed capability-emergence order, never invented.

Construction (engineering choices disclosed in PROGRESS.md; resolution
5 fixes the offsets, the width and which rungs carry a task signal,
not the mechanism that turns that into activation bytes): a MIXTURE
construction, not the additive Gaussian-blend of a naive reading of
"X = surface + task + noise" -- chosen because it gives a low-variance,
near-linear-in-probability response (validated numerically against
`metric_4`'s real kNN kernel before this file was written; see
PROGRESS.md's calibration table). One canonical per-rung vector V[r]
(shared by every key, every trajectory, every site and position -- the
literal "the structure is in the data" premise) plus, per (key,
moment, rung), a MATCH PROBABILITY p_union(t, r) combining a surface
component p_surf(t) = SURF_MAX * (s(t)-0.3)/0.7 (shared by every rung)
and, for r in the REAL R_M, a task component p_task(t, r) = TASK_MAX *
tau_r(t)**K_TASK_EXPONENT (tau_r as resolution 5 specifies exactly:
logistic((i-m_r)/0.75), m_r placed relative to the REAL t_clear index
by mode) via p_union = 1-(1-p_surf)(1-p_task); per site and per
position, independently, each of the 500 items is either a near-copy
of V[r] (probability p_union, its own small noise) or an independent
random vector (probability 1-p_union). References are built at
p_union == 1 (fixed, no time axis); twins at p_union == 0 (pure
noise); the ladder sizes at p_surf(size index) only, no task
component, per resolution 5."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np

EXP4 = Path(__file__).resolve().parents[1]
REPO = EXP4.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402

D = 16                    # resolution 5: d=16
EPS_MATCH = 0.2           # noise on a "matched" item, both sides
EPS_REF = 0.1             # references: cleaner (a released, fully trained model)
SURF_MAX = 0.15
TASK_MAX = 0.55
K_TASK_EXPONENT = 2.0
WIDTH = 0.75               # resolution 5's fixed logistic width

_OFFSET_BY_MODE = {"leads": -2.5, "partial": -0.3, "follows": 1.5,
                   "no_convergence": None, "undetermined": -0.3}


def _logistic(x):
    return 1.0 / (1.0 + np.exp(-x))


def _s_schedule(n_steps):
    """s(i) log-linear .3 -> 1 across the grid."""
    if n_steps == 1:
        return [1.0]
    return [0.3 * (1.0 / 0.3) ** (i / (n_steps - 1)) for i in range(n_steps)]


def _p_surf(s_val):
    return SURF_MAX * max(0.0, min(1.0, (s_val - 0.3) / 0.7))


def _p_task(tau_val):
    return TASK_MAX * (max(0.0, tau_val) ** K_TASK_EXPONENT)


def _seed_from(*parts) -> int:
    """A STABLE (PYTHONHASHSEED-independent) 31-bit seed from a tag."""
    s = "|".join(str(p) for p in parts)
    h = hashlib.sha256(s.encode()).digest()
    return int.from_bytes(h[:4], "big") % (2 ** 31 - 1)


class _World:
    def __init__(self, seed):
        self.seed = int(seed)
        self._V = {}

    def canonical(self, rung):
        if rung not in self._V:
            rng = np.random.default_rng(_seed_from("V", self.seed, rung))
            self._V[rung] = rng.standard_normal((battery_4.N_ITEMS, D))
        return self._V[rung]

    def moment_X(self, tag, rung, p_union, n_sites, *, eps=EPS_MATCH):
        """`[500, n_sites, 1, D]` float32 -- ONE position, not two:
        this synthetic generator does not model a question-end-
        specific signal, so the question-end and prompt-end positions
        would only ever get the same distribution; computing a single
        position and reusing it for both saves half of `set_tables_4`'s
        k-NN work per unit (disclosed in PROGRESS.md -- it matters at
        ~50-100 units x 34 rungs, k-NN measured at ~6 ms/call on this
        stack, not the design's ~1 ms estimate). A MIXTURE construction:
        per site, item i is a near-copy of `canonical(rung)[i]` with
        probability `p_union` (its own noise draw) or an independent
        random vector otherwise."""
        V = self.canonical(rung)
        seed = _seed_from("moment", self.seed, tag, rung, round(float(p_union), 8))
        rng = np.random.default_rng(seed)
        out = np.empty((battery_4.N_ITEMS, n_sites, 1, D), dtype=np.float32)
        for site in range(n_sites):
            mask = rng.random(battery_4.N_ITEMS) < p_union
            noise = rng.standard_normal((battery_4.N_ITEMS, D)) * eps
            vals = np.empty((battery_4.N_ITEMS, D))
            vals[mask] = V[mask] + noise[mask]
            n_un = int((~mask).sum())
            if n_un:
                vals[~mask] = rng.standard_normal((n_un, D))
            out[:, site, 0, :] = vals.astype(np.float32)
        return out


# ------------------------------------------------------- persistence glue

def _write_synthetic_unit(root, key_or_unit, *, family, n_hidden, sites, batch_size, refs,
                          ref_tables, committed_digest, X_provider, keep_activations,
                          compute_max_pairs=True) -> dict:
    """Mirrors `collect_4.process_model_4`'s per-rung loop, but takes
    an already-computed synthetic single-position `X` (shape [n,
    n_sites, 1, D]) from `X_provider(rung)` instead of calling
    `collect_rung_4` (no model, no torch); the SAME k-NN sets stand in
    for both the question-end and prompt-end positions (disclosed on
    `moment_X`), and the pooled variant is not computed at all (S7's
    pooled/global-bank sub-parts read as unavailable in a world, both
    non-gating)."""
    pairing_by_ref = {}
    for ref in (refs or ()):
        rt = ref_tables[ref]
        pairing_by_ref[ref] = collect_4._pairing_positions(sites, n_hidden, rt["sites"], rt["n_hidden"])

    sets_by_rung, overlaps_by_rung, attested_by_rung, activations_by_rung = {}, {}, {}, {}
    align_by_rung = {}
    d_hidden = None

    for rung in battery_4.RUNGS:
        X = X_provider(rung)                                       # [n, n_sites, 1, D]
        d_hidden = X.shape[-1]
        sets = collect_4.set_tables_4(X, k=metric_4.K_4)          # [n_sites, 1, n, k]
        P = X[:, :, 0, :]

        sets_by_rung[rung] = sets[:, 0, :, :]
        attested_by_rung[rung] = {"question_end": sets[:, 0, :, :]}
        activations_by_rung[rung] = {"X": X, "P": P}

        if refs:
            sets_m_pos = {"question_end": sets[:, 0, :, :], "prompt_end": sets[:, 0, :, :]}
            ref_data, ov = {}, {}
            for ref in refs:
                rt = ref_tables[ref]
                ref_data[ref] = {"sets_prompt_end": rt["sets"][rung],
                                 "sets_question_end": rt.get("sets_question_end", {}).get(rung),
                                 "sets_pooled": None,
                                 "activations_prompt_end": None, "sites_q": rt["sites"]}
                ov[ref] = collect_4.overlap_table_4(sets[:, 0, :, :], rt["sets"][rung], pairing_by_ref[ref])
            sites_m_arg = sites if compute_max_pairs else None
            align_by_rung[rung] = collect_4.align_scalars_4(sets_m_pos, None, None, ref_data,
                                                             pairing_by_ref, k=metric_4.K_4,
                                                             sites_m=sites_m_arg)
            overlaps_by_rung[rung] = ov
        else:
            align_by_rung[rung] = {}

    record_fields = dict(
        family=family,
        info={"tensor_digest": committed_digest or f"synthetic:{key_or_unit}", "commit": "synthetic",
             "revision": "synthetic", "repo": "synthetic", "kind": "from_config",
             "config_source": "synthetic", "n_hidden": n_hidden,
             "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}},
        sites=list(sites), d=int(d_hidden), render=battery_4.RENDER_4[family],
        batch_size=int(batch_size), refs=list(refs or ()),
        pairing={r: list(p) for r, p in pairing_by_ref.items()},
        committed_digest=committed_digest, seconds=0.01, stack={"synthetic": True},
        git_sha="0" * 40, prereg_tag=battery_4.PREREG_TAG_4)
    return collect_4.write_load_4(root, key_or_unit, record_fields=record_fields,
                                  sets_by_rung=sets_by_rung, overlaps_by_rung=overlaps_by_rung,
                                  attested_by_rung=attested_by_rung,
                                  activations_by_rung=activations_by_rung, global_sets=None,
                                  align=align_by_rung, keep_activations=keep_activations)


# ----------------------------------------------------------------- worlds

def _rung_sets(traj):
    outcome = battery_4.load_outcome_4(traj)
    return battery_4.rung_sets_4(outcome, bg.load_floors())


def build_world(root, mode: str, *, seed=0, stage: str = "full") -> dict:
    """Writes a synthetic exp4 tree under `root` for the given `mode`
    ("leads" / "partial" / "follows" / "no_convergence" /
    "undetermined"). `stage="reference_only"` writes just the 19
    reference-stage keys plus the four first units (no interior sweep,
    no gate1, no eligibility/power files) -- enough for
    `eligibility_table_4` alone. `stage="full"` additionally sweeps
    every grid point of every written trajectory, writes gate1 records,
    the eligibility record (via `analyze_4.eligibility_table_4` itself)
    and a power-record stub with the fields the analyzer requires."""
    root = Path(root)
    world = _World(seed)
    offset = _OFFSET_BY_MODE[mode]
    signal_div = 3.0 if mode == "undetermined" else 1.0

    rung_sets_by_traj = {traj: _rung_sets(traj) for traj in battery_4.TRAJECTORIES_4}

    # `run()`'s gating path (load_stage_tables_4 over ALL of
    # STAGE1_KEYS_4 + STAGE1_FIRST_UNITS_4, then load_sweep_tables_4
    # for EVERY trajectory) requires all four trajectories' reference-
    # stage and sweep data to be present and valid for a non-
    # INSUFFICIENT_DATA verdict -- so every mode writes all four
    # trajectories STRUCTURALLY. "undetermined" (design: "only the two
    # smallest R_M trajectories written") is realised by injecting the
    # mode's task signal into ONLY the two smallest-|R_M| trajectories
    # (`active_trajectories`) and forcing the other two to behave like
    # "no_convergence" (task ≡ 0 -- typically, but not guaranteed,
    # contributing no eligible cells: pure sampling noise can still
    # cross eligibility's 2-SE bar on a handful of cells by chance,
    # which is exactly how standalone "no_convergence" mode itself
    # reaches UNDETERMINED at some seeds and NO-CONVERGENCE at others
    # -- see PROGRESS.md "World verification") -- structurally
    # complete, behaviourally restricted. Callers that
    # want a smaller, faster tree for a stage='full' test should
    # shrink `battery_4.GRID_4`/`ENDPOINT_STEP_4`/`FIRST_STEP_4`/
    # `STAGE1_FIRST_UNITS_4` to a REAL-step subset before calling
    # `build_world` (test_full_shape_4.py's `_shrink_grids`) -- this
    # module reads those constants live, at call time, so a monkey-
    # patched shrink applies transparently.
    trajectories = battery_4.TRAJECTORIES_4
    if mode == "undetermined":
        active_trajectories = set(sorted(battery_4.TRAJECTORIES_4,
                                         key=lambda t: len(rung_sets_by_traj[t]["R"]))[:2])
    else:
        active_trajectories = set(battery_4.TRAJECTORIES_4)

    # ---------------------------------------------------------- references
    for ref in battery_4.REFERENCES_4:
        family = battery_4._FAMILY_OF_REF_4[ref]
        n_hidden = battery_4.N_HIDDEN_PIN_4[ref]
        sites = metric_4.sites_4(n_hidden)

        def provider(rung, ref=ref, sites=sites):
            return world.moment_X((ref,), rung, 1.0, len(sites), eps=EPS_REF)

        _write_synthetic_unit(root, ref, family=family, n_hidden=n_hidden, sites=sites,
                              batch_size=battery_4.BATCH_4[ref], refs=(), ref_tables={},
                              committed_digest=None, X_provider=provider, keep_activations=True)
    # `collect_4.cross_reference_4` is NOT called here: its CKA arm
    # reads each reference's stored `activations/<rung>.npz` assuming
    # the real two-position `[n, n_sites, 2, d]` layout
    # (`_load_activations_prompt_end` indexes position 1), which this
    # generator's single-position optimisation does not produce. S8's
    # "ceiling" (the references' mutual alignment) therefore reads as
    # empty in a world -- non-gating, disclosed in PROGRESS.md.
    ref_tables_cache = {ref: collect_4.load_ref_tables_4(root, (ref,))[ref]
                       for ref in battery_4.REFERENCES_4}

    # -------------------------------------------------------------- twins
    for traj in battery_4.TRAJECTORIES_4:
        key = battery_4.INIT_KEY_4[traj]
        n_hidden = battery_4.N_HIDDEN_PIN_4[key]
        sites = metric_4.sites_4(n_hidden)
        refs = battery_4.REFS_FOR_4[traj]
        ref_tables = {ref: ref_tables_cache[ref] for ref in refs}

        def provider(rung, key=key, sites=sites):
            return world.moment_X((key,), rung, 0.0, len(sites))

        _write_synthetic_unit(root, key, family=collect_4.family_of_traj_4(traj), n_hidden=n_hidden,
                              sites=sites, batch_size=battery_4.BATCH_4[key], refs=refs,
                              ref_tables=ref_tables, committed_digest=battery_4.committed_init_digest_4(traj),
                              X_provider=provider, keep_activations=True)

    # ------------------------------------------------------------- ladder
    non_pythia = collect_4.non_pythia_refs_4()
    ladder_refs = {ref: ref_tables_cache[ref] for ref in non_pythia}
    ladder_sizes = [s for s in battery_4.LADDER_SIZES_4 if s != "12b"]
    for idx, size in enumerate(ladder_sizes):
        key = f"ladder_pythia_{size}"
        n_hidden = battery_4.N_HIDDEN_PIN_4[key]
        sites = metric_4.sites_4(n_hidden)
        s_val = 0.3 + 0.7 * idx / max(1, len(ladder_sizes) - 1)

        def provider(rung, key=key, sites=sites, s_val=s_val):
            return world.moment_X((key,), rung, _p_surf(s_val), len(sites))

        _write_synthetic_unit(root, key, family="pythia", n_hidden=n_hidden, sites=sites,
                              batch_size=battery_4.BATCH_4[key], refs=non_pythia,
                              ref_tables=ladder_refs, committed_digest=None,
                              X_provider=provider, keep_activations=True)

    # --------------------------------------------------- the trajectories
    for traj in trajectories:
        rs = rung_sets_by_traj[traj]
        R_M = set(rs["R"])
        steps = list(battery_4.GRID_4[traj])
        n_steps = len(steps)
        s_sched = _s_schedule(n_steps)
        tclear_idx = {r: steps.index(rs["t_clear"][r]) for r in R_M}
        n_hidden = battery_4.N_HIDDEN_PIN_4[traj]
        sites = metric_4.sites_4(n_hidden)
        family = collect_4.family_of_traj_4(traj)
        refs = battery_4.REFS_FOR_4[traj]
        ref_tables = {ref: ref_tables_cache[ref] for ref in refs}

        traj_active = traj in active_trajectories

        def p_union_at(i, rung):
            p_s = _p_surf(s_sched[i]) / signal_div
            p_t = 0.0
            if mode != "no_convergence" and traj_active and rung in R_M:
                m_r = tclear_idx[rung] + offset
                tau = _logistic((i - m_r) / WIDTH)
                p_t = _p_task(tau) / signal_div
            return 1 - (1 - p_s) * (1 - p_t)

        which = steps if stage == "full" else [steps[0], steps[-1]]
        for i, step in enumerate(steps):
            if step not in which:
                continue

            def make_provider(i=i):
                def provider(rung):
                    return world.moment_X((traj, "step", i), rung, p_union_at(i, rung), len(sites))
                return provider

            provider = make_provider(i)
            X_cache = {rung: provider(rung) for rung in battery_4.RUNGS}

            def cached_provider(rung, X_cache=X_cache):
                return X_cache[rung]

            digest = battery_4.committed_step_digest_4(traj, step)
            batch_traj = battery_4.BATCH_4[traj]
            # I-5(b): S5(a)'s max-over-pairs sensitivity is only ever
            # real when at least one trajectory's SWEEP units (what
            # `_align_by_step_4` reads) were built with the full
            # site-pair cross product -- pythia_2.8b (tied for the
            # shortest grid) carries it; the other three trajectories'
            # sweep units stay `compute_max_pairs=False` (S5(a) reads
            # {"available": False} there, same as before I-5).
            cmp_max = (traj == "pythia_2.8b")
            if i == 0:
                _write_synthetic_unit(root, (traj, step), family=family, n_hidden=n_hidden,
                                      sites=sites, batch_size=batch_traj, refs=refs,
                                      ref_tables=ref_tables, committed_digest=digest,
                                      X_provider=cached_provider, keep_activations=False,
                                      compute_max_pairs=cmp_max)
            elif i == n_steps - 1:
                _write_synthetic_unit(root, f"endpoint_{traj}", family=family, n_hidden=n_hidden,
                                      sites=sites, batch_size=battery_4.BATCH_4[f"endpoint_{traj}"],
                                      refs=refs, ref_tables=ref_tables, committed_digest=digest,
                                      X_provider=cached_provider, keep_activations=True,
                                      compute_max_pairs=False)
                _write_synthetic_unit(root, (traj, step), family=family, n_hidden=n_hidden,
                                      sites=sites, batch_size=batch_traj, refs=refs,
                                      ref_tables=ref_tables, committed_digest=digest,
                                      X_provider=cached_provider, keep_activations=False,
                                      compute_max_pairs=cmp_max)
            else:
                _write_synthetic_unit(root, (traj, step), family=family, n_hidden=n_hidden,
                                      sites=sites, batch_size=batch_traj, refs=refs,
                                      ref_tables=ref_tables, committed_digest=digest,
                                      X_provider=cached_provider, keep_activations=False,
                                      compute_max_pairs=cmp_max)

        if stage == "full":
            _write_gate1(root, traj)

    if stage == "full":
        from experiments.exp4 import analyze_4 as an4
        table = an4.eligibility_table_4(root)
        battery_4.eligibility_path(root).parent.mkdir(parents=True, exist_ok=True)
        battery_4.eligibility_path(root).write_text(json.dumps(table, indent=1))
        _write_power_stub(root, table, trajectories)

    return {"mode": mode, "trajectories": list(trajectories), "seed": seed}


def _write_gate1(root, traj):
    g1 = battery_4.gate1_rederive_4(root, traj)
    endpoint_step = battery_4.ENDPOINT_STEP_4[traj]
    sweep_rec = json.loads((battery_4.unit_dir(root, traj, endpoint_step) / "_load.json").read_text())
    ref_rec = json.loads((battery_4.reference_dir(root, f"endpoint_{traj}") / "_load.json").read_text())
    rec = battery_4.gate1_record_4(traj=traj, sweep_rec=sweep_rec, reference_rec=ref_rec,
                                   sets_equal=g1["sets_equal"], activation_sha_equal=g1["activation_sha_equal"],
                                   attested_sha_equal=g1["attested_sha_equal"],
                                   digest_equal=g1["digest_equal"], seconds=0.05)
    battery_4.gate1_path(root, traj).parent.mkdir(parents=True, exist_ok=True)
    battery_4.gate1_path(root, traj).write_text(json.dumps(rec, indent=1))


def _write_power_stub(root, eligibility_table, trajectories):
    """Task 5's power tool is not built yet; a stub with the fields
    `analyze_4.run()` requires (resolution 5)."""
    cells = []
    for traj in trajectories:
        for rung, e in (eligibility_table.get(traj) or {}).get("R", {}).items():
            if e.get("eligible"):
                cells.append([traj, rung])
    rungs = sorted({r for _, r in cells})
    elig_sha = bg.sha256_file(battery_4.eligibility_path(root))
    power = {"cells": cells, "rungs": rungs, "eligibility_sha256": elig_sha,
            "declaration": "STUB (Task 5 not built)", "n_sim": 0, "arms": {}}
    battery_4.power_path(root).parent.mkdir(parents=True, exist_ok=True)
    battery_4.power_path(root).write_text(json.dumps(power, indent=1))


# ------------------------------------------------------------- corruptions

MISSING_ROUTES = (
    "unit", "short_unit", "halted", "gate1_endpoint_edited", "first_unit_absent",
    "eligibility_edited", "power_cells_edited", "reference_load_sha_edited", "sets_reindex",
    "gate0_twin_trained", "gate1_sweep_endpoint_edited",
)


def apply_missing(root, missing: str, *, traj="pythia_2.8b") -> str:
    """Mutates an already-built `stage='full'` world for one of
    `MISSING_ROUTES`. Returns a short string that should appear
    (verbatim-ish) among `run()`'s failure messages, for the test to
    grep for."""
    root = Path(root)
    steps = list(battery_4.GRID_4[traj])
    interior = steps[len(steps) // 2]

    if missing == "unit":
        shutil.rmtree(battery_4.unit_dir(root, traj, interior))
        return "unit missing"
    if missing == "short_unit":
        d = battery_4.unit_dir(root, traj, interior)
        (d / "sets" / f"{battery_4.RUNGS[0]}.npz").unlink()
        return "sets file missing"
    if missing == "halted":
        p = battery_4.halt_marker_path(root, traj)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("synthetic halt for a world test\n")
        return "halted"
    if missing == "gate1_endpoint_edited":
        # Edits the ENDPOINT's sets bytes (sha left stale on purpose).
        # `eligibility_table_4` reads this exact endpoint for every
        # rung (add4_mid included, as a flat-pool contributor), so the
        # refusal order (resolution 6: eligibility re-derivation comes
        # BEFORE the per-trajectory gate-1 check) means the FIRST
        # thing to disagree is the coarse whole-file sha integrity
        # check inside `load_record_failures_4` -- gate 1's own byte
        # comparison is never reached on this path, correctly, since
        # an untrustworthy endpoint is refused earlier. The needle
        # matches whichever of the two fires.
        d = battery_4.reference_dir(root, f"endpoint_{traj}")
        rung = battery_4.RUNGS[0]
        p = d / "sets" / f"{rung}.npz"
        with np.load(p) as z:
            arrays = dict(z)
        arrays["sets"] = arrays["sets"].copy()
        arrays["sets"][0, 0, 0] = (int(arrays["sets"][0, 0, 0]) + 1) % battery_4.N_ITEMS
        np.savez_compressed(p, **arrays)
        return "sha"
    if missing == "first_unit_absent":
        shutil.rmtree(battery_4.unit_dir(root, traj, steps[0]))
        return "unit missing"
    if missing == "eligibility_edited":
        p = battery_4.eligibility_path(root)
        obj = json.loads(p.read_text())
        traj0 = next(iter(obj))
        r0 = next(iter(obj[traj0]["R"]))
        obj[traj0]["R"][r0]["x_end"] = obj[traj0]["R"][r0]["x_end"] + 1.0
        p.write_text(json.dumps(obj, indent=1))
        return "eligibility record disagrees"
    if missing == "power_cells_edited":
        p = battery_4.power_path(root)
        obj = json.loads(p.read_text())
        obj["cells"] = [["not-a-real-traj", "not-a-real-rung"]]
        p.write_text(json.dumps(obj, indent=1))
        return "power record"
    if missing == "reference_load_sha_edited":
        p = battery_4.load_record_path(root, "ref_pythia_12b")
        obj = json.loads(p.read_text())
        first_rung = next(iter(obj["sets_sha256"]))
        obj["sets_sha256"][first_rung] = "0" * 64
        p.write_text(json.dumps(obj, indent=1))
        return "sha"
    if missing == "sets_reindex":
        # Edits the "sets" array only, leaving the SAME file's stored
        # `overlap_<ref>` arrays stale, and re-stamps this unit's own
        # `_load.json` sha to match the rewritten file -- so the
        # earlier whole-file integrity check passes and the
        # RE-DERIVED-vs-STORED overlap cross-check inside
        # `per_item_alignment_4` is what actually disagrees.
        d = battery_4.unit_dir(root, traj, steps[0])
        rung = battery_4.RUNGS[0]
        p = d / "sets" / f"{rung}.npz"
        with np.load(p) as z:
            arrays = dict(z)
        # A single re-indexed entry has only a ~k/(n-1) (~2%) chance of
        # actually changing that item's overlap COUNT against a
        # reference (whether the swapped-in neighbour happens to also
        # be a mutual one is close to chance), so `np.array_equal`
        # against the stale stored overlap can come back True purely
        # by luck. Shift EVERY neighbour index of EVERY item by +1
        # (mod N_ITEMS) instead -- the whole neighbour set changes for
        # (with overwhelming probability) every item, at every site.
        arrays["sets"] = (arrays["sets"].astype(np.int64) + 1) % battery_4.N_ITEMS
        arrays["sets"] = arrays["sets"].astype(np.uint16)
        np.savez_compressed(p, **arrays)
        rec_path = d / "_load.json"
        rec = json.loads(rec_path.read_text())
        rec["sets_sha256"][rung] = bg.sha256_file(p)
        rec_path.write_text(json.dumps(rec, indent=1))
        return "stored overlap disagrees"
    if missing == "gate0_twin_trained":
        # Replaces the twin's OWN "sets" bytes, rung by rung, with the
        # trained endpoint's (same shape: same n_hidden/sites, same
        # trajectory family) -- fraction_below becomes exactly 0 (the
        # twin no longer sees LESS of training than the endpoint; it
        # equals it), firing gate 0's own refusal. Every rung's sha is
        # re-stamped to match the copied bytes so the earlier coarse
        # whole-file integrity check passes and gate 0's own
        # fraction-below check is what actually disagrees.
        twin_key = battery_4.INIT_KEY_4[traj]
        twin_dir = battery_4.reference_dir(root, twin_key)
        endpoint_dir = battery_4.reference_dir(root, f"endpoint_{traj}")
        rec_path = twin_dir / "_load.json"
        rec = json.loads(rec_path.read_text())
        for rung in battery_4.RUNGS:
            src = endpoint_dir / "sets" / f"{rung}.npz"
            dst = twin_dir / "sets" / f"{rung}.npz"
            shutil.copyfile(src, dst)
            rec["sets_sha256"][rung] = bg.sha256_file(dst)
        rec_path.write_text(json.dumps(rec, indent=1))
        return "gate 0"
    if missing == "gate1_sweep_endpoint_edited":
        # I-6: edits the SWEEP's OWN copy of the endpoint unit's sets
        # bytes (NOT the reference stage's `endpoint_<traj>`, which
        # `gate1_endpoint_edited` above already covers) -- re-stamps
        # this unit's own sha so the coarse whole-file integrity check
        # passes, and eligibility re-derivation (which reads only the
        # REFERENCE's endpoint) is untouched and agrees with the
        # stored eligibility record, letting the per-trajectory loop
        # actually reach gate 1's OWN byte-level re-derivation
        # (`gate1_rederive_4`), which is what disagrees here.
        endpoint_step = battery_4.ENDPOINT_STEP_4[traj]
        d = battery_4.unit_dir(root, traj, endpoint_step)
        rung = battery_4.RUNGS[0]
        p = d / "sets" / f"{rung}.npz"
        with np.load(p) as z:
            arrays = dict(z)
        arrays["sets"] = (arrays["sets"].astype(np.int64) + 1) % battery_4.N_ITEMS
        arrays["sets"] = arrays["sets"].astype(np.uint16)
        np.savez_compressed(p, **arrays)
        rec_path = d / "_load.json"
        rec = json.loads(rec_path.read_text())
        rec["sets_sha256"][rung] = bg.sha256_file(p)
        rec_path.write_text(json.dumps(rec, indent=1))
        return "re-derived bytes disagree"
    raise ValueError(f"unknown missing route {missing!r}")
