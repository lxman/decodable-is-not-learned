"""Mutation-test the Exp 3c fixture suite, in both directions (doc
Open item 7).

Every provision gets at least a SOFTENING mutant (the gate or check
stops firing — the direction that lets an unwelcome outcome through)
and, where a hardening misread exists, a HARDENING mutant (fires when
it must not — the direction that manufactures INSUFFICIENT_DATA or a
dramatic zero). A surviving mutant means the fixture suite would not
notice that change to the frozen analysis. Targets: analyze_3c.py AND
rederive.py (the gate-1 comparator is verdict-load-bearing).

Runs under 3a's corrected harness: __pycache__ cleared and
PYTHONDONTWRITEBYTECODE=1 before every pytest invocation (a
same-length same-second write leaves stale bytecode and the mutation
never reaches the interpreter).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "experiments/exp3c/analyze_3c.py"
R = ROOT / "experiments/exp3c/rederive.py"

M = [
    # ---- gate 1: zero tolerance (§6.1, reading 1) ----
    (A, "gate1: zero tolerance dropped",
     "    if gate1_diff_cells:", "    if False:"),
    (A, "gate1: tolerance loosened to >3 diffs",
     "                        if v[\"n_diffs\"] > 0}",
     "                        if v[\"n_diffs\"] > 3}"),
    (A, "gate1: fires on a CLEAN comparison (hardening)",
     "    if gate1_diff_cells:", "    if not gate1_diff_cells:"),
    # ---- leak-void (§6.3, reading 3) ----
    (A, "leak: void never applied",
     "            void = str(answer).casefold() in "
     "prompts[rung][i].casefold()",
     "            void = False"),
    (A, "leak: all-void INSUFFICIENT_DATA route dropped",
     "    if all_new_fires > 0 and len(all_void) == all_new_fires:",
     "    if False:"),
    (A, "leak: all-void route fires on ANY fire (hardening)",
     "    if all_new_fires > 0 and len(all_void) == all_new_fires:",
     "    if all_new_fires > 0 and len(all_void) >= 0:"),
    (A, "leak: adjudication reads pre-void counts",
     "        return fires[_key(key)][\"new\"][\"count\"]",
     "        return fires[_key(key)][\"raw_fire_count_pre_void\"]"),
    (A, "leak: non-void filter inverted (hardening)",
     "        non_void = [ad for ad in addresses if not ad[\"void\"]]",
     "        non_void = [ad for ad in addresses if ad[\"void\"]]"),
    (A, "leak: fired flag reads pre-void fires",
     "            \"fired\": bool(non_void),",
     "            \"fired\": bool(addresses),"),
    # ---- adjudication (§6.4) ----
    (A, "adjudication: the fired cell moved",
     "FIRED_CELL = (\"reverse_string\", \"1b\", \"trained\")",
     "FIRED_CELL = (\"rev_string7\", \"1b\", \"trained\")"),
    (A, "adjudication: walls include the fired cell",
     "WALLED_CELLS = tuple(k for k in SCORED_CELLS if k != FIRED_CELL)",
     "WALLED_CELLS = tuple(SCORED_CELLS)"),
    # ---- pooling (§5) ----
    (A, "pooling: exp3's committed count dropped",
     "        k_pool = e3[\"full_string_total\"] + non_void_count(key)",
     "        k_pool = non_void_count(key)"),
    (A, "pooling: exp3's draws dropped from the denominator",
     "        n_pool = e3[\"n_draws_total\"] + \\\n"
     "            new_cells[key][\"recomputed\"][\"n_draws_total\"]",
     "        n_pool = \\\n"
     "            new_cells[key][\"recomputed\"][\"n_draws_total\"]"),
    # ---- every zero a bound; every nonzero a CI ----
    (A, "bounds: zero bound faked to 1.0",
     "        e[\"cp95_upper\"] = a3.cp_upper(0, n, level=CI_LEVEL)",
     "        e[\"cp95_upper\"] = 1.0"),
    (A, "bounds: nonzero CI faked to [0, 1]",
     "        lo, hi = a3.clopper_pearson(k, n, level=CI_LEVEL)",
     "        lo, hi = 0.0, 1.0"),
    (A, "luck floor: wrong base",
     "    return 26.0 ** (-length)", "    return 25.0 ** (-length)"),
    # ---- strata (§5 descriptives) ----
    (A, "strata: void exclusion dropped",
     "                            if not ad[\"void\"] and "
     "ad[\"item\"] in idx_set)",
     "                            if ad[\"item\"] in idx_set)"),
    (A, "strata: stratum membership inverted (hardening)",
     "                            if not ad[\"void\"] and "
     "ad[\"item\"] in idx_set)",
     "                            if not ad[\"void\"] and "
     "ad[\"item\"] not in idx_set)"),
    # ---- exp3-side referent asserts (readings 4, 6) ----
    (A, "referent: fires-table equality dropped",
     "        if got != ref:", "        if False:"),
    (A, "referent: fires-table equality inverted (hardening)",
     "        if got != ref:", "        if got == ref:"),
    (A, "referent: twin zero assert dropped",
     "        if rc[\"full_string_total\"] != 0:", "        if False:"),
    (A, "referent: address pin comparison dropped",
     "    if exp3_fire_addresses != exp3_referent[\"fire_addresses\"]:",
     "    if False:"),
    (A, "referent: answer-length pin dropped",
     "        if lengths != exp3_referent[\"fire_answer_lengths\"][k]:",
     "        if False:"),
    (A, "referent: sha pin on the committed verdict dropped",
     "    if got != want:\n        raise ValueError(\n"
     "            f\"exp3 verdict record",
     "    if False:\n        raise ValueError(\n"
     "            f\"exp3 verdict record"),
    (A, "referent: valueless fires-table entries accepted",
     "        if not (isinstance(e, dict) and isinstance(\n"
     "                e.get(\"full_string_total\"), int)\n"
     "                and isinstance(e.get(\"n_draws\"), int)):",
     "        if False:"),
    (A, "frozen imports: hash assert dropped",
     "        if got != want:\n            raise ValueError(\n"
     "                f\"frozen file",
     "        if False:\n            raise ValueError(\n"
     "                f\"frozen file"),
    # ---- cross-tree pins (§6.2) ----
    (A, "pins: items_sha256 not checked against the §4 pin",
     "        if c[\"items_sha256\"] != sha_refs[rung]:",
     "        if False:"),
    (A, "pins: answers/labels not pinned across trees",
     "            if c[field] != e[field]:", "            if False:"),
    # ---- new-cell loader (§6.2) ----
    (A, "loader: seed set not enforced",
     "    if rec.get(\"seeds\") != list(NEW_SEEDS):", "    if False:"),
    (A, "loader: draws_per_seed not enforced",
     "    if rec.get(\"draws_per_seed\") != DRAWS_PER_SEED_3C:",
     "    if False:"),
    (A, "loader: k_total not enforced",
     "    if rec.get(\"k_total\") != K_NEW:", "    if False:"),
    (A, "loader: sampling dtype policy not enforced",
     "    if rec.get(\"dtype\") != \"float32\":\n"
     "        raise ValueError(\n"
     "            f\"{p}: dtype {rec.get('dtype')!r} violates the "
     "ledgered \"",
     "    if False:\n"
     "        raise ValueError(\n"
     "            f\"{p}: dtype {rec.get('dtype')!r} violates the "
     "ledgered \""),
    (A, "gate1 loader: dtype policy not enforced",
     "        if rec.get(\"dtype\") != \"float32\":\n"
     "            raise ValueError(f\"{p}: dtype {rec.get('dtype')!r} "
     "is not the \"\n"
     "                             f\"campaign's float32\")",
     "        if False:\n"
     "            raise ValueError(f\"{p}: dtype {rec.get('dtype')!r} "
     "is not the \"\n"
     "                             f\"campaign's float32\")"),
    (A, "loader: twin seed on a trained cell accepted",
     "    if rec.get(\"untrained_seed\") is not None:", "    if False:"),
    (A, "loader: stored-tally disagreement accepted",
     "        if normalized != t[\"per_seed\"]:", "        if False:"),
    (A, "loader: stray files silently ignored",
     "            if f.name not in want[d.name]:",
     "            if False:"),
    (A, "loader: unexpected directories (incl. *_untrained) accepted",
     "        if d.is_file() or d.name not in want:",
     "        if False:"),
    (A, "recompute: verify never applied",
     "                if verify_fn(d, answers[i], answer_type):",
     "                if False:"),
    (A, "recompute: first_char never applied",
     "                if a3.score_first_char(d, labels[i]):",
     "                if False:"),
    # ---- gate-1 record loader ----
    (A, "gate1 loader: re-derived depth not pinned to exp3's",
     "        if dps != a3.DRAWS_PER_SEED[rung]:", "        if False:"),
    (A, "gate1 loader: compared volume not enforced",
     "        if compared != n * dps or compared <= 0:",
     "        if False:"),
    (A, "gate1 loader: undisclosed diff counts accepted",
     "        if rec.get(\"n_diffs\") != len(diffs):",
     "        if False:"),
    (A, "gate1 loader: malformed diff entries accepted",
     "            if not (isinstance(dd, dict)",
     "            if False and not (isinstance(dd, dict)"),
    # ---- stream map (reading 7) ----
    (A, "stream map: formula equality dropped",
     "    if m.get(\"formula\") != e.get(\"formula\"):",
     "    if False:"),
    (A, "stream map: entries not checked against the formula",
     "            if m[\"cells\"][k] != want:", "            if False:"),
    (A, "stream map: pooling continuity dropped",
     "            if sd in a3.SEEDS and m[\"cells\"][k] != "
     "e[\"cells\"][k]:",
     "            if False:"),
    # ---- freeze findings A/B (the adversarial session's closures) ----
    (A, "finding A: leak-gate prompt pin dropped",
     "        if got_sha != sha_refs[rung]:", "        if False:"),
    (A, "finding A: leak-gate prompt pin always fires (hardening)",
     "        if got_sha != sha_refs[rung]:", "        if True:"),
    (A, "finding B: gate-1 committed-sha loop closure dropped",
     "        want = gate1_records[key][\"committed_draws_sha256\"]\n"
     "        if got != want:",
     "        want = gate1_records[key][\"committed_draws_sha256\"]\n"
     "        if False:"),
    (A, "finding B: gate-1 committed-sha check always fires (hardening)",
     "        want = gate1_records[key][\"committed_draws_sha256\"]\n"
     "        if got != want:",
     "        want = gate1_records[key][\"committed_draws_sha256\"]\n"
     "        if True:"),
    # ---- rederive comparator (gate 1's teeth) ----
    (R, "comparator: differing draws never recorded",
     "            if str(g) != str(w):", "            if False:"),
    (R, "comparator: regenerated coverage not enforced",
     "        if not isinstance(got, list) or len(got) != dps:",
     "        if False:"),
    (R, "comparator: committed depth not enforced",
     "        if len(committed) != dps:", "        if False:"),
    (R, "comparator: extra regenerated items accepted",
     "    if extra:", "    if False:"),
    (R, "record: compared volume miscounted",
     "        \"draws_compared\": n_items * dps,",
     "        \"draws_compared\": n_items,"),
    (R, "record: diff count not the disclosed list's length",
     "        \"n_diffs\": len(diffs),", "        \"n_diffs\": 0,"),
]


def run():
    for d in (ROOT / "experiments").rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, "-m", "pytest", "experiments/exp3c/tests/",
         "-q", "--no-header", "-x", "--tb=no"],
        cwd=ROOT, capture_output=True, text=True, env=env).returncode


originals = {A: A.read_text(), R: R.read_text()}
killed, survived = [], []
try:
    for target, name, old, new in M:
        orig = originals[target]
        if old not in orig:
            survived.append(f"{name} [PATTERN NOT FOUND]")
            continue
        if orig.count(old) != 1:
            survived.append(f"{name} [PATTERN NOT UNIQUE]")
            continue
        target.write_text(orig.replace(old, new, 1))
        rc = run()
        target.write_text(orig)
        (killed if rc != 0 else survived).append(name)
finally:
    for target, orig in originals.items():
        target.write_text(orig)
print(f"KILLED {len(killed)}/{len(M)}")
for k in killed:
    print("  ok  ", k)
if survived:
    print(f"\nSURVIVED {len(survived)}")
    for s in survived:
        print("  MISS", s)
print("\nbaseline:", "clean" if run() == 0 else "DIRTY")
