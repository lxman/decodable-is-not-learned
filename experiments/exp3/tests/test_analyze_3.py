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
from pathlib import Path

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


# ---------------------------------------- the §5 statistic (Open item 3,
# amended at the freeze — ledger 2026-08-16)
#
# s_i = m_i(a_i[0]) − mean over the answer's INTERIOR characters
# a_i[1..L−2] (multiplicity kept; the last character — the echo target —
# read on neither side); exact one-sided sign test across items, ties
# dropped and disclosed. The w̃ cross-item form this replaced credited
# set-level lexical priming as signal (the freeze's class-defect
# finding); the kill fixtures below pin each degenerate by name.

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
    """Answer "abz": the statistic reads m(a) against the interior mean
    — here just m(b) — and never m(z). Signs by hand:
    .5−.1=+.4 | .2−.3=−.1 | .4−.4=0 tie | .6−.2=+.4."""
    answers = ["abz", "abq", "ady", "bez"]
    items = [mitem("a", a=0.5, b=0.1),   # s = .4
             mitem("a", a=0.2, b=0.3),   # s = -.1
             mitem("a", a=0.4, d=0.4),   # s = 0, tie
             mitem("b", b=0.6, e=0.2)]   # s = .4
    got = a.rung_sign_test(items, answers, n_tests=1)
    assert got["computable"] is True
    assert got["K"] == 2 and got["n_eff"] == 3 and got["n_ties"] == 1
    # p = P(X >= 2 | n=3, .5) = 4/8
    assert got["p"] == pytest.approx(0.5)
    assert got["significant"] is False


def test_sign_statistic_interior_mean_is_position_weighted():
    """Interior multiplicity is kept: answer "abbcz" has interior "bbc",
    so comp = (2·m(b) + m(c))/3. With m(a)=.15, m(b)=0, m(c)=.3 that is
    .1 → s = +.05; a de-duplicated interior would give .15 → a tie —
    the multiset IS the exchangeable object, and dropping repeats
    changes the answer."""
    got = a.rung_sign_test([mitem("a", a=0.15, b=0.0, c=0.3)],
                           ["abbcz"], n_tests=1)
    assert got["K"] == 1 and got["n_eff"] == 1 and got["n_ties"] == 0


def test_lexical_primer_ties_out_by_construction():
    """THE freeze finding's kill fixture: a set-level lexical primer —
    base mass everywhere, one flat boost on every character present in
    the item's string, position-blind — cancels algebraically: every
    character the statistic reads carries base + boost, so s_i = 0
    exactly on every item. The w̃ statistic this replaced scored the
    same world K=n, p ≈ 1e-151 at n=500 (ledger 2026-08-16)."""
    answers = ["gfedcba", "mlkjihg", "trqponm", "zyxwvut"]
    items = []
    for ans in answers:
        boosted = {c: (0.005 + (0.04 if c in set(ans) else 0.0))
                   for c in "abcdefghijklmnopqrstuvwxyz"}
        items.append(dict(mitem(ans[0], **boosted),
                          label_mass=boosted[ans[0]]))
    got = a.rung_sign_test(items, answers, n_tests=4)
    assert got["computable"] is True
    assert got["n_eff"] == 0 and got["n_ties"] == 4
    assert got["p"] == 1.0 and got["significant"] is False


def test_echo_mass_is_read_on_neither_side():
    """The echo character (the answer's LAST character = the input's
    first) is excluded from the statistic entirely: a pure echo model —
    all its letter mass on ans[-1] — produces exact ties, not negative
    signs. An implementation that lets ans[-1] into the competitor set
    turns these into n_eff=4 all-negative and fails this fixture."""
    answers = ["gfedcba", "nmlkjih", "utsrqpo", "zyxwvcb"]
    items = [mitem(ans[0], **{ans[-1]: 0.9}) for ans in answers]
    got = a.rung_sign_test(items, answers, n_tests=1)
    assert got["n_ties"] == 4 and got["n_eff"] == 0
    assert got["significant"] is False


