"""Tranche-1 battery tests: split machinery invariants, oracle agreement on
generated items, basis independence (text-recomputable), and the starving
guarantee itself — a pure lookup table must score chance on every starved
validation set."""

import numpy as np
import pytest

from splits import SplitInfeasible, SplitParams, starving_split
from battery.base import generate_items, normalize_answer, render_prompt
from battery.generators import SPECS

# expected M0 ejections (unique-question spaces below full counts, by design)
EJECT_NAMES = ("month_offset", "letter_half", "alpha_offset",
               "plural_irreg", "past_irreg")
# tokenizer-basis specs need the HF cache — exercised in their own test
TOK_NAMES = ("reverse_string", "acronym")
GENERATING = [s for s in SPECS if s.name not in EJECT_NAMES + TOK_NAMES]
EJECTING = [s for s in SPECS if s.name in EJECT_NAMES]


def _quick(spec, n_eval=40, n_probe=400):
    """Generate a reduced item set for fast tests (real counts run at M0).
    Shared-component specs keep more items: their val share is frac^k and their
    rare classes need the larger n to cover both split sides."""
    import battery.base as bb
    if spec.split_params.shared_components:
        n_probe = 1500
    old_eval, old_np = bb.N_EVAL, spec.n_probe
    bb.N_EVAL, spec.n_probe = n_eval, n_probe
    # relax split minima proportionally for the reduced n; dataclasses.replace
    # carries every other field (a manual rebuild silently dropped one once)
    from dataclasses import replace
    old_sp = spec.split_params
    spec.split_params = replace(
        old_sp, min_holdout_values=min(old_sp.min_holdout_values, 5),
        min_val_items=20)
    try:
        return generate_items(spec, seed=99)
    finally:
        bb.N_EVAL, spec.n_probe, spec.split_params = old_eval, old_np, old_sp


@pytest.mark.parametrize("spec", GENERATING, ids=lambda s: s.name)
def test_generate_oracle_and_basis(spec):
    payload = _quick(spec)
    items = payload["eval_items"] + payload["probe_items"]
    expected = 40 + (1500 if spec.split_params.shared_components else 400)
    assert len(items) == expected
    for it in items[:80]:
        ora = spec.oracle(it["question"])
        assert normalize_answer(ora, spec.answer_type) == \
            normalize_answer(it["answer"], spec.answer_type)
        if spec.basis_fn:
            assert tuple(it["basis"]) == tuple(str(v) for v in spec.basis_fn(it["question"]))
    if spec.scored:
        assert "feasibility" in payload
        assert len(payload["feasibility"]["per_seed"]) == 5


@pytest.mark.parametrize("spec", EJECTING, ids=lambda s: s.name)
def test_small_space_specs_eject(spec):
    """Small unique-question spaces (36 month combos, 26 letters, 130 offsets,
    40/60 irregular cues) cannot meet the uniqueness rule at full counts — the
    M0 ejection path, by design."""
    with pytest.raises(RuntimeError):
        generate_items(spec, seed=99)


def test_starving_split_invariants():
    rng = np.random.default_rng(0)
    bases = [(str(int(rng.integers(30))),) for _ in range(1000)]
    labels = [str(int(b[0]) % 5) for b in bases]
    tr, va, info = starving_split(bases, labels, seed=1,
                                  params=SplitParams(holdout_frac=0.2,
                                                     min_holdout_values=5,
                                                     min_val_items=50))
    held = {bases[i][0] for i in va}
    kept = {bases[i][0] for i in tr}
    assert not (held & kept)                      # value-disjoint by construction
    assert set(np.array(labels)[va]) == set(labels)   # class coverage both sides
    assert set(np.array(labels)[tr]) == set(labels)
    assert len(tr) + len(va) == 1000              # k=1: nothing dropped


def test_shared_components_no_positional_leak():
    rng = np.random.default_rng(0)
    vals = [str(v) for v in range(40)]
    bases = [tuple(rng.choice(vals, size=2, replace=False)) for _ in range(3000)]
    labels = [str((int(a) + int(b)) % 4) for a, b in bases]
    tr, va, info = starving_split(bases, labels, seed=2,
                                  params=SplitParams(holdout_frac=0.4,
                                                     min_holdout_values=5,
                                                     min_val_items=50,
                                                     shared_components=True))
    train_vals = {v for i in tr for v in bases[i]}
    val_vals = {v for i in va for v in bases[i]}
    assert not (train_vals & val_vals)            # NO value appears on both sides
    assert info["n_dropped"] > 0                  # mixed items are discarded


def test_lookup_table_scores_chance_on_starved_val():
    """The design's core claim, executed: a per-value lookup fit on train
    CANNOT beat chance on starved validation (it has never seen those values)."""
    rng = np.random.default_rng(3)
    bases = [(str(int(rng.integers(60))),) for _ in range(2000)]
    labels = np.array([str(int(rng.integers(6))) for _ in range(2000)], dtype=object)
    # make labels a FUNCTION of the basis value (the lookup-friendliest world)
    table = {str(v): str(v % 6) for v in range(60)}
    labels = np.array([table[b[0]] for b in bases], dtype=object)
    tr, va, _ = starving_split(bases, labels, seed=4,
                               params=SplitParams(holdout_frac=0.2,
                                                  min_holdout_values=5,
                                                  min_val_items=100))
    lookup = {}
    for i in tr:
        lookup[bases[i][0]] = labels[i]
    preds = [lookup.get(bases[i][0], "MISS") for i in va]
    acc = float(np.mean([p == labels[i] for p, i in zip(preds, va)]))
    assert acc == 0.0                             # every val value is unseen


def test_infeasible_raises():
    bases = [(str(i % 3),) for i in range(100)]   # only 3 basis values
    labels = [str(i % 2) for i in range(100)]
    with pytest.raises(SplitInfeasible):
        starving_split(bases, labels, seed=0,
                       params=SplitParams(min_holdout_values=15, min_val_items=50))


def test_reverse_string_final_chunk_basis_against_real_tokenizer():
    """The tokenizer-keyed basis (design table #16): the recorded chunk must be
    a suffix of the string as the model sees it, and shared across strings."""
    from battery.generators import _final_chunk
    c1 = _final_chunk("stone")
    c2 = _final_chunk("bone")
    assert "stone".endswith(c1.strip("'"))
    assert isinstance(c2, str) and len(c2) >= 1


def test_acronym_first_token_basis_against_real_tokenizer():
    """#15's basis: the 2nd word's FIRST BPE token (leading space, mid-prompt
    form) — must be a prefix of the word and start with its first letter."""
    from battery.generators_t2 import _first_chunk_with_space
    t = _first_chunk_with_space("stone")
    assert t.strip().startswith("s") and "stone".startswith(t.strip())


def test_render_prompt_matches_exp2_convention():
    p = render_prompt("What is 1 + 1?", [("Q1", "A1"), ("Q2", "A2")])
    assert p.endswith("Q: What is 1 + 1?\nA:")
    assert p.count("Q:") == 3


def test_seed_derivation_is_positional():
    """Ejections must not shift other capabilities' item streams: seeds derive
    from position in the FULL spec list (gen_items convention)."""
    from battery.gen_items import BASE_SEED
    from battery.generators import SPECS as full
    names = [s.name for s in full]
    assert names.index("mod7_add") == 0 and BASE_SEED == 20260718
