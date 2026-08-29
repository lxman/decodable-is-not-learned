# experiments/exp2k/tests/test_battery_2k.py
"""battery_2k: paths, the 4-seed reader's refusals, bits/counts at k on a
hand-built row set, the tier-record literal round-trips through its own
checker, seed freshness against the committed stream maps, the
256-scaled matched k on the design's rates."""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2i import battery_2i as bi
from experiments.exp2k import battery_2k as bk


def _write_gz(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def _rows(n_items=4, seeds=bk.SEEDS_2K, dps=bk.DRAWS_PER_SEED, answer=" 7"):
    rows = []
    for i in range(n_items):
        draws = {}
        for s in seeds:
            # item i verifies on exactly i draws of seed s (so the count at
            # k = 64·m is i·m), the rest are " zzz"
            draws[str(s)] = [answer] * i + [" zzz"] * (dps - i)
        rows.append({"item": i, "draws": draws})
    return rows


def _cap(n_items=4):
    return {"answer_type": "number", "items_sha256": "X" * 64,
            "eval_items": [{"question": f"q{i}", "answer": "7"} for i in range(n_items)]}


def _verify(d, ans, at):
    return d.strip() == str(ans)


def test_constants_are_the_design_dials():
    assert bk.SIZES_2K == ("1b", "410m") and bk.SEEDS_2K == (0, 1, 2, 3)
    assert bk.DRAWS_PER_SEED == 64 and bk.K_TOTAL == 256
    assert bk.LADDER_K == (64, 128, 192, 256) and bk.GATE1_SEED == 0
    assert bk.R_CAP_DESIGN == ("add3_mid", "add_base8", "antonym", "antonym6", "arith_next",
                               "odd6", "sub3_mid", "sub4_mid", "sub_base8")
    assert bk.PREREG_TAG_2K == "exp2k-preregistered"
    assert bk.SEAL_TAG_2K == "exp2k-predictor-sealed"
    assert set(bk.INSTRUMENT_BLOBS_2K) == {"experiments/exp2k/analyze_2k.py",
                                           "experiments/exp2k/battery_2k.py",
                                           "experiments/exp2k/run/tier_2k.py"}
    assert bk.TIER == "k256" and bk.MODE == a2d.MODE == "trained"


def test_paths(tmp_path):
    assert bk.tier_record_path(tmp_path, "1b", "antonym") == \
        tmp_path / "results" / "k256" / "1b_trained" / "antonym.json"
    assert bk.tier_draws_path(tmp_path, "1b", "antonym").name == "antonym.draws.jsonl.gz"
    assert bk.halt_marker_path(tmp_path, "410m", "odd6").name == "odd6.HALTED"
    assert bk.halted_draws_path(tmp_path, "410m", "odd6").name == "odd6.HALTED.jsonl.gz"
    assert bk.seal_path(tmp_path) == tmp_path / "results" / "predictor_2k.json"
    assert bk.power_path(tmp_path) == tmp_path / "results" / "power_2k.json"
    assert bk.committed_draws_path("1b", "antonym") == \
        a2d.tier_draws_path(a2d.EXP2D, "main", "1b", "antonym")
    assert bk.halt_markers(tmp_path) == []
    m = bk.halt_marker_path(tmp_path, "1b", "antonym")
    m.parent.mkdir(parents=True)
    m.write_text("{}")
    assert bk.halt_markers(tmp_path) == [m]


def test_halt_markers_sees_the_evidence_gz_without_its_marker(tmp_path):
    """Freeze F-1: `run_rung` writes `<rung>.HALTED.jsonl.gz` BEFORE
    `<rung>.HALTED`, so a kill (or a failed marker write) in that window
    leaves the evidence file alone. Either artifact is halt evidence."""
    gz = bk.halted_draws_path(tmp_path, "410m", "odd6")
    gz.parent.mkdir(parents=True)
    gz.write_bytes(b"")
    assert bk.halt_markers(tmp_path) == [gz]
    m = bk.halt_marker_path(tmp_path, "410m", "odd6")
    m.write_text("{}")
    assert bk.halt_markers(tmp_path) == [m, gz]      # marker sorts first


def test_read_rows_2k_accepts_the_4_seed_shape_and_sorts(tmp_path):
    p = tmp_path / "x.draws.jsonl.gz"
    rows = _rows()
    _write_gz(p, list(reversed(rows)))
    got = bk.read_rows_2k(p, n_items=4)
    assert [r["item"] for r in got] == [0, 1, 2, 3]
    assert set(got[0]["draws"]) == {"0", "1", "2", "3"}


@pytest.mark.parametrize("mutate,needle", [
    (lambda rows: rows[0]["draws"].pop("3"), "seed streams"),
    (lambda rows: rows[0]["draws"].__setitem__("9", rows[0]["draws"]["0"]), "seed streams"),
    (lambda rows: rows[1]["draws"]["2"].pop(), "draws against draws_per_seed"),
    (lambda rows: rows[1]["draws"]["2"].__setitem__(0, 5), "draws against draws_per_seed"),
    (lambda rows: rows[1]["draws"]["2"].append(" zzz"), "draws against draws_per_seed"),
    (lambda rows: rows.pop(), "coverage incomplete"),
    (lambda rows: rows.append(dict(rows[0])), "bad or duplicate item"),
])
def test_read_rows_2k_refusals(tmp_path, mutate, needle):
    rows = _rows()
    mutate(rows)
    p = tmp_path / "x.draws.jsonl.gz"
    _write_gz(p, rows)
    with pytest.raises(ValueError, match=needle):
        bk.read_rows_2k(p, n_items=4)


def test_bits_and_counts_at_k():
    rows, cap = _rows(), _cap()
    bits = bk.bits_2k(rows, cap, _verify)
    assert len(bits) == 4 and all(len(b) == 256 for b in bits)
    assert bk.counts_at_k(bits, 64) == [0, 1, 2, 3]
    assert bk.counts_at_k(bits, 128) == [0, 2, 4, 6]
    assert bk.counts_at_k(bits, 256) == [0, 4, 8, 12]
    assert bk.block_counts(bits, 3) == [0, 1, 2, 3]
    assert set(bk.counts_by_k(bits)) == set(bk.LADDER_K)
    assert bk.counts_by_k(bits)[192] == [0, 3, 6, 9]
    t = bk.tallies_2k(rows, cap, _verify)
    assert t == {s: {"full_string": 6, "n_draws": 256} for s in ("0", "1", "2", "3")}
    assert bk.mean_rate([0, 4, 8, 12], 256) == pytest.approx(24 / (4 * 256))
    with pytest.raises(ValueError, match="k"):
        bk.counts_at_k(bits, 65)


def test_bits_2k_refuses_incomplete_coverage():
    rows, cap = _rows(), _cap()
    with pytest.raises(ValueError, match="coverage"):
        bk.bits_2k(rows[:3], cap, _verify)


def test_bits_2k_preserves_seed_order():
    # seed 0 all-correct, seeds 1-3 all-wrong: a seed-order bug would move
    # the correct block out of the first 64 bits counts_at_k(64) reads.
    cap = _cap(n_items=1)
    row = {"item": 0, "draws": {"0": [" 7"] * 64, "1": [" x"] * 64,
                                "2": [" x"] * 64, "3": [" x"] * 64}}
    bits = bk.bits_2k([row], cap, _verify)
    assert bk.counts_at_k(bits, 64) == [64]
    assert bk.counts_at_k(bits, 256) == [64]
    assert bits[0][:64] == [1] * 64 and bits[0][64:] == [0] * 192


def test_committed_by_item_and_diff_seed0():
    rows = _rows()
    committed = [{"item": r["item"], "draws": {"0": list(r["draws"]["0"])}} for r in rows]
    assert bk.diff_seed0(rows, committed) == []
    committed[2]["draws"]["0"][5] = " changed"
    d = bk.diff_seed0(rows, committed)
    assert len(d) == 1 and d[0]["item"] == 2 and d[0]["draw"] == 5 and d[0]["seed"] == 0
    by = bk.committed_by_item(committed)
    assert by[3] == committed[3]["draws"]["0"]


def _rec(cap, rows, size="1b", rung="antonym", **over):
    rec = bk.tier_record_2k(rung=rung, size=size, cap=cap, rows=rows, verify_fn=_verify,
                            model_sha=bk.pythia_sha(size), stack={"torch": "t", "transformers": "x"},
                            git_sha="g", seconds=1.0, committed_gz_sha="C" * 64,
                            committed_record_sha="R" * 64,
                            gate1_items_compared=len(rows),
                            gate1_draws_compared=len(rows) * bk.DRAWS_PER_SEED)
    rec.update(over)
    return rec


def test_tier_record_round_trips_through_its_checker():
    cap = bt.load_item_file("antonym")
    n = bt.N_ITEMS
    rows = [{"item": i, "draws": {str(s): [" zzz"] * 64 for s in bk.SEEDS_2K}} for i in range(n)]
    rec = _rec(cap, rows)
    assert bk.tier_record_failures_2k(rec, size="1b", rung="antonym", cap=cap) == []
    assert rec["seeds"] == [0, 1, 2, 3] and rec["k_total"] == 256 and rec["draws_per_seed"] == 64
    assert rec["gate1"] == {"seed": 0, "on_production_path": True, "items_compared": n,
                            "draws_compared": n * 64, "n_diffs": 0,
                            "committed_draws_sha256": "C" * 64, "committed_record_sha256": "R" * 64}
    assert rec["per_seed_tallies"]["3"]["n_draws"] == n * 64
    assert rec["max_new_tokens"] == bt.max_new_tokens("antonym")
    assert rec["items_sha256"] == cap["items_sha256"]
    assert rec["stream_namespace"] == a2d.STREAM_NAMESPACE and rec["dtype"] == a2d.SAMPLING_DTYPE


@pytest.mark.parametrize("over,needle", [
    ({"seeds": [0, 1, 2]}, "seeds"),
    ({"draws_per_seed": 8}, "draws_per_seed"),
    ({"k_total": 64}, "k_total"),
    ({"model_sha": "nope"}, "model_sha"),
    ({"items_sha256": "nope"}, "items_sha256"),
    ({"answer_type": "number"}, "answer_type"),
    ({"max_new_tokens": 99}, "max_new_tokens"),
    ({"temperature": 0.7}, "temperature"),
    ({"truncation": "top_p"}, "truncation"),
    ({"dtype": "float16"}, "dtype"),
    ({"stream_namespace": "exp2k"}, "stream_namespace"),
    ({"tier": "main"}, "tier"),
    ({"size": "410m"}, "size"),
    ({"mode": "untrained"}, "mode"),
    ({"n_items": 499}, "n_items"),
    ({"gate1": {"seed": 0, "on_production_path": True, "items_compared": 499,
                "draws_compared": 500 * 64, "n_diffs": 0, "committed_draws_sha256": "C" * 64,
                "committed_record_sha256": "R" * 64}}, "items_compared"),
    ({"gate1": {"seed": 0, "on_production_path": True, "items_compared": 501,
                "draws_compared": 500 * 64, "n_diffs": 0, "committed_draws_sha256": "C" * 64,
                "committed_record_sha256": "R" * 64}}, "items_compared"),
    ({"gate1": {"seed": 0, "on_production_path": True, "items_compared": 500,
                "draws_compared": 500 * 64, "n_diffs": 1, "committed_draws_sha256": "C" * 64,
                "committed_record_sha256": "R" * 64}}, "n_diffs"),
    ({"gate1": {"seed": 0, "on_production_path": True, "items_compared": 500,
                "draws_compared": 500 * 64, "n_diffs": 0,
                "committed_draws_sha256": "wrong", "committed_record_sha256": "R" * 64}},
     "committed_draws_sha256"),
    ({"per_seed_tallies": {"0": {"full_string": 0, "n_draws": 32000}}}, "per_seed_tallies"),
    ({"answers": ["x"] * 500}, "answer column"),
])
def test_tier_record_failures(over, needle):
    cap = bt.load_item_file("antonym")
    rows = [{"item": i, "draws": {str(s): [" zzz"] * 64 for s in bk.SEEDS_2K}}
            for i in range(bt.N_ITEMS)]
    rec = _rec(cap, rows, **over)
    bad = bk.tier_record_failures_2k(rec, size="1b", rung="antonym", cap=cap)
    assert bad and any(needle in b for b in bad), bad


def test_tier_record_checker_pins_the_committed_gz_sha_to_2i_when_asked():
    """The committed sha the record attests must be 2i's literal for the
    cell (`battery_2i.PYTHIA_PREDICTOR_FILES`) when `committed_sha` is
    supplied — the analyzer supplies it; the runner writes what it
    hashed."""
    cap = bt.load_item_file("antonym")
    rows = [{"item": i, "draws": {str(s): [" zzz"] * 64 for s in bk.SEEDS_2K}}
            for i in range(bt.N_ITEMS)]
    rec = _rec(cap, rows)
    want = bi.PYTHIA_PREDICTOR_FILES[("1b", "antonym")]
    bad = bk.tier_record_failures_2k(rec, size="1b", rung="antonym", cap=cap,
                                     committed_sha=want)
    assert any("committed_draws_sha256" in b for b in bad)
    rec["gate1"]["committed_draws_sha256"] = want
    assert bk.tier_record_failures_2k(rec, size="1b", rung="antonym", cap=cap,
                                      committed_sha=want) == []


def test_pythia_sha_is_2b_pin():
    from models import PYTHIA_SHAS
    assert bk.pythia_sha("1b") == PYTHIA_SHAS["1b"] == "f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2"
    assert bk.pythia_sha("410m") == PYTHIA_SHAS["410m"]
    with pytest.raises(ValueError):
        bk.pythia_sha("2.8b")


def test_stream_collisions_on_the_committed_maps():
    # seed 0 on every R_CAP cell IS 2d's main tier (by design); 1000 the pilot
    hits0 = bk.stream_collisions("antonym", "1b", (0,))
    assert any("stream_map_2d" in h for h in hits0)
    hits1000 = bk.stream_collisions("antonym", "1b", (1000,))
    assert any("stream_map_2d" in h for h in hits1000)
    # seeds 1–3 are fresh on every R_CAP cell at both sizes
    for rung in bk.R_CAP_DESIGN:
        for size in bk.SIZES_2K:
            assert bk.stream_collisions(rung, size, (1, 2, 3)) == [], (rung, size)
    # and NOT fresh where exp3 drew them (the reversal rungs)
    assert any("stream_map.json" in h for h in bk.stream_collisions("reverse_string", "1b", (1,)))
    fr = bk.check_seed_freshness(bk.R_CAP_DESIGN)
    assert fr["new_seeds"] == [1, 2, 3] and fr["cells"] == 18


def test_check_seed_freshness_refuses_a_reversal_rung():
    with pytest.raises(ValueError, match="collide"):
        bk.check_seed_freshness(("reverse_string",))


def test_check_seed_freshness_refuses_when_seed_0_is_not_2ds_main_tier(monkeypatch):
    # seeds 1-3 collide with nothing (clean), but seed 0 ALSO collides
    # with nothing — isolates the seed-0-must-be-2d's-main-tier assertion
    # from the seeds-1-3-must-be-fresh assertion.
    monkeypatch.setattr(bk, "stream_collisions", lambda rung, size, seeds, mode=bk.MODE: [])
    with pytest.raises(ValueError, match="is not 2d's main tier"):
        bk.check_seed_freshness(("antonym",), sizes=("1b",))


def test_committed_rows_are_2d_main_seed0():
    rows = bk.committed_rows("1b", "antonym")
    assert len(rows) == bt.N_ITEMS and set(rows[0]["draws"]) == {"0"}
    assert len(rows[0]["draws"]["0"]) == 64


def test_matched_k_256_on_the_design_rates():
    # design §2's table from 2j's committed rates (verdict.json a1 per_rung)
    a1 = json.loads((bg.REPO / "experiments/exp2j/results/verdict.json").read_text())
    per = a1["a1"]["outcomes"]["olmo7b"]["per_rung"]
    for rung, want in bk.MATCHED_K_DESIGN.items():
        got = bk.matched_k_256(per[rung]["rate_A"], per[rung]["rate_B"])
        assert got["k"] == want, (rung, got)
        assert got["capped"] == (want == 64)
        assert got["n_blocks"] == 64 // want
    assert bk.matched_k_256(0.0, 0.1) == {"k": 1, "capped": False, "n_blocks": 64}
    assert bk.matched_k_256(0.5, 0.1) == {"k": 64, "capped": True, "n_blocks": 1}
    assert bk.matched_k_256(0.1, 0.0) == {"k": 64, "capped": True, "n_blocks": 1}


def test_frozen_files_cover_2j_and_the_sampler_side():
    names = {str(p) for p in bk.FROZEN_FILES_2K}
    for rel in ("exp2j/analyze_2j.py", "exp2j/functionals_2j.py", "exp3d/rederive_3d.py",
                "exp3/run/run_cell.py", "exp2i/run/sample_2i.py", "exp2b/models.py",
                "exp2i/analyze_2i.py", "exp3/sampler.py", "exp2d/analyze_2d.py"):
        assert any(n.endswith(rel) for n in names), rel
    for rel in bk.INSTRUMENT_BLOBS_2K:
        assert not any(n.endswith(rel.split("exp2k/")[1]) for n in names), rel


def test_check_frozen_2k_refuses_unpinned_and_drift(monkeypatch):
    monkeypatch.setattr(bk, "FROZEN_SHA256_2K", {})
    with pytest.raises(RuntimeError, match="not pinned"):
        bk.check_frozen_2k()
    d = bk.frozen_from_disk(strict=False)
    monkeypatch.setattr(bk, "FROZEN_SHA256_2K", d)
    bk.check_frozen_2k()
    k = next(iter(d))
    d[k] = "0" * 64
    with pytest.raises(RuntimeError, match="drifted"):
        bk.check_frozen_2k()


def test_frozen_from_disk_strict_raises_on_a_missing_path():
    if all(p.is_file() for p in bk.FROZEN_FILES_2K):
        pytest.skip("every FROZEN_FILES_2K member is on disk (post-Task-5 state)")
    with pytest.raises(FileNotFoundError):
        bk.frozen_from_disk()


def test_require_prereg_2k_refuses_missing_tag_and_drift():
    with pytest.raises(RuntimeError, match="does not exist"):
        bk.require_prereg_2k(tag_exists=lambda t: False)
    ok = bk.require_prereg_2k(tag_exists=lambda t: True,
                              blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel))
    assert set(ok["instrument_blobs"]) == set(bk.INSTRUMENT_BLOBS_2K)
    with pytest.raises(RuntimeError, match="does not bind"):
        bk.require_prereg_2k(tag_exists=lambda t: True, blob_sha=lambda tag, rel: "x")
