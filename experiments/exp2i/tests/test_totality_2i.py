# experiments/exp2i/tests/test_totality_2i.py
"""Verdict-path totality (2h's F-1 lesson, carried forward): every tree
`analyze_2i.run()` can be handed — the runners' own halts and every
hand-editable shape short of them — must reach a FROZEN TERMINAL, never
an uncaught exception. Each case below RAISES before `collect_total`'s
closure if it is stripped; the control proves the same harness still
reaches SHARED on an untouched world."""
from __future__ import annotations

import json
import shutil

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2i import analyze_2i as an
from experiments.exp2i import battery_2i as bi
from experiments.exp2i.tests import full_shape as fs


@pytest.fixture(scope="module", autouse=True)
def _shrink_instrument_blobs_to_what_exists():
    subset = tuple(r for r in an.INSTRUMENT_BLOBS_2I if (bi.REPO / r).is_file())
    original = an.INSTRUMENT_BLOBS_2I
    an.INSTRUMENT_BLOBS_2I = subset
    yield
    an.INSTRUMENT_BLOBS_2I = original


@pytest.fixture(scope="module")
def base_world(tmp_path_factory):
    root = tmp_path_factory.mktemp("totality_base")
    seal = fs.write_world(root, mode="a_only")
    return root, seal


@pytest.fixture
def world(base_world, tmp_path):
    root, seal = base_world
    shutil.copytree(root / "results", tmp_path / "results")
    return tmp_path, seal


def _run(root, seal, **kw):
    kw.setdefault("n_perm", 30)
    kw.setdefault("n_boot", 10)
    return an.run(root=root, referents_sha=None, manifest_sha=bi.CHECKPOINTS_2I_SHA256,
                  **{**seal, **kw})


def _insufficient(root, seal, needle):
    v = _run(root, seal)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["verdict"]
    assert needle in v["reason"], v["reason"]
    assert v["tests"] is None and v["secondaries"] is None
    return v


# -------------------------------------------------------- predictor seal

def test_predictor_seal_missing(world):
    root, seal = world
    bi.predictor_seal_path(root).unlink()
    _insufficient(root, seal, "predictor seal content")


@pytest.mark.parametrize("payload", ["[]", '"x"', '{"sha256": "a", "tag": "t"'])
def test_predictor_seal_non_dict_or_torn(world, payload):
    root, seal = world
    bi.predictor_seal_path(root).write_text(payload)
    _insufficient(root, seal, "predictor seal content")


def test_predictor_seal_is_a_directory(world):
    root, seal = world
    p = bi.predictor_seal_path(root)
    p.unlink()
    p.mkdir()
    _insufficient(root, seal, "predictor seal content")


def test_predictor_seal_wrong_tag(world):
    root, seal = world
    p = bi.predictor_seal_path(root)
    rec = json.loads(p.read_text())
    rec["tag"] = "not-the-tag"
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "predictor seal content")


def test_predictor_seal_missing_key(world):
    root, seal = world
    p = bi.predictor_seal_path(root)
    rec = json.loads(p.read_text())
    del rec["counts"]
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "predictor seal content")


# ------------------------------------------------------ predictor draws (x_B)

def test_predictor_draws_file_missing(world):
    """x_B's own per-rung draws file — distinct from `predictor_2i.json`
    (the seal) and from the per-rung `.json` record: `sampler_counts_
    olmo` opens only the `.draws.jsonl.gz` file, and raises
    `FileNotFoundError` naming its path when it's gone."""
    root, seal = world
    p = bi.predictor_draws_path(root, "antonym")
    p.unlink()
    _insufficient(root, seal, str(p))


# -------------------------------------------------------------- rung set

def test_rung_set_missing(world):
    root, seal = world
    bi.rung_set_path(root).unlink()
    _insufficient(root, seal, "rung set")


@pytest.mark.parametrize("payload", ["[]", '{"R_OLMO": ['])
def test_rung_set_non_dict_or_torn(world, payload):
    root, seal = world
    bi.rung_set_path(root).write_text(payload)
    _insufficient(root, seal, "rung set")


