"""Exp 2f frozen analysis (design §3–§6): ladder order on the
probe-flat-but-rising pair — one label, three instruments, the same
weights.

Per cell (rung × size) the three instruments read ONE label (§3)
against ONE floor by ONE bar (2d's one-sided exact binomial, α .01):
  PROBE    2b's probe trained on the rung's committed probe-item
           activations (2b/2c files, sha-pinned), evaluated on the
           500 eval items (activations collected AFTER the tag by
           `collect_eval_2f.py` — the only model contact), at 2c's
           site family with Bonferroni; the untrained twin voids a
           cell (ruling c).
  SAMPLING 2d's committed main draws (32,000 per cell) re-parsed
           through 2c's normalizer to the label; pilot (4,000) as
           the replication.
  ARGMAX   2d's committed fp16 greedy continuations (500), likewise.
Exact-match under the same parse must reproduce 2d's committed
tallies (the scorer gate); 2b's starved probe on the committed
activation files must reproduce 2c's m3 records exactly (the
machinery gate); the eval-item activations must pass provenance
pins and the continuity gate (re-collected probe items within
tolerance of the committed rows — the twin must be the SAME random
network, the trained model the same stack).

Verdict tree (§6): INSUFFICIENT_DATA (any referent failure; both
arith_next cells void) → INVERTED (any monotonicity violation in a
non-void cell) → LADDER (all monotone, ≥ 1 detection) → SILENT.
Refusals the loaders raise are COLLECTED and delivered (lesson 8).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

EXP2F = Path(__file__).resolve().parent
EXPERIMENTS = EXP2F.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st  # noqa: E402
from experiments.exp2f import labels_2f as lb  # noqa: E402
from experiments.exp2f import make_referents_2f as mk  # noqa: E402
from experiments.exp2f import probe_2f as pb  # noqa: E402
from experiments.exp2b.splits import SplitParams  # noqa: E402
from experiments.exp2c.run.screen import _load_activation_map  # noqa: E402

EXP2D = a2d.EXP2D
EXP2B, EXP2C = bt.EXP2B, bt.EXP2C
EXP1 = EXPERIMENTS / "exp1"
RESULTS = EXP2F / "results"
REFERENTS_PATH = EXP2F / "referents_2f.json"

RUNGS, SIZES = lb.RUNGS, lb.SIZES
MODES = mk.MODES
ALPHA = pb.ALPHA                      # .01 — 2b's, 2d's, the same object
ALPHA_SENSITIVITY = 0.05
WORLDS = ("INSUFFICIENT_DATA", "INVERTED", "LADDER", "SILENT")
INSTRUMENTS = ("probe", "sampling", "argmax")     # ladder order, deepest first
CONTINUITY_N = 8                      # probe items re-collected per (size, mode)
CONTINUITY_RTOL = 1e-2                # fp16 activations, batched kernels
CONTINUITY_ATOL = 1e-2
CV_SEED = 0
CV_HOLDOUT = 0.2

# §2, verbatim (fixture-pinned to the design doc)
KNOWN_INPUTS_CAVEAT_2F = (
    "Known and committed: 2d's exact-match counts on the four cells "
    "(sub3_mid 35 | 34, arith_next 831 | 531 of 32,000 at 410m | 1b; argmax "
    "0 | 0 and 13 | 19 of 500); 2c's probe records (margin 0, degenerate "
    "best site, at both sizes for both rungs); the 2c/2b activation files "
    "for the rungs' probe items at both sizes, trained and untrained twin, "
    "on disk and sha-pinned. Derivable but not computed: the label-match "
    "rates of the committed draws and continuations under §3's label "
    "functions. This doc is committed before they are computed; what §7 "
    "says about them is arithmetic from the known exact counts, graded in "
    "the retrospective. Genuinely unmeasured: the probe's reading on the "
    "eval items (the activations do not exist yet) — the one quantity in "
    "the design that is neither known nor derivable.")

# ----------------------------------------------------- frozen-file pins

FROZEN_IMPORT_SHA256_2F = {
    EXP2B / "probe_starved.py":
        "e6c81df28e4a7e07db3a123e4b06d3c8a98a7d330cd726596d41b1136c4cd27b",
    EXP2B / "splits.py":
        "49df4c62c3c3bd611b9cf49be46001c12220045a3611a39be5e2bc5b89ded6e0",
    EXP2B / "models.py":
        "a4c5eed26cc92044aeb9ed7b68b177035de3ac2615dbba09a6d21eeb191a55a4",
    EXP2B / "battery" / "generators.py":
        "cf9db0aec80a554ddfc7fbfeea89697e8c01b1e3f9b1710dfbebb72992216b1e",
    EXP2B / "battery" / "base.py":
        "cb91660ec5c00175b1082cfff67a8c9c535bd203ce6bab488dc9655f3590f1c3",
    EXP1 / "signatures" / "stats.py":
        "ceab3eb7f6daf9346b9231f0e4af7e458b43ba4e7361556aef926e1abde2611f",
    EXP2C / "harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    EXP2C / "run" / "screen.py":
        "fef1814142955912066837fbd2119f5c2ae27fe31393ede890584313e2b06873",
    EXP2C / "battery" / "gen_items.py":
        "25001d7baa514c8013be5fb6d7a26433ea2cc1185603515ae75677c3e52dc916",
    EXP2D / "analyze_2d.py":
        "01ee334db5fe273a8509cf4bf79757b52a40a123311acd42554ac1a82e40334a",
    EXP2D / "stats_2d.py":
        "86243932709013ea15b250e9bf15243ce6209e03e6bcf81af0f7ac3f92644b46",
    EXP2D / "battery_2d.py":
        "503a2c09ec320989223561291ff93c71d62d27ed20c5681f9b2d535b7708e81a",
}

# §4: 2d's committed exact-match tallies — the scorer gate
EXACT_MATCH_PIN = {
    ("sub3_mid", "410m", "main"): 35, ("sub3_mid", "1b", "main"): 34,
    ("arith_next", "410m", "main"): 831, ("arith_next", "1b", "main"): 531,
    ("sub3_mid", "410m", "pilot"): 6, ("sub3_mid", "1b", "pilot"): 3,
    ("arith_next", "410m", "pilot"): 109, ("arith_next", "1b", "pilot"): 67,
    ("sub3_mid", "410m", "argmax"): 0, ("sub3_mid", "1b", "argmax"): 0,
    ("arith_next", "410m", "argmax"): 13, ("arith_next", "1b", "argmax"): 19,
}

# §4: the committed probe-item activation files (2b's / 2c's digest lists)
PROBE_NPZ_SHA_PIN = {
    ("sub3_mid", "1b", "trained"):
        "77c60f38472b13974f40f231f59b0a5cdc64dcd4e48cd54de73c2b0291402dc3",
    ("sub3_mid", "1b", "untrained"):
        "feddbe0e0830bbd84affc6ce077bff1933b59ab0507201eca8a32877b709117b",
    ("sub3_mid", "410m", "trained"):
        "a43d9754bc516b54da1bde921d5c517e877ef6b653045c0887b6ab4f09461d9e",
    ("sub3_mid", "410m", "untrained"):
        "fb742dde155eab487406d096a8c29c86e2e9df2c98f8c57430654da301fbb56d",
    ("arith_next", "1b", "trained"):
        "e14dc60e065c89f01b3fa2d05ef91d2d6114324e7c1af423bbcc95a81042f4d4",
    ("arith_next", "1b", "untrained"):
        "30140ffad82ccabf21b8d3493f94612d3a009d99310272ff28d5acbfe5fa9246",
    ("arith_next", "410m", "trained"):
        "cbc399352cc1b8f99b20373e70783cdb2c46b39d4ffcf34e4bc7394473bcdcbc",
    ("arith_next", "410m", "untrained"):
        "ce2395b6ca05d70fa455dc79eceaab8c4ebbf3dd1508fbaf5a1f0f68c8336c7d",
}

# §4: 2c's committed m3 records (seed 0) — the machinery gate, by literal
M3_PIN = {
    ("sub3_mid", "410m"): {"accuracy": 0.12971698113207547, "best_site": [0, 0],
                           "n_train": 1576, "n_val": 424,
                           "held_per_component": [20]},
    ("sub3_mid", "1b"): {"accuracy": 0.12971698113207547, "best_site": [0, 0],
                         "n_train": 1576, "n_val": 424,
                         "held_per_component": [20]},
    ("arith_next", "410m"): {"accuracy": 0.13535911602209943,
                             "best_site": [0, 0], "n_train": 638, "n_val": 362,
                             "held_per_component": [32]},
    ("arith_next", "1b"): {"accuracy": 0.13535911602209943, "best_site": [0, 0],
                           "n_train": 638, "n_val": 362,
                           "held_per_component": [32]},
}
# 2b's spec for the survivor; 2c's SPLIT_PLAN for arith_next
SPLIT_PARAMS = {"sub3_mid": SplitParams(n_holdout=20),
                "arith_next": SplitParams(holdout_frac=0.35)}
UNTRAINED_SEED = 0                     # 2b/2c's twin

REFERENTS_FILE_SHA256 = \
    "b94dab850e2a757284cdb278657eeec611193d7594292aa25d104a8a03a594d8"


def check_frozen_imports_2f() -> None:
    for path, want in FROZEN_IMPORT_SHA256_2F.items():
        got = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        if got != want:
            raise ValueError(f"frozen file {path} has sha256 {got}, expected "
                             f"{want} — 2b/2c/2d are closed and their code is "
                             f"2f's instrument")


def m3_pin_from_record(rec: dict) -> dict:
    return {"accuracy": rec["accuracy"],
            "best_site": [int(rec["best_layer"]), int(rec["best_token"])],
            "n_train": int(rec["split"]["n_train"]),
            "n_val": int(rec["split"]["n_val"]),
            "held_per_component": list(rec["split"]["held_per_component"])}


# --------------------------------------------------------------- manifest

_LITERAL_PIN = object()


def load_manifest(path=REFERENTS_PATH, *, file_sha_pin=_LITERAL_PIN) -> dict:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    pin = REFERENTS_FILE_SHA256 if file_sha_pin is _LITERAL_PIN else file_sha_pin
    if pin is not None and got != pin:
        raise ValueError(f"{path} has sha256 {got} against the pinned {pin}")
    rec = json.loads(raw)
    if rec.get("n_files") != len(rec.get("files", {})):
        raise ValueError(f"{path}: n_files disagrees with its entries")
    return rec


def check_manifest(rec) -> list:
    if rec["n_files"] != mk.N_FILES:
        raise ValueError(f"manifest carries {rec['n_files']} files, the frozen "
                         f"layout has {mk.N_FILES}")
    base = REPO if rec.get("base") == "REPO" else Path(rec["base"])
    bad = []
    for rel, want in rec["files"].items():
        p = base / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != want:
            bad.append(f"manifest: {rel} hashes to {h}, pinned {want}")
    return bad


# ------------------------------------------------------------ paths/meta

def eval_npz_path(root, size, mode, rung) -> Path:
    return (Path(root) / "results" / "activations_eval" / f"{size}_{mode}"
            / f"{rung}.npz")


def continuity_path(root, size, mode) -> Path:
    return Path(root) / "results" / "continuity" / f"{size}_{mode}.json"


def eval_meta(*, size, mode, rung, n_layers, stack) -> dict:
    from models import PYTHIA_SHAS
    return {"size": size, "mode": mode, "capability": rung,
            "which_items": "eval_items", "n_items": lb.N_ITEMS,
            "n_layers": int(n_layers), "model_sha": PYTHIA_SHAS[size],
            "untrained_seed": UNTRAINED_SEED if mode == "untrained" else None,
            "items_sha256": bt.ITEMS_SHA_PIN[rung],
            "positions": ["question_end", "prompt_end"], "dtype": "float16",
            "n_shots": bt.N_SHOTS, "collector": "exp2f", "stack": stack}


def continuity_record(*, size, mode, per_rung, stack) -> dict:
    from models import PYTHIA_SHAS
    rec = {"size": size, "mode": mode, "model_sha": PYTHIA_SHAS[size],
           "untrained_seed": UNTRAINED_SEED if mode == "untrained" else None,
           "n_items_per_rung": CONTINUITY_N,
           "tolerance": {"rtol": CONTINUITY_RTOL, "atol": CONTINUITY_ATOL},
           "rungs": {r: dict(per_rung[r]) for r in RUNGS}, "stack": stack}
    rec["pass"] = continuity_pass(rec) == []
    return rec


def continuity_pass(rec: dict) -> list:
    """Gate 1, RE-DERIVED from the diffs (the runner's `pass` is
    ignored): every rung present, CONTINUITY_N items compared, max
    relative deviation ≤ rtol and max absolute ≤ atol."""
    from models import PYTHIA_SHAS
    bad = []
    size, mode = rec.get("size"), rec.get("mode")
    if rec.get("model_sha") != PYTHIA_SHAS.get(size):
        bad.append(f"continuity {size}/{mode}: model_sha not 2b's pin")
    want_seed = UNTRAINED_SEED if mode == "untrained" else None
    if rec.get("untrained_seed") != want_seed:
        bad.append(f"continuity {size}/{mode}: untrained_seed "
                   f"{rec.get('untrained_seed')!r} != {want_seed!r}")
    for r in RUNGS:
        d = rec.get("rungs", {}).get(r)
        if not d:
            bad.append(f"continuity {size}/{mode}: no record for {r}")
            continue
        if d.get("n_compared") != CONTINUITY_N:
            bad.append(f"continuity {size}/{mode}/{r}: {d.get('n_compared')} "
                       f"items compared, pinned {CONTINUITY_N}")
        if not (d.get("max_rel_diff", 1e9) <= CONTINUITY_RTOL
                and d.get("max_abs_diff", 1e9) <= CONTINUITY_ATOL):
            bad.append(f"continuity {size}/{mode}/{r}: re-collected probe "
                       f"items deviate (max rel {d.get('max_rel_diff')}, abs "
                       f"{d.get('max_abs_diff')}) beyond the tolerance — the "
                       f"eval activations were not drawn from the committed "
                       f"network on the committed stack")
    return bad


# ------------------------------------------------------------- loaders

def load_npz_map(path):
    return _load_activation_map(Path(path))


def load_probe_acts(path, cap, *, sha_pin=None):
    """The committed probe-item activations, thinned to the family;
    y == the committed probe_label list (2c's label, the gate)."""
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"activation file {path} hashes to {got}, pinned "
                         f"{sha_pin} — not the committed probe-item "
                         f"activations")
    act, y, meta = load_npz_map(path)
    items = cap["probe_items"]
    if len(y) != len(items) or [str(v) for v in y] != \
            [str(it["probe_label"]) for it in items]:
        raise ValueError(f"{path}: labels are not the committed probe_labels")
    if meta.get("capability") != cap.get("name"):
        raise ValueError(f"{path}: capability {meta.get('capability')!r}")
    return pb.thin(act), [str(v) for v in y], meta


