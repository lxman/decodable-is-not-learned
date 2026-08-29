# experiments/exp2k/tests/test_totality_2k.py
"""Verdict-path totality (2h/2i/2j's lineage): every tree `analyze_2k.
run()` can be handed must reach a FROZEN TERMINAL (INSUFFICIENT_DATA),
never an uncaught exception — one representative upstream 2i-tree shape
reached THROUGH 2k's `run()`, plus every shape new to 2k's own readers
(the tier record/draws, the seal, the power record, the 2j-verdict
comparison, the forced-exception injection sites), plus the control
(an untouched world still reaches DENSITY).

Each `_insufficient` case asserts `v["verdict"] == "INSUFFICIENT_DATA"`
and the needle in `v["referents"]["failures"]` (the FULL list — not
`v["reason"]`, which prints only the first five), and never raises.

Task 3 left `load_tier_2k`'s two per-size calls at the top of `run()`'s
tier-loading block (`analyze_2k.py`, the "the 2k tiers, the seal, the
power record" section) NOT wrapped in `collect_total`, unlike every
other loader/statistic in this file — Task 4's brief restricted every
edit to `analyze_2k.py` to the one `frozen_check` change (Ruling 3), so
the gap stood, ledgered in PROGRESS.md as defence-in-depth for Task 5
to close. Task 5 follow-up 2 wrapped both call sites in
`collect_total("2k tier {size} load", ...)`;
`test_load_tier_2k_forced_exception_now_lands_gracefully` replaces the
former `..._is_a_known_gap` test, asserting the closed (graceful)
behaviour like every other case in this file."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from experiments.exp2i import battery_2i as bi
from experiments.exp2k import analyze_2k as an
from experiments.exp2k import battery_2k as bk
from experiments.exp2k.tests import full_shape as fs


@pytest.fixture(scope="module")
def base_world(tmp_path_factory):
    root = tmp_path_factory.mktemp("totality_base")
    seal = fs.write_world_2k(root, world="density")
    return root, seal


@pytest.fixture
def world(base_world, tmp_path):
    root, seal = base_world
    shutil.copytree(root / "results", tmp_path / "results")
    return tmp_path, seal


def _run(root, seal, **kw):
    kw.setdefault("n_perm", 30)
    kw.setdefault("n_boot", 10)
    kw.setdefault("referents_sha", False)
    kw.setdefault("imports_pinned", False)
    # the seal's `verdict_2i_path` is an ABSOLUTE path baked in at
    # `base_world` build time for the ORIGINAL base root; every per-test
    # `world` fixture copies `results/` into a FRESH tmp_path, so a test
    # that edits the copy's verdict.json must also redirect this kwarg
    # to the copy (2j's totality test's own lesson) — defaulted here so
    # every test in this file gets the copy by construction.
    kw.setdefault("verdict_2i_path", Path(root) / "results" / "verdict.json")
    return an.run(root_2i=root, root_2k=root, **{**seal, **kw})


def _insufficient(root, seal, needle, **kw):
    v = _run(root, seal, **kw)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["verdict"]
    assert any(needle in f for f in v["referents"]["failures"]), v["referents"]["failures"]
    assert v["primary"] is None and v["secondaries"] is None
    return v


def _raise_injected(*a, **kw):
    raise ValueError("injected for a Task 4 totality test")


# --------------------------------------- one upstream 2i-tree shape,
# --------------------------------------- reached through 2k's run()

def test_predictor_seal_content_torn(world):
    root, seal = world
    bi.predictor_seal_path(root).write_text('{"sha256": "a"')
    _insufficient(root, seal, "2k/2i predictor seal content")


# ------------------------------------------------------- tier record

def test_tier_record_torn(world):
    root, seal = world
    bk.tier_record_path(root, "1b", "antonym").write_text('{"rung": "a')
    _insufficient(root, seal, "2k tier 1b/antonym record read")


def test_tier_record_is_a_list(world):
    root, seal = world
    bk.tier_record_path(root, "1b", "antonym").write_text("[]")
    _insufficient(root, seal, "record is not a dict")


def test_tier_record_is_a_directory(world):
    """`load_tier_2k`'s FIRST check is `rp.is_file() and dp.is_file()` —
    a directory in the record's place is caught THERE ("record or draws
    file missing"), never reaching the `json.loads` attempt the other
    two record shapes exercise."""
    root, seal = world
    p = bk.tier_record_path(root, "1b", "antonym")
    p.unlink()
    p.mkdir()
    _insufficient(root, seal, "2k tier 1b/antonym: record or draws file missing")


# -------------------------------------------------------- tier draws

def test_draws_gz_truncated_is_eof_not_a_raise(world):
    root, seal = world
    p = bk.tier_draws_path(root, "1b", "sub_base8")
    b = p.read_bytes()
    p.write_bytes(b[:int(len(b) * 0.5)])
    v = _insufficient(root, seal, "rows read")
    assert any("EOFError" in f for f in v["referents"]["failures"])


def test_draws_gz_corrupt_is_zlib_error_not_a_raise(world):
    root, seal = world
    p = bk.tier_draws_path(root, "1b", "sub_base8")
    b = bytearray(p.read_bytes())
    for i in range(20, min(len(b), 400)):     # deflate payload, past the header
        b[i] ^= 0xFF
    p.write_bytes(bytes(b))
    _insufficient(root, seal, "rows read")


def test_draws_row_with_three_seed_streams(world):
    root, seal = world
    p = bk.tier_draws_path(root, "1b", "sub_base8")
    rows = bk.read_rows_2k(p)
    del rows[7]["draws"]["3"]
    fs.write_draws(p, rows)
    _insufficient(root, seal, "seed streams")


def test_draws_row_with_a_63_draw_stream(world):
    root, seal = world
    p = bk.tier_draws_path(root, "1b", "sub_base8")
    rows = bk.read_rows_2k(p)
    rows[7]["draws"]["2"] = rows[7]["draws"]["2"][:-1]
    fs.write_draws(p, rows)
    _insufficient(root, seal, "draws_per_seed")


# ---------------------------------------------------- tier record pins

def test_record_seeds_field_wrong(world):
    root, seal = world
    p = bk.tier_record_path(root, "1b", "antonym")
    rec = json.loads(p.read_text())
    rec["seeds"] = [0, 1, 2]
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "seeds =")


def test_record_k_total_wrong(world):
    root, seal = world
    p = bk.tier_record_path(root, "1b", "antonym")
    rec = json.loads(p.read_text())
    rec["k_total"] = 64
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "k_total =")


def test_record_tallies_disagree_with_the_draws(world):
    root, seal = world
    p = bk.tier_record_path(root, "1b", "antonym")
    rec = json.loads(p.read_text())
    rec["per_seed_tallies"] = dict(rec["per_seed_tallies"])
    rec["per_seed_tallies"]["0"] = dict(rec["per_seed_tallies"]["0"])
    rec["per_seed_tallies"]["0"]["full_string"] += 1
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "bits and tallies")


def test_gate1_draws_compared_mismatch(world):
    root, seal = world
    p = bk.tier_record_path(root, "1b", "antonym")
    rec = json.loads(p.read_text())
    rec["gate1"] = dict(rec["gate1"])
    rec["gate1"]["draws_compared"] = 31999
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "gate 1 attested")


# ------------------------------------------------------------- seal

def test_seal_missing(world):
    root, seal = world
    bk.seal_path(root).unlink()
    _insufficient(root, seal, "2k seal read")


def test_seal_torn(world):
    root, seal = world
    bk.seal_path(root).write_text('{"tag": "x"')
    _insufficient(root, seal, "2k seal read")


def test_seal_tag_wrong(world):
    root, seal = world
    p = bk.seal_path(root)
    rec = json.loads(p.read_text())
    rec["tag"] = "wrong-tag"
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "2k seal: tag")


def test_seal_sampling_block_altered(world):
    root, seal = world
    p = bk.seal_path(root)
    rec = json.loads(p.read_text())
    rec["sampling"] = dict(rec["sampling"], temperature=2.0)
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "sampling block")


def test_seal_counts_altered(world):
    root, seal = world
    p = bk.seal_path(root)
    rec = json.loads(p.read_text())
    lst = list(rec["counts"]["1b"]["antonym"])
    lst[0] += 1
    rec["counts"] = dict(rec["counts"])
    rec["counts"]["1b"] = dict(rec["counts"]["1b"])
    rec["counts"]["1b"]["antonym"] = lst
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "2k seal: counts[")


def test_seal_file_sha_altered(world):
    root, seal = world
    p = bk.seal_path(root)
    rec = json.loads(p.read_text())
    rel = sorted(rec["files"])[0]
    rec["files"] = dict(rec["files"], **{rel: "0" * 64})
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "missing or changed since the seal")


def test_seal_sha256_altered(world):
    root, seal = world
    p = bk.seal_path(root)
    rec = json.loads(p.read_text())
    rec["sha256"] = "0" * 64
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "sha256 is not the sha")


def test_seal_counts_by_k_altered(world):
    root, seal = world
    p = bk.seal_path(root)
    rec = json.loads(p.read_text())
    lst = list(rec["counts_by_k"]["1b"]["64"]["antonym"])
    lst[0] += 1
    rec["counts_by_k"] = dict(rec["counts_by_k"])
    rec["counts_by_k"]["1b"] = dict(rec["counts_by_k"]["1b"])
    rec["counts_by_k"]["1b"]["64"] = dict(rec["counts_by_k"]["1b"]["64"])
    rec["counts_by_k"]["1b"]["64"]["antonym"] = lst
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "counts_by_k")


def test_seal_files_table_truncated_is_a_coverage_failure(world):
    """Freeze F-3: a self-consistent but incomplete files table (entries
    dropped, `sha256` recomputed over the survivors, the power record's
    `predictor_sha256` re-pointed at the new composite) attested nothing
    and passed. Coverage of the 36 tier files is now required."""
    root, seal = world
    p = bk.seal_path(root)
    rec = json.loads(p.read_text())
    rec["files"] = {}
    rec["sha256"] = an.seal_sha_of({})
    p.write_text(json.dumps(rec))
    pw = bk.power_path(root)
    prec = json.loads(pw.read_text())
    prec["predictor_sha256"] = rec["sha256"]
    pw.write_text(json.dumps(prec))
    _insufficient(root, seal, "does not cover 36 of the 36 tier files")


def test_seal_files_table_missing_one_entry(world):
    root, seal = world
    p = bk.seal_path(root)
    rec = json.loads(p.read_text())
    gone = sorted(rec["files"])[0]
    rec["files"] = {k: v for k, v in rec["files"].items() if k != gone}
    rec["sha256"] = an.seal_sha_of(rec["files"])
    p.write_text(json.dumps(rec))
    pw = bk.power_path(root)
    prec = json.loads(pw.read_text())
    prec["predictor_sha256"] = rec["sha256"]
    pw.write_text(json.dumps(prec))
    _insufficient(root, seal, "does not cover 1 of the 36 tier files")


def test_whole_cell_seed_stream_copy_refuses(world):
    """Freeze F-4: gate 1 covers seed 0 only. A cell whose seed-2 stream
    is a byte-copy of seed 0 on all 500 items leaves x^(256) an exact
    multiple of x^(64) — rank-identical, so T would come back at 2i's
    own .0949 as a plausible NOT-DENSITY rather than a refusal."""
    root, seal = world
    dp = bk.tier_draws_path(root, "1b", "antonym")
    rows = bk.read_rows_2k(dp)
    for row in rows:
        row["draws"]["2"] = list(row["draws"]["0"])
    fs.write_draws(dp, rows)
    rp = bk.tier_record_path(root, "1b", "antonym")
    rec = json.loads(rp.read_text())
    rec["per_seed_tallies"]["2"] = dict(rec["per_seed_tallies"]["0"])
    rp.write_text(json.dumps(rec))
    _insufficient(root, seal, "reproduces seed 0's stream on all 500 items")


def test_seed_stream_census_is_printed_on_a_clean_tree(world):
    root, seal = world
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "DENSITY", v["reason"]
    census = v["referents"]["seed_stream_census_2k"]
    assert set(census) == set(bk.SIZES_2K)
    assert census["1b"]["antonym"] == {"1": 0, "2": 0, "3": 0}
    assert v["referents"]["pins_active"] == {"frozen_modules": True, "import_surface": False,
                                             "referent_manifest": False}


# ------------------------------------------------------------- power

def test_power_torn(world):
    root, seal = world
    bk.power_path(root).write_text('{"primary": {')
    _insufficient(root, seal, "2k power record")


def test_power_declared_status_wrong(world):
    root, seal = world
    p = bk.power_path(root)
    rec = json.loads(p.read_text())
    rec["primary"] = dict(rec["primary"], declared_status="MAYBE")
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "declared_status")


def test_power_rungs_superset(world):
    root, seal = world
    p = bk.power_path(root)
    rec = json.loads(p.read_text())
    rec["primary"] = dict(rec["primary"], rungs=list(rec["primary"]["rungs"]) + ["extra"])
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "power rungs")


def test_power_n_trained_steps_wrong(world):
    root, seal = world
    p = bk.power_path(root)
    rec = json.loads(p.read_text())
    rec["primary"] = dict(rec["primary"], n_trained_steps=20)
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "n_trained_steps")


def _power_edit(root, **fields):
    p = bk.power_path(root)
    rec = json.loads(p.read_text())
    rec["primary"] = dict(rec["primary"], **fields)
    p.write_text(json.dumps(rec))


def test_power_claims_rungs_simulated_wrong(world):
    """Freeze F-2: the power record's simulation claims are re-derived."""
    root, seal = world
    _power_edit(root, rungs_simulated=[], dropped_degenerate=list(seal_rungs(root)))
    _insufficient(root, seal, "2k power claims: dropped_degenerate", n_perm=200, n_boot=20)


