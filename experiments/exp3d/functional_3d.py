"""The frozen structural functional (design §5.1) and its selection
formula — Experiment 3d's predictor side, computable from the item
file alone: no weights, no forward pass, no samples ("from below" in
the strictest sense, §1).

Four candidates, doc order frozen (C1 < C2 < C3 < C4), each a total
function of a nonempty answer string; for every candidate, ASCENDING
value = cheaper = predicted to fire. Selection is the §5.1 frozen
pair-counting formula on the committed fired sets; the winner is
computed once at build (select_functional.py), committed as
`functional_selection_3d.json`, and recomputed-and-compared at every
analysis run (3a's class, refused: the ranks the verdict uses are
never read from a file the analyzer didn't check).

Midranks, tie structure, the stratified decile bucket, and the
in-sample stratified AUC live here too: one module owns every
functional-side quantity so the analyzer, the selector, and the power
tables cannot drift apart.
"""

from __future__ import annotations

import math


# ------------------------------------------------------ the candidates

def c1_unigram_bits(s: str) -> float:
    """C1: L × H1(s), H1 = −Σ_c f_c log2 f_c over within-string
    character frequencies. 'aaaa' → 0.0; 'ecde' → 6.0; 'abcd' → 8.0.

    The summation runs over the SORTED count multiset — canonical
    order, so two strings with the same character-count partition get
    bit-identical values. Summing in character-first-occurrence order
    (a dict's insertion order) produced 1-ulp differences between
    mathematically equal items, silently splitting tie groups by an
    accident of float addition order (build ledger, PROGRESS.md: the
    freeze's named attack surface — the functional's degrees of
    freedom — hit at build and closed here)."""
    _nonempty(s)
    L = len(s)
    counts: dict[str, int] = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    h1 = -sum((n / L) * math.log2(n / L)
              for n in sorted(counts.values()))
    return L * h1


def c2_distinct_ratio(s: str) -> float:
    """C2: |distinct(s)| / L. 'aaaa' → 0.25; 'ecde' → 0.75."""
    _nonempty(s)
    return len(set(s)) / len(s)


def c3_neg_longest_run(s: str) -> float:
    """C3: −(length of the longest single-character run).
    'rxxxxd' → −4.0; 'ecde' → −1.0."""
    _nonempty(s)
    best = run = 1
    for a, b in zip(s, s[1:]):
        run = run + 1 if a == b else 1
        if run > best:
            best = run
    return -float(best)


def c4_lz78_phrases(s: str) -> float:
    """C4: the number of phrases in the standard LZ78 incremental
    parse of s — a pure phrase count, no coding overhead. The exact
    parser, committed (design §5.1): the dictionary starts empty; the
    parser extends the current phrase while it remains a dictionary
    member; a phrase that leaves the dictionary is added and the
    parse restarts; a TRAILING phrase still open at end-of-string
    counts as a phrase (the standard convention). Worked examples,
    re-proved in the fixture suite: 'rxxxxd' → 4.0 (r|x|xx|xd),
    'ecde' → 4.0 (e|c|d|e, trailing 'e' open at end), 'aaaaaa' → 3.0
    (a|aa|aaa)."""
    _nonempty(s)
    seen: set[str] = set()
    phrases = 0
    cur = ""
    for ch in s:
        cur += ch
        if cur not in seen:
            seen.add(cur)
            phrases += 1
            cur = ""
    if cur:
        phrases += 1
    return float(phrases)


def _nonempty(s) -> None:
    if not isinstance(s, str) or not s:
        raise ValueError(f"the functional is defined on nonempty answer "
                         f"strings, got {s!r}")


# doc order frozen: ties in the selection metric break C1 < C2 < C3 < C4
CANDIDATES = (
    ("C1_unigram_bits", c1_unigram_bits),
    ("C2_distinct_ratio", c2_distinct_ratio),
    ("C3_neg_longest_run", c3_neg_longest_run),
    ("C4_lz78_phrases", c4_lz78_phrases),
)


def candidate_values(fn, answers) -> list:
    return [fn(str(a)) for a in answers]


# ------------------------------------------------------------- strata

def strata_of(answers) -> dict:
    """Item indices by answer length — identical grouping law to
    analyze_3c.strata_of (asserted equal in the fixture suite; not
    imported so this module stays dependency-free for the selector)."""
    out: dict[int, list] = {}
    for i, ans in enumerate(answers):
        out.setdefault(len(str(ans)), []).append(i)
    return out


# ------------------------------------------------------ ranks and ties

def stratified_midranks(values, strata) -> dict:
    """item index → within-stratum midrank of its functional value,
    ascending cost, rank 1 = cheapest, ties averaged (§5.3: a fixed
    property of the frozen functional and the committed item file)."""
    out: dict[int, float] = {}
    for _length, idx in sorted(strata.items()):
        ordered = sorted(idx, key=lambda i: (values[i], i))
        j = 0
        while j < len(ordered):
            k = j
            while k + 1 < len(ordered) and \
                    values[ordered[k + 1]] == values[ordered[j]]:
                k += 1
            mid = (j + 1 + k + 1) / 2.0
            for t in range(j, k + 1):
                out[ordered[t]] = mid
            j = k + 1
    return out


