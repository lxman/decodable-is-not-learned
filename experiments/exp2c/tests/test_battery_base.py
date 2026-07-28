import pytest

from experiments.exp2c.battery.base import CapabilitySpec, validate_spec


def _spec(**kw):
    d = dict(
        name="mod17", family="modulus", dial_name="modulus", dial_value=17,
        description="(a+b) mod 17, 3-digit operands",
        answer_type="number", probe_label_space="a mod 17 (0-16)",
        basis_kind="first operand token (900 values)",
        composability="mod-17 of a 3-digit operand requires digit "
                      "composition; 17 shares no factor with 10",
        dumbest_baseline="lookup keyed on operand token scores chance on "
                         "starved val; random net: mod-17 of multi-digit "
                         "token not expressible from digit statistics",
        oracle=lambda a, b: (a + b) % 17,
        gen=lambda rng: (rng.integers(100, 999), rng.integers(100, 999)),
        seed=20260801, scored=True, rescue_of=None, mechanism_tested=None,
    )
    d.update(kw)
    return CapabilitySpec(**d)


def test_valid_spec_passes():
    assert validate_spec(_spec()) == []


def test_six_mandatory_fields_enforced():
    assert any("family" in v for v in validate_spec(_spec(family="")))
    assert any("dumbest_baseline" in v
               for v in validate_spec(_spec(dumbest_baseline="")))
    assert any("dial" in v for v in validate_spec(_spec(dial_value=None)))


def test_rescue_requires_mechanism():
    bad = _spec(rescue_of="roman", mechanism_tested=None)
    assert any("mechanism" in v for v in validate_spec(bad))
