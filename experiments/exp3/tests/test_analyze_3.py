"""Fixture suite for the frozen Exp 3 analysis (design §5, §6, §11).

One synthetic case per preregistered provision, in both directions:
every gate has a case where it must fire and a case where it must not.
Built in the build session (doc Open item 3), re-run cold at the freeze.

Nothing here computes a mass or sampling quantity for a real cell or
model: those numbers do not exist until after the exp3-preregistered
tag. The referent-facing tests build synthetic record trees; the checks
against real committed records live in verify_referents.py.

This first section covers the referent loaders and the scoring/CP
helpers ported from 3b (doc Open item 8's surface). The statistic,
gates, and verdict tree sections are added with the analyzer build
(Open item 3) and the full-shape batteries live in full_shape.py
(Open item 4).
"""
import hashlib
import json

import pytest

from experiments.exp3 import analyze_3 as a


# ------------------------------------------------- synthetic gate-2 tree

def gate2_record(rung, size, mode, n=500, conts=None, **overrides):
    """A structurally sound 3b probe-size cell record (the gate-2 byte
    referent shape run_cell.py committed: continuations, labels, answers,
    items_sha256, max_new_tokens, model_sha, untrained_seed)."""
    rec = {
        "rung": rung, "size": size, "mode": mode, "n_items": n,
        "continuations": conts if conts is not None
        else [f" {rung[0]}xy" for _ in range(n)],
        "probe_labels": [rung[0]] * n,
        "answers": [rung[0] + "bcdefg"] * n,
        "full_string_correct": 0,
        "max_new_tokens": 12,
        "n_shots": 2,
        "untrained_seed": 0 if mode == "untrained" else None,
        "model_sha": f"sha-{size}",
        "items_sha256": f"items-{rung}",
    }
    rec.update(overrides)
    return rec


def write_gate2_tree(root, mutate=None):
    """All 16 probe-size cells under root/{size}_{mode}/{rung}.json;
    `mutate(rec) -> rec | None` edits one record (None = omit the file)."""
    target = ("rev_string7", "410m", "trained")
    for rung in a.RUNGS:
        for size in a.PROBE_SIZES:
            for mode in a.MODES:
                rec = gate2_record(rung, size, mode)
                if mutate is not None and (rung, size, mode) == target:
                    rec = mutate(rec)
                    if rec is None:
                        continue
                d = root / f"{size}_{mode}"
                d.mkdir(parents=True, exist_ok=True)
                (d / f"{rung}.json").write_text(json.dumps(rec))
    return root


def test_load_gate2_referents_accepts_a_sound_tree(tmp_path):
    refs = a.load_gate2_referents(write_gate2_tree(tmp_path))
    assert len(refs) == 16
    r = refs[("rev_string7", "410m", "trained")]
    assert len(r["continuations"]) == 500
    assert r["items_sha256"] == "items-rev_string7"
    assert r["max_new_tokens"] == 12


def test_load_gate2_referents_rejects_a_missing_cell(tmp_path):
    write_gate2_tree(tmp_path, mutate=lambda rec: None)
    with pytest.raises(FileNotFoundError, match="rev_string7/410m/trained"):
        a.load_gate2_referents(tmp_path)


def test_load_gate2_referents_rejects_count_mismatch(tmp_path):
    """A referent whose stored n disagrees with its continuations is 3a's
    valueless-input class: refused at load, never discovered mid-verdict."""
    def chop(rec):
        rec["continuations"] = rec["continuations"][:499]
        return rec
    write_gate2_tree(tmp_path, mutate=chop)
    with pytest.raises(ValueError, match="499"):
        a.load_gate2_referents(tmp_path)


def test_load_gate2_referents_rejects_path_content_disagreement(tmp_path):
    def relabel(rec):
        return {**rec, "rung": "ctrl_copy"}
    write_gate2_tree(tmp_path, mutate=relabel)
    with pytest.raises(ValueError, match="disagree"):
        a.load_gate2_referents(tmp_path)


