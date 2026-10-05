"""Shared raw-string recipes/constants with retired orchestration exports.

Use exp7integration.world_harness.exercise for miniature protocol tests and its
full_worlds for the separately authorized future synthetic freeze. The legacy
exports below refuse before effects; make_recipe and draws remain active.
"""
from typing import Protocol
from .evidence import require

FAMILIES = ("unscrambling", "deduction", "units", "shapes")
ARMS = ("q0", "q1", "q0s", "q1s")
GRID = tuple(range(40000, 400001, 40000)) + tuple(range(600000, 3400001, 200000)) + (3440000,)
STATES = ("INPUT-SENSITIVE-FORECAST", "SELECTIVE-ONLY", "ORDER-ONLY",
          "NO-JOINT-SUPPORT", "UNDETERMINED")
POISONS = ("missing-sham", "missing-twin", "unequal-k", "duplicate-row", "shared-stream",
    "wrong-target", "wrong-host", "wrong-model-digest", "missing-checkpoint", "swapped-loaders",
    "endpoint-count-only-match", "anchor-mismatch", "seal-after-outcome", "power-after-outcome",
    "self-pin", "entry-only-pin", "changed-init", "transient-unpinned-import", "unpinned-read",
    "HALTED-before-final", "duplicate-once-claim", "missing-secondary", "malformed-power")

class CampaignFixture(Protocol):
    """Legacy protocol declaration, not the active world-harness fixture contract.

    The supported exp7integration.world_harness additionally requires success
    publication and source restoration with truthful phase accounting.
    """
    def install(self, root, recipe): ...
    def poison(self, root, case): ...
    def analyze(self, root): ...
    def summarize(self, report): ...
    def scientific_inputs(self, root): ...
    def claimed(self, root): ...

def draws(mode, index, count, *, k=64):
    require(mode in STATES and k in (16, 64), "fixture mode/budget")
    # The same y ordering serves both predictors, allowing asymmetric worlds.
    rank = index / max(1, count - 1)
    if mode == "INPUT-SENSITIVE-FORECAST":
        n00 = k // 2 + round(rank * k / 2)
    elif mode == "SELECTIVE-ONLY":
        n00 = k
    elif mode == "ORDER-ONLY":
        n00 = round(rank * k)
    else:
        n00 = k // 2
    q0 = ["alpha"] * n00 + ["beta"] * (k - n00)
    q1 = ["alpha"] * (k - n00) + ["beta"] * n00
    return {"q0": q0, "q1": q1, "q0s": list(q0), "q1s": list(q1)}

def make_recipe(left, right, *, pairs=500):
    require(left in STATES and right in STATES and type(pairs) is int and 2 <= pairs <= 500, "world recipe")
    # Eligibility is outcome/u-only. UNDETERMINED is shared when y is thin;
    # asymmetric eligibility uses predictor-specific u buckets, an additional
    # explicit fixture supplied by the integration adapter, not faked here.
    require((left == "UNDETERMINED") == (right == "UNDETERMINED"), "shared-y thin recipe only")
    families = {}
    for fidx, family in enumerate(FAMILIES):
        rows = []
        for index in range(pairs):
            y = index * 26 // (pairs - 1)
            if left == "UNDETERMINED" and fidx >= 2:
                y = 0
            outputs = {}
            for tindex, step in enumerate(GRID):
                outputs[str(step)] = dict(zip(ARMS, ("alpha", "beta", "alpha", "beta")
                    if tindex < y else ("alpha", "alpha", "alpha", "alpha")))
            rows.append({"id": f"{family}:{index:04d}", "index": index,
                "targets": ["alpha", "beta"], "answer_type": "word", "base": "synthetic-base",
                "prompts": {a: f"SYNTHETIC ONLY {family} {index} {a}" for a in ARMS},
                "trained": {"pythia_1b": draws(left, index, pairs), "olmo2_1b": draws(right, index, pairs)},
                "twin": draws("NO-JOINT-SUPPORT", index, pairs, k=16), "outputs": outputs,
                "baselines": {"constant": dict.fromkeys(ARMS, "alpha")}})
        families[family] = rows
    return {"schema": "exp7.synthetic-raw-world.v1", "pairs": pairs, "families": families,
            "grid": list(GRID), "expected": {"pythia_1b": left, "olmo2_1b": right}}

def full_worlds(adapter, root):
    """Retired; use exp7integration.world_harness.full_worlds for future freeze."""
    require(False, "exp7ops.worlds.full_worlds is retired; use exp7integration.world_harness.full_worlds")

def exercise_world_protocol(adapter, root, *, recipe_factory):
    """Retired; use exp7integration.world_harness.exercise for protocol tests."""
    require(False, "exp7ops.worlds.exercise_world_protocol is retired; use exp7integration.world_harness.exercise")
