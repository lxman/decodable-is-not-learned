"""The reusable three-signature instrument.

Import-clean: nothing here depends on the task/model/training code, so Experiments
2/3/4 can `from signatures import ...` without pulling in Exp 1's harnesses.

M1 exposes the frozen primitives and data contract. Signature logic (probe/sampling/
forecast) lands in M2 and will be re-exported here.
"""

from .stats import bonferroni, clopper_pearson, cohens_d, permutation_null
from .schema import (
    AXES,
    SIZE_BUCKETS,
    SYSTEMS,
    ForecastResult,
    GTCheck,
    ProbeResult,
    RunRecord,
    SamplingResult,
)

__all__ = [
    "bonferroni",
    "clopper_pearson",
    "cohens_d",
    "permutation_null",
    "AXES",
    "SIZE_BUCKETS",
    "SYSTEMS",
    "ForecastResult",
    "GTCheck",
    "ProbeResult",
    "RunRecord",
    "SamplingResult",
]
