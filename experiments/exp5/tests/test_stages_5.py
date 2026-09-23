# experiments/exp5/tests/test_stages_5.py
import json
import os
import subprocess
from pathlib import Path

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2d import analyze_2d as a2d
from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5
from experiments.exp5 import collect_5 as c5
from experiments.exp5.run import finals_5 as fin
from experiments.exp5.run import preflight_5 as pf5
from experiments.exp5.run import s9_mac_5 as s9
from experiments.exp5.run import sweep_5 as sw
from experiments.exp5 import search_5 as se
from experiments.exp5.tests import fakes_5 as fk

SIZES = ("1b", "2.8b", "6.9b")
AVAIL = tuple(range(1000, 17000, 1000)) + (143000,)
SPINE = (1000, 4000, 16000, 143000)


def _loss(size, step):
    base = {"1b": 2.6, "2.8b": 2.3, "6.9b": 2.1}[size]
    return base + 30.0 / (step ** 0.5)


def _count(size, step, rung):
    if rung not in ("antonym", "antonym6", "arith_next"):
        return 0
    return min(500, int(80 + 120 * (1 - 1 / (1 + step / 5000))))


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(b5, "SIZES_5", SIZES)
    monkeypatch.setattr(b5, "PAIRS_5", tuple((s, L) for i, s in enumerate(SIZES) for L in SIZES[i + 1:]))
    monkeypatch.setattr(b5, "SMALL_SIDES_5", SIZES[:-1])
    monkeypatch.setattr(b5, "LARGE_SIDES_5", SIZES[1:])
    monkeypatch.setattr(b5, "SPINE_5", SPINE)
    monkeypatch.setattr(b5, "GATE1_INTERIOR_5", {})
    monkeypatch.setattr(b5, "GATE1_REFERENT_SOURCE_5", {})
    monkeypatch.setattr(b5, "FROZEN_SHA256_5", {})
    monkeypatch.setattr(b5, "IMPORTED_SHA256_5", {})
    monkeypatch.setattr(b5, "check_imports_5", lambda: None)   # pinned at Task 6; a no-op here
    # analyze_5.py/power_5.py are Task 5/6 deliverables, not yet on disk at Task 4 —
    # `require_prereg_5`'s `blobs` keyword-default is bound to INSTRUMENT_BLOBS_5 at DEFINITION
    # time (module import), so patching the module attribute alone does not reach it; wrap the
    # function so `finals_5.run`/`sweep_5.run`'s un-parameterized call (they never pass `blobs=`)
    # is exercised over the files the build has BY THIS TASK's end (parallels the check_imports_5
    # override above, same reason).
    _orig_require_prereg_5 = b5.require_prereg_5
    _blobs_so_far = tuple(p for p in b5.INSTRUMENT_BLOBS_5
                          if p not in ("experiments/exp5/analyze_5.py", "experiments/exp5/power_5.py"))
    monkeypatch.setattr(b5, "require_prereg_5",
                        lambda *, tag_exists=None, blob_sha=None, blobs=_blobs_so_far:
                        _orig_require_prereg_5(tag_exists=tag_exists, blob_sha=blob_sha, blobs=blobs))
    monkeypatch.setattr(b5, "S11_STEP_5", 15000)
    man = fk.synthetic_manifest(SIZES, AVAIL)
    battery = bt.load_battery()
    loaders, state = fk.make_loaders(battery, loss_fn=_loss, count_fn=_count,
                                     pythia_2c_count_fn=_count, loss_2c_fn=_loss)
    prereg = dict(tag_exists=lambda t: True, blob_sha=lambda t, r: bg.sha256_file(b5.REPO / r))
    common = dict(root=tmp_path, cache_root=tmp_path, device="cuda", loaders=loaders,
                  manifest=man, sl=fk.small_slice(), host_meta=fk.fake_host(),
                  git_sha="g1", **prereg)
    return dict(common=common, state=state, root=tmp_path, battery=battery)


def _seal_ok(root, tag_exists=None, blobs_bound=None):
    return {"tag": b5.TARGETS_SEAL_TAG_5, "n_paths": 0, "failures": []}


def test_finals_refuses_without_the_prereg_tag(env):
    c = dict(env["common"]); c["tag_exists"] = lambda t: False
    with pytest.raises(RuntimeError, match="does not exist"):
        fin.run(**c)


