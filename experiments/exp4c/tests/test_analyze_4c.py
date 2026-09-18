# experiments/exp4c/tests/test_analyze_4c.py
"""Exp 4c's analyzer, unit level (Task 4 brief step 2, the fast half):
the pinned unit loader's refusals, gate 0 on hand-built site means,
`eligibility_4c` against Exp 4's own `eligibility_table_4` on the same
synthetic tables, the licence block's modifier noun, and `pins_active`.

No torch, no network, no model contact: every table here is a small
random `uint16` array written or held in memory."""
from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp4 import analyze_4 as a4
from experiments.exp4 import battery_4
from experiments.exp4 import collect_4
from experiments.exp4 import metric_4
from experiments.exp4b import battery_4b
from experiments.exp4c import analyze_4c as an
from experiments.exp4c import battery_4c as bc


# ------------------------------------------------------------- fixtures

def _sets(rng, n_sites, n=battery_4.N_ITEMS, k=metric_4.K_4):
    return rng.integers(0, n, size=(n_sites, n, k), dtype=np.uint16)


def _unit(rng, *, n_hidden, refs, n=battery_4.N_ITEMS):
    """An in-memory `_load_one_unit_4c`-shaped unit (no disk)."""
    sites = metric_4.sites_4(n_hidden)
    sets = {r: _sets(rng, len(sites), n=n) for r in bc.RUNGS}
    pairing = a4.expected_pairing_4(n_hidden, refs)
    rec = {"sites": list(sites), "n_hidden": n_hidden, "refs": list(refs),
           "pairing": {k_: list(v) for k_, v in pairing.items()}}
    return {"record": rec, "sets": sets, "overlaps": {}}


def _ref_tables(rng, refs, *, n=battery_4.N_ITEMS):
    return {ref: {r: _sets(rng, len(metric_4.sites_4(battery_4.N_HIDDEN_PIN_4[ref])), n=n)
                  for r in bc.RUNGS} for ref in refs}


def _write_unit_on_disk(tmp_path, key, *, n_hidden, refs, committed_digest, rng,
                        n=battery_4.N_ITEMS, prereg_tag=None, sites=None, pairing=None,
                        n_rungs=None):
    """A minimal on-disk unit `_load_one_unit_4c` can read — only the
    fields that loader actually pins."""
    d = battery_4.key_dir_4(tmp_path, key)
    (d / "sets").mkdir(parents=True, exist_ok=True)
    sites = list(metric_4.sites_4(n_hidden)) if sites is None else list(sites)
    rungs = list(bc.RUNGS)[:n_rungs] if n_rungs else list(bc.RUNGS)
    sets_sha = {}
    for rung in rungs:
        arrays = {"sets": _sets(rng, len(sites), n=n)}
        for ref in refs:
            arrays[f"overlap_{ref}"] = np.zeros((len(sites), n), dtype=np.uint8)
        p = d / "sets" / f"{rung}.npz"
        np.savez_compressed(p, **arrays)
        sets_sha[rung] = bg.sha256_file(p)
    if pairing is None:
        pairing = {k_: list(v) for k_, v in a4.expected_pairing_4(n_hidden, refs).items()}
    rec = {"key": str(key), "family": bc.FAMILY_OF_TRAJ_4C.get(
                key[0] if isinstance(key, tuple) else "olmo2_13b"),
           "render": "plain", "batch_size": bc.BATCH_4C[key[0] if isinstance(key, tuple) else key],
           "committed_digest": committed_digest, "tensor_digest": committed_digest,
           "refs": list(refs), "pairing": pairing, "sites": sites, "n_hidden": n_hidden,
           "prereg_tag": prereg_tag or bc.PREREG_TAG_4C,
           "commit": "x", "revision": "y", "repo": "z", "kind": "candidate",
           "config_source": "c", "loading_info": {"missing_keys": 0, "unexpected_keys": 0,
                                                  "mismatched_keys": 0},
           "sets_sha256": sets_sha, "attested_sha256": {r: "a" for r in rungs},
           "activation_sha256": {r: None for r in rungs}}
    (d / "_load.json").write_text(json.dumps(rec, indent=1))
    return d, rec


# --------------------------------------------------- _load_one_unit_4c

