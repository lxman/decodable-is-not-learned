# experiments/exp2i/tests/test_stages_2i.py
"""The stage runners' control flow with FAKE model/tokenizer/sampler —
no torch, no network, no frozen tree touched. Covers: `blobs_bound` on
a real temporary git repo; `write_draws`'s byte-identity to its exp3
source; `sample_2i.run`'s refusals (missing tag / stale blob / already
sealed) and its writes (2d's row format, `sampler_counts_olmo`
agreement, skip-if-exists, dry-run without a loader); `endpoint_2i
.run`'s refusal (missing predictor seal, drifted blob) and its writes
(both `which` records, the rung set from `stage1_final` not `main`,
dry-run without a loader); `seal_2i.seal_predictor`'s refusals and its
seal shape; `preflight_2i.run`'s "nothing under results/" assertion.
"""
from __future__ import annotations

import gzip
import inspect
import json
import subprocess
from pathlib import Path

import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2i import battery_2i as bi
from experiments.exp2i.run import endpoint_2i as ep
from experiments.exp2i.run import preflight_2i as pf
from experiments.exp2i.run import sample_2i as smp
from experiments.exp2i.run import seal_2i as seal
from experiments.exp3.run.run_cell import write_draws as exp3_write_draws

SMALL_RUNGS = ("antonym", "antonym6", "clock24")   # two STRATA_RUNGS + one extra


@pytest.fixture(autouse=True)
def _shrink_instrument_blobs_to_what_exists(monkeypatch):
    """Task 4 landed `run/sweep_2i.py`, the fifth and final file in
    `analyze_2i.require_prereg_2i`'s real `INSTRUMENT_BLOBS_2I` — so
    this is a no-op now (the subset equals the full five-file set).
    Left in place rather than removed: it keeps these tests exercising
    the STAGE RUNNERS' own control flow (their reason for existing),
    independent of whether the five-file set is ever again momentarily
    incomplete on some future branch — that re-litigation is
    `test_analyze_2i.py`'s job, not this module's."""
    from experiments.exp2i import analyze_2i as an
    subset = tuple(r for r in an.INSTRUMENT_BLOBS_2I if (bi.REPO / r).is_file())
    monkeypatch.setattr(an, "INSTRUMENT_BLOBS_2I", subset)


# ------------------------------------------------------------ blobs_bound

def _git(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def test_blobs_bound_temp_repo(tmp_path):
    _git(["init", "-q"], tmp_path)
    _git(["config", "user.email", "t@t.com"], tmp_path)
    _git(["config", "user.name", "t"], tmp_path)
    f = tmp_path / "file.txt"
    f.write_text("hello")
    _git(["add", "file.txt"], tmp_path)
    _git(["commit", "-q", "-m", "init"], tmp_path)
    _git(["tag", "t1"], tmp_path)

    assert bi.blobs_bound("t1", ["file.txt"], repo_root=tmp_path) == []

    f.write_text("changed")
    assert bi.blobs_bound("t1", ["file.txt"], repo_root=tmp_path) == ["file.txt"]

    f.write_text("hello")   # restore
    assert bi.blobs_bound("t1", ["file.txt"], repo_root=tmp_path) == []

    assert bi.blobs_bound("t1", ["missing.txt"], repo_root=tmp_path) == ["missing.txt"]

    # a path on disk the tag never carried (committed after the tag)
    g = tmp_path / "later.txt"
    g.write_text("new")
    _git(["add", "later.txt"], tmp_path)
    _git(["commit", "-q", "-m", "later"], tmp_path)
    assert bi.blobs_bound("t1", ["later.txt"], repo_root=tmp_path) == ["later.txt"]
    assert bi.blobs_bound("t1", ["file.txt", "later.txt"], repo_root=tmp_path) == \
        ["later.txt"]


# --------------------------------------------------------- write_draws

def test_write_draws_is_byte_identical_to_exp3_source():
    got = inspect.getsource(smp.write_draws)
    want = inspect.getsource(exp3_write_draws)
    assert got == want


def test_write_draws_writes_gzip_jsonl(tmp_path):
    p = tmp_path / "x.draws.jsonl.gz"
    rows = [{"item": 1, "draws": {"0": ["a", "b"]}},
           {"item": 0, "draws": {"0": ["c", "d"]}}]
    smp.write_draws(p, rows)
    with gzip.open(p, "rt") as f:
        lines = [json.loads(line) for line in f]
    assert lines == rows


def _prereg():
    """Matches every real file's CURRENT sha, standing in for 'the tag
    carries what is on disk right now' (2h's own `_prereg()` test
    pattern) — `analyze_2i.require_prereg_2i` (the ONLY implementation
    since Task 4 removed the stub), five-file `INSTRUMENT_BLOBS_2I`,
    all five now on disk."""
    def blob_sha(tag, rel):
        p = bi.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None
    return dict(tag_exists=lambda t: True, blob_sha=blob_sha)


# --------------------------------------------------------------- helpers

class FakeTok:
    all_special_ids = [0]
    padding_side = "left"
    pad_token_id = bi.PAD_TOKEN_ID

    def __call__(self, text, **kw):
        return {"input_ids": [999]}


def _manifest():
    return bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)


