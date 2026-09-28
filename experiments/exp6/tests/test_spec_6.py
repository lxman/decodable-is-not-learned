# experiments/exp6/tests/test_spec_6.py
import json

import pytest

from experiments.exp6.battery import spec as sp


def _spec(draw, **kw):
    base = dict(name="t", task="t", wei_class="E.2", rung_type="string",
                answer_type="word", description="d", seed=1, draw=draw)
    base.update(kw)
    return sp.RungSpec(**base)


def _counter_draw(rng, ctx, slot):
    n = int(rng.integers(10_000))
    return {"question": f"say w{n}", "answer": f"w{n}", "bb_key": f"k{n}",
            "meta": {"n": n}}


def test_validate_refuses_bad_specs():
    assert sp.validate_spec(_spec(_counter_draw)) == []
    assert sp.validate_spec(_spec(_counter_draw, n_options=2))      # two-way choice
    assert sp.validate_spec(_spec(_counter_draw, answer_type="choice"))
    assert sp.validate_spec(_spec(_counter_draw, wei_class="E.1"))
    assert sp.validate_spec(_spec(_counter_draw, rung_type="logic"))
    assert sp.validate_spec(_spec(_counter_draw, collision_kind="both"))
    assert sp.validate_spec(_spec(_counter_draw, description=""))


def test_register_refuses_duplicates(monkeypatch):
    monkeypatch.setattr(sp, "SPECS_6", {})
    sp.register(_spec(_counter_draw, name="a", seed=1))
    with pytest.raises(ValueError):
        sp.register(_spec(_counter_draw, name="a", seed=2))      # name
    with pytest.raises(ValueError):
        sp.register(_spec(_counter_draw, name="b", seed=1))      # seed


def test_with_options_refuses_commas_and_newlines():
    assert sp.with_options("q", ["a", "b"]) == "q\nOptions: a, b"
    with pytest.raises(ValueError):
        sp.with_options("q", ["a, b", "c"])
    with pytest.raises(ValueError):
        sp.with_options("q", ["a\nb", "c"])


def test_generate_is_deterministic_and_complete():
    a = sp.generate(_spec(_counter_draw), {}, collisions=frozenset())
    b = sp.generate(_spec(_counter_draw), {}, collisions=frozenset())
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert len(a["eval_items"]) == sp.N_EVAL and len(a["shots"]) == sp.N_SHOTS
    qs = [it["question"] for it in a["eval_items"]] + [s[0] for s in a["shots"]]
    assert len(set(qs)) == len(qs)
    assert a["shots"][0][1] != a["shots"][1][1]
    assert all(set(it) == {"question", "answer", "bb_sha256", "meta"}
               for it in a["eval_items"])


def test_collision_is_redrawn_not_kept():
    clean = sp.generate(_spec(_counter_draw), {}, collisions=frozenset())
    hit = clean["eval_items"][0]["bb_sha256"]
    got = sp.generate(_spec(_counter_draw), {}, collisions=frozenset({hit}))
    assert got["n_redrawn"]["collision"] >= 1
    assert hit not in {it["bb_sha256"] for it in got["eval_items"]}


def test_unique_answers_is_enforced():
    def draw(rng, ctx, slot):
        n = int(rng.integers(100_000))
        return {"question": f"q{n}", "answer": f"w{n % 700}", "bb_key": f"k{n}",
                "meta": {}}
    free = sp.generate(_spec(draw), {}, collisions=frozenset())
    assert len({it["answer"] for it in free["eval_items"]}) < sp.N_EVAL
    uniq = sp.generate(_spec(draw, unique_answers=True), {}, collisions=frozenset())
    assert len({it["answer"] for it in uniq["eval_items"]}) == sp.N_EVAL
    assert uniq["n_redrawn"]["repeated_answer"] > 0


def test_a_rung_that_cannot_fill_a_slot_raises(monkeypatch):
    monkeypatch.setattr(sp, "MAX_ATTEMPTS_PER_SLOT", 50)
    with pytest.raises(RuntimeError, match="not filled"):
        sp.generate(_spec(lambda rng, ctx, slot: None), {}, collisions=frozenset())


def _opt_item(question, answer, pos):
    return {"question": question, "answer": answer, "bb_key": "k",
            "meta": {"answer_pos": pos}}


def test_check_item_on_option_rungs():
    s = _spec(_counter_draw, n_options=3)
    sp.check_item(s, _opt_item("q\nOptions: owl, crow, hawk", "crow", 2))
    for bad in (_opt_item("q\nOptions: owl, crow, hawk", "crow", 1),    # position
                _opt_item("q\nOptions: owl, crow", "crow", 2),           # count
                _opt_item("q\nOptions: owl, owl, crow", "crow", 3),      # repeated
                _opt_item("q\nOptions: owl, hawk, wren", "crow", 1),     # absent
                _opt_item("q with no options", "crow", 1)):
        with pytest.raises(ValueError):
            sp.check_item(s, bad)


def test_check_item_on_free_form_rungs():
    s = _spec(_counter_draw)
    sp.check_item(s, {"question": "q", "answer": "gulf", "bb_key": "k", "meta": {}})
    for bad in ({"question": "q\nOptions: a, b, c", "answer": "a", "bb_key": "k",
                 "meta": {}},                                   # options on free-form
                {"question": " q", "answer": "a", "bb_key": "k", "meta": {}},
                {"question": "q", "answer": "blue jay", "bb_key": "k", "meta": {}},
                {"question": "q", "answer": "a", "meta": {}}):  # no bb_key
        with pytest.raises(ValueError):
            sp.check_item(s, bad)