def test_power_claims_n_pos_wrong(world):
    root, seal = world
    rungs = seal_rungs(root)
    _power_edit(root, n_pos_lower_bound={r: 0 for r in rungs})
    _insufficient(root, seal, "n_pos_lower_bound", n_perm=200, n_boot=20)


def test_power_claims_t_bar_and_alpha_wrong(world):
    root, seal = world
    _power_edit(root, t_bar=0.0, alpha=1.0)
    v = _insufficient(root, seal, "2k power claims: t_bar", n_perm=200, n_boot=20)
    assert any("2k power claims: alpha" in f for f in v["referents"]["failures"])


def test_power_claims_fields_absent(world):
    """A record that attests none of them cannot be checked — refuse."""
    root, seal = world
    p = bk.power_path(root)
    rec = json.loads(p.read_text())
    rec["primary"] = {k: v for k, v in rec["primary"].items()
                      if k not in an.POWER_CLAIM_FIELDS_2K}
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "does not attest", n_perm=200, n_boot=20)


def seal_rungs(root):
    return sorted(json.loads(bk.power_path(root).read_text())["primary"]["rungs"])


def test_power_predictor_sha_wrong(world):
    root, seal = world
    p = bk.power_path(root)
    rec = json.loads(p.read_text())
    rec["predictor_sha256"] = "0" * 64
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "predictor_sha256")