def load_eval_npz(path, *, size, mode, rung, cap, n_layers):
    act, y, meta = load_npz_map(path)
    want = eval_meta(size=size, mode=mode, rung=rung, n_layers=n_layers,
                     stack=None)
    for k, v in want.items():
        if k == "stack":
            continue
        if meta.get(k) != v:
            raise ValueError(f"{path}: {k} = {meta.get(k)!r}, expected {v!r}")
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    if [str(v) for v in y] != answers:
        raise ValueError(f"{path}: y is not the committed answer list")
    X0 = next(iter(act.values()))
    if X0.shape[0] != lb.N_ITEMS:
        raise ValueError(f"{path}: {X0.shape[0]} rows")
    return pb.thin(act), answers, meta


def load_eval_acts(root, size, mode, rung, cap, *, n_layers):
    return load_eval_npz(eval_npz_path(root, size, mode, rung), size=size,
                         mode=mode, rung=rung, cap=cap, n_layers=n_layers)


def read_cell_rows(d2_root, tier, size, rung) -> list:
    spec = a2d.TIERS[tier]
    return a2d.read_rows(a2d.tier_draws_path(d2_root, tier, size, rung),
                         seed=spec["seed"], dps=spec["draws_per_seed"])


def read_argmax_continuations(d2_root, size, rung) -> list:
    rec = json.loads(a2d.argmax_record_path(d2_root, size, rung).read_text())
    return list(rec["continuations"])


