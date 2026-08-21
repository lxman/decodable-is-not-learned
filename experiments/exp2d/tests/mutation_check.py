"""Mutation-test the Exp 2d fixture suite, in both directions.

Every provision gets at least a SOFTENING mutant (the gate or check
stops firing — the direction that lets an unwelcome outcome through)
and, where a hardening misread exists, a HARDENING mutant (fires when
it must not). A surviving mutant means the fixture suite would not
notice that change to the frozen analysis. Targets: analyze_2d.py,
stats_2d.py, battery_2d.py, rederive_2d.py, compute_power_2d.py,
run/run_cell_2d.py.

Runs under 3a's corrected harness: __pycache__ cleared and
PYTHONDONTWRITEBYTECODE=1 before every pytest invocation. Mutates
sources IN PLACE and restores them — run alone, detached.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "experiments/exp2d/analyze_2d.py"
S = ROOT / "experiments/exp2d/stats_2d.py"
B = ROOT / "experiments/exp2d/battery_2d.py"
D = ROOT / "experiments/exp2d/rederive_2d.py"
P = ROOT / "experiments/exp2d/compute_power_2d.py"
R = ROOT / "experiments/exp2d/run/run_cell_2d.py"

M = [
    # ---- the bar and the margin (§5.1/§5.2) ----
    (S, "bar: alpha loosened", "ALPHA = 0.01 ", "ALPHA = 0.5 "),
    (S, "bar: rate-above-floor conjunct dropped",
     '"significant": bool(p < alpha and rate > floor)',
     '"significant": bool(p < alpha)'),
    (S, "bar: two-sided test",
     'binomtest(k, n, floor, alternative="greater")',
     'binomtest(k, n, floor, alternative="two-sided")'),
    (S, "margin: not zeroed below the bar",
     'm = (bar["rate"] - floor) / (1.0 - floor) if bar["significant"] else 0.0',
     'm = (bar["rate"] - floor) / (1.0 - floor)'),
    (S, "margin: denominator dropped",
     'm = (bar["rate"] - floor) / (1.0 - floor) if bar["significant"] else 0.0',
     'm = (bar["rate"] - floor) if bar["significant"] else 0.0'),
    # ---- the AUC (§5.3) ----
    (S, "auc: ties counted as wins",
     "return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))",
     "return float(((np.asarray(x)[y == 1][:, None] >= np.asarray(x)[y == 0][None, :]).sum()) / (n1 * n0))"),
    (S, "auc: empty class not refused",
     '    if n1 == 0 or n0 == 0:\n        raise ValueError(f"auc undefined: n_rising={n1}, n_flat={n0}")',
     '    if False:\n        raise ValueError(f"auc undefined: n_rising={n1}, n_flat={n0}")'),
    (S, "pairwise: ties not halved",
     "return gt + 0.5 * eq", "return gt + eq"),
    # ---- the block test (§5.3) ----
    (S, "block: sampled add-one convention dropped",
     "p = (1 + count) / (perms.shape[0] + 1)", "p = count / perms.shape[0]"),
    (S, "block: enumerated count excludes the observed (strict)",
     "count = int(np.sum(stats >= obs))", "count = int(np.sum(stats > obs))"),
    (S, "block: layout mismatch not refused",
     "    if len(x) != n or len(y) != n:\n        raise ValueError(\n            f\"block_perm_auc_p: sum(families)={n}",
     "    if False:\n        raise ValueError(\n            f\"block_perm_auc_p: sum(families)={n}"),
    (S, "block: y permuted on the wrong axis (x permuted instead)",
     "    yp = y[perms]                                  # (n_perms, n)\n    stats = (yp @ r - n1 * (n1 + 1) / 2) / (n1 * n0)",
     "    rp = r[perms]\n    stats = (rp @ y - n1 * (n1 + 1) / 2) / (n1 * n0)"),
    (S, "block: perm seed changed", "PERM_SEED = 0 ", "PERM_SEED = 1 "),
    (S, "block: sample size changed", "PERM_SAMPLE = 100_000 ", "PERM_SAMPLE = 10_000 "),
    # ---- the bootstrap (§5.3, fix i) ----
    (S, "boot: undefined resamples imputed .5 (not dropped)",
     "    valid = (n1 > 0) & (n0 > 0)\n    S = auc_pairwise_matrix(x)",
     "    valid = np.ones(len(n1), dtype=bool)\n    n1 = np.maximum(n1, 1); n0 = np.maximum(n0, 1)\n    S = auc_pairwise_matrix(x)"),
    (S, "boot: drop count not reported",
     '"n_valid": n_valid, "n_dropped": n_dropped,\n            "n_boot": int(len(valid)), "boot_mean"',
     '"n_valid": n_valid, "n_dropped": 0,\n            "n_boot": int(len(valid)), "boot_mean"'),
    (S, "boot: seed changed", "BOOT_SEED = 0 ", "BOOT_SEED = 7 "),
    (S, "boot: resample count changed", "N_BOOT = 10_000 ", "N_BOOT = 100 "),
    (S, "boot: counts not 2c's draw order",
     "        pick = rng.choice(n_fam, size=n_fam, replace=True)\n        np.add.at(out[b], pick, 1)",
     "        pick = rng.choice(n_fam, size=n_fam, replace=False)\n        np.add.at(out[b], pick, 1)"),
    # ---- the tree (§6) ----
    (S, "tree: gate-1 branch dropped",
     "    if gate1_diff_cells:\n        return {\"verdict\": \"INSUFFICIENT_DATA\",",
     "    if False:\n        return {\"verdict\": \"INSUFFICIENT_DATA\","),
    (S, "tree: FAIL when CI touches .5 dropped (strict)",
     "    if lo <= 0.5 <= hi:", "    if lo < 0.5 < hi:"),
    (S, "tree: FAIL branch dropped",
     "    if lo <= 0.5 <= hi:", "    if False:"),
    (S, "tree: AUC bar lowered", "AUC_BAR = 0.75 ", "AUC_BAR = 0.5 "),
    (S, "tree: AUC bar strict", "block_p < alpha and auc_obs >= auc_bar",
     "block_p < alpha and auc_obs > auc_bar"),
    (S, "tree: alpha inclusive", "block_p < alpha and auc_obs >= auc_bar",
     "block_p <= alpha and auc_obs >= auc_bar"),
    (S, "tree: PASS without the block test",
     "block_p < alpha and auc_obs >= auc_bar", "auc_obs >= auc_bar"),
    (S, "tree: undefined CI not refused",
     "    if lo is None or hi is None:\n        raise ValueError", "    if False:\n        raise ValueError"),
    # ---- the floor (§5.2, ruling a) ----
    (B, "floor: mean share instead of majority",
     "    top, n_top = counts.most_common(1)[0]",
     "    top, n_top = counts.most_common(1)[0]\n    n_top = len(answers) / len(counts)"),
    (B, "floor: raw answers, not 2c-normalized",
     "    return [h.normalize_answer(str(it[\"answer\"]), at)\n            for it in cap[\"eval_items\"]]",
     "    return [str(it[\"answer\"])\n            for it in cap[\"eval_items\"]]"),
    (B, "floor: option-copy component dropped (ruling H)",
     "    floor = max(maj[\"floor\"], oc[\"floor\"]) if oc else maj[\"floor\"]",
     "    floor = maj[\"floor\"]"),
    (B, "floor: option-listing pin check dropped",
     "    if (oc is None) != (pinned is None) or \\\n            (oc is not None and oc[\"n_options\"] != pinned):",
     "    if False:"),
    (B, "pins: item sha check dropped",
     "    if got != ITEMS_SHA_PIN[rung]:\n        raise ValueError(\n            f\"item file {p} has sha256",
     "    if False:\n        raise ValueError(\n            f\"item file {p} has sha256"),
    (B, "pins: answer-type check dropped",
     "    if at != ANSWER_TYPE_PIN[rung]:", "    if False:"),
    (B, "order: probe_scores order check dropped",
     "    if probe_order != RUNG_ORDER_2D:", "    if False:"),
    (B, "order: manifest sha check dropped",
     "        if ent[\"sha256\"] != ITEMS_SHA_PIN[r]:", "        if False:"),
    # ---- the outcome (§5.2) ----
    (A, "outcome: known-answer gate dropped",
     "    if gate_mismatch:\n        raise ValueError(", "    if False:\n        raise ValueError("),
    (A, "outcome: rising = 12b only",
     '"rising": bool(ascent > 0),', '"rising": bool(per_size["12b"]["margin"] > 0),'),
    (A, "outcome: ascent over two sizes",
     "        ascent = sum(per_size[s][\"margin\"] for s in EVAL_SIZES) / \\\n            len(EVAL_SIZES)",
     "        ascent = sum(per_size[s][\"margin\"] for s in EVAL_SIZES[1:]) / \\\n            len(EVAL_SIZES)"),
    (A, "outcome: floor applied to untrained twin instead",
     "            m = st.corrected_margin(tr[\"correct\"], tr[\"n\"], c)",
     "            m = st.corrected_margin(tr[\"correct\"], tr[\"n\"], max(c, un[\"correct\"] / un[\"n\"] + 1e-9))"),
    (A, "outcome: n pin dropped",
     "                if rec.get(\"n\") != N_ITEMS:", "                if False:"),
    # ---- the predictor (§5.1) ----
    (A, "predictor: 1b only, not the mean",
     '"score": float(sum(per[s]["margin"] for s in sizes) / len(sizes)),',
     '"score": float(per["1b"]["margin"]),'),
    (A, "predictor: draw count pin dropped",
     "            if cell[\"n_draws\"] != n_draws_per_rung:", "            if False:"),
    (A, "tier: stored-tally disagreement not refused",
     "            if not stored or stored.get(\"full_string\") != t[\"verified\"] or \\\n                    stored.get(\"n_draws\") != t[\"n_draws\"]:",
     "            if False:"),
    (A, "tier: incomplete tier not refused",
     "    if missing:\n        raise FileNotFoundError(\n            f\"{tier} tier incomplete",
     "    if False:\n        raise FileNotFoundError(\n            f\"{tier} tier incomplete"),
    (A, "tier: provenance pins dropped",
     "    for k, v in want.items():\n        if rec.get(k) != v:",
     "    for k, v in want.items():\n        if False:"),
    (A, "tier: answers-vs-item-file check dropped",
     "    if [str(a) for a in rec.get(\"answers\", [])] != \\\n            [str(it[\"answer\"]) for it in cap[\"eval_items\"]]:",
     "    if False:"),
    (A, "rows: coverage not pinned",
     "    if len(seen) != n_items:\n        raise ValueError(f\"{path}: {len(seen)} items against {n_items}",
     "    if False:\n        raise ValueError(f\"{path}: {len(seen)} items against {n_items}"),
    (A, "rows: seed not pinned",
     "            if not isinstance(draws, dict) or set(draws) != {str(seed)}:", "            if False:"),
    (A, "rows: dps not pinned",
     "            if not isinstance(stream, list) or len(stream) != dps or \\\n                    not all(isinstance(x, str) for x in stream):",
     "            if False:"),
    # ---- gate 1 (§6) ----
    (A, "gate1: coverage pin dropped (3d F2)",
     "            if rec.get(\"n_items\") != N_ITEMS or \\\n                    rec.get(\"draws_compared\") != GATE1_COVERAGE:",
     "            if False:"),
    (A, "gate1: seed pin dropped",
     "            if rec.get(\"seeds_rederived\") != [GATE1_SEED] or \\\n                    rec.get(\"draws_per_seed\") != TIERS[\"main\"][\"draws_per_seed\"]:",
     "            if False:"),
    (A, "gate1: attested sha vs literal dropped (3c B)",
     "            if rec.get(\"committed_draws_sha256\") != want:", "            if False:"),
    (A, "gate1: fires-reproduced check dropped",
     "            if len(diffs) == 0 and sorted(fires, key=lambda a: (",
     "            if False and sorted(fires, key=lambda a: ("),
    (A, "gate1: n_diffs/diffs coherence dropped",
     "            if not isinstance(diffs, list) or \\\n                    rec.get(\"n_diffs\") != len(diffs):",
     "            if False:"),
    (A, "gate1: diff cells never collected (verdict never INSUFFICIENT)",
     "            if diffs:\n                diff_cells.append(f\"{rung}/{size}\")",
     "            if False:\n                diff_cells.append(f\"{rung}/{size}\")"),
    (A, "gate1: analyzer's own cross-check dropped",
     "            if len(diffs) != gate1[\"cells\"][(rung, size)][\"n_diffs\"]:", "            if False:"),
    (A, "gate1: items sha pin dropped",
     "            if rec.get(\"items_sha256\") != bt.ITEMS_SHA_PIN[rung]:\n                raise ValueError(f\"{p}: items_sha256 against the §4 pin\")",
     "            if False:\n                raise ValueError(f\"{p}: items_sha256 against the §4 pin\")"),
    (D, "rederive: committed sha vs literal dropped",
     "    if gz_sha != want:", "    if False:"),
    (D, "rederive: regenerated coverage not pinned",
     "    if sorted(regenerated) != list(range(a.N_ITEMS)):", "    if False:"),
    (D, "rederive: answers check dropped",
     "    if [str(x) for x in committed.get(\"answers\", [])] != list(answers):", "    if False:"),
    (D, "rederive: halt on diff dropped",
     "    if cmp[\"diffs\"]:\n        raise RuntimeError(", "    if False:\n        raise RuntimeError("),
    # ---- argmax / restriction (§5.4) ----
    (A, "argmax: stored count not recomputed",
     "            if rec.get(\"correct\") != correct:", "            if False:"),
    (A, "argmax: provenance pins dropped",
     "                    or rec.get(\"n_shots\") != bt.N_SHOTS:\n                raise ValueError(f\"{p}: provenance disagrees with the pins\")",
     "                    or rec.get(\"n_shots\") != bt.N_SHOTS:\n                pass"),
    (A, "restriction: performable rungs kept (relabelled, not removed)",
     "    removed = [r for r in RUNGS if outcome[\"rungs\"][r][\"rising\"]\n               and perf[r][\"performable_at_1b\"]]",
     "    removed = []"),
    (A, "percolation: probe-zero conjunct dropped",
     "            and probe[r] == 0]", "            ]"),
    (A, "percolation: 410m read instead of 1b",
     "            and main_cells[(r, REPLICATION_SIZE)][\"verified\"] == 0",
     "            and main_cells[(r, OTHER_SIZE)][\"verified\"] == 0"),
    # ---- frozen-import / referent pins ----
    (A, "pins: frozen-import check dropped",
     "        if got != want:\n            raise ValueError(\n                f\"frozen file {path}",
     "        if False:\n            raise ValueError(\n                f\"frozen file {path}"),
    (A, "pins: referent manifest file sha not checked",
     "    if pin is not None and got != pin:", "    if False:"),
    (A, "pins: referent entries not re-hashed",
     "    if bad:\n        raise ValueError(f\"{len(bad)} referent file(s)",
     "    if False:\n        raise ValueError(f\"{len(bad)} referent file(s)"),
    (A, "stream map: continuity with exp3 dropped",
     "            if exp3_map[\"cells\"].get(key) != mine:", "            if False:"),
    (A, "twin: fires tolerated",
     "    if fires != 0 or rev != TWIN_REVERSAL_DRAWS or ctrl != TWIN_CONTROL_DRAWS:",
     "    if rev != TWIN_REVERSAL_DRAWS or ctrl != TWIN_CONTROL_DRAWS:"),
    # ---- power (§7) ----
    (P, "power: non-rising pilot zeros redrawn (ties not honoured)",
     "            if held_zero[i]:\n                s[i] = 0.0",
     "            if False:\n                s[i] = 0.0"),
    (P, "power: rising raw-zeros held at zero instead of truncated",
     "                u = rng.uniform(0.0, norm.cdf(tau + cap - d))",
     "                u = 0.0"),
    (P, "power: declared-underpowered bar lowered", "POWER_BAR = 0.75 ", "POWER_BAR = 0.05 "),
    (P, "power: declaration read at .75 instead of .85",
     "DECLARATION_TARGET = 0.85 ", "DECLARATION_TARGET = 0.75 "),
    (P, "power: population AUC ties not halved",
     "    return float(one_pos + both_pos + 0.5 * both_zero)",
     "    return float(one_pos + both_pos + both_zero)"),
    (P, "power: tau continuity correction dropped (infinite at 21/21)",
     "    return float(norm.ppf((z0 + 0.5) / (n0 + 1)))",
     "    return float(norm.ppf(z0 / n0))"),
    # ---- runner order (§10) ----
    (R, "runner: main does not wait for the power declaration",
     "        checks += [pilot_clean, power_declared]", "        checks += [pilot_clean]"),
    (R, "runner: argmax does not wait for main",
     "        checks += [main_clean]", "        checks += []"),
    (R, "runner: gate-1 halt ignored",
     "    if halted:\n        raise RuntimeError(f\"§6: {why}\")", "    if False:\n        raise RuntimeError(f\"§6: {why}\")"),
]

TESTS = [str(ROOT / "experiments/exp2d/tests")]
DESELECT = ["-k", "not test_every_terminal_reached and not test_worlds"]


def clear_pycache():
    for d in (ROOT / "experiments/exp2d").rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)


def run_suite(extra=()):
    clear_pycache()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x",
                        "-p", "no:cacheprovider", *TESTS, *extra],
                       cwd=ROOT, env=env, capture_output=True, text=True)
    return r.returncode


def main(argv=None) -> int:
    only = argv[1:] if argv and len(argv) > 1 else None
    survivors, applied = [], 0
    base_rc = run_suite(DESELECT)
    print(f"[mutation] baseline {'clean' if base_rc == 0 else 'FAILING'}",
          flush=True)
    if base_rc != 0:
        return 2
    for i, (path, name, old, new) in enumerate(M):
        if only and str(i) not in only:
            continue
        src = path.read_text()
        if old not in src:
            print(f"  [{i:2d}] TARGET MISSING: {name}", flush=True)
            survivors.append((i, name, "target missing"))
            continue
        path.write_text(src.replace(old, new, 1))
        try:
            rc = run_suite(DESELECT)
        finally:
            path.write_text(src)
        applied += 1
        status = "killed" if rc != 0 else "SURVIVED"
        if rc == 0:
            survivors.append((i, name, "survived"))
        print(f"  [{i:2d}] {status:8s} {name}", flush=True)
    clear_pycache()
    print(f"[mutation] {applied - sum(1 for s in survivors if s[2] == 'survived')}"
          f"/{applied} killed; {len(survivors)} survivor(s)/missing", flush=True)
    for s in survivors:
        print(f"  SURVIVOR [{s[0]}] {s[1]} ({s[2]})", flush=True)
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