def test_item_independent_prior_balances_on_rotation_closed_answers():
    """Anti-concentration kill: under ANY item-independent letter prior
    the signs over a rotation-closed answer set telescope to zero sum —
    they cannot all be positive. Rotations of "abc" with f(a) > f(b) >
    f(c): s = f(a)−f(b) > 0, f(b)−f(c) > 0, f(c)−f(a) < 0 → K=2 of 3,
    p = .5. (The distributional guarantee is θ = .5 exactly by position
    exchangeability; this pins the mechanism on a hand-checkable set.)"""
    f = {"a": 0.5, "b": 0.3, "c": 0.1}
    answers = ["abc", "bca", "cab"]
    items = [mitem(ans[0], **f) for ans in answers]
    got = a.rung_sign_test(items, answers, n_tests=1)
    assert got["K"] == 2 and got["n_eff"] == 3
    assert got["p"] == pytest.approx(0.5)
    assert got["significant"] is False


def test_sign_test_exact_binomial_tail_and_significance():
    """K=18 of N=20 → p = 211/2^20 ≈ 2.01e-4, significant at n_tests=4;
    K=14 of N=20 → p ≈ .0577, not significant even at n_tests=1.
    Positives put mass on the answer's first character; negatives put
    the same mass on its (single) interior character instead."""
    answers = [c + "xq" for c in "abcdefghij"] * 2   # interior = "x"
    strong = [mitem(y[0], **{y[0]: 0.5}) for y in answers]
    for it in strong[:2]:   # two negatives: mass on the interior char
        it["letters"][it["label_char"]] = 0.0
        it["letters"]["x"] = 0.5
        it["label_mass"] = 0.0
    got = a.rung_sign_test(strong, answers, n_tests=4)
    assert got["K"] == 18 and got["n_eff"] == 20
    assert got["p"] == pytest.approx(211 / 2 ** 20)
    assert got["significant"] is True

    weak = [mitem(y[0], **{y[0]: 0.5}) for y in answers]
    for it in weak[:6]:
        it["letters"][it["label_char"]] = 0.0
        it["letters"]["x"] = 0.5
        it["label_mass"] = 0.0
    got = a.rung_sign_test(weak, answers, n_tests=1)
    assert got["K"] == 14
    assert got["p"] == pytest.approx(60460 / 2 ** 20)
    assert got["significant"] is False


def test_sign_test_bonferroni_uses_n_tests():
    """K=16 of N=20 → p ≈ .0059: significant at n_tests=1, NOT at the
    adjudicated n_tests=4 — the correction must actually be applied."""
    answers = [c + "xq" for c in "abcdefghij"] * 2
    items = [mitem(y[0], **{y[0]: 0.5}) for y in answers]
    for it in items[:4]:
        it["letters"][it["label_char"]] = 0.0
        it["letters"]["x"] = 0.5
        it["label_mass"] = 0.0
    assert a.rung_sign_test(items, answers, n_tests=1)["significant"] is True
    assert a.rung_sign_test(items, answers, n_tests=4)["significant"] is False


def test_format_only_emitter_ties_out_by_construction():
    """The §2.2 kill test, still exact under the interior form: mass
    spread indifferently over the letters gives s_i = u − u = 0 on
    every item — all ties, n_eff = 0, and the ledgered all-ties reading
    (significant=False, p=1.0) applies."""
    answers = [c + "xq" for c in "abcdefghij"] * 2
    items = [mitem(y[0], uniform=1.0 / 26) for y in answers]
    got = a.rung_sign_test(items, answers, n_tests=4)
    assert got["computable"] is True
    assert got["n_eff"] == 0 and got["n_ties"] == 20
    assert got["p"] == 1.0
    assert got["significant"] is False


def test_sub_epsilon_signals_are_ties():
    """SIGN_TIE_EPS both directions: a 1e-13 'signal' is float dust and
    must count as a tie, never as a sign — dust-signed items counted
    into K alongside a shrunken n_eff would manufacture significance
    from nothing."""
    answers = ["axq", "bxq", "ayq", "byq"]
    items = [mitem("a", a=1e-13),
             mitem("b", b=0.3),
             mitem("a", a=1e-13),
             mitem("b", y=0.3)]           # mass on the interior char
    got = a.rung_sign_test(items, answers, n_tests=1)
    assert got["K"] == 1 and got["n_ties"] == 2 and got["n_eff"] == 2
    assert got["p"] == pytest.approx(0.75)


