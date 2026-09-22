# experiments/exp5/tests/test_totality_5.py
"""Totality (Task 6 brief, step 3): every tree shape the runners can
leave gives `analyze_5.run()` INSUFFICIENT_DATA, never a raise — on the
MATCHED world `full_shape_5.write_world_5` builds, one corruption at a
time, each applied then RESTORED before the next (the same pattern
`test_full_shape_5.py`'s own `test_refusal_routes_deliver_insufficient_
data` uses, one world built once per test function).

Shape 5 (a pair `dropped`) is the one NON-refusal case in the brief's
list — 6.9b×1b already drops naturally on this synthetic loss curve
(`PROGRESS.md`'s Task 5 entry: "the pair that ends up first in
log['pairs'] once 6.9b×1b drops"), so it is asserted directly on the
CLEAN world rather than manufactured.

Unlike `test_full_shape_5.py`'s own `_run` (which forces `referents_
sha=False, imports_pinned=False, frozen_check=lambda: None` to work
around Task 6 not having pinned yet), this file's `_run` leaves those
three at their PRODUCTION defaults — `FROZEN_SHA256_5`/`IMPORTED_
SHA256_5`/`REFERENTS_5_SHA256` are now pinned against the REAL repo
tree (independent of the synthetic `tmp_path` world), so exercising
them for real here is strictly more coverage, and is what lets the
27-site census below reach the import-surface and referents sites.

Plus the 27-site harness (28 in the committed source — the extra site
is `"5 verdict write"`, gated behind `write=True`; disclosed and
covered as a superset in `test_site_template_count_matches_the_
brief`): every `collect_total_5` label textually inside `analyze_5.
run()`'s own body (AST-derived) is reached at least once across the
shapes below. `run()`'s "5 gate 1(c) {size}" site is
gated behind `battery_5.gate1_interior_steps_5(size)`, which the
synthetic world always leaves empty (`full_shape_5.apply_shrink` sets
`GATE1_INTERIOR_5 = {}`) — one extra probe call, with `GATE1_
INTERIOR_5` monkeypatched non-empty for a size the world actually
built, reaches it (the record is absent, so that one call refuses;
irrelevant to the census, which only needs the SITE reached)."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp5 import analyze_5 as an
from experiments.exp5 import battery_5 as b5
from experiments.exp5.tests import full_shape_5 as fs

pytestmark = pytest.mark.slow

AN5_PATH = Path(an.__file__)


def _run(root, w, **over):
    kw = dict(root=root, write=False, n_sample=200, n_boot=100, manifest=w["manifest"], sl=w["sl"],
              tag_exists=lambda t: True, blob_sha=lambda t, r: bg.sha256_file(b5.REPO / r),
              blobs_bound=lambda t, p, **k: [],
              projection_commit="p1", is_ancestor=lambda a, b: True, seal_tag_commit="s1",
              power_gate="full")
    kw.update(over)
    return an.run(**kw)


def _assert_insufficient(root, w, **over):
    """The brief's own wording: wrap in `try`, fail the test on any
    exception — `analyze_5.run()`'s contract is that it never raises
    for a DATA problem."""
    try:
        v = _run(root, w, **over)
    except Exception as e:  # noqa: BLE001 — the thing under test
        pytest.fail(f"analyze_5.run() raised instead of returning INSUFFICIENT_DATA: "
                   f"{type(e).__name__}: {e}")
    assert v["verdict"] == "INSUFFICIENT_DATA", v
    return v


# ------------------------------------------------------------- the 9 shapes

def test_every_runner_leavable_tree_shape_gives_insufficient_data(tmp_path, monkeypatch):
    w = fs.write_world_5(tmp_path, "MATCHED", monkeypatch=monkeypatch)
    assert _run(tmp_path, w)["verdict"] == "MATCHED"          # the clean control

    # 1. finals halted at gate 1(a): a HALTED marker under 2.8b PLUS the
    # 2.8b final unit left partial (one rung file gone).
    halt_p = b5.halt_marker_path_5(tmp_path, "2.8b")
    halt_p.write_text("gate 1(a): forced halt (totality test)\n")
    rung_p = b5.rung_record_path_5(tmp_path, "2.8b", b5.FINAL_STEP_5, "antonym")
    raw = rung_p.read_bytes()
    rung_p.unlink()
    v = _assert_insufficient(tmp_path, w)
    assert any("halt" in f.lower() for f in v["failures"])
    rung_p.write_bytes(raw)
    halt_p.unlink()

    # 2. a torn unit: no _unit.json at all (a non-final spine step).
    unit_p = b5.unit_record_path_5(tmp_path, "6.9b", 6000)
    raw = unit_p.read_bytes()
    unit_p.unlink()
    v = _assert_insufficient(tmp_path, w)
    assert any("6.9b" in f for f in v["failures"])
    unit_p.write_bytes(raw)

    # 3. a unit with _unit.json present but a rung file removed (a
    # DIFFERENT step from #2, so each corruption is independent).
    rung_p2 = b5.rung_record_path_5(tmp_path, "2.8b", 16000, "count_div13")
    raw2 = rung_p2.read_bytes()
    rung_p2.unlink()
    v = _assert_insufficient(tmp_path, w)
    assert any("2.8b" in f for f in v["failures"])
    rung_p2.write_bytes(raw2)

    # 4. a sweep killed mid-bisection: the search log's pair left "open"
    # (never resolved), stale against what the committed units now show.
    log_p = b5.search_log_path_5(tmp_path, "2.8b")
    raw_log = log_p.read_bytes()
    log = json.loads(raw_log)
    log["pairs"]["1.4b"]["status"] = "open"
    log_p.write_text(json.dumps(log))
    v = _assert_insufficient(tmp_path, w)
    assert any("gate 4" in f for f in v["failures"])
    log_p.write_bytes(raw_log)

    # 5. a pair `dropped` is NOT a refusal — 6.9b x 1b drops naturally
    # on this synthetic curve; the clean world still yields MATCHED.
    v = _run(tmp_path, w)
    assert v["verdict"] == "MATCHED", v["failures"]
    assert v["gate4"]["pairs_dropped"] >= 1
    assert any(d["small"] == "1b" and d["large"] == "6.9b" for d in v["gate4"]["dropped_detail"])

    # 6. a size with no search log at all.
    log_p6 = b5.search_log_path_5(tmp_path, "6.9b")
    raw6 = log_p6.read_bytes()
    log_p6.unlink()
    v = _assert_insufficient(tmp_path, w)
    assert any("search log" in f for f in v["failures"])
    log_p6.write_text(raw6.decode())

    # 7. a corrupt json (torn mid-token).
    loss_p = b5.loss_record_path_5(tmp_path, "6.9b", 6000)
    raw7 = loss_p.read_text()
    loss_p.write_text(raw7[: len(raw7) // 2])
    v = _assert_insufficient(tmp_path, w)
    loss_p.write_text(raw7)

    # 8. a missing power record.
    pp = b5.power_path_5(tmp_path)
    raw8 = pp.read_bytes()
    pp.unlink()
    v = _assert_insufficient(tmp_path, w)
    assert any("power" in f.lower() for f in v["failures"])
    pp.write_bytes(raw8)

    # 9. a projection not in history (gate 5 / B-7).
    v = _assert_insufficient(tmp_path, w, is_ancestor=lambda a, b: False)
    assert any("projection" in f for f in v["failures"])

    # control: clean again after every corruption is restored.
    assert _run(tmp_path, w)["verdict"] == "MATCHED"


# --------------------------------------------------------- the 27-site harness

def _run_function_node():
    src = AN5_PATH.read_text()
    tree = ast.parse(src, filename=str(AN5_PATH))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "run":
            return node
    raise RuntimeError("analyze_5.run() not found in its own AST")


def _site_templates_5() -> list:
    """Every `collect_total_5(thunk, label)` call TEXTUALLY INSIDE
    `run()`'s own body (nested `def`s and lambdas included, since
    `ast.walk` descends into them; `secondaries_5` — a SEPARATE
    top-level function `run()` merely CALLS — is excluded by
    construction). A plain string label is used as-is; an f-string
    label's constant PREFIX (the text up to its first `{placeholder}`)
    is used, since every f-string site here is `f"<literal> {size}"`."""
    out = []
    for node in ast.walk(_run_function_node()):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (func.id if isinstance(func, ast.Name) else
                func.attr if isinstance(func, ast.Attribute) else None)
        if name != "collect_total_5" or len(node.args) < 2:
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


def test_site_template_count_matches_the_brief():
    """Task 6 finding, disclosed: the brief's prose says "27-site
    harness"; the real count, taken from this same AST walk of the
    committed `run()`, is 28 — the extra site is `"5 verdict write"`
    (the `if write: ...` block near the end of `run()`, gated behind
    `write=True`). It is a real `collect_total_5` call textually
    inside `run()`'s own body, so it is covered here as a superset of
    the brief's count rather than excluded to force the number to
    match (PROGRESS.md, Task 6)."""
    assert len(_site_templates_5()) == 28, _site_templates_5()


def test_every_collect_total_5_site_in_run_is_reached_across_the_shapes(tmp_path, monkeypatch):
    templates = _site_templates_5()
    seen = []
    real = an.collect_total_5

    def _recording(thunk, label):
        seen.append(label)
        return real(thunk, label)
    monkeypatch.setattr(an, "collect_total_5", _recording)

    w = fs.write_world_5(tmp_path, "MATCHED", monkeypatch=monkeypatch)
    _run(tmp_path, w)                                          # the clean run alone

    # gate 1(c): unreachable via the synthetic world (GATE1_INTERIOR_5
    # forced empty by apply_shrink) — one probe call with it patched
    # non-empty for a size the world actually built a step for. Left
    # patched for the rest of this test (harmless — the later replays
    # below don't depend on GATE1_INTERIOR_5 being empty).
    monkeypatch.setattr(b5, "GATE1_INTERIOR_5", {"2.8b": (1000,)})
    _run(tmp_path, w)

    # the halted/no-search-log/no-power-record/bad-ancestor shapes reach
    # sites the clean run short-circuits past (later closures skip work
    # when an earlier dependency came back None) — replay a subset.
    halt_p = b5.halt_marker_path_5(tmp_path, "2.8b")
    halt_p.write_text("x\n")
    _run(tmp_path, w)
    halt_p.unlink()

    log_p = b5.search_log_path_5(tmp_path, "6.9b")
    raw = log_p.read_bytes()
    log_p.unlink()
    _run(tmp_path, w)
    log_p.write_bytes(raw)

    pp = b5.power_path_5(tmp_path)
    raw_p = pp.read_bytes()
    pp.unlink()
    _run(tmp_path, w)
    pp.write_bytes(raw_p)

    _run(tmp_path, w, is_ancestor=lambda a, b: False)

    # "5 verdict write" (the 28th site — see test_site_template_count_
    # matches_the_brief) only fires with write=True.
    _run(tmp_path, w, write=True)

    hit = {t for t in templates if any(lbl == t or lbl.startswith(t) for lbl in seen)}
    missing = [t for t in templates if t not in hit]
    assert not missing, f"never reached: {missing}"
