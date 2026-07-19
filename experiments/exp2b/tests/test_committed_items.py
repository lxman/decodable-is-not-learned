"""Known-answer gates against the COMMITTED item files (exp2's convention:
the file, not the generator, is the operationalization — so the file is what
gets verified). Skips cleanly if items have not been generated yet."""

import json
from pathlib import Path

import pytest

from battery.base import ITEMS_DIR, load_items, normalize_answer
from battery.generators import SPECS

_SPEC = {s.name: s for s in SPECS}


def _committed():
    if not ITEMS_DIR.exists():
        return []
    names = [p.stem for p in sorted(ITEMS_DIR.glob("*.json"))
             if p.stem not in ("ejections", "scored_battery")]
    return names


@pytest.mark.parametrize("name", _committed())
def test_oracle_scores_100_percent_on_committed_items(name):
    spec = _SPEC[name]
    payload = load_items(name)
    for it in payload["eval_items"] + payload["probe_items"]:
        ora = spec.oracle(it["question"])
        assert normalize_answer(ora, spec.answer_type) == \
            normalize_answer(it["answer"], spec.answer_type), (name, it["question"])


@pytest.mark.parametrize("name", [n for n in _committed()
                                  if _SPEC[n].scored])
def test_committed_feasibility_and_basis(name):
    spec = _SPEC[name]
    payload = load_items(name)
    feas = payload["feasibility"]
    assert len(feas["per_seed"]) == 5
    for s, info in feas["per_seed"].items():
        assert info["n_val"] >= 300 or spec.split_params.min_val_items < 300
    # basis independently recomputable from text on a sample
    for it in payload["probe_items"][:50]:
        assert tuple(it["basis"]) == tuple(str(v) for v in spec.basis_fn(it["question"]))


def test_ejections_are_exactly_the_designed_five():
    ej = json.loads((ITEMS_DIR / "ejections.json").read_text())
    assert set(ej) == {"month_offset", "letter_half", "alpha_offset",
                      "plural_irreg", "past_irreg"}


def test_candidate_count_meets_design_target():
    # 30 specs - 5 designed ejections - 1 positive control = 24 scored
    # candidates, meeting the design's n >= 24 target BEFORE M1 inclusion
    # (which may itself eject above-threshold candidates).
    scored = [n for n in _committed() if _SPEC[n].scored]
    assert len(scored) == 24
