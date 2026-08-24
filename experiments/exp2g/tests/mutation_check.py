# experiments/exp2g/tests/mutation_check.py
"""Mutation-test the Exp 2g fixture suite. Targets: labels_2g,
strata_2g, stats_2g, probe_2g, checkpoints_2g, predictor_2g,
analyze_2g, run/sweep_2g. Mutates sources IN PLACE and restores them
— run alone, detached (nohup), never under a foreground timeout."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
G = ROOT / "experiments/exp2g"
L, S, T, P, C, R, A, W = (G / "labels_2g.py", G / "strata_2g.py", G / "stats_2g.py",
                          G / "probe_2g.py", G / "checkpoints_2g.py", G / "predictor_2g.py",
                          G / "analyze_2g.py", G / "run/sweep_2g.py")

M = [
    (L, "tens digit: hundreds", "return ans.zfill(3)[-2]", "return ans.zfill(3)[-3]"),
    (L, "hundreds digit: tens", "return ans.zfill(4)[-3]", "return ans.zfill(4)[-2]"),
    (L, "last digit: first", '    if kind == "last_digit":\n        return ans[-1]', '    if kind == "last_digit":\n        return ans[0]'),
    (L, "position: 0-based", "return str(hits[0] + 1)", "return str(hits[0])"),
    (L, "octal check dropped", "if not _OCTAL.fullmatch(ans):", "if False:"),
    (L, "label gate inert", "                if bad:\n                    raise ValueError(\n                        f\"{rung}/{which}", "                if False:\n                    raise ValueError(\n                        f\"{rung}/{which}"),
    (L, "arith_next: 2f-label gate inert", "                if bad_2f:\n                    raise ValueError(\n                        f\"{rung}/{which}: the last-digit label disagrees \"", "                if False:\n                    raise ValueError(\n                        f\"{rung}/{which}: the last-digit label disagrees \""),
    (L, "arith_next: mod7 gate inert", "                if bad_mod7:\n                    raise ValueError(\n                        f\"{rung}/{which}: the committed probe_label \"", "                if False:\n                    raise ValueError(\n                        f\"{rung}/{which}: the committed probe_label \""),
    (L, "floor: majority only", '"floor": float(max(maj, 1.0 / K))', '"floor": float(maj)'),
    (S, "carries: threshold 9", "carry = 1 if x + y + carry >= 10 else 0", "carry = 1 if x + y + carry >= 9 else 0"),
    (S, "borrows: no propagation", "borrow = 1 if x - y - borrow < 0 else 0", "borrow = 1 if x - y < 0 else 0"),
    (S, "octal carry: >= 7", "return int(int(a[-1]) + int(b[-1]) >= 8)", "return int(int(a[-1]) + int(b[-1]) >= 7)"),
    (S, "crosses_100: > 100", "return int(int(ans) >= 100)", "return int(int(ans) > 100)"),
    (S, "merge: floor 5", "MIN_STRATUM = 10", "MIN_STRATUM = 5"),
    (S, "merge: larger neighbour", "j = min(nb, key=lambda k: (size(groups[k]), k))", "j = max(nb, key=lambda k: (size(groups[k]), k))"),
    (S, "merge: nominal merged too", "    if kind in NOMINAL:\n        level_map = {lvl: str(lvl) for lvl in sorted(raw)}", "    if False:\n        level_map = {lvl: str(lvl) for lvl in sorted(raw)}"),
    (S, "strata pin inert", "        if got != RAW_COUNT_PIN[rung]:", "        if False:"),
    (T, "D: y ties counted", "        sy = np.where(mask, sy, 0).astype(np.int8)", "        sy = np.where(mask, np.where(sy == 0, 1, sy), 0).astype(np.int8)"),
    (T, "D: cross-stratum pairs", "    for s in sorted(set(strata.tolist())):\n        idx = np.flatnonzero(strata == s)\n        ys = y[idx]", "    for s in [None]:\n        idx = np.arange(len(y))\n        ys = y[idx]"),
    (T, "perm: p without add-one", '"p": (1 + ge) / (1 + n_perm)', '"p": ge / n_perm'),
    (T, "perm: two-sided", "    ge = int((null >= T_obs).sum())", "    ge = int((np.abs(null) >= abs(T_obs)).sum())"),
    (T, "perm: across strata", "        out[idx] = x[rng.permutation(idx)]", "        out[idx] = x[idx]\n    out = out[rng.permutation(len(out))]"),
    (T, "T: pooled instead of mean", "    T_obs = float(np.mean([v[\"d\"] for v in per_rung.values()]))", "    T_obs = float(np.sum([v[\"d\"] * v[\"n_pairs\"] for v in per_rung.values()]) / np.sum([v[\"n_pairs\"] for v in per_rung.values()]))"),
    (T, "bar: .05", "T_BAR = 0.10", "T_BAR = 0.05"),
    (T, "alpha: .05", "ALPHA = 0.01              # primary", "ALPHA = 0.05              # primary"),
    (P, "cv: holdout 0 (train==val)", "CV_HOLDOUT = 0.2", "CV_HOLDOUT = 0.0"),
    (P, "cv tie: highest site", "    site = next(s for s in sites if per_site[site_key(s)] == best)\n    return tuple(int(v) for v in site), per_site, split", "    site = [s for s in sites if per_site[site_key(s)] == best][-1]\n    return tuple(int(v) for v in site), per_site, split"),
    (P, "scores: max class instead of true", "    return lp[np.arange(len(y)), [col[v] for v in y]]", "    return lp.max(axis=1)"),
    (P, "missing class silently dropped", "    if missing:\n        raise ValueError", "    if False:\n        raise ValueError"),
    (C, "candidate: single safetensors always", "    if single is not None and (rev == \"main\" or single[0] != main_single):", "    if single is not None:"),
    (C, "manifest: duplicates allowed", "        if step != bg.FINAL_STEP and same:\n            raise ValueError", "        if False:\n            raise ValueError"),
    (C, "manifest: exclusion unjustified allowed", "            if not same:\n                raise ValueError", "            if False:\n                raise ValueError"),
    (C, "load_manifest: grid check inert", "        if not m or m.get(\"grid\") != list(bg.GRID[size]) or \\", "        if False or \\"),
    (R, "seal: tag check inert", "    if not tag_exists(bg.SEAL_TAG):", "    if False:"),
    (R, "seal: blob sha not compared", "    if at_tag != got:", "    if False:"),
    (R, "load_predictor: length pin inert", "                if len(c[\"scores\"]) != bg.N_ITEMS or \\", "                if False or \\"),
    (A, "power sha pin inert", "    if sha_pin is not None and got != sha_pin:", "    if False:"),
    (A, "gate 1: counts not compared", "        elif counts[r] != bg.FINAL_COUNT_PIN[size][r]:", "        elif False:"),
    (A, "gate 1: digests not compared", "    if not da or not db or da != db:", "    if False:"),
    (A, "gate 1: continuation diffs ignored", "        if cd.get(r) != 0:", "        if False:"),
    (A, "step record: re-verification dropped", "    if re != [int(b) for b in bits]:", "    if False:"),
    (A, "step record: commit not compared", "    if rec.get(\"commit\") != want_commit:", "    if False:"),
    (A, "step record: seal not compared", "    if rec.get(\"predictor_sha\") != seal_sha:", "    if False:"),
    (A, "outcomes: step0 counted", "            hits = [s for s in steps if bits[s][i]]", "            hits = [s for s in sweep if bits[s][i]]"),
    (A, "tree: twin threshold at .01", "        if p_tw >= ALPHA_TWIN:", "        if p_tw >= ALPHA:"),
    (A, "tree: effect bar dropped", "    if p < ALPHA and T >= T_BAR:", "    if p < ALPHA:"),
    (A, "tree: DIFFICULTY-ONLY needs raw only", "    if p_raw < ALPHA and p >= ALPHA:", "    if p_raw < ALPHA:"),
    (A, "eligibility floor 0", "              rule=\"cv\", one_stratum=False, y_key=\"y\", min_pos=bg.ELIGIBILITY_MIN_POS,", "              rule=\"cv\", one_stratum=False, y_key=\"y\", min_pos=0,"),
    (A, "load_sweep: missing record tolerated", "            if not p.is_file():\n                raise FileNotFoundError(f\"sweep record missing: {p}\")", "            if not p.is_file():\n                continue"),
    (W, "runner: seal not required", "    seal = pr.require_seal(out_root, tag_exists=tag_exists, blob_sha=blob_sha)", "    seal = {\"tag\": bg.SEAL_TAG, \"sha256\": \"unsealed\"}"),
    (W, "runner: halt marker not written", "        bg.halt_marker_path(out_root, size).write_text(\"\\n\".join(failures) + \"\\n\")", "        pass"),
    (W, "runner: gate 1 skipped when diff", "    if failures:\n        _write(bg.gate1_path(out_root, size), rec)\n        bg.halt_marker_path", "    if False:\n        _write(bg.gate1_path(out_root, size), rec)\n        bg.halt_marker_path"),
    (W, "runner: final records before the gate", "    failures = an.gate1_failures(rec, size)", "    failures = []"),
]

TESTS = [str(G / "tests")]
DESELECT = ["--deselect", "experiments/exp2g/tests/test_full_shape.py"]


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp2g" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def run_suite():
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                        *TESTS, *DESELECT], cwd=ROOT, env=env, capture_output=True, text=True)
    return r.returncode == 0, r.stdout[-600:]


def main(argv=None) -> int:
    clear_pycache()
    ok, out = run_suite()
    if not ok:
        print("BASELINE FAILS — fix the suite first\n", out)
        return 2
    survivors = []
    for i, (path, name, old, new) in enumerate(M, 1):
        src = path.read_text()
        if src.count(old) != 1:
            print(f"[{i:2d}] SKIP  {name}: target text not found exactly once in {path.name}")
            survivors.append((i, name, "target-not-found"))
            continue
        backup = path.with_suffix(path.suffix + ".mutation_backup")
        shutil.copy2(path, backup)
        try:
            path.write_text(src.replace(old, new))
            clear_pycache()
            ok, out = run_suite()
        finally:
            shutil.copy2(backup, path)
            backup.unlink()
            clear_pycache()
        print(f"[{i:2d}] {'killed' if not ok else 'SURVIVED'}  {name}", flush=True)
        if ok:
            survivors.append((i, name, "survived"))
    print(f"\n{len(M) - len(survivors)}/{len(M)} killed; survivors: {survivors}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
