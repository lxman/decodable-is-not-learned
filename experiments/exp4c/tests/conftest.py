# experiments/exp4c/tests/conftest.py
"""Registers the `slow` mark (exp4's convention) so pytest does not
warn it is unknown."""
from __future__ import annotations


def pytest_configure(config) -> None:
    config.addinivalue_line(
        "markers", "slow: exercises real git / the real committed trees (slow)")
