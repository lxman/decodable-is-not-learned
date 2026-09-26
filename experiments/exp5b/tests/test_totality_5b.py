# experiments/exp5b/tests/test_totality_5b.py
"""Totality (Task 6 brief, step 3): every tree shape the runners can
leave gives `analyze_5b.run()` INSUFFICIENT_DATA, never a raise — on the
SURVIVES world `full_shape_5b.write_world_5b` builds, one corruption at
a time, each applied then RESTORED before the next (Experiment 5's own
`test_totality_5.py` pattern, one world built once for the whole test
function). Shapes 7 and 8 are the two NON-refusal cases in the brief's
list (a side directory removed / a side with only the final present) —
asserted as EXCLUDED, never INSUFFICIENT_DATA.

Unlike `test_full_shape_5b.py`'s own `run_5b` (which forces `referents_
sha=False, imports_pinned=False, frozen_check=lambda: None` to work
around Task 6 not having pinned yet), this file's `_run` leaves those
three at their PRODUCTION defaults — `FROZEN_SHA256_5B`/`IMPORTED_
SHA256_5B`/`REFERENTS_5B_SHA256` are now pinned against the REAL repo
tree (independent of the synthetic `tmp_path` world; the synthetic
world's own `apply_shrink_5b` monkeypatches `FROZEN_SHA256_5B`/
`IMPORTED_SHA256_5B`/`check_imports_5b` to a no-op regardless, so the
sites are reached either way, while `referents_sha`'s production
default checks the REAL committed `referents_5b.json` against the REAL
`REFERENTS_5B_SHA256` pin — strictly more coverage, exercised for real).

Plus the 24-site harness: every `collect_total_5b` label textually
inside `analyze_5b.run()`'s own body (AST-derived) is reached at least
once across the shapes — collect by monkeypatching `an.collect_total_5b`
to record labels; assert the set equals the AST-listed labels (the
`f"5b units {size}"` site counts once per its template)."""
from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path

import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5
from experiments.exp5b import analyze_5b as an
from experiments.exp5b import battery_5b as b5b
from experiments.exp5b.tests import full_shape_5b as fs5b

pytestmark = pytest.mark.slow

AN5B_PATH = Path(an.__file__)
FINAL = b5.FINAL_STEP_5
M0, M1, M2 = fs5b.WINDOW_W          # 31000, 30000, 29000 (the shrunk world's window)


def _run(w, **over):
    kw = dict(root=w["root5b"], exp5_root=w["root5"], write=False, n_sample=200, n_boot=100,
              manifest=w["manifest"], sl=w["sl"], verdict_sha=False, exp5_kwargs=w["inj5"],
              projection_commit="p2", prereg_commit="t2", is_ancestor=lambda a, b: True,
              power_gate="full", **fs5b._inj())
    kw.update(over)
    return an.run(**kw)


def _assert_insufficient(w, **over):
    """The brief's own wording: wrap in `try`, fail the test on any
    exception — `analyze_5b.run()`'s contract is that it never raises
    for a DATA problem."""
    try:
        v = _run(w, **over)
    except Exception as e:  # noqa: BLE001 — the thing under test
        pytest.fail(f"analyze_5b.run() raised instead of returning INSUFFICIENT_DATA: "
                   f"{type(e).__name__}: {e}")
    assert v["verdict"] == "INSUFFICIENT_DATA", v
    assert v["primary"] is None and v["secondaries"] == {}
    return v


# ------------------------------------------------------------- the 18 shapes

