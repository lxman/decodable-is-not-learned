"""Check saved verdict arithmetic and render reports; never run an analysis.

The only analyze_6 calls replay its pure decision/licence mapping on saved
test summaries. No outcome loader, statistic, permutation or bootstrap runs.
"""
import datetime
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from experiments.exp6 import analyze_6 as an, battery_6 as b6

DEST = Path(__file__).resolve().parent
RESULTS = ROOT / "experiments/exp6/results"
SOURCE_SHA = "70c04aef2bdce01d4edf3774c4fbb9bc1ed77148fc1e03707c137127fe23034d"
FAMILIES = ("smollm3_3b", "olmo7b", "olmo13b", "comma_7b")
NAMES = ("SmolLM3-3B", "OLMo-2 7B", "OLMo-2 13B", "Comma")
v = json.loads((RESULTS / "verdict.json").read_text())
assert hashlib.sha256((RESULTS / "verdict.json").read_bytes()).hexdigest() == SOURCE_SHA
assert v["git_sha"] == "3140369c9197133e899f291f6637c1ca1cb10276"
assert v["n_perm"] == 10000 and v["n_boot"] == 1000
assert all(v["referents"]["pins_active"].values())
assert v["referents"]["failures"] == []
assert v["secondaries"]["failures"] == []
assert v["referents"]["prereg"]["n_bound"] == 33
assert v["referents"]["predictor_seal"]["n_paths"] == 188
assert v["referents"]["endpoint_seal"]["n_paths"] == 172
assert all(x["n_diffs"] == 0 for x in v["referents"]["gate1p"].values())
assert sum(x["draws_compared"] for x in v["referents"]["gate1p"].values()) == 608000

def close(a, b):
    assert math.isclose(a, b, abs_tol=1e-12), (a, b)


def T(row):
    return row["stratified"]["T"]


def fmt(x):
    return "undefined" if x is None else f"{x:.6f}"


checked_tests = 0
checked_bootstraps = 0


def check_saved(node):
    global checked_tests, checked_bootstraps
    if isinstance(node, dict):
        assert "failed" not in node, node
        if "stratified" in node and "eligible" in node:
            checked_tests += 1
            for kind in ("stratified", "raw"):
                s = node[kind]
                if s["T"] is not None:
                    close(s["T"], statistics.mean(x["d"] for x in s["per_rung"].values()))
                    assert s["n_perm"] == 10000
                    close(s["p"], (s["n_ge"]+1) / (s["n_perm"]+1))
            if T(node) is not None:
                assert node["fires"] == (T(node) >= .10 and node["stratified"]["p"] < .01)
            assert set(node["eligible"]) == set(node["per_rung"])
        if "n_boot" in node and "point" in node and "lo" in node:
            checked_bootstraps += 1
            assert node["n_boot"] <= 1000
            if node["lo"] is not None:
                assert node["lo"] <= node["hi"]
        for value in node.values():
            check_saved(value)
    elif isinstance(node, list):
        for value in node:
            check_saved(value)
    elif isinstance(node, float):
        assert math.isfinite(node)


check_saved(v)
tests = {tuple(k.split(":")): x for k, x in v["tests"].items()}
assert len(tests) == 8
for (t, f), row in tests.items():
    assert len(row["eligible"]) >= 3 and row["fires"]
    assert not row["dropped_predictor"] and not row["dropped_degenerate"]
    for rung, r in row["per_rung"].items():
        assert r["n_pos"] >= 20 and r["ci"]["n_boot"] == 1000
        close(r["d"], r["ci"]["point"])
    assert row["thin"] == (["unscramble_long"] if f == "comma_7b" else [])
    assert row["alpha"] == .01 and row["t_bar"] == .1

# Independent headline count from recorded per-rung interval endpoints.
headline = {}
for t in "AB":
    types = {}
    for rung in b6.RUNGS_6:
        fs = [f for f in FAMILIES if rung in tests[t, f]["per_rung"]
              and tests[t, f]["per_rung"][rung]["ci"]["lo"] > 0]
        if len(fs) >= 3:
            types.setdefault(b6.RUNG_TYPE_OF[rung], {})[rung] = fs
    headline[t] = types
assert all(set(headline[t]) == {"string", "choice"} for t in "AB")
for t in "AB":
    assert v["statuses"][t] == {"status": "H", "E": 4, "F": 4,
        "evaluable": list(FAMILIES), "fired": list(FAMILIES), "holds_at": 3}
assert v["verdict"] == "GENERAL"
tree = an.verdict_6([], tests, v["referents"]["rung_sets"], v["referents"]["power"])
for key in ("verdict", "reason", "statuses", "modifiers", "disclosures"):
    assert tree[key] == v[key], key
assert an.licensed_6(tree) == v["licensed_sentence"]
s = v["secondaries"]
assert {str(i) for i in range(1, 14)} == {k.split()[0][1:] for k in s if k.startswith("S")}
assert all(z["within"] for x in s["S10 anchors"].values() for z in x["rungs"].values())
assert s["S7 textures"]["comma_7b"]["rung_level"]["unscramble_long"]["ever"] == 13
assert set(s["S7 textures"]["olmo13b"]["nonfinite_units"]) == {"1000", "2000", "4000", "8000"}