def test_load_gate2_referents_rejects_missing_items_sha(tmp_path):
    def strip_sha(rec):
        rec.pop("items_sha256")
        return rec
    write_gate2_tree(tmp_path, mutate=strip_sha)
    with pytest.raises(ValueError, match="items_sha256"):
        a.load_gate2_referents(tmp_path)


def test_load_gate2_referents_rejects_labels_answers_length_drift(tmp_path):
    def chop_labels(rec):
        rec["probe_labels"] = rec["probe_labels"][:498]
        return rec
    write_gate2_tree(tmp_path, mutate=chop_labels)
    with pytest.raises(ValueError, match="probe_labels"):
        a.load_gate2_referents(tmp_path)


# ------------------------------------------------ items-sha agreement

def test_items_sha_referents_agree_across_a_rungs_cells(tmp_path):
    shas = a.items_sha_referents(a.load_gate2_referents(
        write_gate2_tree(tmp_path)))
    assert shas == {r: f"items-{r}" for r in a.RUNGS}


def test_items_sha_referents_reject_within_rung_disagreement(tmp_path):
    """Two cells of one rung pinning different item files means there is
    no single referent for what exp3 must load — hard error, not a pick."""
    def reseat(rec):
        return {**rec, "items_sha256": "items-DRIFTED"}
    refs = a.load_gate2_referents(write_gate2_tree(tmp_path, mutate=reseat))
    with pytest.raises(ValueError, match="rev_string7"):
        a.items_sha_referents(refs)


# ------------------------------------------------- ported scoring (3b)

def test_first_char_counts_any_non_whitespace_character():
    """3b's regression, kept: clock24_d999's label is a DIGIT. An isalpha
    filter would zero the matched control by construction."""
    assert a.first_char("  8:41 pm") == "8"
    assert a.score_first_char(" 8:41", "8")


def test_first_char_empty_is_none_and_scores_incorrect():
    assert a.first_char("   ") is None
    assert not a.score_first_char("", "a")


def test_score_cell_refuses_length_mismatch():
    with pytest.raises(ValueError, match="cannot be dropped"):
        a.score_cell(["a"], ["a", "b"])


def test_score_cell_gate1_anchor_arithmetic():
    """497/500 is the committed 3b ctrl_copy first-char count; the port
    must reproduce .9940 from a 497-correct synthetic cell."""
    conts = [" c"] * 497 + [" z"] * 3
    got = a.score_cell(conts, ["c"] * 500)
    assert got["correct"] == 497
    assert got["acc"] == pytest.approx(0.9940)


# ------------------------------------------------------- CP helpers

def test_cp_upper_zero_matches_the_closed_form():
    """0/128,000 at one-sided .95 is the doc's ≈2.3e-5 WALL bound."""
    n = 128_000
    assert a.cp_upper(0, n) == pytest.approx(1 - 0.05 ** (1 / n), rel=1e-6)
    assert a.cp_upper(0, n) == pytest.approx(2.34e-5, rel=0.01)


def test_cp_upper_grows_with_successes():
    assert a.cp_upper(5, 1000) > a.cp_upper(0, 1000)


def test_clopper_pearson_zero_lower_bound_is_zero():
    lo, hi = a.clopper_pearson(0, 500)
    assert lo == 0.0
    assert 0 < hi < 0.02


def test_clopper_pearson_level_widens_the_gate3_interval():
    """Gate 3 tests at two-sided level 1 − .01/16; that interval must be
    wider than the reporting 95% one or the Bonferroni is fictional."""
    lo95, hi95 = a.clopper_pearson(50, 16_000, level=0.95)
    lo3, hi3 = a.clopper_pearson(50, 16_000, level=1 - a.ALPHA / a.N_COHERENCE_TESTS)
    assert lo3 < lo95 and hi3 > hi95


# ------------------------------------------------------- probe margins