# ------------------------------------------- 2j verdict.json missing:
# ------------------------------------------- the verdict STANDS (DENSITY)

def test_verdict_2j_missing_leaves_s3_and_s6_failed_but_the_verdict_stands(world, tmp_path_factory):
    root, seal = world
    missing = tmp_path_factory.mktemp("missing_2j") / "verdict.json"
    v = _run(root, seal, n_perm=200, n_boot=20, verdict_2j_path=missing)
    assert v["verdict"] == "DENSITY", v["reason"]
    assert v["secondaries"]["S3 matched density 1b"]["failed"]
    assert v["secondaries"]["S6 410m replicate"]["failed"]
    assert any("S3 matched density 1b" in f for f in v["secondaries"]["failures"])


# ---------------------------------------- forced-exception injection sites

def test_import_surface_entry_failure(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an, "check_imports_2k", _raise_injected)
    v = _run(root, seal, imports_pinned=True)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert any("2k import surface (entry)" in f for f in v["referents"]["failures"])


def test_import_surface_exit_failure(world, monkeypatch):
    # check_imports_2k runs TWICE in run() (entry, then exit after core is
    # computed) through the SAME module-level name — a blanket monkeypatch
    # would fail entry first and never reach exit, so this lets the first
    # call through and breaks only the second.
    root, seal = world
    orig = an.check_imports_2k
    calls = {"n": 0}

    def wrapped():
        calls["n"] += 1
        if calls["n"] >= 2:
            raise ValueError("injected for a Task 5 totality test")
        return orig()

    monkeypatch.setattr(an, "check_imports_2k", wrapped)
    v = _run(root, seal, imports_pinned=True)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert any("2k import surface (exit)" in f for f in v["referents"]["failures"])


