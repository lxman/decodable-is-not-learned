import numpy as np
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp2g import collect_eval_2g as ce


def _rec(**over):
    per = {r: {"n_compared": 8, "max_abs_diff": 0.0, "max_rel_diff": 0.0, "identical": True}
           for r in bg.PREDICTOR_RUNGS}
    gp = {r: {"n_compared": 500, "max_abs_diff": 0.001, "max_rel_diff": 0.002, "identical": False}
          for r in ce.GATE_P_RUNGS}
    rec = ce.continuity_record(size="1b", mode="trained", per_rung=per, gate_p=gp,
                               stack={"torch": "x", "transformers": "y"})
    rec.update(over)
    return rec


def test_pass_record():
    rec = _rec()
    assert rec["pass"] is True and ce.continuity_failures(rec, size="1b", mode="trained") == []


def test_failures_are_rederived_not_trusted():
    rec = _rec()
    rec["rungs"]["antonym"]["max_rel_diff"] = 0.5
    rec["pass"] = True
    assert any("antonym" in f for f in ce.continuity_failures(rec, size="1b", mode="trained"))
    rec = _rec()
    del rec["rungs"]["odd6"]
    assert any("odd6" in f for f in ce.continuity_failures(rec, size="1b", mode="trained"))
    rec = _rec(untrained_seed=7)
    assert ce.continuity_failures(rec, size="1b", mode="trained")
    rec = _rec(model_sha="0" * 40)
    assert ce.continuity_failures(rec, size="1b", mode="trained")
    rec = _rec()
    rec["gate_p"]["sub3_mid"]["max_abs_diff"] = 1.0
    assert any("gate P" in f for f in ce.continuity_failures(rec, size="1b", mode="trained"))
    rec = _rec()
    del rec["gate_p"]["arith_next"]
    assert any("gate P" in f for f in ce.continuity_failures(rec, size="1b", mode="trained"))
    assert ce.continuity_failures(_rec(), size="410m", mode="trained")   # wrong size


def test_eval_meta_pins():
    m = ce.eval_meta(size="1b", mode="untrained", rung="antonym", n_layers=17, stack={})
    assert m["collector"] == "exp2g" and m["untrained_seed"] == 0
    assert m["items_sha256"] == bg.ITEMS_SHA_PIN_OF("antonym")
    assert m["positions"] == ["question_end", "prompt_end"] and m["n_items"] == 500