def _make_fake_sampler(battery, hit_fraction=1.0):
    """A deterministic fake `sample_item`: the first `hit_fraction`
    share of each rung's items answer correctly (draws_per_seed/
    draws_per_seed), the rest miss entirely — enough spread to drive
    `rung_set_from_counts` without a model."""
    def fake(model, tok, prompt, *, rung, size, mode, item_idx, seeds,
            draws_per_seed, max_new_tokens, terminal_ids):
        cap = battery[rung]
        ans = str(cap["eval_items"][item_idx]["answer"])
        n_hit = int(round(hit_fraction * len(cap["eval_items"])))
        text = ans if item_idx < n_hit else "zzz"
        seed = seeds[0]
        return {seed: [text] * draws_per_seed}
    return fake


# ---------------------------------------------------------- sample_2i.run

def test_sample_refuses_without_prereg_tag(tmp_path):
    # Task 3 landed the real analyze_2i.require_prereg_2i, so the
    # try/except import in sample_2i.py now resolves to it rather than
    # the stub; called with no injections it falls through to its own
    # defaults (pr.git_tag_exists), which correctly report that the
    # real 'exp2i-preregistered' tag does not exist on this repo yet —
    # not the stub's "not built yet".
    with pytest.raises(RuntimeError, match="preregistration tag"):
        smp.run(root=tmp_path, device="cpu", rungs=("antonym",), loaders={})


def test_sample_refuses_with_missing_tag_injected(tmp_path):
    with pytest.raises(RuntimeError, match="preregistration tag"):
        smp.run(root=tmp_path, device="cpu", rungs=("antonym",), loaders={},
               tag_exists=lambda t: False, blob_sha=lambda t, r: "x")


def test_sample_refuses_with_stale_blob(tmp_path):
    with pytest.raises(RuntimeError, match="drifted"):
        smp.run(root=tmp_path, device="cpu", rungs=("antonym",), loaders={},
               tag_exists=lambda t: True, blob_sha=lambda t, r: "0" * 64)