# ------------------------------------------------------------ tallies

def label_tallies(draws, answers, kind) -> dict:
    if len(draws) != len(answers):
        raise ValueError("label_tallies: draws/answers length")
    match = miss = exact = 0
    for d, ans in zip(draws, answers):
        lab = lb.emission_label(kind, d)
        if lab is lb.MISS:
            miss += 1
        elif lab == lb.answer_label(kind, ans):
            match += 1
        if lb.exact_match(lb.ANSWER_TYPE, d, ans):
            exact += 1
    return {"n": len(draws), "match": match, "miss": miss, "exact": exact}


def instrument_rung(*, match, n, floor, exact, alpha=ALPHA) -> dict:
    bar = st.binomial_bar(match, n, floor, alpha)
    lo, hi = st.clopper_pearson(match, n)
    return {"match": int(match), "n": int(n), "rate": match / n,
            "exact": int(exact), "exact_rate": exact / n, "p": bar["p"],
            "D": bool(bar["significant"]), "cp95": [lo, hi],
            "floor": float(floor), "alpha": alpha}


def monotone(D) -> bool:
    """D = [probe, sampling, argmax] ∈ {0,1}: argmax ≤ sampling ≤ probe."""
    p, s, g = (bool(x) for x in D)
    return g <= s <= p