def test_epsilon_boundary_sign_is_counted():
    """SIGN_TIE_EPS is a strict > threshold: an s_i just above it is a
    sign, not a tie. This also pins the competitor divisor — an
    implementation that slips the first character into its own
    competitor mean rescales every s_i by n/(n+1) (sign-preserving
    everywhere else) and drags this boundary item under the epsilon."""
    got = a.rung_sign_test([mitem("a", a=1.5e-12)], ["abz"], n_tests=1)
    assert got["K"] == 1 and got["n_eff"] == 1 and got["n_ties"] == 0


def test_same_first_letter_answers_are_computable():
    """The old w̃ form hard-errored when every answer shared one first
    letter (nothing to renormalize over). The interior form needs no
    cross-item distribution: such a rung is perfectly computable, and
    first-character mass still fires it."""
    answers = ["abq", "acq", "adq", "aeq"]
    items = [mitem("a", a=0.5) for _ in answers]
    got = a.rung_sign_test(items, answers, n_tests=1)
    assert got["computable"] is True
    assert got["K"] == 4 and got["n_eff"] == 4


def test_short_answers_are_structural_ties():
    """An answer of length < 3 has no interior: the item is a
    structural tie, counted in n_ties and never dropped — dropping it
    would silently shrink the cell. (No committed battery carries one;
    the rule exists so the statistic is total.)"""
    answers = ["ab", "ba", "axq"]
    items = [mitem("a", a=0.9), mitem("b", b=0.9), mitem("a", a=0.4)]
    got = a.rung_sign_test(items, answers, n_tests=1)
    assert got["n_ties"] == 2 and got["n_eff"] == 1 and got["K"] == 1


def test_digit_support_is_not_computable_and_never_significant():
    """The ledgered letter-support rule (reading 5, re-keyed at the
    freeze): clock24_d999's statistic would read digits — outside the
    stored a–z block — so the sign test records computable=False and
    can never fire; letter support stays computable."""
    answers = ["8:41 pm", "9:10 am", "7:05 pm", "8:59 am"]
    items = [mitem(y[0]) for y in answers]
    got = a.rung_sign_test(items, answers, n_tests=1)
    assert got["computable"] is False
    assert got["significant"] is False and got["p"] == 1.0
    assert got["n_eff"] == 0
    assert "a" in got["reason"] and "z" in got["reason"]

    letter_answers = ["axq", "bxq", "ayq", "byq"]
    letter_items = [mitem(y[0], **{y[0]: 0.3}) for y in letter_answers]
    assert a.rung_sign_test(letter_items, letter_answers,
                            n_tests=1)["computable"] is True


def test_interior_digits_break_computability_even_with_letter_firsts():
    """The re-keyed rule reads EVERY character the statistic touches: a
    letter-first answer with a digit interior is just as uncomputable —
    the interior mean would need masses the stored unit does not
    carry."""
    answers = ["a1q", "b2q", "c3q"]
    items = [mitem(y[0], **{y[0]: 0.3}) for y in answers]
    got = a.rung_sign_test(items, answers, n_tests=1)
    assert got["computable"] is False


def test_upper_end_credits_the_residual_to_the_correct_letter():
    """Reading 1: s_i_hi = (m_i(a_i[0]) + r_i) − the same interior
    mean. An item negative at the lower end can be positive at the
    upper end; the ends are otherwise the same statistic."""
    answers = ["abq", "bxq", "ayq", "bzq"]
    items = [mitem("a", a=0.0, b=0.1, residual=0.15),   # lo −.1, hi +.05
             mitem("b", b=0.3, x=0.0, residual=0.15),
             mitem("a", a=0.3, y=0.0, residual=0.15),
             mitem("b", b=0.3, z=0.0, residual=0.15)]
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


# ----------------------------------------- battery loaders (Open item 3)
#
# Every battery is loaded from its canonical subdirectories only, with
# 3a's discipline: anything malformed, missing, stray, or inconsistent
# with the runner's committed shape is a hard error at load, never a
# verdict. Worlds come from the full-shape maker (Open item 4's
# infrastructure), whose stored tallies are computed independently of
# the analyzer's recompute.

from experiments.exp3.tests import full_shape as fs  # noqa: E402


def edit_cell(root, kind, key, fn):
    """Load one cell record under the runner's layout, transform, rewrite."""
    rung, size, mode = key
    p = Path(root) / "results" / kind / f"{size}_{mode}" / f"{rung}.json"
    rec = json.loads(p.read_text())
    out = fn(rec)
    p.write_text(json.dumps(out))
    return p


