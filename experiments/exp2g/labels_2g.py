# experiments/exp2g/labels_2g.py
"""Exp 2g labels (design §3): one label per rung, a pure function of
the committed item. Ten of the eleven predictor rungs reproduce the
committed `probe_label` field on every eval and probe item (gate G-L).
arith_next is the one exception: its label is 2f's own last-digit
label function (2f showed the mod-7 residue isn't linearly readable),
checked against every eval and probe item as the primary referent; the
committed `probe_label` field — 2c's mod-7 label — is checked
separately as a second referent, against `answer mod 7` rather than
against this rung's label. The answer side is never MISS — anything
outside a label's domain is a hard error."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

EXP2G = Path(__file__).resolve().parent
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2g import battery_2g as bg  # noqa: E402

KIND_OF = {
    "antonym": "position", "antonym6": "position", "median5": "position",
    "odd6": "position",
    "add_base8": "last_char", "sub_base8": "last_char",
    "add3_mid": "tens_digit", "sub3_mid": "tens_digit",
    "sub4_mid": "hundreds_digit",
    "arith_next": "last_digit",
    "count_div13": "count",
}
_N_OPTIONS = {"antonym": 4, "antonym6": 6, "median5": 5, "odd6": 6}
_COUNT_RANGE = (1, 10)
_DIGITS = re.compile(r"[0-9]+")
_OCTAL = re.compile(r"[0-7]+")


def classes_of(rung: str) -> list:
    kind = KIND_OF.get(rung)
    if kind is None:
        raise ValueError(f"{rung!r} has no 2g label")
    if kind == "position":
        return [str(i) for i in range(1, _N_OPTIONS[rung] + 1)]
    if kind == "last_char":
        return [str(i) for i in range(8)]
    if kind in ("tens_digit", "hundreds_digit", "last_digit"):
        return [str(i) for i in range(10)]
    if kind == "count":
        return [str(i) for i in range(_COUNT_RANGE[0], _COUNT_RANGE[1] + 1)]
    raise ValueError(kind)


def n_classes(rung: str) -> int:
    return len(classes_of(rung))


def _options(question: str) -> list:
    if ":" not in question:
        raise ValueError(f"no option list in {question!r}")
    tail = question.rsplit(":", 1)[1].rstrip("?. ")
    opts = [o.strip().lower() for o in tail.split(",")]
    if len(opts) < 2 or any(not o for o in opts):
        raise ValueError(f"malformed option list in {question!r}")
    return opts


def answer_label(rung: str, item: dict) -> str:
    kind = KIND_OF.get(rung)
    if kind is None:
        raise ValueError(f"{rung!r} has no 2g label")
    ans = str(item["answer"]).strip()
    if kind == "position":
        opts = _options(item["question"])
        if len(opts) != _N_OPTIONS[rung]:
            raise ValueError(f"{rung}: {len(opts)} options, expected "
                             f"{_N_OPTIONS[rung]}")
        hits = [i for i, o in enumerate(opts) if o == ans.lower()]
        if len(hits) != 1:
            raise ValueError(f"{rung}: answer {ans!r} found {len(hits)} times "
                             f"among {opts}")
        return str(hits[0] + 1)
    if kind == "last_char":
        if not _OCTAL.fullmatch(ans):
            raise ValueError(f"{rung}: answer {ans!r} is not an octal numeral")
        return ans[-1]
    if not _DIGITS.fullmatch(ans):
        raise ValueError(f"{rung}: answer {ans!r} is not a non-negative integer")
    if kind == "tens_digit":
        if len(ans) > 4:
            raise ValueError(f"{rung}: answer {ans!r} has more than 4 digits")
        return ans.zfill(3)[-2]
    if kind == "hundreds_digit":
        if len(ans) > 5:
            raise ValueError(f"{rung}: answer {ans!r} has more than 5 digits")
        return ans.zfill(4)[-3]
    if kind == "last_digit":
        return ans[-1]
    if kind == "count":
        v = int(ans)
        if not _COUNT_RANGE[0] <= v <= _COUNT_RANGE[1]:
            raise ValueError(f"{rung}: count {v} outside {_COUNT_RANGE}")
        return str(v)
    raise ValueError(kind)


def eval_labels(cap: dict, rung: str) -> list:
    return [answer_label(rung, it) for it in cap["eval_items"]]


def probe_labels(cap: dict, rung: str) -> list:
    return [answer_label(rung, it) for it in cap["probe_items"]]


def check_label_gates(battery: dict) -> dict:
    """G-L: the label function == the committed probe_label on every
    eval item (500/500) and every probe item — for ten of the eleven
    rungs. arith_next is the one exception (design §3): its label is
    fixed as 2f's last-digit label, not the committed `probe_label`
    field, which carries 2c's older mod-7 label — a label a prior
    experiment (2f) showed the representation cannot carry. So
    arith_next's known-answer referent is 2f's own label function
    (`labels_2f.answer_label("last_digit", ...)`), checked on every
    eval and probe item; the committed `probe_label` field is checked
    separately, as a second referent, against 2c's mod-7 label
    (`answer mod 7`) rather than against this rung's label."""
    from experiments.exp2f import labels_2f as lb2f
    gates = {}
    for rung in bg.PREDICTOR_RUNGS:
        cap = battery[rung]
        if rung == "arith_next":
            for which in ("eval_items", "probe_items"):
                items = cap[which]
                bad_2f = [i for i, it in enumerate(items)
                          if lb2f.answer_label("last_digit", it["answer"])
                          != answer_label(rung, it)]
                if bad_2f:
                    raise ValueError(
                        f"{rung}/{which}: the last-digit label disagrees "
                        f"with 2f's last-digit label function on "
                        f"{len(bad_2f)} item(s), e.g. {bad_2f[:3]}")
                bad_mod7 = [i for i, it in enumerate(items)
                            if str(it.get("probe_label"))
                            != str(int(it["answer"]) % 7)]
                if bad_mod7:
                    raise ValueError(
                        f"{rung}/{which}: the committed probe_label "
                        f"disagrees with answer mod 7 on {len(bad_mod7)} "
                        f"item(s), e.g. {bad_mod7[:3]} — not 2c's "
                        f"committed mod-7 label")
        else:
            for which in ("eval_items", "probe_items"):
                bad = [i for i, it in enumerate(cap[which])
                       if str(it.get("probe_label")) != answer_label(rung, it)]
                if bad:
                    raise ValueError(
                        f"{rung}/{which}: the committed probe_label disagrees with "
                        f"the {KIND_OF[rung]} label on {len(bad)} item(s), e.g. "
                        f"{bad[:3]} — the label function is not 2c's")
        n_e, n_p = len(cap["eval_items"]), len(cap["probe_items"])
        if n_e != bg.N_ITEMS:
            raise ValueError(f"{rung}: {n_e} eval items")
        if rung == "arith_next":
            gates[rung] = (f"PASS ({n_e}/{n_e} eval; {n_p}/{n_p} probe; "
                            f"last digit == 2f's label; committed "
                            f"probe_label == answer mod 7)")
        else:
            gates[rung] = f"PASS ({n_e}/{n_e} eval; {n_p}/{n_p} probe)"
    return gates