def test_sample_refuses_after_seal(tmp_path):
    p = bi.predictor_seal_path(tmp_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{}")
    with pytest.raises(RuntimeError, match="already sealed"):
        smp.run(root=tmp_path, device="cpu", rungs=("antonym",), loaders={}, **_prereg())


def test_sample_dry_run_builds_no_loader(tmp_path, capsys):
    def boom(commit, device):
        raise AssertionError("must not be called during dry run")
    smp.run(root=tmp_path, device="cpu", rungs=("antonym",), loaders={"olmo1b": boom},
           dry_run=True, **_prereg())
    assert "would sample" in capsys.readouterr().out


def test_sample_prereg_precedes_any_loader_construction(tmp_path, monkeypatch):
    called = []
    monkeypatch.setattr(smp, "_assert_provenance", lambda: called.append("p"))
    monkeypatch.setattr(smp, "real_loaders", lambda: called.append("l") or {})
    # see test_sample_refuses_without_prereg_tag: the real require_prereg_2i
    # is wired in now, so the no-injection refusal names the missing tag.
    with pytest.raises(RuntimeError, match="preregistration tag"):
        smp.run(root=tmp_path, device="cpu", rungs=("antonym",))
    assert called == []


def test_sample_writes_rows_2d_format_skip_if_exists_and_counts(tmp_path):
    cap = bt.load_item_file("antonym")
    battery = {"antonym": cap}
    fake_sampler = _make_fake_sampler(battery, hit_fraction=0.4)
    loaders = {"olmo1b": lambda commit, device: (object(), FakeTok(),
                                                 {"tensor_digest": "D"})}

    smp.run(root=tmp_path, device="cpu", rungs=("antonym",), loaders=loaders,
           sampler=fake_sampler, **_prereg())

    rec_path = bi.predictor_record_path(tmp_path, "antonym")
    dpath = bi.predictor_draws_path(tmp_path, "antonym")
    assert rec_path.is_file() and dpath.is_file()
    rec = json.loads(rec_path.read_text())
    assert rec["family"] == "olmo2" and rec["size"] == "olmo1b"
    assert rec["revision"] == bi.REV_1B_ENDPOINT
    assert rec["draws_per_seed"] == bi.DRAWS_PER_ITEM == 64
    # full_string tallies DRAWS, not items: 200 hit items * 64/64 draws each
    assert rec["per_seed_tallies"]["0"]["full_string"] == 200 * 64
    assert rec["per_seed_tallies"]["0"]["n_draws"] == 500 * 64

    # 2d's row format: analyze_2d.read_rows accepts it (coverage, one
    # seed stream, exactly draws_per_seed strings per item)
    rows = a2d.read_rows(dpath, seed=bi.SAMPLING_SEED, dps=bi.DRAWS_PER_ITEM,
                        n_items=bi.N_ITEMS)
    assert len(rows) == bi.N_ITEMS

    # sampler_counts_olmo re-derives the same tally independently
    counts = bi.sampler_counts_olmo(("antonym",), root=tmp_path, battery=battery,
                                    verify_fn=a2d.load_verify())
    n_full_hits = sum(1 for c in counts["antonym"] if c == bi.DRAWS_PER_ITEM)
    assert n_full_hits == 200

    # skip-if-exists: a second run must not touch the sampler or the loader
    def boom_sampler(*a, **k):
        raise AssertionError("must not resample an existing rung")

    def boom_loader(*a, **k):
        raise AssertionError("must not load a model when nothing is pending")

    smp.run(root=tmp_path, device="cpu", rungs=("antonym",),
           loaders={"olmo1b": boom_loader}, sampler=boom_sampler, **_prereg())


def test_run_sampling_rung_skip_if_exists_direct(tmp_path):
    """`run()`'s OWN pending check (asserted above) short-circuits
    BEFORE `run_sampling_rung` is ever called when nothing is pending
    — it never exercises `run_sampling_rung`'s own skip-if-exists
    branch (`if out.exists() and dpath.exists():`), only reachable via
    a direct call, e.g. a rung left over from a prior crashed run
    within an otherwise-still-pending `rungs` list."""
    rec = {"rung": "antonym", "correct": 1}
    out = bi.predictor_record_path(tmp_path, "antonym")
    dpath = bi.predictor_draws_path(tmp_path, "antonym")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec))
    dpath.parent.mkdir(parents=True, exist_ok=True)
    dpath.write_bytes(b"")

    def boom(*a, **k):
        raise AssertionError("must not sample when both files already exist")

    got = smp.run_sampling_rung("antonym", out_root=tmp_path,
                                model_ctx=("tok", "model", {}, "commit"),
                                verify_fn=lambda *a: True, sampler=boom)
    assert got == rec