def test_finals_writes_host_gate1a_gate1b_and_seven_finals(env):
    fin.run(**env["common"])
    root = env["root"]
    host = json.loads(b5.host_record_path_5(root).read_text())
    assert b5.host_record_failures_5(host) == []
    g1a = json.loads(b5.gate1a_path_5(root).read_text())
    assert g1a["pass"] and g1a["digests_equal"] and g1a["loss_equal"] and \
        all(v == 0 for v in g1a["continuation_diffs"].values()) and \
        all(v == 500 for v in g1a["continuations_compared"].values())
    g1b = json.loads(b5.gate1b_path_5(root).read_text())
    assert g1b["pass"] and g1b["no_referent"] == list(SIZES)     # GATE1_REFERENT_SOURCE_5 emptied
    for size in SIZES:
        assert b5.unit_complete_5(root, size, b5.FINAL_STEP_5)
    table = json.loads(b5.loss_table_path_5(root).read_text())
    assert set(table) == set(SIZES) and all("143000" in table[s] for s in SIZES)
    assert env["state"]["loaded"].count(("2.8b", 143000)) == 1       # gate 1(a)'s path b IS the unit


def test_finals_halts_on_a_gate1a_digest_mismatch(env):
    c = dict(env["common"])
    loaders, _ = fk.make_loaders(env["battery"], loss_fn=_loss, count_fn=_count,
                                 pythia_2c_count_fn=_count, loss_2c_fn=_loss, pythia_2c_digest="other")
    c["loaders"] = loaders
    with pytest.raises(SystemExit):
        fin.run(**c)
    assert b5.halt_marker_path_5(env["root"], "2.8b").exists()
    assert not b5.gate1a_path_5(env["root"]).is_file() or \
        not json.loads(b5.gate1a_path_5(env["root"]).read_text())["pass"]


def test_finals_gate1a_catches_a_per_doc_loss_mismatch_with_equal_aggregate(env):
    """Task 6 mutation kill: gate 1(a)'s `loss_equal` requires the
    per-document loss lists to match too, not only the aggregate scalar
    — a mutant that drops the per_doc_loss comparison would read two
    paths with an identical mean but a genuinely different per-token
    computation as equal."""
    c = dict(env["common"])
    base_loaders = dict(c["loaders"])

    def custom_loss(model, sl, *, batch_size, device):
        n_docs = len(sl["offsets"]) - 1
        per_set = {name: {"loss": 2.5, "n_tokens": 0} for name in sl["set_names"]}
        for d in range(n_docs):
            per_set[sl["set_names"][int(sl["set_index"][d])]]["n_tokens"] += \
                int(sl["offsets"][d + 1] - sl["offsets"][d] - 1)
        per_doc = [2.5] * n_docs
        if model.get("path") != "a":                # the candidate path only
            per_doc[0] = 2.5001
        return {"loss": 2.5, "n_scored": sl["meta"]["n_scored"], "n_docs": n_docs,
                "per_set": per_set, "per_doc_loss": per_doc, "finite": True, "n_nonfinite": 0,
                "batch_size": batch_size, "pad_id": b5.PAD_ID_5, "logits_dtype": "float16",
                "log_softmax_dtype": "float32", "accumulation": "fake",
                "slice_sha256": sl["sha256"], "seconds": 0.0}
    c["loaders"] = {**base_loaders, "loss": custom_loss}
    with pytest.raises(SystemExit):
        fin.run(**c)
    assert b5.halt_marker_path_5(env["root"], "2.8b").exists()
    g1a = json.loads(b5.gate1a_path_5(env["root"]).read_text())
    assert g1a["loss_2c_path"] == g1a["loss_candidate_path"] == 2.5      # aggregate agrees
    assert g1a["loss_equal"] is False                                   # per_doc_loss disagrees
    assert g1a["per_doc_diffs"] == 1


def test_finals_halts_on_a_gate1b_tolerance_failure(env, monkeypatch):
    monkeypatch.setattr(b5, "GATE1_REFERENT_SOURCE_5", {"1b": "fake"})
    monkeypatch.setattr(b5, "mac_final_counts_5",
                        lambda size: ({r: 0 for r in bt.RUNGS} if size == "1b" else None))
    with pytest.raises(SystemExit):
        fin.run(**env["common"])
    assert b5.halt_marker_path_5(env["root"], "1b").exists()
    g1b = json.loads(b5.gate1b_path_5(env["root"]).read_text())
    assert not g1b["pass"] and any("antonym" in f for f in g1b["failures"])


def test_finals_host_record_is_write_once_and_stack_checked(env):
    fin.run(**env["common"])
    c = dict(env["common"]); c["host_meta"] = {**fk.fake_host(), "stack": {**fk.fake_host()["stack"], "torch": "9.9"}}
    with pytest.raises(RuntimeError, match="host record"):
        fin.run(**c)