lines = ["EXPERIMENT 6 VERDICT: " + v["verdict"], "", "reason: " + v["reason"],
         "", "licence (frozen text): " + v["licensed_sentence"], "",
         "calibration: " + v["calibration_note"], "",
         "Production run: 2026-10-04 00:40:05–02:58:15 UTC; one invocation.",
         "10,000 permutations; 1,000 bootstraps; every production pin active.",
         "Analysis HEAD: " + v["git_sha"], "verdict.json SHA256: " + SOURCE_SHA,
         "All numbers below are rendered from that saved JSON, without rerunning statistics.",
         "Full S1–S13 records, sensitivity tests, per-rung intervals and disclosures: verdict.json.",
         "", "PRIMARY (T = mean within-stratum Somers' D; fires iff T >= .10 and p < .01)"]
for name, row in v["tests"].items():
    lines.append(f"{name}: T={T(row):.9f}, p={row['stratified']['p']:.12g}, rungs={len(row['eligible'])}, fires={row['fires']}")
    for rung, r in row["per_rung"].items():
        lines.append(f"  {rung}: D={r['d']:.9f}, CI95=[{r['ci']['lo']:.9f}, {r['ci']['hi']:.9f}], n_pos={r['n_pos']}")
lines += ["", "HEADLINE SUPPORT (positive interval on >=3 evaluable families)", json.dumps(headline, indent=2),
          "", "POWER SET DISCLOSURE",
          "All eight tests were declared POWERED before sweeps. Six read exactly the simulated set.",
          "Both Comma tests read 9/10: unscramble_long has 13 ever-correct items (<20), so is THIN.",
          "Their power simulations cover a wider set; do not transfer the exact-set probability to these readings.",
          "", "NAMED SECONDARIES — descriptive/non-gating; no additional alpha claim"]
for f, name in zip(FAMILIES, NAMES):
    lines += ["", name]
    lines.append("S1 k64/128/192/256: " + ", ".join(fmt(T(s['S1 ladder'][f]['ladder'][str(k)])) for k in (64,128,192,256)))
    lines.append("S1 individual 64-draw blocks: " + ", ".join(f"{k}={fmt(T(x))}" for k,x in s['S1 ladder'][f]['blocks']['per_seed'].items()))
    lines.append("S2 410m: " + fmt(T(s['S2 410m at 256'][f])))
    z = s['S3 the two predictors'][f]
    lines.append("S3 B|A=" + fmt(T(z['B_beyond_A'])) + "; A|B=" + fmt(T(z['A_beyond_B'])) + "; paired B-A=" + json.dumps(z['paired_difference']))
    for t in "AB":
        for group in ('by_type','by_class'):
            lines.append(f"S4 {t} {group}: " + ", ".join(f"{k}={fmt(T(x))} (rungs={len(x['eligible'])})" for k,x in s['S4 by type and class'][f][t][group].items()))
    lines.append("S5 answer prior: " + fmt(T(s['S5 answer prior']['test'][f])))
    lines.append("S6 init counts: " + json.dumps(s['S6 referents']['init'][f]))
    z = s['S7 textures'][f]
    lines += ["S7 flat rungs: " + json.dumps(z['flat_rungs']),
              "S7 transient clears on flat: " + json.dumps(z['transient_clears_on_flat']),
              "S7 nonfinite units: " + json.dumps(z['nonfinite_units']),
              "S7 collapse records (>=90% identical continuations on a rung): " + str(len(z['collapses'])),
              "S7 ever/final/first-clear/ceiling by rung:"]
    for r, x in z['rung_level'].items():
        lines.append(f"  {r}: ever={x['ever']}, final={x['final']}, s_star={x['s_star']}, ceiling={z['ceiling_fraction'][r]}")
    for t in "AB":
        key = t+":"+f
        lines.append(f"S9 {t} earlier/new T: " + fmt(s['S9 two batteries'][key]['battery_2c']['T']) + "/" + fmt(T(tests[t,f])))
        lines.append(f"S10 {t}: " + json.dumps(s['S10 anchors'][key]))
        lines.append(f"S11 {t}: " + fmt(T(s['S11 structure-conditioned']['tests'][key])))
        lines.append(f"S12 {t}: " + fmt(T(s['S12 ipa relaxed']['families'][f]['predictors'][t]['test'])))
        lines.append(f"S13 {t}: " + fmt(T(s['S13 beyond the heuristic floor']['tests'][key])))
        lines.append(f"first-correct {t}: " + fmt(T(s['sensitivities']['first_correct']['tests'][key])))
    lines.append("S12 IPA endpoint strict/relaxed: " + json.dumps(s['S12 ipa relaxed']['families'][f]['endpoint_count']))
    lines.append("S13 sets: " + json.dumps(s['S13 beyond the heuristic floor']['rungs'][f]))
    lines.append("B conditioned on A, zero/median: " + ", ".join(fmt(T(x)) for x in s['sensitivities']['B_conditioned_on_A'][f].values()))
