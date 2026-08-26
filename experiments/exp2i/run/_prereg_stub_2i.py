# experiments/exp2i/run/_prereg_stub_2i.py
"""Placeholder for `analyze_2i.require_prereg_2i` (Task 3's single real
implementation, design §7 / Global Constraints: the tag
`exp2i-preregistered` is blob-bound to the analyzer, battery, sampler
stage, endpoint stage and sweep runner). `sample_2i`/`endpoint_2i`
import-guard onto this stub until Task 3 lands:

    try:
        from experiments.exp2i.analyze_2i import require_prereg_2i
    except ImportError:
        from experiments.exp2i.run._prereg_stub_2i import require_prereg_2i

FAILS CLOSED in production: `require_prereg_2i()` called with no
arguments (both `tag_exists`/`blob_sha` default `None`) always raises
— nothing in this build can pass model contact on the strength of an
unbuilt analyzer. A test that supplies BOTH exercises this module's
own tag+blob check, so `sample_2i`/`endpoint_2i`'s WIRING to the
refusal (does a missing tag propagate? a stale blob?) is testable now,
without waiting on Task 3.

Judgment call, disclosed: this stub's own instrument-blob set
(`INSTRUMENT_BLOBS_STUB_2I`) covers only the three files that exist at
Task 2's build time — `battery_2i.py`, `run/sample_2i.py`,
`run/endpoint_2i.py`. The brief's full `INSTRUMENT_BLOBS_2I` also
names `analyze_2i.py` (Task 3) and `run/sweep_2i.py` (Task 4), neither
of which exists yet; Task 3's real `analyze_2i.require_prereg_2i` is
the authority for the complete five-file set. Task 4 deletes this
file per the brief."""

from __future__ import annotations

import sys
from pathlib import Path

EXP2I = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP2I.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402

INSTRUMENT_BLOBS_STUB_2I = (
    "experiments/exp2i/battery_2i.py",
    "experiments/exp2i/run/sample_2i.py",
    "experiments/exp2i/run/endpoint_2i.py",
)


def require_prereg_2i(*, tag_exists=None, blob_sha=None) -> dict:
    if tag_exists is None or blob_sha is None:
        raise RuntimeError(
            "exp2i: analyze_2i.require_prereg_2i not built yet — refusing")
    if not tag_exists(bi.PREREG_TAG):
        raise RuntimeError(f"refusing: the preregistration tag "
                           f"{bi.PREREG_TAG!r} does not exist — the design "
                           f"must be frozen and tagged before any OLMo "
                           f"model contact")
    blobs, drift = {}, []
    for rel in INSTRUMENT_BLOBS_STUB_2I:
        p = REPO / rel
        got = bg.sha256_file(p) if p.is_file() else None
        want = blob_sha(bi.PREREG_TAG, rel)
        blobs[rel] = got
        if got is None:
            drift.append(f"{rel}: not on disk")
        elif want is None:
            drift.append(f"{rel}: no blob at {bi.PREREG_TAG}")
        elif want != got:
            drift.append(f"{rel}: working copy {got} != {want} at the tag")
    if drift:
        raise RuntimeError(f"refusing: the instrument has drifted from "
                           f"{bi.PREREG_TAG!r} — {'; '.join(drift)}")
    return {"tag": bi.PREREG_TAG, "instrument_blobs": blobs}