def _sweep_kwargs(env, **over):
    kw = dict(env["common"])
    kw.update(dict(seal_check=_seal_ok, projection_commit="p1", is_ancestor=lambda a, b: True,
                   power_present=True))
    kw.update(over)
    return kw


def test_sweep_refuses_without_finals_seal_power_or_projection(env):
    fin.run(**env["common"])
    with pytest.raises(RuntimeError, match="seal"):
        sw.run(size="2.8b", **_sweep_kwargs(env, seal_check=lambda r, **k: {"failures": ["x"]}))
    with pytest.raises(RuntimeError, match="power"):
        sw.run(size="2.8b", **_sweep_kwargs(env, power_present=False))
    with pytest.raises(RuntimeError, match="projection"):
        sw.run(size="2.8b", **_sweep_kwargs(env, projection_commit=None))
    with pytest.raises(RuntimeError, match="projection"):
        sw.run(size="2.8b", **_sweep_kwargs(env, is_ancestor=lambda a, b: False))


def test_sweep_spine_then_brackets_then_windows_then_s11(env):
    fin.run(**env["common"])
    sw.run(size="2.8b", **_sweep_kwargs(env))
    root = env["root"]
    log = json.loads(b5.search_log_path_5(root, "2.8b").read_text())
    assert log["spine"] == list(SPINE)
    assert [r["step"] for r in log["requests"][:len(SPINE) - 1]] == list(SPINE[:-1])
    pair = log["pairs"]["1b"]
    assert pair["status"] == "done"
    lo, hi = pair["plan"]["bracket"]
    losses = {int(k): v["loss"] for k, v in json.loads(b5.loss_table_path_5(root).read_text())["2.8b"].items()}
    assert losses[lo] >= pair["target"] > losses[hi] and hi - lo == 1000
    for s in pair["plan"]["b_minus"] + pair["plan"]["b_plus"] + [lo, hi]:
        assert b5.unit_complete_5(root, "2.8b", s)
    assert log["s11"]["step"] == 15000 and b5.unit_complete_5(root, "2.8b", 15000)
    # nothing else loaded: every unit on disk is named by the spine, the pair, the final or S11
    named = set(SPINE) | {lo, hi} | set(pair["plan"]["b_minus"]) | set(pair["plan"]["b_plus"]) \
        | set(pair["plan"]["bisected"]) | {15000}
    on_disk = {int(p.name[4:]) for p in (b5.units_root_5(root) / "2.8b").iterdir() if p.name.startswith("step")}
    assert on_disk == named


def test_sweep_of_a_size_that_is_never_a_large_side_loads_only_s11(env):
    """Freeze F-1: run/campaign_5.sh runs sweep_5 for the smallest size too
    (S11 only). Before the closure the runner loaded that size's whole
    spine, eight units gate 4 names nowhere (expected_steps_5 gives a
    size that is never a large side {final, S11} only) — every campaign
    verdict INSUFFICIENT_DATA."""
    from experiments.exp5 import analyze_5 as an
    fin.run(**env["common"])
    n = len(env["state"]["loaded"])
    smallest = b5.SIZES_5[0]
    assert smallest not in b5.LARGE_SIDES_5
    sw.run(size=smallest, **_sweep_kwargs(env))
    assert env["state"]["loaded"][n:] == [(smallest, b5.S11_STEP_5)]
    root = env["root"]
    on_disk = {int(p.name[4:]) for p in (b5.units_root_5(root) / smallest).iterdir()
               if p.name.startswith("step")}
    assert on_disk == {b5.FINAL_STEP_5, b5.S11_STEP_5}
    units = {smallest: {"losses": {}}}
    assert on_disk <= an.expected_steps_5(units, env["common"]["manifest"], smallest)