def test_load_tier_2k_forced_exception_now_lands_gracefully(world, monkeypatch):
    """Task 5 follow-up 2 closed the gap the module docstring describes:
    both per-size `load_tier_2k(...)` calls in `run()` are now
    `collect_total`-wrapped, so a forced exception lands
    INSUFFICIENT_DATA instead of escaping uncaught."""
    root, seal = world
    monkeypatch.setattr(an, "load_tier_2k", _raise_injected)
    _insufficient(root, seal, "2k tier 1b load")


def test_seal_failures_2k_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an, "seal_failures_2k", _raise_injected)
    _insufficient(root, seal, "2k seal vs re-derivation")


def test_run_test_forced_exception_in_core(world, monkeypatch):
    """`_run_test` is called by the comparison gate, the block gate, AND
    the core primary — all under the SAME module-global name — so a
    blanket monkeypatch would fail the comparison gate first and never
    reach `_core()` at all. Selective on the primary's own distinctive
    size label ("1b:k256", used nowhere else) isolates the shape the
    brief asks for without touching frozen code."""
    root, seal = world
    real = an._run_test

    def _selective(counts, label, *a, **kw):
        if label == "1b:k256":
            raise ValueError("injected for a Task 4 totality test")
        return real(counts, label, *a, **kw)

    monkeypatch.setattr(an, "_run_test", _selective)
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert any("2k primary" in f for f in v["referents"]["failures"])
    assert v["primary"] is None and v["secondaries"] is None


