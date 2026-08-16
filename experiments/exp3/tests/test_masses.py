"""Fixtures for the mass module (design §5, doc Open item 1): synthetic
distributions with hand-computable answers, both directions per
provision.

The synthetic vocabulary below is chosen to pin every classification
edge the real tokenizer presents: leading-space letter tokens (' a'),
uppercase ('A' casefolds into 'a'), pure whitespace (' ', '\\n'),
empty decodes (position-1 mass that defers the first visible
character), non-breaking space (Python str whitespace — must classify
exactly as first_char strips it), a digit token (clock24_d999's label
space), and a non-alphanumeric printable ('?').

No real model or tokenizer is touched anywhere in this file.
"""
import pytest

from experiments.exp3 import analyze_3 as a
from experiments.exp3 import masses as m

#           0     1    2    3    4     5   6     7     8       9
DECODED = (" a", "b", "A", " ", "\n", "", " 8", "zz", "\xa0", "?")


def probs(**by_id):
    p = [0.0] * len(DECODED)
    for k, v in by_id.items():
        p[int(k[1:])] = v
    return p


# ------------------------------------------------------ classification

def test_token_classes_route_through_first_char():
    """One whitespace/casefold definition for the whole experiment: the
    class of a token IS first_char of its decode. None = whitespace-path
    (deferred first character), everything else the character itself."""
    fc = m.token_first_chars(DECODED)
    assert fc == ["a", "b", "a", None, None, None, "8", "z", None, "?"]
    assert m.whitespace_ids(fc) == (3, 4, 5, 8)


def test_token_classes_agree_with_first_char_on_every_entry():
    for text, cls in zip(DECODED, m.token_first_chars(DECODED)):
        assert cls == a.first_char(text)


# ------------------------------------------------------ depth-1 masses

def test_depth1_masses_sum_by_class_with_casefold():
    p1 = probs(t0=0.2, t1=0.1, t2=0.05, t6=0.15, t7=0.3, t9=0.2)
    fc = m.token_first_chars(DECODED)
    got = m.depth2_masses(p1, fc, m.whitespace_ids(fc), {},
                          chars=("a", "b", "z", "8"))
    assert got["mass"]["a"] == pytest.approx(0.25)   # ' a' + 'A'
    assert got["mass"]["b"] == pytest.approx(0.10)
    assert got["mass"]["z"] == pytest.approx(0.30)
    assert got["mass"]["8"] == pytest.approx(0.15)
    assert got["residual"] == pytest.approx(0.0)
    assert got["ws_mass_p1"] == pytest.approx(0.0)


def test_untracked_chars_report_zero_not_error():
    p1 = probs(t1=1.0)
    fc = m.token_first_chars(DECODED)
    got = m.depth2_masses(p1, fc, m.whitespace_ids(fc), {}, chars=("q",))
    assert got["mass"]["q"] == 0.0


# ------------------------------------------------------ depth-2 masses

def test_depth2_expands_whitespace_paths_and_leaves_residual():
    """Hand-computed: P(' ')=0.3 routes 0.5 to 'a', 0.3 to 'z', 0.2 to
    whitespace again (residual); P('\\n')=0.1 routes 1.0 to 'b'."""
    p1 = probs(t0=0.1, t3=0.3, t4=0.1, t7=0.2, t9=0.3)
    fc = m.token_first_chars(DECODED)
    p2 = {3: probs(t0=0.5, t3=0.2, t7=0.3),
          4: probs(t1=1.0)}
    got = m.depth2_masses(p1, fc, m.whitespace_ids(fc), p2,
                          chars=("a", "b", "z"))
    assert got["mass"]["a"] == pytest.approx(0.1 + 0.3 * 0.5)
    assert got["mass"]["b"] == pytest.approx(0.1 * 1.0)
    assert got["mass"]["z"] == pytest.approx(0.2 + 0.3 * 0.3)
    assert got["residual"] == pytest.approx(0.3 * 0.2)
    assert got["ws_mass_p1"] == pytest.approx(0.4)


def test_nonbreaking_space_is_a_whitespace_path():
    """'\\xa0' strips under Python str whitespace — the mass side must
    treat it exactly as first_char does, or the two instruments measure
    different distributions and gate 3 fires on a self-inflicted drift."""
    p1 = probs(t8=1.0)
    fc = m.token_first_chars(DECODED)
    p2 = {8: probs(t1=1.0)}
    got = m.depth2_masses(p1, fc, m.whitespace_ids(fc), p2, chars=("b",))
    assert got["mass"]["b"] == pytest.approx(1.0)


def test_empty_decode_is_a_whitespace_path():
    p1 = probs(t5=1.0)
    fc = m.token_first_chars(DECODED)
    p2 = {5: probs(t7=1.0)}
    got = m.depth2_masses(p1, fc, m.whitespace_ids(fc), p2, chars=("z",))
    assert got["mass"]["z"] == pytest.approx(1.0)
    assert got["residual"] == pytest.approx(0.0)


# ------------------------------------------------- malformed inputs

def test_missing_probs2_for_a_live_whitespace_token_is_refused():
    """A whitespace token carrying position-1 mass with no depth-2
    distribution is a valueless input (3a's class): the mass would be
    silently undercounted into the residual's blind spot."""
    p1 = probs(t3=0.5, t1=0.5)
    fc = m.token_first_chars(DECODED)
    with pytest.raises(ValueError, match="no depth-2 distribution"):
        m.depth2_masses(p1, fc, m.whitespace_ids(fc), {}, chars=("b",))


