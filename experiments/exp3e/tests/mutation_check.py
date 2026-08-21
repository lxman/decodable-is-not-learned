"""Mutation-test the Exp 3e fixture suite, in both directions (doc
Open item 8).

Every provision gets at least a SOFTENING mutant (the gate or check
stops firing — the direction that lets an unwelcome outcome through)
and, where a hardening misread exists, a HARDENING mutant (fires when
it must not). A surviving mutant means the fixture suite would not
notice that change to the frozen analysis. Targets: analyze_3e.py,
stats_3e.py, partition_3e.py, scorer_3e.py, rederive_3e.py,
scorer_gates_3e.py.

Runs under 3a's corrected harness: __pycache__ cleared and
PYTHONDONTWRITEBYTECODE=1 before every pytest invocation. The power
record's reproduce test is deselected under mutation (it re-runs the
Monte Carlo and would dominate the wall clock without testing the
mutated provision).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "experiments/exp3e/analyze_3e.py"
S = ROOT / "experiments/exp3e/stats_3e.py"
P = ROOT / "experiments/exp3e/partition_3e.py"
C = ROOT / "experiments/exp3e/scorer_3e.py"
D = ROOT / "experiments/exp3e/rederive_3e.py"
G = ROOT / "experiments/exp3e/scorer_gates_3e.py"

M = [
    # ---- gate 1: zero tolerance (§6, §10.3) ----
    (A, "gate1: zero tolerance dropped",
     "    if gate1_diff_cells:", "    if False:"),
    (A, "gate1: fires on a CLEAN comparison (hardening)",
     "    if gate1_diff_cells:", "    if not gate1_diff_cells:"),
    (A, "gate1: coverage pin dropped (3d F2)",
     "        if rec.get(\"n_items\") != len(items) or rec.get(\"items\") "
     "!= items:\n            raise ValueError(\n                f\"{p}: "
     "items {rec.get('items')!r} (n_items \"\n                f\"{rec.get("
     "'n_items')!r}) are not the preregistered \"\n                f\""
     "subset — gate 1",
     "        if False:\n            raise ValueError(\n                f\"{p}: "
     "items {rec.get('items')!r} (n_items \"\n                f\"{rec.get("
     "'n_items')!r}) are not the preregistered \"\n                f\""
     "subset — gate 1"),
    (A, "gate1: seed pin dropped",
     "        if rec.get(\"seeds_rederived\") != [seed]:", "        if False:"),
    (A, "gate1: fires-reproduced check dropped",
     "        if len(diffs) == 0 and fires != expected_fires[size]:",
     "        if False:"),
    (A, "gate1: attestation-vs-disk check dropped (finding B)",
     "        if got != attested:", "        if False:"),
    (A, "gate1: disk-vs-literal check dropped",
     "        if got != want:\n            raise ValueError(\n"
     "                f\"3d shard for {size} hashes to {got} against the §4 \"",
     "        if False:\n            raise ValueError(\n"
     "                f\"3d shard for {size} hashes to {got} against the §4 \""),
    # ---- leak-void (§5.2, 3c semantics) ----
    (A, "leak: fire void never applied",
     "            void = sc.is_void(answer, prompts[RUNG][i])",
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
    (C, "leak: competitor void never applied",
     "            void = bool(prompts is not None\n"
     "                        and is_void(tgt, prompts[item]))",
     "            void = False"),
    (C, "leak: void competitor still counted",
     "                \"count\": 0 if void else len(addresses),",
     "                \"count\": len(addresses),"),
    # ---- the verdict tree (§6) ----
    (A, "tree: SHORTCUT branch dropped",
     "    if adj[\"p_low\"] is not None and adj[\"p_low\"] <= st.ALPHA_3E:",
     "    if False:"),
    (A, "tree: ANTI branch dropped",
     "    if adj[\"p_high\"] is not None and adj[\"p_high\"] <= st.ALPHA_3E:",
     "    if False:"),
    (A, "tree: m_min bar off by one",
     "    if n_f >= m_min:", "    if n_f > m_min:"),
    (A, "tree: THIN qualifier dropped",
     "    thin = bool(adj[\"thin\"])", "    thin = False"),
    (A, "tree: replication annotation inverted",
     "    rep_rejects = rep[\"p_low\"] is not None and rep[\"p_low\"] <= "
     "st.ALPHA_3E",
     "    rep_rejects = rep[\"p_low\"] is not None and rep[\"p_low\"] > "
     "st.ALPHA_3E"),
    (A, "tree: specificity annotation read from the wrong cell",
     "    spec = specificity[ADJUDICATING_SIZE]",
     "    spec = specificity[REPLICATION_SIZE]"),
    # ---- the primary (§5.3) ----
    (A, "primary: X counted over reachable items",
     "            len(f[\"fired_items\"]), len(f[\"fired_non_reachable\"]),",
     "            len(f[\"fired_items\"]), len(f[\"fired_reachable\"]),"),
    (S, "primary: lower tail excludes the observed point",
     "    return (float(sum(pmf[: x + 1])), float(sum(pmf[x:])))",
     "    return (float(sum(pmf[: x])), float(sum(pmf[x:])))"),
    (S, "primary: upper tail excludes the observed point",
     "    return (float(sum(pmf[: x + 1])), float(sum(pmf[x:])))",
     "    return (float(sum(pmf[: x + 1])), float(sum(pmf[x + 1:])))"),
    (S, "alpha loosened", "ALPHA_3E = 0.05", "ALPHA_3E = 0.5"),
    (S, "THIN bar moved", "THIN_MAX = 10", "THIN_MAX = 1000"),
    (S, "m_min: strict inequality",
     "        if Fraction(math.comb(N - K, n), math.comb(N, n)) <= "
     "Fraction(alpha):",
     "        if Fraction(math.comb(N - K, n), math.comb(N, n)) < "
     "Fraction(alpha) / 2:"),
    # ---- the count-weighted null (§5.4) ----
    (S, "count-weighted: DP takes every item (subset size ignored)",
     "        for m in range(min(K, len(counts)), 0, -1):",
     "        for m in range(min(K, len(counts)), 0, -1):\n"
     "            if m != K:\n                continue"),
    (S, "count-weighted: lower tail excludes the observed point",
     "    low = Fraction(sum(w for s, w in dist.items() if s <= t_obs), tot)",
     "    low = Fraction(sum(w for s, w in dist.items() if s < t_obs), tot)"),
    # ---- designation exchangeability (§5.5) ----
    (S, "designation: upper tail excludes the observed point",
     "    p = Fraction(sum(w for s, w in dist.items() if s >= t_obs), tot)",
     "    p = Fraction(sum(w for s, w in dist.items() if s > t_obs), tot)"),
    (S, "designation: T_s sums every slot, not the reverse",
     "    t_obs = sum(v[0] for v in vecs)", "    t_obs = sum(sum(v) for v in vecs)"),
    (S, "designation: |M| = 0 item admitted",
     "        if len(v) < 2:", "        if len(v) < 1:"),
    (S, "m_s,min: best case uses the largest thetas",
     "    thetas = sorted(Fraction(1, 1 + int(m)) for m in m_sizes)",
     "    thetas = sorted((Fraction(1, 1 + int(m)) for m in m_sizes), "
     "reverse=True)"),
    (S, "annotation: SPARSE bar off by one",
     "    if m_s_min is None or events < m_s_min:",
     "    if m_s_min is None or events <= m_s_min:"),
    (S, "annotation: DIRECTED at any p (hardening)",
     "    if p is not None and p <= alpha:", "    if p is not None:"),
    # ---- the partition (§5.1) ----
    (P, "partition: equal-char swap admitted",
     "            if x[i] == x[j]:\n                continue",
     "            if False:\n                continue"),
    (P, "partition: rotation dropped from N(x)",
     "    out.add(rotate_left(x))\n    out.add(rotate_right(x))",
     "    out.add(rotate_left(x))"),
    (P, "partition: overlap clause inverted",
     "                  if s != a and s[0] == a[0] and overlap(s, x) >= ov_a)",
     "                  if s != a and s[0] == a[0] and overlap(s, x) <= ov_a)"),
    (P, "partition: first-character match dropped",
     "                  if s != a and s[0] == a[0] and overlap(s, x) >= ov_a)",
     "                  if s != a and overlap(s, x) >= ov_a)"),
    (P, "partition: pattern read on the answer",
     "        pat = repeat_pattern(x)     # stated on the INPUT (§1/§3 tables)",
     "        pat = repeat_pattern(a)"),
    (P, "partition: palindrome refusal dropped",
     "        if x == a:\n            raise ValueError(",
     "        if False:\n            raise ValueError("),
    (P, "partition: record recompute comparison dropped",
     "    if got != want:\n        raise ValueError(\n"
     "            f\"committed partition record {path} is not the frozen \"",
     "    if False:\n        raise ValueError(\n"
     "            f\"committed partition record {path} is not the frozen \""),
    # ---- pins ----
    (A, "pins: frozen-import hash assert dropped",
     "        if got != want:\n            raise ValueError(\n"
     "                f\"frozen file",
     "        if False:\n            raise ValueError(\n"
     "                f\"frozen file"),
    (A, "pins: subset literal check dropped",
     "    if partition[\"items\"] != [int(i) for i in subset_pin]:",
     "    if False:"),
    (A, "pins: partition file sha check dropped",
     "        if got != file_sha_pin:", "        if False:"),
    (A, "pins: power record recompute comparison dropped",
     "        if rec.get(k) != v:", "        if False:"),
    (A, "pins: committed-fires re-score comparison dropped",
     "        if got_key != want_key:", "        if False:"),
    (A, "pins: draws-file sha check dropped",
     "    if got != want:\n        raise ValueError(\n"
     "            f\"committed draws file {p} ({label}) has sha256",
     "    if False:\n        raise ValueError(\n"
     "            f\"committed draws file {p} ({label}) has sha256"),
    (A, "pins: twin-fire refusal dropped",
     "    if twin_fires != 0 or twin_rev != pins[\"reversal\"] or \\\n"
     "            twin_ctrl != pins[\"control\"]:",
     "    if False:"),
    (A, "pins: answer_type pin dropped (3d F1)",
     "        if answer_type != answer_type_pin:", "        if False:"),
    (A, "pins: stream map subset-formula check dropped",
     "            if ss[f\"s{s}\"] != want_sub:", "            if False:"),
    # ---- shard ingestion ----
    (A, "shards: stored-tally recompute comparison dropped",
     "        if normalized != t[\"per_seed\"]:", "        if False:"),
    (A, "shards: out-of-subset row admitted",
     "            if i not in want_items:\n                raise ValueError(",
     "            if False:\n                raise ValueError("),
    (A, "shards: subset items pin dropped",
     "    if rec.get(\"n_items\") != len(items) or rec.get(\"items\") != "
     "items:\n        raise ValueError(\n            f\"{p}: items "
     "{rec.get('items')!r} (n_items \"",
     "    if False:\n        raise ValueError(\n            f\"{p}: items "
     "{rec.get('items')!r} (n_items \""),
    (A, "shards: twin shard admitted",
     "    if rec.get(\"untrained_seed\") is not None:", "    if False:"),
    # ---- scorer gates (§5.5) ----
    (A, "scorer gates: failed record accepted",
     "    if ga.get(\"passed\") is not True or gb.get(\"passed\") is not "
     "True or \\\n            rec.get(\"passed\") is not True:",
     "    if False:"),
    (A, "scorer gates: referent comparison dropped",
     "        if exp != fires_pin[size] or got != fires_pin[size]:",
     "        if False:"),
    (G, "scorer gates: gate (a) passes on any addresses",
     "        gate_a[\"per_size_passed\"][size] = bool(got == exp)",
     "        gate_a[\"per_size_passed\"][size] = True"),
    (G, "scorer gates: gate (b) passes on any counts",
     "        gate_b[\"per_size_passed\"][size] = bool(got == exp)",
     "        gate_b[\"per_size_passed\"][size] = True"),
    # ---- gate-1 record + comparator ----
    (D, "record: rederived seed lies",
     "        \"seeds_rederived\": [GATE1_SEED_3E[size]],",
     "        \"seeds_rederived\": [0],"),
    (D, "record: coverage attests the full battery",
     "        \"draws_compared\": len(items) * DRAWS_PER_SEED_3E,",
     "        \"draws_compared\": 500 * DRAWS_PER_SEED_3E,"),
    (D, "subset rows: missing item admitted",
     "    if missing:\n        raise ValueError(", "    if False:\n        raise ValueError("),
]


BACKUP_SUFFIX = ".mutation_backup"
TARGETS = (A, S, P, C, D, G)


def heal_stranded_mutants() -> None:
    """A killed run can die between mutate and restore; the backup
    file written before every mutation makes that recoverable — and
    healing runs FIRST, so a stranded mutant can never masquerade as
    a baseline failure."""
    for path in TARGETS:
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
         "experiments/exp3e/tests/", "-q", "-x", "--no-header", "-p",
         "no:cacheprovider", "-k", "not committed_file"],
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