# --------------------------------------------------------------- gates

def check_exact_pin(tallies: dict, pin: dict) -> list:
    bad = []
    for key, want in pin.items():
        got = tallies.get(key)
        if got is None:
            bad.append(f"exact-match pin: {'/'.join(key)} not scored")
        elif got != want:
            bad.append(f"exact-match pin: {'/'.join(key)} re-scores to {got}, "
                       f"pinned {want} — the parse is not 2d's criterion")
    return bad


def check_m3_gate(battery, m3_pin, *, probe_root=None) -> list:
    bad = []
    for (rung, size), pin in m3_pin.items():
        cap = battery[rung]
        act, y, _ = load_npz_map(mk.probe_npz_path(size, "trained", rung,
                                                   probe_root=probe_root))
        bases = [tuple(it["basis"]) for it in cap["probe_items"]]
        out = pb.starved_accuracies(act, y, bases, SPLIT_PARAMS[rung], seed=0)
        got = {"accuracy": out["accuracy"], "best_site": out["best_site"],
               "n_train": out["split"]["n_train"], "n_val": out["split"]["n_val"],
               "held_per_component": list(out["split"]["held_per_component"])}
        if got != pin:
            bad.append(f"m3 gate {rung}/{size}: 2b's starved probe on the "
                       f"committed activations gives {got}, the committed m3 "
                       f"record says {pin}")
    return bad


