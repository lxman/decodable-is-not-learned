"""Synthetic full-shape batteries for the Exp 3 freeze rule (design §2
item 1, §8, §10, Open item 4): the frozen verdict tree must be EXECUTED
to every terminal branch — four worlds, PARTIAL, every
INSUFFICIENT_DATA route, both contamination interactions, a coherence
fire, a residual-bracket disagreement — end to end through the frozen
loaders, before the tag.

Each battery is a complete on-disk world in the runner's own layout:
28 mass cells, 16 sampling cells with raw draws beside them
(`{rung}.draws.jsonl.gz`), 16 re-decode cells, and a synthetic gate-2
referent tree in 3b's record shape. `run_battery` loads it through
analyze_3's own producers with the REAL committed floors and REAL
committed probe margins, and adjudicates.

Worlds use n = 20 items per rung (the loaders pin cross-battery
consistency and the preregistered draw counts, not the item count, so
small worlds stay honest); every count below is chosen so gate 3's
coherence holds except where a battery deliberately breaks it, and the
matched control's answers begin with DIGITS so every world exercises
the reading-5 letter-support path through the real loader.

The stored per-seed tallies are computed HERE with 2c's verify and
3b's first_char directly — independently of the analyzer's own
recompute — so the loader's tally agreement check crosses two
implementations rather than one function against itself.
"""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

from experiments.exp3 import analyze_3 as a

EXP3 = Path(__file__).resolve().parents[1]

