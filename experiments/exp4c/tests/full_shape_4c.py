# experiments/exp4c/tests/full_shape_4c.py
"""Synthetic Exp 4c trees for world-testing `analyze_4c.run()` (Task 4
brief, step 1). Written THROUGH the production persistence
(`collect_4.set_tables_4`, `overlap_table_4`, `align_scalars_4`,
`write_load_4`, `battery_4c.gate1_rederive_4c`, `gate1_record_4c`)
from synthetic activations — never through the stage runner (Task 3's
tests own that). The OUTCOME side is REAL: every rung set, every
t_clear and every clear index comes from `battery_4c.load_outcome_4c`
reading 2h's and 2l's committed sweep trees, so a world's texture sits
on top of the real emergence order and never invents one.

No torch, no network, no model contact anywhere in this module.

Construction: Exp 4's own mixture generator (`exp4.tests.full_shape._World`
— one canonical per-rung vector V[r] shared by every key, and per
(key, moment, rung) a match probability `p_union` combining a surface
component every rung shares with a task component only some rungs
get). What differs per mode is WHERE the task component sits relative
to the task's own clear index c:

  replicates / type_general   rising rungs at m = c - 2.5 (up before t-)
  not_replicated              rising rungs at m = c + 1.5 (after the clear)
  type_bound                  non-arithmetic rising at c - 2.5, arithmetic at c + 1.5
  reversed                    rising rungs at c + 1.5 AND the FLAT pool given
                              its own early task component (m = 0.5)

`reversed` moves the FLAT pool rather than damping the rising rungs'
surface component, which is the brief's letter: pre-clear the surface
component is a few hundredths of a match probability, so scaling it
would put the whole contrast inside the k-NN sampling noise and the
world would reach `p_minus < .05` by luck or not at all. Raising the
flat pool instead puts the rising tasks' pre-clear growth below the
never-performing tasks' by construction, which is what REVERSED
means. Disclosed here and in PROGRESS.md."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np

EXP4C = Path(__file__).resolve().parents[1]
REPO = EXP4C.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402
from experiments.exp4.tests import full_shape as fs  # noqa: E402
from experiments.exp4c import battery_4c as bc  # noqa: E402

WORLD_N_SIM_4C = 40
WORLD_N_BOOT_4C = 200
WORLD_B_4C = 200
MODES_4C = ("replicates", "not_replicated", "reversed", "type_bound", "type_general")

# FREEZE F-4: the cache key. `build_world` used to key on (mode, seed)
# alone, so ANY edit to a module that writes into a world — the four
# below, the same set `mutation_check.WORLD_WRITING_PATHS_4C` names and
# the mutation harness bypasses the cache for — silently reused a world
# built by the previous version. The mutation harness had its own
# per-mutant workaround; an ORDINARY edit (a fix round, a freeze
# closure) had none, and the worlds run that is supposed to verify the
# closure would have re-measured the pre-closure build. The four
# modules' content now enters the key, so a stale world cannot be
# served: it is simply a cache miss.
WORLD_INPUT_MODULES_4C = (
    EXP4C / "battery_4c.py",
    EXP4C / "collect_4c.py",
    EXP4C / "power_4c.py",
    EXP4C / "tests" / "full_shape_4c.py",
)


def world_inputs_digest_4c() -> str:
    """A short digest of every module whose content decides what
    `_build_world_uncached` writes."""
    h = hashlib.sha256()
    for p in WORLD_INPUT_MODULES_4C:
        h.update(p.name.encode())
        h.update(b"\0")
        h.update(p.read_bytes() if p.is_file() else b"<absent>")
    return h.hexdigest()[:12]


INIT_P_UNION_4C = 0.02          # the real step 0: near-noise, well below the endpoint
LEAD_OFFSET_4C = -2.5           # m = c + offset: the task signal is up before t-
LAG_OFFSET_4C = 1.5             # m = c + offset: it arrives after the clear
REVERSED_FLAT_M_4C = 0.5        # the flat pool's own early task component

_EXP4_REFERENCES_4C = ("ref_pythia_12b", "ref_olmo2_7b", "ref_smollm3_3b", "ref_comma_7b")
_LADDER_KEY_4C = "ladder_pythia_6.9b"


def _offsets_for(mode, rung_type):
    """`m - c` for a rising rung of this type under this mode, or
    `None` when the mode gives it no task component at all."""
    if mode in ("replicates", "type_general"):
        return LEAD_OFFSET_4C
    if mode in ("not_replicated", "reversed"):
        return LAG_OFFSET_4C
    if mode == "type_bound":
        return LEAD_OFFSET_4C if rung_type != "arithmetic" else LAG_OFFSET_4C
    raise ValueError(f"unknown mode {mode!r}")


# ------------------------------------------------- persistence (4c's own)

def _write_synthetic_unit_4c(root, key_or_unit, *, family, n_hidden, sites, batch_size, refs,
                             ref_tables, committed_digest, X_provider) -> dict:
    """`exp4.tests.full_shape._write_synthetic_unit`'s body with 4c's
    three deltas: `render` and `prereg_tag` from `battery_4c`, and
    `keep_activations=False` (4c keeps no activation file — dial k
    dropped CKA, its only consumer). The set tables, the stored
    overlaps and the attested question-end tables are produced by the
    identical calls, so a unit written here and the Exp 4 reference
    written by exp4's own writer from the SAME moment are byte-equal —
    which is what gate 1 compares."""
    pairing_by_ref = {}
    for ref in (refs or ()):
        rt = ref_tables[ref]
        pairing_by_ref[ref] = collect_4._pairing_positions(sites, n_hidden, rt["sites"],
                                                           rt["n_hidden"])
    sets_by_rung, overlaps_by_rung, attested_by_rung, activations_by_rung = {}, {}, {}, {}
    align_by_rung = {}
    d_hidden = None
    for rung in battery_4.RUNGS:
        X = X_provider(rung)                                   # [n, n_sites, 1, D]
        d_hidden = X.shape[-1]
        sets = collect_4.set_tables_4(X, k=metric_4.K_4)       # [n_sites, 1, n, k]
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
                                 "sets_pooled": None, "activations_prompt_end": None,
                                 "sites_q": rt["sites"]}
                ov[ref] = collect_4.overlap_table_4(sets[:, 0, :, :], rt["sets"][rung],
                                                    pairing_by_ref[ref])
            align_by_rung[rung] = collect_4.align_scalars_4(sets_m_pos, None, None, ref_data,
                                                            pairing_by_ref, k=metric_4.K_4,
                                                            sites_m=None)
            overlaps_by_rung[rung] = ov
        else:
            align_by_rung[rung] = {}
    record_fields = dict(
        family=family,
        info={"tensor_digest": committed_digest, "commit": "synthetic",
              "revision": "synthetic", "repo": "synthetic", "kind": "candidate",
              "config_source": "synthetic", "n_hidden": n_hidden,
              "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}},
        sites=list(sites), d=int(d_hidden), render=bc.RENDER_4C[family],
        batch_size=int(batch_size), refs=list(refs or ()),
        pairing={r: list(p) for r, p in pairing_by_ref.items()},
        committed_digest=committed_digest, seconds=0.01, stack={"synthetic": True},
        git_sha="0" * 40, prereg_tag=bc.PREREG_TAG_4C)
    return collect_4.write_load_4(root, key_or_unit, record_fields=record_fields,
                                  sets_by_rung=sets_by_rung, overlaps_by_rung=overlaps_by_rung,
                                  attested_by_rung=attested_by_rung,
                                  activations_by_rung=activations_by_rung, global_sets=None,
                                  align=align_by_rung, keep_activations=False)


def _write_gate1_4c(root4c, root4, traj) -> dict:
    der = bc.gate1_rederive_4c(root4c, root4, traj)
    sweep_rec = json.loads((battery_4.unit_dir(root4c, traj, bc.ENDPOINT_STEP_4C[traj])
                            / "_load.json").read_text())
    ref_rec = json.loads((bc.gate1_reference_dir_4c(root4c, root4, traj)
                          / "_load.json").read_text())
    rec = bc.gate1_record_4c(traj=traj, sweep_rec=sweep_rec, reference_rec=ref_rec,
                             rederived=der, seconds=0.05)
    p = battery_4.gate1_path(root4c, traj)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1))
    return rec


def _write_power_record_4c(root4c, *, n_sim=WORLD_N_SIM_4C, seed=0) -> dict:
    """Task 5: the REAL `power_4c.compute` record, over the real (live,
    committed-pin) cell structure — `power_4c` is data-free, so a
    world's record is a genuine small-`n_sim` power record, not a
    stand-in. The worlds run `power_gate="full"`, so this record must
    reproduce byte-for-byte when the analyzer re-derives it, which it
    does trivially (same structure, same n_sim/seed)."""
    from experiments.exp4c import power_4c as pw4c
    structure = pw4c.cell_structure_4c()
    rec = pw4c.compute(structure, n_sim=n_sim, seed=seed)
    p = EXP4C / "results" / "power_4c.json" if root4c is None else \
        Path(root4c) / "results" / "power_4c.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1, sort_keys=True, allow_nan=False))
    return rec


# ----------------------------------------------------------------- worlds

def build_world(root4c, root4, mode: str, *, seed=0) -> dict:
    """Cache-aware entry point (Task 5 fix round 1b): if the
    `EXP4C_WORLD_CACHE` env var is set, a world for this exact
    `(mode, seed, world_inputs_digest_4c())` is built ONCE into
    `<cache>/<mode>_<seed>_<digest>/` and every later call for the SAME
    key copies from there instead of
    re-running `_build_world_uncached` (the expensive part — synthetic
    activations written through the real production persistence for
    every grid step of both real trajectories). Falls back to building
    directly, every time, when the env var is unset — the committed
    test suite's own behaviour is UNCHANGED without it. The cache
    directory is gitignored scratch, never committed, never read by
    any non-test code."""
    if mode not in MODES_4C:
        raise ValueError(f"unknown mode {mode!r}; one of {MODES_4C}")
    root4c, root4 = Path(root4c), Path(root4)
    cache_env = os.environ.get("EXP4C_WORLD_CACHE")
    if not cache_env:
        return _build_world_uncached(root4c, root4, mode, seed=seed)

    cache_dir = Path(cache_env) / f"{mode}_{seed}_{world_inputs_digest_4c()}"
    marker = cache_dir / "_BUILD_COMPLETE"
    if marker.is_file():
        shutil.copytree(cache_dir / "root4c", root4c)
        shutil.copytree(cache_dir / "root4", root4)
        return {"root4c": root4c, "root4": root4, "mode": mode, "seed": seed}

    result = _build_world_uncached(root4c, root4, mode, seed=seed)
    tmp_cache = cache_dir.with_name(cache_dir.name + f".building.{os.getpid()}")
    tmp_cache.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root4c, tmp_cache / "root4c")
    shutil.copytree(root4, tmp_cache / "root4")
    (tmp_cache / "_BUILD_COMPLETE").write_text("done\n")
    # Atomic-ish publish: another concurrent builder for the SAME
    # (mode, seed) would have raced the same rename; last one standing
    # wins, both had a correct build.
    if not marker.is_file():
        if cache_dir.exists():
            shutil.rmtree(cache_dir, ignore_errors=True)
        tmp_cache.rename(cache_dir)
    else:
        shutil.rmtree(tmp_cache, ignore_errors=True)
    return result


def _build_world_uncached(root4c, root4, mode: str, *, seed=0) -> dict:
    """Writes the Exp 4 reference-stage keys under `root4` and 4c's own
    41 units, two gate-1 records and the power stand-in under
    `root4c`."""
    world = fs._World(seed)

    # ---- Exp 4's four released references (p_union = 1, no refs of
    # their own) and the Pythia 6.9b gate-1 reference, through Exp 4's
    # OWN frozen writer.
    for ref in _EXP4_REFERENCES_4C:
        family = battery_4._FAMILY_OF_REF_4[ref]
        n_hidden = battery_4.N_HIDDEN_PIN_4[ref]
        sites = metric_4.sites_4(n_hidden)

        def provider(rung, ref=ref, sites=sites):
            return world.moment_X((ref,), rung, 1.0, len(sites), eps=fs.EPS_REF)

        fs._write_synthetic_unit(root4, ref, family=family, n_hidden=n_hidden, sites=sites,
                                 batch_size=battery_4.BATCH_4[ref], refs=(), ref_tables={},
                                 committed_digest=None, X_provider=provider,
                                 keep_activations=True, compute_max_pairs=False)
    ref_cache = {ref: collect_4.load_ref_tables_4(root4, (ref,))[ref]
                 for ref in _EXP4_REFERENCES_4C}

    rung_sets, clear_idx, schedules = {}, {}, {}
    for traj in bc.TRAJECTORIES_4C:
        pin = bc.RUNG_SET_PIN_4C[traj]
        rung_sets[traj] = {"R": set(pin["R"]), "flat": set(pin["flat"])}
        clear_idx[traj] = dict(bc.CLEAR_INDEX_PIN_4C[traj])
        schedules[traj] = fs._s_schedule(len(bc.GRID_4C[traj]))

    def p_union_at(traj, i, rung):
        p_s = fs._p_surf(schedules[traj][i])
        p_t = 0.0
        if rung in rung_sets[traj]["R"] and rung in clear_idx[traj]:
            off = _offsets_for(mode, bc.RUNG_TYPE_4C[rung])
            m = clear_idx[traj][rung] + off
            p_t = fs._p_task(fs._logistic((i - m) / fs.WIDTH))
        elif mode == "reversed" and rung in rung_sets[traj]["flat"]:
            p_t = fs._p_task(fs._logistic((i - REVERSED_FLAT_M_4C) / fs.WIDTH))
        return 1 - (1 - p_s) * (1 - p_t)

    # ---- the Pythia 6.9b gate-1 reference: Exp 4's own ladder table,
    # written from the SAME moment tag as 4c's 6.9b sweep endpoint, so
    # gate 1's byte comparison is a real one across two writers.
    ladder_n_hidden = battery_4.N_HIDDEN_PIN_4[_LADDER_KEY_4C]
    ladder_sites = metric_4.sites_4(ladder_n_hidden)
    ladder_refs = collect_4.non_pythia_refs_4()
    ladder_tag = ("pythia_6.9b", "step", len(bc.GRID_4C["pythia_6.9b"]) - 1)
    ladder_end_i = len(bc.GRID_4C["pythia_6.9b"]) - 1

    def ladder_provider(rung):
        return world.moment_X(ladder_tag, rung, p_union_at("pythia_6.9b", ladder_end_i, rung),
                              len(ladder_sites))

    fs._write_synthetic_unit(
        root4, _LADDER_KEY_4C, family="pythia", n_hidden=ladder_n_hidden, sites=ladder_sites,
        batch_size=battery_4.BATCH_4[_LADDER_KEY_4C], refs=ladder_refs,
        ref_tables={r: ref_cache[r] for r in ladder_refs},
        committed_digest=bc.committed_step_digest_4c("pythia_6.9b",
                                                     bc.ENDPOINT_STEP_4C["pythia_6.9b"]),
        X_provider=ladder_provider, keep_activations=False, compute_max_pairs=False)

    # ---- 4c's own units
    for traj in bc.TRAJECTORIES_4C:
        steps = list(bc.GRID_4C[traj])
        n_hidden = bc.N_HIDDEN_PIN_4C[traj]
        sites = metric_4.sites_4(n_hidden)
        family = bc.FAMILY_OF_TRAJ_4C[traj]
        refs = bc.REFS_FOR_4C[traj]
        ref_tables = {ref: ref_cache[ref] for ref in refs}

        def init_provider(rung, sites=sites, traj=traj):
            return world.moment_X((traj, "init"), rung, INIT_P_UNION_4C, len(sites))

        _write_synthetic_unit_4c(
            root4c, (traj, bc.INIT_STEP_4C), family=family, n_hidden=n_hidden, sites=sites,
            batch_size=bc.BATCH_4C[traj], refs=refs, ref_tables=ref_tables,
            committed_digest=bc.committed_step_digest_4c(traj, bc.INIT_STEP_4C),
            X_provider=init_provider)

        for i, step in enumerate(steps):
            tag = (traj, "step", i)

            def provider(rung, tag=tag, i=i, sites=sites, traj=traj):
                return world.moment_X(tag, rung, p_union_at(traj, i, rung), len(sites))

            digest = bc.committed_step_digest_4c(traj, step)
            _write_synthetic_unit_4c(root4c, (traj, step), family=family, n_hidden=n_hidden,
                                     sites=sites, batch_size=bc.BATCH_4C[traj], refs=refs,
                                     ref_tables=ref_tables, committed_digest=digest,
                                     X_provider=provider)
            # the 13B thin endpoint: the SAME moment as the sweep's own
            # endpoint unit, so gate 1's byte comparison is exact
            if traj == "olmo2_13b" and step == bc.ENDPOINT_STEP_4C[traj]:
                _write_synthetic_unit_4c(
                    root4c, bc.THIN_ENDPOINT_KEY_4C, family=family, n_hidden=n_hidden,
                    sites=sites, batch_size=bc.BATCH_4C[bc.THIN_ENDPOINT_KEY_4C], refs=refs,
                    ref_tables=ref_tables, committed_digest=digest, X_provider=provider)

        _write_gate1_4c(root4c, root4, traj)

    _write_power_record_4c(root4c)
    return {"root4c": root4c, "root4": root4, "mode": mode, "seed": seed}


# --------------------------------------------------------- run harness

def discovery_stub_4c(root4=None) -> dict:
    """The discovery gate's record, injected: `rank_4c.discovery_set_4c`
    reads Exp 4's committed 92-unit sweep tree, which a synthetic
    `root4` does not have. The pins themselves plus the invariance
    fields plus a 42-cell table S6 needs — every value is the design
    session's own, so `check_discovery_pins_4c` passes exactly as it
    would on the real tree."""
    rec = dict(rk_pin())
    rec["cells"] = _discovery_cells_stub_4c(rec)
    return rec


def rk_pin() -> dict:
    from experiments.exp4c import rank_4c as rk
    return {k: (dict(v) if isinstance(v, dict) else v) for k, v in rk.DISCOVERY_PIN_4C.items()}


def _discovery_cells_stub_4c(rec) -> list:
    """42 cells whose mean q is the pinned U exactly — S6 pools cell
    q's, and the stub must pool to the same number the real record
    would."""
    n = int(rec["n_cells"])
    return [{"traj": "discovery", "rung": f"cell{i}", "q": float(rec["U"])} for i in range(n)]


def world_run_kwargs_4c(**over) -> dict:
    """The TEST-ONLY injections every world run makes, each disclosed
    in `pins_active`: no real git tag, no real seal, no referent
    manifest and no import pin (Task 5 writes both), the discovery gate
    stubbed (a synthetic `root4` has no Exp 4 sweep tree), and
    `power_gate="full"` (Task 5's `power_4c` is data-free, so the
    world's own small-`n_sim` record reproduces byte for byte against
    the live cell structure exactly as the real record will)."""
    kw = dict(frozen_check=lambda: None,
              tag_exists=lambda t: True,
              blob_sha=lambda tag, rel: (bg.sha256_file(REPO / rel)
                                         if (REPO / rel).is_file() else None),
              blobs_bound=lambda tag, paths, repo_root=None: [],
              referents_sha=False, imports_pinned=False,
              discovery_check=discovery_stub_4c,
              power_gate="full", expected_n_sim=WORLD_N_SIM_4C,
              n_boot=WORLD_N_BOOT_4C, B=WORLD_B_4C)
    kw.update(over)
    return kw


def existing_instrument_blobs_4c() -> tuple:
    """`INSTRUMENT_BLOBS_4C` restricted to the files that exist —
    `power_4c.py` and `results/power_4c.json` arrive with Task 5, and
    `require_prereg_4c` refuses on a blob that is not on disk."""
    return tuple(rel for rel in bc.INSTRUMENT_BLOBS_4C if (REPO / rel).is_file())


def run_world(world, **over) -> dict:
    from experiments.exp4c import analyze_4c as an
    return an.run(root=world["root4c"], root4=world["root4"], **world_run_kwargs_4c(**over))


def copy_world(world, dst_dir) -> dict:
    dst_dir = Path(dst_dir)
    r4c, r4 = dst_dir / "root4c", dst_dir / "root4"
    shutil.copytree(world["root4c"], r4c)
    shutil.copytree(world["root4"], r4)
    return {"root4c": r4c, "root4": r4, "mode": world["mode"], "seed": world["seed"]}


# ------------------------------------------------------------ corruptions

MISSING_ROUTES_4C = (
    "thin_endpoint_missing", "gate1_missing", "gate1_sets_equal_false", "step0_missing",
    "short_unit", "sets_sha_off", "halted", "exp4_ref_record_tampered",
    "power_record_missing", "gate1_bytes_disagree",
)


def apply_missing_4c(world, route: str) -> str:
    """Mutates an already-built world for one of `MISSING_ROUTES_4C`.
    Returns a needle that must appear among `run()`'s failures."""
    root4c, root4 = Path(world["root4c"]), Path(world["root4"])
    traj = "pythia_6.9b"
    steps = list(bc.GRID_4C[traj])
    interior = steps[len(steps) // 2]

    if route == "thin_endpoint_missing":
        shutil.rmtree(battery_4.reference_dir(root4c, bc.THIN_ENDPOINT_KEY_4C))
        return "endpoint_olmo2_13b"
    if route == "gate1_missing":
        battery_4.gate1_path(root4c, traj).unlink()
        return "gate 1 pythia_6.9b: record missing"
    if route == "gate1_sets_equal_false":
        p = battery_4.gate1_path(root4c, traj)
        rec = json.loads(p.read_text())
        rec["sets_equal"][battery_4.RUNGS[0]] = False
        p.write_text(json.dumps(rec, indent=1))
        return "sets_equal is not True"
    if route == "step0_missing":
        shutil.rmtree(battery_4.unit_dir(root4c, traj, bc.INIT_STEP_4C))
        return "unit missing"
    if route == "short_unit":
        d = battery_4.unit_dir(root4c, traj, interior)
        rec_p = d / "_load.json"
        rec = json.loads(rec_p.read_text())
        rec["sets_sha256"].pop(battery_4.RUNGS[0])
        rec_p.write_text(json.dumps(rec, indent=1))
        return "unit short"
    if route == "sets_sha_off":
        d = battery_4.unit_dir(root4c, traj, interior)
        rec_p = d / "_load.json"
        rec = json.loads(rec_p.read_text())
        rec["sets_sha256"][battery_4.RUNGS[0]] = "0" * 64
        rec_p.write_text(json.dumps(rec, indent=1))
        return "sets sha != the recorded"
    if route == "halted":
        p = battery_4.halt_marker_path(root4c, "olmo2_13b")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("synthetic halt for a world test\n")
        return "halted"
    if route == "exp4_ref_record_tampered":
        p = battery_4.load_record_path(root4, "ref_comma_7b")
        rec = json.loads(p.read_text())
        rec["sets_sha256"][battery_4.RUNGS[0]] = "0" * 64
        p.write_text(json.dumps(rec, indent=1))
        return "sha256"
    if route == "power_record_missing":
        (root4c / "results" / "power_4c.json").unlink()
        return "power record missing"
    if route == "gate1_bytes_disagree":
        # The one route ONLY `gate1_rederive_4c`'s raw-byte comparison
        # catches. The sweep's OWN endpoint unit gets a different set
        # table for one rung, its stored `overlap_<ref>` arrays are
        # RECOMPUTED from the new table (so `alignment_series_4c`'s
        # stored-vs-re-derived cross-check agrees), and its own
        # `sets_sha256` is restamped (so the loader's whole-file
        # integrity check agrees). `gate1.json` still attests
        # `sets_equal` True for every rung, `attested_sha256` and
        # `tensor_digest` are untouched — every other gate passes, and
        # the endpoint's bytes simply are not the gate-1 reference's.
        d = battery_4.unit_dir(root4c, traj, bc.ENDPOINT_STEP_4C[traj])
        rung = battery_4.RUNGS[0]
        p = d / "sets" / f"{rung}.npz"
        with np.load(p) as z:
            arrays = dict(z)
        arrays["sets"] = ((arrays["sets"].astype(np.int64) + 1)
                          % battery_4.N_ITEMS).astype(np.uint16)
        rec_p = d / "_load.json"
        rec = json.loads(rec_p.read_text())
        ref_raw = collect_4.load_ref_tables_4(root4, bc.REFS_FOR_4C[traj])
        for ref, pairing in rec["pairing"].items():
            arrays[f"overlap_{ref}"] = collect_4.overlap_table_4(
                arrays["sets"], ref_raw[ref]["sets"][rung], pairing)
        np.savez_compressed(p, **arrays)
        rec["sets_sha256"][rung] = bg.sha256_file(p)
        rec_p.write_text(json.dumps(rec, indent=1))
        return "re-derived bytes disagree"
    raise ValueError(f"unknown route {route!r}")