def test_units_refuse_a_checkpoint_or_unit_record_from_another_host(env):
    """Freeze F-3: gate 0's per-unit host comparison covered _loss and the
    rung records only; a _checkpoint.json (or _unit.json) naming another
    stack/host passed."""
    from experiments.exp5 import analyze_5 as an
    fin.run(**env["common"])
    root = env["root"]
    host = json.loads(b5.host_record_path_5(root).read_text())
    kw = dict(manifest=env["common"]["manifest"], battery=env["battery"], verify_fn=a2d.load_verify(),
              host=host, slice_sha=env["common"]["sl"]["sha256"],
              n_scored=env["common"]["sl"]["meta"]["n_scored"])
    an.load_units_5(root, "1b", **kw)                             # clean
    d = b5.unit_dir_5(root, "1b", b5.FINAL_STEP_5)

    def restamp():
        u = json.loads((d / "_unit.json").read_text())
        u["files"] = {n: bg.sha256_file(d / n) for n in u["files"]}
        (d / "_unit.json").write_text(json.dumps(u))
    ck = json.loads((d / "_checkpoint.json").read_text())
    (d / "_checkpoint.json").write_text(json.dumps({**ck, "stack": {**ck["stack"], "torch": "2.13.0"}}))
    restamp()
    with pytest.raises(ValueError, match="_checkpoint: stack"):
        an.load_units_5(root, "1b", **kw)
    (d / "_checkpoint.json").write_text(json.dumps(ck)); restamp()
    u = json.loads((d / "_unit.json").read_text())
    (d / "_unit.json").write_text(json.dumps({**u, "host_sha256": "x"}))
    with pytest.raises(ValueError, match="_unit.json: host_sha256"):
        an.load_units_5(root, "1b", **kw)


def test_a_non_finite_unit_loss_halts_the_size(env, monkeypatch):
    """Freeze F-7 (ruling B-3(b)): the first non-finite loss on any unit halts
    the size at that unit — HALTED marker naming it, unit incomplete, the
    checkpoint freed, exit 2 — and the analyzer's halt-marker route refuses."""
    fin.run(**env["common"])
    bad_step = SPINE[1]
    loaders = dict(env["common"]["loaders"])
    orig = loaders["loss"]

    def nan_loss(model, sl, *, batch_size, device):
        out = orig(model, sl, batch_size=batch_size, device=device)
        if model["size"] == "2.8b" and model["step"] == bad_step:
            out = {**out, "loss": float("nan"), "finite": False, "n_nonfinite": 7}
        return out
    loaders["loss"] = nan_loss
    kw = _sweep_kwargs(env)
    kw["loaders"] = loaders
    with pytest.raises(SystemExit) as ex:
        sw.run(size="2.8b", **kw)
    assert ex.value.code == 2
    root = env["root"]
    marker = b5.halt_marker_path_5(root, "2.8b")
    assert marker.is_file() and f"step{bad_step}" in marker.read_text() and "n_nonfinite 7" in marker.read_text()
    assert b5.loss_record_path_5(root, "2.8b", bad_step).is_file()
    assert not b5.unit_record_path_5(root, "2.8b", bad_step).exists()
    assert not b5.unit_complete_5(root, "2.8b", bad_step)
    assert ("2.8b", bad_step) in env["state"]["freed"]
    assert not any(b5.rung_record_path_5(root, "2.8b", bad_step, r).exists() for r in b5.RUNGS)
    with pytest.raises(RuntimeError, match="halted"):
        sw.run(size="2.8b", **_sweep_kwargs(env))
    from experiments.exp5 import analyze_5 as an
    v = an.run(root=root, manifest=env["common"]["manifest"], sl=env["common"]["sl"], n_sample=50, n_boot=20,
               tag_exists=lambda t: True, blob_sha=lambda t, r: bg.sha256_file(b5.REPO / r),
               blobs_bound=lambda t, p, **k: [], projection_commit="p1", is_ancestor=lambda a, b: True,
               seal_tag_commit="s1", referents_sha=False, imports_pinned=False,
               frozen_check=lambda: None, power_gate="skip")
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any(f.startswith("5 halt marker") and f"step{bad_step}" in f for f in v["failures"])


def test_sweep_reuses_units_across_partners_and_records_it(env):
    fin.run(**env["common"])
    sw.run(size="6.9b", **_sweep_kwargs(env))
    root = env["root"]
    manifest = env["common"]["manifest"]
    log = json.loads(b5.search_log_path_5(root, "6.9b").read_text())
    # RULING A: `requested_all` is the complete replay (spine + bisect + window, in order),
    # each step marked "loaded" (this pair's own request() calls, in `requests`) or "reused"
    # (plan_5 found it already known — the spine, or the pre-loaded final). The plain
    # `requests` list stays loaded-only, so it alone never shows "reused" (confirmed structural
    # in the Task 4 report); `requested_all` is where both actions are visible.
    actions = [r["action"] for pair in log["pairs"].values() for r in pair["requested_all"]]
    assert "reused" in actions and "loaded" in actions
    assert set(log["pairs"]) == {"1b", "2.8b"}
    loaded = env["state"]["loaded"]
    assert len(loaded) == len(set(loaded))            # no unit loaded twice

    # gate 4's identity: requested_all reproduces exactly what a fresh reader of the COMMITTED
    # loss table (not the in-memory losses the run used) would replay, for every done pair.
    avail = b5.available_5(manifest, "6.9b")
    spine = b5.spine_5(manifest, "6.9b")
    table = json.loads(b5.loss_table_path_5(root).read_text())["6.9b"]
    losses_committed = {int(k): v["loss"] for k, v in table.items()}
    for small, pair in log["pairs"].items():
        if pair["status"] != "done":
            continue
        rep = se.replay_5(losses_committed, avail, spine, pair["target"])
        assert [r["step"] for r in pair["requested_all"]] == se.requested_steps_5(rep)


