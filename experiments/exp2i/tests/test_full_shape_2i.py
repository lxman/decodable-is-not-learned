# experiments/exp2i/tests/test_full_shape_2i.py
"""Every 2i terminal, end to end on synthetic 7B sweeps (real x_A,
synthetic x_B and outcome) through the production loaders and the
prereg/seal-tag paths."""
import pytest

from experiments.exp2i import analyze_2i as an
from experiments.exp2i import battery_2i as bi
from experiments.exp2i.tests import full_shape as fs


@pytest.fixture(scope="module", autouse=True)
def _shrink_instrument_blobs_to_what_exists():
    """Task 4 landed `run/sweep_2i.py`, the fifth and final file in
    `INSTRUMENT_BLOBS_2I` — this is a no-op now (the subset equals the
    full five-file set). Left in place: it keeps these tests
    exercising the TREE (their reason for existing), not re-litigating
    the five-file instrument set — that is `test_analyze_2i.py`'s job.
    Plain monkeypatching (not the `monkeypatch` fixture, which is
    function-scoped) so a single module-scoped `worlds` fixture sees
    it consistently."""
    subset = tuple(r for r in an.INSTRUMENT_BLOBS_2I if (bi.REPO / r).is_file())
    original = an.INSTRUMENT_BLOBS_2I
    an.INSTRUMENT_BLOBS_2I = subset
    yield
    an.INSTRUMENT_BLOBS_2I = original


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
    assert v["secondaries"]["extra_rungs_raw"] == {}   # R_EXTRA is empty in every world
    assert v["secondaries"]["rung_level"]["table"]
    assert v["secondaries"]["flat_rungs"]
    assert v["secondaries"]["twin_counts"]
    assert all(c == 0 for c in v["secondaries"]["twin_counts"].values())
    assert v["secondaries"]["main_vs_endpoint"]
    assert v["referents"]["gate1"]
    assert v["referents"]["power"]["A"]["declared_status"] == "POWERED"
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2I
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


def test_w6_w7_w8_w9_w10_reasons(worlds):
    assert any("endpoint" in f.lower() for f in
              worlds["W6 INSUFFICIENT missing endpoint"][0]["referents"]["failures"])
    assert any("does not bind" in f for f in
              worlds["W7 INSUFFICIENT drifted seal"][0]["referents"]["failures"])
    assert any("halted" in f for f in
              worlds["W8 INSUFFICIENT halted"][0]["referents"]["failures"])
    assert any("bit diff" in f for f in
              worlds["W9 INSUFFICIENT gate-1 diff"][0]["referents"]["failures"])
    assert any("no eligible rung" in f for f in
              worlds["W10 INSUFFICIENT degenerate x_B"][0]["referents"]["failures"])


def test_insufficient_worlds_carry_no_tests_or_secondaries(worlds):
    for name in ("W6 INSUFFICIENT missing endpoint", "W7 INSUFFICIENT drifted seal",
                "W8 INSUFFICIENT halted", "W9 INSUFFICIENT gate-1 diff",
                "W10 INSUFFICIENT degenerate x_B"):
        v, _ = worlds[name]
        assert v["tests"] is None and v["secondaries"] is None
        assert v["licensed_sentence"] == an.LICENSED["INSUFFICIENT_DATA"]
