"""Licences are part of the rule, not editorial aftercare."""
from .contract import PREDICTORS, require

LIMIT = ("Shared input-sensitive difficulty and learned heuristics remain live explanations. "
         "This does not identify an internal algorithm or distinguish resolution from "
         "new computation. No unqualified joint POWERED label is available.")
LICENCES = {
    "INSUFFICIENT_DATA": "Instrument could not adjudicate.",
    "UNDETERMINED": "Not enough informative families for the forecast rule.",
    "INPUT-SENSITIVE-FORECAST": (
        "On this battery, the conditional target-response score shifts in the correct "
        "direction on average and forecasts paired success in SmolLM3-3B. Fixed "
        "within-pair/render target odds with changing availability alone cannot supply "
        "its expected conditional shift. This is an aggregate conjunction; per-family "
        "witnesses must be named separately."),
    "SELECTIVE-ONLY": (
        "The small model responds in the correct direction, but transfer does not reach "
        "the forecast rule at the declared resolution."),
    "ORDER-ONLY": (
        "A relative item ordering exists without the specified mean conditional "
        "target-shift evidence. No partial-competence mechanism licence."),
    "NO-JOINT-SUPPORT": (
        "The proposed joint account is not supported at this resolution. No conclusion "
        "that outputs contain no task information.")}


def licence(state):
    require(state in LICENCES, "unknown state")
    return LICENCES[state] + " " + LIMIT


def aggregate(readings):
    require(type(readings) is dict and set(readings) == set(PREDICTORS), "two predictors required")
    states = {p: readings[p]["state"] for p in PREDICTORS}
    require(set(states.values()) <= set(LICENCES), "unknown predictor state")
    named = tuple(p for p in PREDICTORS if states[p] == "INPUT-SENSITIVE-FORECAST")
    if "INSUFFICIENT_DATA" in states.values():
        label = "INSUFFICIENT_DATA"
    elif len(named) == 2:
        label = "BOTH-PREDICTORS"
    elif named:
        label = "PYTHIA-ONLY" if named[0] == "pythia_1b" else "OLMO-ONLY"
    else:
        label = "NO-PREDICTOR-JOINT-LICENCE"
    return {"aggregate": label, "licensed_predictors": named, "states": states,
            "licences": {p: licence(states[p]) for p in PREDICTORS},
            "note": "Retain both full predictor readings, eligible sets and component power disclosures."}