# 2c must win the `harness` name (run_cell's ordering, verbatim
# reasoning): only its harness defines the verify the tallies use.
for _p in (EXP3.parent / "exp2b", EXP3.parent / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

N = 20
P_SIG = 0.6        # adjudicated "mass elevated" cells
P_CTRL = 0.94      # ctrl_copy: coherent with 602/640 fc and 600 fires
P_HOT = 0.3        # a twin loud enough to contaminate at n_tests = 1
P_FLOOR = 0.076    # split cells: mean label mass .038 ≈ 1/26
P_CLOCK = 0.37     # the agreement quadrant's committed neighbourhood

# default sampling counts (first-char draws, verified full-string
# fires) per cell class; rev cells pool 20*256 = 5120 draws, control
# cells 20*32 = 640
FC_REV_FLOOR = 195     # ≈ .038 * 5120: coherent with P_FLOOR masses
FC_REV_SIG = 3072      # = .60 * 5120: coherent with P_SIG masses
FC_CTRL = 602          # ≈ .94 * 640, of which 600 verify full-string
FC_CTRL_FLOOR = 24     # ≈ .038 * 640: quiet twins
FC_CLOCK = 237         # ≈ .37 * 640, 150 of them full-string


def rung_items(rung):
    """(labels, answers) for a synthetic rung. Letter rungs cycle ten
    first letters (w̃ well-spread, guard clear); the matched control's
    answers begin with digits — the real shape, reading 5's path."""
    if rung == a.MATCHED_CONTROL:
        firsts = "123456789"
        answers = [f"{firsts[i % 9]}:4{i % 10} pm" for i in range(N)]
    else:
        firsts = "abcdefghij"
        answers = [f"{firsts[i % 10]}{rung[:3]}q{i}" for i in range(N)]
    return [ans[0] for ans in answers], answers


def _blank_letters():
    return {c: 0.0 for c in a.LETTERS}


def mass_items_for(case, labels, answers, *, depth=2):
    """Per-item mass records in masses.py's stored shape, per case.

    floor      — signs split 10/10 (not significant), mean label .038
    sig / sig94 / hot — all mass on the correct letter (significant)
    digit37 / digitfloor — the digit-label control (letters empty,
                 label mass in `extra`; sign test not computable)
    flip       — lower end 10/20 (not sig), whole residual flips the
                 odd items positive at the upper end (reading 1)
    zero       — all-ties cell (every mass 0)
    """
    items = []
    support = sorted(set(labels))
    for i, (label, _ans) in enumerate(zip(labels, answers)):
        lc = str(label)[0].casefold()
        letters = _blank_letters()
        extra = {}
        residual = 0.0
        if case in ("sig", "sig94", "hot"):
            letters[lc] = {"sig": P_SIG, "sig94": P_CTRL, "hot": P_HOT}[case]
        elif case == "floor":
            if i % 2 == 0:
                letters[lc] = P_FLOOR
            else:
                comp = next(c for c in support if c != lc)
                letters[comp] = P_FLOOR
        elif case == "flip":
            if i % 2 == 0:
                letters[lc] = 0.05
            else:
                comp = next(c for c in support if c != lc)
                letters[comp] = 0.05
                residual = 0.2
        elif case == "digit37":
            extra[lc] = P_CLOCK
        elif case == "digitfloor":
            extra[lc] = 0.038
        elif case == "zero":
            pass
        else:
            raise ValueError(f"unknown mass case {case!r}")
        label_mass = letters[lc] if lc in letters else extra.get(lc, 0.0)
        rec = {"letters": letters, "extra": extra, "label_char": lc,
               "label_mass": label_mass, "residual": residual,
               "ws_mass_p1": residual, "terminal_mass": 0.0,
               "depth": depth}
        if depth == 1:
            # 12b's honest wider bracket: unresolved whitespace mass
            rec["residual"] = rec["residual"] + 0.05
            rec["ws_mass_p1"] = rec["residual"]
        items.append(rec)
    return items


def build_rows(rung, labels, answers, n_fc, n_fire):
    """Deterministic draw rows hitting exactly n_fc first-char draws,
    n_fire of which verify full-string. Slots are filled in
    (draw index, item, seed) order so fires spread across seeds first
    (the per-seed spread the record reports with any fire)."""
    if not n_fc >= n_fire >= 0:
        raise ValueError(f"n_fc {n_fc} must be >= n_fire {n_fire} >= 0")
    dps = a.DRAWS_PER_SEED[rung]
    slots = [(d, i, s) for d in range(dps) for i in range(N)
             for s in a.SEEDS]
    if n_fc > len(slots):
        raise ValueError(f"n_fc {n_fc} exceeds {len(slots)} slots")
    rows = [{"item": i, "draws": {str(s): [" ~z"] * dps for s in a.SEEDS}}
            for i in range(N)]
    for t, (d, i, s) in enumerate(slots[:n_fc]):
        text = f" {answers[i]}" if t < n_fire else f" {labels[i]}~x"
        rows[i]["draws"][str(s)][d] = text
    return rows


def independent_tallies(rows, answers, labels, answer_type):
    """The stored convenience tallies, computed here with 2c's verify
    and 3b's first_char in a plain loop — NOT with the analyzer's
    recompute, so the loader's agreement check crosses implementations."""
    import harness

    out = {str(s): {"full_string": 0, "first_char": 0, "n_draws": 0}
           for s in a.SEEDS}
    for row in rows:
        i = row["item"]
        for s in a.SEEDS:
            for d in row["draws"][str(s)]:
                out[str(s)]["n_draws"] += 1
                if harness.verify(d, answers[i], answer_type):
                    out[str(s)]["full_string"] += 1
                if a.score_first_char(d, labels[i]):
                    out[str(s)]["first_char"] += 1
    return out


# ------------------------------------------------------------ the world

def default_world():
    """The WALL base: reversal at floor and silent, ctrl_copy loud and
    verified, the matched control in its agreement quadrant, every twin
    quiet, re-decode byte-identical to the gate-2 tree."""
    mass = {}
    for rung in a.RUNGS:
        for size, mode in [(s, m) for m in a.MODES
                           for s in (a.SIZES if m == "trained"
                                     else a.PROBE_SIZES)]:
            if rung == a.POSITIVE_CONTROL:
                case = "sig94" if mode == "trained" else "floor"
            elif rung == a.MATCHED_CONTROL:
                case = "digit37" if mode == "trained" else "digitfloor"
            else:
                case = "floor"
            mass[(rung, size, mode)] = case
    draws = {}
    for rung in a.RUNGS:
        for size in a.PROBE_SIZES:
            for mode in a.MODES:
                if rung == a.POSITIVE_CONTROL:
                    fc, fire = (FC_CTRL, 600) if mode == "trained" \
                        else (FC_CTRL_FLOOR, 0)
                elif rung == a.MATCHED_CONTROL:
                    fc, fire = (FC_CLOCK, 150) if mode == "trained" \
                        else (FC_CTRL_FLOOR, 0)
                else:
                    fc, fire = FC_REV_FLOOR, 0
                draws[(rung, size, mode)] = (fc, fire)
    return {"mass": mass, "draws": draws, "redecode_drift": {}}


def write_world(root: Path, *, mass=None, draws=None, redecode_drift=None,
                answer_type="word") -> Path:
    """One complete on-disk world under `root`, in the runner's layout,
    plus the synthetic gate-2 referent tree under root/'gate2'."""
    world = default_world()
    world["mass"].update(mass or {})
    world["draws"].update(draws or {})
    world["redecode_drift"].update(redecode_drift or {})
    root = Path(root)

    gate2 = {}
    for rung in a.RUNGS:
        labels, answers = rung_items(rung)
        for size in a.PROBE_SIZES:
            for mode in a.MODES:
                conts = [f" g{i}-{rung}-{size}-{mode}" for i in range(N)]
                gate2[(rung, size, mode)] = conts
                rec = {"rung": rung, "size": size, "mode": mode,
                       "n_items": N, "continuations": conts,
                       "probe_labels": labels, "answers": answers,
                       "full_string_correct": 0, "max_new_tokens": 12,
                       "n_shots": 2,
                       "untrained_seed": 0 if mode == "untrained" else None,
                       "model_sha": f"synthetic-{size}",
                       "items_sha256": f"items-{rung}"}
                p = root / "gate2" / f"{size}_{mode}" / f"{rung}.json"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps(rec))

    def prov(rung, size, mode, dtype):
        labels, answers = rung_items(rung)
        return {"rung": rung, "size": size, "mode": mode, "n_items": N,
                "probe_labels": labels, "answers": answers,
                "answer_type": answer_type, "n_shots": 2, "dtype": dtype,
                "untrained_seed": 0 if mode == "untrained" else None,
                "model_sha": f"synthetic-{size}",
                "items_sha256": f"items-{rung}"}

    for (rung, size, mode), case in world["mass"].items():
        labels, answers = rung_items(rung)
        depth = 1 if size == "12b" else 2
        dtype = "float16" if size == "12b" else "float32"
        rec = {**prov(rung, size, mode, dtype), "depth": depth,
               "items": mass_items_for(case, labels, answers, depth=depth)}
        p = root / "results" / "mass" / f"{size}_{mode}" / f"{rung}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec))

    for (rung, size, mode), (n_fc, n_fire) in world["draws"].items():
        labels, answers = rung_items(rung)
        rows = build_rows(rung, labels, answers, n_fc, n_fire)
        d = root / "results" / "sampling" / f"{size}_{mode}"
        d.mkdir(parents=True, exist_ok=True)
        with gzip.open(d / f"{rung}.draws.jsonl.gz", "wt") as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True) + "\n")
        rec = {**prov(rung, size, mode, "float32"),
               "seeds": list(a.SEEDS),
               "draws_per_seed": a.DRAWS_PER_SEED[rung],
               "k_total": a.K_TOTAL[rung],
               "per_seed_tallies": independent_tallies(
                   rows, answers, labels, answer_type),
               "draws_file": f"{rung}.draws.jsonl.gz"}
        (d / f"{rung}.json").write_text(json.dumps(rec))

    for (rung, size, mode), conts in gate2.items():
        labels, answers = rung_items(rung)
        drifted = list(conts)
        for i in range(world["redecode_drift"].get((rung, size, mode), 0)):
            drifted[N - 1 - i] = drifted[N - 1 - i] + " DRIFT"
        rec = {**prov(rung, size, mode, "float16"),
               "continuations": drifted, "full_string_correct": 0,
               "max_new_tokens": 12}
        p = root / "results" / "redecode" / f"{size}_{mode}" / f"{rung}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec))

    return root