def test_every_runner_leavable_tree_shape_gives_insufficient_data(tmp_path, monkeypatch):
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    r5, r5b = w["root5"], w["root5b"]
    v0 = _run(w)
    assert v0["verdict"] == "SURVIVES", v0["failures"][:3]          # the clean control

    # 1. a HALTED marker on one side.
    hp = b5b.halt_marker_path_5b(r5b, "1b")
    hp.write_text("gate 1: forced halt (totality test)\n")
    v = _assert_insufficient(w)
    assert any("halt" in f.lower() for f in v["failures"])
    hp.unlink()

    # 2. a torn member unit: no _unit.json at all (a non-final window step).
    unit_p = b5.unit_record_path_5(r5b, "1.4b", M0)
    raw = unit_p.read_bytes()
    unit_p.unlink()
    v = _assert_insufficient(w)
    assert any("1.4b" in f for f in v["failures"])
    unit_p.write_bytes(raw)

    # 3. a unit with _unit.json present but a rung file removed (a DIFFERENT
    # step/size from #2, so each corruption is independent).
    rung_p = b5.rung_record_path_5(r5b, "1b", M1, "antonym")
    raw3 = rung_p.read_bytes()
    rung_p.unlink()
    v = _assert_insufficient(w)
    assert any("1b" in f for f in v["failures"])
    rung_p.write_bytes(raw3)

    # 4. a unit without its 5b attestation.
    p4 = b5b.unit5b_record_path_5b(r5b, "1b", M2)
    raw4 = p4.read_bytes()
    p4.unlink()
    v = _assert_insufficient(w)
    assert any("_unit_5b" in f for f in v["failures"])
    p4.write_bytes(raw4)

    # 5. a _unit_5b.json with the wrong prereg tag.
    p5 = b5b.unit5b_record_path_5b(r5b, "2.8b", FINAL)
    raw5 = p5.read_text()
    rec5 = json.loads(raw5)
    rec5["prereg_tag"] = "wrong-tag"
    p5.write_text(json.dumps(rec5))
    v = _assert_insufficient(w)
    assert any("prereg_tag" in f for f in v["failures"])
    p5.write_text(raw5)

    # 6. an extra step directory (nothing else loaded) — the copy must be
    # internally self-consistent: every step-bearing field in this synthetic
    # world embeds the step number as a literal text substring (Task 5's
    # Finding C), and _unit.json's own recorded per-file shas must be
    # refreshed post-substitution or the copy reads as torn, not extra.
    extra = b5b.unit_dir_5b(r5b, "1b", 12000)
    shutil.copytree(b5b.unit_dir_5b(r5b, "1b", M1), extra)
    for fp in extra.iterdir():
        if fp.name != "_unit.json":
            fp.write_text(fp.read_text().replace(str(M1), "12000"))
    unit_p6 = extra / "_unit.json"
    unit_rec6 = json.loads(unit_p6.read_text().replace(str(M1), "12000"))
    unit_rec6["files"] = {name: bg.sha256_file(extra / name) for name in unit_rec6["files"]}
    unit_p6.write_text(json.dumps(unit_rec6))
    v = _assert_insufficient(w)
    assert any("never requested" in f for f in v["failures"])
    shutil.rmtree(extra)

    # 7. a side directory removed entirely — NOT a refusal, EXCLUDED.
    side7 = b5b.units_root_5b(r5b) / "1.4b"
    moved7 = tmp_path / "moved_1.4b"
    shutil.move(str(side7), str(moved7))
    v = _run(w)
    assert v["verdict"] != "INSUFFICIENT_DATA", v["failures"][:3]
    assert v["sides"]["excluded"] == ["1.4b"], v["sides"]
    shutil.move(str(moved7), str(side7))

    # 8. a side with only the final present — NOT a refusal, EXCLUDED.
    moved_members = {}
    for step in fs5b.WINDOW_W:
        d = b5b.unit_dir_5b(r5b, "2.8b", step)
        dest = tmp_path / f"moved_2.8b_{step}"
        shutil.move(str(d), str(dest))
        moved_members[step] = dest
    v = _run(w)
    assert v["verdict"] != "INSUFFICIENT_DATA", v["failures"][:3]
    assert "2.8b" in v["sides"]["excluded"], v["sides"]
    for step, dest in moved_members.items():
        shutil.move(str(dest), str(b5b.unit_dir_5b(r5b, "2.8b", step)))

    # 9. a side with a torn final — a refusal.
    final_dir = b5b.unit_dir_5b(r5b, "1b", FINAL)
    moved9 = tmp_path / "moved_1b_final"
    shutil.move(str(final_dir), str(moved9))
    v = _assert_insufficient(w)
    assert any("1b" in f for f in v["failures"])
    shutil.move(str(moved9), str(final_dir))

    # 10. the host record missing.
    hostp = b5b.host_record_path_5b(r5b)
    raw10 = hostp.read_bytes()
    hostp.unlink()
    v = _assert_insufficient(w)
    assert any("host record" in f for f in v["failures"])
    hostp.write_bytes(raw10)

    # 11. the host record with a drifted stack pin.
    rec11 = json.loads(raw10)
    rec11["stack"]["torch"] = "0.0.0"
    hostp.write_text(json.dumps(rec11))
    v = _assert_insufficient(w)
    assert any("host record" in f for f in v["failures"])
    hostp.write_bytes(raw10)

    # 12a. results/gate1_5b.json missing.
    g1p = b5b.gate1_path_5b(r5b)
    raw12 = g1p.read_bytes()
    g1p.unlink()
    v = _assert_insufficient(w)
    assert any("gate 1" in f for f in v["failures"])
    g1p.write_bytes(raw12)

    # 12b. results/gate1_5b.json with pass flipped.
    rec12 = json.loads(raw12)
    rec12["pass"] = not rec12["pass"]
    g1p.write_text(json.dumps(rec12))
    v = _assert_insufficient(w)
    assert any("gate 1" in f for f in v["failures"])
    g1p.write_bytes(raw12)

    # 13a. the power record missing.
    pp = b5b.power_path_5b(r5b)
    raw13 = pp.read_bytes()
    pp.unlink()
    v = _assert_insufficient(w)
    assert any("power" in f.lower() for f in v["failures"])
    pp.write_bytes(raw13)

    # 13b. the power record with n_sim tampered.
    rec13 = json.loads(raw13)
    rec13["n_sim"] = rec13["n_sim"] + 1
    pp.write_text(json.dumps(rec13, indent=1, sort_keys=True))
    v = _assert_insufficient(w)
    assert any("power" in f.lower() for f in v["failures"])
    pp.write_bytes(raw13)

    # 13c. the power record with structure_sha256 tampered.
    rec13c = json.loads(raw13)
    rec13c["structure_sha256"] = "0" * 64
    pp.write_text(json.dumps(rec13c, indent=1, sort_keys=True))
    v = _assert_insufficient(w)
    assert any("power" in f.lower() for f in v["failures"])
    pp.write_bytes(raw13)

    # 14. the projection not an ancestor.
    v = _assert_insufficient(w, is_ancestor=lambda a, b: False)
    assert any("projection" in f for f in v["failures"])

    # 15a. Experiment 5's tree: a rung count edited.
    p15a = b5.rung_record_path_5(r5, "2.8b", b5.FINAL_STEP_5, "antonym")
    raw15a = p15a.read_bytes()
    rec15a = json.loads(raw15a)
    rec15a["correct"] += 1
    p15a.write_text(json.dumps(rec15a))
    v = _assert_insufficient(w)
    assert any(f.startswith("5b exp5") for f in v["failures"])
    p15a.write_bytes(raw15a)

    # 15b. Experiment 5's tree: the verdict.json edited.
    vp15 = r5 / "results" / "verdict.json"
    raw15b = vp15.read_bytes()
    vv15 = json.loads(raw15b)
    vv15["primary"]["T"] = vv15["primary"]["T"] + 1e-9
    vp15.write_text(json.dumps(vv15))
    v = _assert_insufficient(w)
    assert any("differs from the committed" in f for f in v["failures"])
    vp15.write_bytes(raw15b)

    # 15c. an Experiment 5 instrument blob not bound at exp5-closed.
    v = _assert_insufficient(w, blob_sha=lambda t, r: ("0" * 64) if r == "experiments/exp5/stats_5.py"
                             else bg.sha256_file(b5b.REPO / r))
    assert any("does not bind" in f for f in v["failures"])

    # 16. the exp5-closed tag absent.
    v = _assert_insufficient(w, tag_exists=lambda t: t != "exp5-closed")
    assert any("exp5-closed" in f for f in v["failures"])

    # 17. the 5b prereg tag absent.
    v = _assert_insufficient(w, tag_exists=lambda t: t != b5b.PREREG_TAG_5B)
    assert any(b5b.PREREG_TAG_5B in f for f in v["failures"])

    # 18. a corrupt json (_unit_5b.json truncated mid-token).
    p18 = b5b.unit5b_record_path_5b(r5b, "2.8b", M0)
    raw18 = p18.read_text()
    p18.write_text(raw18[: len(raw18) // 2])
    v = _assert_insufficient(w)
    p18.write_text(raw18)

    # control: clean again after every corruption is restored.
    v_final = _run(w)
    assert v_final["verdict"] == "SURVIVES", v_final["failures"][:3]


# ---------------------- the five gated sites + verdict write (fix round 1)

def test_the_five_post_units_sites_raise_without_the_wrapper(tmp_path, monkeypatch):
    """Fix round 1 (Important 1): `cells`/`primary`/`sigma hat`/
    `calibration`/`modifier` sit behind `if not failures and cells5_live
    is not None:` — no corruption shape reaches them (every shape IS a
    failure), so they need a PASSING tree. One SURVIVES world, one
    `st.<fn>` patched to raise ValueError at a time, restored between —
    under the stripped wrapper the raise propagates out of `run()`
    instead of becoming a labelled failure."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    # power_gate="skip" throughout this test: power_5b.arm_5b calls st.primary_5b AND
    # st.sigma_hat_5b internally (the SAME module-level names this test monkeypatches),
    # so power_gate="full"'s real compute_5b recomputation at the EARLIER "5b power
    # record" gate would collaterally raise there first, short-circuiting `failures`
    # before the cells/primary/sigma-hat/calibration/modifier block is even reached —
    # found by running this test once and seeing "5b power record" catch it instead of
    # the intended site (Task 6 fix round 1 finding).
    v0 = _run(w, power_gate="skip")
    assert v0["verdict"] == "SURVIVES", v0["failures"][:3]        # sanity: this block is reached clean

    sites = (("cells_5b", "5b cells"), ("primary_5b", "5b primary"), ("sigma_hat_5b", "5b sigma hat"),
            ("calibration_read_5b", "5b calibration"), ("modifier_5b", "5b modifier"))
    for fn_name, label in sites:
        orig = getattr(an.st, fn_name)
        monkeypatch.setattr(an.st, fn_name, lambda *a, **k: (_ for _ in ()).throw(ValueError("boom")))
        try:
            v = _run(w, power_gate="skip")
        except Exception as e:  # noqa: BLE001 — the thing under test
            pytest.fail(f"analyze_5b.run() raised for {fn_name}: {type(e).__name__}: {e}")
        finally:
            monkeypatch.setattr(an.st, fn_name, orig)
        assert v["verdict"] == "INSUFFICIENT_DATA", (fn_name, v)
        assert any(f.startswith(label) for f in v["failures"]), (fn_name, v["failures"])

    # the clean world still computes normally once every patch is undone
    v_final = _run(w, power_gate="skip")
    assert v_final["verdict"] == "SURVIVES", v_final["failures"][:3]


def test_verdict_write_site_raises_without_the_wrapper(tmp_path, monkeypatch):
    """Fix round 1: '5b verdict write' is the one site whose failure does
    NOT enter `v["failures"]` — it is recorded as `v["write_failure"]`
    with the rest of the verdict otherwise intact (design: a write
    failure must never retroactively change a computed verdict). Under
    the stripped wrapper the OSError propagates out of `run()` entirely."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    vpath = w["root5b"] / "results" / "verdict.json"
    vpath.mkdir(parents=True, exist_ok=True)          # a DIRECTORY where the write expects a file
    try:
        v = _run(w, write=True)
    except Exception as e:  # noqa: BLE001 — the thing under test
        pytest.fail(f"analyze_5b.run() raised on a write failure: {type(e).__name__}: {e}")
    finally:
        vpath.rmdir()
    assert v["verdict"] == "SURVIVES", v["failures"][:3]          # the verdict is otherwise intact
    assert isinstance(v.get("write_failure"), str) and v["write_failure"].startswith("5b verdict write")


# --------------------------------------------------------- the site harness

def _run_function_node():
    src = AN5B_PATH.read_text()
    tree = ast.parse(src, filename=str(AN5B_PATH))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "run":
            return node
    raise RuntimeError("analyze_5b.run() not found in its own AST")


def _site_templates_5b() -> list:
    """Every `collect_total_5b(thunk, label)` call TEXTUALLY INSIDE
    `run()`'s own body (nested `def`s and lambdas included, since
    `ast.walk` descends into them; `secondaries_5b` — a SEPARATE
    top-level function `run()` merely CALLS — is excluded by
    construction). A plain string label is used as-is; an f-string
    label's constant PREFIX is used, since every f-string site here is
    `f"5b units {size}"`."""
    out = []
    for node in ast.walk(_run_function_node()):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (func.id if isinstance(func, ast.Name) else
                func.attr if isinstance(func, ast.Attribute) else None)
        if name != "collect_total_5b" or len(node.args) < 2:
            continue
        label_node = node.args[1]
        if isinstance(label_node, ast.Constant) and isinstance(label_node.value, str):
            out.append(label_node.value)
        elif isinstance(label_node, ast.JoinedStr):
            prefix = ""
            for piece in label_node.values:
                if isinstance(piece, ast.Constant):
                    prefix += str(piece.value)
                else:
                    break
            out.append(prefix)
    return out


def test_site_template_count_is_24():
    """Task 6 finding, disclosed (Experiment 5's own `mutation_check.py`
    convention, carried forward): a totality mutant strips exactly one
    `collect_total_5b` call from `run()`'s own body, textually — this
    count check FAILS the instant any one of them is applied, giving
    every totality mutant a STRUCTURAL kill independent of whether the
    shapes below happen to drive that specific site to a raise. The
    brief does not name an exact count for 5b; 24 is the number this
    same AST walk finds in the committed `analyze_5b.py::run()` today."""
    assert len(_site_templates_5b()) == 24, _site_templates_5b()


def test_every_collect_total_5b_site_in_run_is_reached_across_the_shapes(tmp_path, monkeypatch):
    templates = _site_templates_5b()
    seen = []
    real = an.collect_total_5b

    def _recording(thunk, label):
        seen.append(label)
        return real(thunk, label)
    monkeypatch.setattr(an, "collect_total_5b", _recording)

    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    v = _run(w)                                                # the clean run: reaches every site
    assert v["verdict"] == "SURVIVES", v["failures"][:3]       # above the "not failures" gate too
    _run(w, write=True)                                        # "5b verdict write" — write=True only

    # a refusal shape too, for the record (every site above the primary/
    # cells block is unconditional and already recorded by the two calls
    # above; this call is harmless extra coverage, not load-bearing).
    hp = b5b.halt_marker_path_5b(w["root5b"], "1b")
    hp.write_text("x\n")
    _run(w)
    hp.unlink()

    hit = {t for t in templates if any(lbl == t or lbl.startswith(t) for lbl in seen)}
    missing = [t for t in templates if t not in hit]
    assert not missing, f"never reached: {missing}"
