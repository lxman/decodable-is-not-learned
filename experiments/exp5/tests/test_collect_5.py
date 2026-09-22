# experiments/exp5/tests/test_collect_5.py
import hashlib
import json

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2d import analyze_2d as a2d
from experiments.exp5 import battery_5 as b5
from experiments.exp5 import collect_5 as c5
from experiments.exp5.tests import fakes_5 as fk

SIZES = ("1b", "2.8b")
AVAIL = (1000, 2000, 4000, 8000, 143000)


@pytest.fixture
def world(tmp_path, monkeypatch):
    battery = bt.load_battery()
    man = fk.synthetic_manifest(SIZES, AVAIL)
    loaders, state = fk.make_loaders(battery, loss_fn=lambda s, k: 3.0 - k / 1e5,
                                     count_fn=lambda s, k, r: (100 if r == "antonym" else 0))
    host = c5.host_record_5("cuda", fk.fake_host()["transports"], stack=fk.fake_host()["stack"],
                            gpu="fake", python="3.11.16")
    return dict(root=tmp_path, battery=battery, manifest=man, loaders=loaders, state=state,
                host=host, sl=fk.small_slice(), verify_fn=a2d.load_verify())


def test_host_record_has_sha_and_passes_contract():
    h = c5.host_record_5("cuda", {"classic_mbps": 1.0, "xet_mbps": 2.0, "used": "xet"},
                         stack=fk.fake_host()["stack"], gpu="g", python="3.11.16")
    assert len(h["sha256"]) == 64 and b5.host_record_failures_5(h) == []
    h2 = c5.host_record_5("cuda", {"classic_mbps": 1.0, "xet_mbps": 2.0, "used": "xet"},
                          stack=fk.fake_host()["stack"], gpu="g", python="3.11.16")
    assert h2["sha256"] == h["sha256"]           # canonical: no timestamps inside the hash


def test_run_unit_writes_36_files_then_unit_json_last_and_frees(world):
    w = world
    rec = c5.run_unit_5("1b", 2000, root=w["root"], manifest=w["manifest"], cache_root=w["root"],
                        device="cuda", battery=w["battery"], verify_fn=w["verify_fn"], sl=w["sl"],
                        host=w["host"], loaders=w["loaders"], git_sha="g", why="spine")
    d = b5.unit_dir_5(w["root"], "1b", 2000)
    assert rec["action"] == "loaded"
    assert set(p.name for p in d.iterdir()) == set(b5.unit_files_5()) | {"_unit.json"}
    assert b5.unit_complete_5(w["root"], "1b", 2000)
    unit = json.loads((d / "_unit.json").read_text())
    assert unit["why"] == "spine" and unit["git_sha"] == "g" and unit["size"] == "1b"
    ck = json.loads((d / "_checkpoint.json").read_text())
    assert ck["digest"] == hashlib.sha256(b"d-1b-2000").hexdigest()
    assert ck["n_params"] == 1000 and ck["dtype"] == "float16"
    entry = b5.entry_5(w["manifest"], "1b", 2000)
    assert b5.checkpoint_record_failures_5(ck, size="1b", step=2000, entry=entry) == []
    loss = json.loads((d / "_loss.json").read_text())
    assert b5.loss_record_failures_5(loss, size="1b", step=2000, host=w["host"],
                                     slice_sha="slice-fake", n_scored=197) == []
    r = json.loads((d / "antonym.json").read_text())
    assert r["correct"] == 100 and r["prereg_tag"] == "exp5-preregistered"
    assert b5.rung_record_failures_5(r, size="1b", step=2000, rung="antonym",
                                     cap=w["battery"]["antonym"], entry=entry,
                                     verify_fn=w["verify_fn"], host=w["host"]) == []
    assert w["state"]["freed"] == [("1b", 2000)] and w["state"]["released"] == 1


def test_run_unit_skips_a_complete_unit(world):
    w = world
    kw = dict(root=w["root"], manifest=w["manifest"], cache_root=w["root"], device="cuda",
              battery=w["battery"], verify_fn=w["verify_fn"], sl=w["sl"], host=w["host"],
              loaders=w["loaders"], git_sha="g", why="spine")
    c5.run_unit_5("1b", 2000, **kw)
    rec = c5.run_unit_5("1b", 2000, **kw)
    assert rec["action"] == "reused" and w["state"]["loaded"] == [("1b", 2000)]


def test_run_unit_failure_leaves_no_unit_json_and_frees(world, monkeypatch):
    w = world
    loaders, state = fk.make_loaders(w["battery"], loss_fn=lambda s, k: 3.0,
                                     count_fn=lambda s, k, r: 0, raise_on="mod13")
    with pytest.raises(RuntimeError, match="fake failure"):
        c5.run_unit_5("1b", 2000, root=w["root"], manifest=w["manifest"], cache_root=w["root"],
                      device="cuda", battery=w["battery"], verify_fn=w["verify_fn"], sl=w["sl"],
                      host=w["host"], loaders=loaders, git_sha="g", why="spine")
    d = b5.unit_dir_5(w["root"], "1b", 2000)
    assert not (d / "_unit.json").exists() and not b5.unit_complete_5(w["root"], "1b", 2000)
    assert state["freed"] == [("1b", 2000)]


def test_rebuild_loss_table_reads_every_complete_unit(world):
    w = world
    kw = dict(root=w["root"], manifest=w["manifest"], cache_root=w["root"], device="cuda",
              battery=w["battery"], verify_fn=w["verify_fn"], sl=w["sl"], host=w["host"],
              loaders=w["loaders"], git_sha="g", why="spine")
    c5.run_unit_5("1b", 2000, **kw)
    c5.run_unit_5("2.8b", 4000, **kw)
    t = c5.rebuild_loss_table_5(w["root"])
    assert t["1b"]["2000"]["loss"] == 3.0 - 2000 / 1e5 and "4000" in t["2.8b"]
    assert b5.loss_table_path_5(w["root"]).is_file()


def test_prefetcher_runs_the_download_and_waits(world):
    w = world
    pf = c5.Prefetcher(w["loaders"], cache_root=w["root"])
    pf.start("1b", b5.entry_5(w["manifest"], "1b", 4000))
    pf.wait()
    assert w["state"]["prefetched"] == [("1b", "step4000")]
    pf.wait()                                        # idempotent
