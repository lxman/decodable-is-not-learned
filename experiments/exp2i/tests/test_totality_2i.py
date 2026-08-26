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

# I-4 / Ruling 18: `primary_2i` (== `an2h.primary_2h`) raising 'no
# eligible rung' (every candidate rung n_pos-thin, inside `cells_for`)
# or `stats_2g.perm_test` raising 'no informative pair' for one
# specific rung is no longer routed to `collect_total`'s 'primary
# olmo7b' site at all — `_run_test` catches both INSIDE itself and
# returns an undefined (fires=False, named) result, so the OTHER
# test's real result still stands and the tree reaches a real world,
# not INSUFFICIENT_DATA. Driven directly against `an.primary_2i`
# (the same object `_run_test` calls, `an.primary_2i is an2h.
# primary_2h`) rather than by engineering a battery/floor combination
# that is simultaneously floor-clearing (in R_CAP) and n_pos-thin — I-1
# makes that combination impossible for the eleven real STRATA_RUNGS
# floors (a rung that clears a 15-25% floor at n=500 already has far
# more than `bg.ELIGIBILITY_MIN_POS` positive items).

def test_no_eligible_rung_is_undefined_not_a_crash(world, monkeypatch):
    """Every rung `primary_2i` is offered comes back thin (n_pos below
    the eligibility floor): BOTH tests land on 'undefined: no eligible
    rung', fires=False, verdict NEITHER — a terminal, not a crash."""
    root, seal = world

    def boom(*a, **kw):
        raise ValueError("primary_2h: no eligible rung")
    monkeypatch.setattr(an, "primary_2i", boom)
    v = _run(root, seal)
    assert v["verdict"] == "NEITHER", v["reason"]
    assert v["tests"]["A"]["named_inside"] == "undefined: no eligible rung"
    assert v["tests"]["B"]["named_inside"] == "undefined: no eligible rung"
    assert an.DISCLOSURE_UNDEFINED_2I["A"] in v["reason"]
    assert an.DISCLOSURE_UNDEFINED_2I["B"] in v["reason"]
    assert an.DISCLOSURE_UNDEFINED_2I["A"] in v["licensed_sentence"]
    assert an.DISCLOSURE_UNDEFINED_2I["B"] in v["licensed_sentence"]


def test_no_informative_pair_drops_the_rung_and_retries(world, monkeypatch):
    """`stats_2g.perm_test`'s 'no informative pair' for exactly the
    FIRST call `primary_2i` receives carrying the full eleven-rung
    R_CAP (Test A's own first attempt — `_outcomes_and_tests_2i` calls
    A before B, long before any of `run()`'s several OTHER `_run_test`
    secondaries also reach `primary_2i` with their own eleven- or
    ten-rung calls, so a plain call-INDEX assertion is not robust
    against those; a one-shot 'fail on the first eleven-rung call'
    latch is): `_run_test` drops the named rung and retries with the
    reduced ten — and here the real 2h machinery takes over for that
    retry and every later call, proving the retry genuinely reaches a
    live result, not merely that the exception was swallowed. Test B
    is untouched (the latch has already fired by the time B's own
    first call arrives) and so carries no dropped rung at all."""
    root, seal = world
    from experiments.exp2h import analyze_2h as an2h
    real = an2h.primary_2h
    state = {"fired": False, "first_rung": None, "retry_rungs": None}
    n_cap = len(bi.STRATA_RUNGS)

    def spy(pred, out, strata, *, size_pred, rungs, **kw):
        if not state["fired"] and len(rungs) == n_cap:
            state["fired"] = True
            state["first_rung"] = rungs[0]
            raise ValueError(f"perm_test: rung {rungs[0]} has no informative "
                             f"pair — not eligible")
        if (state["fired"] and state["retry_rungs"] is None
                and len(rungs) == n_cap - 1):
            state["retry_rungs"] = tuple(rungs)
        return real(pred, out, strata, size_pred=size_pred, rungs=rungs, **kw)
    monkeypatch.setattr(an, "primary_2i", spy)
    v = _run(root, seal, n_perm=300, n_boot=20)
    assert v["verdict"] == "SHARED", v["reason"]
    assert state["fired"] is True
    assert set(state["retry_rungs"]) == set(bi.STRATA_RUNGS) - {state["first_rung"]}
    assert v["tests"]["A"]["fires"] is True
    assert v["tests"]["A"]["dropped_degenerate"] == [state["first_rung"]]
    assert v["tests"]["B"]["dropped_degenerate"] == []


def test_rung_set_derivation_mismatch_hand_edited_r_cap(world):
    """I-1: R_CAP must be RE-DERIVABLE from the endpoint's own correct
    counts + the real floors, not merely internally consistent (a
    subset of the eleven, partitioning R_OLMO with R_EXTRA — both of
    which `_load_rung_set` already checks). Moving one rung from R_CAP
    to R_EXTRA by hand keeps it a valid partition and a valid subset,
    so only the re-derivation catches it."""
    root, seal = world
    p = bi.rung_set_path(root)
    rec = json.loads(p.read_text())
    moved = rec["R_CAP"][0]
    rec["R_CAP"] = rec["R_CAP"][1:]
    rec["R_EXTRA"] = rec["R_EXTRA"] + [moved]
    p.write_text(json.dumps(rec))
    v = _insufficient(root, seal, "rung set re-derivation")
    assert any(moved in f for f in v["referents"]["failures"])


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
    """`predictor_2g.load_predictor` ALSO calls `sg.check_strata_pins`
    internally as part of its OWN validation (`predictor_2g.py`,
    load_predictor's own body) — a bare monkeypatch breaks THAT call
    first, so `pred2g`/`strata` come back None and the `if strata is
    not None:` block (this site's actual home) is skipped entirely,
    never reached regardless of whether the site is mutated. A
    counting wrapper lets the FIRST call (load_predictor's) through to
    the real function and only raises on the SECOND (analyze_2i.run()'s
    own explicit call at this collect_total site, the real target)."""
    root, seal = world
    from experiments.exp2g import strata_2g as sg
    real = sg.check_strata_pins
    calls = []

    def boom(table):
        calls.append(1)
        if len(calls) == 1:
            return real(table)
        raise ValueError("boom strata gate")
    monkeypatch.setattr(sg, "check_strata_pins", boom)
    _insufficient(root, seal, "strata gate")
    assert len(calls) == 2


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


