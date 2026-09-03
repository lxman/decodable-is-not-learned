# experiments/exp2m/tests/conftest.py
"""Registers the `slow` mark used by test_stages_2m.py's
`test_predictor_seals_bind_for_real` (real git against the committed
2k/2i seal tags, ≈ 15 s) so pytest does not warn it is unknown."""
from __future__ import annotations


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "slow: exercises real git against committed tags (slow)")
