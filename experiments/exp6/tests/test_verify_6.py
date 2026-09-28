# experiments/exp6/tests/test_verify_6.py
import random
import string

import pytest

from experiments.exp6 import verify_6 as v6


def test_types_and_budgets_are_pinned():
    assert v6.ANSWER_TYPES_6 == ("number", "word", "span", "ipa", "sequence")
    assert v6.MAX_NEW_TOKENS_6 == {"number": 8, "word": 12, "span": 12,
                                   "ipa": 24, "sequence": 16}


def test_number_and_word_are_2c_verbatim():
    h = v6.harness_2c()
    for text in (" 1,234 apples", "-332\n\nQ: next", "The answer is 7.",
                 " Gulf\nQ:", "'owl'.", "  red book  "):
        for at in ("number", "word"):
            assert v6.normalize_6(text, at) == h.normalize_answer(text, at)


def test_whole_line_types_compare_the_whole_first_line():
    assert v6.normalize_6(" Apparel  cabinets\tmark\nQ: x", "sequence") == \
        "apparel cabinets mark"
    assert v6.normalize_6(' "6pm to 9pm".', "span") == "6pm to 9pm"
    assert v6.verify_6(" 6pm to 9pm\n\nQ:", "6pm to 9pm", "span")
    assert not v6.verify_6(" 6pm to 8pm", "6pm to 9pm", "span")
    assert not v6.verify_6(" apparel cabinets", "apparel cabinets mark", "sequence")


def test_ipa_keeps_case_and_reads_one_token():
    assert v6.normalize_6(" ˈbətən and more\nQ:", "ipa") == "ˈbətən"
    assert v6.verify_6(" ˈbətən.", "ˈbətən", "ipa")
    assert not v6.verify_6(" ˈBətən", "ˈbətən", "ipa")     # no case folding
    assert not v6.verify_6(" bətən", "ˈbətən", "ipa")      # the stress mark counts


def test_unknown_type_is_refused():
    with pytest.raises(ValueError):
        v6.normalize_6("x", "choice")


def test_answer_side_is_a_hard_error():
    for at in v6.ANSWER_TYPES_6:
        with pytest.raises(ValueError):
            v6.verify_6("anything", " .!? ", at)


# strings on which 2c's `word` path raises: after the punctuation strip
# a lone non-space whitespace character is left, truthy and unsplittable
INDEX_ERROR_DRAWS = ['"\r!', "?\x0c.", "'\x0b'", "!\u00a0?", '"\t"']


def test_the_2c_word_path_raises_and_verify_6_absorbs_it():
    h = v6.harness_2c()
    for d in INDEX_ERROR_DRAWS:
        with pytest.raises(IndexError):
            h.normalize_answer(d, "word")
        assert v6.verify_6(d, "owl", "word") is False
        assert v6.verify_6(d, "42", "number") is False
        with pytest.raises(ValueError, match="empty string"):
            v6.normalize_answer_side(d, "word")


def test_draw_side_is_total():
    rng = random.Random(0)
    alphabet = string.printable + "ˈˌəɪʊ  \u2009\u00a0"
    fixed = ["", " ", "\n", "\n\n", ".", '" "', "' '", ". .", "!?", "\t",
             "\n .\n", "-", "- 5", ",", "1,", " \u00a0 "] + INDEX_ERROR_DRAWS
    draws = fixed + ["".join(rng.choice(alphabet) for _ in range(rng.randint(0, 12)))
                     for _ in range(20_000)]
    for at, ans in (("number", "42"), ("word", "owl"), ("span", "6pm to 9pm"),
                    ("ipa", "ˈbətən"), ("sequence", "a b c")):
        for d in draws:
            assert v6.verify_6(d, ans, at) in (True, False)


def test_exact_under_criterion():
    assert v6.exact_under_criterion("1131", "number")
    assert v6.exact_under_criterion("-332", "number")
    assert not v6.exact_under_criterion("12 apples", "number")
    assert v6.exact_under_criterion("gulf", "word")
    assert not v6.exact_under_criterion("blue jay", "word")     # 2d F-3's class
    assert v6.exact_under_criterion("blue jay", "sequence")
    assert v6.exact_under_criterion("ˈfoʊˌtoʊz", "ipa")