def test_sample_default_rungs_is_bt_rungs(tmp_path, monkeypatch):
    monkeypatch.setattr(bt, "RUNGS", ("antonym",))
    got = []
    monkeypatch.setattr(smp, "real_loaders",
                        lambda: {"olmo1b": lambda c, d: got.append((c, d)) or
                                 (_ for _ in ()).throw(AssertionError("no model"))})
    smp.run(root=tmp_path, device="cpu", loaders=None, dry_run=True, **_prereg())
    # dry run only prints; real_loaders() is constructed but never called


# --------------------------------------------------------- endpoint_2i.run

def _write_predictor_seal(root, files=None, sha="SEALSHA0"):
    p = bi.predictor_seal_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"files": files or {}, "counts": {}, "sha256": sha,
                             "tag": bi.PREDICTOR_SEAL_TAG, "sampling": {}}))
    return sha


def _bound_ok(tag, paths, repo_root=None):
    return []


def test_endpoint_refuses_without_prereg_tag(tmp_path):
    # see test_sample_refuses_without_prereg_tag
    with pytest.raises(RuntimeError, match="preregistration tag"):
        ep.run(root=tmp_path, device="cpu", loaders={})


def test_endpoint_refuses_without_predictor_seal(tmp_path):
    with pytest.raises(RuntimeError, match="predictor seal"):
        ep.run(root=tmp_path, device="cpu", loaders={}, **_prereg())


def test_endpoint_refuses_on_drifted_blob(tmp_path):
    _write_predictor_seal(tmp_path)
    with pytest.raises(RuntimeError, match="does not bind"):
        ep.run(root=tmp_path, device="cpu", loaders={},
              blobs_bound=lambda tag, paths, repo_root=None: list(paths), **_prereg())


class WhichAwareRunner:
    def __init__(self, amap, correct_prompts):
        self.amap, self.correct_prompts = amap, correct_prompts

    def generate(self, prompts, k):
        return [self.amap[p] if p in self.correct_prompts else "zzz"
               for p in prompts]


def _endpoint_loaders(commit_stage1, commit_main, amap, correct_prompts_by_which):
    def olmo7b(commit, device):
        which = "stage1_final" if commit == commit_stage1 else "main"
        model = {"commit": commit, "which": which}
        return model, FakeTok(), {"tensor_digest": f"D-{which}"}

    def runner_factory(tok, model):
        return WhichAwareRunner(amap, correct_prompts_by_which[model["which"]])

    return {"olmo7b": olmo7b, "runner": runner_factory}


def _full_amap_and_correct(hit_rungs):
    """Built over the REAL, full 34-rung battery (`bt.load_battery()`),
    not a monkeypatched subset: `bg.load_floors()` cross-checks that
    its floors cover exactly `bt.RUNGS`, so `endpoint_2i.run` — which
    hard-codes `tuple(bt.RUNGS)`, per the brief, no `rungs=` override —
    cannot be exercised with a shrunk rung set. This stays fast:
    building 34 rungs' prompts is pure string formatting, no torch."""
    from harness import render_prompt
    battery = bt.load_battery()
    amap, correct = {}, set()
    for r, cap in battery.items():
        shots = [tuple(s) for s in cap["shots"]][:bg.N_SHOTS]
        for it in cap["eval_items"]:
            p = render_prompt(it["question"], shots)
            amap[p] = str(it["answer"])
            if r in hit_rungs:
                correct.add(p)
    return battery, amap, correct