def test_secondary_forced_exception_leaves_the_verdict_standing(world, monkeypatch):
    """Unlike the refusal tests above, a secondary's own failure does
    NOT flip the overall verdict — `_sec` catches it locally (`sec[name]
    = {"failed": f[0]}`) and the primary alone still decides DENSITY/
    NOT-DENSITY."""
    root, seal = world
    monkeypatch.setattr(an, "s1_blocks", _raise_injected)
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "DENSITY", v["reason"]
    assert v["secondaries"]["S1 block replication 1b"]["failed"]
    assert any("S1 block replication 1b" in f for f in v["secondaries"]["failures"])


def test_comparison_gate_x64_vs_2d_mismatch_detected(world, monkeypatch):
    # gate 1 GUARANTEES x_A^(64) equals 2d's own committed count on every
    # world this file builds (seed 0 is always the real committed row),
    # so this loop never has anything to catch there — perturbing 2d's
    # SEPARATE cached count directly is the only way to exercise it.
    root, seal = world
    real = bi.sampler_counts_pythia

    def wrong(size, rungs):
        out = dict(real(size, rungs))
        r = next(iter(out))
        out[r] = [v + 1 for v in out[r]]
        return out

    monkeypatch.setattr(bi, "sampler_counts_pythia", wrong)
    v = _run(root, seal)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert any("comparison gate 2k counts" in f for f in v["referents"]["failures"])


def test_comparison_gate_per_rung_d_mismatch_detected(world):
    # corrupts ONE rung's on-disk per-rung d WITHOUT touching stratified.T,
    # so the earlier "comparison gate 2k A64" T check passes and only the
    # per-rung loop can catch it.
    root, seal = world
    vpath = root / "results" / "verdict.json"
    v2i = json.loads(vpath.read_text())
    r = next(iter(v2i["tests"]["A"]["per_rung"]))
    v2i["tests"]["A"]["per_rung"][r]["d"] = (v2i["tests"]["A"]["per_rung"][r]["d"] or 0.0) + 100.0
    vpath.write_text(json.dumps(v2i))
    v = _run(root, seal)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert any("comparison gate 2k A per-rung" in f for f in v["referents"]["failures"])


def test_comparison_gate_forced_exception(world, tmp_path):
    # _cmp's first read is v2i (verdict_2i_path); pointing it at a
    # nonexistent file raises before any bad-entry logic runs, isolating
    # whether _cmp AS A WHOLE is collect_total-wrapped.
    root, seal = world
    v = _run(root, seal, verdict_2i_path=tmp_path / "nonexistent_verdict.json")
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert any("2k comparison gate re-derivation" in f for f in v["referents"]["failures"])


# ------------------------------------------------------------- control

def test_untouched_world_still_reaches_density(world):
    """n_perm=30's permutation p-value floor can never clear ALPHA
    regardless of T; only the control needs resolution enough to
    actually fire (2i's/2j's own totality control tests, same reason)."""
    root, seal = world
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "DENSITY", v["reason"]
    assert v["primary"]["fires"] is True
