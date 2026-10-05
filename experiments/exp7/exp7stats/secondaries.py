"""All eight preregistered secondary sections; raw-preserving S8 always runs."""
from fractions import Fraction as F
from collections import Counter
from exp7core.scoring import score_draws
from exp7core.inference import mean, eligibility, Cell
from exp7core.strata import availability_buckets
from .common import ARMS, FAMILIES, PREDICTORS, require, digest
from .data import cells, score_slice, predictor_support, baseline_score
from .bootstrap import Metric, run as bootstrap, difference

NAMES = ("S1_competitors", "S2_canonical_sham", "S3_family_coverage", "S4_partitions",
         "S5_draw_budgets", "S6_trajectories", "S7_baselines_twin", "S8_label_reversal")


def scalar_scores(scores, field):
    if field == "canonical":
        return {f: tuple(s.canonical.x for s in ss) for f, ss in scores.items()}
    if field == "sham":
        return {f: tuple(s.sham.x for s in ss) for f, ss in scores.items()}
    return {f: tuple(getattr(s, field) for s in ss) for f, ss in scores.items()}


def render_support(tables):
    supported = [t.x for t in tables if t.supported]
    return {"mean_d": mean([F(t.n00+t.n11-t.n01-t.n10, 2*t.k) for t in tables]),
            "mean_u": mean([F(t.m0+t.m1, 2*t.k) for t in tables]),
            "unsupported": len(tables)-len(supported),
            "supported_only_mean_x": mean(supported) if supported else None}


def support_rows(scores, pairs):
    out = []
    for s, pair in zip(scores, pairs):
        supported = [t.x for t in (s.canonical, s.sham) if t.supported]
        out.append({"id": pair.id, "x": s.x, "d": s.d, "u": s.u, "rate": s.rate,
                    "wrong": s.wrong, "C": s.C, "W": s.W, "row_totals": s.row_totals,
                    "unsupported_renders": s.unsupported,
                    "supported_only": mean(supported) if supported else None,
                    "raw_identity": {"rate": s.rate, "half_u_plus_d": (s.u+s.d)/2}})
    return out


def reversal(battery, predictors, outcomes):
    before = digest({p: v.raw for p, v in predictors.items()})
    outcome_before = digest({f: [o["raw"] for o in outcomes[f]] for f in FAMILIES})
    checked, baselines, na_pairs = {}, 0, 0
    for p, predictor in predictors.items():
        count = 0
        budgets = ((0, 16),) if p == "twin" else ((0, 16), (0, 32), (0, 64), (32, 64))
        for f in FAMILIES:
            for pair, raw in zip(battery.family(f), dict(predictor.raw)[f]):
                for start, stop in budgets:
                    draws = {a: raw[j][start:stop] for j, a in enumerate(ARMS)}
                    first = score_draws(draws, pair.targets, pair.kind, k=stop-start)
                    swapped = score_draws(draws, pair.targets[::-1], pair.kind, k=stop-start)
                    require(swapped.x == -first.x and swapped.d == -first.d and swapped.u == first.u,
                            f"S8 reversal {p}/{pair.id}/{start}:{stop}")
                    count += 1
        checked[p] = count
    for f in FAMILIES:
        for pair in battery.family(f):
            for name, outputs in pair.baselines:
                if outputs.status == "NOT_APPLICABLE":
                    na_pairs += 1
                    continue
                s = baseline_score(pair, outputs)
                draws = {a: [outputs.outputs[j]] for j, a in enumerate(ARMS)}
                r = score_draws(draws, pair.targets[::-1], pair.kind, k=1)
                require((r.x, r.d, r.u) == (-s.x, -s.d, s.u), f"S8 baseline {name}/{pair.id}")
                baselines += 1
    after = digest({p: v.raw for p, v in predictors.items()})
    outcome_after = digest({f: [o["raw"] for o in outcomes[f]] for f in FAMILIES})
    require(before == after and outcome_before == outcome_after, "S8 mutated generated strings")
    return {"status": "EXACT", "checked_pair_budgets": checked, "checked_baseline_pairs": baselines,
            "baseline_not_applicable_pairs": na_pairs,
            "baseline_note": "All applicable baseline outputs, including explicitly marked abstention MISS strings, are rescored; N/A cells remain reported with reasons.",
            "predictor_raw_before": before, "predictor_raw_after": after,
            "outcome_raw_before": outcome_before, "outcome_raw_after": outcome_after,
            "note": "Swap target designation only, never regenerate or mutate strings."}


