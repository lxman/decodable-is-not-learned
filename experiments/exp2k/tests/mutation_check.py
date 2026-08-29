# experiments/exp2k/tests/mutation_check.py
"""Mutation-test exp2k's OWN modules — battery_2k (readers, bits/counts,
the tier-record checker, seed freshness, matched-k, the prereg
binding), run/tier_2k (the gate-1 comparison and halt path), and
analyze_2k (the 2k tier loader, the seal/power checkers, the tree,
S1-S7's machinery, the comparison/block gates, the import-surface
scan, and every `collect_total` call site in `run()` and
`load_2i_tree`/`load_tier_2k`, AST-generated via 2i's own
`_totality_mutants`, imported verbatim rather than re-implemented).
Everything upstream of 2k (2i/2j/2g/2h/2d/2c/exp3/exp3c/exp3d) is
frozen instrument, pinned by `FROZEN_SHA256_2K`/`FROZEN_IMPORT_SHA256_2G`,
and is not re-targeted here.

Task 5's ruling (2j's precedent): run each mutant against the FAST
modules only (`test_battery_2k.py`, `test_tier_2k.py`,
`test_analyze_2k.py` — under a minute together); the world/totality
modules take 4-7 minutes each and would make a ~55-mutant run a
many-hour one. A mutant that survives the fast modules is either
closed with a new fast test (preferred) or, when only a world/totality
shape can observe the behaviour it changes, recorded as 'killed by
worlds/totality only' after one targeted confirmation run — see
PROGRESS.md's Task 5 entry for which mutants took that path and for
any documented-equivalent mutant (a proof in the ledger, not merely an
assertion — 2j's `matched_k` clip precedent).

Mutates sources IN PLACE (with a `.mutation_backup` copy) and restores
them in `finally` — run alone, detached (nohup), never under a
foreground timeout."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.exp2i.tests.mutation_check import _totality_mutants  # noqa: E402

K = ROOT / "experiments/exp2k"
BK = K / "battery_2k.py"
TK = K / "run" / "tier_2k.py"
AN = K / "analyze_2k.py"

M = [
    # -------------------------------------------------------- battery_2k.py
    (BK, "read_rows_2k: seed-set exact-match loosened to subset-accepted",
     '            if not isinstance(draws, dict) or set(draws) != want:',
     '            if not isinstance(draws, dict) or not (set(draws) <= want):'),
    (BK, "read_rows_2k: draws_per_seed exact-match loosened to a floor (>dps silently accepted)",
     '                if not isinstance(stream, list) or len(stream) != dps or \\',
     '                if not isinstance(stream, list) or len(stream) < dps or \\'),
    (BK, "counts_at_k: prefix b[:k] widened to b[:k+1]",
     '    return [int(sum(b[:k])) for b in bits]',
     '    return [int(sum(b[:k + 1])) for b in bits]'),
    (BK, "block_counts: slice start off by one (b * 64 -> b * 64 + 1)",
     '    return [int(sum(row[b * DRAWS_PER_SEED:(b + 1) * DRAWS_PER_SEED])) for row in bits]',
     '    return [int(sum(row[b * DRAWS_PER_SEED + 1:(b + 1) * DRAWS_PER_SEED])) for row in bits]'),
    (BK, "bits_2k: seed order reversed (breaks the seed-ordered prefix every counts_at_k reads)",
     '        for s in SEEDS_2K:\n'
     '            b.extend(int(bool(verify_fn(d, ans, at))) for d in row["draws"][str(s)])',
     '        for s in reversed(SEEDS_2K):\n'
     '            b.extend(int(bool(verify_fn(d, ans, at))) for d in row["draws"][str(s)])'),
    (BK, "tallies_2k: every seed's tally reads seed 0's draws (n_draws/full_string counting "
         "only seed 0)",
     '            for d in row["draws"][str(s)]:',
     '            for d in row["draws"]["0"]:'),
    (BK, "tier_record_failures_2k: gate1 n_diffs != 0 check removed",
     '        if g.get("n_diffs") != 0:\n'
     '            bad.append(f"{label}: gate1 n_diffs = {g.get(\'n_diffs\')!r} (the runner should "\n'
     '                       f"have halted)")',
     '        if False:\n'
     '            bad.append(f"{label}: gate1 n_diffs = {g.get(\'n_diffs\')!r} (the runner should "\n'
     '                       f"have halted)")'),
    (BK, "tier_record_failures_2k: gate1 items_compared exact-match loosened to a floor",
     '        if g.get("items_compared") != N_ITEMS:',
     '        if g.get("items_compared") < N_ITEMS:'),
    (BK, "tier_record_failures_2k: committed_sha comparison removed",
     '        if committed_sha is not None and g.get("committed_draws_sha256") != committed_sha:\n'
     '            bad.append(f"{label}: gate1 committed_draws_sha256 {g.get(\'committed_draws_sha256\')!r}"\n'
     '                       f" is not 2i\'s pinned {committed_sha!r} for the cell")',
     '        if False:\n'
     '            bad.append(f"{label}: gate1 committed_draws_sha256 {g.get(\'committed_draws_sha256\')!r}"\n'
     '                       f" is not 2i\'s pinned {committed_sha!r} for the cell")'),
    (BK, "TIER_RECORD_PINS_2K: model_sha dropped from the pinned-field tuple",
     '"stream_namespace", "model_sha")',
     '"stream_namespace")'),
    (BK, "stream_collisions: 2d's own map silently skipped",
     '    for mp in STREAM_MAPS:\n'
     '        cells = _cells_of(mp)',
     '    for mp in STREAM_MAPS:\n'
     '        if mp.name == "stream_map_2d.json":\n'
     '            continue\n'
     '        cells = _cells_of(mp)'),
    (BK, "check_seed_freshness: the seed-0-is-2d's-main-tier assertion removed",
     '            if not any("stream_map_2d" in h for h in stream_collisions(rung, size, (GATE1_SEED,))):',
     '            if False and not any("stream_map_2d" in h '
     'for h in stream_collisions(rung, size, (GATE1_SEED,))):'),
    (BK, "matched_k_256: the cap condition >= loosened to > (a tie no longer caps at 64)",
     '    if rate_b64 <= 0 or 256.0 * rate_a64 >= 64.0 * rate_b64:',
     '    if rate_b64 <= 0 or 256.0 * rate_a64 > 64.0 * rate_b64:'),
    (BK, "matched_k_256: floor(x + 0.5) rounding replaced by truncation",
     '    k = int(np.floor(K_TOTAL * rate_a64 / rate_b64 + 0.5))',
     '    k = int(K_TOTAL * rate_a64 / rate_b64)'),
    (BK, "require_prereg_2k: blob-binding mismatch inverted (want == got raises instead of !=)",
     '        if want != got:',
     '        if want == got:'),
    # -------------------------------------------------------------- tier_2k.py
    (TK, "run_rung: gate-1 diff comparison inverted (g != w -> g == w)",
     'if g != w]',
     'if g == w]'),
    (TK, "run_rung: the HALTED marker is no longer written on a gate-1 fire",
     '            m = bk.halt_marker_path(out_root, size, rung)\n'
     '            m.parent.mkdir(parents=True, exist_ok=True)\n'
     '            m.write_text(json.dumps({"rung": rung, "size": size, "item": i,\n'
     '                                     "items_compared": i + 1, "n_diffs": len(diffs),\n'
     '                                     "diffs": diffs[:5], "model_sha": model_sha,\n'
     '                                     "committed_draws_sha256": committed_gz_sha,\n'
     '                                     "stack": _stack(), "git_sha": _git_sha()}, indent=1))',
     '            m = bk.halt_marker_path(out_root, size, rung)\n'
     '            if False:\n'
     '                m.parent.mkdir(parents=True, exist_ok=True)\n'
     '                m.write_text(json.dumps({"rung": rung, "size": size, "item": i,\n'
     '                                         "items_compared": i + 1, "n_diffs": len(diffs),\n'
     '                                         "diffs": diffs[:5], "model_sha": model_sha,\n'
     '                                         "committed_draws_sha256": committed_gz_sha,\n'
     '                                         "stack": _stack(), "git_sha": _git_sha()}, indent=1))'),
    (TK, "run_rung: the normal draws file is ALSO written on a halt (skip-if-exists would then "
         "treat a halted rung as done)",
     '            write_draws(bk.halted_draws_path(out_root, size, rung), rows)',
     '            write_draws(bk.halted_draws_path(out_root, size, rung), rows)\n'
     '            write_draws(dpath, rows)'),
    (TK, "run_rung: _refuse_if_halted removed (a halted tree no longer refuses a later call)",
     '    _refuse_if_halted(out_root)\n'
     '    from experiments.exp3.sampler import sample_item',
     '    from experiments.exp3.sampler import sample_item'),
    (TK, "run_rung: the model_sha refusal removed",
     '    if model_sha != bk.pythia_sha(size):\n'
     '        raise RuntimeError(f"model_sha {model_sha!r} is not 2b\'s pinned {bk.pythia_sha(size)!r} "\n'
     '                           f"for {size} — not the weights 2d sampled")',
     '    if False:\n'
     '        raise RuntimeError(f"model_sha {model_sha!r} is not 2b\'s pinned {bk.pythia_sha(size)!r} "\n'
     '                           f"for {size} — not the weights 2d sampled")'),
    (TK, "run_rung: the per-item coverage diff (wrong draw count) no longer detected",
     '        if len(mine) != bk.DRAWS_PER_SEED or len(theirs) != bk.DRAWS_PER_SEED:',
     '        if False:'),
    # -------------------------------------------------------------- analyze_2k.py
    (AN, "verdict_tree_2k: the firing branch reports NOT-DENSITY instead of DENSITY",
     '        return {"verdict": "DENSITY", "annotation": None, "declared_status": status,',
     '        return {"verdict": "NOT-DENSITY", "annotation": None, "declared_status": status,'),
    (AN, "verdict_tree_2k: the structured/null annotation boundary decoupled from ALPHA "
         "(p < ALPHA -> p < 0.05, ALPHA is 0.01)",
     '    annotation = "structured" if (T is not None and p < ALPHA) else "null"',
     '    annotation = "structured" if (T is not None and p < 0.05) else "null"'),
    (AN, "_licensed: the POWERED branch returns the UNDERPOWERED licence",
     '        elif tree["declared_status"] == "POWERED":\n'
     '            licensed = LICENSED_2K["NOT-DENSITY"]',
     '        elif tree["declared_status"] == "POWERED":\n'
     '            licensed = LICENSED_2K["NOT-DENSITY_UNDERPOWERED"]'),
    (AN, "load_tier_2k/_gate: the gate-1 diff check removed",
     '            if diffs:\n'
     '                raise ValueError(f"gate 1: {len(diffs)} seed-0 draw(s) differ from 2d\'s "\n'
     '                                 f"committed bytes (first {diffs[0]})")',
     '            if False:\n'
     '                raise ValueError(f"gate 1: {len(diffs)} seed-0 draw(s) differ from 2d\'s "\n'
     '                                 f"committed bytes (first {diffs[0]})")'),
    (AN, "load_tier_2k/_gate: the draws_compared attestation check removed",
     '            if rec["gate1"].get("draws_compared") != n_cmp:',
     '            if False:'),
    (AN, "load_tier_2k/_bits: the per_seed_tallies re-derivation check removed",
     '            if t != rec.get("per_seed_tallies"):',
     '            if False:'),
    (AN, "load_tier_2k: committed_sha argument dropped from the record check",
     '        bad = bk.tier_record_failures_2k(rec, size=size, rung=rung, cap=cap,\n'
     '                                         committed_sha=bi.PYTHIA_PREDICTOR_FILES[(size, rung)])',
     '        bad = bk.tier_record_failures_2k(rec, size=size, rung=rung, cap=cap)'),
    (AN, "seal_failures_2k: the 256-draw counts check removed",
     '            if got != c["counts"][bk.K_TOTAL]:',
     '            if False:'),
    (AN, "seal_failures_2k: the counts_by_k ladder check removed",
     '                if gk != c["counts"][k]:',
     '                if False:'),
    (AN, "seal_failures_2k: the per-file sha check removed",
     '            if not p.is_file() or bg.sha256_file(p) != sha:',
     '            if False:'),
    (AN, "seal_failures_2k: the composite sha256 check removed",
     '        if seal.get("sha256") != seal_sha_of(files):',
     '        if False:'),
    (AN, "load_power_2k: the rung-set equality loosened to a subset check",
     '    if set(prim.get("rungs", [])) != set(r_cap):',
     '    if not set(r_cap).issubset(set(prim.get("rungs", []))):'),
    (AN, "load_power_2k: the predictor_sha256 check removed",
     '    if rec.get("predictor_sha256") != seal_sha:\n'
     '        raise ValueError(f"{p}: predictor_sha256 {rec.get(\'predictor_sha256\')!r} is not the "\n'
     '                         f"sealed predictor\'s {seal_sha!r} — the record is a claim about a "\n'
     '                         f"different predictor")',
     '    if False:\n'
     '        raise ValueError(f"{p}: predictor_sha256 {rec.get(\'predictor_sha256\')!r} is not the "\n'
     '                         f"sealed predictor\'s {seal_sha!r} — the record is a claim about a "\n'
     '                         f"different predictor")'),
    (AN, "run()/_cmp: the x_A^(64)-vs-2d comparison loop removed (world/totality only)",
     '            for s in bk.SIZES_2K:\n'
     '                from_2d = bi.sampler_counts_pythia(s, r_cap)',
     '            for s in ():\n'
     '                from_2d = bi.sampler_counts_pythia(s, r_cap)'),
    (AN, "run()/_cmp: the per-rung d comparison loop removed (world/totality only)",
     '            for r in r_cap:\n'
     '                if a["per_rung"].get(r, {}).get("d") != on_disk["per_rung"].get(r):',
     '            for r in ():\n'
     '                if a["per_rung"].get(r, {}).get("d") != on_disk["per_rung"].get(r):'),
    (AN, "run()/_core: the block gate inverted (raises on a correct reproduction) — "
         "world/totality only",
     '            if t64 != comparison["A64"]["stratified"]["T"]:',
     '            if t64 == comparison["A64"]["stratified"]["T"]:'),
    (AN, "run(): the halt-marker scan removed — a halted tree no longer refuses",
     '    for m in bk.halt_markers(root_2k):',
     '    for m in []:'),
    (AN, "s1_blocks: sd uses ddof=0 instead of ddof=1",
     '            "sd": float(np.std(finite, ddof=1)) if len(finite) > 1 else None,',
     '            "sd": float(np.std(finite, ddof=0)) if len(finite) > 1 else None,'),
    (AN, "placement_on_ladder: log2 interpolation replaced by linear interpolation in k",
     '            return {"k_equivalent": float(2 ** (np.log2(lo) + frac * (np.log2(hi) - np.log2(lo)))),',
     '            return {"k_equivalent": float(lo + frac * (hi - lo)),'),
    (AN, "s3_matched: n_blocks hardcoded to 1 (the block machinery's block count ignored)",
     '        reading = an2j._block_reading(r, bits_b[r], m["k"], m["n_blocks"], bi.SIZE_PRED, out, strata)',
     '        reading = an2j._block_reading(r, bits_b[r], m["k"], 1, bi.SIZE_PRED, out, strata)'),
    (AN, "ladder_2k: iterates only k in (64, 256), dropping 128/192",
     '                         out, strata, rungs, **kw) for k in bk.LADDER_K}',
     '                         out, strata, rungs, **kw) for k in (64, 256)}'),
    (AN, "check_imports_2k: the tests/-directory exclusion swallows everything "
         "('tests' in rp.parts -> True)",
     '        if not s.startswith(_EXPERIMENTS_ROOT_2K + "/") or "tests" in rp.parts:',
     '        if not s.startswith(_EXPERIMENTS_ROOT_2K + "/") or True:'),
]

# One mutant per collect_total(...) call site in analyze_2k.py's run() AND
# load_2i_tree/load_tier_2k, generated from the real, current source at
# import time rather than hand-picked (2j's Finding 4 lesson, one
# experiment later — this file has THREE functions with collect_total
# sites, not one, and _totality_mutants walks the whole file).
M += _totality_mutants(AN)

# Task 5 ruling: fast modules only by default — the world/totality modules
# (test_full_shape_2k.py, test_totality_2k.py) take 4-7 minutes each. A
# `--totality` flag switches the covering suite to TOTALITY_TESTS so a
# totality-only kill is reproducible from the committed harness, not a
# scratch script.
TESTS = [str(K / "tests" / "test_battery_2k.py"), str(K / "tests" / "test_tier_2k.py"),
         str(K / "tests" / "test_analyze_2k.py")]
# 2j's precedent: totality confirmation is test_totality_2k.py ALONE (~4
# min) — its forced-exception injections are exactly what a stripped
# collect_total / inverted refusal-gate mutant needs to be observed by.
TOTALITY_TESTS = [str(K / "tests" / "test_totality_2k.py")]
# A handful of comparison-gate mutants (run()/_cmp's x_A^(64)-vs-2d and
# per-rung-d loops) are shielded by gate 1 in every tree test_totality_2k.py
# builds (seed 0 is always the real committed row, so those two loops can
# never find a real mismatch there) and by load_tier_2k's own gate-1
# re-derivation (_gate) similarly. Only test_full_shape_2k.py's worlds
# (W8's byte-level draws corruption after the record already claims clean;
# W10's wrong_pin) exercise the shapes these need — confirmed with `--only`
# against this list ONLY, never concurrently with a `--totality` run (both
# mutate the SAME files by path; two processes racing on one
# `.mutation_backup` corrupts the restore).
FULLSHAPE_TESTS = [str(K / "tests" / "test_full_shape_2k.py")]


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp2k" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def _refuse_if_any_backup_exists() -> None:
    """Fix round 1 / Finding 3: a stray `.mutation_backup` anywhere under
    `experiments/exp2k` means either a concurrent run is already in
    flight or a previous run crashed without restoring — either way,
    starting a NEW run on top of it is how this task's own process
    hazard happened (two concurrent runs raced on one backup file and
    silently corrupted `analyze_2k.py`). Refuse before the baseline
    check even starts."""
    found = sorted((ROOT / "experiments" / "exp2k").rglob("*.mutation_backup"))
    if found:
        raise RuntimeError(f"refusing: {len(found)} .mutation_backup file(s) already present "
                           f"under experiments/exp2k (a concurrent run, or a previous crash that "
                           f"never restored) — resolve by hand before starting a new run: {found}")


def _acquire_backup(path):
    """Exclusive-create `path`'s `.mutation_backup` (`open(..., 'xb')`):
    a second, concurrent `mutation_check.py` targeting the SAME path
    refuses immediately instead of racing this run's own restore-then-
    delete cycle (fix round 1 / Finding 3 — the exact race that
    corrupted `analyze_2k.py` earlier in this task). Copies `path`'s
    current bytes into the backup; the caller restores and removes it
    in `finally`, same as before."""
    backup = path.with_suffix(path.suffix + ".mutation_backup")
    try:
        with open(backup, "xb") as f:
            f.write(path.read_bytes())
    except FileExistsError:
        raise RuntimeError(f"refusing: {backup} already exists — a concurrent mutation_check.py "
                           f"run may be in flight against {path.name} (or a previous run crashed "
                           f"without restoring); resolve it by hand before retrying")
    return backup


def run_suite(tests):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                        *tests], cwd=ROOT, env=env, capture_output=True, text=True)
    return r.returncode == 0, r.stdout[-600:]


def _parse_only(argv) -> set:
    """`--only N[,N,...]` — 1-based mutant indices (M's own numbering,
    printed by every run) to restrict this run to. Returns None (no
    restriction) if `--only` is absent."""
    for a in argv:
        if a.startswith("--only="):
            return {int(x) for x in a[len("--only="):].split(",") if x}
    if "--only" in argv:
        i = argv.index("--only")
        if i + 1 < len(argv):
            return {int(x) for x in argv[i + 1].split(",") if x}
    return None


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    totality = "--totality" in argv
    fullshape = "--fullshape" in argv
    tests = FULLSHAPE_TESTS if fullshape else (TOTALITY_TESTS if totality else TESTS)
    only = _parse_only(argv)

    _refuse_if_any_backup_exists()
    clear_pycache()
    ok, out = run_suite(tests)
    if not ok:
        print("BASELINE FAILS — fix the suite first\n", out)
        return 2
    label = "fullshape" if fullshape else ("totality" if totality else "fast")
    print(f"baseline OK ({label} pass, "
         f"{'all' if only is None else sorted(only)} mutants)\n", flush=True)

    survivors = []
    considered = 0
    for i, (path, name, old, new) in enumerate(M, 1):
        if only is not None and i not in only:
            continue
        considered += 1
        src = path.read_text()
        if src.count(old) != 1:
            print(f"[{i:2d}] SKIP  {name}: target text not found exactly once in {path.name} "
                  f"(count={src.count(old)})")
            survivors.append((i, name, "target-not-found"))
            continue
        backup = _acquire_backup(path)
        try:
            path.write_text(src.replace(old, new))
            clear_pycache()
            ok, out = run_suite(tests)
        finally:
            shutil.copy2(backup, path)
            backup.unlink()
            clear_pycache()
        print(f"[{i:2d}] {'killed' if not ok else 'SURVIVED'}  {name}", flush=True)
        if ok:
            survivors.append((i, name, "survived"))
    skipped = [s for s in survivors if s[2] == "target-not-found"]
    real = [s for s in survivors if s[2] == "survived"]
    print(f"\n{considered - len(survivors)}/{considered} killed; "
          f"{len(real)} survivor(s): {real}; "
          f"{len(skipped)} SKIP (target text not found, stale mutant): {skipped}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