def test_endpoint_writes_both_records_and_rung_set_from_stage1_final(tmp_path):
    _write_predictor_seal(tmp_path, sha="SEALSHA-1")
    manifest = _manifest()
    commit_stage1 = bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B)["commit"]
    commit_main = bi.entry_main(manifest, bi.REPO_7B)["commit"]

    battery, amap, all_correct = _full_amap_and_correct(SMALL_RUNGS)
    loaders = _endpoint_loaders(commit_stage1, commit_main, amap,
                               {"stage1_final": all_correct, "main": set()})

    ep.run(root=tmp_path, device="cpu", loaders=loaders,
          blobs_bound=_bound_ok, **_prereg())

    for rung in SMALL_RUNGS:
        for which in ("stage1_final", "main"):
            p = bi.endpoint_record_path(tmp_path, which, rung)
            assert p.is_file()
            rec = json.loads(p.read_text())
            assert rec["which"] == which and "step" not in rec
            assert rec["family"] == "olmo2" and rec["size"] == bi.SIZE_OUT
            assert rec["predictor_sha"] == "SEALSHA-1"
            assert rec["seal_tag"] == bi.PREDICTOR_SEAL_TAG
        stage1_rec = json.loads(
            bi.endpoint_record_path(tmp_path, "stage1_final", rung).read_text())
        main_rec = json.loads(
            bi.endpoint_record_path(tmp_path, "main", rung).read_text())
        assert stage1_rec["correct"] == 500
        assert main_rec["correct"] == 0

    rung_set = json.loads(bi.rung_set_path(tmp_path).read_text())
    assert rung_set["R_OLMO"] == ["antonym", "antonym6", "clock24"]
    assert rung_set["R_CAP"] == ["antonym", "antonym6"]
    assert rung_set["R_EXTRA"] == ["clock24"]
    assert set(rung_set["endpoint_file_sha256"]) == {
        f"results/endpoint/{which}/{r}.json"
        for which in ("stage1_final", "main") for r in bt.RUNGS}


def test_endpoint_skip_if_exists_and_dry_run(tmp_path):
    _write_predictor_seal(tmp_path, sha="SEALSHA-2")
    manifest = _manifest()
    commit_stage1 = bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B)["commit"]
    commit_main = bi.entry_main(manifest, bi.REPO_7B)["commit"]
    battery, amap, all_correct = _full_amap_and_correct(bt.RUNGS)
    loaders = _endpoint_loaders(commit_stage1, commit_main, amap,
                               {"stage1_final": all_correct, "main": all_correct})

    def boom(commit, device):
        raise AssertionError("must not be called during dry run")

    ep.run(root=tmp_path, device="cpu", loaders={"olmo7b": boom}, dry_run=True,
          blobs_bound=_bound_ok, **_prereg())
    assert not bi.endpoint_record_path(tmp_path, "stage1_final", "antonym").exists()

    ep.run(root=tmp_path, device="cpu", loaders=loaders, blobs_bound=_bound_ok,
          **_prereg())
    assert bi.endpoint_record_path(tmp_path, "stage1_final", "antonym").exists()

    def boom_loader(*a, **k):
        raise AssertionError("must not load a model when nothing is pending")
    ep.run(root=tmp_path, device="cpu", loaders={"olmo7b": boom_loader},
          blobs_bound=_bound_ok, **_prereg())


def _write_endpoint_records(root, which, rungs, *, correct, seal_sha):
    """Fabricates valid `which`-records directly via `item_record_2i`
    (already covered by its own tests) — fast, no `evaluate_items`/
    battery machinery needed, for tests whose focus is the per-`which`
    skip (finding 2), not the eval path itself."""
    for rung in rungs:
        cap = bt.load_item_file(rung)
        n = bt.N_ITEMS
        ev = {"bits": [1] * correct + [0] * (n - correct), "correct": correct,
             "continuations": ["x"] * n}
        ckpt = {"revision": which, "commit": "C", "kind": "thin-loader", "files": [],
               "weight_sha256": "D", "config_source": "cs", "tokenizer_source": "ts"}
        rec = ep.item_record_2i(rung=rung, family=bi.FAMILY, size=bi.SIZE_OUT,
                               which=which, cap=cap, ev=ev, ckpt=ckpt,
                               seal={"tag": bi.PREDICTOR_SEAL_TAG, "sha256": seal_sha},
                               t_s=0.0)
        p = bi.endpoint_record_path(root, which, rung)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec, indent=1))


