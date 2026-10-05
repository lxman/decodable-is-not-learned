"""Raw-string fixture recipe and adapter-driven production-composition worlds.

Only make_recipe(..., pairs=small) is run during planning. Full execution is a
future build test using the FINAL reconciled Campaign adapter, never a core-only
world lookup and never a real campaign tree.
"""
from typing import Protocol
from itertools import product
from .evidence import require, canonical, digest, once, snapshot

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
    """Pinned adapter must use production producers, validators and analyzer.

    install writes complete fake raw units, independent trust/tag/grant records,
    anchors and both genuinely separate host loader paths using production
    serializers. No precomputed score/expected verdict is installed as input.
    analyze consumes its once-claim and returns saved report; summarize projects
    the report without recomputing tests. poisoning edits bytes after valid setup.
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
    return exercise_world_protocol(adapter, root, recipe_factory=make_recipe)

def exercise_world_protocol(adapter, root, *, recipe_factory):
    """Explicit recipe injection is for MINIATURE protocol tests, not live CLI."""
    root.mkdir()
    cases = list(product(STATES[:4], repeat=2)) + [("UNDETERMINED", "UNDETERMINED")]
    records = []
    for index, (left, right) in enumerate(cases):
        target = root / f"world-{index:02d}"
        target.mkdir()
        recipe = recipe_factory(left, right)
        adapter.install(target, recipe)
        before = adapter.scientific_inputs(target)
        report = adapter.analyze(target)
        view = adapter.summarize(report)
        require(view["states"] == recipe["expected"], "raw-tree world mismatch")
        require(view["secondaries"] == list(range(1, 9)), "all eight secondary sections required")
        require("does not identify an internal algorithm" in view["licence"], "licence limitation missing")
        require(adapter.scientific_inputs(target) == before, "analysis changed raw evidence")
        require(adapter.claimed(target) is True, "analysis once-claim absent")
        # Re-entry must deliver refusal, never another statistical invocation.
        again = adapter.summarize(adapter.analyze(target))
        require(set(again["states"].values()) == {"INSUFFICIENT_DATA"}, "once gate failed")
        from exp7stats.common import dumps
        records.append({"case": [left, right], "report_sha256": digest(dumps(report))})
    for poison in POISONS:
        target = root / poison
        target.mkdir()
        adapter.install(target, recipe_factory(STATES[0], STATES[0]))
        adapter.poison(target, poison)
        before = adapter.scientific_inputs(target)
        view = adapter.summarize(adapter.analyze(target))
        require(set(view["states"].values()) == {"INSUFFICIENT_DATA"}, "poison escaped: " + poison)
        require(view["statistics_executed"] is False, "refusal computed statistics")
        require(adapter.scientific_inputs(target) == before, "poison evidence erased")
        records.append({"poison": poison, "state": "INSUFFICIENT_DATA"})
    once(root / "worlds-receipt.json", records)
    return records
