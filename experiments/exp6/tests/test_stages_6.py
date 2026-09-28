# experiments/exp6/tests/test_stages_6.py
"""The order of the stages, each rule on the smallest tree that shows
it: a stage refuses before it loads anything, and says why."""
import pytest

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import families_6 as fm
from experiments.exp6 import floors_6 as fl
from experiments.exp6 import records_6 as r6
from experiments.exp6 import referents_6 as rf
from experiments.exp6.run import _common_6 as cm
from experiments.exp6.run import endpoint_6 as ep
from experiments.exp6.run import seal_endpoint_6 as se
from experiments.exp6.run import seal_predictor_6 as sp
from experiments.exp6.run import sweep_6 as sw
from experiments.exp6.tests import _world_6 as W


_Never = W.Unreached


def _sealed_predictor(root):
    """The smallest tree a predictor seal describes: one file under
    results/predictor and the table that names it."""
    f = r6.results(root) / "predictor" / "unit.json"
    f.parent.mkdir(parents=True)
    f.write_text("{}")
    files = sp.file_table(root)
    r6.write_json(r6.seal_path(root), {"files": files,
                                       "sha256": r6.composite_sha(files)})
    return f


def test_the_predictor_seal_is_the_files_on_disk_under_the_tag(tmp_path):
    f = _sealed_predictor(tmp_path)
    ok = dict(tag_exists=W.tag_exists, blobs_bound=W.blobs_bound)
    seal = ep.require_predictor_seal(tmp_path, **ok)
    assert list(seal["files"]) == ["results/predictor/unit.json"]
    with pytest.raises(RuntimeError, match="does not exist"):
        ep.require_predictor_seal(tmp_path, tag_exists=lambda t: False,
                                  blobs_bound=W.blobs_bound)
    seen = []

    def drift(tag, rel, *, repo_root=None):
        seen.append((tag, sorted(rel)))
        return sorted(rel)[:1]
    with pytest.raises(RuntimeError, match="does not bind 1 file"):
        ep.require_predictor_seal(tmp_path, tag_exists=W.tag_exists, blobs_bound=drift)
    # the tag is asked for every file of the table AND for the seal itself
    assert seen[0][0] == r6.PREDICTOR_SEAL_TAG_6 and len(seen[0][1]) == 2
    for change in ("changed", "added", "removed"):
        extra = f.parent / "late.json"
        if change == "changed":
            f.write_text('{"x": 1}')
        elif change == "added":
            extra.write_text("{}")
        else:
            f.unlink()
        with pytest.raises(RuntimeError, match="does not describe the files on disk"):
            ep.require_predictor_seal(tmp_path, **ok)
        with pytest.raises(RuntimeError, match="does not describe the files on disk"):
            ep.run(root=tmp_path, loaders=_Never(), host=W.host(), **W.INJECT_SEAL)
        with pytest.raises(RuntimeError, match="does not describe the files on disk"):
            se.seal(tmp_path, **W.INJECT_SEAL)
        f.write_text("{}")
        extra.unlink(missing_ok=True)
    ep.require_predictor_seal(tmp_path, **ok)


def test_no_stage_runs_on_an_unsealed_predictor(tmp_path):
    for call in (lambda: ep.run(root=tmp_path, loaders=_Never(), host=W.host(),
                                **W.INJECT_SEAL),
                 lambda: se.seal(tmp_path, **W.INJECT_SEAL)):
        with pytest.raises((RuntimeError, FileNotFoundError)):
            call()
    assert [p for p in tmp_path.rglob("*") if p.is_file()] == []


def test_a_host_off_the_stack_pin_loads_nothing(tmp_path):
    _sealed_predictor(tmp_path)
    good = W.host()
    bad = dict(good, stack=dict(good["stack"], torch="0.0.1"))
    with pytest.raises(RuntimeError, match="host record"):
        ep.run(root=tmp_path, loaders=_Never(), host=bad, **W.INJECT_SEAL)
    assert not (r6.results(tmp_path) / "endpoint").exists()


