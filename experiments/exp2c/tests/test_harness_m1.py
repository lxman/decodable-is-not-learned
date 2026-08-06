# experiments/exp2c/tests/test_harness_m1.py
"""M1 harness + ctrl_copy control pins (gate 4 machinery). The scoring
functions must match 2b's byte-for-byte — that identity is what makes
the reused survivors' 2b record comparable (design §7) — so the first
test pins them against exp2b's own module."""

import inspect

import numpy as np

from experiments.exp2c.battery import generators_controls
from experiments.exp2c.battery.base import SPECS
from experiments.exp2c.battery.family_map import scored_battery_families
from experiments.exp2c import harness


def test_scoring_functions_match_2b_behaviorally():
    import experiments.exp2b.battery.base as b2b
    shots = [("Q1?", "a1"), ("Q2?", "a2")]
    assert harness.render_prompt("Q3?", shots) == b2b.render_prompt("Q3?", shots)
    assert harness.render_prompt("Q?", None) == b2b.render_prompt("Q?", None)
    cases = [(" 1,234 apples\nQ:", "number"), ("BB4", "number"),
             ("-17.", "number"), ("  Word! extra\nmore", "word"),
             ("'quoted'", "word"), ("", "word"), ("A90", "number"),
             ("x y z\n", "letters"), ("  YES.  ", "choice")]
    for text, at in cases:
        assert harness.normalize_answer(text, at) == \
            b2b.normalize_answer(text, at), (text, at)
        assert harness.verify(text, text, at) == b2b.verify(text, text, at)


def test_ctrl_copy_registered_as_unscored_control():
    spec = SPECS["ctrl_copy"]
    assert spec.scored is False
    assert spec.answer_type == "word"
    assert spec.seed == 20260827
    # oracle = first letter (probe label); surface answer = the string
    assert spec.oracle("abcd") == "a"
    assert spec.surface_answer("abcd") == "abcd"


def test_ctrl_copy_never_enters_scored_battery():
    # no tier-1 verdict exists for ctrl_copy, and scored=False: the
    # 35-rung battery shape must be unaffected by its registration
    fams = scored_battery_families()
    assert "ctrl_copy" not in fams
    assert len(fams) == 35


def test_ctrl_copy_gen_matches_2b_semantics():
    rng = np.random.default_rng(0)
    for _ in range(50):
        s = generators_controls._gen_ctrl_copy(rng)
        assert 4 <= len(s) <= 6 and s.islower() and s.isalpha()


class FakeRunner:
    """Echoes each prompt's quoted string — a perfect copier."""

    def __init__(self):
        self.calls = []

    def generate(self, prompts, max_new_tokens):
        import re
        self.calls.append((len(prompts), max_new_tokens))
        return [" " + re.findall(r"'([a-z]+)'", p)[-1] + "\nQ:" for p in prompts]


def test_evaluate_argmax_scores_perfect_copier_at_one():
    cap = {"name": "ctrl_copy", "answer_type": "word",
           "shots": [["Repeat the string 'abcd' exactly.", "abcd"],
                     ["Repeat the string 'zyxw' exactly.", "zyxw"]],
           "eval_items": [
               {"question": f"Repeat the string '{s}' exactly.", "answer": s}
               for s in ("gorm", "welt", "prax")]}
    r = harness.evaluate_argmax(FakeRunner(), cap)
    assert r["correct"] == 3 and r["acc"] == 1.0
    assert r["cp95"][0] > 0.29                        # CP lower bound, n=3
    assert r["n_shots"] == 2


def test_evaluate_to_file_skips_existing(tmp_path):
    p = tmp_path / "410m_trained" / "ctrl_copy.json"
    p.parent.mkdir(parents=True)
    p.write_text('{"acc": 0.5, "sentinel": true}')
    called = []
    out = harness.evaluate_to_file(
        lambda: called.append(1), {"name": "x"}, p, {})
    assert out["sentinel"] is True and not called    # no model load on hit