def test_sweep_drops_a_pair_the_large_model_never_reaches(env, monkeypatch):
    fin.run(**env["common"])
    # make 1b's final loss LOWER than anything 2.8b reaches
    p = b5.loss_record_path_5(env["root"], "1b", b5.FINAL_STEP_5)
    rec = json.loads(p.read_text()); rec["loss"] = 0.5
    for v in rec["per_set"].values():
        v["loss"] = 0.5
    p.write_text(json.dumps(rec))
    unit = json.loads(b5.unit_record_path_5(env["root"], "1b", b5.FINAL_STEP_5).read_text())
    unit["files"]["_loss.json"] = bg.sha256_file(p)
    b5.unit_record_path_5(env["root"], "1b", b5.FINAL_STEP_5).write_text(json.dumps(unit))
    c5.rebuild_loss_table_5(env["root"])
    sw.run(size="2.8b", **_sweep_kwargs(env))
    log = json.loads(b5.search_log_path_5(env["root"], "2.8b").read_text())
    assert log["pairs"]["1b"]["status"] == "dropped"


def test_sweep_resumes_and_refuses_when_halted(env):
    fin.run(**env["common"])
    sw.run(size="2.8b", **_sweep_kwargs(env))
    n = len(env["state"]["loaded"])
    sw.run(size="2.8b", **_sweep_kwargs(env))          # idempotent: nothing new loaded
    assert len(env["state"]["loaded"]) == n
    b5.halt_marker_path_5(env["root"], "2.8b").write_text("x\n")
    with pytest.raises(RuntimeError, match="halted"):
        sw.run(size="2.8b", **_sweep_kwargs(env))


def test_sweep_dry_run_writes_nothing(env):
    fin.run(**env["common"])
    before = {p for p in env["root"].rglob("*")}
    sw.run(size="2.8b", dry_run=True, **_sweep_kwargs(env))
    assert {p for p in env["root"].rglob("*")} == before


def test_sweep_gate1c_halts_on_tolerance(env, monkeypatch):
    fin.run(**env["common"])
    monkeypatch.setattr(b5, "GATE1_INTERIOR_5", {"2.8b": (1000, 4000)})
    monkeypatch.setattr(b5, "mac_interior_counts_5", lambda size, step: {r: 400 for r in bt.RUNGS})
    with pytest.raises(SystemExit):
        sw.run(size="2.8b", **_sweep_kwargs(env))
    g = json.loads(b5.gate1c_path_5(env["root"], "2.8b").read_text())
    assert not g["pass"] and b5.halt_marker_path_5(env["root"], "2.8b").exists()


def test_sweep_prefetches_spine_and_window_steps_but_never_bisected(env):
    fin.run(**env["common"])
    sw.run(size="2.8b", **_sweep_kwargs(env))
    root = env["root"]
    log = json.loads(b5.search_log_path_5(root, "2.8b").read_text())
    prefetched = set(env["state"]["prefetched"])
    # Every spine step after the first — except the spine's own last point,
    # which is FINAL_STEP_5: fin.run() above already completed that unit,
    # so the completeness guard suppresses its prefetch (nothing to fetch).
    for s in SPINE[1:-1]:
        assert ("2.8b", b5.revision_of_5(s)) in prefetched
    assert ("2.8b", b5.revision_of_5(SPINE[-1])) not in prefetched
    for pair in log["pairs"].values():
        window_reqs = [r["step"] for r in pair["requests"] if r["why"] == "window"]
        for s in window_reqs[1:]:                     # every WINDOW step after the first
            assert ("2.8b", b5.revision_of_5(s)) in prefetched
        for r in pair["requests"]:                     # NO bisected step is ever prefetched
            if r["why"] == "bisect":
                assert ("2.8b", b5.revision_of_5(r["step"])) not in prefetched


