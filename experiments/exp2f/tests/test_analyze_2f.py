"""analyze_2f: pins, the label tallies on committed-layout cells, the
continuity gate's re-derivation, the m3 gate, the tree, and run()'s
refusal routing — on a module world plus the REAL committed bytes
where the answer is known."""
import hashlib
import json

import numpy as np
import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import stats_2d as st
from experiments.exp2f import analyze_2f as a
from experiments.exp2f import labels_2f as lb
from experiments.exp2f import make_referents_2f as mk
from experiments.exp2f.tests import full_shape as fs


# ------------------------------------------------------------------ pins

def test_frozen_import_pins_hold():
    a.check_frozen_imports_2f()
    names = {p.name for p in a.FROZEN_IMPORT_SHA256_2F}
    assert names >= {"probe_starved.py", "splits.py", "models.py", "stats.py",
                     "harness.py", "screen.py", "gen_items.py", "analyze_2d.py",
                     "stats_2d.py", "battery_2d.py", "generators.py"}


def test_exact_match_pin_is_2ds_record():
    assert a.EXACT_MATCH_PIN[("arith_next", "410m", "main")] == 831
    assert a.EXACT_MATCH_PIN[("arith_next", "1b", "main")] == 531
    assert a.EXACT_MATCH_PIN[("sub3_mid", "410m", "main")] == 35
    assert a.EXACT_MATCH_PIN[("sub3_mid", "1b", "main")] == 34
    assert a.EXACT_MATCH_PIN[("arith_next", "410m", "pilot")] == 109
    assert a.EXACT_MATCH_PIN[("arith_next", "1b", "pilot")] == 67
    assert a.EXACT_MATCH_PIN[("sub3_mid", "410m", "pilot")] == 6
    assert a.EXACT_MATCH_PIN[("sub3_mid", "1b", "pilot")] == 3
    assert a.EXACT_MATCH_PIN[("arith_next", "410m", "argmax")] == 13
    assert a.EXACT_MATCH_PIN[("arith_next", "1b", "argmax")] == 19
    assert a.EXACT_MATCH_PIN[("sub3_mid", "410m", "argmax")] == 0
    assert a.EXACT_MATCH_PIN[("sub3_mid", "1b", "argmax")] == 0


def test_npz_pins_match_the_committed_digest_files():
    """The 8 activation shas by literal == the lines of 2b's / 2c's
    activations_sha256.txt (three sources, one value, at the freeze
    the files themselves)."""
    for (rung, size, mode), want in a.PROBE_NPZ_SHA_PIN.items():
        exp = a2d.bt.EXP2B if rung in a2d.bt.REUSED else a2d.bt.EXP2C
        txt = (exp / "results" / "activations_sha256.txt").read_text()
        line = f"{want}  activations/{size}_{mode}/{rung}.npz"
        assert line in txt, (rung, size, mode)


def test_m3_pins_are_the_committed_records():
    for (rung, size), pin in a.M3_PIN.items():
        rec = json.loads(mk.m3_record_path(size, rung).read_text())
        assert a.m3_pin_from_record(rec) == pin


def test_split_params_are_2bs_and_2cs():
    from experiments.exp2b.splits import SplitParams
    assert a.SPLIT_PARAMS["sub3_mid"] == SplitParams(n_holdout=20)
    assert a.SPLIT_PARAMS["arith_next"] == SplitParams(holdout_frac=0.35)


# ----------------------------------------------------------- module world