def test_the_endpoint_seal_refuses_a_tree_with_failures_and_a_second_seal(tmp_path):
    _sealed_predictor(tmp_path)
    with pytest.raises(RuntimeError, match="cannot seal: "):
        se.seal(tmp_path, **W.INJECT_SEAL)
    assert not r6.rung_sets_path(tmp_path).exists()
    r6.write_json(r6.rung_sets_path(tmp_path), {"families": {}})
    with pytest.raises(RuntimeError, match="sealed ONCE"):
        se.seal(tmp_path, **W.INJECT_SEAL)
    assert r6.read_json(r6.rung_sets_path(tmp_path)) == {"families": {}}


def test_the_sweep_requires_the_sealed_endpoint_stage(tmp_path):
    _sealed_predictor(tmp_path)
    ok = dict(tag_exists=W.tag_exists, blobs_bound=W.blobs_bound)
    with pytest.raises(RuntimeError, match="the endpoint stage is not sealed"):
        sw.require_endpoint_seal(tmp_path, **ok)
    r6.write_json(r6.rung_sets_path(tmp_path), {"sealed_files": []})
    with pytest.raises(RuntimeError, match="power.*the endpoint stage is not sealed"):
        sw.require_endpoint_seal(tmp_path, **ok)       # the power record too
    with pytest.raises(RuntimeError, match="the endpoint stage is not sealed"):
        sw.run(fm.FAMILIES_6[0], root=tmp_path, loaders=_Never(), host=W.host(),
               **W.INJECT_SEAL)
    r6.write_json(r6.power_path(tmp_path), {})
    with pytest.raises(RuntimeError, match="does not exist"):
        sw.require_endpoint_seal(tmp_path, tag_exists=lambda t: False,
                                 blobs_bound=W.blobs_bound)
    with pytest.raises(RuntimeError, match="does not exist"):
        sw.run(fm.FAMILIES_6[0], root=tmp_path, loaders=_Never(), host=W.host(),
               **dict(W.INJECT_SEAL, tag_exists=lambda t: t == r6.PREREG_TAG_6))


def test_a_unit_is_complete_with_its_records_and_not_before(tmp_path):
    """The load record is written LAST: alone it says a unit is done. A
    load record with a rung's record missing is a unit cut short."""
    f, which = fm.FAMILIES_6[0], r6.ENDPOINT_WHICH_6[0]
    step = fm.grid(f)[0]
    for load, record, done in (
            (r6.endpoint_load_path(tmp_path, f, which),
             lambda r: r6.endpoint_record_path(tmp_path, f, which, r),
             lambda: ep.which_complete(tmp_path, f, which)),
            (r6.checkpoint_path(tmp_path, f, step),
             lambda r: r6.sweep_record_path(tmp_path, f, step, r),
             lambda: sw.step_complete(tmp_path, f, step))):
        assert done() is False
        r6.write_json(load, {})
        assert done() is False
        for r in b6.ALL_RUNGS_6[:-1]:
            r6.write_json(record(r), {})
        assert done() is False                          # one rung short
        r6.write_json(record(b6.ALL_RUNGS_6[-1]), {})
        assert done() is True
        load.unlink()
        assert done() is False                          # the records alone


def _second_time(message="unpinned module on the import surface: x.py"):
    """A check that passes at entry and fails at exit."""
    n = {"calls": 0}

    def check():
        n["calls"] += 1
        if n["calls"] > 1:
            raise RuntimeError(message)
    return check


def test_the_power_record_is_not_written_behind_an_exit_gate_that_fires(
        tmp_path, monkeypatch):
    from experiments.exp6 import power_6 as pw6
    _sealed_predictor(tmp_path)
    r6.write_json(r6.rung_sets_path(tmp_path), {"families": {}})
    monkeypatch.setattr(pw6, "real_inputs", lambda root: ({}, None))
    monkeypatch.setattr(pw6, "compute", lambda inputs, **kw: {
        "tests": {}, "tree": {"p_general": {}, "p_battery_bound": {}}})
    with pytest.raises(RuntimeError, match="EXIT GATE FIRED"):
        pw6.main([], root=tmp_path,
                 **dict(W.INJECT_SEAL, frozen_check=_second_time()))
    assert not r6.power_path(tmp_path).exists()
    assert r6.endpoint_halt_path(tmp_path).is_file()
    # and with the gate quiet the record is written, once
    r6.endpoint_halt_path(tmp_path).unlink()
    pw6.main([], root=tmp_path, **W.INJECT_SEAL)
    assert r6.power_path(tmp_path).is_file()
    with pytest.raises(RuntimeError, match="written ONCE"):
        pw6.main([], root=tmp_path, **W.INJECT_SEAL)


