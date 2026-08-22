"""Mutation-test the Exp 2f fixture suite, both directions. Targets:
labels_2f.py, probe_2f.py, analyze_2f.py, make_referents_2f.py,
collect_eval_2f.py. 3a's corrected harness (pycache cleared,
PYTHONDONTWRITEBYTECODE=1); the full-shape worlds deselected (the
module world in test_analyze_2f covers run()'s routing). Mutates
sources IN PLACE and restores them — run alone, detached.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
L = ROOT / "experiments/exp2f/labels_2f.py"
P = ROOT / "experiments/exp2f/probe_2f.py"
A = ROOT / "experiments/exp2f/analyze_2f.py"
K = ROOT / "experiments/exp2f/make_referents_2f.py"
C = ROOT / "experiments/exp2f/collect_eval_2f.py"

M = [
    # ---- labels (§3) ----
    (L, "mid digit: first digit instead", 'return digits.zfill(3)[1]', 'return digits.zfill(3)[0]'),
    (L, "mid digit: 4-digit answers accepted", "        if not 1 <= len(digits) <= 3:\n            return MISS", "        if not 1 <= len(digits) <= 4:\n            return MISS"),
    (L, "last digit: first digit", '        return digits[-1]', '        return digits[0]'),
    (L, "mod7: mod 10", '        return str(int(digits) % 7)', '        return str(int(digits) % 10)'),
    (L, "emission: negative accepted", "    if not s or not _DIGITS.fullmatch(s):\n        return MISS", "    if not s:\n        return MISS\n    s = s.lstrip('-')\n    if not _DIGITS.fullmatch(s):\n        return MISS"),
    (L, "emission: not 2c's normalizer (whole text)", '    return bt.harness_2c().normalize_answer(text, ANSWER_TYPE)', '    return text.strip().split()[0] if text.strip() else ""'),
    (L, "floor: majority only (1/K dropped)", '                "floor": float(max(maj, 1.0 / K)),', '                "floor": float(maj),'),
    (L, "floor: 1/K only", '                "floor": float(max(maj, 1.0 / K)),', '                "floor": float(1.0 / K),'),
    (L, "probe-label gate inert", "        if bad:\n            raise ValueError(\n                f\"{rung}: the committed probe_label", "        if False:\n            raise ValueError(\n                f\"{rung}: the committed probe_label"),
    (L, "primary label for arith_next = mod7", 'PRIMARY = {"sub3_mid": "mid_digit", "arith_next": "last_digit"}', 'PRIMARY = {"sub3_mid": "mid_digit", "arith_next": "mod7"}'),
    # ---- probe (§5) ----
    (P, "family: every layer", "    keep = sorted(set(range(0, n_layers, LAYER_STRIDE)) | {n_layers - 1})", "    keep = sorted(set(range(0, n_layers)))"),
    (P, "family: final layer dropped", "    keep = sorted(set(range(0, n_layers, LAYER_STRIDE)) | {n_layers - 1})", "    keep = sorted(set(range(0, n_layers, LAYER_STRIDE)))"),
    (P, "probe: C changed", "C = ps.C", "C = 100.0"),
    (P, "detect: Bonferroni dropped", "    corrected = list(bonferroni(raw))", "    corrected = list(raw)"),
    (P, "detect: rate-above-floor conjunct dropped", "    detected = bool(corrected[best] < alpha and accs[best] > floor)", "    detected = bool(corrected[best] < alpha)"),
    (P, "detect: best by accuracy only", "    best = min(range(len(sites)), key=lambda i: (corrected[i], -accs[i]))", "    best = max(range(len(sites)), key=lambda i: accs[i])"),
    (P, "void rule dropped", "    void = bool(twin_detects_at_best)", "    void = False"),
    (P, "trained-exceeds-twin dropped", "        d = bool(tr[\"detected\"] and exceeds)", "        d = bool(tr[\"detected\"])"),
    (P, "twin read at its own best site, not trained's", "    tw_at_best = tw[\"per_site\"][best]", "    tw_at_best = tw[\"per_site\"][_key(tw[\"best_site\"])]"),
    (P, "starved: thinning dropped", "    act = thin(act)\n    train_idx, val_idx, info = starving_split", "    train_idx, val_idx, info = starving_split"),
    (P, "starved: best by min accuracy", "    best = max(sites, key=lambda s: per[s][\"acc\"])", "    best = min(sites, key=lambda s: per[s][\"acc\"])"),
    (P, "cv: holdout ignored (train == val)", "    val_idx, tr_idx = perm[:n_val], perm[n_val:]", "    val_idx, tr_idx = perm[:n_val], perm"),
    # ---- analyzer: pins & gates ----
    (A, "frozen-import pin inert", "        if got != want:\n            raise ValueError(f\"frozen file {path} has sha256 {got}, expected \"", "        if False:\n            raise ValueError(f\"frozen file {path} has sha256 {got}, expected \""),
    (A, "exact pin: 831 altered", '("arith_next", "410m", "main"): 831', '("arith_next", "410m", "main"): 830'),
    (A, "exact pin: mismatch not a failure", "        elif got != want:\n            bad.append(f\"exact-match pin:", "        elif False:\n            bad.append(f\"exact-match pin:"),
    (A, "npz sha pin inert", "    if sha_pin is not None and got != sha_pin:", "    if False:"),
    (A, "probe y gate inert", "    if len(y) != len(items) or [str(v) for v in y] != \\\n            [str(it[\"probe_label\"]) for it in items]:", "    if False:"),
    (A, "m3 gate: mismatch not a failure", "        if got != pin:\n            bad.append(f\"m3 gate", "        if False:\n            bad.append(f\"m3 gate"),
    (A, "m3 literal altered", '("arith_next", "1b"): {"accuracy": 0.13535911602209943, "best_site": [0, 0],\n                           "n_train": 638', '("arith_next", "1b"): {"accuracy": 0.13535911602219943, "best_site": [0, 0],\n                           "n_train": 638'),
    (A, "continuity: tolerance not enforced", "        if not (d.get(\"max_rel_diff\", 1e9) <= CONTINUITY_RTOL\n                and d.get(\"max_abs_diff\", 1e9) <= CONTINUITY_ATOL):", "        if False:"),
    (A, "continuity: n_compared not enforced", "        if d.get(\"n_compared\") != CONTINUITY_N:", "        if False:"),
    (A, "continuity: runner's pass trusted", "    rec[\"pass\"] = continuity_pass(rec) == []\n    return rec", "    rec[\"pass\"] = True\n    return rec"),
    (A, "eval meta: model_sha not enforced", "    for k, v in want.items():\n        if k == \"stack\":\n            continue", "    for k, v in want.items():\n        if k in (\"stack\", \"model_sha\"):\n            continue"),
    (A, "eval meta: n_layers not enforced", "    for k, v in want.items():\n        if k == \"stack\":\n            continue\n        if meta.get(k) != v:", "    for k, v in want.items():\n        if k in (\"stack\", \"n_layers\"):\n            continue\n        if meta.get(k) != v:"),
    (A, "eval y not the answers", "    if [str(v) for v in y] != answers:\n        raise ValueError", "    if False:\n        raise ValueError"),
    (A, "manifest: hash mismatch not a failure", "        if h != want:\n            bad.append(f\"manifest: {rel} hashes to {h}, pinned {want}\")", "        if False:\n            bad.append(f\"manifest: {rel} hashes to {h}, pinned {want}\")"),
    (A, "manifest own sha not enforced", "    if pin is not None and got != pin:\n        raise ValueError(f\"{path} has sha256 {got} against the pinned {pin}\")", "    if False:\n        raise ValueError(f\"{path} has sha256 {got} against the pinned {pin}\")"),
    # ---- analyzer: tallies, bar, tree ----
    (A, "tallies: MISS counted as match", "        if lab is lb.MISS:\n            miss += 1\n        elif lab == lb.answer_label(kind, ans):\n            match += 1", "        if lab is lb.MISS:\n            miss += 1\n            match += 1\n        elif lab == lb.answer_label(kind, ans):\n            match += 1"),
    (A, "tallies: exact via label equality", "        if lb.exact_match(lb.ANSWER_TYPE, d, ans):\n            exact += 1", "        if lab is not lb.MISS and lab == lb.answer_label(kind, ans):\n            exact += 1"),
    (A, "bar: significant replaced by rate > floor", '            "D": bool(bar["significant"]), "cp95": [lo, hi],', '            "D": bool(match / n > floor), "cp95": [lo, hi],'),
    (A, "monotone: probe ≤ sampling (reversed)", "    return g <= s <= p", "    return p <= s <= g"),
    (A, "monotone: argmax-without-sampler allowed", "    return g <= s <= p", "    return s <= p"),
    (A, "tree: void cells counted as violations", "    live = {k: c for k, c in cells.items() if not c[\"void\"]}\n    viol", "    live = dict(cells)\n    viol"),
    (A, "tree: both-void branch dropped", "    if n_void_arith >= 2:", "    if False:"),
    (A, "tree: referent branch dropped", "    if referent_failures:\n        return {\"verdict\": \"INSUFFICIENT_DATA\",\n                \"reason\": f\"{len(referent_failures)} referent failure(s): \"", "    if False:\n        return {\"verdict\": \"INSUFFICIENT_DATA\",\n                \"reason\": f\"{len(referent_failures)} referent failure(s): \""),
    (A, "tree: SILENT returned as LADDER", "    if n_det > 0:\n        return {\"verdict\": \"LADDER\",", "    if True:\n        return {\"verdict\": \"LADDER\","),
    (A, "cell: D reads the pilot tier", "    D = [probe[\"D_probe\"], sampling[\"main\"][\"D\"], argmax[\"D\"]]", "    D = [probe[\"D_probe\"], sampling[\"pilot\"][\"D\"], argmax[\"D\"]]"),
    (A, "cell: probe labels computed from the committed probe_label (wrong kind)", "    y_train = [lb.answer_label(kind, it[\"answer\"]) for it in cap[\"probe_items\"]]", "    y_train = [str(it[\"probe_label\"]) for it in cap[\"probe_items\"]]"),
    (A, "run: exact gate not applied", "    ef = check_exact_pin(tallies, exact_pin) if tallies else []", "    ef = []"),
    (A, "run: continuity failures not collected", "    failures += cf\n", "    pass\n"),
    (A, "run: m3 failures not collected", "        failures += f + mf", "        failures += f"),
    (A, "run: caveat dropped", '        v = {"verdict": tree["verdict"], "reason": tree["reason"],\n             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2F,\n             "licensed_sentence": LICENSED[tree["verdict"]],', '        v = {"verdict": tree["verdict"], "reason": tree["reason"],\n             "known_inputs_caveat": "",\n             "licensed_sentence": LICENSED[tree["verdict"]],'),
    (A, "run: arith_next void count ignores one size", "        n_void_arith = sum(1 for s in SIZES\n                           if cells[_cell_key(\"arith_next\", s)][\"void\"])", "        n_void_arith = int(cells[_cell_key(\"arith_next\", SIZES[0])][\"void\"])"),
    # ---- builder / collector ----
    (K, "builder: activation files not pinned", "            for mode in MODES:\n                files.append(probe_npz_path(size, mode, rung,\n                                            probe_root=probe_root))", "            for mode in MODES[:0]:\n                files.append(probe_npz_path(size, mode, rung,\n                                            probe_root=probe_root))"),
    (C, "collector: identical claimed unconditionally", '            "identical": bool(np.array_equal(new, com))}', '            "identical": True}'),
    (C, "collector: shape mismatch accepted", "    if new.shape != com.shape:\n        raise ValueError", "    if False:\n        raise ValueError"),
]

TESTS = [str(ROOT / "experiments/exp2f/tests")]
DESELECT = ["--deselect", "experiments/exp2f/tests/test_full_shape.py"]


def clear_pycache():
    for d in (ROOT / "experiments/exp2f").rglob("__pycache__"):
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