def test_the_next_steps_prefetch_overlaps_the_current_units_scoring(env, monkeypatch):
    """Freeze F-8 (ruling): run_unit_5 joins the prefetcher only when the
    in-flight download is the unit it is about to load. The next spine
    step's prefetch starts BEFORE the current unit's rungs are scored and is
    joined only after them (before the next unit loads); before the closure
    run_unit_5 called wait() and joined it before loading the current unit."""
    import threading
    import time as _time
    fin.run(**env["common"])
    events, lock = [], threading.Lock()

    def ev(*e):
        with lock:
            events.append(e)
    base = dict(env["common"]["loaders"])

    def checkpoint(size, step, entry, **k):
        ev("load", size, int(step))
        return base["checkpoint"](size, step, entry, **k)

    def runner(tok, model):
        r = base["runner"](tok, model)
        gen = r.generate
        seen = {"n": 0}

        def generate(prompts, max_new_tokens):
            if seen["n"] == 0:
                ev("score", model["size"], model["step"])
            seen["n"] += 1
            return gen(prompts, max_new_tokens)
        r.generate = generate
        return r

    def prefetch(size, entry, cache_root):
        step = b5.FINAL_STEP_5 if entry["revision"] == "main" else int(entry["revision"][4:])
        ev("prefetch_start", size, step)
        _time.sleep(0.05)
        ev("prefetch_done", size, step)
    orig_wait = c5.Prefetcher.wait

    def wait(self):
        if self._t is not None and self.target is not None:
            ev("join", *self.target)
        return orig_wait(self)
    monkeypatch.setattr(c5.Prefetcher, "wait", wait)
    kw = _sweep_kwargs(env)
    kw["loaders"] = {**base, "checkpoint": checkpoint, "runner": runner, "prefetch": prefetch}
    sw.run(size="2.8b", **kw)
    idx = lambda e: events.index(e)
    checked = 0
    for cur, nxt in zip(SPINE[:-2], SPINE[1:-1]):          # the final is already complete
        assert idx(("prefetch_start", "2.8b", nxt)) < idx(("score", "2.8b", cur))
        j = idx(("join", "2.8b", nxt))
        assert idx(("load", "2.8b", cur)) < idx(("score", "2.8b", cur)) < j < idx(("load", "2.8b", nxt))
        checked += 1
    assert checked == len(SPINE) - 2
    pf = c5.Prefetcher(kw["loaders"], cache_root=env["root"])
    assert pf.target is None
    pf.wait_for("2.8b", 1000)                              # idle: no-op
    pf.start("2.8b", {"revision": "step2000"})
    assert pf.target == ("2.8b", 2000)
    pf.wait_for("2.8b", 1000)                              # a different step: not joined
    assert pf.target == ("2.8b", 2000)
    pf.wait_for("2.8b", 2000)                              # the same step: joined
    assert pf.target is None and pf._t is None


def test_preflight_runs_on_the_fakes_and_writes_nothing_under_results(env, tmp_path_factory):
    fin.run(**env["common"])
    root = env["root"]
    cache_root = tmp_path_factory.mktemp("preflight_cache")   # separate from root/results entirely
    before = {p for p in root.rglob("*")}
    host = c5.host_record_5("cuda", fk.fake_host()["transports"], stack=fk.fake_host()["stack"],
                            gpu="fake", python="3.11.16")
    pf5.run(root=root, cache_root=cache_root, device="cuda", loaders=env["common"]["loaders"],
           manifest=env["common"]["manifest"], sl=env["common"]["sl"], battery=env["battery"],
           verify_fn=a2d.load_verify(), host=host,
           probe_size="6.9b", probe_steps=(1000, 2000), rung="antonym", final_size="1b")
    after = {p for p in root.rglob("*")}
    assert after == before                             # nothing landed under root/ at all —
    # in particular results/host_5.json (already written by the fin.run() call above) is untouched


def test_preflight_early_warning_is_the_earliest_step_a_window_can_reach():
    """Ruling B-3(c): the preflight's early warning loads 12b step1000 and the
    earliest window member, step256 (t_lo >= spine[0] = 1000 -> B- = {256, 512});
    step1 is loadable by no window."""
    man = b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    size = pf5.PREFLIGHT_SIZE_5
    avail = b5.available_5(man, size)
    spine = b5.spine_5(man, size)
    i = avail.index(spine[0])
    earliest_window = min(avail[max(0, i - b5.N_WINDOW_SIDE_5):i])
    assert pf5.PREFLIGHT_STEPS_5 == (spine[0], earliest_window) == (1000, 256)
    assert 1 not in pf5.PREFLIGHT_STEPS_5