def margins_file(tmp_path, v410=0.62634, v1b=0.77251,
                 r410=0.57312, r1b=0.67489):
    p = tmp_path / "probe_margins.json"
    p.write_text(json.dumps({
        "rev_string7": {"410m": {"mean": v410}, "1b": {"mean": v1b}},
        "reverse_string": {"410m": {"mean": r410}, "1b": {"mean": r1b}}}))
    return p


def test_load_probe_margins_accepts_the_committed_values(tmp_path):
    m = a.load_probe_margins(margins_file(tmp_path))
    assert m["rev_string7"]["410m"] == pytest.approx(0.62634)


def test_load_probe_margins_rejects_drift_from_the_design_doc(tmp_path):
    """The doc quotes .6263/.7725/.5731/.6749; a margins file that rounds
    elsewhere is not the file the design was written against."""
    with pytest.raises(ValueError, match="design"):
        a.load_probe_margins(margins_file(tmp_path, v410=0.61))


# ---------------------------------------------- twin hash referents (3b)

def twin_check_file(tmp_path, drop_size=None):
    checks = [{"check": f"untrained twin constructs {s} seed=0",
               "ok": True, "state_sha256": f"hash-{s}", "deterministic": True}
              for s in a.PROBE_SIZES if s != drop_size]
    p = tmp_path / "referent_check.json"
    p.write_text(json.dumps({"all_ok": True, "checks": checks}))
    return p


def test_load_twin_hash_referents_extracts_both_sizes(tmp_path):
    got = a.load_twin_hash_referents(twin_check_file(tmp_path))
    assert got == {"410m": "hash-410m", "1b": "hash-1b"}


def test_load_twin_hash_referents_rejects_a_missing_size(tmp_path):
    """A twin referent with no recorded hash is a valueless input (3a's
    class): the seed-0 construction check would have nothing to equal."""
    with pytest.raises(ValueError, match="1b"):
        a.load_twin_hash_referents(twin_check_file(tmp_path, drop_size="1b"))


# ------------------------------------------------------------- floors

def synth_floor_pair(tmp_path, break_sha=False, break_items=False):
    """A floors file + items tree that agree (or deliberately do not)."""
    items = [{"answer": c + "bcdefg",
              "question": f"Spell the string 'z{c}works' backwards.",
              "probe_label": c}
             for c in ("abcdefghijklmnopqrstuvwxy" + "z") * 20 for c in [c]]
    items = items[:500]
    cap_root = tmp_path / "items"
    cap_root.mkdir()
    for rung in a.RUNGS:
        (cap_root / f"{rung}.json").write_text(
            json.dumps({"eval_items": items}))
    floors = {r: a.chance_floors(items) for r in a.RUNGS}
    fp = tmp_path / "floors.json"
    fp.write_text(json.dumps(floors))
    sha = hashlib.sha256(fp.read_bytes()).hexdigest()
    if break_sha:
        fp.write_text(json.dumps(floors) + " ")
    if break_items:
        drifted = [{**it, "answer": "qqqqqqq"} for it in items]
        for rung in a.RUNGS:
            (cap_root / f"{rung}.json").write_text(
                json.dumps({"eval_items": drifted}))
    loader = lambda rung: json.loads(  # noqa: E731
        (cap_root / f"{rung}.json").read_text())["eval_items"]
    return fp, sha, loader


def test_load_floors_accepts_a_consistent_pair(tmp_path):
    fp, sha, loader = synth_floor_pair(tmp_path)
    floors = a.load_floors(fp, expected_sha=sha, items_loader=loader)
    assert set(floors) == set(a.RUNGS)


def test_load_floors_rejects_sha_drift(tmp_path):
    fp, sha, loader = synth_floor_pair(tmp_path, break_sha=True)
    with pytest.raises(ValueError, match="sha"):
        a.load_floors(fp, expected_sha=sha, items_loader=loader)


def test_load_floors_rejects_items_drift(tmp_path):
    fp, sha, loader = synth_floor_pair(tmp_path, break_items=True)
    with pytest.raises(ValueError, match="recompute"):
        a.load_floors(fp, expected_sha=sha, items_loader=loader)