def _key_69():
    return ("pythia_6.9b", bc.GRID_4C["pythia_6.9b"][0])


def test_load_one_unit_refuses_the_exp4_tag(tmp_path):
    rng = np.random.default_rng(0)
    key = _key_69()
    _write_unit_on_disk(tmp_path, key, n_hidden=33, refs=bc.REFS_FOR_4C["pythia_6.9b"],
                        committed_digest=bc.committed_step_digest_4c(*key), rng=rng, n=12,
                        prereg_tag=battery_4.PREREG_TAG_4)
    with pytest.raises(ValueError, match="prereg_tag"):
        an._load_one_unit_4c(tmp_path, key)


def test_load_one_unit_refuses_a_wrong_pairing_key_set(tmp_path):
    rng = np.random.default_rng(1)
    key = _key_69()
    refs = bc.REFS_FOR_4C["pythia_6.9b"]
    full = {k_: list(v) for k_, v in a4.expected_pairing_4(33, refs).items()}
    short = {k_: v for k_, v in full.items() if k_ != refs[0]}
    _write_unit_on_disk(tmp_path, key, n_hidden=33, refs=refs,
                        committed_digest=bc.committed_step_digest_4c(*key), rng=rng, n=12,
                        pairing=short)
    with pytest.raises(ValueError, match="pairing keys"):
        an._load_one_unit_4c(tmp_path, key)


def test_load_one_unit_refuses_a_short_unit(tmp_path):
    rng = np.random.default_rng(2)
    key = _key_69()
    _write_unit_on_disk(tmp_path, key, n_hidden=33, refs=bc.REFS_FOR_4C["pythia_6.9b"],
                        committed_digest=bc.committed_step_digest_4c(*key), rng=rng, n=12,
                        n_rungs=33)
    with pytest.raises(ValueError, match="sets_sha256 covers|unit short"):
        an._load_one_unit_4c(tmp_path, key)


def test_load_one_unit_refuses_a_missing_unit(tmp_path):
    with pytest.raises(ValueError, match="unit missing"):
        an._load_one_unit_4c(tmp_path, _key_69())


# ---------------------------------------------------------------- gate 0

def test_gate0_4c_counts_cells_per_rung_site_reference_and_drops_site_0(monkeypatch):
    """Hand-built site means: the twin below the endpoint at every
    kept site of every (rung, reference) gives fraction_below 1.0, and
    the excluded site 0 is counted in `n_cells_excluded`, never in
    `n_cells`."""
    refs = bc.REFS_FOR_4C["olmo2_13b"]
    n_hidden = 41
    sites = metric_4.sites_4(n_hidden)
    rec = {"sites": list(sites), "n_hidden": n_hidden, "refs": list(refs),
           "pairing": {r: [0] * len(sites) for r in refs}}
    twin = {"record": rec, "sets": {}, "overlaps": {}}
    end = {"record": rec, "sets": {}, "overlaps": {}}

    lo = {r: {ref: np.full(len(sites), 0.10) for ref in refs} for r in bc.RUNGS}
    hi = {r: {ref: np.full(len(sites), 0.30) for ref in refs} for r in bc.RUNGS}
    # site 0 inverted: the degenerate constant-token site, dropped
    for r in bc.RUNGS:
        for ref in refs:
            lo[r][ref] = lo[r][ref].copy(); lo[r][ref][0] = 1.0
            hi[r][ref] = hi[r][ref].copy(); hi[r][ref][0] = 1.0

    calls = {"n": 0}

    def fake_site_means(tables, ref_tables, pairing_by_ref):
        calls["n"] += 1
        return lo if calls["n"] == 1 else hi

    monkeypatch.setattr(a4, "_gate0_site_means_4", fake_site_means)
    g = an.gate0_4c(None, "olmo2_13b", {}, twin, end)
    assert g["pass"] is True
    assert g["fraction_below"] == 1.0
    assert g["n_cells"] == len(bc.RUNGS) * (len(sites) - 1) * len(refs)
    assert g["n_cells_excluded"] == len(bc.RUNGS) * len(refs)
    assert g["excluded_sites"] == [0]
    assert set(g["per_reference"]) == set(refs)


