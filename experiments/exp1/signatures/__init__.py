"""The reusable three-signature instrument.

Import-clean: nothing here depends on the task/model/training code, so Experiments
2/3/4 can `from signatures import ...` without pulling in Exp 1's harnesses.

M1 exposed the frozen primitives and data contract; M2 adds the signature logic
(activations + probe/sampling/forecast). Exp 2/3/4 import the three signature
functions and the schema from here.
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
from .activations import ResidualActivationCollector
from .probe import probe_below_threshold
from .sampling import elicit_by_sampling
from .forecast import forecast_from_below

__all__ = [
    # stats primitives
    "bonferroni",
    "clopper_pearson",
    "cohens_d",
    "permutation_null",
    # schema / data contract
    "AXES",
    "SIZE_BUCKETS",
    "SYSTEMS",
    "ForecastResult",
    "GTCheck",
    "ProbeResult",
    "RunRecord",
    "SamplingResult",
    # signature logic
    "ResidualActivationCollector",
    "probe_below_threshold",
    "elicit_by_sampling",
    "forecast_from_below",
]
