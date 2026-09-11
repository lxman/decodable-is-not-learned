# experiments/exp4/tests/test_battery_4.py
"""Known-answer gates and unit tests for `battery_4.py` (Task 2):
manifest grids against the frozen sources; the four committed rung
sets reproduced from the sweep bits (the program's per-experiment
"known-answer gate" convention); `t_clear_4`/`clears_and_stays_4` on a
hand-built three-rung outcome; committed digests against the real
committed trees; `load_outcome_4`'s refusals on a corrupted copy of a
real step directory; the model tables (`BATCH_4`, `REFS_FOR_4`,
`STAGE1_KEYS_4`, `N_HIDDEN_PIN_4`); `require_prereg_4` on fakes (2n's
own test pattern, mirrored); `reference_seal_paths_4`'s exact shape;
`load_record_4`/`load_record_failures_4`/`unit_complete_4`; `gate1_*`
on synthetic trees.

No test loads a model or touches the network — `load_key_4`/
`load_step_4`/`free_step_4` (MODEL CONTACT) are never executed here."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import battery_4 as b4  # noqa: E402
from experiments.exp4 import metric_4 as mt  # noqa: E402

import models as models_2b  # noqa: E402  (exp2b's; on sys.path via battery_2d's insertion)

FLOORS = bg.load_floors()
BATTERY = bt.load_battery()

_GRID_FIELD = {"pythia_2.8b": "trained_steps", "olmo2_7b": "grid_7b",
              "smollm3_3b": "grid_3b", "comma_7b": "grid_comma"}


# --------------------------------------------------------------- manifests

def test_manifests_4_grids_match_frozen_sources():
    m = b4.manifests_4()
    for traj, field in _GRID_FIELD.items():
        assert tuple(m[traj][field]) == b4.GRID_4[traj]


def test_grid_entry_4_returns_a_real_entry_per_trajectory():
    for traj in b4.TRAJECTORIES_4:
        e = b4.grid_entry_4(traj, b4.ENDPOINT_STEP_4[traj])
        assert e.get("commit")


def test_sweep_root_4_points_at_the_real_committed_dirs():
    for traj in b4.TRAJECTORIES_4:
        assert b4.SWEEP_ROOT_4[traj].is_dir()


# --------------------------------------------------------- rung-set pins

@pytest.mark.parametrize("traj", b4.TRAJECTORIES_4)
def test_rung_set_pin_reproduces_from_the_committed_trees(traj):
    """The known-answer gate: R reproduced from the sweep bits through
    `load_outcome_4` + `rung_sets_4` with 2d's floors equals the
    committed literal."""
    outcome = b4.load_outcome_4(traj, battery=BATTERY)
    rs = b4.rung_sets_4(outcome, FLOORS)
    assert tuple(sorted(rs["R"])) == tuple(sorted(b4.RUNG_SET_PIN_4[traj]))
    assert rs["endpoint_step"] == b4.ENDPOINT_STEP_4[traj]
    assert b4.check_rung_set_pins_4(traj, rs) == []


def test_check_rung_set_pins_4_catches_a_wrong_pin(monkeypatch):
    outcome = b4.load_outcome_4("pythia_2.8b", battery=BATTERY)
    rs = b4.rung_sets_4(outcome, FLOORS)
    monkeypatch.setitem(b4.RUNG_SET_PIN_4, "pythia_2.8b", ("not_a_real_rung",))
    fails = b4.check_rung_set_pins_4("pythia_2.8b", rs)
    assert fails and "pythia_2.8b" in fails[0]


# --------------------------------------------------- t_clear / clears_and_stays

def _hand_outcome():
    """Four rungs over five hand-picked steps, floor 0.1 for all:
    `flat_r` never clears; `rise_r` clears at step 3 and stays;
    `trans_r` clears at step 2, reverts, clears again at step 5 —
    `t_clear_4` reports the FIRST rise (2), `clears_and_stays_4` the
    LAST rise that never reverts (5), and (being significant at the
    endpoint) it lands in `rung_sets_4`'s "R"; `blip_r` clears once at
    step 2 and reverts for good — significant at NO later step
    including the endpoint, so it lands in "transient" (fired, but not
    at the endpoint) while `t_clear_4` still finds its one rise (2) and
    `clears_and_stays_4` finds none."""
    steps = [1, 2, 3, 4, 5]
    low, high = 40, 300  # 40/500=.08 < floor .1;  300/500=.6 >> floor, p << .01
    correct = {
        "flat_r": [low, low, low, low, low],
        "rise_r": [low, low, high, high, high],
        "trans_r": [low, high, low, low, high],
        "blip_r": [low, high, low, low, low],
    }
    per_step = {}
    for i, step in enumerate(steps):
        per_step[step] = {"digest": f"digest-{step}",
                          "rungs": {r: {"correct": correct[r][i], "n": 500,
                                       "bits": [1] * correct[r][i] + [0] * (500 - correct[r][i])}
                                    for r in correct}}
    return {"steps": steps, "per_step": per_step}


def test_t_clear_4_and_clears_and_stays_4_on_a_hand_built_outcome():
    outcome = _hand_outcome()
    floors = {"flat_r": 0.1, "rise_r": 0.1, "trans_r": 0.1, "blip_r": 0.1}
    tc = b4.t_clear_4(outcome, floors)
    cas = b4.clears_and_stays_4(outcome, floors)
    assert tc == {"flat_r": None, "rise_r": 3, "trans_r": 2, "blip_r": 2}
    assert cas == {"flat_r": None, "rise_r": 3, "trans_r": 5, "blip_r": None}
    assert tc["trans_r"] != cas["trans_r"]      # differs on the transient-but-ends-high pattern
    assert tc["blip_r"] != cas["blip_r"]        # differs on the transient-and-reverts pattern
    assert tc["rise_r"] == cas["rise_r"]        # agrees once risen and stayed


def test_rung_sets_4_on_the_hand_built_outcome():
    outcome = _hand_outcome()
    floors = {"flat_r": 0.1, "rise_r": 0.1, "trans_r": 0.1, "blip_r": 0.1}
    rs = b4.rung_sets_4(outcome, floors)
    assert rs["R"] == ["rise_r", "trans_r"]      # significant at the endpoint (step 5)
    assert rs["flat"] == ["flat_r"]              # never significant
    assert rs["transient"] == ["blip_r"]         # fired, not significant at the endpoint
    assert rs["endpoint_step"] == 5


# --------------------------------------------------------------- digests

def test_committed_step_digest_4_pythia_matches_checkpoint_json():
    got = b4.committed_step_digest_4("pythia_2.8b", 1000)
    ckpt = json.loads((b4.SWEEP_ROOT_4["pythia_2.8b"] / "step1000" / "_checkpoint.json")
                      .read_text())
    assert got == ckpt["digest"]


@pytest.mark.parametrize("traj,step", [("olmo2_7b", 1000), ("smollm3_3b", 40000),
                                       ("comma_7b", 10000)])
def test_committed_step_digest_4_matches_rung_weight_sha256_string(traj, step):
    got = b4.committed_step_digest_4(traj, step)
    rung_rec = json.loads((b4.SWEEP_ROOT_4[traj] / f"step{step}" / "antonym.json").read_text())
    assert isinstance(rung_rec["weight_sha256"], str)
    assert got == rung_rec["weight_sha256"]


def test_committed_init_digest_4_for_all_four():
    d28 = b4.committed_init_digest_4("pythia_2.8b")
    ckpt0 = json.loads((b4.SWEEP_ROOT_4["pythia_2.8b"] / "step0" / "_checkpoint.json").read_text())
    assert d28 == ckpt0["digest"]
    for traj in ("olmo2_7b", "smollm3_3b", "comma_7b"):
        got = b4.committed_init_digest_4(traj)
        twin = json.loads((b4.SWEEP_ROOT_4[traj] / "twin" / "_checkpoint.json").read_text())
        assert got == twin["digest"]


# ----------------------------------------------- load_outcome_4 refusals

def _mini_sweep_root(tmp_path, traj: str, step: int) -> Path:
    dst_root = tmp_path / "sweep" / traj
    shutil.copytree(b4.SWEEP_ROOT_4[traj] / f"step{step}", dst_root / f"step{step}")
    return dst_root


def test_load_outcome_4_refuses_a_missing_rung(tmp_path, monkeypatch):
    traj, step = "pythia_2.8b", 1000
    mini = _mini_sweep_root(tmp_path, traj, step)
    (mini / f"step{step}" / "antonym.json").unlink()
    monkeypatch.setitem(b4.SWEEP_ROOT_4, traj, mini)
    monkeypatch.setitem(b4.GRID_4, traj, (step,))
    with pytest.raises(FileNotFoundError):
        b4.load_outcome_4(traj, battery=BATTERY)


def test_load_outcome_4_refuses_a_bad_items_sha(tmp_path, monkeypatch):
    traj, step = "pythia_2.8b", 1000
    mini = _mini_sweep_root(tmp_path, traj, step)
    p = mini / f"step{step}" / "antonym.json"
    rec = json.loads(p.read_text())
    rec["items_sha256"] = "0" * 64
    p.write_text(json.dumps(rec))
    monkeypatch.setitem(b4.SWEEP_ROOT_4, traj, mini)
    monkeypatch.setitem(b4.GRID_4, traj, (step,))
    with pytest.raises(ValueError, match="items_sha256"):
        b4.load_outcome_4(traj, battery=BATTERY)


def test_load_outcome_4_refuses_a_short_bits_list(tmp_path, monkeypatch):
    traj, step = "pythia_2.8b", 1000
    mini = _mini_sweep_root(tmp_path, traj, step)
    p = mini / f"step{step}" / "antonym.json"
    rec = json.loads(p.read_text())
    rec["bits"] = rec["bits"][:10]
    p.write_text(json.dumps(rec))
    monkeypatch.setitem(b4.SWEEP_ROOT_4, traj, mini)
    monkeypatch.setitem(b4.GRID_4, traj, (step,))
    with pytest.raises(ValueError, match="bits"):
        b4.load_outcome_4(traj, battery=BATTERY)


# ------------------------------------------------------------ model tables

def test_batch_4_values():
    assert b4.BATCH_4["pythia_2.8b"] == 32
    assert b4.BATCH_4["olmo2_7b"] == 16
    assert b4.BATCH_4["smollm3_3b"] == 32
    assert b4.BATCH_4["comma_7b"] == 16
    assert b4.BATCH_4["ref_pythia_12b"] == 16
    assert b4.BATCH_4["ladder_pythia_70m"] == 32
    assert b4.BATCH_4["ladder_pythia_6.9b"] == 16


def test_refs_for_4_three_each_none_of_own_family():
    for traj in b4.TRAJECTORIES_4:
        refs = b4.REFS_FOR_4[traj]
        assert len(refs) == 3
        assert all(b4.FAMILY_OF_KEY_4[r] != b4.FAMILY_OF_KEY_4[traj] for r in refs)
    covered = sorted(r for refs in b4.REFS_FOR_4.values() for r in refs)
    for ref in b4.REFERENCES_4:
        assert covered.count(ref) == 3   # every reference used by the other three


def test_stage1_keys_4_and_first_units_4_counts():
    assert len(b4.STAGE1_KEYS_4) == 19
    assert len(set(b4.STAGE1_KEYS_4)) == 19
    assert set(b4.REFERENCES_4) <= set(b4.STAGE1_KEYS_4)
    assert len(b4.STAGE1_FIRST_UNITS_4) == 4
    assert b4.STAGE1_FIRST_UNITS_4 == tuple((t, b4.GRID_4[t][0]) for t in b4.TRAJECTORIES_4)


def test_n_hidden_pin_4_consistent_with_site_count_pin_4():
    assert set(b4.N_HIDDEN_PIN_4.values()) <= set(mt.SITE_COUNT_PIN_4.keys())
    for key in b4.STAGE1_KEYS_4:
        assert key in b4.N_HIDDEN_PIN_4
    for traj in b4.TRAJECTORIES_4:
        assert traj in b4.N_HIDDEN_PIN_4


def test_pythia_commits_4_matches_the_committed_scan_and_2b_shas():
    inv = b4.load_pythia_inventory_4()
    for s in ("70m", "160m", "1.4b"):
        assert b4.PYTHIA_COMMITS_4[s] == inv["commits"][s]
    for s, sha in models_2b.PYTHIA_SHAS.items():
        assert b4.PYTHIA_COMMITS_4[s] == sha
    assert set(b4.PYTHIA_COMMITS_4) == set(b4.LADDER_SIZES_4)


def test_render_and_position_constants():
    assert b4.RENDER_4["comma"] == "bos"
    assert b4.RENDER_4["pythia"] == "plain" and b4.RENDER_4["olmo2"] == "plain" \
        and b4.RENDER_4["smollm3"] == "plain"
    assert b4.POSITIONS_4[b4.PRIMARY_POSITION_4] == "prompt_end"


# ----------------------------------------------------------- prereg binding

def test_require_prereg_4_with_fakes(monkeypatch):
    with pytest.raises(RuntimeError, match="does not exist"):
        b4.require_prereg_4(tag_exists=lambda t: False, blob_sha=lambda t, r: None)
    present = tuple(r for r in b4.INSTRUMENT_BLOBS_4 if (b4.REPO / r).is_file())
    assert present  # battery_4.py and metric_4.py exist at this point in the build
    monkeypatch.setattr(b4, "INSTRUMENT_BLOBS_4", present)
    ok = b4.require_prereg_4(tag_exists=lambda t: t == b4.PREREG_TAG_4,
                             blob_sha=lambda t, r: bg.sha256_file(b4.REPO / r))
    assert ok["tag"] == b4.PREREG_TAG_4 and set(ok["instrument_blobs"]) == set(present)
    with pytest.raises(RuntimeError, match="does not bind"):
        b4.require_prereg_4(tag_exists=lambda t: True, blob_sha=lambda t, r: "0" * 64)


# ------------------------------------------------------- reference seal paths

def test_reference_seal_paths_4_shape(tmp_path):
    paths = b4.reference_seal_paths_4(tmp_path)
    assert len(paths) == 19 * 37 + 4 * 36 + 2 == 849
    assert paths == sorted(paths)
    assert all(not p.is_absolute() for p in paths)

    assert Path("results/reference/ref_pythia_12b/_load.json") in paths
    assert Path("results/reference/ref_pythia_12b/global.npz") in paths
    assert Path("results/reference/ref_pythia_12b/align.json") in paths
    assert Path("results/reference/ref_pythia_12b/sets/antonym.npz") in paths

    traj, step = b4.STAGE1_FIRST_UNITS_4[0]
    unit_rel = Path(f"results/sweep/{traj}/step{step}")
    assert (unit_rel / "_load.json") in paths
    assert (unit_rel / "align.json") in paths
    assert (unit_rel / "sets" / "antonym.npz") in paths
    assert (unit_rel / "global.npz") not in paths   # sweep units carry no global.npz

    assert Path("results/reference/eligibility_4.json") in paths
    assert Path("results/reference/power_4.json") in paths


def test_key_dir_4_dispatch(tmp_path):
    assert b4.key_dir_4(tmp_path, "ref_pythia_12b") == b4.reference_dir(tmp_path, "ref_pythia_12b")
    assert b4.key_dir_4(tmp_path, ("pythia_2.8b", 1000)) == b4.unit_dir(tmp_path, "pythia_2.8b", 1000)
    assert b4.key_dir_4(tmp_path, ["pythia_2.8b", 1000]) == b4.unit_dir(tmp_path, "pythia_2.8b", 1000)


# ------------------------------------------------------------ _complete_info
# (fix round 1: the loader-info completeness helper `load_key_4`/`load_step_4`
# route every branch through; pure, so directly testable.)

def _full_info(**overrides):
    base = {"commit": "c1", "revision": "r1", "repo": "repo1", "kind": "thin",
           "config_source": "cs1", "n_hidden": 17,
           "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0},
           "tensor_digest": "d1"}
    base.update(overrides)
    return base


def test_complete_info_fills_missing_and_never_overrides_present():
    info = {"commit": "already-here", "tensor_digest": "d1"}
    out = b4._complete_info(info, commit="ignored-default", revision="r1", repo="repo1",
                            kind="thin", config_source="cs1", n_hidden=17,
                            loading_info={"missing_keys": 0, "unexpected_keys": 0,
                                         "mismatched_keys": 0})
    assert out["commit"] == "already-here"   # a present value is never overridden
    assert out["revision"] == "r1"           # a missing value is filled
    assert out["kind"] == "thin"
    assert out["n_hidden"] == 17
    for field in b4._INFO_CONTRACT_FIELDS_4:
        assert out.get(field) is not None


def test_complete_info_raises_when_a_field_has_no_default_and_is_missing():
    info = {"commit": "c1", "revision": "r1", "repo": "repo1", "kind": "thin",
           "config_source": "cs1", "n_hidden": 17}   # no tensor_digest, no loading_info
    with pytest.raises(ValueError, match="tensor_digest"):
        b4._complete_info(info, commit=None, revision=None, repo=None, kind=None,
                          config_source=None, n_hidden=None, loading_info=None)


def test_complete_info_raises_on_an_invalid_kind():
    info = _full_info(kind="bogus")
    with pytest.raises(ValueError, match="kind"):
        b4._complete_info(info, commit=None, revision=None, repo=None, kind=None,
                          config_source=None, n_hidden=None, loading_info=None)


def test_complete_info_fills_the_twin_shape_from_load_twin_like_fixtures():
    """Mirrors what `twin_*` branches pass: `_complete_info` supplies
    `commit` (the config commit), `kind="from_config"` and the all-zero
    `loading_info` — none of which a `load_twin_*` frozen function
    returns on its own."""
    info = {"repo": "repo1", "revision": "twin", "config_source": "cs1", "tensor_digest": "d1"}
    out = b4._complete_info(info, commit="config-commit", revision="twin", repo="repo1",
                            kind="from_config", config_source="cs1", n_hidden=33,
                            loading_info=b4._ZERO_LOADING_INFO_4)
    assert out["commit"] == "config-commit"
    assert out["kind"] == "from_config"
    assert out["loading_info"] == {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}


# --------------------------------------------------------------- records

def _write_npz_like(p: Path, payload: bytes) -> str:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _good_record_and_dir(tmp_path):
    key = "ref_pythia_12b"
    d = b4.reference_dir(tmp_path, key)
    sets_sha = {r: _write_npz_like(d / "sets" / f"{r}.npz", f"sets-{r}".encode())
               for r in ("antonym", "arith_next")}
    global_sha = _write_npz_like(d / "global.npz", b"global-payload")
    info = {"commit": "c0ffee", "revision": "main", "repo": "fake/repo", "kind": "candidate",
            "config_source": "fake/repo@c0ffee", "n_hidden": 37,
            "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0},
            "tensor_digest": "deadbeef"}
    rec = b4.load_record_4(key=key, family="pythia", info=info, sites=[0, 18, 36], d=5120,
                           render="plain", batch_size=16, refs=("ref_olmo2_7b",),
                           pairing={"ref_olmo2_7b": [0, 18, 36]}, sets_sha=sets_sha,
                           global_sha=global_sha, attested_sha={"antonym": "a" * 64},
                           activation_sha={"antonym": "b" * 64}, committed_digest="deadbeef",
                           seconds=1.5, stack={"torch": "2.12.1"}, git_sha="abc123",
                           prereg_tag=b4.PREREG_TAG_4)
    return key, d, rec


def test_load_record_4_shape_and_load_record_failures_4_clean(tmp_path):
    key, d, rec = _good_record_and_dir(tmp_path)
    assert rec["key"] == key
    assert rec["family"] == "pythia" and rec["render"] == "plain" and rec["batch_size"] == 16
    assert rec["sites"] == [0, 18, 36] and rec["d"] == 5120
    assert rec["prereg_tag"] == b4.PREREG_TAG_4


def test_load_record_4_serializes_a_unit_key_as_a_list():
    rec = b4.load_record_4(key=("pythia_2.8b", 1000), family="pythia", info={}, sites=[0],
                           d=8, render="plain", batch_size=32, refs=(), pairing={},
                           sets_sha={}, global_sha=None, attested_sha=None, activation_sha=None,
                           committed_digest="x", seconds=0.1, stack={}, git_sha="x",
                           prereg_tag=b4.PREREG_TAG_4)
    assert rec["key"] == ["pythia_2.8b", 1000]
    json.dumps(rec)  # round-trips through JSON (no tuples left inside)


def test_load_record_failures_4_clean_round_trip(tmp_path):
    key, d, rec = _good_record_and_dir(tmp_path)
    bad = b4.load_record_failures_4(rec, key=key, expected_family="pythia",
                                     expected_render="plain", expected_batch=16,
                                     expected_committed_digest="deadbeef",
                                     expected_refs=("ref_olmo2_7b",), root=tmp_path)
    assert bad == []


@pytest.mark.parametrize("field,bad_value,label", [
    ("family", "olmo2", "family"),
    ("render", "bos", "render"),
    ("batch_size", 999, "batch_size"),
    ("committed_digest", "wrong-digest", "committed_digest"),
    ("refs", ["ref_comma_7b"], "refs"),
    ("prereg_tag", "some-other-tag", "prereg_tag"),
])
def test_load_record_failures_4_catches_each_field(tmp_path, field, bad_value, label):
    key, d, rec = _good_record_and_dir(tmp_path)
    rec = dict(rec)
    rec[field] = bad_value
    bad = b4.load_record_failures_4(rec, key=key, expected_family="pythia",
                                     expected_render="plain", expected_batch=16,
                                     expected_committed_digest="deadbeef",
                                     expected_refs=("ref_olmo2_7b",), root=tmp_path)
    assert bad and any(label in f for f in bad)


@pytest.mark.parametrize("field", list(b4._INFO_CONTRACT_FIELDS_4))
def test_load_record_failures_4_catches_a_null_contract_field(tmp_path, field):
    """Fix round 1: every one of the eight loader-info fields
    (`_INFO_CONTRACT_FIELDS_4`) must be present and non-null on the
    record, including `kind` and `commit` explicitly (the reviewer's
    two named cases)."""
    key, d, rec = _good_record_and_dir(tmp_path)
    rec = dict(rec)
    rec[field] = None
    bad = b4.load_record_failures_4(rec, key=key, expected_family="pythia",
                                     expected_render="plain", expected_batch=16,
                                     expected_committed_digest="deadbeef",
                                     expected_refs=("ref_olmo2_7b",), root=tmp_path)
    assert bad and any(field in f for f in bad)


def test_load_record_failures_4_catches_an_invalid_kind_value(tmp_path):
    key, d, rec = _good_record_and_dir(tmp_path)
    rec = dict(rec)
    rec["kind"] = "bogus"
    bad = b4.load_record_failures_4(rec, key=key, expected_family="pythia",
                                     expected_render="plain", expected_batch=16,
                                     expected_committed_digest="deadbeef",
                                     expected_refs=("ref_olmo2_7b",), root=tmp_path)
    assert bad and any("kind" in f for f in bad)


def test_load_record_failures_4_clean_round_trip_covers_every_contract_field(tmp_path):
    """The good fixture itself must already satisfy every contract
    field non-null — otherwise the parametrized null-field test above
    would be vacuous for that field."""
    key, d, rec = _good_record_and_dir(tmp_path)
    for field in b4._INFO_CONTRACT_FIELDS_4:
        assert rec.get(field) is not None, field
    assert rec["kind"] in b4._INFO_KIND_VALUES_4


def test_load_record_failures_4_catches_sets_sha_mismatch(tmp_path):
    key, d, rec = _good_record_and_dir(tmp_path)
    (d / "sets" / "antonym.npz").write_bytes(b"tampered-bytes")
    bad = b4.load_record_failures_4(rec, key=key, expected_family="pythia",
                                     expected_render="plain", expected_batch=16,
                                     expected_committed_digest="deadbeef",
                                     expected_refs=("ref_olmo2_7b",), root=tmp_path)
    assert bad and any("sets sha" in f for f in bad)


def test_load_record_failures_4_catches_global_sha_mismatch(tmp_path):
    key, d, rec = _good_record_and_dir(tmp_path)
    (d / "global.npz").write_bytes(b"tampered-global")
    bad = b4.load_record_failures_4(rec, key=key, expected_family="pythia",
                                     expected_render="plain", expected_batch=16,
                                     expected_committed_digest="deadbeef",
                                     expected_refs=("ref_olmo2_7b",), root=tmp_path)
    assert bad and any("global sha" in f for f in bad)


@pytest.mark.parametrize("field", ["attested_sha256", "activation_sha256"])
def test_load_record_failures_4_requires_attested_and_activation_sha_present(tmp_path, field):
    key, d, rec = _good_record_and_dir(tmp_path)
    rec = dict(rec)
    rec[field] = None
    bad = b4.load_record_failures_4(rec, key=key, expected_family="pythia",
                                     expected_render="plain", expected_batch=16,
                                     expected_committed_digest="deadbeef",
                                     expected_refs=("ref_olmo2_7b",), root=tmp_path)
    assert bad and any(field in f for f in bad)


def test_unit_complete_4_true_then_false_on_corruption(tmp_path):
    traj, step = "pythia_2.8b", 1000
    d = b4.unit_dir(tmp_path, traj, step)
    sets_sha = {r: _write_npz_like(d / "sets" / f"{r}.npz", f"data-{r}".encode()) for r in bt.RUNGS}
    (d / "align.json").write_text("{}")
    (d / "_load.json").write_text(json.dumps({"sets_sha256": sets_sha}))
    assert b4.unit_complete_4(tmp_path, (traj, step)) is True
    (d / "sets" / f"{bt.RUNGS[0]}.npz").write_bytes(b"corrupted")
    assert b4.unit_complete_4(tmp_path, (traj, step)) is False


def test_unit_complete_4_false_when_missing(tmp_path):
    assert b4.unit_complete_4(tmp_path, ("pythia_2.8b", 999999)) is False
    assert b4.unit_complete_4(tmp_path, "ref_pythia_12b") is False


# ------------------------------------------------------------------- gate 1

def test_gate1_record_4_and_gate1_failures_4_roundtrip():
    sets_equal = {r: True for r in bt.RUNGS}
    act_equal = {r: True for r in bt.RUNGS}
    att_equal = {r: True for r in bt.RUNGS}
    g1 = b4.gate1_record_4(traj="pythia_2.8b",
                           sweep_rec={"commit": "c1", "tensor_digest": "d1"},
                           reference_rec={"commit": "c1", "tensor_digest": "d1"},
                           sets_equal=sets_equal, activation_sha_equal=act_equal,
                           attested_sha_equal=att_equal,
                           digest_equal=True, seconds=12.0)
    assert b4.gate1_failures_4(g1, traj="pythia_2.8b") == []

    bad_sets = dict(sets_equal)
    bad_sets[bt.RUNGS[0]] = False
    g1_bad = dict(g1)
    g1_bad["sets_equal"] = bad_sets
    fails = b4.gate1_failures_4(g1_bad, traj="pythia_2.8b")
    assert fails and any(bt.RUNGS[0] in f for f in fails)

    g1_bad_tag = dict(g1)
    g1_bad_tag["prereg_tag"] = "wrong"
    fails2 = b4.gate1_failures_4(g1_bad_tag, traj="pythia_2.8b")
    assert fails2 and any("prereg_tag" in f for f in fails2)

    g1_bad_digest = dict(g1)
    g1_bad_digest["digest_equal"] = False
    fails3 = b4.gate1_failures_4(g1_bad_digest, traj="pythia_2.8b")
    assert fails3 and any("digest_equal" in f for f in fails3)


def _write_gate1_tree(tmp_path, traj: str, *, sweep_bytes_by_rung, ref_bytes_by_rung,
                      same_digest=True):
    endpoint = b4.ENDPOINT_STEP_4[traj]
    ref_dir = b4.reference_dir(tmp_path, f"endpoint_{traj}")
    sweep_d = b4.unit_dir(tmp_path, traj, endpoint)
    act_sha = {}
    att_sha = {}
    for r in bt.RUNGS:
        (ref_dir / "sets" / f"{r}.npz").parent.mkdir(parents=True, exist_ok=True)
        (ref_dir / "sets" / f"{r}.npz").write_bytes(ref_bytes_by_rung(r))
        (sweep_d / "sets" / f"{r}.npz").parent.mkdir(parents=True, exist_ok=True)
        (sweep_d / "sets" / f"{r}.npz").write_bytes(sweep_bytes_by_rung(r))
        act_sha[r] = hashlib.sha256(f"activation-{r}".encode()).hexdigest()
        att_sha[r] = hashlib.sha256(f"attested-{r}".encode()).hexdigest()
    ref_rec = {"tensor_digest": "same-digest", "activation_sha256": act_sha,
              "attested_sha256": att_sha}
    sweep_rec = {"tensor_digest": "same-digest" if same_digest else "different-digest",
                "activation_sha256": dict(act_sha), "attested_sha256": dict(att_sha)}
    (ref_dir / "_load.json").write_text(json.dumps(ref_rec))
    (sweep_d / "_load.json").write_text(json.dumps(sweep_rec))
    return ref_dir, sweep_d


def test_gate1_rederive_4_all_equal(tmp_path):
    traj = "pythia_2.8b"
    _write_gate1_tree(tmp_path, traj,
                      sweep_bytes_by_rung=lambda r: f"data-{r}".encode(),
                      ref_bytes_by_rung=lambda r: f"data-{r}".encode())
    out = b4.gate1_rederive_4(tmp_path, traj)
    assert out["n_rungs"] == len(bt.RUNGS)
    assert all(out["sets_equal"].values())
    assert all(out["activation_sha_equal"].values())
    assert all(out["attested_sha_equal"].values())
    assert out["digest_equal"] is True


def test_gate1_rederive_4_one_rung_differs(tmp_path):
    traj = "pythia_2.8b"
    bad_rung = bt.RUNGS[0]
    _write_gate1_tree(tmp_path, traj,
                      sweep_bytes_by_rung=lambda r: (b"different" if r == bad_rung
                                                     else f"data-{r}".encode()),
                      ref_bytes_by_rung=lambda r: f"data-{r}".encode())
    out = b4.gate1_rederive_4(tmp_path, traj)
    assert out["sets_equal"][bad_rung] is False
    assert all(v for k, v in out["sets_equal"].items() if k != bad_rung)
    assert out["digest_equal"] is True


def test_gate1_rederive_4_digest_mismatch(tmp_path):
    traj = "pythia_2.8b"
    _write_gate1_tree(tmp_path, traj,
                      sweep_bytes_by_rung=lambda r: f"data-{r}".encode(),
                      ref_bytes_by_rung=lambda r: f"data-{r}".encode(),
                      same_digest=False)
    out = b4.gate1_rederive_4(tmp_path, traj)
    assert out["digest_equal"] is False
    assert all(out["sets_equal"].values())


# ----------------------------------------------------------------- misc pins

def test_check_frozen_4_noop_when_empty(monkeypatch):
    monkeypatch.setattr(b4, "FROZEN_SHA256_4", {})
    b4.check_frozen_4()  # must not raise


def test_check_frozen_4_raises_on_drift(monkeypatch, tmp_path):
    p = tmp_path / "frozen.py"
    p.write_text("x = 1\n")
    monkeypatch.setattr(b4, "FROZEN_SHA256_4", {p: "0" * 64})
    with pytest.raises(ValueError):
        b4.check_frozen_4()
