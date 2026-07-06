"""Battery invariants (design doc §2-§3). These run against the COMMITTED item
files, not just the generators — the file is the operationalization, so the file
is what gets tested."""

import json
import re
from pathlib import Path

import pytest

from battery.base import ITEMS_DIR, N_EVAL, N_PROBE, normalize_answer, render_prompt, verify
from battery.generators import SPEC_BY_NAME, SPECS, _WORDS, from_roman, to_roman

SCORED = [s.name for s in SPECS if s.scored]
CONTROLS = [s.name for s in SPECS if not s.scored]


def _load(name):
    return json.loads((ITEMS_DIR / f"{name}.json").read_text())


# ---- file-level invariants ----------------------------------------------------

def test_all_specs_have_committed_files():
    assert len(SPECS) == 18 and len(SCORED) == 16 and len(CONTROLS) == 2
    for s in SPECS:
        assert (ITEMS_DIR / f"{s.name}.json").exists(), f"missing items for {s.name}"


@pytest.mark.parametrize("name", [s.name for s in SPECS])
def test_item_counts_and_schema(name):
    d = _load(name)
    assert len(d["eval_items"]) == N_EVAL and len(d["probe_items"]) == N_PROBE
    assert len(d["shots"]) == 2
    for it in d["eval_items"] + d["probe_items"]:
        assert it["question"] and it["answer"] and it["probe_label"] != ""


@pytest.mark.parametrize("name", [s.name for s in SPECS])
def test_oracle_scores_100_percent_on_committed_items(name):
    """THE known-answer gate: the text-parsing oracle must recompute every
    committed answer exactly (process rule 2, applied to the battery itself)."""
    d, spec = _load(name), SPEC_BY_NAME[name]
    for it in d["eval_items"] + d["probe_items"]:
        ora = spec.oracle(it["question"])
        assert verify(ora, it["answer"], spec.answer_type), \
            f"{name}: oracle {ora!r} != {it['answer']!r} on {it['question']!r}"


@pytest.mark.parametrize("name", [s.name for s in SPECS])
def test_shots_are_correct_and_disjoint_from_items(name):
    d, spec = _load(name), SPEC_BY_NAME[name]
    qs = {it["question"] for it in d["eval_items"] + d["probe_items"]}
    for q, a in d["shots"]:
        assert q not in qs, f"{name}: shot leaked into items"
        try:
            assert verify(spec.oracle(q), a, spec.answer_type), f"{name}: bad shot {q!r}"
        except Exception as e:  # oracle must parse its own shots
            raise AssertionError(f"{name}: oracle cannot parse shot {q!r}: {e}")


@pytest.mark.parametrize("name", SCORED)
def test_scored_items_are_unique(name):
    d = _load(name)
    qs = [it["question"] for it in d["eval_items"] + d["probe_items"]]
    assert len(set(qs)) == len(qs)


# ---- split hygiene --------------------------------------------------------------

@pytest.mark.parametrize("name", ["unscramble", "acronym", "alpha_order", "cipher"])
def test_word_pool_tasks_share_no_words_across_splits(name):
    """Design §3: probe/eval item-AND-word disjointness for word-pool tasks (the
    Exp 1 entity-split discipline: the probe must generalize, not memorize)."""
    d = _load(name)
    rx = re.compile(r"'([a-z ]+)'|: ([a-z, ]+)\?")

    def words_of(items):
        out = set()
        for it in items:
            m = rx.search(it["question"])
            blob = (m.group(1) or m.group(2)) if m else ""
            out |= set(blob.replace(",", " ").split())
            out.add(it["answer"])
        return out

    ev, pr = words_of(d["eval_items"]), words_of(d["probe_items"])
    if name == "acronym":
        # answers are letter-strings, not pool words — check the source words only
        ev = {w for w in ev if len(w) > 3}
        pr = {w for w in pr if len(w) > 3}
        assert not ev & pr, f"{name}: source words cross splits"
    else:
        ans_ev = {it["answer"] for it in d["eval_items"]}
        ans_pr = {it["answer"] for it in d["probe_items"]}
        assert not ans_ev & ans_pr, f"{name}: answers cross splits"
        if name == "alpha_order":
            assert not ev & pr, f"{name}: source words cross splits"


def test_wordlist_is_4_to_6_letters_lowercase():
    for w in _WORDS:
        assert 4 <= len(w) <= 6 and w.isalpha() and w.islower(), w


# ---- probe labels ---------------------------------------------------------------

@pytest.mark.parametrize("name", [s.name for s in SPECS])
def test_probe_labels_have_usable_cardinality(name):
    """A probe target needs >=2 classes, each with >=30 probe examples (else the
    5-seed logistic probe of design §3 is data-starved on its rarest class)."""
    from collections import Counter
    d = _load(name)
    counts = Counter(it["probe_label"] for it in d["probe_items"])
    assert len(counts) >= 2, f"{name}: constant probe label"
    assert min(counts.values()) >= 30, f"{name}: starved class {counts.most_common()[-1]}"


# ---- verification helpers -------------------------------------------------------

def test_normalize_answer_numbers():
    assert normalize_answer(" 1,234 meters\nextra", "number") == "1234"
    assert normalize_answer("The answer is 85.", "number") == "85"


def test_normalize_answer_words():
    assert normalize_answer(" Apple.\n", "word") == "apple"
    assert normalize_answer("'noah'", "word") == "noah"


def test_render_prompt_two_shot_shape():
    p = render_prompt("What is 2 + 2?", [("What is 1 + 1?", "2"), ("What is 3 + 1?", "4")])
    assert p.count("Q:") == 3 and p.endswith("A:")


def test_roman_round_trip():
    for n in range(1, 100):
        assert from_roman(to_roman(n)) == n
