# experiments/exp2c/tests/test_m3_stage1.py
"""Tests for M3 Stage 1 assembly.

Produces the canonical predictor record that `analyze.py` consumes at
M5. Two hard behaviours carried from the standing two-stage-lock
decision: the assembler REFUSES to run before a clean M2 report, and
REFUSES to overwrite an existing output. Both are load-bearing — the
Stage 1 record is the thing the tag commits to, and a silent rerun
after the tag would break the commitment it encodes.

untrained_fires source ruled 2026-08-11 (Michael): the campaign
known_absent fits, classified through the same `stats_bounds.classify_fire`
path gate 2 uses — same population and depth as the m3 fits they control.
"""

import json

import pytest

from experiments.exp2c.analyze import AnalyzeInputs, verdict
from experiments.exp2c.battery import family_map
from experiments.exp2c.run import m3_stage1 as m3
from experiments.exp2c.run import power_conditional as pc


# ------------------------------------------------------------- refusals

def test_refuses_to_run_without_an_m2_report(tmp_path):
    with pytest.raises(RuntimeError, match="M2 report"):
        m3.assemble(report_path=tmp_path / "nope.json",
                    out_path=tmp_path / "probe_scores.json")


def test_refuses_to_run_on_an_aborted_m2_report(tmp_path):
    rp = tmp_path / "m2_report.json"
    rp.write_text(json.dumps({"gate2": {"fires": [], "n_fits": 0},
                              "gate3": {}, "abort": True}))
    with pytest.raises(RuntimeError, match="abort"):
        m3.assemble(report_path=rp, out_path=tmp_path / "probe_scores.json")


def test_refuses_to_overwrite_an_existing_record(tmp_path):
    out = tmp_path / "probe_scores.json"
    out.write_text("{}")
    with pytest.raises(RuntimeError, match="overwrite"):
        m3.assemble(out_path=out)


# ------------------------------------------------------------ the record

def test_record_covers_exactly_the_scored_battery():
    rec = m3.assemble(write=False)
    fmap = family_map.scored_battery_families()
    assert {r["name"] for r in rec["rungs"]} == set(fmap)
    assert len(rec["rungs"]) == 34
    for r in rec["rungs"]:
        assert r["family"] == fmap[r["name"]]
        assert isinstance(r["scored"], bool)
        assert "probe_score" in r
        assert "ascent_score" not in r  # filled at M4/M5, not now


def test_probe_scores_match_the_independent_implementation():
    """Design Sec 3: seed-mean margin, then mean over the two probe
    sizes. `power_conditional.realized_probe_scores` implements the same
    definition from the same records by a different code path; the two
    must agree to the last bit or one of them is wrong."""
    rec = m3.assemble(write=False)
    rungs, _ = pc.battery_layout()
    independent = dict(zip(rungs, pc.realized_probe_scores()))
    for r in rec["rungs"]:
        assert r["probe_score"] == pytest.approx(independent[r["name"]],
                                                 abs=1e-12)


def test_rungs_are_laid_out_in_family_blocks():
    """analyze.py groups into contiguous per-family blocks by first
    appearance; the record must already be in that order so the block
    test's layout convention holds."""
    rec = m3.assemble(write=False)
    seen, order = set(), []
    for r in rec["rungs"]:
        if r["family"] not in seen:
            seen.add(r["family"])
            order.append(r["family"])
    blocks = [r["family"] for r in rec["rungs"]]
    expected = [f for f in order
                for _ in range(sum(b == f for b in blocks))]
    assert blocks == expected


# --------------------------------------------------------- untrained_fires

def test_untrained_fires_come_from_the_campaign_known_absent_fits():
    """Michael's ruling 2026-08-11. Every scored rung gets an entry, and
    the classifications are drawn from the known_absent fit records."""
    rec = m3.assemble(write=False)
    fmap = family_map.scored_battery_families()
    assert set(rec["untrained_fires"]) == set(fmap)
    allowed = {"not_fire", "tolerated", "elevated", "structural_abort"}
    for name, fires in rec["untrained_fires"].items():
        assert fires, f"{name} has no untrained fits"
        assert set(fires) <= allowed


def test_untrained_fires_exclude_rungs_outside_the_scored_battery():
    """hamming8 was ejected at M1 but its known_absent fits stay
    committed as honest record; they must not re-enter here (gate-1
    arithmetic is 220, not 230)."""
    rec = m3.assemble(write=False)
    assert "hamming8" not in rec["untrained_fires"]
    assert "hamming8" not in {r["name"] for r in rec["rungs"]}


