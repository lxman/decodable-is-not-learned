"""rederive_2d: gate 1 on the production path, against committed bytes."""
import json

import pytest

from experiments.exp2d import analyze_2d as a
from experiments.exp2d import rederive_2d as rd
from experiments.exp2d.tests import full_shape as fs


@pytest.fixture(scope="module")
def env():
    battery, _ = fs.battery()
    return {"battery": battery, "verify": a.load_verify()}


def _rows(rung, size):
    return [{"item": r["item"], "draws": {"0": list(r["draws"]["0"])}}
            for r in fs.committed_rows(rung, size)]


def _answers(env, rung):
    return [str(it["answer"]) for it in env["battery"][rung]["eval_items"]]


def test_committed_rows_compare_identical_with_expected_fires(env):
    for rung in a.REVERSAL_RUNGS:
        for size in a.PROBE_SIZES:
            cmp = rd.compare_rows(rung, size, _rows(rung, size),
                                  answers=_answers(env, rung),
                                  answer_type="word", verify_fn=env["verify"])
            assert cmp["diffs"] == []
            assert cmp["draws_compared"] == 32_000
            assert cmp["fires"] == list(a.GATE1_EXPECTED_FIRES[(rung, size)])
            assert cmp["committed_gz_sha"] == a.COMMITTED_DRAWS_SHA256[rung][size]


def test_single_altered_draw_is_a_diff_with_address(env):
    rows = _rows("reverse_string", "410m")
    rows[17]["draws"]["0"][40] = rows[17]["draws"]["0"][40] + " "
    cmp = rd.compare_rows("reverse_string", "410m", rows,
                          answers=_answers(env, "reverse_string"),
                          answer_type="word", verify_fn=env["verify"])
    assert len(cmp["diffs"]) == 1
    assert (cmp["diffs"][0]["item"], cmp["diffs"][0]["draw"]) == (17, 40)
    assert "got" in cmp["diffs"][0] and "committed" in cmp["diffs"][0]


def test_coverage_is_pinned_around_the_comparator(env):
    rows = _rows("rev_string7", "1b")
    with pytest.raises(ValueError, match="coverage"):
        rd.compare_rows("rev_string7", "1b", rows[:499],
                        answers=_answers(env, "rev_string7"),
                        answer_type="word", verify_fn=env["verify"])
    rows[3]["draws"]["0"] = rows[3]["draws"]["0"][:63]
    with pytest.raises(ValueError, match="draws_per_seed"):
        rd.compare_rows("rev_string7", "1b", rows,
                        answers=_answers(env, "rev_string7"),
                        answer_type="word", verify_fn=env["verify"])


def test_committed_shard_must_hash_to_literal(env):
    bad = {r: dict(v) for r, v in a.COMMITTED_DRAWS_SHA256.items()}
    bad["reverse_string"]["1b"] = "00" * 32
    with pytest.raises(ValueError, match="literal"):
        rd.compare_rows("reverse_string", "1b", _rows("reverse_string", "1b"),
                        answers=_answers(env, "reverse_string"),
                        answer_type="word", verify_fn=env["verify"],
                        committed_shas=bad)


def test_answers_must_be_the_batterys(env):
    ans = _answers(env, "reverse_string")
    ans[0] = "nope"
    with pytest.raises(ValueError, match="answers"):
        rd.compare_rows("reverse_string", "1b", _rows("reverse_string", "1b"),
                        answers=ans, answer_type="word",
                        verify_fn=env["verify"])


def test_record_and_halt_writes_then_raises(tmp_path, env):
    rows = _rows("reverse_string", "1b")
    rec = rd.record_and_halt_on_diff(
        "reverse_string", "1b", rows, answers=_answers(env, "reverse_string"),
        answer_type="word", verify_fn=env["verify"], items_sha="x" * 64,
        model_sha="m", stack={}, out_root=tmp_path)
    assert rec["n_diffs"] == 0 and rec["on_production_path"] is True
    assert rec["fires_reproduced"] == [{"item": 436, "seed": 0, "draw": 6}]
    p = a.gate1_record_path(tmp_path, "1b", "reverse_string")
    assert p.exists()
    p.unlink()
    rows[0]["draws"]["0"][0] += "!"
    with pytest.raises(RuntimeError, match="GATE 1 FIRED"):
        rd.record_and_halt_on_diff(
            "reverse_string", "1b", rows,
            answers=_answers(env, "reverse_string"), answer_type="word",
            verify_fn=env["verify"], items_sha="x" * 64, model_sha="m",
            stack={}, out_root=tmp_path)
    assert json.loads(p.read_text())["n_diffs"] == 1   # written before raise
