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
    first letters over all-letter answers (the amended statistic reads
    the first character and the interior "{rung[:3]}q", so every read
    character stays inside a–z); the matched control's answers begin
    with digits — the real shape, reading 5's path."""
    if rung == a.MATCHED_CONTROL:
        firsts = "123456789"
        answers = [f"{firsts[i % 9]}:4{i % 10} pm" for i in range(N)]
    else:
        firsts = "abcdefghij"
        suffix = "abcdefghijklmnopqrst"
        answers = [f"{firsts[i % 10]}{rung[:3]}q{suffix[i]}"
                   for i in range(N)]
    return [ans[0] for ans in answers], answers


def _blank_letters():
    return {c: 0.0 for c in a.LETTERS}


def mass_items_for(case, labels, answers, *, depth=2):
    """Per-item mass records in masses.py's stored shape, per case.

    floor      — signs split 10/10 (not significant), mean label .038;
                 the negative items put their mass on 'q', a character
                 in every letter-rung answer's INTERIOR and never a
                 first letter here (the amended statistic's competitor)
    sig / sig94 / hot / hot10 — all mass on the correct letter
                 (significant; hot10's LOW mean .10 is the gate-3
                 ruling's crack: rank-fired sign test under a mass
                 bracket far below healthy sampled rates)
    digit37 / digitfloor — the digit-label control (letters empty,
                 label mass in `extra`; sign test not computable)
    flip       — lower end 10/20 (not sig), whole residual flips the
                 odd items positive at the upper end (reading 1)
    zero       — all-ties cell (every mass 0)
    """
    items = []
    for i, (label, _ans) in enumerate(zip(labels, answers)):
        lc = str(label)[0].casefold()
        letters = _blank_letters()
        extra = {}
        residual = 0.0
        if case in ("sig", "sig94", "hot", "hot10"):
            letters[lc] = {"sig": P_SIG, "sig94": P_CTRL, "hot": P_HOT,
                           "hot10": 0.10}[case]
        elif case == "floor":
            if i % 2 == 0:
                letters[lc] = P_FLOOR
            else:
                letters["q"] = P_FLOOR
        elif case == "flip":
            if i % 2 == 0:
                letters[lc] = 0.05
            else:
                letters["q"] = 0.05
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


def run_battery(root: Path) -> dict:
    """End to end through the frozen loaders: the world's own mass,
    sampling, re-decode, and gate-2 trees; the REAL committed floors
    and REAL committed probe margins."""
    return a.verdict(a.load_mass_cells(root),
                     a.load_sampling_cells(root),
                     a.load_redecode_cells(root),
                     a.load_gate2_referents(root / "gate2"),
                     a.load_floors(),
                     a.load_probe_margins())


# ------------------------------------------------------- the batteries
#
# Every terminal branch of design §6, plus the disclosed-but-not-fatal
# provisions, each as a complete world. `expect_contaminated` defaults
# to [] in the assertions; `check` callables assert the world's own
# provision on the verdict record.

REV_ADJ = [(r, s, "trained") for r in a.REVERSAL_RUNGS
           for s in a.PROBE_SIZES]

MASS_SIG_ADJ = {k: "sig" for k in REV_ADJ}
DRAWS_SIG_FIRE = {k: (FC_REV_SIG, 5) for k in REV_ADJ}
DRAWS_SIG_QUIET = {k: (FC_REV_SIG, 0) for k in REV_ADJ}
DRAWS_FLOOR_FIRE = {k: (FC_REV_FLOOR, 1) for k in REV_ADJ}