def test_load_mass_cells_accepts_a_sound_world(tmp_path):
    cells = a.load_mass_cells(fs.write_world(tmp_path))
    assert set(cells) == set(a.MASS_CELLS) and len(cells) == 28
    c = cells[("rev_string7", "410m", "trained")]
    assert len(c["items"]) == fs.N
    it = c["items"][0]
    assert set(it["letters"]) == set(a.LETTERS)
    assert c["depth"] == 2 and c["dtype"] == "float32"


def test_load_mass_cells_rejects_a_missing_cell(tmp_path):
    fs.write_world(tmp_path)
    (tmp_path / "results" / "mass" / "2.8b_trained"
     / "ctrl_copy.json").unlink()
    with pytest.raises(FileNotFoundError, match="ctrl_copy"):
        a.load_mass_cells(tmp_path)


def test_load_mass_cells_rejects_a_stray_file(tmp_path):
    """A file the preregistered battery does not name, sitting inside a
    canonical subdirectory, is a half-copied or wrong-tree directory —
    refused, not silently ignored."""
    fs.write_world(tmp_path)
    (tmp_path / "results" / "mass" / "410m_trained"
     / "extra_rung.json").write_text("{}")
    with pytest.raises(ValueError, match="extra_rung"):
        a.load_mass_cells(tmp_path)


def test_load_mass_cells_rejects_path_content_disagreement(tmp_path):
    fs.write_world(tmp_path)
    edit_cell(tmp_path, "mass", ("rev_string7", "410m", "trained"),
              lambda rec: {**rec, "rung": "ctrl_copy"})
    with pytest.raises(ValueError, match="disagree"):
        a.load_mass_cells(tmp_path)


def test_load_mass_cells_rejects_item_count_mismatch(tmp_path):
    fs.write_world(tmp_path)
    edit_cell(tmp_path, "mass", ("rev_string7", "410m", "trained"),
              lambda rec: {**rec, "items": rec["items"][:-1]})
    with pytest.raises(ValueError, match="items"):
        a.load_mass_cells(tmp_path)


def test_load_mass_cells_rejects_a_gappy_letter_vector(tmp_path):
    fs.write_world(tmp_path)

    def gap(rec):
        del rec["items"][3]["letters"]["q"]
        return rec
    edit_cell(tmp_path, "mass", ("reverse_string", "1b", "trained"), gap)
    with pytest.raises(ValueError, match="letter"):
        a.load_mass_cells(tmp_path)


def test_load_mass_cells_rejects_negative_mass(tmp_path):
    fs.write_world(tmp_path)

    def neg(rec):
        rec["items"][0]["letters"]["a"] = -0.1
        return rec
    edit_cell(tmp_path, "mass", ("ctrl_copy", "410m", "trained"), neg)
    with pytest.raises(ValueError, match="negative"):
        a.load_mass_cells(tmp_path)


def test_load_mass_cells_rejects_masses_summing_past_one(tmp_path):
    fs.write_world(tmp_path)

    def oversum(rec):
        rec["items"][0]["letters"] = {c: 0.1 for c in
                                      "abcdefghijklmnopqrstuvwxyz"}
        rec["items"][0]["label_mass"] = 0.1
        return rec
    edit_cell(tmp_path, "mass", ("ctrl_copy", "410m", "trained"), oversum)
    with pytest.raises(ValueError, match="sum"):
        a.load_mass_cells(tmp_path)


def test_load_mass_cells_rejects_label_char_drift(tmp_path):
    """label_char must be the probe label's first character AND the
    answer's — the record cannot support m(y_i) otherwise."""
    fs.write_world(tmp_path)

    def drift(rec):
        rec["items"][0]["label_char"] = "z"
        rec["items"][0]["label_mass"] = rec["items"][0]["letters"]["z"]
        return rec
    edit_cell(tmp_path, "mass", ("rev_string7", "1b", "trained"), drift)
    with pytest.raises(ValueError, match="label"):
        a.load_mass_cells(tmp_path)