def test_a_host_record_is_named_by_its_own_sha(tmp_path):
    h = W.host("box-1")
    r6.write_json(cm.hosts_dir(tmp_path) / f"{h['sha256'][:12]}.json", h)
    bad, hosts = se.load_hosts(tmp_path)
    assert bad == [] and list(hosts) == [h["sha256"]]
    r6.write_json(cm.hosts_dir(tmp_path) / "aaaaaaaaaaaa.json", h)
    bad, _ = se.load_hosts(tmp_path)
    assert bad == ["6 host aaaaaaaaaaaa.json: host record aaaaaaaaaaaa.json: "
                   "not named by its own sha256"]


def test_the_rung_sets_record_is_measured_against_the_stage(tmp_path):
    """What the endpoint seal names is the stage's file table, and every
    file it names is the file it sealed: re-derived, not read."""
    battery = b6.load_battery_6()
    floors, heur = fl.floor_table_6(battery), fl.heuristic_table_6(battery)
    h = W.host("box-1")["sha256"]
    stage = {f: {w: {"load": {"host_sha256": h},
                     "records": {r: {"correct": 0} for r in b6.ALL_RUNGS_6}}
                 for w in r6.ENDPOINT_WHICH_6} for f in fm.FAMILIES_6}
    names = se.named_files(tmp_path, {h})
    assert len(names) == len(set(names)) == 2 + len(fm.FAMILIES_6) * len(
        r6.ENDPOINT_WHICH_6) * (1 + len(b6.ALL_RUNGS_6))
    for rel in names:
        r6.write_json(tmp_path / rel, {"file": rel})

    def record():
        return {"families": se.derive_rung_sets(stage, floors, heur),
                "rule": se.RULE_6, "prereg_tag": r6.PREREG_TAG_6,
                "sealed_files": list(names),
                "sealed_sha256": {rel: r6.sha256_file(tmp_path / rel) for rel in names}}
    check = lambda rec: se.rung_sets_failures(rec, stage, floors, heur, tmp_path)
    assert check(record()) == []
    rec = record()
    (tmp_path / names[5]).write_text("{}")                  # a sealed file changed
    assert check(rec) == [f"6 rung sets: {names[5]} is not the sealed file"]
    (tmp_path / names[5]).unlink()                          # or is gone
    assert check(rec) == [f"6 rung sets: {names[5]} is not the sealed file"]
    r6.write_json(tmp_path / names[5], {"file": names[5]})
    assert check(rec) == []
    short = dict(rec, sealed_files=names[:-1])              # a table that leaves one out
    assert "6 rung sets: sealed_files is not the endpoint stage's file table" in check(short)
    thin = dict(rec, sealed_sha256={k: v for k, v in rec["sealed_sha256"].items()
                                    if k != names[0]})
    assert check(thin) == ["6 rung sets: sealed_sha256 does not cover sealed_files"]
    assert check(dict(rec, rule="another rule")) == ["6 rung sets: rule or prereg_tag"]
    other = dict(rec, families=dict(rec["families"], olmo7b={}))
    assert check(other) == ["6 rung sets: the record does not re-derive from the "
                            "endpoint records and the floors"]


