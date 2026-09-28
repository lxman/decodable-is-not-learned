# experiments/exp6/tests/_build.py
"""Build rungs for the generator tests straight from the driver, with
the real collision index — no dependency on generate.py."""
from experiments.exp6.battery import collisions_6 as c6
from experiments.exp6.battery import spec as sp


def build(names, ctx) -> dict:
    return {n: sp.generate(sp.SPECS_6[n], ctx, collisions=c6.for_spec(sp.SPECS_6[n]),
                           collisions_extra=c6.extra_for_spec(sp.SPECS_6[n]))
            for n in names}


def check_clean(built) -> None:
    for name, d in built.items():
        items = d["eval_items"]
        assert len(items) == 500 and len(d["shots"]) == 2, name
        assert len({it["question"] for it in items}) == 500, name
        keys = c6.for_spec(sp.SPECS_6[name])
        assert not any(it["bb_sha256"] in keys for it in items), name
        extra = c6.extra_for_spec(sp.SPECS_6[name])
        assert not any(k in extra for it in items
                       for k in it.get("bb_extra_sha256", [])), name
        assert d["shots"][0][1] != d["shots"][1][1], name