def build(battery, predictors, outcomes, primary, shape):
    metrics, plans = {}, {}
    y = {f: tuple(o["y"] for o in outcomes[f]) for f in FAMILIES}
    ys = {f: tuple(o["y_sham"] for o in outcomes[f]) for f in FAMILIES}
    report = {name: {} for name in NAMES}
    for p in PREDICTORS:
        pred = predictors[p]
        scores, strata = dict(pred.scores), dict(pred.strata)
        subset = tuple(primary[p]["eligible"])
        def add(name, xx, yy=y, ss=strata, keep=subset):
            key = f"{p}/{name}"
            require(key not in metrics, "duplicate secondary metric")
            metrics[key] = Metric(tuple(keep), xx, yy, ss)
            return key
        competitors = {field: add(f"competitor/{field}", scalar_scores(scores, field))
                       for field in ("x", "d", "rate", "u", "wrong")}
        canonical = add("canonical", scalar_scores(scores, "canonical"))
        sham = add("sham", scalar_scores(scores, "sham"), ys)
        family_keys = {f: {field: add(f"family/{f}/{field}", scalar_scores(scores, field), keep=(f,))
                           for field in ("x", "d")} for f in FAMILIES}
        partitions = {}
        for name in ("base", "median", "tercile"):
            cs = cells(pred, outcomes, battery, partition=name)
            keep, elig = eligibility(cs)
            ss = {c.family: c.strata for c in cs}
            key = add(f"partition/{name}", scalar_scores(scores, "x"), ss=ss, keep=keep)
            partitions[name] = {"metric": key, "eligibility": elig, "eligible": keep,
                                "pair_count": sum(len(c.ids) for c in cs), "dropped_pairs": 0,
                                "blocks": {f: dict(pred.partitions)[f][name][1] for f in FAMILIES}}
        budgets = {}
        for name, start, stop in (("k16", 0, 16), ("k32", 0, 32), ("k64", 0, 64),
                                  ("half_first32", 0, 32), ("half_last32", 32, 64)):
            sc = score_slice(pred, battery, start, stop)
            xx = scalar_scores(sc, "x")
            fixed = add(f"budget/{name}/fixed", xx)
            ss = {f: availability_buckets(tuple(pair.base for pair in battery.family(f)),
                                          tuple(s.u for s in sc[f]))[0] for f in FAMILIES}
            cs = tuple(Cell(f, tuple(pair.id for pair in battery.family(f)), sc[f], y[f], ss[f]) for f in FAMILIES)
            keep, elig = eligibility(cs)
            rebucketed = add(f"budget/{name}/rebucketed", xx, ss=ss, keep=keep)
            budgets[name] = {"range": (start, stop), "fixed": fixed, "rebucketed": rebucketed,
                             "rebucketed_eligibility": elig,
                             "support": {f: {"unsupported_renders": sum(s.unsupported for s in sc[f]),
                                             "mean_u": mean([s.u for s in sc[f]])} for f in FAMILIES}}
        trajectory = {}
        for arm_index, arm in enumerate(ARMS):
            yy = {f: tuple(sum(b[arm_index] for b in o["bits"]) for o in outcomes[f]) for f in FAMILIES}
            trajectory[f"member_{arm}"] = add(f"trajectory/member_{arm}", scalar_scores(scores, "x"), yy)
        for label, yy in (("joint", y), ("joint_sham", ys),
                          ("first_joint_order", {f: tuple(o["first_order_score"] for o in outcomes[f]) for f in FAMILIES})):
            trajectory[label] = add(f"trajectory/{label}", scalar_scores(scores, "x"), yy)
        baselines = {}
        for f in FAMILIES:
            bs = {}
            for name, _ in battery.family(f)[0].baselines:
                first = dict(battery.family(f)[0].baselines)[name]
                if first.status == "NOT_APPLICABLE":
                    bs[name] = {"status": "NOT_APPLICABLE", "na_reason": first.na_reason,
                                "baseline_missing": False, "N": 0, "reading": None, "not_in_applicable_denominator": True}
                    continue
                sscores = []
                abstentions = [0]*4
                for pair in battery.family(f):
                    values = dict(pair.baselines)[name]
                    sscores.append(baseline_score(pair, values))
                    for j, flag in enumerate(values.abstained):
                        abstentions[j] += flag
                xx = {f: tuple(s.x for s in sscores)}
                key = add(f"baseline/{f}/{name}", xx, yy={f: y[f]}, ss={f: strata[f]}, keep=(f,))
                bs[name] = {"status": "APPLICABLE", "metric": key, "N": len(sscores),
                            "baseline_missing": False,
                            "canonical_joint_count": sum(s.canonical.n00*s.canonical.n11 for s in sscores),
                            "sham_joint_count": sum(s.sham.n00*s.sham.n11 for s in sscores),
                            "abstentions_by_arm": dict(zip(ARMS, abstentions)),
                            "applicable_denominator_retained": True, "mean_d": mean([s.d for s in sscores]),
                            "mean_u": mean([s.u for s in sscores]),
                            "pair_rows": [{**row, "abstained": dict(zip(ARMS, dict(pair.baselines)[name].abstained))}
                                          for row, pair in zip(support_rows(sscores, battery.family(f)), battery.family(f))]}
            baselines[f] = bs
        twin_key = add("twin_same_primary_strata", scalar_scores(dict(predictors["twin"].scores), "x"))
        plans[p] = {"competitors": competitors, "canonical": canonical, "sham": sham,
                    "partitions": partitions, "budgets": budgets, "trajectory": trajectory,
                    "baselines": baselines, "twin": twin_key, "family_keys": family_keys}
    summaries, samples = bootstrap(metrics, {f: shape.n for f in FAMILIES},
                                    B=shape.bootstraps, namespace="exp7/verdict/all-readings-v2")
    for p in PREDICTORS:
        pred, plan = predictors[p], plans[p]
        comp = plan["competitors"]
        report[NAMES[0]][p] = {"readings": {k: summaries[v] for k, v in comp.items()},
                              "paired_T_differences": {k: difference(summaries, samples, comp["x"], comp[k])
                                                       for k in ("d", "rate", "u", "wrong")},
                              "mean_x_minus_d": {**difference(summaries, samples, comp["x"], comp["d"], key="mean"),
                                                 "note": "Unlike conditional and raw scales; not a decomposition of x."}}
        report[NAMES[1]][p] = {"canonical": summaries[plan["canonical"]], "sham": summaries[plan["sham"]],
                              "paired_T_difference": difference(summaries, samples, plan["canonical"], plan["sham"]),
                              "paired_mean_difference": difference(summaries, samples, plan["canonical"], plan["sham"], key="mean"),
                              "joint_agreement_by_family": {f: mean([o["joint_agreement"] for o in outcomes[f]]) for f in FAMILIES},
                              "per_checkpoint_agreement": {f: [F(sum(o["joint"][j] == o["sham"][j] for o in outcomes[f]), shape.n)
                                                                 for j in range(len(shape.grid))] for f in FAMILIES}}
        report[NAMES[1]][p]["render_support"] = {
            f: {render: render_support([getattr(s, render) for s in pred.family(f)])
                for render in ("canonical", "sham")} for f in FAMILIES}
        fam = {}
        for f in FAMILIES:
            scores = pred.family(f)
            supported = [t.x for s in scores for t in (s.canonical, s.sham) if t.supported]
            fam[f] = {"eligibility": primary[p]["families"][f],
                      "mean_x": mean([s.x for s in scores]), "mean_d": mean([s.d for s in scores]),
                      "mean_u": mean([s.u for s in scores]),
                      "supported_only_mean": mean(supported) if supported else None,
                      "rows": support_rows(scores, battery.family(f)),
                      "readings": {field: summaries[key] for field, key in plan["family_keys"][f].items()}}
        report[NAMES[2]][p] = {"eligible": primary[p]["eligible"], "all_four": fam,
                              "support": predictor_support(pred), "dropped_pairs": 0,
                              "witness_note": "Aggregate conjunction; different retained families may drive its two components."}
        report[NAMES[3]][p] = {name: {**value, "reading": summaries[value["metric"]]}
                              for name, value in plan["partitions"].items()}
        report[NAMES[4]][p] = {"budgets": {name: {**value, "fixed": summaries[value["fixed"]],
                                                 "rebucketed": summaries[value["rebucketed"]]}
                                          for name, value in plan["budgets"].items()},
                              "disjoint_halves_T": difference(summaries, samples,
                                  plan["budgets"]["half_first32"]["fixed"], plan["budgets"]["half_last32"]["fixed"]),
                              "no_new_draws": True}
        report[NAMES[5]][p] = {name: summaries[key] for name, key in plan["trajectory"].items()}
        report[NAMES[6]][p] = {"baselines": {f: {name: ({**value, "reading": summaries[value["metric"]]}
                                                       if value["status"] == "APPLICABLE" else value)
                                                for name, value in bs.items()}
                                           for f, bs in plan["baselines"].items()},
                              "twin_on_primary_strata": summaries[plan["twin"]],
                              "trained_minus_twin_T": difference(summaries, samples, comp["x"], plan["twin"]),
                              "limitation": "A baseline explaining a family limits its interpretation; no algorithm-recovery claim."}
    report[NAMES[0]]["predictor_difference"] = difference(summaries, samples,
        plans[PREDICTORS[0]]["competitors"]["x"], plans[PREDICTORS[1]]["competitors"]["x"])
    report[NAMES[5]]["pair_trajectories"] = {f: [{"id": pair.id, **{k: v for k, v in o.items() if k != "raw"}}
                                                 for pair, o in zip(battery.family(f), outcomes[f])] for f in FAMILIES}
    report[NAMES[5]]["grid"] = shape.grid
    report[NAMES[6]]["twin_all_families"] = {f: {"mean_x": mean([s.x for s in predictors["twin"].family(f)]),
                                                "rows": support_rows(predictors["twin"].family(f), battery.family(f))}
                                           for f in FAMILIES}
    coverage = dict(battery.baseline_coverage)
    report[NAMES[6]]["applicability_coverage"] = {**coverage,
        "total_cells": sum(coverage.values()), "applicable_denominator": coverage["applicable_cells"],
        "baseline_missing": [],
        "note": "Applicable abstentions remain MISS observations in every pair and in the applicable-cell denominator; N/A has an explicit reason."}
    report[NAMES[7]] = reversal(battery, predictors, outcomes)
    for name in NAMES:
        require(bool(report[name]), f"missing secondary {name}")
        report[name]["status"] = "DESCRIPTIVE" if name != NAMES[7] else "EXACT"
    main_intervals = {p: summaries[plans[p]["competitors"]["x"]]["bootstrap"] for p in PREDICTORS}
    return report, main_intervals
