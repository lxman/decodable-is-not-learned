# experiments/exp5/tests/conftest.py
"""Registers the `slow` mark (exp4c's convention)."""
from __future__ import annotations


def pytest_configure(config) -> None:
    config.addinivalue_line(
        "markers", "slow: exercises real git / the real committed trees / the Hub file (slow)")