def collect(thunk, label):
    try:
        return thunk(), []
    except (ValueError, FileNotFoundError) as e:
        return None, [f"{label}: {e}"]


# ---------------------------------------------------------------- cells

def _cell_key(rung, size) -> str:
    return f"{rung}/{size}"


def compute_cell(*, rung, size, kind, floor, battery, d2_root, root,
                 probe_root, probe_acts, alpha=ALPHA, with_cv=True) -> dict:
    """One cell, one label kind, one floor: the three rungs and the
    pattern. `probe_acts[(rung, size, mode)]` = (act_train, meta) loaded
    once by run()."""
    cap = battery[rung]
    y_train = [lb.answer_label(kind, it["answer"]) for it in cap["probe_items"]]
    y_eval = lb.eval_labels(cap, kind)
    act_tr, meta_tr = probe_acts[(rung, size, "trained")]
    act_tw, _ = probe_acts[(rung, size, "untrained")]
    n_layers = int(meta_tr["n_layers"])
    ev_tr, _, _ = load_eval_acts(root, size, "trained", rung, cap,
                                 n_layers=n_layers)
    ev_tw, _, _ = load_eval_acts(root, size, "untrained", rung, cap,
                                 n_layers=n_layers)
    probe = pb.probe_rung(act_tr, y_train, ev_tr, y_eval, act_tw, ev_tw,
                          floor=floor, alpha=alpha)
    if with_cv:
        cv = pb.cv_probe_sites(act_tr, y_train, sorted(act_tr),
                               seed=CV_SEED, holdout_frac=CV_HOLDOUT)
        probe["cv_probe"] = {"split": cv.pop("split"),
                             "per_site": {str(k): v for k, v in cv.items()},
                             "best_acc": max(v["acc"] for v in cv.values())}
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    sampling = {}
    for tier in ("main", "pilot"):
        rows = read_cell_rows(d2_root, tier, size, rung)
        seed = str(a2d.TIERS[tier]["seed"])
        draws = [d for r in rows for d in r["draws"][seed]]
        ans = [answers[r["item"]] for r in rows for _ in r["draws"][seed]]
        t = label_tallies(draws, ans, kind)
        sampling[tier] = {**instrument_rung(match=t["match"], n=t["n"],
                                            floor=floor, exact=t["exact"],
                                            alpha=alpha),
                          "miss": t["miss"], "seed": int(seed)}
    conts = read_argmax_continuations(d2_root, size, rung)
    t = label_tallies(conts, answers, kind)
    argmax = {**instrument_rung(match=t["match"], n=t["n"], floor=floor,
                                exact=t["exact"], alpha=alpha), "miss": t["miss"]}
    D = [probe["D_probe"], sampling["main"]["D"], argmax["D"]]
    void = bool(probe["void"])
    return {"rung": rung, "size": size, "label": kind, "floor": float(floor),
            "alpha": alpha, "D": D, "void": void,
            "monotone": None if void else monotone(D),
            "probe": probe, "sampling": sampling, "argmax": argmax}


