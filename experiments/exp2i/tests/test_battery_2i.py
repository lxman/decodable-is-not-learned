# experiments/exp2i/tests/test_battery_2i.py
"""battery_2i: constants, the grid, the rung-set rule, the OLMo
predictor reader, the tokenizer deltas' pure assertions, and the
frozen pins. Zero model contact, zero network — no test touches the
Hub. Manifest-shaped tests (build_manifest/entry_*/load_manifest) run
on the COMMITTED `hub_inventory_olmo.json` / `checkpoints_2i.json`,
written once by the Step 3/4 scan+build outside any test."""
import gzip
import json

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2g import checkpoints_2g as ck
from experiments.exp2g import strata_2g
from experiments.exp2h import battery_2h as bh
from experiments.exp2i import battery_2i as bi


# ------------------------------------------------------------ constants

def test_constants():
    assert bi.FAMILY == "olmo2"
    assert bi.SIZE_PRED == "olmo1b" and bi.SIZE_OUT == "olmo7b"
    assert bi.REPO_1B == "allenai/OLMo-2-0425-1B"
    assert bi.REPO_7B == "allenai/OLMo-2-1124-7B"
    assert bi.REV_1B_ENDPOINT == "stage1-step1907359-tokens4001B"
    assert bi.REV_1B_MAIN == "main"
    assert bi.REV_7B_ENDPOINT == "stage1-step928646-tokens3896B"
    assert bi.REV_7B_MAIN == "main"
    assert bi.TWIN == "twin" and bi.TWIN_SEED == 0
    assert bi.ENDPOINT_STEP_7B == 928646
    assert bi.PREREG_TAG == "exp2i-preregistered"
    assert bi.PREDICTOR_SEAL_TAG == "exp2i-predictor-sealed"
    assert bi.ENDPOINT_SEAL_TAG == "exp2i-endpoint-sealed"
    assert bi.N_ITEMS == bt.N_ITEMS == 500
    assert bi.DRAWS_PER_ITEM == 64
    assert bi.SAMPLING_SEED == 0
    assert bi.STRATA_RUNGS == tuple(strata_2g.COVARIATE_OF)
    assert len(bi.STRATA_RUNGS) == 11
    assert bi.CKPT_CACHE.name == "ckpt_cache_2i"


# ------------------------------------------------------------------ grid

def test_grid_7b_ascending_21_endpoint_last():
    assert len(bi.GRID_7B) == 21
    assert list(bi.GRID_7B) == sorted(bi.GRID_7B)
    assert bi.GRID_7B[-1] == 928646 == bi.ENDPOINT_STEP_7B
    assert bi.trained_steps_7b() == bi.GRID_7B
    assert bi.n_trained_7b() == 21
    assert 0 not in bi.GRID_7B    # no true step0 on the 7B branch


def test_revision_of_7b_raises_off_grid():
    with pytest.raises(ValueError, match="GRID_7B"):
        bi.revision_of_7b(3000)


# ------------------------------------------------------- rung-set rule

def test_rung_set_from_counts_hand_computed():
    """A synthetic 34-rung count table against 2d's REAL floors: two
    strata rungs and one non-strata rung set to a clear pass (500/500),
    everything else at zero. Hand-computed split: R_OLMO sorted,
    R_CAP = R_OLMO ∩ the eleven, R_EXTRA = the rest — with at least one
    non-strata rung firing (clock24), per the brief."""
    floors = bg.load_floors()
    assert "clock24" not in bi.STRATA_RUNGS
    assert "antonym" in bi.STRATA_RUNGS and "antonym6" in bi.STRATA_RUNGS
    counts = {r: 0 for r in bt.RUNGS}
    counts["antonym"] = 500
    counts["antonym6"] = 500
    counts["clock24"] = 500
    got = bi.rung_set_from_counts(counts, floors)
    assert got["R_OLMO"] == ["antonym", "antonym6", "clock24"]
    assert got["R_CAP"] == ["antonym", "antonym6"]
    assert got["R_EXTRA"] == ["clock24"]
    assert set(got["per_rung"]) == set(bt.RUNGS)
    for r in got["R_OLMO"]:
        assert got["per_rung"][r]["significant"] is True
        assert got["per_rung"][r]["k"] == 500
    for r in set(bt.RUNGS) - set(got["R_OLMO"]):
        assert got["per_rung"][r]["significant"] is False
        assert got["per_rung"][r]["k"] == 0