def test_load_mass_cells_rejects_label_mass_disagreement(tmp_path):
    fs.write_world(tmp_path)

    def drift(rec):
        rec["items"][0]["label_mass"] = 0.9
        return rec
    edit_cell(tmp_path, "mass", ("rev_string7", "1b", "trained"), drift)
    with pytest.raises(ValueError, match="label_mass"):
        a.load_mass_cells(tmp_path)


def test_load_mass_cells_enforces_the_depth_and_dtype_policy(tmp_path):
    """The ledgered dtype policy, executable: depth 2 / float32
    everywhere except 12b's depth-1 / float16 exception."""
    fs.write_world(tmp_path)
    edit_cell(tmp_path, "mass", ("rev_string7", "410m", "trained"),
              lambda rec: {**rec, "depth": 1,
                           "items": [{**it, "depth": 1}
                                     for it in rec["items"]]})
    with pytest.raises(ValueError, match="depth"):
        a.load_mass_cells(tmp_path)


def test_load_mass_cells_enforces_the_12b_exception(tmp_path):
    fs.write_world(tmp_path)
    edit_cell(tmp_path, "mass", ("rev_string7", "12b", "trained"),
              lambda rec: {**rec, "dtype": "float32"})
    with pytest.raises(ValueError, match="dtype"):
        a.load_mass_cells(tmp_path)


# ------------------------------------------------------ sampling loader

def test_load_sampling_cells_accepts_and_recomputes(tmp_path):
    cells = a.load_sampling_cells(fs.write_world(tmp_path))
    assert set(cells) == set(a.SAMPLING_CELLS) and len(cells) == 16
    quiet = cells[("rev_string7", "410m", "trained")]
    assert quiet["recomputed"]["full_string_total"] == 0
    assert quiet["recomputed"]["first_char_total"] == fs.FC_REV_FLOOR
    assert quiet["recomputed"]["n_draws_total"] == fs.N * 256
    assert quiet["recomputed"]["fired"] is False
    loud = cells[("ctrl_copy", "1b", "trained")]
    assert loud["recomputed"]["full_string_total"] == 600
    assert loud["recomputed"]["first_char_total"] == fs.FC_CTRL
    assert loud["recomputed"]["fired"] is True
    assert sum(loud["recomputed"]["per_item_full_string"]) == 600


def test_load_sampling_cells_refuses_stored_tally_disagreement(tmp_path):
    """The convenience tallies are recomputed from the raw draws with
    2c's verify and 3b's first_char; ANY disagreement is a refusal
    (the runner and the analyzer no longer agree on what happened)."""
    fs.write_world(tmp_path)

    def corrupt(rec):
        rec["per_seed_tallies"]["0"]["full_string"] += 1
        return rec
    edit_cell(tmp_path, "sampling", ("rev_string7", "410m", "trained"),
              corrupt)
    with pytest.raises(ValueError, match="tall"):
        a.load_sampling_cells(tmp_path)


def test_load_sampling_cells_rejects_a_missing_draws_file(tmp_path):
    fs.write_world(tmp_path)
    (tmp_path / "results" / "sampling" / "410m_trained"
     / "ctrl_copy.draws.jsonl.gz").unlink()
    with pytest.raises(FileNotFoundError, match="draws"):
        a.load_sampling_cells(tmp_path)


def test_load_sampling_cells_rejects_a_duplicate_item_row(tmp_path):
    import gzip as gz
    fs.write_world(tmp_path)
    p = (tmp_path / "results" / "sampling" / "410m_trained"
         / "ctrl_copy.draws.jsonl.gz")
    lines = gz.open(p, "rt").readlines()
    with gz.open(p, "wt") as f:
        f.writelines(lines + [lines[0]])
    with pytest.raises(ValueError, match="duplicate"):
        a.load_sampling_cells(tmp_path)


