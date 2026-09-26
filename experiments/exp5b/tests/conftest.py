# experiments/exp5b/tests/conftest.py
"""Registers the `slow` mark (Experiment 5's convention)."""
from __future__ import annotations


def pytest_configure(config) -> None:
    config.addinivalue_line(
        "markers", "slow: exercises real git / the real committed trees (slow)")
