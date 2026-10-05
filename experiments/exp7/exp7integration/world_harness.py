"""Final producer-world protocol with manager-approved truthful phase accounting."""
from itertools import product
from exp7ops.evidence import require, once, canonical, digest
from exp7ops.worlds import STATES, POISONS, make_recipe

LATE_FAULTS = frozenset(("entry-only-pin", "HALTED-before-final"))


def full_worlds(fixture, root):
    """Future freeze only: literal n500/raw64/twin16/grid26 and default statistics."""
    require(fixture.miniature is False, "full worlds require default numerical driver")
    return exercise(fixture, root, recipe_factory=make_recipe)


def exercise(fixture, root, *, recipe_factory):
    root.mkdir()
    rows = []
    try:
        for i, pair in enumerate(list(product(STATES[:4], repeat=2))+[(STATES[4], STATES[4])]):
            target = root/f"world-{i:02d}"; target.mkdir()
            recipe = recipe_factory(*pair)
            fixture.install(target, recipe)
            before = fixture.scientific_inputs(target)
            report = fixture.analyze(target); view = fixture.summarize(report)
            require(view["states"] == recipe["expected"] and view["statistics_executed"] is True, "raw producer-world mismatch")
            require(view["secondaries"] == list(range(1, 9)) and "does not identify an internal algorithm" in view["licence"], "secondary/licence coverage")
            require(fixture.scientific_inputs(target) == before and fixture.claimed(target), "raw evidence/once claims")
            require(fixture.success_published(target), "missing scientific publication")
            second = fixture.summarize(fixture.analyze(target))
            require(set(second["states"].values()) == {"INSUFFICIENT_DATA"} and second["statistics_executed"] is False, "once-only reentry executed")
            from exp7stats.common import dumps
            rows.append({"case": list(pair), "report_sha256": digest(dumps(report))})
        for poison in POISONS:
            target = root/poison; target.mkdir()
            fixture.install(target, recipe_factory(STATES[0], STATES[0]))
            fixture.poison(target, poison)
            before = fixture.scientific_inputs(target)
            view = fixture.summarize(fixture.analyze(target))
            require(set(view["states"].values()) == {"INSUFFICIENT_DATA"}, "poison escaped: "+poison)
            require(view["statistics_executed"] is (poison in LATE_FAULTS), "incorrect phase accounting: "+poison)
            require(not fixture.success_published(target), "poison published scientific success: "+poison)
            require(fixture.scientific_inputs(target) == before, "poison evidence erased")
            rows.append({"poison": poison, "state": "INSUFFICIENT_DATA", "statistics_executed": view["statistics_executed"]})
        once(root/"worlds-receipt.json", rows)
        return rows
    finally:
        fixture.restore_sources()
