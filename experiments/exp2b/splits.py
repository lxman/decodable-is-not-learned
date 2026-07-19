"""Basis-starved split construction (design doc §2 fields 3+5, §3).

The battery's central mechanism: each item carries a BASIS — a tuple of surface
components a lookup strategy would key on (operand tokens, word first-tokens,
(letter, shift) combos). A starving split holds out a set of values per
component; validation items are those whose components are ALL held out, train
items those whose components are ALL kept, and mixed items are DISCARDED from
the fit. A lookup table keyed on any component therefore scores chance on
validation by construction; an additive per-component score is starved the same
way (every component value in validation is unseen).

Per-seed variation (process rule 5): the 5 probe seeds re-draw WHICH values are
held out. Class coverage is enforced by seeded rejection: every probe class
must appear in both train and validation, else redraw (bounded).

Feasibility (design §2 field 5, checked at generation AND at fit time):
  >= MIN_HOLDOUT_VALUES held-out values per component (spec may override where
  the design table names an exact count), >= MIN_VAL_ITEMS validation items,
  every class on both sides — for EVERY seed. A capability that cannot satisfy
  this for all 5 seeds is ejected at M0 and reported.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

MIN_HOLDOUT_VALUES = 15   # design §2 field 5 default
MIN_VAL_ITEMS = 300       # design §2 field 5 default
MAX_REDRAWS = 200


@dataclass
class SplitParams:
    """Per-capability split parameters. Defaults follow design §2 field 5; a
    spec overrides n_holdout/min_holdout_values only where the design table
    names an exact count (e.g. cipher's per-class combo holdout).

    shared_components: when the components draw from ONE value space (gcd's two
    operands, sort3's three numbers), a per-position holdout leaks — a value
    held out at position 0 but kept at position 1 is still learnable. Shared
    mode draws a single holdout set from the union and applies it to every
    position."""
    holdout_frac: float = 0.2
    n_holdout: int | None = None          # exact held-out value count per component
    min_holdout_values: int = MIN_HOLDOUT_VALUES
    min_val_items: int = MIN_VAL_ITEMS
    shared_components: bool = False
    # Hold out a proportional share of values WITHIN each label group (k=1 only;
    # requires each basis value to induce exactly one label). For targets whose
    # label is a function of the basis value with rare classes (unscramble/caesar
    # first letters), uniform value holdout starves rare classes off one side —
    # exp2's letter-stratification lesson, applied to the split.
    stratify_by_label: bool = False


class SplitInfeasible(Exception):
    pass


def _component_values(bases: list[tuple], k: int) -> list[list[str]]:
    return [sorted({b[i] for b in bases}) for i in range(k)]


def starving_split(bases: list[tuple], labels, seed: int,
                   params: SplitParams) -> tuple[np.ndarray, np.ndarray, dict]:
    """Return (train_idx, val_idx, info) for one seed.

    bases: per-item basis tuples (all the same arity k).
    val = items with ALL components held out; train = ALL kept; mixed dropped.
    Raises SplitInfeasible if constraints cannot be met in MAX_REDRAWS draws.
    """
    labels = np.asarray(labels)
    k = len(bases[0])
    if any(len(b) != k for b in bases):
        raise ValueError("inconsistent basis arity")
    values = _component_values(bases, k)
    classes = set(labels.tolist())
    rng = np.random.default_rng(seed)

    union = sorted({v for comp in values for v in comp})

    label_of: dict = {}
    if params.stratify_by_label:
        if k != 1:
            raise ValueError("stratify_by_label requires single-component bases")
        for b, lbl in zip(bases, labels):
            prev = label_of.setdefault(b[0], lbl)
            if prev != lbl:
                raise ValueError(f"basis value {b[0]!r} induces two labels; "
                                 f"stratification undefined")

    for attempt in range(MAX_REDRAWS):
        held: list[set] = []
        if params.stratify_by_label:
            frac = (params.n_holdout / len(values[0])
                    if params.n_holdout is not None else params.holdout_frac)
            groups: dict = {}
            for v in values[0]:
                groups.setdefault(label_of[v], []).append(v)
            h = set()
            for lbl, vals in sorted(groups.items()):
                if len(vals) < 2:
                    raise SplitInfeasible(
                        f"label {lbl!r} has only {len(vals)} basis value(s); "
                        f"cannot keep the class on both sides")
                n = min(len(vals) - 1, max(1, int(round(frac * len(vals)))))
                h |= set(rng.permutation(vals)[:n].tolist())
            held = [h]
        elif params.shared_components:
            n = params.n_holdout if params.n_holdout is not None else max(
                1, int(np.ceil(params.holdout_frac * len(union))))
            if n >= len(union):
                raise SplitInfeasible(
                    f"shared holdout {n} >= union cardinality {len(union)}")
            shared = set(rng.permutation(union)[:n].tolist())
            held = [shared] * k
        else:
            for comp_vals in values:
                n = params.n_holdout if params.n_holdout is not None else max(
                    1, int(np.ceil(params.holdout_frac * len(comp_vals))))
                if n >= len(comp_vals):
                    raise SplitInfeasible(
                        f"holdout {n} >= component cardinality {len(comp_vals)}")
                held.append(set(rng.permutation(comp_vals)[:n].tolist()))

        is_val = np.array([all(b[i] in held[i] for i in range(k)) for b in bases])
        is_train = np.array([all(b[i] not in held[i] for i in range(k)) for b in bases])
        val_idx, train_idx = np.where(is_val)[0], np.where(is_train)[0]

        n_held = min(len(h) for h in held)
        ok = (n_held >= params.min_holdout_values
              and len(val_idx) >= params.min_val_items
              and set(labels[val_idx].tolist()) == classes
              and set(labels[train_idx].tolist()) == classes)
        if ok:
            info = {"seed": seed, "attempt": attempt, "k": k,
                    "held_per_component": [len(h) for h in held],
                    "n_train": int(len(train_idx)), "n_val": int(len(val_idx)),
                    "n_dropped": int(len(bases) - len(train_idx) - len(val_idx))}
            return train_idx, val_idx, info

    raise SplitInfeasible(
        f"no valid split in {MAX_REDRAWS} draws (seed {seed}): "
        f"components {[len(v) for v in values]}, classes {len(classes)}, "
        f"need >= {params.min_holdout_values} held values and "
        f">= {params.min_val_items} val items with full class coverage")


def feasibility_report(bases: list[tuple], labels, params: SplitParams,
                       seeds=(0, 1, 2, 3, 4)) -> dict:
    """Design §2 field 5: the committed feasibility record for one capability."""
    per_seed = {}
    for s in seeds:
        _, _, info = starving_split(bases, labels, s, params)  # raises if infeasible
        per_seed[str(s)] = info
    k = len(bases[0])
    values = _component_values(bases, k)
    return {"component_cardinalities": [len(v) for v in values],
            "params": {"holdout_frac": params.holdout_frac,
                       "n_holdout": params.n_holdout,
                       "min_holdout_values": params.min_holdout_values,
                       "min_val_items": params.min_val_items},
            "per_seed": per_seed}
