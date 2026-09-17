# experiments/exp4b/tests/conftest.py
"""Registers the `slow` mark (2n's convention, carried forward from
exp4's own conftest) so pytest does not warn it is unknown, and the
ONE session-scoped synthetic LEADS world (`full_shape_4b.
build_world_4b`, mode="leads", seed=11 -- exp4's own `_leads_world`
fixture's choice, `experiments/exp4/tests/test_full_shape_4.py`)
`test_analyze_4b.py` and `test_full_shape_4b.py` both share read-only,
so the one expensive `stage="full"` sweep (~11-13 minutes) is paid
ONCE per test session rather than once per module."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "slow: exercises real git against committed tags (slow)")


@pytest.fixture(scope="session")
def _leads_world_4b(tmp_path_factory):
    from experiments.exp4b.tests import full_shape_4b as fs4b
    root = tmp_path_factory.mktemp("leads_world_4b")
    root, v4 = fs4b.build_world_4b(root, "leads", seed=11)
    return root, v4


def fresh_copy_4b(template_root, tmp_path) -> Path:
    dst = tmp_path / "world"
    shutil.copytree(template_root, dst)
    return dst
