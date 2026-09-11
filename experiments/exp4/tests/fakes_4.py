# experiments/exp4/tests/fakes_4.py
"""Test-only fakes for exp4's model contact (Task 2 resolution 6).
Runs WITHOUT torch: a tiny numpy shim (`_ShimTensor`) stands in for a
torch.Tensor (`.to(...)`/`.cpu()` no-ops, `.numpy()` the array,
`.shape`, indexing) so `FakeModel(...)(input_ids=..., attention_mask=
..., output_hidden_states=True)` returns an object whose
`.hidden_states` is a tuple of `n_hidden` such tensors, shape
`[B, T, d]`, a DETERMINISTIC function of the seed and the token ids —
never of call order or of any randomness drawn at call time: layer L's
state is a fixed seeded embedding table indexed by the (mod-vocab)
token ids, scaled by (L + 1), plus a fixed seeded per-layer offset.

`fake_loaders(seed_by_key)` returns the `loaders` dict shape Task 3
defines (`"key"`, `"step"`, `"free_step"`, `"release"`); every info
dict carries a `tensor_digest` derived from the seed alone
(`sha256(f"fake:{seed}")`) so a test can pin two keys to the same seed
(equal digests) or different seeds (a deliberate mismatch)."""
from __future__ import annotations

import hashlib

import numpy as np


class _ShimTensor:
    """A minimal numpy-backed stand-in for a torch.Tensor."""

    def __init__(self, array):
        self._a = np.asarray(array)

    def to(self, *args, **kwargs):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self._a

    @property
    def shape(self):
        return self._a.shape

    @property
    def dtype(self):
        return self._a.dtype

    def __array__(self, dtype=None):
        return self._a if dtype is None else self._a.astype(dtype)

    def __getitem__(self, item):
        out = self._a[item]
        return _ShimTensor(out) if isinstance(out, np.ndarray) else out

    def __len__(self):
        return len(self._a)

    def __eq__(self, other):
        if isinstance(other, _ShimTensor):
            return np.array_equal(self._a, other._a)
        return NotImplemented

    def __repr__(self):
        return f"_ShimTensor{self._a.shape!r}"


class _ShimBatch(dict):
    """What `FakeTokenizer.__call__` returns when `return_tensors="pt"`:
    a dict (so `["input_ids"]` still works) that also answers `.to
    (device)` with itself, as a real BatchEncoding does."""

    def to(self, *args, **kwargs):
        return self


class FakeTokenizer:
    """Maps characters to ids via `ord(c)` (`vocab_by_char` is accepted
    for interface parity but unused — `ord` already covers any char);
    pads to the batch's longest sequence on `padding_side` with
    `pad_token_id`."""

    def __init__(self, vocab_by_char=None, padding_side: str = "right",
                 pad_token_id: int = 0):
        self.vocab_by_char = vocab_by_char
        self.padding_side = padding_side
        self.pad_token_id = int(pad_token_id)

    @staticmethod
    def _ids(text: str) -> list:
        return [ord(c) for c in text]

    def __call__(self, texts, return_tensors=None, padding=False,
                 add_special_tokens=False):
        single = isinstance(texts, str)
        rows = [self._ids(texts)] if single else [self._ids(t) for t in texts]
        width = max((len(r) for r in rows), default=0)
        input_ids, attn = [], []
        for r in rows:
            if padding:
                pad = [self.pad_token_id] * (width - len(r))
                if self.padding_side == "left":
                    ids, mask = pad + r, [0] * len(pad) + [1] * len(r)
                else:
                    ids, mask = r + pad, [1] * len(r) + [0] * len(pad)
            else:
                ids, mask = r, [1] * len(r)
            input_ids.append(ids)
            attn.append(mask)
        if return_tensors == "pt":
            return _ShimBatch(input_ids=_ShimTensor(np.array(input_ids, dtype=np.int64)),
                              attention_mask=_ShimTensor(np.array(attn, dtype=np.int64)))
        return {"input_ids": input_ids, "attention_mask": attn}


class _FakeConfig:
    def __init__(self, n_hidden: int):
        self.num_hidden_layers = int(n_hidden) - 1


class _FakeOutput:
    def __init__(self, hidden_states):
        self.hidden_states = hidden_states


class FakeModel:
    """`__call__` is a pure function of (seed, ids, layer) — a fixed
    seeded embedding table times (layer + 1) plus a fixed seeded
    per-layer offset. `config.num_hidden_layers = n_hidden - 1`."""

    def __init__(self, seed: int, n_hidden: int, d: int, vocab_size: int = 1024):
        self.seed = int(seed)
        self.n_hidden = int(n_hidden)
        self.d = int(d)
        self.vocab_size = int(vocab_size)
        self.config = _FakeConfig(n_hidden)
        rng = np.random.default_rng(self.seed)
        self._embed = rng.standard_normal((self.vocab_size, self.d)).astype(np.float32)
        self._offsets = rng.standard_normal((self.n_hidden, self.d)).astype(np.float32)

    def __call__(self, input_ids, attention_mask=None, output_hidden_states=True):
        ids = input_ids.numpy() if isinstance(input_ids, _ShimTensor) else np.asarray(input_ids)
        ids = np.mod(ids, self.vocab_size)
        base = self._embed[ids]  # [B, T, d]
        states = tuple(
            _ShimTensor((base * (layer + 1) + self._offsets[layer]).astype(np.float32))
            for layer in range(self.n_hidden))
        return _FakeOutput(states)

    def to(self, *args, **kwargs):
        return self

    def eval(self):
        return self


def fake_digest(seed: int) -> str:
    return hashlib.sha256(f"fake:{seed}".encode()).hexdigest()


def fake_loaders(seed_by_key: dict, *, n_hidden_by: dict, d: int = 8,
                 vocab_size: int = 1024) -> dict:
    """The `loaders` dict shape Task 3 defines. `seed_by_key` maps
    every key (str) AND every `(traj, step)` the caller will load to an
    int seed; `n_hidden_by` maps the same names to an n_hidden (pass
    `battery_4.N_HIDDEN_PIN_4` for the real pins, or a small stand-in
    dict for a fixture)."""

    def _load(name, seed):
        model = FakeModel(seed, n_hidden_by[name], d, vocab_size)
        tok = FakeTokenizer()
        info = {"tensor_digest": fake_digest(seed), "commit": f"fake-{seed}",
                "revision": "fake", "repo": f"fake/{name}", "kind": "fake",
                "config_source": f"fake/{name}@fake", "n_hidden": n_hidden_by[name],
                "loading_info": {"missing_keys": 0, "unexpected_keys": 0,
                                 "mismatched_keys": 0}}
        return model, tok, info

    def load_key(key, *, cache_root=None, device="mps"):
        return _load(key, seed_by_key[key])

    def load_step(traj, step, *, cache_root=None, device="mps"):
        return _load(traj, seed_by_key[(traj, step)])

    def free_step(traj, step, cache_root=None) -> None:
        return None

    def release(model) -> None:
        return None

    return {"key": load_key, "step": load_step, "free_step": free_step,
            "release": release}