def test_rung_set_is_a_directory(world):
    root, seal = world
    p = bi.rung_set_path(root)
    p.unlink()
    p.mkdir()
    _insufficient(root, seal, "rung set")


def test_rung_set_missing_key(world):
    root, seal = world
    p = bi.rung_set_path(root)
    rec = json.loads(p.read_text())
    del rec["per_rung"]
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "rung set")


def test_rung_set_r_cap_not_a_subset(world):
    root, seal = world
    p = bi.rung_set_path(root)
    rec = json.loads(p.read_text())
    rec["R_CAP"] = rec["R_CAP"] + ["clock24"]   # not one of the eleven
    rec["R_OLMO"] = rec["R_OLMO"] + ["clock24"]
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "rung set")


def test_rung_set_does_not_partition(world):
    root, seal = world
    p = bi.rung_set_path(root)
    rec = json.loads(p.read_text())
    rec["R_EXTRA"] = ["clock24"]   # not in R_OLMO -> no longer a partition
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "rung set")


# ----------------------------------------------------------- power record

def test_power_record_missing(world):
    root, seal = world
    bi.power_path(root).unlink()
    _insufficient(root, seal, "power record")


@pytest.mark.parametrize("payload", ["[]", '{"A": {'])
def test_power_record_non_dict_or_torn(world, payload):
    root, seal = world
    bi.power_path(root).write_text(payload)
    _insufficient(root, seal, "power record")


def test_power_record_is_a_directory(world):
    root, seal = world
    p = bi.power_path(root)
    p.unlink()
    p.mkdir()
    _insufficient(root, seal, "power record")


def test_power_record_missing_declared_status(world):
    root, seal = world
    p = bi.power_path(root)
    rec = json.loads(p.read_text())
    del rec["A"]["declared_status"]
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "power record")


def test_power_record_missing_declaration(world):
    root, seal = world
    p = bi.power_path(root)
    rec = json.loads(p.read_text())
    del rec["B"]["declaration"]
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "power record")


# ------------------------------------------------------- seal tag bindings

def test_predictor_seal_tag_missing(world):
    root, seal = world
    tag_exists = lambda t: t != bi.PREDICTOR_SEAL_TAG   # noqa: E731
    v = _run(root, {**seal, "tag_exists": tag_exists})
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("predictor seal" in f and "does not exist" in f
              for f in v["referents"]["failures"])


def test_predictor_seal_tag_drifted(world):
    root, seal = world
    blobs_bound = lambda tag, paths, repo_root=None: (  # noqa: E731
        ["drifted"] if tag == bi.PREDICTOR_SEAL_TAG else [])
    v = _run(root, {**seal, "blobs_bound": blobs_bound})
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("predictor seal" in f and "does not bind" in f
              for f in v["referents"]["failures"])


def test_endpoint_seal_tag_missing(world):
    root, seal = world
    tag_exists = lambda t: t != bi.ENDPOINT_SEAL_TAG   # noqa: E731
    v = _run(root, {**seal, "tag_exists": tag_exists})
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("endpoint seal" in f and "does not exist" in f
              for f in v["referents"]["failures"])


def test_endpoint_seal_tag_drifted(world):
    root, seal = world
    blobs_bound = lambda tag, paths, repo_root=None: (  # noqa: E731
        ["drifted"] if tag == bi.ENDPOINT_SEAL_TAG else [])
    v = _run(root, {**seal, "blobs_bound": blobs_bound})
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("endpoint seal" in f and "does not bind" in f
              for f in v["referents"]["failures"])


# ------------------------------------------------------- endpoint records

def test_stage1_final_record_missing(world):
    root, seal = world
    bi.endpoint_record_path(root, "stage1_final", "antonym").unlink()
    _insufficient(root, seal, "endpoint stage1_final")


def test_stage1_final_record_torn(world):
    root, seal = world
    bi.endpoint_record_path(root, "stage1_final", "antonym").write_text('{"rung": "a')
    _insufficient(root, seal, "endpoint stage1_final")