def verdict_tree_2f(referent_failures, cells, n_void_arith) -> dict:
    if referent_failures:
        return {"verdict": "INSUFFICIENT_DATA",
                "reason": f"{len(referent_failures)} referent failure(s): "
                          f"{list(referent_failures)[:5]}"}
    if n_void_arith >= 2:
        return {"verdict": "INSUFFICIENT_DATA",
                "reason": "both arith_next cells are void (the untrained twin "
                          "detects at the trained model's best site)"}
    live = {k: c for k, c in cells.items() if not c["void"]}
    viol = [k for k, c in live.items() if not monotone(c["D"])]
    if viol:
        return {"verdict": "INVERTED",
                "reason": f"monotonicity (argmax ⇒ sampling ⇒ probe) violated "
                          f"in {sorted(viol)}"}
    n_det = sum(int(bool(x)) for c in live.values() for x in c["D"])
    if n_det > 0:
        return {"verdict": "LADDER",
                "reason": f"every non-void cell monotone; {n_det} detection(s) "
                          f"across {len(live)} cell(s)"}
    return {"verdict": "SILENT",
            "reason": "no instrument detects in any non-void cell"}


LICENSED = {
    "LADDER": ("the essay's instrument ladder — probes see deepest, "
               "exhaustive sampling next, argmax last — stands on a second "
               "task class (arithmetic); 2c's silence on these rungs is "
               "attributed to its targets: a probe label chosen for starving "
               "can be linearly unreadable, and a basis-starved validation "
               "set measures generalization, not presence"),
    "INVERTED": ("the ladder is reversal's, not the instruments': the essay's "
                 "instrument-ladder paragraph is demoted to 'on reversal' and "
                 "the discriminator's ordering clause is withdrawn as general"),
    "SILENT": ("2d's 'not silent' was at guessing level under a matched "
               "criterion; 2d's 'the probe's silence was the probe' is "
               "retracted; no anomaly"),
    "INSUFFICIENT_DATA": "nothing; the record states which referent failed",
}


