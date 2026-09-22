"""Thread pinning for Experiment 5 (exp4's `_threads_4` shape, exp5's own
tag-bound file): the four variables numpy's BLAS backends read AT IMPORT
TIME, set to 1 before numpy is imported anywhere in this process, so the
sign-flip matvec (`signs @ block_sums`) and every mean the analyzer
computes are bit-reproducible across processes. No numpy, no torch, no
I/O here."""
from __future__ import annotations

import os
import sys

THREAD_ENV_5 = ("VECLIB_MAXIMUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                "MKL_NUM_THREADS")
PINNED_BEFORE_NUMPY_5 = "numpy" not in sys.modules
for _v in THREAD_ENV_5:
    os.environ[_v] = "1"
del _v


def thread_pin_record_5() -> dict:
    return {"env": {v: os.environ.get(v) for v in THREAD_ENV_5},
            "pinned_before_numpy": PINNED_BEFORE_NUMPY_5}