def check_class_coverage(battery: dict) -> dict:
    """Every eval label must occur among the probe labels (else the
    probe has no row for it and the item's score is undefined)."""
    out = {}
    for rung in bg.PREDICTOR_RUNGS:
        cap = battery[rung]
        pe, pp = set(eval_labels(cap, rung)), set(probe_labels(cap, rung))
        out[rung] = {"eval_classes": sorted(pe), "probe_classes": sorted(pp),
                     "eval_not_in_probe": sorted(pe - pp)}
        if pe - pp:
            raise ValueError(f"{rung}: eval labels {sorted(pe - pp)} never "
                             f"occur among the probe items")
    return out


def floor_table(battery: dict) -> dict:
    """The label's floor for the rung-level descriptive (§6.4):
    max(majority label share over the 500 eval labels, 1/K)."""
    out = {}
    for rung in bg.PREDICTOR_RUNGS:
        y = eval_labels(battery[rung], rung)
        counts = Counter(y)
        top, n_top = counts.most_common(1)[0]
        K = n_classes(rung)
        maj = n_top / len(y)
        out[rung] = {"floor": float(max(maj, 1.0 / K)), "majority_share": float(maj),
                     "majority_label": top, "n_classes": K, "n_items": len(y),
                     "class_counts": {k: v for k, v in sorted(counts.items())}}
    return out


if __name__ == "__main__":
    b = bg.load_battery(bg.PREDICTOR_RUNGS)
    for r, g in check_label_gates(b).items():
        print(f"{r:12s} {KIND_OF[r]:14s} {g}")
    check_class_coverage(b)