# ------------------------------------------------------------------ run

def run(root=EXP2F, *, d2_root=EXP2D, probe_root=None,
        manifest_path=REFERENTS_PATH, manifest_sha_pin=_LITERAL_PIN,
        exact_pin=None, m3_pin=None, npz_pin=None, write=False,
        out_path=None) -> dict:
    exact_pin = EXACT_MATCH_PIN if exact_pin is None else exact_pin
    m3_pin = M3_PIN if m3_pin is None else m3_pin
    npz_pin = PROBE_NPZ_SHA_PIN if npz_pin is None else npz_pin
    check_frozen_imports_2f()
    manifest = load_manifest(manifest_path, file_sha_pin=manifest_sha_pin)
    failures = check_manifest(manifest)
    battery = {r: bt.load_item_file(r) for r in RUNGS}
    floors = lb.floor_table(battery)
    gates = {"probe_label_gates": lb.check_probe_label_gates(battery)}
    verify_fn = a2d.load_verify()

    # exact-match gate: 2d's tiers through 2d's loader, then the parse
    tallies = {}
    for tier in ("main", "pilot"):
        cells_, f = collect(lambda t=tier: a2d.load_sampling_tier(
            d2_root, t, battery, verify_fn, rungs=RUNGS), f"{tier} tier")
        failures += f
        if cells_:
            for (rung, size), c in cells_.items():
                tallies[(rung, size, tier)] = c["verified"]
    arg, f = collect(lambda: a2d.load_argmax(d2_root, battery, verify_fn,
                                             rungs=RUNGS), "argmax tier")
    failures += f
    if arg:
        for (rung, size), c in arg.items():
            tallies[(rung, size, "argmax")] = c["correct"]
    ef = check_exact_pin(tallies, exact_pin) if tallies else []
    failures += ef
    gates["exact_match_gate"] = (f"PASS ({len(exact_pin)}/{len(exact_pin)} "
                                 f"cells)" if not ef and tallies else "FAIL")

    # the committed probe-item activations + the machinery gate
    probe_acts = {}
    for size in SIZES:
        for rung in RUNGS:
            for mode in MODES:
                p = mk.probe_npz_path(size, mode, rung, probe_root=probe_root)
                got, f = collect(lambda p=p, r=rung, k=(rung, size, mode):
                                 load_probe_acts(p, battery[r],
                                                 sha_pin=npz_pin[k]),
                                 f"probe activations {rung}/{size}/{mode}")
                failures += f
                if got:
                    probe_acts[(rung, size, mode)] = (got[0], got[2])
    mf = []
    if len(probe_acts) == 8:
        mf, f = collect(lambda: check_m3_gate(battery, m3_pin,
                                              probe_root=probe_root), "m3 gate")
        mf = mf or []
        failures += f + mf
    gates["m3_gate"] = "PASS (4/4 cells exact)" if len(probe_acts) == 8 \
        and not mf else "FAIL"

    # gate 1: continuity of the eval-item collection with the committed rows
    cf = []
    for size in SIZES:
        for mode in MODES:
            p = continuity_path(root, size, mode)
            if not p.is_file():
                cf.append(f"continuity {size}/{mode}: record missing ({p})")
                continue
            cf += continuity_pass(json.loads(p.read_text()))
    failures += cf
    gates["continuity_gate"] = "PASS (4/4 records)" if not cf else "FAIL"

    referents = {
        "failures": list(failures),
        "manifest": {"path": str(manifest_path), "n_files": manifest["n_files"],
                     "sha256": hashlib.sha256(
                         Path(manifest_path).read_bytes()).hexdigest()},
        **gates,
        "exact_tallies": {"/".join(k): v for k, v in sorted(tallies.items())},
        "frozen_imports_2f": len(FROZEN_IMPORT_SHA256_2F),
    }
    floors_out = {f"{r}/{k}": v for (r, k), v in floors.items()}

    cells = None
    if not failures:
        cells = {}
        for size in SIZES:
            for rung in RUNGS:
                kind = lb.PRIMARY[rung]
                got, f = collect(lambda rung=rung, size=size, kind=kind:
                                 compute_cell(rung=rung, size=size, kind=kind,
                                              floor=floors[(rung, kind)]["floor"],
                                              battery=battery, d2_root=d2_root,
                                              root=root, probe_root=probe_root,
                                              probe_acts=probe_acts),
                                 f"cell {rung}/{size}")
                failures += f
                if got:
                    cells[_cell_key(rung, size)] = got
        referents["failures"] = list(failures)
    if failures:
        tree = verdict_tree_2f(failures, {}, 0)
        v = {"verdict": tree["verdict"], "reason": tree["reason"],
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2F,
             "licensed_sentence": LICENSED["INSUFFICIENT_DATA"],
             "referents": referents, "cells": None, "floors": floors_out,
             "n_void": None, "n_violations": None, "n_detections": None,
             "model_contact": "eval-item activations only"}
    else:
        n_void_arith = sum(1 for s in SIZES
                           if cells[_cell_key("arith_next", s)]["void"])
        tree = verdict_tree_2f([], cells, n_void_arith)
        live = {k: c for k, c in cells.items() if not c["void"]}
        viol = sorted(k for k, c in live.items() if not monotone(c["D"]))
        sec = {}
        for name, kw in (("arith_next_mod7", {"kind": "mod7"}),
                         ("alpha_05", {"alpha": ALPHA_SENSITIVITY}),
                         ("majority_share_floor", {"floor_key": "majority_share"})):
            sc = {}
            for size in SIZES:
                for rung in RUNGS:
                    kind = kw.get("kind") if rung == "arith_next" and "kind" in kw \
                        else lb.PRIMARY[rung]
                    fl = floors[(rung, kind)][kw.get("floor_key", "floor")]
                    fl = max(fl, 1e-9)
                    sc[_cell_key(rung, size)] = compute_cell(
                        rung=rung, size=size, kind=kind, floor=fl,
                        battery=battery, d2_root=d2_root, root=root,
                        probe_root=probe_root, probe_acts=probe_acts,
                        alpha=kw.get("alpha", ALPHA), with_cv=False)
            nv = sum(1 for s in SIZES if sc[_cell_key("arith_next", s)]["void"])
            sec[name] = {"cells": sc, "tree": verdict_tree_2f([], sc, nv)}
        sec["starved_2c_records"] = {f"{r}/{s}": M3_PIN[(r, s)] if m3_pin is M3_PIN
                                     else m3_pin[(r, s)]
                                     for r in RUNGS for s in SIZES}
        v = {"verdict": tree["verdict"], "reason": tree["reason"],
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2F,
             "licensed_sentence": LICENSED[tree["verdict"]],
             "referents": referents, "cells": cells, "floors": floors_out,
             "n_void": int(sum(c["void"] for c in cells.values())),
             "n_violations": len(viol), "violations": viol,
             "n_detections": int(sum(int(bool(x)) for c in live.values()
                                     for x in c["D"])),
             "instruments": list(INSTRUMENTS),
             "secondaries": sec,
             "model_contact": "eval-item activations only (collector record)"}
    if write:
        out = Path(out_path or RESULTS / "verdict.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(v, indent=1, default=str))
    return v


if __name__ == "__main__":
    v = run(write="--write" in sys.argv)
    print(json.dumps({k: v[k] for k in ("verdict", "reason", "referents",
                                        "n_void", "n_violations",
                                        "n_detections")},
                     indent=1, default=str))
