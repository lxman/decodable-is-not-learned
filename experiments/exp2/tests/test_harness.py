"""Harness tests: the full argmax-evaluation loop driven by fake runners, so the
mechanics are known-good before any model is queried (M2's known-answer gates
then certify the same loop WITH the real models)."""

import json

import pytest

from battery.base import load_items, render_prompt
from harness import (MAX_NEW_TOKENS, clopper_pearson, evaluate_argmax,
                     evaluate_to_file, normalized_margin)

CAP = load_items("add2")


def question_of(prompt: str) -> str:
    """Recover the final question from a rendered prompt (ends 'Q: <q>\\nA:')."""
    return prompt.rsplit("Q: ", 1)[1][: -len("\nA:")]


class OracleRunner:
    """Answers every question correctly — the pipeline's known-answer fake."""

    def __init__(self, cap):
        self.gold = {it["question"]: it["answer"] for it in cap["eval_items"]}
        self.seen_prompts = []

    def generate(self, prompts, max_new_tokens):
        self.seen_prompts.extend(prompts)
        return [" " + self.gold[question_of(p)] + "\nQ: junk" for p in prompts]


class GarbageRunner:
    def generate(self, prompts, max_new_tokens):
        return [" zzzz" for _ in prompts]


def test_clopper_pearson_edges_and_width():
    assert clopper_pearson(0, 500)[0] == 0.0
    assert clopper_pearson(500, 500)[1] == 1.0
    lo, hi = clopper_pearson(0, 500)
    assert hi < 0.01  # a zero over 500 items is a bound, not a claimed zero
    lo2, hi2 = clopper_pearson(250, 500)
    assert lo2 < 0.5 < hi2 and (hi2 - lo2) < 0.1


def test_oracle_runner_scores_perfect():
    r = evaluate_argmax(OracleRunner(CAP), CAP)
    assert r["correct"] == r["n"] == len(CAP["eval_items"])
    assert r["acc"] == 1.0 and r["cp95"][1] == 1.0


def test_garbage_runner_scores_zero_with_cp_bound():
    r = evaluate_argmax(GarbageRunner(), CAP)
    assert r["correct"] == 0 and r["acc"] == 0.0
    assert 0.0 < r["cp95"][1] < 0.01


def test_prompts_carry_exactly_the_two_committed_shots():
    runner = OracleRunner(CAP)
    evaluate_argmax(runner, CAP, n_shots=2)
    p = runner.seen_prompts[0]
    for q, a in CAP["shots"]:
        assert f"Q: {q}\nA: {a}" in p
    assert p.endswith("\nA:") and p.count("Q: ") == 3  # 2 shots + the question


def test_zero_shot_variant_has_no_shots():
    runner = OracleRunner(CAP)
    evaluate_argmax(runner, CAP, n_shots=0)
    assert runner.seen_prompts[0].count("Q: ") == 1


def test_answer_types_all_have_generation_caps():
    from run.run_inclusion import all_capability_names
    for name in all_capability_names():
        assert load_items(name)["answer_type"] in MAX_NEW_TOKENS, name


def test_normalized_margin_maps_chance_to_zero():
    trained = {"acc": 0.55, "cp95": [0.51, 0.59]}
    chance = {"acc": 0.10, "cp95": [0.08, 0.13]}
    m = normalized_margin(trained, chance)
    assert m["margin"] == pytest.approx(0.5)
    assert m["margin_cp95"][0] == pytest.approx((0.51 - 0.1) / 0.9)
    zero = normalized_margin({"acc": 0.10, "cp95": [0.07, 0.13]}, chance)
    assert zero["margin"] == pytest.approx(0.0)


def test_evaluate_to_file_skips_existing_result(tmp_path):
    calls = []

    def factory():
        calls.append(1)
        return OracleRunner(CAP)

    path = tmp_path / "410m_trained" / "add2.json"
    r1 = evaluate_to_file(factory, CAP, path, {"size": "410m", "mode": "trained"})
    assert len(calls) == 1 and r1["acc"] == 1.0 and r1["size"] == "410m"
    r2 = evaluate_to_file(factory, CAP, path, {"size": "410m", "mode": "trained"})
    assert len(calls) == 1  # cache hit: factory never called, model never loaded
    assert r2 == json.loads(path.read_text()) == r1