def test_rung_set_from_counts_is_pure_on_a_subset():
    floors = bg.load_floors()
    counts = {"antonym": 0, "clock24": 500}
    got = bi.rung_set_from_counts(counts, floors)
    assert got["R_OLMO"] == ["clock24"]
    assert got["R_CAP"] == []
    assert got["R_EXTRA"] == ["clock24"]
    assert set(got["per_rung"]) == {"antonym", "clock24"}


# ---------------------------------------------------------- predictors

def test_sampler_counts_pythia_is_battery_2h_reexport():
    assert bi.sampler_counts_pythia is bh.sampler_counts


def test_predictor_paths(tmp_path):
    assert bi.predictor_draws_path(tmp_path, "antonym") == (
        tmp_path / "results" / "predictor" / "olmo1b" / "antonym.draws.jsonl.gz")
    assert bi.predictor_record_path(tmp_path, "antonym") == (
        tmp_path / "results" / "predictor" / "olmo1b" / "antonym.json")


def test_sampler_counts_olmo_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError) as exc:
        bi.sampler_counts_olmo(("antonym",), root=tmp_path, battery={},
                               verify_fn=lambda *a: False)
    assert "antonym" in str(exc.value)


def _write_toy_draws(path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as f:
        for item, draws in rows:
            f.write(json.dumps({"item": item, "draws": {"0": draws}}) + "\n")


def test_sampler_counts_olmo_reproduces_hand_counts(tmp_path, monkeypatch):
    monkeypatch.setattr(bi, "N_ITEMS", 2)
    rung = "toy_rung"
    draws0 = ["hit"] * 5 + ["miss"] * 59     # 64 draws, 5 verified hits
    draws1 = ["hit"] * 61 + ["miss"] * 3     # 64 draws, 61 verified hits
    _write_toy_draws(bi.predictor_draws_path(tmp_path, rung),
                     [(0, draws0), (1, draws1)])
    battery = {rung: {"eval_items": [{"answer": "hit"}, {"answer": "hit"}],
                      "answer_type": "word"}}
    got = bi.sampler_counts_olmo((rung,), root=tmp_path, battery=battery,
                                 verify_fn=lambda pred, ans, at: pred == ans)
    assert got == {rung: [5, 61]}


def test_sampler_counts_olmo_verify_fn_receives_answer_type(tmp_path, monkeypatch):
    monkeypatch.setattr(bi, "N_ITEMS", 1)
    rung = "toy_rung2"
    _write_toy_draws(bi.predictor_draws_path(tmp_path, rung),
                     [(0, ["x"] * 64)])
    battery = {rung: {"eval_items": [{"answer": "x"}], "answer_type": "letter"}}
    seen_types = []

    def verify_fn(pred, ans, at):
        seen_types.append(at)
        return pred == ans

    got = bi.sampler_counts_olmo((rung,), root=tmp_path, battery=battery,
                                 verify_fn=verify_fn)
    assert got == {rung: [64]}
    assert seen_types == ["letter"] * 64


# --------------------------------------------------------- check_tokenizer

class _StubTok:
    def __init__(self, padding_side="left", pad_token_id=None, first_id=999,
                special_ids=(100257, bi.PAD_TOKEN_ID)):
        self.padding_side = padding_side
        self.pad_token_id = bi.PAD_TOKEN_ID if pad_token_id is None else pad_token_id
        self.all_special_ids = list(special_ids)
        self._first_id = first_id

    def __call__(self, text):
        return {"input_ids": [self._first_id, 1, 2, 3]}


def test_check_tokenizer_passes_on_a_good_stub():
    bi.check_tokenizer(_StubTok())    # no raise


def test_check_tokenizer_refuses_wrong_padding_side():
    with pytest.raises(RuntimeError, match="padding_side"):
        bi.check_tokenizer(_StubTok(padding_side="right"))


def test_check_tokenizer_refuses_wrong_pad_id():
    with pytest.raises(RuntimeError, match="pad_token_id"):
        bi.check_tokenizer(_StubTok(pad_token_id=0))


def test_check_tokenizer_refuses_a_bos_prefix():
    with pytest.raises(RuntimeError, match="BOS"):
        bi.check_tokenizer(_StubTok(first_id=100257))   # a special id, prepended


def test_load_tokenizer_never_executed_here():
    # load_tokenizer touches the network (AutoTokenizer.from_pretrained);
    # this suite only asserts it exists and is callable, never calls it.
    assert callable(bi.load_tokenizer)


# ------------------------------------------------------------------ paths

def test_paths(tmp_path):
    assert bi.sweep_dir(tmp_path) == tmp_path / "results" / "sweep" / "olmo7b"
    assert bi.record_path(tmp_path, 1000, "antonym") == (
        tmp_path / "results" / "sweep" / "olmo7b" / "step1000" / "antonym.json")
    assert bi.record_path(tmp_path, bi.TWIN, "antonym") == (
        tmp_path / "results" / "sweep" / "olmo7b" / "twin" / "antonym.json")
    assert bi.checkpoint_record_path(tmp_path, 1000).name == "_checkpoint.json"
    assert bi.checkpoint_record_path(tmp_path, bi.TWIN).parent.name == "twin"
    assert bi.gate1_path(tmp_path) == (
        tmp_path / "results" / "sweep" / "olmo7b" / "gate1.json")
    assert bi.halt_marker_path(tmp_path).name == "HALTED"
    assert bi.endpoint_dir(tmp_path) == tmp_path / "results" / "endpoint"
    assert bi.endpoint_record_path(tmp_path, "stage1_final", "antonym") == (
        tmp_path / "results" / "endpoint" / "stage1_final" / "antonym.json")
    assert bi.endpoint_record_path(tmp_path, "main", "antonym") == (
        tmp_path / "results" / "endpoint" / "main" / "antonym.json")
    with pytest.raises(ValueError):
        bi.endpoint_record_path(tmp_path, "bogus", "antonym")
    assert bi.rung_set_path(tmp_path) == (
        tmp_path / "results" / "endpoint" / "rung_set_2i.json")
    assert bi.predictor_seal_path(tmp_path) == (
        tmp_path / "results" / "predictor" / "predictor_2i.json")
    assert bi.power_path(tmp_path) == (
        tmp_path / "results" / "endpoint" / "power_2i.json")


def test_ckpt_cache_path():
    from pathlib import Path
    assert bi.CKPT_CACHE == Path.home() / "emergence-lab" / "ckpt_cache_2i"


# --------------------------------------------------------------- loaders
#
# The loader family imports huggingface_hub/torch/transformers lazily
# inside each function body — never at module import — so this suite
# never touches the network or a model; it only asserts the functions
# exist with the right shape and that ck.tensor_digest is reused (not
# redefined).

def test_loader_family_present_and_not_executed():
    for name in ("download_entry", "verify_downloads", "clean_dir",
                "load_checkpoint", "load_thin", "load_twin_7b",
                "load_tokenizer", "free_checkpoint"):
        assert callable(getattr(bi, name))
    assert not hasattr(bi, "tensor_digest")   # reused via ck import, not redefined
    assert bi.ck is ck


# --------------------------------------------------- _check_loading_info
#
# The shared shape check `load_checkpoint`/`load_thin` both apply to
# `output_loading_info` (fix round 1, Important finding: the two
# loaders duplicated this 4-line block verbatim). Pure — a plain dict
# shaped like `output_loading_info`, no torch.

def test_check_loading_info_clean_dict_returns_counts_no_raise():
    li = {"missing_keys": [], "unexpected_keys": [], "mismatched_keys": []}
    counts = bi._check_loading_info(li, "some/repo@rev")
    assert counts == {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}


def test_check_loading_info_missing_key_raises_naming_label_and_key():
    li = {"missing_keys": ["lm_head.weight"], "unexpected_keys": [],
         "mismatched_keys": []}
    with pytest.raises(ValueError) as exc:
        bi._check_loading_info(li, "some/repo@rev (candidate files)")
    msg = str(exc.value)
    assert "some/repo@rev (candidate files)" in msg
    assert "missing_keys" in msg
    assert "lm_head.weight" in msg


# ------------------------------------------------------------- frozen pins

def test_frozen_sha256_matches_on_disk():
    bi.check_frozen_2i()
    assert len(bi.FROZEN_SHA256) == 16
    for path, want in bi.FROZEN_SHA256.items():
        assert bg.sha256_file(path) == want, path


def test_frozen_sha256_catches_drift():
    real = dict(bi.FROZEN_SHA256)
    bad_path = next(iter(real))
    bi.FROZEN_SHA256[bad_path] = "0" * 64
    try:
        with pytest.raises(ValueError):
            bi.check_frozen_2i()
    finally:
        bi.FROZEN_SHA256[bad_path] = real[bad_path]
    bi.check_frozen_2i()    # restored — must pass again


def test_pythia_predictor_files_pin():
    assert len(bi.PYTHIA_PREDICTOR_FILES) == 68
    keys = set(bi.PYTHIA_PREDICTOR_FILES)
    assert {k[0] for k in keys} == {"1b", "410m"}
    for size in ("1b", "410m"):
        rungs = {r for (s, r) in keys if s == size}
        assert rungs == set(bt.RUNGS)
    bi.check_pythia_predictor_files()


def test_pythia_predictor_files_catches_drift():
    real = dict(bi.PYTHIA_PREDICTOR_FILES)
    bad_key = next(iter(real))
    bi.PYTHIA_PREDICTOR_FILES[bad_key] = "0" * 64
    try:
        with pytest.raises(ValueError):
            bi.check_pythia_predictor_files()
    finally:
        bi.PYTHIA_PREDICTOR_FILES[bad_key] = real[bad_key]
    bi.check_pythia_predictor_files()


# ---------------------------------------------------------------- manifest
#
# These run on the COMMITTED `hub_inventory_olmo.json` (the Step 3
# scan: 965 revisions for REPO_7B — 928 stage1 + main + 36 stage-2
# ingredient/other branches; 3 for REPO_1B — endpoint, main, step0) and
# the COMMITTED `checkpoints_2i.json` it builds (Step 4). The known
# commits below are read from that committed manifest and match the
# Global Constraints' verified prefixes exactly (endpoint c0371f42…,
# 7B main 7df9a825…, 1B main a1847dff…, 1B endpoint 9d3e4365…).

_COMMIT_7B_ENDPOINT = "c0371f4281bf2376207646c6b62ddc6c442c7577"
_COMMIT_7B_MAIN = "7df9a82518afdecae4e8c026b27adccc8c1f0032"
_COMMIT_1B_MAIN = "a1847dff35000b4271fa70afc5db10fd29fedbdf"
_COMMIT_1B_ENDPOINT = "9d3e43659f00c17e6da23cf32333afd1fc39fa1a"


def test_load_inventory_committed():
    inv = bi.load_inventory()
    assert bi.REPO_7B in inv and bi.REPO_1B in inv
    assert len(inv[bi.REPO_7B]) == 965
    assert len(inv[bi.REPO_1B]) == 3
    assert set(inv[bi.REPO_1B]) == {
        bi.REV_1B_ENDPOINT, bi.REV_1B_MAIN, "stage1-step0-tokens0B"}
    assert inv[bi.REPO_7B]["main"]["commit"] == _COMMIT_7B_MAIN
    assert inv[bi.REPO_1B]["main"]["commit"] == _COMMIT_1B_MAIN


def test_build_manifest_from_committed_inventory():
    inv = bi.load_inventory()
    m = bi.build_manifest(inv)
    ents = m["entries_7b"]
    assert m["repo_1b"] == bi.REPO_1B and m["repo_7b"] == bi.REPO_7B
    assert m["grid_7b"] == list(bi.GRID_7B)
    assert m["trained_steps_7b"] == list(bi.GRID_7B)
    # 21 grid entries + the twin placeholder
    assert len(ents) == 22
    assert set(ents) == {str(s) for s in bi.GRID_7B} | {bi.TWIN}
    twin = ents[bi.TWIN]
    assert twin == {"revision": bi.TWIN, "commit": None, "files": [],
                    "kind": "from_config", "seed": bi.TWIN_SEED,
                    "config_commit": _COMMIT_7B_ENDPOINT}
    # every 7B grid entry: safetensors-shards, exactly 6 shards + index
    for step in bi.GRID_7B:
        e = ents[str(step)]
        assert e["kind"] == "safetensors-shards"
        shards = [f for f in e["files"] if f.endswith(".safetensors")]
        assert len(shards) == 6
        assert "model.safetensors.index.json" in e["files"]
        assert set(e["lfs_sha256"]) == set(shards)
        assert set(e["lfs_size"]) == set(shards)
    # every grid signature (kind, sorted lfs shas) is distinct
    sigs = {step: (e["kind"], tuple(sorted(e["lfs_sha256"].items())))
            for step, e in ents.items() if step != bi.TWIN}
    assert len(set(sigs.values())) == len(sigs)
    # the endpoint resolves to the pinned branch and commit
    endpoint = ents[str(bi.ENDPOINT_STEP_7B)]
    assert endpoint["revision"] == bi.REV_7B_ENDPOINT
    assert endpoint["commit"] == _COMMIT_7B_ENDPOINT
    # main entries, both repos
    main_7b = m["main"][bi.REPO_7B]
    assert main_7b["revision"] == "main" and main_7b["commit"] == _COMMIT_7B_MAIN
    assert main_7b["kind"] == "safetensors-shards"
    main_1b = m["main"][bi.REPO_1B]
    assert main_1b["revision"] == "main" and main_1b["commit"] == _COMMIT_1B_MAIN
    assert len([f for f in main_1b["files"] if f.endswith(".safetensors")]) == 2
    # the 1B endpoint entry
    e1b = m["entry_1b_endpoint"]
    assert e1b["revision"] == bi.REV_1B_ENDPOINT
    assert e1b["commit"] == _COMMIT_1B_ENDPOINT
    assert len([f for f in e1b["files"] if f.endswith(".safetensors")]) == 2
    # no other scanned revision (of 965) duplicates the endpoint's
    # candidate signature — the design's expectation, printed if false
    assert m["final_duplicates"] == []
    # stage 2 changes the weights: the endpoint does NOT byte-match main
    assert m["signature_equals_main"] is False
    assert m["n_revisions"] == {bi.REPO_1B: 3, bi.REPO_7B: 965}


def test_manifest_on_disk_matches_a_fresh_build():
    inv = bi.load_inventory()
    fresh = bi.build_manifest(inv)
    on_disk = json.loads(bi.CHECKPOINTS_PATH.read_text())
    assert on_disk == fresh
    got_sha = bg.sha256_file(bi.CHECKPOINTS_PATH)
    reloaded = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=got_sha)
    assert reloaded == fresh