def test_endpoint_per_which_skip_stage1_final_present_main_absent(tmp_path):
    """Finding 2: a `which` with every rung already present must not
    load a model at all; the other `which` still does, exactly once."""
    _write_predictor_seal(tmp_path, sha="SEALSHA-3")
    _write_endpoint_records(tmp_path, "stage1_final", bt.RUNGS, correct=500,
                            seal_sha="SEALSHA-3")
    manifest = _manifest()
    commit_stage1 = bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B)["commit"]
    commit_main = bi.entry_main(manifest, bi.REPO_7B)["commit"]
    battery, amap, all_correct = _full_amap_and_correct(bt.RUNGS)

    calls = []

    def olmo7b(commit, device):
        calls.append(commit)
        if commit == commit_stage1:
            raise AssertionError("stage1_final is fully present — must not load it")
        return ({"commit": commit, "which": "main"}, FakeTok(),
               {"tensor_digest": "D-main"})

    loaders = {"olmo7b": olmo7b,
              "runner": lambda tok, model: WhichAwareRunner(amap, all_correct)}

    ep.run(root=tmp_path, device="cpu", loaders=loaders, blobs_bound=_bound_ok,
          **_prereg())

    assert calls == [commit_main]
    for rung in bt.RUNGS:
        assert bi.endpoint_record_path(tmp_path, "main", rung).exists()
    rung_set = json.loads(bi.rung_set_path(tmp_path).read_text())
    assert set(rung_set["R_OLMO"]) == set(bt.RUNGS)   # 500/500 clears every floor


def test_endpoint_per_which_skip_both_present_writes_rung_set_no_loader(tmp_path):
    """Finding 2, the second case: both revisions fully present, only
    the rung set missing — the loader must never be called, and the
    rung set is still written from the read-back records."""
    _write_predictor_seal(tmp_path, sha="SEALSHA-4")
    _write_endpoint_records(tmp_path, "stage1_final", bt.RUNGS, correct=500,
                            seal_sha="SEALSHA-4")
    _write_endpoint_records(tmp_path, "main", bt.RUNGS, correct=0,
                            seal_sha="SEALSHA-4")
    assert not bi.rung_set_path(tmp_path).exists()

    def boom(commit, device):
        raise AssertionError("loader must not be called when every record exists")

    ep.run(root=tmp_path, device="cpu", loaders={"olmo7b": boom},
          blobs_bound=_bound_ok, **_prereg())

    rung_set = json.loads(bi.rung_set_path(tmp_path).read_text())
    assert set(rung_set["R_OLMO"]) == set(bt.RUNGS)


def test_endpoint_seal_check_passes_exact_repo_relative_paths(tmp_path):
    """Finding 3: `_require_predictor_seal` must hand `blobs_bound`
    EXACTLY the seal file + all 34 draws files + all 34 record files,
    as paths relative to `repo_root` — not a narrowed or approximate
    set. A tmp `root` nested under a (separate) tmp `repo_root`, so a
    correct implementation cannot get away with `root == repo_root`."""
    repo_root = tmp_path / "repo"
    root = repo_root / "experiments" / "exp2i"
    files = {}
    for rung in bt.RUNGS:
        files[str(bi.predictor_draws_path(root, rung).relative_to(root))] = f"d_{rung}"
        files[str(bi.predictor_record_path(root, rung).relative_to(root))] = f"r_{rung}"
    _write_predictor_seal(root, files=files, sha="SEALSHA-5")

    received = {}

    def recording_bound(tag, paths, repo_root=None):
        received["tag"], received["paths"] = tag, list(paths)
        received["repo_root"] = repo_root
        return []

    ep._require_predictor_seal(root, blobs_bound=recording_bound, repo_root=repo_root)

    assert received["tag"] == bi.PREDICTOR_SEAL_TAG
    assert received["repo_root"] == repo_root
    prefix = "experiments/exp2i"
    expected = {f"{prefix}/results/predictor/predictor_2i.json"} | \
        {f"{prefix}/{k}" for k in files}
    assert len(files) == 2 * len(bt.RUNGS)          # sanity: 34 draws + 34 records
    assert set(received["paths"]) == expected
    assert len(received["paths"]) == len(expected)  # no duplicates


