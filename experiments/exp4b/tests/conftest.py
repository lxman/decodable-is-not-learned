# experiments/exp4b/tests/conftest.py
"""Registers the `slow` mark (2n's convention, carried forward from
exp4's own conftest) so pytest does not warn it is unknown, and TWO
session-scoped synthetic worlds (`full_shape_4b.build_world_4b`):
LEADS (mode="leads", seed=11 -- exp4's own `_leads_world` fixture's
choice, `experiments/exp4/tests/test_full_shape_4.py`) and FOLLOWS
(mode="follows", seed=3 -- the world that clears the design §4
feasibility floor and completes the placebo pipeline end to end;
Task 5's `test_full_shape_4b.py::_follows_world_4b`, promoted here from
module- to session-scope by Task 6 so `test_totality_4b.py` and
`test_determinism_4b.py` can share the SAME build rather than paying
their own ~11-13 minute `stage="full"` sweep). Every slow module in
this package shares both read-only, so each expensive build is paid
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


@pytest.fixture(scope="session")
def _follows_world_4b(tmp_path_factory):
    """Task 5's own module-scoped fixture (`test_full_shape_4b.py`),
    promoted to session scope: "follows" is the world whose OWN noise
    clears the design §4 feasibility floor and completes the placebo
    pipeline (S1-S8, gates 1-5, `p_cal`), unlike "leads" (which hits
    the floor first -- see `test_full_shape_4b.py`'s module docstring).
    seed=3, ONE fresh `stage="full"` build, shared by every module that
    needs a completing world."""
    from experiments.exp4b.tests import full_shape_4b as fs4b
    root = tmp_path_factory.mktemp("follows_world_4b")
    return fs4b.build_world_4b(root, "follows", seed=3)


def fresh_copy_4b(template_root, tmp_path) -> Path:
    dst = tmp_path / "world"
    shutil.copytree(template_root, dst)
    return dst