def test_build_manifest_refuses_duplicate_signature_among_grid_points():
    """The real committed inventory has no duplicate among its 21 grid
    points (`test_build_manifest_from_committed_inventory`'s own
    `final_duplicates == []`/distinct-signatures assertions), so the
    refusal branch (`if step != ENDPOINT_STEP_7B and same:`) is never
    exercised by that test — only by a genuinely duplicated pair,
    built here by copying one grid revision's file dict onto another's
    (mutation harness mutant 2)."""
    import copy
    inv = copy.deepcopy(bi.load_inventory())
    steps = [s for s in bi.GRID_7B if s != bi.ENDPOINT_STEP_7B][:2]
    revs = {}
    for rev in inv[bi.REPO_7B]:
        m = bi._STAGE1_RE.fullmatch(rev)
        if m and int(m.group(1)) in steps:
            revs[int(m.group(1))] = rev
    assert set(revs) == set(steps)
    rev_a, rev_b = revs[steps[0]], revs[steps[1]]
    inv[bi.REPO_7B][rev_b]["files"] = dict(inv[bi.REPO_7B][rev_a]["files"])
    with pytest.raises(ValueError, match="duplicate"):
        bi.build_manifest(inv)


def test_write_load_manifest_roundtrip(tmp_path):
    inv = bi.load_inventory()
    manifest = bi.build_manifest(inv)
    p = tmp_path / "checkpoints_2i.json"
    bi.write_manifest(p, manifest)
    got = bg.sha256_file(p)
    loaded = bi.load_manifest(p, sha_pin=got)
    assert loaded == manifest
    with pytest.raises(ValueError):
        bi.load_manifest(p, sha_pin="0" * 64)
    assert bi.load_manifest(p, sha_pin=None) == manifest