def test_s9_mac_writes_one_unit_with_host_record_and_tolerance(env):
    fin.run(**env["common"])
    sw.run(size="2.8b", **_sweep_kwargs(env))
    root = env["root"]
    box_counts = {r: json.loads(b5.rung_record_path_5(root, "2.8b", 4000, r).read_text())["correct"]
                 for r in bt.RUNGS}
    host = s9.mac_host_record_5(write_once_root=root, stack=fk.fake_host()["stack"],
                                gpu="fake-mac", python="3.11.16")
    assert b5.host_record_failures_5(host) == [] and host["device"] == "mps"
    assert s9.s9_host_path_5(root).is_file()
    # write-once: a second call with a DIFFERENT stack still returns the on-disk record
    host2 = s9.mac_host_record_5(write_once_root=root,
                                 stack={**fk.fake_host()["stack"], "torch": "9.9"})
    assert host2 == host
    out = s9.run(size="2.8b", step=4000, root=root, cache_root=root, device="mps",
                loaders=env["common"]["loaders"], manifest=env["common"]["manifest"],
                sl=env["common"]["sl"], host=host, box_counts=box_counts)
    d = b5.s9_dir_5(root, "2.8b", 4000)
    assert set(p.name for p in d.iterdir()) == set(b5.unit_files_5()) | {"_unit.json"}
    assert out["failures"] == []                        # identical counts against itself
    # final review M-11: the analyzer's S9 "present" path on this tree
    from experiments.exp5 import analyze_5 as an
    s9r = an._s9_cross_host_5(root)
    assert s9r["status"] == "present" and len(s9r["units"]) == 1
    u = s9r["units"][0]
    assert (u["size"], u["step"]) == ("2.8b", 4000) and u["tolerance_failures"] == [] and u["loss_diff"] == 0
    rp = d / "antonym.json"; rec = json.loads(rp.read_text())
    rp.write_text(json.dumps({**rec, "correct": rec["correct"] + 16}))
    tol = an._s9_cross_host_5(root)["units"][0]["tolerance_failures"]
    assert any("antonym: |Δ| 16" in f and f"({box_counts['antonym']} vs the Mac's "
               f"{rec['correct'] + 16})" in f for f in tol), tol
    assert not b5.unit_complete_5(root, "2.8b", 4000) or \
        b5.rung_record_path_5(root, "2.8b", 4000, "antonym").is_file()   # the campaign unit untouched


def test_a_torn_unit_is_wiped_and_rewritten_by_the_runner(env):
    """Final review M-10: a unit directory holding 30 of its 36 files and no
    _unit.json (a crash mid-unit) is discarded whole and rewritten."""
    fin.run(**env["common"])
    root, step = env["root"], SPINE[1]
    d = b5.unit_dir_5(root, "2.8b", step)
    d.mkdir(parents=True)
    names = list(b5.unit_files_5())[:30]
    for n in names:
        (d / n).write_text('{"TORN_MARKER_5": true}')
    assert not b5.unit_complete_5(root, "2.8b", step)
    sw.run(size="2.8b", **_sweep_kwargs(env))
    assert b5.unit_complete_5(root, "2.8b", step)
    assert sorted(p.name for p in d.iterdir()) == sorted(list(b5.unit_files_5()) + ["_unit.json"])
    assert not any("TORN_MARKER_5" in (d / n).read_text() for n in b5.unit_files_5())
    assert env["state"]["loaded"].count(("2.8b", step)) == 1


# ------------------------------------------------------- box shell scripts

SCRIPTS_5 = ("campaign_5.sh", "box_setup_5.sh", "pull_units_5.sh", "status_box_5.sh",
            "commit_watcher_5.sh", "rebundle_box_5.sh", "make_bundle_5.sh")


@pytest.mark.parametrize("name", SCRIPTS_5)
def test_box_script_is_syntactically_valid_bash(name):
    p = Path(__file__).resolve().parents[1] / "run" / name
    assert p.is_file(), f"{p} missing"
    r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
    assert r.returncode == 0, f"{name}: {r.stderr}"


@pytest.mark.parametrize("name", SCRIPTS_5)
def test_box_script_is_executable(name):
    p = Path(__file__).resolve().parents[1] / "run" / name
    assert p.stat().st_mode & 0o111, f"{name} is not executable"


RUN_5 = Path(__file__).resolve().parents[1] / "run"