def test_load_sampling_cells_rejects_a_missing_seed_stream(tmp_path):
    import gzip as gz
    fs.write_world(tmp_path)
    p = (tmp_path / "results" / "sampling" / "410m_trained"
         / "ctrl_copy.draws.jsonl.gz")
    rows = [json.loads(x) for x in gz.open(p, "rt")]
    del rows[0]["draws"]["3"]
    with gz.open(p, "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with pytest.raises(ValueError, match="seed"):
        a.load_sampling_cells(tmp_path)


def test_load_sampling_cells_rejects_a_short_stream(tmp_path):
    import gzip as gz
    fs.write_world(tmp_path)
    p = (tmp_path / "results" / "sampling" / "1b_untrained"
         / "rev_string7.draws.jsonl.gz")
    rows = [json.loads(x) for x in gz.open(p, "rt")]
    rows[5]["draws"]["2"] = rows[5]["draws"]["2"][:-1]
    with gz.open(p, "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with pytest.raises(ValueError, match="64"):
        a.load_sampling_cells(tmp_path)


def test_load_sampling_cells_rejects_a_missing_item_row(tmp_path):
    import gzip as gz
    fs.write_world(tmp_path)
    p = (tmp_path / "results" / "sampling" / "410m_untrained"
         / "clock24_d999.draws.jsonl.gz")
    lines = gz.open(p, "rt").readlines()
    with gz.open(p, "wt") as f:
        f.writelines(lines[:-1])
    with pytest.raises(ValueError, match="row"):
        a.load_sampling_cells(tmp_path)


def test_load_sampling_cells_enforces_the_preregistered_draw_counts(tmp_path):
    """k = 256 per reversal item (4 × 64) and 32 per control item is
    §3's budget; a record claiming anything else is not this design."""
    fs.write_world(tmp_path)
    edit_cell(tmp_path, "sampling", ("rev_string7", "410m", "trained"),
              lambda rec: {**rec, "draws_per_seed": 32, "k_total": 128})
    with pytest.raises(ValueError, match="draws_per_seed"):
        a.load_sampling_cells(tmp_path)


def test_load_sampling_cells_enforces_fp32(tmp_path):
    fs.write_world(tmp_path)
    edit_cell(tmp_path, "sampling", ("rev_string7", "410m", "trained"),
              lambda rec: {**rec, "dtype": "float16"})
    with pytest.raises(ValueError, match="dtype"):
        a.load_sampling_cells(tmp_path)


# ------------------------------------------------------ redecode loader

def test_load_redecode_cells_accepts_a_sound_world(tmp_path):
    cells = a.load_redecode_cells(fs.write_world(tmp_path))
    assert set(cells) == set(a.SAMPLING_CELLS) and len(cells) == 16
    c = cells[("ctrl_copy", "410m", "trained")]
    assert len(c["continuations"]) == fs.N
    assert c["dtype"] == "float16"


def test_load_redecode_cells_rejects_a_missing_cell(tmp_path):
    fs.write_world(tmp_path)
    (tmp_path / "results" / "redecode" / "1b_trained"
     / "reverse_string.json").unlink()
    with pytest.raises(FileNotFoundError, match="reverse_string"):
        a.load_redecode_cells(tmp_path)


def test_load_redecode_cells_enforces_3bs_fp16_path(tmp_path):
    """Gate 2 must reproduce 3b's bytes, which were made at fp16 by
    generate; a float32 re-decode is not that referent's path."""
    fs.write_world(tmp_path)
    edit_cell(tmp_path, "redecode", ("ctrl_copy", "410m", "trained"),
              lambda rec: {**rec, "dtype": "float32"})
    with pytest.raises(ValueError, match="dtype"):
        a.load_redecode_cells(tmp_path)


def test_load_redecode_cells_rejects_count_mismatch(tmp_path):
    fs.write_world(tmp_path)
    edit_cell(tmp_path, "redecode", ("ctrl_copy", "410m", "trained"),
              lambda rec: {**rec,
                           "continuations": rec["continuations"][:-1]})
    with pytest.raises(ValueError, match="continuations"):
        a.load_redecode_cells(tmp_path)


def test_load_redecode_cells_rejects_twin_seed_violation(tmp_path):
    fs.write_world(tmp_path)
    edit_cell(tmp_path, "redecode", ("ctrl_copy", "410m", "untrained"),
              lambda rec: {**rec, "untrained_seed": 7})
    with pytest.raises(ValueError, match="seed"):
        a.load_redecode_cells(tmp_path)


def test_load_verify_returns_2cs_verify():
    """The fire recompute uses 2c's exact-match verify, resolved from
    the exp2c tree (provenance-asserted, run_cell's discipline)."""
    verify = a.load_verify()
    assert verify(" gfedcba\nextra", "gfedcba", "word") is True
    assert verify(" gfedcbaz", "gfedcba", "word") is False