# ---------------------------------------- the §5 statistic (Open item 3)
#
# s_i = m_i(y_i) − Σ_{c≠y_i} w̃_c m_i(c), w̃ the empirical answer-first-
# letter distribution renormalized per item to exclude y_i; exact
# one-sided sign test across items, ties dropped and disclosed.

def mitem(label, residual=0.0, uniform=None, **letter_masses):
    """A per-item mass record in masses.py's stored shape."""
    letters = {c: 0.0 for c in "abcdefghijklmnopqrstuvwxyz"}
    if uniform is not None:
        letters = {c: uniform for c in letters}
    for c, v in letter_masses.items():
        letters[c] = v
    lc = str(label)[0].casefold()
    return {"letters": letters, "extra": {},
            "label_char": lc,
            "label_mass": letters.get(lc, 0.0),
            "residual": residual, "ws_mass_p1": residual,
            "terminal_mass": 0.0}


def test_sign_statistic_hand_computed_case():
    """Support {a: .75, b: .25}. For a y=a item, w̃ = {b: 1.0}, so
    s = m(a) − m(b); for the y=b item, w̃ = {a: 1.0}, s = m(b) − m(a)."""
    answers = ["ax", "ay", "az", "bq"]
    items = [mitem("a", a=0.5, b=0.1),   # s = .4
             mitem("a", a=0.2, b=0.3),   # s = -.1
             mitem("a", a=0.4, b=0.4),   # s = 0, tie
             mitem("b", b=0.6, a=0.2)]   # s = .4
    got = a.rung_sign_test(items, answers, n_tests=1)
    assert got["computable"] is True
    assert got["K"] == 2 and got["n_eff"] == 3 and got["n_ties"] == 1
    # p = P(X >= 2 | n=3, .5) = 4/8
    assert got["p"] == pytest.approx(0.5)
    assert got["significant"] is False


def test_sign_test_exact_binomial_tail_and_significance():
    """K=18 of N=20 → p = 211/2^20 ≈ 2.01e-4, significant at n_tests=4;
    K=14 of N=20 → p ≈ .0577, not significant even at n_tests=1."""
    answers = [c + "x" for c in "abcdefghij"] * 2
    strong = [mitem(y[0], **{y[0]: 0.5}) for y in answers]
    for it in strong[:2]:   # two negatives: mass on a competitor instead
        it["letters"][it["label_char"]] = 0.0
        other = "a" if it["label_char"] != "a" else "b"
        it["letters"][other] = 0.5
        it["label_mass"] = 0.0
    got = a.rung_sign_test(strong, answers, n_tests=4)
    assert got["K"] == 18 and got["n_eff"] == 20
    assert got["p"] == pytest.approx(211 / 2 ** 20)
    assert got["significant"] is True

    weak = [mitem(y[0], **{y[0]: 0.5}) for y in answers]
    for it in weak[:6]:
        it["letters"][it["label_char"]] = 0.0
        other = "a" if it["label_char"] != "a" else "b"
        it["letters"][other] = 0.5
        it["label_mass"] = 0.0
    got = a.rung_sign_test(weak, answers, n_tests=1)
    assert got["K"] == 14
    assert got["p"] == pytest.approx(60460 / 2 ** 20)
    assert got["significant"] is False


def test_sign_test_bonferroni_uses_n_tests():
    """K=16 of N=20 → p ≈ .0059: significant at n_tests=1, NOT at the
    adjudicated n_tests=4 — the correction must actually be applied."""
    answers = [c + "x" for c in "abcdefghij"] * 2
    items = [mitem(y[0], **{y[0]: 0.5}) for y in answers]
    for it in items[:4]:
        it["letters"][it["label_char"]] = 0.0
        other = "a" if it["label_char"] != "a" else "b"
        it["letters"][other] = 0.5
        it["label_mass"] = 0.0
    assert a.rung_sign_test(items, answers, n_tests=1)["significant"] is True
    assert a.rung_sign_test(items, answers, n_tests=4)["significant"] is False