def test_box_setup_seeds_pip_into_the_uv_venv():
    """Final review I-2: `uv venv` makes a venv without pip; every `python -m pip`
    line after it died under `set -e`."""
    txt = (RUN_5 / "box_setup_5.sh").read_text()
    venv = [ln for ln in txt.splitlines() if ln.strip().startswith("uv venv")]
    assert venv and all("--seed" in ln for ln in venv)
    assert "-m pip" in txt                     # the install lines rely on the seeded pip


def test_puller_and_watcher_never_stage_or_keep_a_partial_file():
    """Final review I-4: skip a unit only with all 37 files present; rsync
    partials outside the repo; the watcher stages by pathspec, never -A."""
    pull = (RUN_5 / "pull_units_5.sh").read_text()
    assert '-eq 37 ] && continue' in pull and '[ -f "$LOCAL/$u/_unit.json" ] && continue' not in pull
    assert pull.count('--temp-dir="$TMPD"') == 2 and "TMPD=/tmp/exp5_rsync_tmp" in pull
    watch = (RUN_5 / "commit_watcher_5.sh").read_text()
    code = [ln for ln in watch.splitlines() if not ln.lstrip().startswith("#")]
    assert not any("git add -A" in ln for ln in code)
    assert ':(glob)$WATCH_DIR/**/*.json' in watch and ':(glob)$WATCH_DIR/**/HALTED' in watch


def _git(cwd, *a):
    return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True).stdout.strip()


def _mac_and_box(tmp_path, *, tag=True, projection=True):
    mac = tmp_path / "mac"; mac.mkdir()
    _git(mac, "init", "-q", "-b", "master"); _git(mac, "config", "user.email", "a@b"); _git(mac, "config", "user.name", "a")
    fin = mac / "experiments/exp5/results/units/1b/step143000/_unit.json"
    fin.parent.mkdir(parents=True); fin.write_text("{}\n")
    (mac / "README").write_text("v1\n"); _git(mac, "add", "README"); _git(mac, "commit", "-qm", "prereg")
    b1 = tmp_path / "b1.bundle"; _git(mac, "bundle", "create", str(b1), "--all")
    box = tmp_path / "box"; subprocess.run(["git", "clone", "-q", str(b1), str(box)], check=True)
    bfin = box / "experiments/exp5/results/units/1b/step143000/_unit.json"
    bfin.parent.mkdir(parents=True); bfin.write_text("{}\n")          # the box's own untracked final
    _git(mac, "add", "-A"); _git(mac, "commit", "-qm", "finals")
    if tag:
        _git(mac, "tag", "exp5-targets-sealed")
    if projection:
        pj = mac / "experiments/exp5/projection.md"; pj.write_text("# p\n")
        _git(mac, "add", "-A"); _git(mac, "commit", "-qm", "projection")
    b2 = tmp_path / "b2.bundle"
    r = subprocess.run(["bash", str(RUN_5 / "make_bundle_5.sh"), str(b2)], capture_output=True, text=True,
                       env={**os.environ, "REPO_DIR": str(mac)})
    assert r.returncode == 0 and str(b2) in r.stdout, r.stderr
    return mac, box, b2


def test_rebundle_moves_the_box_to_the_bundles_master_with_the_seal_and_projection(tmp_path):
    """Final review I-3: the box lands on the Mac's HEAD (the old recipe stayed on
    the old commit), the seal tag present, the projection an ancestor of HEAD."""
    mac, box, b2 = _mac_and_box(tmp_path)
    r = subprocess.run(["bash", str(RUN_5 / "rebundle_box_5.sh"), str(b2)], capture_output=True, text=True,
                       env={**os.environ, "REPO_DIR": str(box)})
    assert r.returncode == 0, r.stdout + r.stderr
    assert _git(box, "rev-parse", "HEAD") == _git(mac, "rev-parse", "HEAD")
    assert "targets seal tag: exp5-targets-sealed" in r.stdout and "is an ancestor of HEAD" in r.stdout


@pytest.mark.parametrize("missing", ["tag", "projection"])
def test_rebundle_refuses_without_the_seal_tag_or_the_projection(tmp_path, missing):
    mac, box, b2 = _mac_and_box(tmp_path, tag=(missing != "tag"), projection=(missing != "projection"))
    r = subprocess.run(["bash", str(RUN_5 / "rebundle_box_5.sh"), str(b2)], capture_output=True, text=True,
                       env={**os.environ, "REPO_DIR": str(box)})
    assert r.returncode == 2 and "REFUSING" in r.stdout, r.stdout + r.stderr