def test_each_new_pool_rung_has_ten_untrained_fits():
    """5 seeds x 2 probe sizes per rung."""
    rec = m3.assemble(write=False)
    new_pool = set(family_map.scored_battery_families()) - set(
        json.loads((m3.RESULTS / "reuse_manifest.json").read_text())
        ["survivors"])
    for name in new_pool:
        assert len(rec["untrained_fires"][name]) == 10, name


# ------------------------------------------------------- shuffled_fires

def test_shuffled_fires_are_reshaped_for_analyze():
    """m2_report stores fires as positional records; analyze.py reads
    f["classification"]."""
    rec = m3.assemble(write=False)
    report = json.loads((m3.RESULTS / "m2_report.json").read_text())
    assert len(rec["shuffled_fires"]) == len(report["gate2"]["fires"])
    for f in rec["shuffled_fires"]:
        assert "classification" in f


# ---------------------------------------------------------- integration

def test_record_drives_analyze_end_to_end():
    """The point of the artifact: it must load into AnalyzeInputs and
    run the frozen verdict tree. Ascent scores are stubbed here — the
    real ones do not exist until M4."""
    rec = m3.assemble(write=False)
    rungs = [dict(r, ascent_score=float(i))
             for i, r in enumerate(rec["rungs"])]
    inp = AnalyzeInputs(rungs=rungs,
                        untrained_fires=rec["untrained_fires"],
                        shuffled_fires=rec["shuffled_fires"])
    out = verdict(inp)
    assert out["verdict"] in {"PASS", "FAIL", "INDETERMINATE",
                              "INSUFFICIENT_DATA", "PIPELINE_ABORT"}


def test_no_rung_is_lost_to_residual_attrition():
    """With the ruled source, attrition must not silently shrink the
    battery below the dual floor. If this fails the verdict is
    INSUFFICIENT_DATA and that needs a ruling, not a surprise at M5."""
    rec = m3.assemble(write=False)
    dropped = [n for n, fires in rec["untrained_fires"].items()
               if any(c in ("elevated", "structural_abort") for c in fires)]
    assert dropped == [], f"residual gate-1 attrition would drop {dropped}"


# ------------------------------------------- layer-0 reservoir channel
#
# Characterization tests, not red-green: they pin a property of the
# committed records that was discovered during assembly (2026-08-11).
# A layer-0 fit reads the embedding, which is effectively injective over
# the tokens in play while n_train < d, so its validation accuracy is
# fixed by the items and the split alone — identical across model SIZES
# and across TRAINED/UNTRAINED weights. That is the Exp 2 reservoir
# channel. It is harmless here only because nothing that fires uses it,
# which is what these guard.

def _m3_fits():
    import glob, os, re
    out = {}
    for stage in ("m3", "known_absent"):
        for f in glob.glob(str(m3.RESULTS / "probes" / stage / "*.json")):
            mm = re.match(r"(410m|1b)_(.+)_seed(\d)$", os.path.basename(f)[:-5])
            out[(stage, mm.group(2), int(mm.group(3)), mm.group(1))] = \
                json.loads(open(f).read())
    return out


def test_no_firing_fit_reads_the_layer_0_channel():
    """The load-bearing one. If a PRESENT fit ever sat at layer 0 its
    margin would be weight-independent — a leak, not a measurement, and
    the predictor would be partly reading the item set."""
    fits = _m3_fits()
    bad = [k for k, v in fits.items()
           if k[0] == "m3" and v["present"] and v["best_layer"] == 0]
    assert bad == [], f"present m3 fits at layer 0: {bad}"


def test_layer_0_fits_are_weight_independent():
    """Documents why cross-size identical accuracies in the committed
    records are expected rather than a collection bug."""
    fits = _m3_fits()
    pairs = [(fits[("m3", c, s, z)], fits[("known_absent", c, s, z)])
             for (stage, c, s, z) in fits if stage == "m3"
             and ("known_absent", c, s, z) in fits]
    both0 = [(a, b) for a, b in pairs
             if a["best_layer"] == 0 and b["best_layer"] == 0]
    assert both0, "no layer-0 pairs found — the characterization is stale"
    for a, b in both0:
        assert a["accuracy"] == b["accuracy"]


def test_record_carries_its_provenance():
    rec = m3.assemble(write=False)
    assert rec["untrained_fires_source"] == "campaign_known_absent"
    assert rec["n_rungs"] == 34
    assert rec["n_families"] == 16
    assert rec["m2_report_clean"] is True
