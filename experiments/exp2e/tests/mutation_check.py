"""Mutation-test the Exp 2e fixture suite, in both directions.

Every provision gets at least a SOFTENING mutant (a gate stops firing,
the primary reads a different functional, a constant moves) and, where
a hardening misread exists, a HARDENING mutant. A surviving mutant
means the suite would not notice that change to the frozen analysis.
Targets: functionals_2e.py, analyze_2e.py, make_referents_2e.py.

Runs under 3a's corrected harness: __pycache__ cleared and
PYTHONDONTWRITEBYTECODE=1 before every pytest invocation; the
full-shape worlds are deselected (the disk-free verdict fixtures in
test_analyze_2e cover the same provisions). Mutates sources IN PLACE
and restores them — run alone, detached.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
F = ROOT / "experiments/exp2e/functionals_2e.py"
A = ROOT / "experiments/exp2e/analyze_2e.py"
K = ROOT / "experiments/exp2e/make_referents_2e.py"

M = [
    # ---- ε (ruling c) ----
    (F, "eps: a whole draw, not half", "return 1.0 / (2 * n)", "return 1.0 / n"),
    (F, "eps: n ≤ 0 accepted", "    if n <= 0:\n        raise ValueError", "    if False:\n        raise ValueError"),
    (F, "eps: pilot reads the main constant",
     "    e = eps_for(n) if eps is None else float(eps)\n    out = {}\n    for r in rungs:\n        c = floors[r][floor_key]",
     "    e = EPS_MAIN if eps is None else float(eps)\n    out = {}\n    for r in rungs:\n        c = floors[r][floor_key]"),
    # ---- F1 (§5.1) ----
    (F, "F1: floor subtracted, not divided", "return math.log((rate + eps) / floor)", "return math.log(rate + eps) - floor"),
    (F, "F1: floor ignored", "return math.log((rate + eps) / floor)", "return math.log(rate + eps)"),
    (F, "F1: 1b only, not the mean over sizes",
     '        out[r] = {"per_size": per,\n                  "score": float(sum(per.values()) / len(sizes)),\n                  "floor": float(c), "eps": e}',
     '        out[r] = {"per_size": per,\n                  "score": float(per[sizes[-1]]),\n                  "floor": float(c), "eps": e}'),
    (F, "F1: floor_key ignored (majority sensitivity inert)",
     "    for r in rungs:\n        c = floors[r][floor_key]\n        per = {s: log_excess",
     "    for r in rungs:\n        c = floors[r][\"floor\"]\n        per = {s: log_excess"),
    (F, "F1: n_draws mismatch accepted",
     "    if cell[\"n_draws\"] != n_draws:\n        raise ValueError", "    if False:\n        raise ValueError"),
    (F, "F1: floor range unchecked", "    if not (0.0 < floor < 1.0):\n        raise ValueError(f\"log_excess", "    if False:\n        raise ValueError(f\"log_excess"),
    # ---- F2 / B0 / F3 ----
    (F, "F2: ε doubled", "per = {s: math.log(_rate(cells, r, s, n) + e) for s in sizes}", "per = {s: math.log(_rate(cells, r, s, n) + 2 * e) for s in sizes}"),
    (F, "B0: sign flipped", 'out[r] = {"score": float(-math.log(c)), "floor": float(c)}', 'out[r] = {"score": float(math.log(c)), "floor": float(c)}'),
    (F, "F3: raw values ranked instead of midranks", "    R = rankdata(mean_rate)\n    Z = rankdata(floor)", "    R = mean_rate\n    Z = floor"),
    (F, "F3: floor not partialled out", "    resid = R - A @ coef", "    resid = R - R.mean()"),
    (F, "F3: no intercept in the fit", "    A = np.column_stack([np.ones(len(rungs)), Z])", "    A = np.column_stack([np.zeros(len(rungs)), Z])"),
    (F, "F3: 1b only ranked",
     "    mean_rate = np.array([sum(_rate(cells, r, s, n) for s in sizes) / len(sizes)",
     "    mean_rate = np.array([sum(_rate(cells, r, s, n) for s in sizes[-1:]) / 1"),
    # ---- paired bootstrap ----
    (F, "paired: undefined resamples kept", "    valid = (n1 > 0) & (n0 > 0)\n    c1v", "    valid = np.ones(len(n1), dtype=bool); n1 = np.maximum(n1, 1); n0 = np.maximum(n0, 1)\n    c1v"),
    (F, "paired: difference reversed", "    d = a1 - a2", "    d = a2 - a1"),
    (F, "paired: 90% interval", 'pct = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]', 'pct = lambda v: [float(np.percentile(v, 5)), float(np.percentile(v, 95))]'),
    (F, "paired: drop count not reported", '"n_valid": n_valid, "n_dropped": n_dropped,\n            "n_boot": int(len(valid))}', '"n_valid": n_valid, "n_dropped": 0,\n            "n_boot": int(len(valid))}'),
    # ---- tree (§6) ----
    (F, "tree: referent branch dropped", "    if referent_failures:\n        return {\"verdict\": \"INSUFFICIENT_DATA\",", "    if False:\n        return {\"verdict\": \"INSUFFICIENT_DATA\","),
    (F, "tree: bars not 2d's", "ALPHA = st.ALPHA          # ruling d: 2d's bars, the same objects\nAUC_BAR = st.AUC_BAR", "ALPHA = 0.05\nAUC_BAR = 0.6"),
    (F, "layout: family sizes not recomputed", "    sizes = [sum(1 for f in fams if f == fam) for fam in order]\n    return kept, sizes, fams", "    sizes = list(bt.FAMILY_SIZES)\n    return kept, sizes, fams"),
    # ---- analyzer: pins ----
    (A, "frozen-import pin not enforced", "        if got != want:\n            raise ValueError(\n                f\"frozen file {path}", "        if False:\n            raise ValueError(\n                f\"frozen file {path}"),
    (A, "manifest own-sha pin not enforced", "    if pin is not None and got != pin:", "    if False:"),
    (A, "manifest: missing file not a failure", "            bad.append(f\"manifest: {rel} missing\")\n            continue", "            continue"),
    (A, "manifest: hash mismatch not a failure", "        if h != want:\n            bad.append(f\"manifest: {rel} hashes to {h}, pinned {want}\")", "        if False:\n            bad.append(f\"manifest: {rel} hashes to {h}, pinned {want}\")"),
    (A, "manifest: n_files self-consistency dropped", "    if rec.get(\"n_files\") != len(rec.get(\"files\", {})):\n        raise ValueError", "    if False:\n        raise ValueError"),
    (A, "tally pin: mismatch not a failure", "        if got != want:\n            bad.append(f\"tally pin: {rung}/{size} re-tallies to {got}, \"", "        if False:\n            bad.append(f\"tally pin: {rung}/{size} re-tallies to {got}, \""),
    (A, "tally pin: doc table altered", '"arith_next": (831, 531)', '"arith_next": (831, 532)'),
    (A, "2d comparison: field loop dropped", "        if cmp[k] != rec[k]:\n            bad.append", "        if False:\n            bad.append"),
    (A, "2d comparison: literal pin not compared", "    if rec != pin:\n        bad.append", "    if False:\n        bad.append"),
    (A, "2d literal: AUC altered", '"auc": 0.5454545454545454,\n                  "block_p"', '"auc": 0.5454545454545455,\n                  "block_p"'),
    (A, "collect: every exception swallowed", "    except (ValueError, FileNotFoundError) as e:", "    except Exception as e:"),
    (A, "collect: refusals raised (terminal unreachable)", "    except (ValueError, FileNotFoundError) as e:\n        return None, [f\"{label}: {e}\"]", "    except () as e:\n        return None, [f\"{label}: {e}\"]"),
    # ---- analyzer: run() routing ----
    (A, "run: tally pin check skipped", "        failures += check_tally_pin(main_cells, tally_pin)", "        pass"),
    (A, "run: comparison gate skipped", "            failures += check_comparison_2d(cmp, root, verdict_2d_pin)", "            pass"),
    (A, "run: failures do not route to INSUFFICIENT_DATA", "    if failures:\n        v = insufficient_data_record_2e(", "    if False:\n        v = insufficient_data_record_2e("),
    (A, "run: manifest check skipped", "    failures = check_manifest(root, manifest)", "    failures = []"),
    # ---- analyzer: the verdict ----
    (A, "primary reads F2", 'PRIMARY_FUNCTIONAL = "F1"', 'PRIMARY_FUNCTIONAL = "F2"'),
    (A, "primary reads B0", 'PRIMARY_FUNCTIONAL = "F1"', 'PRIMARY_FUNCTIONAL = "B0"'),
    (A, "caveat dropped from the record", '"known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2E,\n        "licensed_sentence_if_pass"', '"known_inputs_caveat": "",\n        "licensed_sentence_if_pass"'),
    (A, "sentence omits B0", 'f"null was its threshold\'s. B0 — the floor alone, −log c — "\n            f"scores AUC {b0_auc:.4f} on the same label', 'f"null was its threshold\'s. "\n            f"(baseline omitted) {b0_auc:.0f}'),
    (A, "sentence omits the disclosure", 'f"matches is a PASS about answer spaces). Disclosure: "\n            f"{KNOWN_INPUTS_CAVEAT_2E}")', 'f"matches is a PASS about answer spaces).")'),
    (A, "pilot replication reads the main tier", "    P1 = fn.f1_table(pilot_cells, floors)", "    P1 = fn.f1_table(main_cells, floors)"),
    (A, "1b-only replication reads 410m", 'vec({r: F1[r]["per_size"][REPLICATION_SIZE] for r in RUNGS}), y,\n        group, counts))\n    sec["replication_410m_only"]', 'vec({r: F1[r]["per_size"][OTHER_SIZE] for r in RUNGS}), y,\n        group, counts))\n    sec["replication_410m_only"]'),
    (A, "ε sensitivity rows read the primary ε", "        t = fn.f1_table(main_cells, floors, eps=e)", "        t = fn.f1_table(main_cells, floors)"),
    (A, "majority-only sensitivity reads the ruled floor", '    Fm = fn.f1_table(main_cells, floors, floor_key="majority_floor")', '    Fm = fn.f1_table(main_cells, floors, floor_key="floor")'),
    (A, "drop-two sensitivity keeps the 34", "    kept, sizes_r, fams_r = fn.drop_rungs_layout(FIRST_DIGIT_RUN_RUNGS)", "    kept, sizes_r, fams_r = fn.drop_rungs_layout(())"),
    (A, "F1 − B0 paired arms swapped", '    sec["f1_minus_b0"] = fn.cluster_bootstrap_auc_paired(\n        X["F1"], X["B0"], y, fams, counts=counts)', '    sec["f1_minus_b0"] = fn.cluster_bootstrap_auc_paired(\n        X["B0"], X["F1"], y, fams, counts=counts)'),
    (A, "label: 12b-only used as primary", '    y = a2d._labels(outcome, "rising")\n    y12', '    y = a2d._labels(outcome, "rising_12b")\n    y12'),
    (A, "per-rung F1 column decoupled from the tree input", '            "F1": float(X["F1"][i]),', '            "F1": float(X["F2"][i]),'),
    (A, "probe AUC pin check inert", '"auc_matches_2d_record": bool(pt["auc"] == PROBE_2C_AUC_PIN),', '"auc_matches_2d_record": True,'),
    (A, "insufficient record loses the caveat", '        "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2E,\n        "referents": referents,\n        "primary": None,', '        "known_inputs_caveat": None,\n        "referents": referents,\n        "primary": None,'),
    # ---- manifest builder ----
    (K, "builder: verdict.json not pinned", '    files.append(root / "results" / "verdict.json")\n    return files', '    return files'),
    (K, "builder: pilot tier not pinned", 'TIERS = ("pilot", "main")', 'TIERS = ("main", "main")'),
]

TESTS = [str(ROOT / "experiments/exp2e/tests")]
DESELECT = ["--deselect", "experiments/exp2e/tests/test_full_shape.py"]


def clear_pycache():
    for d in (ROOT / "experiments/exp2e").rglob("__pycache__"):
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
    print(f"[mutation] {applied - len([s for s in survivors if s[2] == 'survived'])}"
          f"/{applied} killed; {len(survivors)} survivor(s)")
    for s in survivors:
        print("   ", s)
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