def test_gate_1b_is_rederived_over_every_family_or_fails(tmp_path):
    """A family whose endpoint stage is cut short is a failure of the
    gate, not a family the gate leaves out."""
    from experiments.exp6 import referents_6 as rf

    def stage(delta=0):
        return {f: {"stage1_final": {"records": {
                        r: {"correct": rf.mac_endpoint_count(f, r) + delta}
                        for r in b6.ANCHORS_6}},
                    "init": {"records": {r: {"correct": rf.mac_count(f, fm.INIT, r)}
                                         for r in b6.ANCHORS_6}}}
                for f in fm.FAMILIES_6}
    whole = se.gate1b_rederived(stage())
    assert whole["pass"] and whole["failures"] == []
    assert sorted(whole["families"]) == sorted(fm.FAMILIES_6)
    assert whole["tolerance_per_rung"] == rf.TOL_PER_RUNG_6 == 15
    assert se.gate1b_rederived(stage(15))["pass"]
    off = se.gate1b_rederived(stage(16))                     # one item over the tolerance
    assert not off["pass"] and len(off["failures"]) == len(fm.FAMILIES_6) * len(b6.ANCHORS_6)
    short = stage()
    del short["olmo7b"]["init"]
    got = se.gate1b_rederived(short)
    assert not got["pass"] and "olmo7b" not in got["families"]
    assert got["failures"] == ["6 gate 1(b) olmo7b: the endpoint stage is incomplete"]
    del short["comma_7b"]
    assert len(se.gate1b_rederived(short)["failures"]) == 2
    # the runner's record against the re-derivation
    h = W.host("box-1")
    hosts = {h["sha256"]: h}
    assert se.gate1b_failures(tmp_path, stage(), hosts) == ["6 gate 1(b): record missing"]
    r6.write_json(r6.gate1b_path(tmp_path), dict(whole, prereg_tag=r6.PREREG_TAG_6,
                                                 host_sha256=h["sha256"]))
    assert se.gate1b_failures(tmp_path, stage(), hosts) == []
    assert se.gate1b_failures(tmp_path, stage(), {}) == [
        f"6 gate 1(b): host {h['sha256'][:12]} has no host record"]
    with pytest.raises(TypeError):                # the host check has no default that skips it
        se.gate1b_failures(tmp_path, stage())
    assert se.gate1b_failures(tmp_path, stage(1), hosts) == [
        "6 gate 1(b): the record's families does not re-derive from the endpoint records"]


def test_an_endpoint_read_names_a_host_that_has_a_record(tmp_path):
    f, which = fm.FAMILIES_6[0], r6.ENDPOINT_WHICH_6[0]
    battery = b6.load_battery_6()
    h = W.host("box-1")
    r6.write_json(r6.endpoint_load_path(tmp_path, f, which), {"host_sha256": h["sha256"]})
    kw = dict(battery=battery, man=fm.manifest(f), seal_sha256="0" * 64)
    line = f"6 endpoint {f}/{which}: host {h['sha256'][:12]} has no host record"
    bad, _ = se.load_which(tmp_path, f, which, hosts={}, **kw)
    assert line in bad
    bad, _ = se.load_which(tmp_path, f, which, hosts={h["sha256"]: h}, **kw)
    assert line not in bad and bad                 # the record fails on everything else
    assert se.load_which(tmp_path, f, r6.ENDPOINT_WHICH_6[1], hosts={}, **kw) == (
        [f"6 endpoint {f}/{r6.ENDPOINT_WHICH_6[1]}: load record missing"], None)


def _read(correct=300, n=b6.N_ITEMS):
    return {"bits": [1] * correct + [0] * (n - correct),
            "continuations": [" yes"] * correct + [" no"] * (n - correct),
            "correct": correct}


def _gate1(thin=None, cand=None, sealed=None, *, digests=("d", "d"), anchors=(),
           sealed_digest="d"):
    whole = {r: _read() for r in b6.ALL_RUNGS_6}
    return sw.gate1_record(
        "olmo7b", thin=dict(whole, **(thin or {})), cand=dict(whole, **(cand or {})),
        sealed=dict(whole, **(sealed or {})), thin_load={"digest": digests[0]},
        cand_load={"digest": digests[1], "commit": "c"},
        sealed_load={"digest": sealed_digest}, anchor_bad=list(anchors))