def tie_structure(values, strata) -> dict:
    """Per stratum: the sorted distinct values with their item counts
    and midranks — the effective resolution of the test, printed at
    freeze (§2: 2c's tie collapse, named and pre-empted)."""
    out = {}
    mids = stratified_midranks(values, strata)
    for length, idx in sorted(strata.items()):
        groups: dict[float, int] = {}
        for i in idx:
            groups[values[i]] = groups.get(values[i], 0) + 1
        out[str(length)] = {
            "n_items": len(idx),
            "n_distinct_values": len(groups),
            "groups": [{"value": v, "count": n,
                        "midrank": mids[next(i for i in idx
                                             if values[i] == v)]}
                       for v, n in sorted(groups.items())],
        }
    return out


def decile_bucket(values, strata) -> list:
    """B (§5.4): the cheapest ceil(n_s/10) items per stratum, frozen at
    tag. Boundary ties inside a tied value group are broken by item
    index — an arbitrary-but-frozen total order, disclosed; the
    PRIMARY statistic uses midranks and carries no such arbitrariness."""
    out = []
    for _length, idx in sorted(strata.items()):
        take = math.ceil(len(idx) / 10)
        ordered = sorted(idx, key=lambda i: (values[i], i))
        out.extend(ordered[:take])
    return sorted(out)


# ------------------------------------- the §5.1 frozen selection metric

def stratum_auc(values, fired, unfired) -> float:
    """AUC_s = (#{fired-cheaper-than-unfired pairs} + 0.5·#{tied
    pairs}) / (|F_s|·|U_s|), cheaper = smaller value."""
    if not fired or not unfired:
        raise ValueError("stratum AUC needs at least one fired and one "
                         "unfired item")
    wins = ties = 0
    for f in fired:
        for u in unfired:
            if values[f] < values[u]:
                wins += 1
            elif values[f] == values[u]:
                ties += 1
    return (wins + 0.5 * ties) / (len(fired) * len(unfired))


def stratified_auc(values, strata, fired_set) -> dict:
    """The §5.1 formula, exactly: Σ_s |F_s||U_s|·AUC_s / Σ_s |F_s||U_s|
    over strata with |F_s| > 0. Returns the weighted AUC and the
    per-stratum decomposition (printed as provenance)."""
    fired_set = set(fired_set)
    n_all = sum(len(idx) for idx in strata.values())
    bad = [i for i in fired_set if not any(i in idx
                                          for idx in strata.values())]
    if bad:
        raise ValueError(f"fired items {sorted(bad)} are not in any "
                         f"stratum of the {n_all}-item battery")
    num = den = 0.0
    per = {}
    for length, idx in sorted(strata.items()):
        f = [i for i in idx if i in fired_set]
        u = [i for i in idx if i not in fired_set]
        if not f:
            per[str(length)] = {"n_fired": 0, "note": "no fired items — "
                                "stratum carries no selection weight"}
            continue
        if not u:
            raise ValueError(f"stratum {length} is entirely fired — the "
                             f"pair count is undefined")
        auc = stratum_auc(values, f, u)
        w = len(f) * len(u)
        per[str(length)] = {"n_fired": len(f), "n_unfired": len(u),
                            "weight": w, "auc": auc}
        num += w * auc
        den += w
    if den == 0:
        raise ValueError("no stratum carries a fired item — the "
                         "selection metric is undefined")
    return {"stratified_auc": num / den, "per_stratum": per}


def select_winner(answers, fired_1b, fired_410m) -> dict:
    """§5.1 end to end: per candidate, the mean of the two cells'
    stratified AUCs; highest mean wins; ties break by the 1b AUC, then
    by doc order. No builder discretion remains."""
    strata = strata_of(answers)
    table = []
    for name, fn in CANDIDATES:
        vals = candidate_values(fn, answers)
        a1b = stratified_auc(vals, strata, fired_1b)
        a41 = stratified_auc(vals, strata, fired_410m)
        table.append({
            "candidate": name,
            "auc_1b": a1b["stratified_auc"],
            "auc_1b_per_stratum": a1b["per_stratum"],
            "auc_410m": a41["stratified_auc"],
            "auc_410m_per_stratum": a41["per_stratum"],
            "mean_auc": (a1b["stratified_auc"] + a41["stratified_auc"])
            / 2.0,
        })
    # doc order is the list order; max() keeps the FIRST maximum under
    # exact float equality, which is exactly the frozen tie-break chain
    best = max(range(len(table)),
               key=lambda j: (table[j]["mean_auc"], table[j]["auc_1b"],
                              -j))
    return {"table": table, "winner": table[best]["candidate"],
            "winner_index": best}