def test_zero_mass_whitespace_token_needs_no_probs2():
    p1 = probs(t1=1.0)
    fc = m.token_first_chars(DECODED)
    got = m.depth2_masses(p1, fc, m.whitespace_ids(fc), {}, chars=("b",))
    assert got["mass"]["b"] == pytest.approx(1.0)


def test_position1_distribution_must_sum_to_one():
    p1 = probs(t1=0.5)
    fc = m.token_first_chars(DECODED)
    with pytest.raises(ValueError, match="sums to"):
        m.depth2_masses(p1, fc, m.whitespace_ids(fc), {}, chars=("b",))


def test_negative_probability_is_refused():
    p1 = probs(t1=1.2, t7=-0.2)
    fc = m.token_first_chars(DECODED)
    with pytest.raises(ValueError, match="negative"):
        m.depth2_masses(p1, fc, m.whitespace_ids(fc), {}, chars=("b",))


def test_depth2_row_must_sum_to_one():
    p1 = probs(t3=1.0)
    fc = m.token_first_chars(DECODED)
    p2 = {3: probs(t1=0.4)}
    with pytest.raises(ValueError, match="sums to"):
        m.depth2_masses(p1, fc, m.whitespace_ids(fc), p2, chars=("b",))


def test_length_mismatch_between_probs_and_classes_is_refused():
    fc = m.token_first_chars(DECODED)
    with pytest.raises(ValueError, match="classes"):
        m.depth2_masses([1.0], fc, m.whitespace_ids(fc), {}, chars=("a",))


# ---------------------------------------------------- terminal (eos/pad)

def test_terminal_mass_is_disclosed_not_expanded():
    """Special ids (eos/pad) decode to '' but are NOT whitespace-path:
    the sampled channel stops at EOS, so no character ever follows.
    Routing their mass through depth 2 would credit letter paths
    sampling cannot realize — a gate-3 incoherence manufactured by the
    instrument's own bookkeeping. Terminal mass is its own bucket."""
    p1 = probs(t5=0.4, t1=0.6)
    fc = m.token_first_chars(DECODED)
    ws = tuple(i for i in m.whitespace_ids(fc) if i != 5)
    got = m.depth2_masses(p1, fc, ws, {}, chars=("b",), terminal_ids=(5,))
    assert got["mass"]["b"] == pytest.approx(0.6)
    assert got["terminal_mass"] == pytest.approx(0.4)
    assert got["residual"] == pytest.approx(0.0)


def test_terminal_id_needs_no_depth2_row():
    p1 = probs(t5=1.0)
    fc = m.token_first_chars(DECODED)
    ws = tuple(i for i in m.whitespace_ids(fc) if i != 5)
    got = m.depth2_masses(p1, fc, ws, {}, chars=("b",), terminal_ids=(5,))
    assert got["terminal_mass"] == pytest.approx(1.0)


def test_depth2_landing_on_a_terminal_id_is_terminal_not_residual():
    """' ' then EOS: the channel ends after whitespace — determined (no
    character), not undetermined (residual)."""
    p1 = probs(t3=1.0)
    fc = m.token_first_chars(DECODED)
    ws = tuple(i for i in m.whitespace_ids(fc) if i != 5)
    p2 = {3: probs(t5=0.7, t1=0.3)}
    got = m.depth2_masses(p1, fc, ws, p2, chars=("b",), terminal_ids=(5,))
    assert got["mass"]["b"] == pytest.approx(0.3)
    assert got["terminal_mass"] == pytest.approx(0.7)
    assert got["residual"] == pytest.approx(0.0)


# ------------------------------------------------- conservation checks

def test_tracked_mass_plus_residual_never_exceeds_one():
    p1 = probs(t0=0.5, t3=0.5)
    fc = m.token_first_chars(DECODED)
    p2 = {3: probs(t0=0.6, t3=0.4)}
    got = m.depth2_masses(p1, fc, m.whitespace_ids(fc), p2,
                          chars=tuple("abz8") + ("?",))
    total = sum(got["mass"].values()) + got["residual"]
    assert total <= 1.0 + 1e-9
    assert got["mass"]["a"] == pytest.approx(0.5 + 0.5 * 0.6)
    assert got["residual"] == pytest.approx(0.5 * 0.4)


def test_item_record_carries_the_26_letter_vector_and_label_mass():
    """§5: the a–z vector is stored per item, and the label's own mass —
    also for a digit label, where the vector alone would lose it."""
    p1 = probs(t0=0.3, t6=0.6, t1=0.1)
    fc = m.token_first_chars(DECODED)
    rec = m.item_mass_record(p1, fc, m.whitespace_ids(fc), {},
                             label="8")
    assert set(rec["letters"]) == set("abcdefghijklmnopqrstuvwxyz")
    assert rec["letters"]["a"] == pytest.approx(0.3)
    assert rec["label_char"] == "8"
    assert rec["label_mass"] == pytest.approx(0.6)
    assert rec["extra"]["8"] == pytest.approx(0.6)
    assert rec["residual"] == pytest.approx(0.0)


def test_item_record_letter_label_reads_from_the_vector():
    p1 = probs(t7=0.8, t1=0.2)
    fc = m.token_first_chars(DECODED)
    rec = m.item_mass_record(p1, fc, m.whitespace_ids(fc), {}, label="z")
    assert rec["label_mass"] == pytest.approx(0.8)
    assert rec["extra"] == {}
