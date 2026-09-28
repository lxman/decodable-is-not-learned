# experiments/exp6/tests/test_records_6.py
"""Records: the layout, the draws' io, and the checks the analyzer runs
on every record — each check made to FAIL once, on a record that differs
from a good one in that field alone."""
import copy
import gzip
import json

import pytest

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import families_6 as fm
from experiments.exp6 import records_6 as r6
from experiments.exp6 import referents_6 as rf

CAP = None


@pytest.fixture(scope="module")
def cap():
    return b6.load_item_file_6("sort3")


def _rows(cap, seeds=(0,), dps=64, n_right=3):
    good = [" " + it["answer"] for it in cap["eval_items"]]
    return [{"item": i, "draws": {str(s): [good[i]] * n_right + [" qqq"] * (dps - n_right)
                                  for s in seeds}} for i in range(b6.N_ITEMS)]


# ------------------------------------------------------------------ layout
def test_the_tiers_and_units():
    units = r6.predictor_units()
    assert len(units) == 93 and len(set(units)) == 93
    assert r6.tier_shape("pythia_1b", "main")["k"] == 256
    assert r6.tier_shape("pythia_410m", "main")["k"] == 256
    assert r6.tier_shape("olmo2_1b", "main")["k"] == 64
    assert r6.tier_shape("pythia_1b", "pilot") == {
        "mode": "trained", "rungs": b6.RUNGS_6, "seeds": (1000,), "dps": 8, "k": 8}
    assert r6.tier_shape("pythia_1b", "twin")["mode"] == "untrained"
    assert r6.tier_shape("pythia_1b", "control")["rungs"] == ("ctrl_copy",)
    with pytest.raises(ValueError):
        r6.tier_shape("olmo2_1b", "twin")
    assert r6.TEST_PREDICTOR == {"A": "pythia_1b", "B": "olmo2_1b"}
    assert set(r6.tier_shape("pythia_1b", "main")["rungs"]) == \
        set(b6.RUNGS_6) | set(b6.ANCHORS_6)


def test_no_two_paths_differ_only_in_case(tmp_path):
    """The records cross from a case-sensitive box to a case-insensitive
    Mac: two names that differ only in case are one name there."""
    h = "ab" * 32
    paths = [r6.sweep_halt_path(tmp_path, "olmo7b"),
             r6.halted_step_dir(tmp_path, "olmo7b", 1000),
             r6.gate1_path(tmp_path, "olmo7b", h), r6.gate1_dir(tmp_path, "olmo7b", h),
             r6.step_dir(tmp_path, "olmo7b", 1000)]
    # results/sweep/<family>/<name>: the names inside one family's directory
    names = [p.relative_to(r6.sweep_dir(tmp_path, "olmo7b")).parts[0].lower()
             for p in paths]
    assert names == ["halted", "failed_steps", "gate1_abababababab.json",
                     "gate1_abababababab", "step1000"]
    assert len(set(names)) == len(names)
    assert r6.gate1_path(tmp_path, "olmo7b", h).name == "gate1_abababababab.json"
    assert r6.gate_record_path(tmp_path, "olmo7b", h, r6.SWEEP_THIN, "lcs").parts[-3:] \
        == ("gate1_abababababab", "thin", "lcs.json")
    assert r6.gate_load_path(tmp_path, "olmo7b", h, r6.SWEEP_CAND).name == "_cand.json"


def test_halt_markers_see_both_artifacts(tmp_path):
    assert r6.halt_markers(tmp_path) == []
    a = r6.tier_halt_path(tmp_path, "pythia_1b", "main", "lcs")
    a.parent.mkdir(parents=True)
    a.with_name(a.name + ".jsonl.gz").write_bytes(b"")     # the rows, marker not yet
    assert len(r6.halt_markers(tmp_path)) == 1
    d = r6.halted_step_dir(tmp_path, "olmo7b", 1000)
    d.mkdir(parents=True)                                   # the evidence, marker not yet
    assert len(r6.halt_markers(tmp_path)) == 2
    r6.sweep_halt_path(tmp_path, "olmo7b").write_text("x\n")
    r6.endpoint_halt_path(tmp_path).parent.mkdir(parents=True)
    r6.endpoint_halt_path(tmp_path).write_text("x\n")
    assert len(r6.halt_markers(tmp_path)) == 4


# ------------------------------------------------------------------- draws
def test_draws_round_trip_and_are_byte_stable(tmp_path, cap):
    rows = _rows(cap)
    r6.write_draws(tmp_path / "a.gz", rows)
    r6.write_draws(tmp_path / "b.gz", rows)
    assert (tmp_path / "a.gz").read_bytes() == (tmp_path / "b.gz").read_bytes()
    assert r6.read_draws(tmp_path / "a.gz", seeds=(0,), dps=64) == rows