def test_stage1_final_record_is_a_directory(world):
    root, seal = world
    p = bi.endpoint_record_path(root, "stage1_final", "antonym")
    p.unlink()
    p.mkdir()
    _insufficient(root, seal, "endpoint stage1_final")


def test_main_record_missing(world):
    root, seal = world
    bi.endpoint_record_path(root, "main", "antonym").unlink()
    _insufficient(root, seal, "endpoint main")


def test_stage1_final_record_mutated_field_fails_reverification(world):
    root, seal = world
    p = bi.endpoint_record_path(root, "stage1_final", "antonym")
    rec = json.loads(p.read_text())
    rec["predictor_sha"] = "not-the-seal-sha"
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "endpoint stage1_final")


# -------------------------------------------------------------- gate 1

def test_gate1_missing(world):
    root, seal = world
    bi.gate1_path(root).unlink()
    _insufficient(root, seal, "gate 1 olmo7b: record missing")


@pytest.mark.parametrize("payload", ["[]", '{"rungs": ['])
def test_gate1_non_dict_or_torn(world, payload):
    # a bare list parses clean and fails inside gate1_failures_7b's
    # re-derivation (AttributeError: list has no .get); truncated JSON
    # fails at the load itself (JSONDecodeError) — different collect_
    # total labels, both correctly INSUFFICIENT_DATA, so the needle is
    # deliberately just "gate 1 olmo7b" to match either.
    root, seal = world
    bi.gate1_path(root).write_text(payload)
    _insufficient(root, seal, "gate 1 olmo7b")


def test_gate1_is_a_directory(world):
    root, seal = world
    p = bi.gate1_path(root)
    p.unlink()
    p.mkdir()
    _insufficient(root, seal, "gate 1 olmo7b: record missing")


def test_gate1_field_wrong_type(world):
    root, seal = world
    p = bi.gate1_path(root)
    rec = json.loads(p.read_text())
    rec["bit_diffs"] = [0, 0]
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "gate 1 olmo7b re-derivation")


def test_gate1_bit_diff_fires(world):
    root, seal = world
    p = bi.gate1_path(root)
    rec = json.loads(p.read_text())
    rec["bit_diffs"] = dict(rec["bit_diffs"])
    rec["bit_diffs"]["antonym"] = 3
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "bit diff")


def test_halt_marker_present(world):
    root, seal = world
    bi.halt_marker_path(root).write_text("gate 1 olmo7b: drift\n")
    _insufficient(root, seal, "the runner halted")


def test_halt_marker_is_a_directory(world):
    root, seal = world
    bi.halt_marker_path(root).mkdir(parents=True)
    _insufficient(root, seal, "halt marker")


# --------------------------------------------------- rung set vs endpoint

def test_rung_set_vs_endpoint_mismatch(world):
    root, seal = world
    p = bi.rung_set_path(root)
    rec = json.loads(p.read_text())
    rec["per_rung"] = {"antonym": {"k": 999999}}
    p.write_text(json.dumps(rec))
    # `_check_rung_set_vs_endpoint`'s own bad-strings carry a
    # "rung set olmo7b/<rung>:" prefix, not the collect_total label
    # ("rung set vs endpoint") — the label only appears if the check
    # itself RAISES, which this one does not (it returns a list, like
    # gate1_failures_7b).
    _insufficient(root, seal, "disagrees with the endpoint")


# -------------------------------------------------------------- the sweep

def test_sweep_record_missing(world):
    root, seal = world
    bi.record_path(root, bi.GRID_7B[0], "antonym").unlink()
    _insufficient(root, seal, "sweep olmo7b")


def test_sweep_record_torn(world):
    root, seal = world
    bi.record_path(root, bi.GRID_7B[0], "antonym").write_text('{"rung": "a')
    _insufficient(root, seal, "sweep olmo7b")


