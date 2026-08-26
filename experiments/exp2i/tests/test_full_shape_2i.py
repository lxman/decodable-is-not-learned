# experiments/exp2i/tests/test_full_shape_2i.py
"""Every 2i terminal, end to end on synthetic 7B sweeps (real x_A,
synthetic x_B and outcome) through the production loaders and the
prereg/seal-tag paths."""
import pytest

from experiments.exp2i import analyze_2i as an
from experiments.exp2i import battery_2i as bi
from experiments.exp2i.tests import full_shape as fs


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    out = {}
    for name, kw, want in fs.world_specs():
        root = tmp_path_factory.mktemp(name.split()[0])
        seal = fs.write_world(root, **kw)
        out[name] = (fs.run_world(root, seal), want)
    return out


def test_every_terminal_reached(worlds):
    got = {}
    for name, (v, want) in worlds.items():
        assert v["verdict"] == want, f"{name}: {v['verdict']} ({v['reason']})"
        got.setdefault(v["verdict"], name)
    assert set(got) == set(an.WORLDS)


def test_w1_shared_shape(worlds):
    v, _ = worlds["W1 SHARED"]
    A, B = v["tests"]["A"], v["tests"]["B"]
    assert A["fires"] is True
    assert B["fires"] is False
    assert "twin" not in A and "twin" not in B
    assert A["stratified"]["T"] >= 0.10 and A["stratified"]["p"] < 0.01
    assert v["secondaries"]["within_alone"]
    assert v["secondaries"]["cross_beyond_within"]
    assert v["secondaries"]["replication_410m_cross"]
    assert v["secondaries"]["first_correct_A"]
    assert v["secondaries"]["first_correct_B"]
    assert v["secondaries"]["reverse_direction"]
    # both reverse-direction descriptives were already-known outcomes
    # (design §2) before x_B was sealed — the stamp is load-bearing,
    # not decorative: it is what tells a reader this leg is not a
    # forecast.
    rd = v["secondaries"]["reverse_direction"]
    assert rd["vs_2.8b"]["known_outcome"] is True
    assert rd["vs_6.9b"]["known_outcome"] is True
    assert v["secondaries"]["extra_rungs_raw"] == {}   # R_EXTRA is empty in every world
    assert v["secondaries"]["rung_level"]["table"]
    assert v["secondaries"]["flat_rungs"]
    assert v["secondaries"]["twin_counts"]
    assert all(c == 0 for c in v["secondaries"]["twin_counts"].values())
    assert v["secondaries"]["main_vs_endpoint"]
    assert v["referents"]["gate1"]
    assert v["referents"]["power"]["A"]["declared_status"] == "POWERED"
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2I
    assert v["calibration_note"] == an.CALIBRATION_SENTENCE_2I
    assert v["licensed_sentence"] == an.LICENSED["SHARED"]


def test_w2_lineage_shape(worlds):
    v, _ = worlds["W2 LINEAGE"]
    A, B = v["tests"]["A"], v["tests"]["B"]
    assert A["fires"] is False
    assert B["fires"] is True
    assert v["licensed_sentence"] == an.LICENSED["LINEAGE"]


def test_w3_both_shape(worlds):
    v, _ = worlds["W3 BOTH"]
    A, B = v["tests"]["A"], v["tests"]["B"]
    assert A["fires"] is True and B["fires"] is True
    assert v["licensed_sentence"] == an.LICENSED["BOTH"]


def test_w4_neither_independent(worlds):
    v, _ = worlds["W4 NEITHER independent"]
    assert v["licensed_sentence"] == an.LICENSED["NEITHER"]


def test_w5_inverted_named_on_both(worlds):
    v, _ = worlds["W5 NEITHER inverted"]
    A, B = v["tests"]["A"], v["tests"]["B"]
    assert A["fires"] is False and B["fires"] is False
    assert A["named_inside"] and "inverted" in A["named_inside"]
    assert B["named_inside"] and "inverted" in B["named_inside"]
    assert "A " in v["reason"] and "inverted" in v["reason"]
    assert "B " in v["reason"]


