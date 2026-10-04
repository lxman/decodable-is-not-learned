"""Independent saved-output audit. Never imports analyze or reads source outcomes.

Reconstructs counts, every paired table and nesting from saved pattern histograms;
checks aggregates, table coverage and every displayed numeric row. Bootstrap
intervals are checked for bounds/order and faithful display, not recomputed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from itertools import combinations, product
from pathlib import Path

EXPECTED = {"sizes": ["410m", "1b", "1.4b", "2.8b", "6.9b", "12b"],
            "steps": [1000, 2000, 4000, 5000, 6000, 8000, 16000, 32000, 100000, 143000],
            "n_rungs": 34, "n_families": 16, "n_items_per_rung": 500}
TABLES = ("counts", "accuracy", "contrasts", "transitions", "texture", "time_averages")
TYPES = ("arithmetic", "option", "string")
# Independent transcription of the fixed older-battery order, not outcome-derived.
FAMILIES = (
    ("mid_digit", "add4_mid sub4_mid add3_mid sub3_mid"), ("antonym", "antonym6 antonym"),
    ("seq_extrap", "arith_next quad_next"), ("base_repr", "base12_digitsum base13 base7 oct2dec"),
    ("rotation", "caesar_len8 caesar"), ("clock", "clock24_d999 clock24"),
    ("rescue_collatz", "collatz_step2"), ("counting", "count_div13 count_div7"),
    ("str_align", "hamming12"), ("rescue_isqrt", "isqrt_gap"), ("order_stat", "median5 median7"),
    ("modulus", "mod13_comp mod17 mod19 mod13"), ("odd_one_out", "odd6 odd_one_out"),
    ("reversal", "rev_string7 reverse_string"), ("rescue_roman", "roman_sum7"),
    ("base_arith", "sub_base8 add_base8"),
)
FROZEN_RUNGS = [(r, f) for f, rungs in FAMILIES for r in rungs.split()]
OPTION = {"antonym", "antonym6", "odd6", "odd_one_out"}
STRING = {"reverse_string", "rev_string7", "caesar", "caesar_len8", "hamming12"}
INTEGERS = set("step training_tokens n_params n_items correct clearing_rungs n_rungs n_families n00 n01 n10 n11 correct_difference clear_gain clear_loss gross_gains gross_losses clear_gains clear_losses adjacent_decreases any_loss ever_correct all_wrong n_checkpoints n_item_observations".split())
FLOATS = set("accuracy floor mean_accuracy slope_accuracy_per_doubling spearman loss_fraction_all loss_fraction_ever".split())


class InvalidOutput(ValueError):
    pass


def check(ok, message):
    if not ok:
        raise InvalidOutput(message)


def equal(actual, expected, label="value"):
    if isinstance(expected, dict):
        check(isinstance(actual, dict) and actual.keys() == expected.keys(), f"{label}: keys")
        for k in expected:
            equal(actual[k], expected[k], f"{label}/{k}")
    elif isinstance(expected, list):
        check(isinstance(actual, list) and len(actual) == len(expected), f"{label}: length")
        for i, (a, e) in enumerate(zip(actual, expected)):
            equal(a, e, f"{label}/{i}")
    elif isinstance(expected, float):
        check(isinstance(actual, (int, float)) and math.isfinite(actual) and
              math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-12), f"{label}: {actual} != {expected}")
    else:
        check(actual == expected, f"{label}: {actual!r} != {expected!r}")


def subset(actual, expected, label):
    for key, value in expected.items():
        check(key in actual, f"{label}: missing {key}")
        equal(actual[key], value, f"{label}/{key}")


def read_table(path):
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        check(reader.fieldnames is not None and len(reader.fieldnames) == len(set(reader.fieldnames)), "CSV header")
        rows = []
        for row in reader:
            check(None not in row and None not in row.values(), "ragged CSV")
            for k, value in row.items():
                if k in INTEGERS:
                    row[k] = int(value)
                elif k in FLOATS or k.endswith("_pp"):
                    row[k] = float(value) if value else None
                    check(row[k] is None or math.isfinite(row[k]), f"nonfinite {path.name}/{k}")
                elif k in ("reference_clear", "nondecreasing"):
                    check(value in ("True", "False"), f"invalid boolean {k}")
                    row[k] = value == "True"
                elif k == "size_pattern_counts":
                    row[k] = json.loads(value)
            rows.append(row)
        return rows


def index(rows, keys, expected):
    out = {tuple(r[k] for k in keys): r for r in rows}
    check(len(out) == len(rows) and set(out) == set(expected), f"coverage/duplicates: {keys}")
    return out


def mean(values):
    return sum(values) / len(values)


def ranks(values):
    return [mean([i + 1 for i, v in enumerate(sorted(values)) if v == x]) for x in values]


def corr(x, y):
    xx, yy = [v - mean(x) for v in x], [v - mean(y) for v in y]
    return sum(a * b for a, b in zip(xx, yy)) / math.sqrt(sum(a * a for a in xx) * sum(b * b for b in yy))


def verify_saved(dest, *, expected=None):
    """expected is test-only injection of miniature dimensions; CLI is fixed scope."""
    production = expected is None
    expected = EXPECTED if expected is None else expected
    dest = Path(dest)
    filenames = {f"{t}.csv" for t in TABLES} | {"summary.json", "REPORT.md", "provenance.json"}
    check({p.name for p in dest.iterdir()} == filenames, "incomplete, refused or unexpected output files")
    manifest = json.loads((dest / "provenance.json").read_text())
    check(manifest["state"] == "complete", "provenance incomplete")
    check(set(manifest["outputs_sha256"]) == filenames - {"provenance.json"}, "output hash coverage")
    for name, digest in manifest["outputs_sha256"].items():
        equal(hashlib.sha256((dest / name).read_bytes()).hexdigest(), digest, name)
    s = json.loads((dest / "summary.json").read_text())
    equal(s["scope"], expected, "fixed scope")
    if production:
        equal(manifest["source_commit"], "6deb2d55fd170cf76cae325ff41e4c750b2b775f")
        for name in ("source", "launch"):
            payload = (json.dumps(manifest[f"{name}_files"], sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
            equal(hashlib.sha256(payload).hexdigest(), manifest[f"{name}_manifest_sha256"], f"{name} manifest")
            equal(s["provenance"][f"{name}_commit"], manifest[f"{name}_commit"])
            equal(s["provenance"][f"{name}_manifest_sha256"], manifest[f"{name}_manifest_sha256"])
            check(re.fullmatch(r"[0-9a-f]{40}", manifest[f"{name}_commit"]) is not None, "commit format")
            for rel, record in manifest[f"{name}_files"].items():
                check(not Path(rel).is_absolute() and ".." not in Path(rel).parts, "manifest path")
                check(re.fullmatch(r"[0-9a-f]{64}", record["sha256"]) is not None and
                      re.fullmatch(r"[0-9a-f]{40}", record["git_blob"]) is not None and record["bytes"] >= 0, "file binding format")
        equal(set(manifest["launch_files"]), {"analyses/matched-token/" + name for name in
              ("analyze.py", "test_analyze.py", "verify_outputs.py", "PLAN.md")}, "launch file coverage")
        prefix = "experiments/exp5/results/units/"
        unit_names = ["_unit.json", "_checkpoint.json", "_loss.json"] + [r + ".json" for r, _ in FROZEN_RUNGS]
        selected = {f"{prefix}{size}/step{step}/{name}" for size in expected["sizes"]
                    for step in expected["steps"] for name in unit_names}
        equal({p for p in manifest["source_files"] if p.startswith(prefix)}, selected, "selected source payload coverage")
        receipts = index(manifest["units"], ("step", "size"), product(expected["steps"], expected["sizes"]))
        for (_, size), rec in receipts.items():
            equal(rec["n_params"], s["parameter_counts"][size], "unit parameter receipt")
        equal([(r["rung"], r["family"]) for r in s["rungs"]], FROZEN_RUNGS, "fixed rung/family order")
        for r in s["rungs"]:
            equal(r["type"], "option" if r["rung"] in OPTION else "string" if r["rung"] in STRING else "arithmetic")
        equal(s["bootstrap"]["n_draws"], 10000)
        equal(s["bootstrap"]["seed"], 20261004)
    equal(s["tokens_per_step"], 2097152)
    equal(s["bootstrap"]["quantile_method"], "linear")
    equal(s["bootstrap"]["percentiles"], [2.5, 97.5])
    equal(s["bootstrap"]["shared_across_all_conditions"], True)
    sizes, steps = expected["sizes"], expected["steps"]
    nr, nf, n = (expected[k] for k in ("n_rungs", "n_families", "n_items_per_rung"))
    check(len(s["rungs"]) == nr, "rung metadata count")
    meta = {r["rung"]: r for r in s["rungs"]}
    check(len(meta) == nr, "duplicate rung metadata")
    rungs = list(meta)
    families = list(dict.fromkeys(r["family"] for r in s["rungs"]))
    check(len(families) == nf, "family coverage")
    equal(s["bootstrap"]["family_order"], families)
    equal(s["families"], [{"family": f, "n_rungs": sum(m["family"] == f for m in meta.values()),
                          "all_rung_weight": sum(m["family"] == f for m in meta.values()) / nr,
                          "equal_family_weight": 1 / nf} for f in families], "family weights")
    equal(s["types"], [{"type": t, "n_rungs": sum(m["type"] == t for m in meta.values())} for t in TYPES], "types")
    check(all(r["n_rungs"] > 0 for r in s["types"]) and sum(r["n_rungs"] for r in s["types"]) == nr, "type partition")
    equal(set(s["parameter_counts"]), set(sizes))
    params = [s["parameter_counts"][size] for size in sizes]
    check(all(type(x) is int and x > 0 for x in params) and all(x < y for x, y in zip(params, params[1:])), "parameter counts")
    tables = {name: read_table(dest / f"{name}.csv") for name in TABLES}
    equal(s["table_rows"], {k: len(rows) for k, rows in tables.items()})
    pairs = list(combinations(sizes, 2))
    counts = index(tables["counts"], ("step", "size", "rung"), product(steps, sizes, rungs))
    textures = index(tables["texture"], ("step", "rung"), product(steps, rungs))
    transitions = index(tables["transitions"], ("step", "smaller", "larger", "rung"),
                        ((t, a, b, r) for t in steps for a, b in pairs for r in rungs))
    index(tables["accuracy"], ("step", "size"), product(steps, sizes))
    index(tables["contrasts"], ("step", "smaller", "larger"), ((t, a, b) for t in steps for a, b in pairs))
    index(tables["time_averages"], ("grid", "smaller", "larger"), ((g, a, b) for g in ("all_steps", "shared_spine") for a, b in pairs))
    for table in tables.values():
        for row in table:
            if "step" in row:
                equal(row["training_tokens"], row["step"] * 2097152, "tokens")
    for (step, size, rung), row in counts.items():
        m = meta[rung]
        check(type(row["correct"]) is int and 0 <= row["correct"] <= n, "count range")
        check(0 < m["floor"] < 1 and 1 <= m["minimum_clear_count"] <= n + 1, "reference metadata")
        subset(row, {"n_items": n, "n_params": s["parameter_counts"][size], "family": m["family"],
                     "type": m["type"], "floor": m["floor"], "accuracy": row["correct"] / n,
                     "reference_clear": row["correct"] >= m["minimum_clear_count"]}, "count")
    # Reconstruct all size bits algebraically from the saved 64-bin sufficient statistic.
    for (step, rung), tex in textures.items():
        hist = tex["size_pattern_counts"]
        check(len(hist) == 2 ** len(sizes) and all(type(x) is int and x >= 0 for x in hist) and sum(hist) == n, "pattern histogram")
        marginals = [sum(k for code, k in enumerate(hist) if (code >> i) & 1) for i in range(len(sizes))]
        equal(marginals, [counts[step, size, rung]["correct"] for size in sizes], "histogram marginals")
        lost = sum(k for code, k in enumerate(hist) if any((code >> i) & 1 and not (code >> (i + 1)) & 1 for i in range(len(sizes) - 1)))
        ever = n - hist[0]
        x, y = [math.log2(p) for p in params], [k / n for k in marginals]
        slope = sum((xx - mean(x)) * (yy - mean(y)) for xx, yy in zip(x, y)) / sum((xx - mean(x)) ** 2 for xx in x)
        subset(tex, {"any_loss": lost, "ever_correct": ever, "all_wrong": hist[0], "n_items": n,
                     "loss_fraction_all": lost / n, "loss_fraction_ever": lost / ever if ever else None,
                     "adjacent_decreases": sum(a > b for a, b in zip(marginals, marginals[1:])),
                     "nondecreasing": all(a <= b for a, b in zip(marginals, marginals[1:])),
                     "slope_accuracy_per_doubling": slope,
                     "spearman": None if len(set(marginals)) == 1 else corr(list(range(len(sizes))), ranks(marginals))}, "texture")
        for i, j in combinations(range(len(sizes)), 2):
            a, b = sizes[i], sizes[j]
            row = transitions[step, a, b, rung]
            cells = {(lo, hi): sum(k for code, k in enumerate(hist) if (code >> i) & 1 == lo and (code >> j) & 1 == hi)
                     for lo, hi in product((0, 1), repeat=2)}
            ac, bc = counts[step, a, rung]["reference_clear"], counts[step, b, rung]["reference_clear"]
            subset(row, {"n_items": n, **{f"n{lo}{hi}": k for (lo, hi), k in cells.items()},
                         "correct_difference": marginals[j] - marginals[i],
                         "clear_gain": int(not ac and bc), "clear_loss": int(ac and not bc)}, "transition")
            equal(row["n01"] - row["n10"], row["correct_difference"], "gains minus losses")
            equal(sum(row[k] for k in ("n00", "n01", "n10", "n11")), n, "pair coverage")
    for row in tables["accuracy"]:
        cell = [counts[row["step"], row["size"], r] for r in rungs]
        subset(row, {"n_rungs": nr, "n_items": nr * n, "correct": sum(c["correct"] for c in cell),
                     "mean_accuracy": sum(c["correct"] for c in cell) / (nr * n),
                     "clearing_rungs": sum(c["reference_clear"] for c in cell)}, "accuracy aggregate")
    for table in ("contrasts", "time_averages"):
        for row in tables[table]:
            times = [row["step"]] if table == "contrasts" else [t for t in steps if row["grid"] == "all_steps" or t not in (5000, 6000)]
            a, b = row["smaller"], row["larger"]
            differences = {r: mean([100 * (counts[t, b, r]["correct"] - counts[t, a, r]["correct"]) / n for t in times]) for r in rungs}
            subset(row, {"n_rungs": nr, "n_families": nf, "all_rung_pp": mean(list(differences.values())),
                         "equal_family_pp": mean([mean([v for r, v in differences.items() if meta[r]["family"] == f]) for f in families]),
                         **{t + "_pp": mean([v for r, v in differences.items() if meta[r]["type"] == t]) for t in TYPES}}, "contrast aggregate")
            for name in ("all_rung", "equal_family"):
                lo, hi = row[name + "_ci_low_pp"], row[name + "_ci_high_pp"]
                check(-100 - 1e-10 <= lo <= hi <= 100 + 1e-10, "interval range/order")
            if table == "contrasts":
                cells = [transitions[row["step"], a, b, r] for r in rungs]
                subset(row, {"n_items": nr * n, "gross_gains": sum(c["n01"] for c in cells),
                             "gross_losses": sum(c["n10"] for c in cells),
                             "clear_gains": sum(c["clear_gain"] for c in cells),
                             "clear_losses": sum(c["clear_loss"] for c in cells)}, "contrast transitions")
                equal(100 * (row["gross_gains"] - row["gross_losses"]) / (nr * n), row["all_rung_pp"], "aggregate paired identity")
            else:
                subset(row, {"n_checkpoints": len(times), "n_item_observations": len(times) * nr * n}, "time denominators")
    equal(s["accuracy"], tables["accuracy"], "summary accuracy")
    displayed = {(sizes[0], sizes[-1]), *zip(sizes, sizes[1:])}
    equal(s["displayed_contrasts"], [r for r in tables["contrasts"] if (r["smaller"], r["larger"]) in displayed], "summary contrasts")
    equal(s["time_averages"], tables["time_averages"], "summary time averages")
    nested = []
    for t in steps:
        cells = [textures[t, r] for r in rungs]
        lost, ever = sum(c["any_loss"] for c in cells), sum(c["ever_correct"] for c in cells)
        nested.append({"step": t, "training_tokens": t * 2097152, "any_loss": lost, "n_items": nr * n,
                       "ever_correct": ever, "loss_fraction_all": lost / (nr * n),
                       "loss_fraction_ever": lost / ever if ever else None,
                       "nondecreasing_rungs": sum(c["nondecreasing"] for c in cells), "n_rungs": nr})
    equal(s["nesting"], nested, "nesting aggregates")
    report = (dest / "REPORT.md").read_text()
    check(s["limitations"] in report, "summary/report limitations differ")
    check_report(report, s)
    return {"state": "verified", "table_rows": s["table_rows"],
            "bootstrap_rerun": False, "source_outcomes_read": False}


def check_report(text, summary):
    """Independent formatting of ALL numeric table rows, not a substring of one headline."""
    rows = []
    for r in summary["accuracy"]:
        rows.append(f"| {r['step']} | {r['training_tokens']} | {r['size']} | {r['correct']}/{r['n_items']} | {r['mean_accuracy']:.6f} | {r['clearing_rungs']}/{r['n_rungs']} |")
    for r in summary["displayed_contrasts"] + summary["time_averages"]:
        estimates = [f"{r[k + '_pp']:.6f} [{r[k + '_ci_low_pp']:.6f}, {r[k + '_ci_high_pp']:.6f}]" for k in ("all_rung", "equal_family")]
        prefix = f"{r['step']}" if "step" in r else f"{r['grid']} | {r['n_checkpoints']}"
        row = f"| {prefix} | {r['larger']} − {r['smaller']} | {estimates[0]} | {estimates[1]} | {r['arithmetic_pp']:.6f} / {r['option_pp']:.6f} / {r['string_pp']:.6f} |"
        if "step" in r:
            row += f" {r['gross_gains']} / {r['gross_losses']} / {r['n_items']} | {r['clear_gains']} / {r['clear_losses']} / {r['n_rungs']} |"
        rows.append(row)
    for r in summary["nesting"]:
        rows.append(f"| {r['step']} | {r['any_loss']}/{r['n_items']} | {r['any_loss']}/{r['ever_correct']} | {r['nondecreasing_rungs']}/{r['n_rungs']} |")
    for r in summary["families"]:
        rows.append(f"| {r['family']} | {r['n_rungs']} | {r['all_rung_weight']:.6f} | {r['equal_family_weight']:.6f} |")
    # Header lines start with one of these words; remaining table rows are numeric evidence.
    headers = ("| Step |", "| Grid |", "| Family |", "|---")
    actual = [line for line in text.splitlines() if line.startswith("|") and not line.startswith(headers)]
    equal(actual, rows, "displayed report rows")
    scope = summary["scope"]
    for literal in (
        f"Source `{summary['provenance']['source_commit']}`; launch `{summary['provenance']['launch_commit']}`.",
        f"Coverage: {len(scope['steps'])} checkpoints × {len(scope['sizes'])} sizes × {scope['n_rungs']} rungs × {scope['n_items_per_rung']} items.",
        f"Bootstrap: {summary['bootstrap']['n_draws']} shared family draws; seed 20261004; percentile 95% intervals (pp).",
        "Type counts: " + "; ".join(f"{r['type']} {r['n_rungs']}/{scope['n_rungs']}" for r in summary["types"]) + ".",
        "143000 is the fixed final comparison", "Known-data descriptive reuse", "not a causal parameter-only",
        "not a time", "without repeated-read noise", "not a zero capability",
    ):
        check(literal in text, f"report missing or inconsistent: {literal}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=Path(__file__).with_name("results"))
    args = parser.parse_args(argv)
    try:
        print(json.dumps(verify_saved(args.directory), sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError, ZeroDivisionError) as e:
        print(f"INVALID OUTPUT: {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
