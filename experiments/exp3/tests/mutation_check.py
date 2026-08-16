"""Mutation-test the Exp 3 fixture suite, in both directions (doc Open
items 3 and 4).

Every provision gets at least a SOFTENING mutant (the gate or check
stops firing — the direction that lets an unwelcome outcome through)
and, where a hardening misread exists, a HARDENING mutant (fires when
it must not — the direction that manufactures INSUFFICIENT_DATA, a
dramatic zero, or significance from float dust). A surviving mutant
means the fixture suite would not notice that change to the frozen
analysis.

Excluded as EQUIVALENT (checked numerically at build, ledgered): a
mutant deleting the explicit all-ties branch — scipy's binom.sf(-1, 0,
.5) is 1.0, so the branch is the ledgered reading made visible rather
than an observable behaviour change.

Runs under 3a's corrected harness: __pycache__ cleared and
PYTHONDONTWRITEBYTECODE=1 before every pytest invocation, because a
same-length same-second write leaves stale bytecode and the mutation
never reaches the interpreter (3a FREEZE_CHECKLIST, "A defect in the
mutation harness itself").
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "experiments/exp3/analyze_3.py"

M = [
    # ---- the §5 statistic (interior-competitor form, freeze amendment) ----
    ("statistic: echo character admitted into the competitor set",
     "        interior = s[1:-1]", "        interior = s[1:]"),
    ("statistic: first character admitted into its own competitor set",
     "        interior = s[1:-1]", "        interior = s[:-1]"),
    ("statistic: interior multiplicity dropped (competitors de-duplicated)",
     "        comp = sum(float(it[\"letters\"][c]) for c in interior) \\\n"
     "            / len(interior)",
     "        comp = sum(float(it[\"letters\"][c]) for c in set(interior)) \\\n"
     "            / len(set(interior))"),
    ("statistic: interior-less items silently dropped instead of tied",
     "        if not interior:\n            signs.append(0.0)\n"
     "            continue",
     "        if not interior:\n            continue"),
    ("statistic: upper end never credits the residual",
     "        if upper:\n            m_y += float(it[\"residual\"])",
     "        if False:\n            m_y += float(it[\"residual\"])"),
    ("statistic: K counts float dust as signal",
     "    K = sum(1 for s in signs if s > SIGN_TIE_EPS)",
     "    K = sum(1 for s in signs if s > 0)"),
    ("statistic: ties detected only at exact zero",
     "    n_ties = sum(1 for s in signs if abs(s) <= SIGN_TIE_EPS)",
     "    n_ties = sum(1 for s in signs if abs(s) <= 0)"),
    ("statistic: binomial tail off by one (sf(K) for sf(K-1))",
     "    p = float(binom.sf(K - 1, n_eff, 0.5))",
     "    p = float(binom.sf(K, n_eff, 0.5))"),
    ("statistic: Bonferroni dropped",
     "    return p, bool(p * n_tests < alpha)",
     "    return p, bool(p < alpha)"),
    ("statistic: non-letter read characters silently treated as computable",
     "    if outside:", "    if False:"),
    # ---- bracket ends (reading 1) ----
    ("bracket: adjudication reads the upper end where present",
     "        return sign_tests[_key(key)][\"lower\"][\"significant\"]",
     "        return sign_tests[_key(key)].get(\"upper\", "
     "sign_tests[_key(key)][\"lower\"])[\"significant\"]"),
    ("bracket: threshold widened so the upper end never computes",
     "RESIDUAL_BRACKET_THRESHOLD = 0.01",
     "RESIDUAL_BRACKET_THRESHOLD = 0.5"),
    ("bracket: lower/upper disagreement not reported",
     "            if upper[\"significant\"] != lower[\"significant\"]:",
     "            if False:"),
    ("bracket: residual dropped from the cell bracket's upper end",
     "    hi = sum(float(it[\"label_mass\"]) + float(it[\"residual\"])\n"
     "             for it in mass_items) / n",
     "    hi = sum(float(it[\"label_mass\"]) + 0.0\n"
     "             for it in mass_items) / n"),
    # ---- scope (readings 5 and 8) ----
    ("scope: eval-size mass cells take significance tests too",
     "        if size not in PROBE_SIZES:\n            continue",
     "        if False:\n            continue"),
    ("scope: adjudicated cells at n_tests=1",
     "        n_tests = N_ADJ_TESTS if adjudicated else 1",
     "        n_tests = 1"),
    ("scope: twins and controls at the adjudicated n_tests",
     "        n_tests = N_ADJ_TESTS if adjudicated else 1",
     "        n_tests = N_ADJ_TESTS"),
    ("scope: adjudication widened to the controls",
     "ADJUDICATED = tuple((r, s, \"trained\") for r in REVERSAL_RUNGS",
     "ADJUDICATED = tuple((r, s, \"trained\") for r in RUNGS"),
    # ---- gate 1 (positive control) ----
    ("gate1: skipped",
     "    if not (all(gate1[\"mass_significant\"].values())",
     "    if False and not (all(gate1[\"mass_significant\"].values())"),
    ("gate1: either probe size suffices instead of both",
     "    if not (all(gate1[\"mass_significant\"].values())",
     "    if not (any(gate1[\"mass_significant\"].values())"),
    ("gate1: sampled full-string CP arm dropped",
     "            and all(v > 0.5 for v in",
     "            and all(v > -1 for v in"),
    # ---- gate 2 (byte identity) ----
    ("gate2: tolerance so wide it never fires",
     "BYTE_TOLERANCE = 2", "BYTE_TOLERANCE = 500"),
    ("gate2: zero tolerance — an allowed pair of diffs kills the run",
     "BYTE_TOLERANCE = 2", "BYTE_TOLERANCE = 0"),
    ("gate2: diffs never disclosed",
     "        if diffs:", "        if False:"),
    ("gate2: continuations never compared",
     "                 if str(g) != str(w)]",
     "                 if False]"),
    # ---- gate 3 (coherence; readings 2 and 9) ----
    ("gate3: never triggers",
     "    if incoherent_adj:", "    if False:"),
    ("gate3: trigger widened to all 16 sampling cells",
     "    incoherent_adj = [_key(k) for k in GATE3_FATAL_CELLS",
     "    incoherent_adj = [_key(k) for k in SAMPLING_CELLS"),
    ("gate3: fatal set narrowed back to the adjudicated four (freeze "
     "ruling on reading 2 undone)",
     "GATE3_FATAL_CELLS = ADJUDICATED + (\n"
     "    (POSITIVE_CONTROL, \"410m\", \"trained\"), "
     "(POSITIVE_CONTROL, \"1b\", \"trained\"))",
     "GATE3_FATAL_CELLS = ADJUDICATED"),
    ("gate3: interval at plain .95 instead of the Bonferroni level",
     "    level = 1.0 - alpha / N_COHERENCE_TESTS",
     "    level = 0.95"),
    ("gate3: everything coherent by fiat",
     "            \"coherent\": not (ci_hi < b_lo or b_hi < ci_lo)}",
     "            \"coherent\": True}"),
    # ---- gate 5 (contamination) and step 6 ----
    ("gate5: mass arm dropped",
     "            if mass_arm or fire_arm:", "            if fire_arm:"),
    ("gate5: fire arm dropped",
     "            if mass_arm or fire_arm:", "            if mass_arm:"),
    ("gate5: contaminated rungs not excluded from step 6",
     "    eligible = [(r, s) for r in REVERSAL_RUNGS if r not in "
     "contaminated\n                for s in PROBE_SIZES]",
     "    eligible = [(r, s) for r in REVERSAL_RUNGS\n"
     "                for s in PROBE_SIZES]"),
    ("gate5: vacuous quantifier allowed to adjudicate",
     "    if not eligible:", "    if False:"),
    ("step6: ELICITABLE on any cell rather than all",
     "    if worlds == {\"ELICITABLE\"}:",
     "    if \"ELICITABLE\" in worlds:"),
    ("step6: WALL swallows mixtures",
     "    if worlds == {\"WALL\"}:", "    if \"WALL\" in worlds:"),
    ("step6: fires never fire",
     "                 \"fired\": rc[\"fired\"]}",
     "                 \"fired\": False}"),
    ("step6: everything fires",
     "                 \"fired\": rc[\"fired\"]}",
     "                 \"fired\": True}"),
    ("step6: per-item-max bound aliases the pooled bound",
     "            entry[\"cp95_upper_per_item_max\"] = cp_upper(\n"
     "                0, sampling_cells[key][\"k_total\"])",
     "            entry[\"cp95_upper_per_item_max\"] = "
     "entry[\"cp95_upper_pooled\"]"),
    # ---- battery shape (reading 7) ----
    ("shape: missing cells accepted",
     "        if set(got) != set(SAMPLING_CELLS):", "        if False:"),
    ("shape: items_sha256 pins not checked",
     "            if c[\"items_sha256\"] != sha_refs[rung]:",
     "            if False:"),
    ("shape: answers/labels not pinned to the referent",
     "                if c[field] != ref[field]:",
     "                if False:"),
    # ---- loaders ----
    ("loader: stray files silently ignored",
     "            if f.name not in want_names:", "            if False:"),
    ("loader: dtype policy not enforced",
     "    if rec.get(\"dtype\") != want_dtype:", "    if False:"),
    ("loader: short seed streams accepted",
     "len(stream) != dps or \\", "len(stream) < 0 or \\"),
    ("loader: duplicate item rows accepted",
     "            if i in seen:", "            if False:"),
    ("loader: gappy letter vectors accepted",
     "            if not isinstance(letters, dict) or set(letters) != "
     "set(LETTERS):",
     "            if False:"),
    ("loader: stored-tally disagreement accepted",
     "        if normalized != recomputed:", "        if False:"),
    ("recompute: verify never applied",
     "                if verify_fn(d, answers[i], answer_type):",
     "                if False:"),
    ("recompute: first_char never applied",
     "                if score_first_char(d, labels[i]):",
     "                if False:"),
    # ---- committed-referent pins (ported from 3b) ----
    ("floors: sha pin not checked",
     "    if got_sha != expected_sha:", "    if False:"),
    ("floors: recompute-assert dropped",
     "        if recomputed != committed.get(rung):", "        if False:"),
    # ---- scoring (ported from 3b) ----
    ("scoring: leading whitespace not stripped",
     "    s = str(continuation).lstrip()", "    s = str(continuation)"),
    ("scoring: unparseable draws scored correct",
     "    return bool(got is not None and got == "
     "str(probe_label)[0].casefold())",
     "    return bool(got is None or got == "
     "str(probe_label)[0].casefold())"),
    # ---- Clopper–Pearson ----
    ("cp: upper bound always 1",
     "    return float(beta.ppf(level, k + 1, n - k))", "    return 1.0"),
    ("cp: lower bound always 0",
     "    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))",
     "    lo = 0.0"),
]


def run():
    for d in (ROOT / "experiments").rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, "-m", "pytest", "experiments/exp3/tests/", "-q",
         "--no-header", "-x", "--tb=no"],
        cwd=ROOT, capture_output=True, text=True, env=env).returncode


orig = A.read_text()
killed, survived = [], []
try:
    for name, old, new in M:
        if old not in orig:
            survived.append(f"{name} [PATTERN NOT FOUND]")
            continue
        A.write_text(orig.replace(old, new, 1))
        rc = run()
        A.write_text(orig)
        (killed if rc != 0 else survived).append(name)
finally:
    A.write_text(orig)
print(f"KILLED {len(killed)}/{len(M)}")
for k in killed:
    print("  ok  ", k)
if survived:
    print(f"\nSURVIVED {len(survived)}")
    for s in survived:
        print("  MISS", s)
print("\nbaseline:", "clean" if run() == 0 else "DIRTY")