def test_load_manifest_refuses_wrong_grid(tmp_path):
    inv = bi.load_inventory()
    manifest = bi.build_manifest(inv)
    manifest["grid_7b"] = list(manifest["grid_7b"])[:-1]
    p = tmp_path / "checkpoints_2i.json"
    bi.write_manifest(p, manifest)
    with pytest.raises(ValueError, match="frozen 7B grid"):
        bi.load_manifest(p, sha_pin=bg.sha256_file(p))


def test_entry_7b():
    inv = bi.load_inventory()
    manifest = bi.build_manifest(inv)
    e = bi.entry_7b(manifest, 1000)
    assert e["revision"] == "stage1-step1000-tokens5B"
    e_final = bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B)
    assert e_final["revision"] == bi.REV_7B_ENDPOINT
    e_twin = bi.entry_7b(manifest, bi.TWIN)
    assert e_twin["revision"] == bi.TWIN
    with pytest.raises(ValueError):
        bi.entry_7b(manifest, 999999)


def test_entry_1b_endpoint_and_entry_main():
    inv = bi.load_inventory()
    manifest = bi.build_manifest(inv)
    e = bi.entry_1b_endpoint(manifest)
    assert e["revision"] == bi.REV_1B_ENDPOINT
    m7 = bi.entry_main(manifest, bi.REPO_7B)
    assert m7["revision"] == "main" and m7["commit"] == _COMMIT_7B_MAIN
    m1 = bi.entry_main(manifest, bi.REPO_1B)
    assert m1["revision"] == "main" and m1["commit"] == _COMMIT_1B_MAIN
    with pytest.raises(ValueError):
        bi.entry_main(manifest, "not/a-repo")