def test_checkpoint_record_missing(world):
    root, seal = world
    bi.checkpoint_record_path(root, bi.GRID_7B[0]).unlink()
    _insufficient(root, seal, "sweep olmo7b")


def test_sweep_dir_replaced_by_a_file(world):
    root, seal = world
    d = bi.sweep_dir(root)
    shutil.rmtree(d)
    d.write_text("not a directory")
    _insufficient(root, seal, "gate 1 olmo7b")


# ------------------------------------------------- the primary's own refusals

def _rewrite_r_cap(root, fn):
    bat = bg.load_battery(list(bi.STRATA_RUNGS))
    steps = bi.trained_steps_7b() + (bi.TWIN,)
    for step in steps:
        for r in bi.STRATA_RUNGS:
            p = bi.record_path(root, step, r)
            rec = json.loads(p.read_text())
            fn(rec, bat[r])
            rec["correct"] = sum(rec["bits"])
            p.write_text(json.dumps(rec))


def test_no_eligible_rung_is_a_terminal_not_a_crash(world):
    """Every R_CAP rung silent (n_pos 0 at every step): both tests'
    `primary_2i` raise 'no eligible rung' — behind the freeze's
    refusal it is INSUFFICIENT_DATA, not a crash."""
    root, seal = world

    def z(rec, cap):
        rec["continuations"] = [" zzz"] * len(rec["bits"])
        rec["bits"] = [0] * len(rec["bits"])
    _rewrite_r_cap(root, z)
    _insufficient(root, seal, "no eligible rung")


def test_no_informative_pair_is_a_terminal_not_a_crash(world):
    """y constant on every item of every R_CAP rung: `perm_test` raises
    'no informative pair' — likewise a terminal."""
    root, seal = world

    def one(rec, cap):
        rec["continuations"] = [f" {it['answer']}" for it in cap["eval_items"]]
        rec["bits"] = [1] * len(rec["bits"])
    _rewrite_r_cap(root, one)
    _insufficient(root, seal, "no informative pair")


# ---------------------------------------- totality: every collect_total site
#
# Review round-1 finding 4 extended the mutation harness's totality
# category from six hand-picked `collect_total` sites to all 27 in
# `run()`, generated programmatically. Thirteen survived on the first
# pass — not weak mutants, but sites this file had never driven to a
# real failure (either because the real committed tree never fails
# there, or because `_run`'s own `referents_sha=None` skips the
# referent-manifest block entirely). Each gets a dedicated failure
# here, via `monkeypatch` on the function `collect_total` wraps at
# that exact site, so the wrapper is the only thing standing between
# the raise and an uncaught exception out of `run()`.

def test_upstream_frozen_imports_check_failure_is_insufficient_data(world, monkeypatch):
    root, seal = world

    def boom():
        raise ValueError("boom frozen imports 2g")
    monkeypatch.setattr(bg, "check_frozen_imports_2g", boom)
    _insufficient(root, seal, "upstream frozen imports")


def test_check_frozen_2i_failure_is_insufficient_data(world, monkeypatch):
    root, seal = world

    def boom():
        raise ValueError("boom frozen 2i")
    monkeypatch.setattr(bi, "check_frozen_2i", boom)
    _insufficient(root, seal, "frozen imports")


def test_check_pythia_predictor_files_failure_is_insufficient_data(world, monkeypatch):
    root, seal = world

    def boom():
        raise ValueError("boom pythia predictor files")
    monkeypatch.setattr(bi, "check_pythia_predictor_files", boom)
    _insufficient(root, seal, "pythia predictor files")


def test_load_battery_failure_is_insufficient_data(world, monkeypatch):
    root, seal = world

    def boom(rungs=None):
        raise ValueError("boom battery")
    monkeypatch.setattr(bg, "load_battery", boom)
    _insufficient(root, seal, "battery")


def test_load_floors_failure_is_insufficient_data(world, monkeypatch):
    root, seal = world

    def boom():
        raise ValueError("boom floors")
    monkeypatch.setattr(bg, "load_floors", boom)
    _insufficient(root, seal, "2d floors")


