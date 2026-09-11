# experiments/exp4/tests/conftest.py
"""Registers the `slow` mark (2n's convention, carried forward even
though no exp4 test uses it yet) so pytest does not warn it is
unknown."""
from __future__ import annotations


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "slow: exercises real git against committed tags (slow)")
