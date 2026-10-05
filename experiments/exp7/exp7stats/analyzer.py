"""Once-only Experiment 7 verdict, all eight secondaries, no model imports."""
from exp7core.worlds import licence, aggregate
from .common import (SCHEMA, PREDICTORS, PRODUCTION, Shape, require, receipt,
                     digest, decode, stage, require_protocol, pin)
from .data import load_battery, load_predictors, load_outcomes, cells, predictor_support
from .kernels import primary, require_runtime
from .secondaries import build as secondaries
from .power import verify_power_semantics, realized_support, predictor_geometry
from .calibration import verify_envelope_semantics


def analyze_loaded(battery, predictors, outcomes, *, shape=PRODUCTION):
    """Pure composition on independently validated raw data; fixture-safe."""
    readings = {}
    for p in PREDICTORS:
        reading = primary(cells(predictors[p], outcomes, battery), B=shape.permutations,
                          namespace=("exp7-actual-verdict-v2", p), full=True)
        readings[p] = {**reading, "licence": licence(reading["state"])}
    secondary, intervals = secondaries(battery, predictors, outcomes, readings, shape)
    for p in PREDICTORS:
        readings[p]["bootstrap"] = intervals[p]
    return {"schema": SCHEMA, "stage": "analysis", "state": "COMPLETE",
            "battery_sha256": battery.sha256, "primary": readings,
            "aggregate": aggregate(readings), "secondaries": secondary,
            "fixed_families_note": "Bootstrap intervals do not generalize over task families or independently trained networks.",
            "selectivity_power_note": "Separate hypothetical envelope, not joint power or a data-adapted selectivity absence declaration."}


def _operation(campaign, provenance, shape, *, production):
    runtime = require_runtime()
    require_protocol(campaign, ("battery", "predictor_data", "outcomes", "verify_predictor_seal",
                                "verify_power", "verify_complete"))
    seal = receipt(campaign.verify_predictor_seal(), "seal_sha256")
    complete = receipt(campaign.verify_complete(), "complete_sha256")
    power_receipt = receipt(campaign.verify_power(), "power_sha256")
    require(type(seal.get("bindings")) is dict and seal["bindings"] and
            type(complete.get("bindings")) is dict and complete["bindings"], "independent complete bindings")
    battery = load_battery(campaign.battery(), shape)
    require(seal.get("battery_sha256") == battery.sha256, "seal battery mismatch")
    record = decode(power_receipt.get("record"))
    require(type(record) is dict and digest(record) == power_receipt["power_sha256"], "power record byte-equivalent digest")
    predictors = load_predictors(campaign.predictor_data(), battery, shape)
    if production:
        record = verify_power_semantics(record, seal["seal_sha256"], battery.sha256,
                                        geometry=predictor_geometry(predictors))
        verify_envelope_semantics(record.get("selectivity_envelope"))
        pin(record.get("calibration_sha256"))
    else:
        # Explicit miniature API never claims actual power. It still checks
        # independent identity; no production record may cross this route.
        require(record.get("fixture") is True and record.get("seal_sha256") == seal["seal_sha256"]
                and record.get("battery_sha256") == battery.sha256, "miniature power identity")
    if production:
        require(digest(record.get("predictor_support")) == digest({p: predictor_support(predictors[p]) for p in PREDICTORS}),
                "power predictor support/ties do not rederive from seal")
    outcomes = load_outcomes(campaign.outcomes(), battery, shape)
    result = analyze_loaded(battery, predictors, outcomes, shape=shape)
    if production:
        power = realized_support(record, predictors, outcomes, result["primary"])
        envelope = record["selectivity_envelope"]
    else:
        power = {p: {"status": "SYNTHETIC-NO-POWER-CLAIM"} for p in PREDICTORS}
        envelope = {"status": "SYNTHETIC-NO-ENVELOPE-RUN"}
    return {**result, "seal_sha256": seal["seal_sha256"], "complete_sha256": complete["complete_sha256"],
            "statistical_runtime": runtime,
            "power_sha256": power_receipt["power_sha256"], "forecast_power": power,
            "selectivity_envelope": envelope, "verification_bindings": {
                "predictor": seal["bindings"], "outcomes": complete["bindings"]}}


def run(campaign):
    """Only production entry; 500 pairs,26 steps,10k+10k tests,1k bootstrap."""
    return stage(campaign, "analysis", lambda provenance: _operation(campaign, provenance, PRODUCTION, production=True))


def synthetic_run(campaign, shape):
    """Explicit synthetic-only entry, produces production:false receipts."""
    require(isinstance(shape, Shape) and shape.n < 500 and shape.permutations < 10000
            and shape.bootstraps < 1000, "miniature shape required")
    return stage(campaign, "analysis", lambda provenance: _operation(campaign, provenance, shape, production=False),
                 production=False)