@pytest.fixture(scope="module")
def world(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("w")
    pins = fs.build_world(tmp, cells=fs.full_cells(),
                          probe_strength={("arith_next", s): 4.0 for s in lb.SIZES},
                          run=False)
    return tmp, pins


def test_label_tallies_on_world_rows(world):
    root, pins = world
    battery = fs.battery()
    rows = a.read_cell_rows(root, "main", "1b", "arith_next")
    answers = [str(it["answer"]) for it in battery["arith_next"]["eval_items"]]
    t = a.label_tallies(
        [d for r in rows for d in r["draws"]["0"]], 
        [answers[r["item"]] for r in rows for _ in r["draws"]["0"]],
        "last_digit")
    assert t["n"] == 32_000 and t["exact"] == 300 and t["match"] == 6300 \
        and t["miss"] == 32_000 - 6300
    t7 = a.label_tallies(
        [d for r in rows for d in r["draws"]["0"]],
        [answers[r["item"]] for r in rows for _ in r["draws"]["0"]], "mod7")
    assert t7["exact"] == 300 and t7["match"] == 300    # +10 breaks mod 7


def test_instrument_rung_applies_2ds_bar(world):
    r = a.instrument_rung(match=3420, n=32_000, floor=.1, exact=300)
    assert r["D"] is True and r["rate"] == pytest.approx(3420 / 32000)
    assert r["p"] == st.binomial_bar(3420, 32_000, .1)["p"]
    r2 = a.instrument_rung(match=3300, n=32_000, floor=.1, exact=0)
    assert r2["D"] is False          # .103 over .10: z ≈ 1.8, not at α .01
    assert r2["p"] == st.binomial_bar(3300, 32_000, .1)["p"]
    assert r2["exact"] == 0 and r["exact_rate"] == 300 / 32_000


def test_continuity_gate_rederives_pass_from_diffs():
    rec = a.continuity_record(size="1b", mode="trained", per_rung={
        r: {"items": list(range(8)), "n_compared": 8, "max_abs_diff": 0.0,
            "max_rel_diff": 0.0} for r in lb.RUNGS}, stack=fs.FAKE_STACK)
    assert a.continuity_pass(rec) == []
    bad = json.loads(json.dumps(rec))
    bad["rungs"]["arith_next"]["max_rel_diff"] = a.CONTINUITY_RTOL * 2
    bad["pass"] = True                          # the runner's claim is ignored
    assert any("continuity" in f for f in a.continuity_pass(bad))
    bad2 = json.loads(json.dumps(rec)); bad2["rungs"]["sub3_mid"]["n_compared"] = 4
    assert a.continuity_pass(bad2)


def test_eval_npz_loader_refuses_wrong_provenance(world):
    root, pins = world
    battery = fs.battery()
    act, y, meta = a.load_eval_acts(root, "1b", "trained", "arith_next",
                                    battery["arith_next"], n_layers=7)
    assert set(act) == set(a.pb.site_family(7)) and len(y) == 500
    with pytest.raises(ValueError, match="n_layers"):
        a.load_eval_acts(root, "1b", "trained", "arith_next",
                         battery["arith_next"], n_layers=17)
    p = a.eval_npz_path(root, "1b", "trained", "arith_next")
    z = np.load(p, allow_pickle=False)
    meta2 = json.loads(str(z["meta"])); meta2["model_sha"] = "deadbeef"
    alt = root / "alt.npz"
    np.savez_compressed(alt, X=z["X"], y=z["y"], meta=json.dumps(meta2))
    with pytest.raises(ValueError, match="model_sha"):
        a.load_eval_npz(alt, size="1b", mode="trained", rung="arith_next",
                        cap=battery["arith_next"], n_layers=7)


def test_m3_gate_on_world(world):
    root, pins = world
    battery = fs.battery()
    f = a.check_m3_gate(battery, pins["m3_pin"], probe_root=root)
    assert f == []
    bad = {k: dict(v) for k, v in pins["m3_pin"].items()}
    bad[("arith_next", "1b")]["accuracy"] += 0.01
    f2 = a.check_m3_gate(battery, bad, probe_root=root)
    assert len(f2) == 1 and "m3" in f2[0]


def test_tree():
    cells = {"a": {"D": [True, True, False], "void": False},
             "b": {"D": [False, False, False], "void": False}}
    assert a.verdict_tree_2f(referent_failures=[], cells=cells,
                             n_void_arith=0)["verdict"] == "LADDER"
    cells["a"]["D"] = [False, True, False]
    assert a.verdict_tree_2f([], cells, 0)["verdict"] == "INVERTED"
    cells["a"]["D"] = [False, False, False]
    assert a.verdict_tree_2f([], cells, 0)["verdict"] == "SILENT"
    assert a.verdict_tree_2f(["x"], cells, 0)["verdict"] == "INSUFFICIENT_DATA"
    assert a.verdict_tree_2f([], cells, 2)["verdict"] == "INSUFFICIENT_DATA"
    # a void cell (D_probe None) is excluded from the pattern count
    cells["a"] = {"D": [None, True, True], "void": True}
    assert a.verdict_tree_2f([], cells, 1)["verdict"] == "SILENT"
    assert a.monotone([True, False, False]) and a.monotone([True, True, True])
    assert not a.monotone([False, True, False]) and not a.monotone([True, False, True])


def test_run_routes_refusals(world):
    root, pins = world
    kw = dict(d2_root=root, probe_root=root, manifest_path=pins["manifest_path"],
              manifest_sha_pin=pins["manifest_sha_pin"], exact_pin=pins["exact_pin"],
              m3_pin=pins["m3_pin"], npz_pin=pins["npz_pin"])
    bad = dict(pins["exact_pin"]); bad[("sub3_mid", "410m", "pilot")] += 1
    v = a.run(root, **{**kw, "exact_pin": bad})
    assert v["verdict"] == "INSUFFICIENT_DATA" and \
        any("exact-match" in f and "sub3_mid/410m/pilot" in f
            for f in v["referents"]["failures"])
    badn = dict(pins["npz_pin"]); badn[("arith_next", "1b", "untrained")] = "0" * 64
    v2 = a.run(root, **{**kw, "npz_pin": badn})
    assert v2["verdict"] == "INSUFFICIENT_DATA" and \
        any("activation file" in f for f in v2["referents"]["failures"])
    with pytest.raises(ValueError, match="sha256"):
        a.run(root, **{**kw, "manifest_sha_pin": "1" * 64})


def test_caveat_is_the_doc_paragraph_verbatim():
    import re
    doc = (a.REPO / "experiment-2f-design.md").read_text()
    m = re.search(r"Known and committed:.*?neither known nor derivable\.", doc, re.S)
    para = re.sub(r"\s*\n\s*", " ", m.group(0).replace("**", "")).strip()
    assert a.KNOWN_INPUTS_CAVEAT_2F == para


# --------------------------------------------------- collector (no model)

def test_collector_compare_rows_and_record():
    from experiments.exp2f import collect_eval_2f as ce
    rng = np.random.default_rng(0)
    com = rng.normal(size=(8, 17, 2, 64)).astype(np.float16)
    same = ce.compare_rows(com, com)
    assert same["identical"] and same["max_abs_diff"] == 0.0 and same["n_compared"] == 8
    new = com.astype(np.float32); new[0, 3, 1, 5] += 0.5
    d = ce.compare_rows(new, com)
    assert not d["identical"] and d["max_abs_diff"] == pytest.approx(0.5, abs=1e-3)
    with pytest.raises(ValueError, match="shapes"):
        ce.compare_rows(com[:4], com)
    rec = a.continuity_record(size="410m", mode="untrained", per_rung={
        r: {"items": list(range(8)), **d} for r in lb.RUNGS}, stack={"t": "x"})
    assert rec["pass"] is False and rec["untrained_seed"] == 0
    assert a.continuity_pass(rec)


def test_collector_uses_2cs_renderer_and_positions():
    from experiments.exp2f import collect_eval_2f as ce
    from experiments.exp2c.run import screen
    from experiments.exp2b.battery import base as b2
    q, shots = "What is 1 + 1?", [("What is 2 + 2?", "4")]
    assert screen._render_prompt(q, shots) == b2.render_prompt(q, shots)
    assert ce.screen is screen