def test_gate1_rederive_check_failure_is_insufficient_data(world, monkeypatch):
    """C-1's own collect_total site — the same totality standard every
    other check in `run()` gets. This covers only the RAISE half of
    `run()`'s own `failures += f + (g2bad or [])` line (`f`, from
    `collect_total` catching an exception) — see the sibling test below
    for the OTHER half (`g2bad`, the function's own returned failure
    list on a clean, non-raising call)."""
    root, seal = world

    def boom(sweep_endpoint_records, stage1_final_records, gate_record):
        raise ValueError("boom gate1 rederive")
    monkeypatch.setattr(an, "gate1_rederive_7b", boom)
    _insufficient(root, seal, "gate 1 olmo7b re-derivation (byte identity)")


def test_gate1_rederive_real_mismatch_is_insufficient_data(world):
    """The OTHER half: `gate1_rederive_7b` returns NORMALLY with a
    non-empty failure list (a real, self-consistent byte mismatch — no
    exception at all) — proving `run()` actually WIRES that returned
    list into `failures` via `(g2bad or [])`, not merely that a raised
    exception gets caught (which the sibling test above already
    covers, and which alone would NOT catch a mutation that drops
    `(g2bad or [])` from the line, since `g2bad` is always `None` in
    the raise case regardless). Deliberately NOT in `full_shape.py`
    (whose worlds `test_full_shape_2i.py` alone exercises) — that file
    is DESELECTed from the mutation harness's own `run_suite()`.

    Flips TWO items in OPPOSITE directions (one 0->1, one 1->0) so
    `correct` — and therefore the world's already-cached `rung_set_2i
    .json` per-rung `k` — is UNCHANGED: isolating this world to the
    byte-level mismatch alone, not also (accidentally) tripping the
    unrelated, pre-existing `_check_rung_set_vs_endpoint` count check
    the first draft of this test discovered firing instead."""
    root, seal = world
    from experiments.exp2g import battery_2g as bg
    cap = bg.load_battery(["antonym"])["antonym"]
    p = bi.endpoint_record_path(root, "stage1_final", "antonym")
    rec = json.loads(p.read_text())
    bits = list(rec["bits"])
    conts = list(rec["continuations"])
    i_zero = next(i for i in range(len(bits)) if bits[i] == 0)
    i_one = next(i for i in range(len(bits)) if bits[i] == 1)
    bits[i_zero], bits[i_one] = 1, 0
    for i in (i_zero, i_one):
        answer = cap["eval_items"][i]["answer"]
        conts[i] = f" {answer}" if bits[i] else " zzz"
    rec["bits"], rec["continuations"] = bits, conts
    rec["correct"] = sum(bits)
    sweep_correct = json.loads(
        bi.record_path(root, bi.ENDPOINT_STEP_7B, "antonym").read_text())["correct"]
    assert rec["correct"] == sweep_correct   # the count is unchanged, only the bytes moved
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "gate 1 olmo7b re-derive")


def test_rung_set_derivation_check_failure_is_insufficient_data(world, monkeypatch):
    """I-1's own collect_total site."""
    root, seal = world

    def boom(rung_set, stage1_final, floors):
        raise ValueError("boom rung set derivation")
    monkeypatch.setattr(an, "_check_rung_set_derivation", boom)
    _insufficient(root, seal, "rung set re-derivation")


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


def test_primary_computation_unrelated_exception_is_insufficient_data(world, monkeypatch):
    """`_outcomes_and_tests_2i`'s own `collect_total` site in `run()`
    (labeled "primary olmo7b"): Ruling 18's `_run_test` only catches
    the two NAMED ValueError shapes ('no eligible rung', 'no
    informative pair') — that is precisely what keeps this site from
    ever seeing an exception via those two paths any more. Anything
    ELSE `primary_2i` might raise (a different exception type, or a
    ValueError matching neither pattern) still propagates all the way
    out of `_outcomes_and_tests_2i` uncaught by `_run_test`, and this
    site must still catch it — not left to crash `run()`. Distinct
    from `test_no_eligible_rung_is_undefined_not_a_crash` and
    `test_no_informative_pair_drops_the_rung_and_retries` above, which
    exercise the two paths `_run_test` now handles gracefully (and so
    no longer reach this site at all)."""
    root, seal = world

    def boom(*a, **kw):
        raise RuntimeError("boom — not one of Ruling 18's two named ValueError shapes")
    monkeypatch.setattr(an, "primary_2i", boom)
    _insufficient(root, seal, "primary olmo7b")


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