lines += ["", "S6 predictor twin: " + json.dumps(s['S6 referents']['predictor_twin']),
          "S6 pilot: " + json.dumps(s['S6 referents']['pilot']), "", "S8 directed outcome order:"]
for k, x in s['S8 outcome order']['pairs'].items():
    lines.append(f"  {k}: T={fmt(T(x['test']))}, rungs={len(x['test']['eligible'])}")
lines += ["", "S11/S12/S13/first-correct/two-of-four worlds: " + ", ".join([
    s['S11 structure-conditioned']['world'], s['S12 ipa relaxed']['world'],
    s['S13 beyond the heuristic floor']['world'], s['sensitivities']['first_correct']['world'],
    s['sensitivities']['naming_rule_two_of_four']['world']]),
    "", "gate failures: []", "secondary failures: []",
    "Four early OLMo-13B fp16 non-finite loads are retained as emitted under design §3.4.",
    "Close-out propagation awaits Michael's separate approval."]
(RESULTS / "VERDICT.txt").write_text("\n".join(lines) + "\n")

# Literal inclusive ranges from projection.md, committed before sweep contact.
groups = [(['unscramble_short','unscramble_long'],(.08,.35),(.12,.42)),
          (['sort3','sort5'],(.03,.28),(.07,.35)),
          (['ipa_word'],(-.04,.20),(.00,.28)),
          (['ascii_bubble'],(-.02,.24),(.00,.30)),
          (['shapes'],(-.03,.22),(.00,.28)),
          (['deduction3','deduction5'],(.00,.25),(.03,.32)),
          (['unit_interp1','unit_interp2'],(-.04,.20),(-.02,.24)),
          (['lcs'],(-.04,.23),(-.02,.28)),
          (['modarith_add1'],(-.05,.22),(-.03,.28))]
ranges = {(t,r): bounds for rs, a, b in groups for t,bounds in (('A',a),('B',b)) for r in rs}
grade = ["# Experiment 6 — complete numerical projection grading", "",
         "Source: the pre-sweep `../projection.md`; values from the once-written `verdict.json`.",
         "HIT means inside the inclusive range, with no extra tolerance. Ineligible cells are not graded.",
         "", "## Eight test forecasts", "",
         "| Test | Point | Range | Actual T | Numeric | Called fire | Actual fire | Binary |",
         "|---|---:|---|---:|---|---|---|---|"]
forecasts = {'A':[(.14,.06,.22,True),(.13,.05,.21,True),(.15,.07,.23,True),(.09,.01,.17,False)],
             'B':[(.18,.09,.27,True),(.17,.08,.26,True),(.19,.10,.28,True),(.13,.04,.22,True)]}
for t in 'AB':
    for f, (point, lo, hi, fire) in zip(FAMILIES, forecasts[t]):
        actual = T(tests[t,f]); result = tests[t,f]['fires']
        grade.append(f"| {t}:{f} | {point:.2f} | [{lo:.2f}, {hi:.2f}] | {actual:.6f} | {'HIT' if lo<=actual<=hi else 'MISS'} | {fire} | {result} | {'HIT' if fire==result else 'MISS'} |")
grade += ["", "## Every eligible per-rung cell", "",
          "| Test | Rung | Range | Actual D | Grade |", "|---|---|---|---:|---|"]
counts = {t:{'HIT':0,'LOW':0,'HIGH':0} for t in 'AB'}
for (t,f), row in tests.items():
    for rung, x in row['per_rung'].items():
        lo, hi = ranges[t,rung]; d = x['d']
        g = 'LOW' if d < lo else 'HIGH' if d > hi else 'HIT'
        counts[t][g] += 1
        grade.append(f"| {t}:{f} | {rung} | [{lo:.2f}, {hi:.2f}] | {d:.6f} | {g} |")
grade += ["", "Totals: " + json.dumps(counts), "",
          "Both Comma unscramble_long cells are THIN (13 ever-correct items); neither is graded.",
          "Endpoint exclusions were known when the projection was made and receive no forecast credit."]
(RESULTS / "projection-grade.md").write_text("\n".join(grade) + "\n")
summary = {"verified_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "source_sha256":SOURCE_SHA,"checks":"saved arithmetic, defaults, pins/gates, full secondary presence, decision and licence replay; no statistics rerun",
           "saved_test_summaries_checked":checked_tests,"saved_bootstrap_summaries_checked":checked_bootstraps,
           "verdict":v['verdict'],"headline_support":headline,"per_rung_projection_counts":counts,
           "max_anchor_abs_diff":max(abs(z['diff']) for x in s['S10 anchors'].values() for z in x['rungs'].values()),
           "mean_cross_battery_decline":{t:statistics.mean(s['S9 two batteries'][t+':'+f]['battery_2c']['T']-T(tests[t,f]) for f in FAMILIES) for t in 'AB'}}
(DEST / "verification.json").write_text(json.dumps(summary,indent=2)+"\n")
assert hashlib.sha256((RESULTS / "verdict.json").read_bytes()).hexdigest() == SOURCE_SHA
print(json.dumps(summary,indent=2))
