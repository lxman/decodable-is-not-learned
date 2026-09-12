# experiments/exp4/_threads_4.py
"""Thread pinning for Experiment 4 (final-review Minor 7; design §3.2's
"single-threaded, pinned kernel").

The k-NN kernel and every scalar the analyzer derives from it are
supposed to be a deterministic function of the activation bytes. A
multi-threaded BLAS reduction is not: the order in which partial sums
are combined depends on how many threads the pool happened to start
with, so `Xn @ Xn.T` can differ in its last bits between two processes
on the same machine, and the `argsort` that reads it can then order two
items whose similarities tie at that precision differently. The four
variables below are the ones numpy's backends read AT IMPORT TIME (the
thread pool is sized when the BLAS library is first loaded), so this
module must be imported BEFORE numpy — it is the first exp4 import in
`analyze_4.py`, `run/reference_4.py`, `run/sweep_4.py` and
`run/preflight_4.py`, each placed above the `import numpy` line and
above every other `experiments.*` import (all of which pull numpy in
transitively).

`PINNED_BEFORE_NUMPY_4` records whether that actually held in this
process: if some other module got numpy in first, the assignment below
is still made (and `threads_pinned_4()` still reads True) but it came
too late to size the pool, which is a disclosure, not a refusal —
nothing in the instrument depends on the pin for correctness, only for
byte-reproducibility across processes, and the determinism fixture
(`test_full_shape_4.test_determinism_fixture_two_processes`) is what
actually measures it.

No numpy, no torch, no I/O: importing this module must stay free."""
from __future__ import annotations

import os
import sys

THREAD_ENV_4 = ("VECLIB_MAXIMUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                "MKL_NUM_THREADS")

PINNED_BEFORE_NUMPY_4 = "numpy" not in sys.modules

for _v in THREAD_ENV_4:
    os.environ[_v] = "1"
del _v


def threads_pinned_4() -> bool:
    """True iff every variable in `THREAD_ENV_4` currently reads "1" in
    this process's environment — what the load record and the verdict
    carry as `threads_pinned`."""
    return all(os.environ.get(v) == "1" for v in THREAD_ENV_4)


def thread_pin_record_4() -> dict:
    """The disclosable form: the pin's own state plus whether it was
    applied before numpy was first imported."""
    return {"threads_pinned": threads_pinned_4(),
            "pinned_before_numpy": bool(PINNED_BEFORE_NUMPY_4),
            "variables": {v: os.environ.get(v) for v in THREAD_ENV_4}}
