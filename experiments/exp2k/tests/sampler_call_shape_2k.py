# experiments/exp2k/tests/sampler_call_shape_2k.py
"""Design §3.2's fixture, written at the adversarial freeze: prove that
seed 0's bytes do NOT depend on which other seeds are in the same
`sample_item` call, so that gate 1 is a statement about the stream
formula and the weights and not about call shape.

Standalone by design. It is the only 2k module that imports `torch`, so
it carries no `test_` prefix and pytest never collects it — the
committed suite stays weight-free and torch-free (the build's standing
constraint). Run it by hand:

    PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python \
        -m experiments.exp2k.tests.sampler_call_shape_2k

ZERO MODEL CONTACT: the "model" is a fake whose forward is a pure,
deterministic function of the ids it is handed (a fixed logit table
rotated by the input id), and the "tokenizer" is a fake that maps ids
to `t<id>` strings. No weights are loaded, no network is touched. What
is real is exp3's frozen `sample_item` — its seed loop, its chunk plan,
its per-seed generator construction and its cache crop — which is the
only thing the claim is about.

The claim, made executable: for the production call shape
`seeds = (0, 1, 2, 3)` and the single-seed shape `seeds = (0,)` that 2d
used, the 64 seed-0 draws are byte-identical. The same is asserted for
every proper prefix and for a reordering that puts seed 0 last, so the
fixture would also catch a future change that batched seeds together or
shared one generator across them."""
from __future__ import annotations

import sys
from pathlib import Path

EXP2K = Path(__file__).resolve().parents[1]
if str(EXP2K.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2K.parent.parent))

import torch  # noqa: E402

from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp3.sampler import sample_item  # noqa: E402

VOCAB = 37
PROMPT_LEN = 5
TERMINAL = (VOCAB - 1,)


class _Enc(dict):
    def to(self, _device):
        return self


class _FakeTok:
    all_special_ids = list(TERMINAL)

    def __call__(self, prompt, return_tensors=None):
        ids = torch.arange(PROMPT_LEN, dtype=torch.long).unsqueeze(0)
        return _Enc(input_ids=ids, attention_mask=torch.ones_like(ids))

    def decode(self, ids, skip_special_tokens=False):
        return "".join(f"t{int(i)}" for i in ids)


class _FakeCache:
    """The two methods exp3's sampler calls on `past_key_values`."""

    def __init__(self):
        self.rows = 1
        self.length = PROMPT_LEN

    def batch_repeat_interleave(self, rows):
        self.rows = rows

    def crop(self, n):
        self.length = n


class _Out:
    def __init__(self, logits, past=None):
        self.logits = logits
        self.past_key_values = past


class _FakeModel:
    """A deterministic pure function of the ids it is handed: logit i of
    row r is `base[(i + id_r) % VOCAB]`, with `base` a fixed ramp. No
    state, no randomness, so any difference between two runs comes from
    the sampler's own generator handling — which is what is under test."""

    device = "cpu"

    def __init__(self):
        self.base = torch.linspace(-2.0, 2.0, VOCAB, dtype=torch.float32)
        self.past = _FakeCache()

    def _logits_for(self, ids):
        rows = [torch.roll(self.base, int(i)) for i in ids]
        return torch.stack(rows).unsqueeze(1)          # [rows, 1, V]

    def __call__(self, input_ids=None, past_key_values=None, attention_mask=None,
                 use_cache=False, logits_to_keep=None):
        if past_key_values is None:                    # the prompt forward
            return _Out(self._logits_for([int(input_ids[0, -1])]), self.past)
        return _Out(self._logits_for([int(x) for x in input_ids[:, -1]]))


def draws_for(seeds, *, rung="antonym", size="1b", item=0, max_new_tokens=8):
    tok, model = _FakeTok(), _FakeModel()
    return sample_item(model, tok, "prompt", rung=rung, size=size, mode=bk.MODE,
                       item_idx=item, seeds=tuple(seeds),
                       draws_per_seed=bk.DRAWS_PER_SEED,
                       max_new_tokens=max_new_tokens, terminal_ids=TERMINAL)


def main() -> int:
    production = draws_for(bk.SEEDS_2K)
    alone = draws_for((bk.GATE1_SEED,))
    shapes = {"seeds=(0,)": alone,
              "seeds=(0, 1)": draws_for((0, 1)),
              "seeds=(0, 1, 2)": draws_for((0, 1, 2)),
              "seeds=(3, 2, 1, 0)": draws_for((3, 2, 1, 0))}
    ref = production[bk.GATE1_SEED]
    assert len(ref) == bk.DRAWS_PER_SEED and len(set(ref)) > 1, "the fake is degenerate"
    bad = 0
    print(f"production call shape seeds={list(bk.SEEDS_2K)}: "
          f"{sum(len(v) for v in production.values())} draws, "
          f"{len(set(ref))} distinct seed-0 draws")
    for label, got in shapes.items():
        same = got[bk.GATE1_SEED] == ref
        n_diff = sum(1 for a, b in zip(got[bk.GATE1_SEED], ref) if a != b)
        print(f"  seed-0 block vs {label:<20} {'IDENTICAL' if same else f'{n_diff} DIFFS'}")
        bad += 0 if same else 1
    # and the new seeds are NOT copies of seed 0 (F-4's shape, on the fake)
    for s in bk.SEEDS_2K:
        if s != bk.GATE1_SEED and production[s] == ref:
            print(f"  seed {s} duplicates seed 0 — the sampler is not per-seed")
            bad += 1
    print("PASS: seed 0's bytes are independent of the seeds tuple" if not bad
          else f"FAIL: {bad} shape(s) disagree")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