def test_format_only_emitter_ties_out_by_construction():
    """The §2.2 kill test: mass spread indifferently over the letters
    gives s_i = m − m·Σw̃ = 0 exactly — all ties, n_eff = 0, and the
    ledgered all-ties reading (significant=False, p=1.0) applies."""
    answers = [c + "x" for c in "abcdefghij"] * 2
    items = [mitem(y[0], uniform=1.0 / 26) for y in answers]
    got = a.rung_sign_test(items, answers, n_tests=4)
    assert got["computable"] is True
    assert got["n_eff"] == 0 and got["n_ties"] == 20
    assert got["p"] == 1.0
    assert got["significant"] is False


def test_single_letter_support_is_a_hard_error():
    """w_y = 1 leaves nothing to renormalize over: a rung whose answers
    all share one first letter cannot carry this statistic (guard, not
    a silent zero)."""
    answers = ["ax", "ay", "az"]
    items = [mitem("a", a=0.5) for _ in answers]
    with pytest.raises(ValueError, match="renormaliz"):
        a.rung_sign_test(items, answers, n_tests=1)


def test_digit_support_is_not_computable_and_never_significant():
    """The ledgered letter-support rule (reading 5): clock24_d999's
    answers begin with digits, outside the stored a–z block — the sign
    test records computable=False and can never fire; letter support
    stays computable."""
    answers = ["8:41 pm", "9:10 am", "7:05 pm", "8:59 am"]
    items = [mitem(y[0]) for y in answers]
    got = a.rung_sign_test(items, answers, n_tests=1)
    assert got["computable"] is False
    assert got["significant"] is False and got["p"] == 1.0
    assert got["n_eff"] == 0
    assert "a" in got["reason"] and "z" in got["reason"]

    letter_answers = ["ax", "bx", "ay", "by"]
    letter_items = [mitem(y[0], **{y[0]: 0.3}) for y in letter_answers]
    assert a.rung_sign_test(letter_items, letter_answers,
                            n_tests=1)["computable"] is True


def test_upper_end_credits_the_residual_to_the_correct_letter():
    """Reading 1: s_i_hi = (m_i(y_i) + r_i) − Σ w̃_c m_i(c). An item
    negative at the lower end can be positive at the upper end; the
    ends are otherwise the same statistic."""
    answers = ["ax", "bx", "ay", "by"]
    items = [mitem("a", a=0.0, b=0.1, residual=0.15),   # lo −.1, hi +.05
             mitem("b", b=0.3, a=0.0, residual=0.15),
             mitem("a", a=0.3, b=0.0, residual=0.15),
             mitem("b", b=0.3, a=0.0, residual=0.15)]
    lo = a.rung_sign_test(items, answers, n_tests=1)
    hi = a.rung_sign_test(items, answers, n_tests=1, upper=True)
    assert lo["K"] == 3 and hi["K"] == 4
    assert lo["end"] == "lower" and hi["end"] == "upper"


def test_sign_test_refuses_item_answer_length_mismatch():
    with pytest.raises(ValueError, match="items"):
        a.rung_sign_test([mitem("a", a=0.5)], ["ax", "bx"], n_tests=1)


def test_cell_mass_bracket_is_the_mean_over_items():
    """Reading 9: the gate-3 bracket is [mean label mass,
    mean(label mass + residual)] — and it must read label_mass, not the
    letter block, so the digit-label control carries a bracket too."""
    items = [mitem("a", a=0.2, residual=0.1),
             mitem("b", b=0.4, residual=0.3)]
    lo, hi = a.cell_mass_bracket(items)
    assert lo == pytest.approx(0.3)
    assert hi == pytest.approx(0.5)

    digit = [dict(mitem("8"), label_mass=0.4),
             dict(mitem("9"), label_mass=0.2)]
    lo, hi = a.cell_mass_bracket(digit)
    assert lo == pytest.approx(0.3) and hi == pytest.approx(0.3)
