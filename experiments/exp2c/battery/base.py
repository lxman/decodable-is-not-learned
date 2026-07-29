"""Spec discipline for 2c (design §2): 2b's five mandatory fields plus
family membership + dial value. A spec that cannot fill its fields
honestly does not enter the battery."""

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class CapabilitySpec:
    name: str
    family: str
    dial_name: str
    dial_value: object
    description: str
    answer_type: str
    probe_label_space: str
    basis_kind: str
    composability: str
    dumbest_baseline: str
    oracle: Callable
    gen: Callable
    seed: int
    scored: bool = True
    rescue_of: Optional[str] = None
    mechanism_tested: Optional[str] = None
    # Review ruling 2026-07-29 (Fix A): the committed item's `answer` is
    # surface_answer(*gen_output) -- the full task result the question
    # text demands -- while `probe_label` stays on `oracle`. None means
    # the oracle output IS the true surface answer (the template asks for
    # the probe target directly, as in the rescue-style specs).
    surface_answer: Optional[Callable] = None


REQUIRED_TEXT = ("family", "description", "probe_label_space", "basis_kind",
                 "composability", "dumbest_baseline")


def validate_spec(spec: CapabilitySpec) -> list:
    v = []
    for f in REQUIRED_TEXT:
        if not getattr(spec, f):
            v.append(f"{spec.name}: empty mandatory field '{f}'")
    if spec.dial_value is None or not spec.dial_name:
        v.append(f"{spec.name}: dial (name, value) is mandatory (design §2)")
    if spec.rescue_of and not spec.mechanism_tested:
        v.append(f"{spec.name}: rescue must name the mechanism it tests")
    if not callable(spec.oracle) or not callable(spec.gen):
        v.append(f"{spec.name}: oracle and gen must be callables")
    return v


SPECS: dict = {}


def register(spec: CapabilitySpec) -> CapabilitySpec:
    bad = validate_spec(spec)
    if bad:
        raise ValueError("; ".join(bad))
    SPECS[spec.name] = spec
    return spec