def test_item_record_2i_requires_exactly_one_of_step_which():
    with pytest.raises(ValueError, match="exactly one"):
        ep.item_record_2i(rung="antonym", family="olmo2", size="olmo7b",
                          cap={"items_sha256": "x", "answer_type": "word"},
                          ev={"bits": [], "correct": 0, "continuations": []},
                          ckpt={"revision": "main", "commit": "c", "kind": "k"},
                          seal={"tag": "t", "sha256": "s"}, t_s=0.0)
    with pytest.raises(ValueError, match="exactly one"):
        ep.item_record_2i(rung="antonym", family="olmo2", size="olmo7b",
                          cap={"items_sha256": "x", "answer_type": "word"},
                          ev={"bits": [], "correct": 0, "continuations": []},
                          ckpt={"revision": "main", "commit": "c", "kind": "k"},
                          seal={"tag": "t", "sha256": "s"}, t_s=0.0,
                          step=5, which="main")


# ------------------------------------------------------------- seal_2i

def _sample_small_rungs(tmp_path, rungs, hit_fraction_by_rung):
    battery = {r: bt.load_item_file(r) for r in rungs}
    loaders = {"olmo1b": lambda commit, device: (object(), FakeTok(),
                                                 {"tensor_digest": "D"})}
    for rung in rungs:
        fake_sampler = _make_fake_sampler(battery, hit_fraction_by_rung[rung])
        smp.run(root=tmp_path, device="cpu", rungs=(rung,), loaders=loaders,
               sampler=fake_sampler, **_prereg())
    return battery


