# experiments/exp4b/tests/conftest.py
"""Registers the `slow` mark (2n's convention, carried forward from
exp4's own conftest) so pytest does not warn it is unknown."""
from __future__ import annotations


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "slow: exercises real git against committed tags (slow)")
