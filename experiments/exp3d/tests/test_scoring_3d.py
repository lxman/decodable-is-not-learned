"""Unit fixtures for the scoring arm (doc Open item 4): the frozen
span rule's refusal paths on synthetic tokenizers, the known-answer
gate's band arithmetic at its edges, and the teacher-forced chain's
arithmetic — exp(ℓ) must equal the product of the sampler-law step
probabilities, proven against a fake model with known logits."""
import math

import pytest
import torch

from experiments.exp3.sampler import step_probs
from experiments.exp3d import scoring_3d as sc


# ------------------------------------------------------- the span rule

class CharTok:
    def __call__(self, text, **kw):
        return {"input_ids": [ord(ch) for ch in text]}

    def decode(self, ids):
        return "".join(chr(i) for i in ids)


def test_answer_span_clean():
    span = sc.answer_span(CharTok(), "Q: x\nA:", "qvux")
    assert CharTok().decode(span) == " qvux"


def test_answer_span_refuses_prefix_violation():
    class MergeTok(CharTok):
        def __call__(self, text, **kw):
            ids, i = [], 0
            while i < len(text):
                if text[i:i + 2] == ": ":
                    ids.append(9999)
                    i += 2
                else:
                    ids.append(ord(text[i]))
                    i += 1
            return {"input_ids": ids}

    with pytest.raises(sc.SpanError, match="prefix violation"):
        sc.answer_span(MergeTok(), "A:", "qvux")


def test_answer_span_refuses_round_trip_violation():
    class LossyTok(CharTok):
        def decode(self, ids):
            return "".join(chr(i) for i in ids).upper()

    with pytest.raises(sc.SpanError, match="round-trip"):
        sc.answer_span(LossyTok(), "A:", "qvux")


def test_answer_span_refuses_empty_answer():
    with pytest.raises(sc.SpanError, match="empty answer"):
        sc.answer_span(CharTok(), "A:", "")


# -------------------------------------------------- the gate arithmetic

def test_ctrl_gate_band_edges():
    r = 12787 / 16000
    ok = sc.ctrl_gate([math.log(r)] * 500, "410m")
    assert ok["passed"] and ok["committed_rate"] == pytest.approx(r)
    low = sc.ctrl_gate([math.log(0.5 * r - 1e-6)] * 500, "410m")
    assert not low["passed"]
    at_lower = sc.ctrl_gate([math.log(0.5 * r + 1e-9)] * 500, "410m")
    assert at_lower["passed"]
    high = sc.ctrl_gate([math.log(r + 0.021)] * 500, "410m")
    assert not high["passed"]
    within_upper = sc.ctrl_gate([math.log(r + 0.019)] * 500, "410m")
    assert within_upper["passed"]


def test_ctrl_gate_none_counts_as_zero():
    r = 13460 / 16000
    # 260 items at the committed rate, 240 dead: p̂ = .52 r, safely
    # inside the band with dead items contributing exactly zero
    ell = [math.log(r)] * 260 + [None] * 240
    g = sc.ctrl_gate(ell, "1b")
    assert g["predicted_rate"] == pytest.approx(0.52 * r)
    assert g["passed"]


def test_in_band_is_inclusive_at_both_edges():
    assert sc.in_band(0.25, 0.25, 0.5)
    assert sc.in_band(0.5, 0.25, 0.5)
    assert sc.in_band(0.3, 0.25, 0.5)
    assert not sc.in_band(0.24999, 0.25, 0.5)
    assert not sc.in_band(0.50001, 0.25, 0.5)


# --------------------------------------- the chain against a fake model

class FakeEnc(dict):
    def to(self, device):
        return self


class FakeTok:
    """Vocabulary = characters 'a'..'h' as ids 0..7; prompts and
    answers restricted to that alphabet."""

    def __call__(self, text, return_tensors=None, **kw):
        ids = [ord(ch) - ord("a") for ch in text.replace(" ", "g")]
        if return_tensors == "pt":
            return FakeEnc(input_ids=torch.tensor([ids]))
        return {"input_ids": ids}

    def decode(self, ids):
        return "".join(" " if i == 6 else chr(ord("a") + i)
                       for i in ids)


class FakeOut:
    def __init__(self, logits, past):
        self.logits = logits
        self.past_key_values = past


class FakeModel:
    """Deterministic logits that depend on the number of steps taken —
    the chain arithmetic is checkable by hand."""
    device = "cpu"

    def __init__(self, dead_step=None):
        self.dead_step = dead_step
        self.steps = 0

    def _logits(self):
        base = torch.arange(8, dtype=torch.float32) * 0.3 \
            + self.steps * 0.1
        if self.dead_step is not None and self.steps == self.dead_step:
            base = torch.full((8,), -torch.inf)
            base[0] = 0.0    # all mass on id 0
        return base.view(1, 1, 8)

    def __call__(self, input_ids=None, past_key_values=None,
                 attention_mask=None, use_cache=False,
                 logits_to_keep=None, **kw):
        out = FakeOut(self._logits(), object())
        self.steps += 1
        return out


def test_score_items_chain_is_sampler_law_product():
    tok = FakeTok()
    model = FakeModel()
    # answer 'ab' → span decodes ' ab' → ids [6, 0, 1]
    res = sc.score_items(model, tok, ["ca"], ["ab"])
    ell = res["ell"][0]
    # replicate: step probs at steps 0,1,2 for ids 6,0,1
    ref = FakeModel()
    want = 0.0
    for tid in (6, 0, 1):
        p = float(step_probs(ref._logits()[0, -1])[tid])
        ref.steps += 1
        want += math.log(p)
    assert ell == pytest.approx(want, rel=1e-12)
    assert res["span_token_ids"][0] == [6, 0, 1]
    assert res["zero_probability_items"] == 0


def test_score_items_zero_probability_path():
    tok = FakeTok()
    model = FakeModel(dead_step=1)    # second forward kills ids != 0
    res = sc.score_items(model, tok, ["ca"], ["ab"])
    # span [6, 0, 1]: step0 fine; step1 gives p(0)=1 fine for id 0...
    # id at position 1 IS 0 → survives; step2: logits at step 2 normal.
    assert res["ell"][0] is not None
    model = FakeModel(dead_step=0)    # first step kills id 6
    res = sc.score_items(model, tok, ["ca"], ["ab"])
    assert res["ell"][0] is None
    assert res["zero_probability_items"] == 1
    assert res["per_token_logprobs"][0] == [None]