def test_seal_refuses_if_already_sealed(tmp_path):
    p = bi.predictor_seal_path(tmp_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{}")
    with pytest.raises(RuntimeError, match="already sealed"):
        seal.seal_predictor(tmp_path)


def test_seal_refuses_missing_rungs(tmp_path, monkeypatch):
    monkeypatch.setattr(bt, "RUNGS", SMALL_RUNGS)
    _sample_small_rungs(tmp_path, ("antonym",), {"antonym": 1.0})
    with pytest.raises(RuntimeError, match="missing a draws\\+record pair"):
        seal.seal_predictor(tmp_path)


def test_seal_writes_predictor_2i_json(tmp_path, monkeypatch):
    monkeypatch.setattr(bt, "RUNGS", SMALL_RUNGS)
    hits = {"antonym": 1.0, "antonym6": 0.0, "clock24": 0.5}
    battery = _sample_small_rungs(tmp_path, SMALL_RUNGS, hits)

    rec = seal.seal_predictor(tmp_path)

    out_path = bi.predictor_seal_path(tmp_path)
    assert out_path.is_file()
    on_disk = json.loads(out_path.read_text())
    assert on_disk == rec
    assert rec["tag"] == bi.PREDICTOR_SEAL_TAG
    assert set(rec["counts"]) == set(SMALL_RUNGS)
    assert sum(1 for c in rec["counts"]["antonym"] if c == bi.DRAWS_PER_ITEM) == 500
    assert sum(1 for c in rec["counts"]["antonym6"] if c == bi.DRAWS_PER_ITEM) == 0
    assert sum(1 for c in rec["counts"]["clock24"] if c == bi.DRAWS_PER_ITEM) == 250
    # 2 draws + 2 record files per rung = 6 files total
    assert len(rec["files"]) == 2 * len(SMALL_RUNGS)
    for relpath in rec["files"]:
        assert (Path(tmp_path) / relpath).is_file()
    sampling = rec["sampling"]
    assert sampling["size"] == bi.SIZE_PRED and sampling["repo"] == bi.REPO_1B
    assert sampling["revision"] == bi.REV_1B_ENDPOINT
    assert sampling["draws_per_item"] == bi.DRAWS_PER_ITEM
    assert sampling["stream_namespace"] == "exp3"
    # sha256 = sha over the sorted "{relpath} {sha}" lines
    import hashlib
    lines = "\n".join(f"{r} {s}" for r, s in sorted(rec["files"].items()))
    assert rec["sha256"] == hashlib.sha256(lines.encode()).hexdigest()

    # re-refuses once sealed
    with pytest.raises(RuntimeError, match="already sealed"):
        seal.seal_predictor(tmp_path)


def test_seal_refuses_a_record_from_the_wrong_checkpoint(tmp_path, monkeypatch):
    """FREEZE F-1, the runner side: the seal is what the predictor tag
    binds, so a stage-1 run against the wrong checkpoint / item file /
    protocol is refused HERE, before the tag exists — through the SAME
    function the frozen verdict applies (`analyze_2i
    .predictor_record_failures_2i`), not a second copy."""
    monkeypatch.setattr(bt, "RUNGS", SMALL_RUNGS)
    hits = {r: 0.5 for r in SMALL_RUNGS}
    _sample_small_rungs(tmp_path, SMALL_RUNGS, hits)
    p = bi.predictor_record_path(tmp_path, SMALL_RUNGS[0])
    rec = json.loads(p.read_text())
    rec["revision"] = "main"
    p.write_text(json.dumps(rec))
    with pytest.raises(RuntimeError, match="provenance failure"):
        seal.seal_predictor(tmp_path)
    assert not bi.predictor_seal_path(tmp_path).exists()


def test_seal_refuses_a_record_whose_items_moved(tmp_path, monkeypatch):
    monkeypatch.setattr(bt, "RUNGS", SMALL_RUNGS)
    _sample_small_rungs(tmp_path, SMALL_RUNGS, {r: 0.5 for r in SMALL_RUNGS})
    p = bi.predictor_record_path(tmp_path, SMALL_RUNGS[1])
    rec = json.loads(p.read_text())
    rec["items_sha256"] = "de" * 32
    p.write_text(json.dumps(rec))
    with pytest.raises(RuntimeError, match="provenance failure"):
        seal.seal_predictor(tmp_path)


# ---------------------------------------------------------- preflight_2i

class PreflightRunner:
    def __init__(self, amap):
        self.amap = amap

    def generate(self, prompts, k):
        return [self.amap[p] for p in prompts]


def test_preflight_writes_nothing_under_results(tmp_path, capsys):
    from harness import render_prompt
    battery = {r: bt.load_item_file(r) for r in pf.PREFLIGHT_RUNGS}
    amap = {}
    for r, cap in battery.items():
        shots = [tuple(s) for s in cap["shots"]][:bt.N_SHOTS]
        for it in cap["eval_items"][:pf.N_ITEMS_PREFLIGHT]:
            amap[render_prompt(it["question"], shots)] = str(it["answer"])

    loaders = {"olmo1b_main": lambda commit, device: (object(), FakeTok(), {}),
              "runner": lambda tok, model: PreflightRunner(amap)}

    # pre-existing, unrelated file under results/ — must survive untouched
    pre = Path(tmp_path) / "results" / "unrelated.txt"
    pre.parent.mkdir(parents=True, exist_ok=True)
    pre.write_text("keep")

    pf.run(root=tmp_path, device="cpu", loaders=loaders)

    assert pre.read_text() == "keep"
    written = [p for p in (Path(tmp_path) / "results").rglob("*")
              if p.is_file() and p != pre]
    assert written == []
    out = capsys.readouterr().out
    assert "verify=1" in out


def test_preflight_checks_tokenizer(tmp_path):
    class BadTok(FakeTok):
        padding_side = "right"

    loaders = {"olmo1b_main": lambda commit, device: (object(), BadTok(), {}),
              "runner": lambda tok, model: PreflightRunner({})}
    with pytest.raises(RuntimeError, match="padding_side"):
        pf.run(root=tmp_path, device="cpu", loaders=loaders, rungs=(), n_items=0)