def test_gate_1_is_three_reads_of_the_endpoint_compared():
    """This host's two loader paths against each other, bit for bit and
    continuation for continuation, their digests equal; this host
    against the sealed record within the tolerance; the anchors against
    the Mac's counts. Each alone fails the gate."""
    rung = b6.RUNGS_6[3]
    good = _gate1()
    assert good["pass"] and good["failures"] == []
    assert good["rungs_compared"] == len(b6.ALL_RUNGS_6) == 20
    assert good["rungs"][rung] == {
        "compared": 500, "bit_diffs": 0, "continuation_diffs": 0, "sealed_count": 300,
        "host_count": 300, "abs_diff_vs_sealed": 0}
    # (a) one continuation differs and scores the same
    other = _read()
    other["continuations"][0] = " yes."
    got = _gate1(cand={rung: other})
    assert got["failures"] == [f"6 gate 1(a) olmo7b/{rung}: 0 bit and 1 continuation "
                               f"diffs between the two loaders"]
    # (a) one bit differs
    flip = _read()
    flip["bits"][0] = 0
    got = _gate1(cand={rung: flip})
    assert got["rungs"][rung]["bit_diffs"] == 1 and not got["pass"]
    # (a) a read that is short
    got = _gate1(thin={rung: _read(n=499)}, cand={rung: _read(n=499)},
                 sealed={rung: _read()})
    assert got["failures"] == [f"6 gate 1(a) olmo7b/{rung}: 499 items compared, not 500"]
    # (a) the digests
    assert _gate1(digests=("d", "e"), sealed_digest="e")["failures"] == [
        "6 gate 1(a) olmo7b: the two loaders' tensor digests differ"]
    for d in ("", None):
        assert _gate1(digests=(d, d), sealed_digest=d)["failures"] == [
            "6 gate 1(a) olmo7b: the two loaders' tensor digests differ",
            "6 gate 1(b) olmo7b: this host's tensor digest is not the sealed endpoint "
            "read's"]
    # (b) the read that set R_f and this host's file-verified read are one model
    got = _gate1(sealed_digest="another")
    assert got["failures"] == ["6 gate 1(b) olmo7b: this host's tensor digest is not "
                               "the sealed endpoint read's"]
    assert (got["digest_sealed"], got["digest_candidate"]) == ("another", "d")
    assert not got["pass"] and good["digest_sealed"] == "d"
    # (b) this host against the sealed record: fifteen items pass, sixteen do not
    assert _gate1(sealed={rung: _read(285)})["pass"]
    got = _gate1(sealed={rung: _read(284)})
    assert got["failures"] == [f"6 gate 1(b) olmo7b/{rung}: |Δ| 16 > 15 against the "
                               f"sealed endpoint record"]
    assert got["rungs"][rung]["abs_diff_vs_sealed"] == 16
    # (c) what the anchors' comparison handed in
    got = _gate1(anchors=["6 gate 1(c) olmo7b/step1: sub_base8"])
    assert got["failures"] == ["6 gate 1(c) olmo7b/step1: sub_base8"] and not got["pass"]


def test_the_load_record_is_written_last(tmp_path, monkeypatch):
    """The load record is the completeness signal: a kill between two
    records must leave a unit that reads as unfinished."""
    order = []
    monkeypatch.setattr(sw.r6, "unit_record", lambda **kw: {"rung": kw["rung"]})
    monkeypatch.setattr(sw.r6, "write_json", lambda path, obj: order.append(str(path)))
    read = {"load": {"digest": "d"},
            "evs": {r: {"seconds": 0.0} for r in b6.ALL_RUNGS_6}}
    ctx = {"host": {"sha256": "h"}, "seal_sha": "s", "stack": {}, "git_sha": "",
           "endpoint_sha": "e"}
    sw.write_units(read, family="olmo7b", battery={r: None for r in b6.ALL_RUNGS_6},
                   ctx=ctx, path_of=lambda r: tmp_path / f"{r}.json",
                   load_path=tmp_path / "_checkpoint.json", step=1000)
    assert len(order) == len(b6.ALL_RUNGS_6) + 1
    assert order[-1] == str(tmp_path / "_checkpoint.json")


def _seal_endpoint(root):
    """The smallest tree the sweep takes for a sealed endpoint stage, on
    a predictor that is sealed."""
    r6.write_json(r6.rung_sets_path(root), {"sealed_files": []})
    r6.write_json(r6.power_path(root), {})


def test_no_test_can_reach_a_model():
    """The guard of `conftest.py`, measured from inside a test: the Hub
    is off and the model cache is an empty directory, whatever the
    machine's own cache holds."""
    import os
    import huggingface_hub
    from huggingface_hub import constants as c
    assert os.environ["HF_HUB_OFFLINE"] == "1" and c.HF_HUB_OFFLINE is True
    assert "exp6-no-models-" in str(c.HF_HUB_CACHE)
    assert not os.path.isdir(c.HF_HUB_CACHE) or not os.listdir(c.HF_HUB_CACHE)
    with pytest.raises(Exception) as e:                   # reached only behind the guard
        huggingface_hub.hf_hub_download(fm.repo(fm.FAMILIES_6[0]), "config.json")
    assert type(e.value).__name__ in ("LocalEntryNotFoundError", "OfflineModeIsEnabled")