def test_gate0_4c_fails_below_the_bar(monkeypatch):
    refs = ("ref_comma_7b",)
    n_hidden = 33
    sites = metric_4.sites_4(n_hidden)
    rec = {"sites": list(sites), "n_hidden": n_hidden, "refs": list(refs),
           "pairing": {r: [0] * len(sites) for r in refs}}
    unit = {"record": rec, "sets": {}, "overlaps": {}}
    same = {r: {ref: np.full(len(sites), 0.2) for ref in refs} for r in bc.RUNGS}
    monkeypatch.setattr(a4, "_gate0_site_means_4", lambda *a_, **k_: same)
    g = an.gate0_4c(None, "pythia_6.9b", {}, unit, unit)
    assert g["pass"] is False and g["fraction_below"] == 0.0


# ----------------------------------------------------------- eligibility

def test_eligibility_4c_equals_exp4s_eligibility_table_on_the_same_tables(monkeypatch):
    """`eligibility_4c` IS `analyze_4.eligibility_table_4`'s per-run
    body. Proved by running BOTH over the identical synthetic tables:
    Exp 4's function with its trajectory table monkeypatched to this
    one run and its loaders redirected at the same in-memory units,
    4c's with those units passed as arguments. Equality to the float,
    not a tolerance.

    Chosen over a hand-computed fixture because the quantity under
    test is not the formula but the CLAIM that this is Exp 4's own
    instrument (S4 is the continuity arm): a hand fixture would prove
    4c's arithmetic and say nothing about the identity."""
    traj = "pythia_6.9b"
    refs = bc.REFS_FOR_4C[traj][:1]
    rng = np.random.default_rng(7)
    steps = [1000, 2000, 3000]
    unit_t1 = _unit(rng, n_hidden=33, refs=refs)
    unit_end = _unit(rng, n_hidden=33, refs=refs)
    ref_tables = _ref_tables(rng, refs)

    R = ["antonym", "arith_next"]
    flat = ["mod13", "mod17", "base7"]
    rs = {"R": R, "flat": flat, "transient": [], "t_clear": {"antonym": 3000, "arith_next": 3000},
          "endpoint_step": 3000}

    monkeypatch.setattr(battery_4, "TRAJECTORIES_4", (traj,))
    monkeypatch.setattr(battery_4, "GRID_4", {traj: tuple(steps)})
    monkeypatch.setattr(bc, "GRID_4C", {traj: tuple(steps)})
    monkeypatch.setattr(battery_4, "REFS_FOR_4", {traj: refs})
    monkeypatch.setattr(battery_4, "load_outcome_4", lambda t, battery=None: {"steps": steps})
    monkeypatch.setattr(battery_4, "rung_sets_4", lambda oc, floors: rs)
    monkeypatch.setattr(bt, "load_battery", lambda: {})
    monkeypatch.setattr(bg, "load_floors", lambda: {})
    monkeypatch.setattr(collect_4, "load_ref_tables_4",
                        lambda root, keys: {r: {"sets": ref_tables[r]} for r in keys})

    def fake_load(root, key):
        return unit_t1 if isinstance(key, tuple) else unit_end
    monkeypatch.setattr(a4, "_load_one_unit_4", fake_load)

    want = a4.eligibility_table_4("ignored", n_boot=50, seed=0)[traj]
    got = an.eligibility_4c("ignored", traj, ref_tables, unit_t1, unit_end, rs,
                            n_boot=50, seed=0)
    assert json.dumps(got, sort_keys=True) == json.dumps(want, sort_keys=True)


# ------------------------------------------------------------ S4's design

def test_design_4c_agrees_with_real_design_4b_on_exp4_cells():
    """`_design_4c` reproduces `battery_4b.real_design_4b`'s rule. The
    frozen function cannot be called on 4c's own cells — it keys its
    output dict on `battery_4.TRAJECTORIES_4` and then indexes it by
    each cell's `traj`, so a `pythia_6.9b` cell raises `KeyError` —
    so the rule is proved on cells it CAN take."""
    cells = [{"traj": "olmo2_7b", "rung": "antonym", "t_clear_index": 5},
             {"traj": "olmo2_7b", "rung": "add_base8", "t_clear_index": 3},
             {"traj": "comma_7b", "rung": "odd6", "t_clear_index": 4}]
    want = battery_4b.real_design_4b(cells)
    got = _design_over(an, cells, battery_4.TRAJECTORIES_4)
    assert got == want

    with pytest.raises(KeyError):
        battery_4b.real_design_4b([{"traj": "pythia_6.9b", "rung": "antonym",
                                    "t_clear_index": 6}])


