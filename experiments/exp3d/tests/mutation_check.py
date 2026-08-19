"""Mutation-test the Exp 3d fixture suite, in both directions (doc
Open item 7).

Every provision gets at least a SOFTENING mutant (the gate or check
stops firing — the direction that lets an unwelcome outcome through)
and, where a hardening misread exists, a HARDENING mutant (fires when
it must not). A surviving mutant means the fixture suite would not
notice that change to the frozen analysis. Targets: analyze_3d.py,
rank_test_3d.py, functional_3d.py, rederive_3d.py, scoring_3d.py.

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
A = ROOT / "experiments/exp3d/analyze_3d.py"
R = ROOT / "experiments/exp3d/rank_test_3d.py"
F = ROOT / "experiments/exp3d/functional_3d.py"
D = ROOT / "experiments/exp3d/rederive_3d.py"
S = ROOT / "experiments/exp3d/scoring_3d.py"

M = [
    # ---- gate 1: zero tolerance (§6, §10.2) ----
    (A, "gate1: zero tolerance dropped",
     "    if gate1_diff_cells:", "    if False:"),
    (A, "gate1: fires on a CLEAN comparison (hardening)",
     "    if gate1_diff_cells:", "    if not gate1_diff_cells:"),
    # ---- leak-void (§5.2, 3c semantics) ----
    (A, "leak: void never applied",
     "            void = str(answer).casefold() in "
     "prompts[RUNG][i].casefold()",
     "            void = False"),
    (A, "leak: all-void INSUFFICIENT_DATA route dropped",
     "    if all_new_fires > 0 and len(all_void) == all_new_fires:",
     "    if False:"),
    (A, "leak: all-void route fires on ANY fire (hardening)",
     "    if all_new_fires > 0 and len(all_void) == all_new_fires:",
     "    if all_new_fires > 0 and len(all_void) >= 0:"),
    (A, "leak: non-void filter inverted (hardening)",
     "        non_void = [ad for ad in addresses if not ad[\"void\"]]",
     "        non_void = [ad for ad in addresses if ad[\"void\"]]"),
    # ---- the verdict tree (§6) ----
    (A, "tree: STRUCTURED branch dropped",
     "    if adj[\"p_low\"] is not None and adj[\"p_low\"] <= "
     "rt.ALPHA_3D:",
     "    if False:"),
    (A, "tree: ANTI branch dropped",
     "    if adj[\"p_high\"] is not None and adj[\"p_high\"] <= "
     "rt.ALPHA_3D:",
     "    if False:"),
    (A, "tree: m_min bar off by one",
     "    if n_f >= m_min:", "    if n_f > m_min:"),
    (A, "tree: THIN qualifier dropped",
     "    thin = bool(n_f <= rt.THIN_MAX)", "    thin = False"),
    (A, "tree: replication annotation inverted",
     "    rep_rejects = rep[\"p_low\"] is not None and \\\n"
     "        rep[\"p_low\"] <= rt.ALPHA_3D",
     "    rep_rejects = rep[\"p_low\"] is not None and \\\n"
     "        rep[\"p_low\"] > rt.ALPHA_3D"),
    # ---- frozen pins ----
    (A, "pins: frozen-import hash assert dropped",
     "        if got != want:\n            raise ValueError(\n"
     "                f\"frozen file",
     "        if False:\n            raise ValueError(\n"
     "                f\"frozen file"),
    (A, "pins: item-file sha check dropped",
     "    if got != ITEMS_SHA_PIN[rung]:", "    if False:"),
    (A, "pins: committed-fires pin comparison dropped",
     "        if got != want:\n            raise ValueError(\n"
     "                f\"committed fires re-extracted",
     "        if False:\n            raise ValueError(\n"
     "                f\"committed fires re-extracted"),
    (A, "pins: twin-fire refusal dropped",
     "    if twin_fires != 0:", "    if False:"),
    (A, "pins: gate-1 attestation-vs-disk check dropped (finding B)",
     "        if got != attested:", "        if False:"),
    (A, "pins: gate-1 disk-vs-literal check dropped",
     "        if got != want_pin[size]:", "        if False:"),
    # ---- shard ingestion ----
    (A, "shards: dtype policy check dropped",
     "    if rec.get(\"dtype\") != \"float32\":\n"
     "        raise ValueError(\n"
     "            f\"{p}: dtype {rec.get('dtype')!r} violates the "
     "ledgered \"",
     "    if False:\n"
     "        raise ValueError(\n"
     "            f\"{p}: dtype {rec.get('dtype')!r} violates the "
     "ledgered \""),
    (A, "shards: stored-tally recompute comparison dropped",
     "        if normalized != t[\"per_seed\"]:", "        if False:"),
    (A, "shards: block seed pin dropped",
     "    if rec.get(\"seeds\") != list(block):", "    if False:"),
    (A, "shards: cross-shard answer identity dropped",
     "                if [str(x) for x in rec[\"answers\"]] != answers "
     "or \\\n                        rec[\"items_sha256\"] != items_sha:",
     "                if False:"),
    # ---- scoring records (§5.5) ----
    (A, "scoring: failed ctrl gate accepted",
     "                if gate.get(\"passed\") is not True:",
     "                if False:"),
    (A, "scoring: span-failure count accepted nonzero",
     "            if rec.get(\"span_round_trip_failures\") != 0:",
     "            if False:"),
    (A, "scoring: gate referent comparison dropped",
     "                if gate.get(\"committed_count\") != pin[\"count\"]"
     " or \\\n                        gate.get(\"committed_n_draws\") "
     "!= pin[\"n_draws\"]:",
     "                if False:"),
    # ---- selection + power pins ----
    (A, "selection: winner recompute comparison dropped",
     "    if rec.get(\"winner\") != sel[\"winner\"]:",
     "    if False:"),
    (A, "selection: values recompute comparison dropped",
     "    if rec.get(\"winner_values\") != values:", "    if False:"),
    (A, "selection: bucket recompute comparison dropped",
     "    if rec.get(\"decile_bucket\") != bucket:", "    if False:"),
    (A, "power: m_min recompute comparison dropped",
     "    if rec.get(\"m_min\") != m_min:", "    if False:"),
    # ---- the statistic (§5.3) ----
    (R, "null: DP convex coefficient corrupted",
     "            keep = 1.0 - m / j", "            keep = m / j"),
    (R, "null: lower tail excludes the observed point",
     "    low = float(pmf[: t + 1].sum()) if t < len(pmf) else 1.0",
     "    low = float(pmf[: t].sum()) if t < len(pmf) else 1.0"),
    (R, "statistic: rank sum degraded to a count",
     "    return float(sum(midranks[i] for i in fired_set))",
     "    return float(len(fired_set))"),
    (R, "alpha loosened",
     "ALPHA_3D = 0.05", "ALPHA_3D = 0.5"),
    (R, "THIN bar moved",
     "THIN_MAX = 4", "THIN_MAX = 400"),
    (R, "MC permutation seed drifts",
     "MC_PERM_SEED = 20260818", "MC_PERM_SEED = 1"),
    (R, "m_min: best-case placement always anti-directional",
     "    sorted_ranks = {k: sorted(doubled_midranks(mids, "
     "strata[int(k)]),\n                              "
     "reverse=(direction == \"high\"))",
     "    sorted_ranks = {k: sorted(doubled_midranks(mids, "
     "strata[int(k)]),\n                              "
     "reverse=True)"),
    (R, "bucket: upper tail flipped",
     "    p = float(pmf[obs:].sum()) if obs < len(pmf) else 0.0",
     "    p = float(pmf[:obs].sum()) if obs < len(pmf) else 0.0"),
    # ---- the functional (§5.1) ----
    (F, "c1: canonical summation order dropped (the ulp defect)",
     "    h1 = -sum((n / L) * math.log2(n / L)\n"
     "              for n in sorted(counts.values()))",
     "    h1 = -sum((n / L) * math.log2(n / L)\n"
     "              for n in counts.values())"),
    (F, "c4: trailing open phrase dropped",
     "    if cur:\n        phrases += 1", "    if False:\n"
     "        phrases += 1"),
    (F, "auc: tie half-credit dropped",
     "            elif values[f] == values[u]:\n"
     "                ties += 1",
     "            elif False:\n"
     "                ties += 1"),
    (F, "selection: pair-count weights flattened",
     "        w = len(f) * len(u)", "        w = 1"),
    (F, "selection: doc-order tie-break inverted",
     "               key=lambda j: (table[j][\"mean_auc\"], "
     "table[j][\"auc_1b\"],\n                              -j))",
     "               key=lambda j: (table[j][\"mean_auc\"], "
     "table[j][\"auc_1b\"],\n                              j))"),
    (F, "midranks: ties resolved by first index",
     "            mid = (j + 1 + k + 1) / 2.0",
     "            mid = j + 1.0"),
    (F, "bucket: ceil degraded to floor",
     "        take = math.ceil(len(idx) / 10)",
     "        take = len(idx) // 10"),
    # ---- gate-1 comparator ----
    (D, "diff: comparison never fires",
     "            if str(g) != str(w):", "            if False:"),
    (D, "diff: incomplete regeneration accepted",
     "        if not isinstance(got, list) or len(got) != dps:",
     "        if False:"),
    (D, "record: rederived seed lies",
     "        \"seeds_rederived\": [GATE1_SEED_3D],",
     "        \"seeds_rederived\": [0],"),
    # ---- the scoring arm ----
    (S, "span: prefix assert dropped",
     "    if enc_f[: len(enc_p)] != enc_p:", "    if False:"),
    (S, "span: round-trip assert dropped",
     "    if got != \" \" + answer:", "    if False:"),
    (S, "gate: lower band gutted",
     "    lo = CTRL_GATE_LOWER_FACTOR * r", "    lo = 0.0"),
    (S, "gate: band exclusive at the edges (hardening)",
     "    return lo <= p_hat <= hi", "    return lo < p_hat < hi"),
    (S, "chain: zero-probability guard dropped",
     "            if p <= 0.0:", "            if False:"),
]


BACKUP_SUFFIX = ".mutation_backup"


def heal_stranded_mutants() -> None:
    """A killed run can die between mutate and restore; the backup
    file written before every mutation makes that recoverable — and
    healing runs FIRST, so a stranded mutant can never masquerade as
    a baseline failure (this happened once at build: the first run
    was killed mid-mutant and left the bucket tail flipped on disk)."""
    for path in (A, R, F, D, S):
        b = Path(str(path) + BACKUP_SUFFIX)
        if b.exists():
            path.write_text(b.read_text())
            b.unlink()
            print(f"  healed stranded mutant in {path.name}")


def clear_pycache() -> None:
    for p in (ROOT / "experiments").rglob("__pycache__"):
        shutil.rmtree(p, ignore_errors=True)


def run_suite() -> int:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "experiments/exp3d/tests/", "-q", "-x", "--no-header", "-p",
         "no:cacheprovider"],
        cwd=ROOT, env=env, capture_output=True, text=True)
    return r.returncode


def main() -> int:
    heal_stranded_mutants()
    clear_pycache()
    base = run_suite()
    if base != 0:
        print("BASELINE SUITE FAILS — fix before mutating")
        return 2
    print(f"baseline clean; {len(M)} mutants")
    survivors = []
    for i, (path, name, old, new) in enumerate(M, 1):
        src = path.read_text()
        if src.count(old) != 1:
            print(f"  {i:2d} BROKEN MUTANT (target count "
                  f"{src.count(old)}): {name}")
            survivors.append((i, name, "broken-target"))
            continue
        b = Path(str(path) + BACKUP_SUFFIX)
        try:
            b.write_text(src)
            path.write_text(src.replace(old, new))
            clear_pycache()
            rc = run_suite()
        finally:
            path.write_text(src)
            if b.exists():
                b.unlink()
        if rc == 0:
            print(f"  {i:2d} SURVIVED: {name}")
            survivors.append((i, name, "survived"))
        else:
            print(f"  {i:2d} killed: {name}")
    clear_pycache()
    if survivors:
        print(f"\n{len(survivors)} SURVIVOR(S):")
        for i, name, kind in survivors:
            print(f"  {i:2d} [{kind}] {name}")
        return 1
    print(f"\nKILLED {len(M)}/{len(M)}, baseline clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