def test_a_loader_table_that_is_handed_in_is_the_one_used(tmp_path, monkeypatch):
    """An empty table is a table. On 2026-09-28 a mutation run handed a
    runner a table that must not be reached; the table was empty, the
    runner read `loaders or real_loaders()`, and SmolLM3-3B's endpoint
    was fetched and loaded. No stage falls through what it was handed."""
    W.no_real_loaders(monkeypatch)
    assert not _Never()
    _sealed_predictor(tmp_path)
    with pytest.raises(AssertionError, match="reached its loader 'thin'"):
        ep.run(root=tmp_path, loaders=_Never(), host=W.host(), **W.INJECT_SEAL)
    _seal_endpoint(tmp_path)
    with pytest.raises(AssertionError, match="reached its loader 'thin'"):
        sw.run(fm.FAMILIES_6[0], root=tmp_path, loaders=_Never(), host=W.host(),
               **W.INJECT_SEAL)
    assert not list(r6.results(tmp_path).rglob("gate1_*"))


def test_a_host_does_not_resume_behind_its_own_failed_gate(tmp_path, monkeypatch):
    """The gate record is written before the halt marker. A kill between
    the two leaves a failed gate and no marker: the host that comes back
    reads its own record and loads nothing."""
    W.no_real_loaders(monkeypatch)
    _sealed_predictor(tmp_path)
    _seal_endpoint(tmp_path)
    f, h = fm.FAMILIES_6[0], W.host()
    gate = r6.gate1_path(tmp_path, f, h["sha256"])
    r6.write_json(gate, {"pass": False, "failures": ["6 gate 1(a): x"],
                         "host_sha256": h["sha256"]})
    before = gate.read_bytes()
    with pytest.raises(RuntimeError, match="records a failed gate"):
        sw.run(f, root=tmp_path, loaders=_Never(), host=h, **W.INJECT_SEAL)
    assert gate.read_bytes() == before
    assert not r6.step_dir(tmp_path, f, fm.endpoint_step(f)).exists()


def _never_scored(loaders):
    def touched(*a, **k):
        raise AssertionError("a model that is not the Mac's was handed a prompt")
    return dict(loaders, runner=touched, nonfinite=touched)


def test_a_checkpoint_that_is_not_the_macs_is_not_scored(tmp_path):
    """Gate 1(d): the digest the loader MEASURED against the Mac's
    committed one, before anything is scored. The endpoint stage's thin
    read sets R_f and is checked by no file sha; this is what ties it to
    a referent."""
    design = W.Design(W.spec(), b6.load_battery_6())
    wrong = _never_scored(W.fake_loaders(design, digest=lambda f, k, how: "0" * 64))
    _sealed_predictor(tmp_path)
    f = fm.FAMILIES_6[0]
    with pytest.raises(RuntimeError, match=r"GATE 1\(d\) FIRED") as e:
        ep.run(root=tmp_path, loaders=wrong, host=W.host(), **W.INJECT_SEAL)
    assert f"6 gate 1(d) {f}/stage1_final: tensor digest 000000000000 is not the " \
        f"Mac's committed {rf.mac_digest(f, fm.endpoint_step(f))[:12]}" in str(e.value)
    marker = r6.endpoint_halt_path(tmp_path)
    assert marker.is_file() and "6 gate 1(d)" in marker.read_text()
    # the marker carries the whole of what the loader measured, not twelve characters
    import json
    seen = json.loads(marker.read_text().splitlines()[-1])
    assert seen["digest"] == "0" * 64 and seen["family"] == f and seen["key"] == "stage1_final"
    assert seen["commit"] == fm.entry(f, fm.manifest(f), fm.endpoint_step(f))["commit"]
    assert not list((r6.results(tmp_path) / "endpoint").rglob("*.json"))
    with pytest.raises(RuntimeError, match="halt marker"):     # and nothing resumes
        ep.run(root=tmp_path, loaders=wrong, host=W.host(), **W.INJECT_SEAL)
    # the sweep: at its gate, and at a grid step (the load record kept as evidence)
    marker.unlink()
    _seal_endpoint(tmp_path)
    with pytest.raises(RuntimeError, match=r"GATE 1\(d\) FIRED"):
        sw.run(f, root=tmp_path, loaders=wrong, host=W.host(), **W.INJECT_SEAL)
    text = r6.sweep_halt_path(tmp_path, f).read_text()
    assert "6 gate 1(d)" in text and json.loads(text.splitlines()[-1])["digest"] == "0" * 64
    assert not list(r6.sweep_dir(tmp_path, f).rglob("*.json"))
    step = fm.grid(f)[0]
    kept = r6.halted_step_dir(tmp_path, f, step) / "_checkpoint.json"
    ctx = {"host": W.host(), "device": "cuda", "seal_sha": "s", "endpoint_sha": "e",
           "stack": {}, "git_sha": ""}
    fails = sw.run_step(f, step, root=tmp_path, man=fm.manifest(f),
                        battery=b6.load_battery_6(), ctx=ctx, loaders=wrong,
                        cache_root=tmp_path / "ckpt")
    assert len(fails) == 1 and fails[0].startswith(f"6 gate 1(d) {f}/step{step}: ")
    assert r6.read_json(kept)["digest"] == "0" * 64
    assert not r6.step_dir(tmp_path, f, step).exists()