def _design_over(mod, cells, trajectories):
    """`_design_4c` with its trajectory table swapped for Exp 4's, so
    the two functions are compared on the same keys."""
    import unittest.mock as um
    with um.patch.object(mod.bc, "TRAJECTORIES_4C", tuple(trajectories)):
        return mod._design_4c(cells)


# -------------------------------------------------------- licence block

@pytest.mark.parametrize("modifier", ["TYPE-GENERAL", "TYPE-BOUND", "NEITHER"])
def test_licence_block_substitutes_the_modifier_noun(modifier):
    lic = an.licence_block_4c("REPLICATES", {"modifier": modifier},
                              {"bounded": False, "alpha_at_bar": 0.001, "deciding_bar": 0.01},
                              {"reversed": False}, None)
    assert lic["modifier"] == modifier
    assert an.MODIFIER_NOUN_4C[modifier] in lic["sentence"]
    assert lic["sentence"].startswith("on two training runs nobody had read")
    assert an.KNOWN_OUTCOME_CAVEAT_4C in lic["sentence"]


def test_licence_block_adds_the_bounded_and_reversed_sentences():
    lic = an.licence_block_4c("NOT-REPLICATED", {"modifier": "NEITHER"},
                              {"bounded": True, "alpha_at_bar": 0.2, "deciding_bar": 0.05},
                              {"reversed": True}, None)
    assert lic["bounded"] is True and lic["reversed"] is True
    assert an.BOUNDED_SENTENCE_4C.split("(")[0].strip() in lic["sentence"]
    assert "below" in lic["sentence"]
    # NOT-REPLICATED with no power record names the missing record
    assert "power record" in lic["sentence"]


def test_licence_block_quotes_the_power_record_when_present():
    lic = an.licence_block_4c("NOT-REPLICATED", {"modifier": "NEITHER"},
                              {"bounded": False, "alpha_at_bar": 0.01, "deciding_bar": 0.05},
                              {"reversed": False},
                              {"declaration": "DECLARED UNDERPOWERED IN ADVANCE",
                               "blind_region": "any type-bound effect"})
    assert "DECLARED UNDERPOWERED IN ADVANCE" in lic["sentence"]
    assert "any type-bound effect" in lic["sentence"]


def test_insufficient_data_licence_is_a_refusal():
    lic = an.licence_block_4c("INSUFFICIENT_DATA", None, None, None, None)
    assert lic["modifier"] is None
    assert lic["sentence"].startswith("no licence")


# ------------------------------------------------------------ pins_active

def test_pins_active_records_every_injection(tmp_path):
    v = an.run(root=tmp_path, root4=tmp_path / "root4", frozen_check=lambda: None,
               tag_exists=lambda t: True, blob_sha=lambda tag, rel: None,
               blobs_bound=lambda *a_, **k_: [], referents_sha=False, imports_pinned=False,
               discovery_check=lambda root4=None: dict(an.rk.DISCOVERY_PIN_4C),
               power_gate="skip", n_boot=5, B=5)
    pa = v["pins_active"]
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert pa["frozen_modules"] is False and pa["prereg_binding"] is False
    assert pa["seal_binding"] is False and pa["discovery_gate"] is False
    assert pa["import_surface"] is False and pa["referent_manifest"] is False
    assert pa["power_gate"] == "skip" and pa["power_reproduced"] is False
    assert pa["threads_pinned"] is True
    assert isinstance(pa["threads_pinned_before_numpy"], bool)
    json.dumps(v, allow_nan=False)


def test_the_design_session_pins_are_what_the_gate_compares():
    """A discovery record one ulp off `DISCOVERY_PIN_4C` is a failure,
    not a rounding tolerance (the known-answer gate, design §3.7(1))."""
    rec = dict(an.rk.DISCOVERY_PIN_4C)
    rec["U"] = rec["U"] + 1e-12
    assert an.rk.check_discovery_pins_4c(rec)
