"""ctrl_copy positive control for 2c (design gate 4: argmax reliability
>= 0.9 at both probe sizes, measured on 2c's OWN items at M1 -- never
transferred from a prior battery).

Generator and oracle ported verbatim from exp2b battery/generators.py
(`_gen_ctrl_copy` / `_oracle_ctrl_copy`), adapted to 2c's gen(rng)
calling convention (no split argument; 2c's generate() draws eval and
probe from one stream). The spec fills 2c's mandatory fields honestly;
scored=False keeps it out of the ladder, and having no tier-1 verdict
keeps it out of family_map's scored battery by construction.

Seed 20260827 = the next unused value in the growth sequence
(20260817-20260826 are taken by the nine growth rungs and hamming8's
regeneration); choice ledgered with the M1 entry.
"""

from .base import CapabilitySpec, register

_LET = "abcdefghijklmnopqrstuvwxyz"


def _gen_ctrl_copy(rng):
    n = int(rng.integers(4, 7))
    return "".join(_LET[int(rng.integers(26))] for _ in range(n))


def _oracle_ctrl_copy(s):
    return s[0]                      # probe label: first letter (26)


def _surface_ctrl_copy(s):
    return s                         # the answer is the string itself


CTRL_COPY = register(CapabilitySpec(
    name="ctrl_copy",
    family="control",
    dial_name="string length",
    dial_value="4-6",
    description="POSITIVE CONTROL: exact copy of a quoted string "
                "(gate 4 argmax reliability; never scored)",
    answer_type="word",
    probe_label_space="first letter (26)",
    basis_kind="(control -- gate, not scored; per-item-fresh string, "
               "letter_sum split precedent for feasibility only)",
    composability="(control)",
    dumbest_baseline="copying the quoted span is surface-trivial by "
                     "design: the control gates measurement reliability "
                     "(argmax >= 0.9 at both probe sizes, design gate 4), "
                     "it never enters the scored ladder and its items "
                     "are never probe-fitted",
    oracle=_oracle_ctrl_copy,
    gen=_gen_ctrl_copy,
    seed=20260827,
    scored=False,
    surface_answer=_surface_ctrl_copy,
))