def test_a_twin_is_outside_the_digest_gate_and_a_real_step_0_is_inside():
    for f in fm.FAMILIES_6:
        end = fm.endpoint_step(f)
        right = {"digest": rf.mac_digest(f, end)}
        for key in ("stage1_final", r6.SWEEP_THIN, r6.SWEEP_CAND, end):
            assert rf.digest_failures(right, f, key, label="x") == []
            assert len(rf.digest_failures({"digest": "0" * 64}, f, key, label="x")) == 1
            assert len(rf.digest_failures({}, f, key, label="x")) == 1
        assert rf.digest_failures(right, f, fm.grid(f)[0], label="x") != []
        twin = fm.INIT_KIND[f] == "twin"
        assert (rf.digest_failures({"digest": "anything"}, f, "init", label="x") == []) \
            is twin
    assert rf.digest_failures({"digest": rf.mac_digest("olmo13b", fm.INIT)}, "olmo13b",
                              "init", label="x") == []


def test_the_endpoint_stage_reads_nothing_once_it_is_sealed(tmp_path):
    """The gate record is a sealed file. A run after the seal would
    rewrite it under another host and another HEAD."""
    _sealed_predictor(tmp_path)
    r6.write_json(r6.rung_sets_path(tmp_path), {"sealed_files": []})
    for dry in (False, True):
        with pytest.raises(RuntimeError, match="the endpoint stage is sealed"):
            ep.run(root=tmp_path, loaders=_Never(), host=W.host(), dry_run=dry,
                   **W.INJECT_SEAL)
    assert not r6.gate1b_path(tmp_path).exists()


def test_a_record_is_written_whole_or_not_at_all(tmp_path, monkeypatch):
    p = tmp_path / "a" / "rec.json"
    r6.write_json(p, {"v": 1})
    assert r6.read_json(p) == {"v": 1} and [x.name for x in p.parent.iterdir()] == [
        "rec.json"]

    def killed(src, dst):
        raise KeyboardInterrupt("killed between the write and the rename")
    monkeypatch.setattr(r6.os, "replace", killed)
    with pytest.raises(KeyboardInterrupt):
        r6.write_json(p, {"v": 2})
    assert r6.read_json(p) == {"v": 1}                  # the file that was there
    # what the kill left is named by its writer: two writers do not share it
    import os
    assert sorted(x.name for x in p.parent.iterdir()) == [
        "rec.json", f"rec.json.{os.getpid()}.tmp"]


def test_a_torn_record_is_not_resumed_over(tmp_path):
    f, which = fm.FAMILIES_6[0], r6.ENDPOINT_WHICH_6[0]
    step = fm.grid(f)[0]
    for load, done in ((r6.endpoint_load_path(tmp_path, f, which),
                        lambda: ep.which_complete(tmp_path, f, which)),
                       (r6.checkpoint_path(tmp_path, f, step),
                        lambda: sw.step_complete(tmp_path, f, step))):
        assert r6.whole(load) is False and done() is False
        load.parent.mkdir(parents=True, exist_ok=True)
        for torn in (b"", b'{"family": "ol', b"[1, 2]", b"\xff\xfe"):
            load.write_bytes(torn)
            with pytest.raises(RuntimeError, match="torn record"):
                done()
        load.unlink()
        load.mkdir()                                   # a directory where a file belongs
        with pytest.raises(RuntimeError, match="torn record"):
            done()