@pytest.mark.parametrize("break_it,match", [
    (lambda rows: rows.pop(), "items are not"),
    (lambda rows: rows.__setitem__(3, dict(rows[3], item=2)), "items are not"),
    (lambda rows: rows[5]["draws"].__setitem__("1", rows[5]["draws"]["0"]), "seeds"),
    (lambda rows: rows[5]["draws"]["0"].pop(), "63 draws"),
    (lambda rows: rows[5]["draws"]["0"].__setitem__(0, 7), "draws"),
])
def test_read_draws_pins_coverage(tmp_path, cap, break_it, match):
    rows = _rows(cap)
    break_it(rows)
    r6.write_draws(tmp_path / "a.gz", rows)
    with pytest.raises(ValueError, match=match):
        r6.read_draws(tmp_path / "a.gz", seeds=(0,), dps=64)


def test_a_truncated_stream_raises_what_the_analyzer_collects(tmp_path, cap):
    from experiments.exp2i import analyze_2i as an2i
    r6.write_draws(tmp_path / "a.gz", _rows(cap))
    raw = (tmp_path / "a.gz").read_bytes()
    (tmp_path / "a.gz").write_bytes(raw[:len(raw) // 2])
    got, bad = an2i.collect_total(
        lambda: r6.read_draws(tmp_path / "a.gz", seeds=(0,), dps=64), "x")
    assert got is None and len(bad) == 1


def test_bits_counts_blocks_and_tallies(cap):
    rows = _rows(cap, seeds=(0, 1, 2, 3), dps=64, n_right=5)
    bits = r6.bits_of(rows, cap, seeds=(0, 1, 2, 3))
    assert len(bits) == 500 and all(len(b) == 256 for b in bits)
    assert r6.counts_of(bits) == [20] * 500
    assert r6.counts_of(bits, 64) == [5] * 500 and r6.counts_of(bits, 128) == [10] * 500
    assert [r6.block_counts(bits, b)[0] for b in range(4)] == [5, 5, 5, 5]
    t = r6.tallies_from_bits(bits, seeds=(0, 1, 2, 3), dps=64)
    assert t == {str(s): {"verified": 2500, "n_draws": 32000} for s in range(4)}
    assert r6.tallies_of(rows, cap, seeds=(0, 1, 2, 3)) == t
    # seed ORDER: a draw right only under seed 2 lands in the third block
    rows[0]["draws"] = {str(s): [" qqq"] * 64 for s in range(4)}
    rows[0]["draws"]["2"][0] = " " + cap["eval_items"][0]["answer"]
    bits = r6.bits_of(rows, cap, seeds=(0, 1, 2, 3))
    assert [r6.block_counts(bits, b)[0] for b in range(4)] == [0, 0, 1, 0]
    # the ladder reads the FIRST k draws: the seeds in order, 64 at a time
    assert [r6.counts_of(bits, k)[0] for k in r6.LADDER_K] == [0, 0, 1, 1]
    assert r6.counts_of([[1, 0, 0, 0], [0, 0, 0, 1]], 2) == [1, 0]


def test_a_runner_that_returns_too_few_continuations_is_refused(cap):
    class Short:
        def generate(self, prompts, max_new_tokens):
            return [" x"] * (len(prompts) - 1)

    class Whole:
        def generate(self, prompts, max_new_tokens):
            assert max_new_tokens == b6.max_new_tokens_6(cap["name"])
            return [" " + str(it["answer"]) for it in cap["eval_items"]]
    with pytest.raises(RuntimeError, match="wrong number of continuations"):
        r6.evaluate_items_6(Short(), cap)
    ev = r6.evaluate_items_6(Whole(), cap)
    assert ev["correct"] == 500 == sum(ev["bits"]) and len(ev["continuations"]) == 500


def test_diff_draws_counts_what_it_compared(cap):
    a, b = _rows(cap), _rows(cap)
    d = r6.diff_draws(a, b, seeds=(0,))
    assert d == {"items_compared": 500, "draws_compared": 32000, "n_diffs": 0,
                 "first": None}
    b[7]["draws"]["0"][3] += "!"
    d = r6.diff_draws(a, b, seeds=(0,))
    assert d["n_diffs"] == 1 and d["first"] == {"item": 7, "seed": 0, "draw": 3}
    with pytest.raises(ValueError, match="no committed row"):
        r6.diff_draws(a, b[:499], seeds=(0,))
    assert r6.diff_draws(a[:10], b, seeds=(0,))["items_compared"] == 10   # coverage is COUNTED


# ------------------------------------------------------------ tier records
def _tier(cap, **over):
    rows = _rows(cap)
    rec = r6.tier_record(predictor="olmo2_1b", tier="main", rung="sort3", cap=cap,
                         rows=rows, model=rf.model_pin("olmo2_1b"),
                         stack={"torch": "2.12.1"}, git_sha="abc", seconds=1.0,
                         draws_sha256="d" * 64)
    rec.update(over)
    return rec, r6.bits_of(rows, cap, seeds=(0,))


def _tier_failures(rec, bits, cap, **kw):
    args = dict(predictor="olmo2_1b", tier="main", rung="sort3", cap=cap, bits=bits,
                model_pin=rf.model_pin("olmo2_1b"), draws_sha256="d" * 64)
    args.update(kw)
    return r6.tier_record_failures(rec, **args)


def test_a_good_tier_record_has_no_failure(cap):
    rec, bits = _tier(cap)
    assert _tier_failures(rec, bits, cap) == []
    assert rec["k_total"] == 64 and rec["max_new_tokens"] == 16
    assert rec["prereg_tag"] == "exp6-preregistered"


@pytest.mark.parametrize("field,value", [
    ("rung", "sort5"), ("predictor", "pythia_1b"), ("tier", "pilot"), ("size", "1b"),
    ("mode", "untrained"), ("n_items", 499), ("answer_type", "word"), ("n_shots", 0),
    ("dtype", "float16"), ("items_sha256", "0" * 64), ("stream_namespace", "exp6"),
    ("seeds", [1]), ("draws_per_seed", 32), ("k_total", 32), ("max_new_tokens", 12),
    ("temperature", 0.7), ("truncation", "top_p"), ("prereg_tag", "other"),
    ("draws_file", "x.gz"), ("repo", "someone/else"), ("commit", "main"),
    ("model_sha", "0" * 64), ("model_sha", ""), ("draws_sha256", "e" * 64),
    ("untrained_seed", 0),
])
def test_every_pinned_field_of_a_tier_record_is_measured(cap, field, value):
    rec, bits = _tier(cap, **{field: value})
    bad = _tier_failures(rec, bits, cap)
    assert bad and any(field in b or "model" in b for b in bad), (field, bad)


def test_a_tier_record_whose_provenance_was_rewritten_is_caught(cap):
    """2i F-1: a record rewritten to claim another model, other items,
    another seed, left the verdict unchanged. Here each is a failure."""
    rec, bits = _tier(cap)
    rec["answers"] = rec["answers"][::-1]
    assert any("answers" in b for b in _tier_failures(rec, bits, cap))
    rec, bits = _tier(cap)
    rec["per_seed_tallies"]["0"]["verified"] += 1
    assert any("tallies" in b for b in _tier_failures(rec, bits, cap))
    rec, bits = _tier(cap)
    bits[0][0] ^= 1                       # the draws on disk say otherwise
    assert any("tallies" in b for b in _tier_failures(rec, bits, cap))


# ----------------------------------------------------------- outcome records
class _Runner:
    def __init__(self, conts):
        self.conts = conts

    def generate(self, prompts, max_new_tokens):
        self.seen = (len(prompts), max_new_tokens)
        return self.conts


def _unit(cap, family="olmo7b", step=1000, which=None, **over):
    man = fm.manifest(family)
    key = step if which is None else (fm.endpoint_step(family)
                                      if which != "init" else fm.INIT)
    entry = fm.entry(family, man, key)
    conts = [" " + it["answer"] for it in cap["eval_items"]]
    conts[1] = " qqq"
    run = _Runner(conts)
    ev = r6.evaluate_items_6(run, cap)
    assert run.seen == (500, 16) and ev["correct"] == 499 and ev["bits"][1] == 0
    info = {"tensor_digest": "dg", "sha256": dict(entry.get("lfs_sha256") or {}),
            "loading_info": {"missing_keys": 0, "unexpected_keys": 0,
                             "mismatched_keys": 0}}
    if entry.get("kind") == "from_config":
        info["seed"] = entry["seed"]
    load = r6.load_record(family=family, key=(which or int(step)), entry=entry,
                          info=info, device="cuda", host_sha256="h" * 64, seconds=1,
                          n_nonfinite=0)
    rec = r6.unit_record(family=family, rung="sort3", cap=cap, ev=ev, load=load,
                         host_sha256="h" * 64, seal_sha256="s" * 64,
                         stack={"torch": "2.12.1"}, git_sha="abc", seconds=1.0,
                         step=(None if which else step), which=which,
                         endpoint_sha256="e" * 64)
    rec.update(over)
    return rec, load, entry


def _unit_failures(rec, load, cap, step=1000, which=None, **kw):
    args = dict(family="olmo7b", rung="sort3", cap=cap, load=load,
                seal_sha256="s" * 64, host_sha256="h" * 64,
                step=(None if which else step), which=which,
                endpoint_sha256="e" * 64)
    args.update(kw)
    return r6.unit_record_failures(rec, **args)


def test_a_good_unit_record_has_no_failure(cap):
    rec, load, entry = _unit(cap)
    assert _unit_failures(rec, load, cap) == []
    assert r6.load_record_failures(load, family="olmo7b", key=1000, entry=entry,
                                   host_sha256="h" * 64) == []
    assert rec["step"] == 1000 and "which" not in rec
    assert rec["endpoint_sha256"] == "e" * 64
    rec, load, _ = _unit(cap, which="stage1_final")
    assert "endpoint_sha256" not in rec and "step" not in rec
    assert _unit_failures(rec, load, cap, which="stage1_final") == []
    rec, load, _ = _unit(cap, which=r6.SWEEP_THIN)
    assert rec["endpoint_sha256"] == "e" * 64            # a sweep host's read carries it
    with pytest.raises(ValueError, match="exactly one"):
        r6.unit_record(family="olmo7b", rung="sort3", cap=cap, ev={}, load=load,
                       host_sha256="", seal_sha256="", stack={}, git_sha="",
                       seconds=0, step=1, which="init")


@pytest.mark.parametrize("field,value", [
    ("rung", "sort5"), ("family", "olmo13b"), ("items_sha256", "0" * 64), ("n", 499),
    ("max_new_tokens", 12), ("n_shots", 0), ("dtype", "float32"), ("batch_size", 8),
    ("render", "bos"), ("answer_type", "word"), ("prereg_tag", "other"),
    ("correct", 500), ("commit", "main"), ("revision", "main"),
    ("weight_sha256", "other"), ("weight_sha256", ""), ("repo", "x/y"),
    ("kind", "thin-loader"), ("predictor_sha256", "0" * 64),
    ("host_sha256", "0" * 64), ("step", 2000), ("endpoint_sha256", "0" * 64),
])
def test_every_pinned_field_of_a_unit_record_is_measured(cap, field, value):
    rec, load, _ = _unit(cap, **{field: value})
    assert _unit_failures(rec, load, cap), field


def test_the_bits_are_rederived_from_the_continuations(cap):
    rec, load, _ = _unit(cap)
    rec["bits"][1] = 1                                   # a bit flipped to a success
    rec["correct"] = 500
    bad = _unit_failures(rec, load, cap)
    assert any("do not re-derive" in b for b in bad)
    rec, load, _ = _unit(cap)
    rec["continuations"] = rec["continuations"][:499]
    assert any("500 long" in b for b in _unit_failures(rec, load, cap))
    rec, load, _ = _unit(cap)
    rec["continuations"][0] = None
    assert any("not a string" in b for b in _unit_failures(rec, load, cap))


@pytest.mark.parametrize("field,value,match", [
    ("family", "olmo13b", "family"), ("key", 2000, "key"), ("repo", "x/y", "repo"),
    ("revision", "main", "revision"), ("commit", "main", "commit"),
    ("dtype", "float32", "dtype"), ("digest", "", "digest"),
    ("host_sha256", "0" * 64, "host"), ("n_nonfinite_logits", None, "finiteness"),
    ("loading_info", {"missing_keys": 3}, "mismatches"),
    ("sha256", {}, "manifest"),
])
def test_every_field_of_a_load_record_is_measured(cap, field, value, match):
    rec, load, entry = _unit(cap)
    load = dict(load, **{field: value})
    bad = r6.load_record_failures(load, family="olmo7b", key=1000, entry=entry,
                                  host_sha256="h" * 64)
    assert bad and any(match in b for b in bad), bad


def test_a_twin_carries_its_seed_and_comma_its_stop_id(cap):
    from experiments.exp2n import battery_2n as bn
    man = fm.manifest("comma_7b")
    e = fm.entry("comma_7b", man, fm.INIT)
    info = {"tensor_digest": "dg", "seed": e["seed"],
            "generation_eos_token_id": bn.EOS_STOP_ID_2N, "config_eos_token_id": 2}
    load = r6.load_record(family="comma_7b", key="init", entry=e, info=info,
                          device="cuda", host_sha256="h", seconds=1, n_nonfinite=0)
    assert r6.load_record_failures(load, family="comma_7b", key="init", entry=e) == []
    assert any("twin seed" in b for b in r6.load_record_failures(
        dict(load, seed=1), family="comma_7b", key="init", entry=e))
    assert any("stop id" in b for b in r6.load_record_failures(
        dict(load, generation_eos_token_id=2), family="comma_7b", key="init", entry=e))


def test_composite_sha_is_order_free_and_content_bound():
    a = r6.composite_sha({"x": "1", "y": "2"})
    assert a == r6.composite_sha({"y": "2", "x": "1"})
    assert a != r6.composite_sha({"x": "1", "y": "3"})
    assert a != r6.composite_sha({"x": "1", "z": "2"})