BATTERIES = {
    # ---- the four worlds ----
    "wall": {
        "world": {},
        "expect": "WALL",
        "check": [
            lambda out: all(v == "WALL" for v in out["cell_labels"].values()),
            # every zero ships as a CP bound, pooled and per-item-max
            lambda out: 0 < out["fires"]["rev_string7/410m/trained"]
            ["cp95_upper_pooled"] < 1e-3,
            lambda out: out["fires"]["rev_string7/410m/trained"]
            ["cp95_upper_per_item_max"] > out["fires"]
            ["rev_string7/410m/trained"]["cp95_upper_pooled"],
            # the probe stays the arbiter, in the frozen reason text
            lambda out: "arbiter" in out["reason"],
            # reading 5 through the real path: the digit-label control's
            # sign test is recorded not-computable, never significant
            lambda out: out["mass_sign_tests"]
            ["clock24_d999/410m/trained"]["lower"]["computable"] is False,
            # adjudicated sign tests run at n_tests = 4, twins at 1
            lambda out: out["mass_sign_tests"]
            ["rev_string7/410m/trained"]["lower"]["n_tests"] == 4,
            lambda out: out["mass_sign_tests"]
            ["rev_string7/410m/untrained"]["lower"]["n_tests"] == 1,
        ]},
    "elicitable": {
        "world": {"mass": MASS_SIG_ADJ, "draws": DRAWS_SIG_FIRE,
                  # two byte diffs on a passing battery: within 3b's
                  # tolerance, disclosed regardless
                  "redecode_drift": {("clock24_d999", "1b", "untrained"): 2}},
        "expect": "ELICITABLE",
        "check": [
            lambda out: len(out["byte_diffs"]
                            ["clock24_d999/1b/untrained"]) == 2,
            # per-seed spread reported with any fire
            lambda out: out["fires"]["rev_string7/410m/trained"]
            ["fired_seeds"] == {"0": 2, "1": 1, "2": 1, "3": 1},
        ]},
    "bulk_only": {
        "world": {"mass": MASS_SIG_ADJ, "draws": DRAWS_SIG_QUIET},
        "expect": "BULK-ONLY",
        "check": [lambda out: "autoregressive" in out["reason"]]},
    "tail_only": {
        "world": {"draws": DRAWS_FLOOR_FIRE},
        "expect": "TAIL-ONLY",
        "check": [lambda out: "strong" in out["reason"]]},
    "partial": {
        "world": {"mass": {("rev_string7", s, "trained"): "sig"
                           for s in a.PROBE_SIZES},
                  "draws": {("rev_string7", s, "trained"): (FC_REV_SIG, 5)
                            for s in a.PROBE_SIZES}},
        "expect": "PARTIAL",
        "check": [
            lambda out: out["cell_labels"]["rev_string7/410m"] ==
            "ELICITABLE",
            lambda out: out["cell_labels"]["reverse_string/410m"] == "WALL",
        ]},
    # ---- INSUFFICIENT_DATA routes ----
    "id_gate1_mass": {
        # the positive control's mass sign test dies at ONE probe size —
        # "both" means both. Its draws stay loud, so the mass/draws
        # mismatch also shows up as a disclosed control incoherence
        # (reading 2: disclosed, and gate 1 is what takes the verdict).
        "world": {"mass": {("ctrl_copy", "1b", "trained"): "floor"}},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "ctrl_copy",
        "check": [
            lambda out: out["gate1"]["mass_significant"]["1b"] is False,
            lambda out: out["coherence"]["ctrl_copy/1b/trained"]
            ["coherent"] is False,
        ]},
    "id_gate1_cp": {
        # mass arm healthy, sampled full-string arm dead: 200/640
        # verified is far above nothing but its CP95 lower bound ≤ .5
        "world": {"draws": {("ctrl_copy", "410m", "trained"):
                            (FC_CTRL, 200)}},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "ctrl_copy",
        "check": [
            lambda out: out["gate1"]["mass_significant"]["410m"] is True,
            lambda out: out["gate1"]["full_string_cp95_lower"]["410m"] < 0.5,
        ]},
    "id_gate2_bytes": {
        "world": {"redecode_drift": {("rev_string7", "410m", "trained"): 3}},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "byte",
        "check": [
            lambda out: len(out["byte_diffs"]
                            ["rev_string7/410m/trained"]) == 3,
            lambda out: "DRIFT" in out["byte_diffs"]
            ["rev_string7/410m/trained"][0]["got"],
        ]},
    "id_gate3_coherence": {
        # an adjudicated cell's mass says .6, its draws say nothing —
        # a code-path defect, not a finding
        "world": {"mass": {("rev_string7", "410m", "trained"): "sig"}},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "coheren",
        "check": [lambda out: out["coherence"]
                  ["rev_string7/410m/trained"]["coherent"] is False]},
    "id_gate3_ctrl_incoherent_behind_passing_gate1": {
        # the freeze ruling's crack (reading 2, ledger 2026-08-16):
        # ctrl_copy's sign test fires on rank (label mass .10, interior
        # zero) and its verified full-string rate .625 clears the CP
        # arm — BOTH gate-1 arms pass — while the first-char count's
        # CP interval is disjoint from the .10 mass bracket. A run
        # must not proceed past a disagreeing positive control.
        "world": {"mass": {("ctrl_copy", "410m", "trained"): "hot10"},
                  "draws": {("ctrl_copy", "410m", "trained"): (400, 400)}},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "coheren",
        "check": [
            lambda out: out["gate1"]["mass_significant"]["410m"] is True,
            lambda out: out["gate1"]["full_string_cp95_lower"]["410m"] > 0.5,
            lambda out: out["coherence"]["ctrl_copy/410m/trained"]
            ["coherent"] is False,
        ]},
    "id_both_rungs_contaminated": {
        # one twin fires on the mass arm (draws kept coherent with its
        # hot mass), the other on a verified full-string draw
        "world": {"mass": {("rev_string7", "410m", "untrained"): "hot"},
                  "draws": {("rev_string7", "410m", "untrained"): (1536, 0),
                            ("reverse_string", "1b", "untrained"):
                            (FC_REV_FLOOR, 1)}},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "contamin",
        "expect_contaminated": ["rev_string7", "reverse_string"],
        "check": [
            lambda out: out["contamination_evidence"]["rev_string7"]
            [0]["mass_arm"] is True,
            lambda out: out["contamination_evidence"]["reverse_string"]
            [0]["fire_arm"] is True,
        ]},
    # ---- contamination × step 6 interaction ----
    "contaminated_one_rung": {
        # rev_string7's twin fires, so step 6 quantifies over
        # reverse_string alone — which is ELICITABLE everywhere. An
        # implementation that ignores the exclusion sees rev_string7's
        # WALL cells and returns PARTIAL instead.
        "world": {"mass": {("rev_string7", "410m", "untrained"): "hot",
                           **{("reverse_string", s, "trained"): "sig"
                              for s in a.PROBE_SIZES}},
                  "draws": {("rev_string7", "410m", "untrained"): (1536, 0),
                            **{("reverse_string", s, "trained"):
                               (FC_REV_SIG, 5) for s in a.PROBE_SIZES}}},
        "expect": "ELICITABLE",
        "expect_contaminated": ["rev_string7"]},
    # ---- disclosed-but-not-fatal provisions ----
    "bracket_disagreement": {
        # mean residual .1 > .01 in an adjudicated cell: the upper end
        # is computed and disagrees (significant) — its own finding;
        # adjudication reads the lower end and the world stays WALL
        "world": {"mass": {("rev_string7", "410m", "trained"): "flip"},
                  "draws": {("rev_string7", "410m", "trained"): (128, 0)}},
        "expect": "WALL",
        "check": [
            lambda out: out["bracket_findings"] == [
                "rev_string7/410m/trained"],
            lambda out: out["mass_sign_tests"]["rev_string7/410m/trained"]
            ["upper"]["significant"] is True,
            lambda out: out["mass_sign_tests"]["rev_string7/410m/trained"]
            ["lower"]["significant"] is False,
        ]},
    "eval_mass_is_descriptive": {
        # an eval-size cell loud enough to pass any test takes no test
        # (reading 8) and moves no verdict; it is visible in the scale
        # trend
        "world": {"mass": {("rev_string7", "12b", "trained"): "sig"}},
        "expect": "WALL",
        "check": [
            lambda out: "rev_string7/12b/trained" not in
            out["mass_sign_tests"],
            lambda out: out["mass_scale_trend"]["rev_string7"]["12b"] >
            out["mass_scale_trend"]["rev_string7"]["2.8b"],
        ]},
    "twin_incoherence_is_disclosed_not_fatal": {
        # reading 2's trigger scope: a NON-adjudicated cell's
        # incoherence (a twin here) is disclosed in full and the
        # verdict stands
        "world": {"draws": {("ctrl_copy", "410m", "untrained"): (300, 0)}},
        "expect": "WALL",
        "check": [lambda out: out["coherence"]
                  ["ctrl_copy/410m/untrained"]["coherent"] is False]},
    "coherence_level_margin": {
        # 230/5120 sampled first-char against the [.038, .038] floor
        # bracket: DISJOINT at plain .95 (CP lower .0394) but coherent
        # at the §6.3 Bonferroni level 1−.01/16 (CP lower .0357) — the
        # world that catches a coherence check run at the wrong level
        "world": {"draws": {("rev_string7", "410m", "trained"): (230, 0)}},
        "expect": "WALL",
        "check": [lambda out: out["coherence"]
                  ["rev_string7/410m/trained"]["coherent"] is True]},
}


def run_all(base: Path) -> dict:
    out = {}
    for name, spec in BATTERIES.items():
        root = Path(base) / name
        write_world(root, **spec.get("world", {}))
        out[name] = run_battery(root)
    return out


if __name__ == "__main__":
    import tempfile

    base = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        Path(tempfile.mkdtemp(prefix="exp3_full_shape_"))
    results = run_all(base)
    ok = True
    for name, spec in BATTERIES.items():
        v = results[name]
        good = (v["verdict"] == spec["expect"]
                and spec.get("expect_reason", "") in v.get("reason", "")
                and v["contaminated"] == spec.get("expect_contaminated", [])
                and all(chk(v) for chk in spec.get("check", [])))
        ok &= good
        print(f"{'ok  ' if good else 'FAIL'} {name}: {v['verdict']}"
              f" (contaminated={v['contaminated']})")
    print("ALL TERMINAL BRANCHES REACHED" if ok else "FULL-SHAPE RUN FAILED")
    sys.exit(0 if ok else 1)
