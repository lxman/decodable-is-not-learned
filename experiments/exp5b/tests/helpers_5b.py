# experiments/exp5b/tests/helpers_5b.py
"""Shared injections for the 5b tests: the tag callables over the repo's
real files, and the prereg wrap over the 5b blobs PRESENT on disk (the
analyzer and the power record land at Tasks 5/6; `require_prereg_5b`'s
`blobs` keyword default is bound at definition time, so the module
attribute is wrapped, as Experiment 5's `test_stages_5.py` did)."""
from __future__ import annotations

from experiments.exp2g import battery_2g as bg
from experiments.exp5b import battery_5b as b5b


def blob_sha_disk(tag, rel):
    p = b5b.REPO / rel
    return bg.sha256_file(p) if p.is_file() else None


def tag_inj():
    return dict(tag_exists=lambda t: True, blob_sha=blob_sha_disk)


def wrap_prereg_over_present_blobs(monkeypatch):
    orig = b5b.require_prereg_5b
    present = tuple(rel for rel in b5b.INSTRUMENT_BLOBS_5B if (b5b.REPO / rel).is_file())
    monkeypatch.setattr(b5b, "require_prereg_5b",
                        lambda *, tag_exists=None, blob_sha=None, blobs=present:
                        orig(tag_exists=tag_exists, blob_sha=blob_sha, blobs=blobs))