def test_revision_of_7b_resolves_against_the_committed_manifest():
    assert bi.revision_of_7b(1000) == "stage1-step1000-tokens5B"
    assert bi.revision_of_7b(bi.ENDPOINT_STEP_7B) == bi.REV_7B_ENDPOINT
    for step in bi.GRID_7B:
        rev = bi.revision_of_7b(step)
        assert rev.startswith(f"stage1-step{step}-tokens") or \
            (step == bi.ENDPOINT_STEP_7B and rev == bi.REV_7B_ENDPOINT)


def test_candidate_from_checkpoints_2g_accepts_olmo_shard_names():
    """Decision 1: `ck.candidate` was written for Pythia's naming; this
    confirms — on the real committed inventory — that it accepts
    OLMo's `model-0000N-of-00006.safetensors` shards unmodified, so no
    local `candidate_olmo` was needed."""
    inv = bi.load_inventory()
    table = inv[bi.REPO_7B]
    main_files = table["main"]["files"]
    cand = ck.candidate(bi.REV_7B_ENDPOINT, table[bi.REV_7B_ENDPOINT]["files"],
                        main_files)
    assert cand is not None
    assert cand["kind"] == "safetensors-shards"
    assert len(cand["lfs"]) == 6
    assert all(f.startswith("model-") and f.endswith(".safetensors")
              for f in cand["lfs"])