def test_w6_w7_w8_w9_reasons(worlds):
    assert any("endpoint" in f.lower() for f in
              worlds["W6 INSUFFICIENT missing endpoint"][0]["referents"]["failures"])
    assert any("does not bind" in f for f in
              worlds["W7 INSUFFICIENT drifted seal"][0]["referents"]["failures"])
    assert any("halted" in f for f in
              worlds["W8 INSUFFICIENT halted"][0]["referents"]["failures"])
    # C-1: W9 flips real stage1_final bytes while gate1.json's attested
    # diffs stay zero — the OLD attested-only `gate1_failures_7b` would
    # have missed this; only `gate1_rederive_7b`'s re-derivation names it.
    w9 = worlds["W9 INSUFFICIENT gate-1 diff (real bytes, attestation blind)"][0]
    assert any("re-derive" in f and "bit diff" in f for f in w9["referents"]["failures"])
    assert not any("gate 1 olmo7b/add4_mid:" in f for f in w9["referents"]["failures"]), \
        "the OLD attested-only check must NOT fire on this world (attestation lies clean)"
    # the mirror: bytes identical, attestation lies — the re-derivation's
    # OWN agreement check ((b) in the docstring) catches it even though
    # the byte comparison itself finds nothing.
    w9b = worlds["W9b INSUFFICIENT gate-1 attested mismatch (bytes identical)"][0]
    assert any("disagrees with the re-derived" in f for f in w9b["referents"]["failures"])


def test_w10_degenerate_b_reaches_shared_with_disclosure(worlds):
    """I-4/Ruling 18: every R_CAP rung constant in x_B is no longer a
    referent failure — Test B is undefined, not a crash, and Test A
    (mode='a_only') still fires, so the world reaches SHARED carrying
    the verbatim disclosure in both `reason` and `licensed_sentence`."""
    v, want = worlds["W10 SHARED via degenerate x_B (Test B undefined)"]
    assert want == "SHARED"
    assert v["verdict"] == "SHARED", v["reason"]
    A, B = v["tests"]["A"], v["tests"]["B"]
    assert A["fires"] is True
    assert B["fires"] is False
    assert B["named_inside"] and B["named_inside"].startswith("undefined")
    assert sorted(B["dropped_degenerate"]) == sorted(bi.STRATA_RUNGS)
    assert an.DISCLOSURE_UNDEFINED_2I["B"] in v["reason"]
    assert an.DISCLOSURE_UNDEFINED_2I["B"] in v["licensed_sentence"]
    assert an.DISCLOSURE_UNDEFINED_2I["A"] not in v["reason"]   # A fired, not undefined


def test_undefined_test_a_reaches_lineage_with_the_disclosure(tmp_path, monkeypatch):
    """FREEZE battery item 11 / Ruling 18, the OTHER direction. The
    published symmetry is only exercised on Test B by `world_specs()`
    (x_B is synthetic and can be made constant; x_A is the REAL
    committed 2d table and is never synthesized), so the A branch gets
    its own world here: `sampler_counts_pythia` — the production reader
    `run()` calls for x_A — is substituted by a constant table, i.e.
    'what if Pythia-1b emitted every item equally often'. Test A is
    then degenerate on every R_CAP rung and undefined; Test B (mode
    'b_only') still fires; the world is LINEAGE and carries A's
    verbatim disclosure in BOTH `reason` and `licensed_sentence`.

    Measured at the freeze and recorded in FREEZE_CHECKLIST.md: on the
    real committed x_A no rung of the eleven is degenerate at either
    size (2-8 live strata per rung at 1b, 2-6 at 410m), so this branch
    is unreachable on the real data — Ruling 18 bites on Test B alone."""
    from experiments.exp2d import battery_2d as bt
    root = tmp_path / "w"
    root.mkdir()
    seal = fs.write_world(root, mode="b_only")
    monkeypatch.setattr(bi, "sampler_counts_pythia",
                        lambda size, rungs: {r: [7] * bt.N_ITEMS for r in rungs})
    v = fs.run_world(root, seal)
    assert v["verdict"] == "LINEAGE", v["reason"]
    A, B = v["tests"]["A"], v["tests"]["B"]
    assert A["fires"] is False and B["fires"] is True
    assert A["named_inside"].startswith("undefined")
    assert A["stratified"]["T"] is None            # R-2: None, never NaN
    assert sorted(A["dropped_degenerate"]) == sorted(bi.STRATA_RUNGS)
    assert an.DISCLOSURE_UNDEFINED_2I["A"] in v["reason"]
    assert an.DISCLOSURE_UNDEFINED_2I["A"] in v["licensed_sentence"]
    assert an.DISCLOSURE_UNDEFINED_2I["B"] not in v["reason"]
    assert "T=undefined" in v["reason"]


def test_insufficient_worlds_carry_no_tests_or_secondaries(worlds):
    for name in ("W6 INSUFFICIENT missing endpoint", "W7 INSUFFICIENT drifted seal",
                "W8 INSUFFICIENT halted",
                "W9 INSUFFICIENT gate-1 diff (real bytes, attestation blind)",
                "W9b INSUFFICIENT gate-1 attested mismatch (bytes identical)"):
        v, _ = worlds[name]
        assert v["tests"] is None and v["secondaries"] is None
        assert v["licensed_sentence"] == an.LICENSED["INSUFFICIENT_DATA"]