def test_load_verify_failure_is_insufficient_data(world, monkeypatch):
    root, seal = world
    from experiments.exp2d import analyze_2d as a2d

    def boom():
        raise ValueError("boom verify")
    monkeypatch.setattr(a2d, "load_verify", boom)
    _insufficient(root, seal, "verify criterion")


def test_load_predictor_2g_failure_is_insufficient_data(world, monkeypatch):
    root, seal = world
    from experiments.exp2g import predictor_2g as pr

    def boom(path, sha_pin):
        raise ValueError("boom 2g predictor")
    monkeypatch.setattr(pr, "load_predictor", boom)
    _insufficient(root, seal, "2g predictor")


def test_strata_gate_failure_is_insufficient_data(world, monkeypatch):
    root, seal = world
    from experiments.exp2g import strata_2g as sg

    def boom(strata):
        raise ValueError("boom strata gate")
    monkeypatch.setattr(sg, "check_strata_pins", boom)
    _insufficient(root, seal, "strata gate")


def test_entry_stage1_lookup_failure_is_insufficient_data(world, monkeypatch):
    root, seal = world

    def boom(manifest, step):
        raise ValueError("boom entry_7b")
    monkeypatch.setattr(bi, "entry_7b", boom)
    _insufficient(root, seal, "7B endpoint entry")


def test_entry_main_lookup_failure_is_insufficient_data(world, monkeypatch):
    root, seal = world

    def boom(manifest, repo):
        raise ValueError("boom entry_main")
    monkeypatch.setattr(bi, "entry_main", boom)
    _insufficient(root, seal, "7B main entry")


def test_rung_set_vs_endpoint_check_failure_is_insufficient_data(world, monkeypatch):
    root, seal = world

    def boom(rung_set, stage1_final):
        raise ValueError("boom rung set vs endpoint")
    monkeypatch.setattr(an, "_check_rung_set_vs_endpoint", boom)
    _insufficient(root, seal, "rung set vs endpoint")


def test_referent_manifest_check_failure_is_insufficient_data(tmp_path, monkeypatch):
    """The `world`/`_run` fixtures always pass `referents_sha=None`
    (a synthetic world has no relation to the real committed
    `referents_2i.json`), so this site is unreachable through them —
    it needs a call with `referents_sha` set, which only happens on
    the real, empty tree here (every other refusal fires too; the
    point is that the referent one is named and nothing raises)."""
    from experiments.exp2i import make_referents_2i as mkr

    def boom(path, sha_pin):
        raise ValueError("boom referents")
    monkeypatch.setattr(mkr, "check_referents", boom)
    v = an.run(root=tmp_path, referents_sha="not-none",
              manifest_sha=bi.CHECKPOINTS_2I_SHA256, n_perm=10, n_boot=5)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["verdict"]
    assert "referent manifest" in v["reason"]


def test_secondary_thunk_failure_is_caught_not_raised(world, monkeypatch):
    """The generic `_sec(name, thunk)` helper's own `collect_total`
    call: breaking ONE secondary (`extra_rungs_raw`) must land it in
    `secondaries[name]["failed"]`, not raise out of `run()` —
    secondaries are non-gating, so the verdict itself is unaffected."""
    root, seal = world

    def boom(x_a, x_b, out, r_extra):
        raise ValueError("boom extra_rungs_raw")
    monkeypatch.setattr(an, "_extra_rungs_raw_2i", boom)
    v = _run(root, seal)
    assert v["verdict"] != "INSUFFICIENT_DATA", v["reason"]
    assert "boom extra_rungs_raw" in v["secondaries"]["extra_rungs_raw"]["failed"]


# ------------------------------------------------------------- control

def test_untouched_world_still_reaches_shared(world):
    root, seal = world
    v = _run(root, seal, n_perm=300, n_boot=20)
    assert v["verdict"] == "SHARED", v["reason"]
    assert v["tests"]["A"]["fires"] is True
    assert v["tests"]["B"]["fires"] is False
