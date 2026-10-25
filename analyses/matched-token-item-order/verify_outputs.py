"""Saved-output verifier for `analyses/matched-token-item-order/`.

Audits `results/summary.json`, `results/per_rung.csv`, `results/checkpoint_curve.csv`,
`results/all_rungs_143k.csv`, `results/provenance.json`, and `results/REPORT.md`
for schema completeness, SHA-256 integrity, mathematical consistency of rung
averages ($T$), and byte-exact report rendering without rerunning permutations.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import analyze as an  # noqa: E402


def verify_results_dir(results_dir: Path = an.RESULTS) -> dict:
    required = (
        "summary.json",
        "per_rung.csv",
        "checkpoint_curve.csv",
        "all_rungs_143k.csv",
        "provenance.json",
        "REPORT.md",
    )
    for name in required:
        p = results_dir / name
        if p.is_symlink() or not p.is_file():
            raise ValueError(f"missing or symlink output file: {p}")

    prov = json.loads(
        (results_dir / "provenance.json").read_text(encoding="utf-8"),
        parse_constant=lambda c: (_ for _ in ()).throw(ValueError(f"non-finite JSON constant: {c}")),
    )
    if prov.get("source_commit") != an.SOURCE:
        raise ValueError(f"provenance source_commit {prov.get('source_commit')} != {an.SOURCE}")

    for name, want_sha in prov["outputs_sha256"].items():
        got_sha = an.sha256_path(results_dir / name)
        if got_sha != want_sha:
            raise ValueError(f"output sha256 mismatch on {name}: got {got_sha}, expected {want_sha}")

    summary = json.loads(
        (results_dir / "summary.json").read_text(encoding="utf-8"),
        parse_constant=lambda c: (_ for _ in ()).throw(ValueError(f"non-finite JSON constant: {c}")),
    )
    if summary.get("source_commit") != an.SOURCE:
        raise ValueError("summary.json source_commit mismatch")

    # Verify that every defined test's stratified T equals the unweighted mean of its eligible per-rung d values
    def _check_block(block: dict, label: str) -> None:
        for pname, res in block.items():
            if not res.get("defined"):
                continue
            el = res["eligible"]
            if not el:
                raise ValueError(f"{label}/{pname}: defined=True but eligible is empty")
            d_vals = [float(res["per_rung"][r]["d"]) for r in el]
            mean_d = sum(d_vals) / len(d_vals)
            t_val = float(res["stratified"]["T"])
            if not math.isclose(mean_d, t_val, abs_tol=1e-9):
                raise ValueError(f"{label}/{pname}: T={t_val} != mean(per_rung.d)={mean_d}")
            raw_vals = [float(res["per_rung"][r]["raw_d"]) for r in el]
            mean_raw = sum(raw_vals) / len(raw_vals)
            raw_t = float(res["raw"]["T"])
            if not math.isclose(mean_raw, raw_t, abs_tol=1e-9):
                raise ValueError(f"{label}/{pname}: raw T={raw_t} != mean(per_rung.raw_d)={mean_raw}")
            fb = res["family_bootstrap"]
            if not math.isclose(float(fb["rung_mean"]), t_val, abs_tol=1e-9):
                raise ValueError(f"{label}/{pname}: family_bootstrap.rung_mean != T")

    _check_block(summary["primary_rcap_143k"], "primary_rcap_143k")
    _check_block(summary["primary_rpred11_143k"], "primary_rpred11_143k")
    _check_block(summary["first_size_rcap_143k"], "first_size_rcap_143k")
    _check_block(summary["first_size_rpred11_143k"], "first_size_rpred11_143k")
    _check_block(summary["greedy_zero_rcap_143k"], "greedy_zero_rcap_143k")
    _check_block(summary["greedy_zero_rpred11_143k"], "greedy_zero_rpred11_143k")
    _check_block(summary["no28b_rcap_143k"], "no28b_rcap_143k")
    _check_block(summary["no28b_rpred11_143k"], "no28b_rpred11_143k")
    _check_block(summary["grid_40_rcap"], "grid_40_rcap")
    _check_block(summary["grid_40_rpred11"], "grid_40_rpred11")
    _check_block(summary["spine_32_rcap"], "spine_32_rcap")
    _check_block(summary["spine_32_rpred11"], "spine_32_rpred11")
    _check_block(summary["conditioning_143k"], "conditioning_143k")
    for s in an.OUTCOME_SIZES:
        _check_block(summary["by_size_rcap_143k"][s], f"by_size_rcap_143k/{s}")
        _check_block(summary["by_size_rpred11_143k"][s], f"by_size_rpred11_143k/{s}")
    for t_str, crec in summary["checkpoint_curve"].items():
        _check_block(crec["rcap"], f"checkpoint_curve/{t_str}/rcap")
        _check_block(crec["rpred11"], f"checkpoint_curve/{t_str}/rpred11")

    # Verify CSV row counts and Report byte-identity
    with (results_dir / "per_rung.csv").open("r", encoding="utf-8", newline="") as fh:
        per_rung_rows = list(csv.DictReader(fh))
    if not per_rung_rows:
        raise ValueError("per_rung.csv is empty")

    with (results_dir / "checkpoint_curve.csv").open("r", encoding="utf-8", newline="") as fh:
        curve_rows = list(csv.DictReader(fh))
    if len(curve_rows) != len(an.STEPS) * (4 + 2):
        raise ValueError(f"unexpected checkpoint_curve.csv row count: {len(curve_rows)}")

    with (results_dir / "all_rungs_143k.csv").open("r", encoding="utf-8", newline="") as fh:
        all34_rows = list(csv.DictReader(fh))
    if len(all34_rows) != an.N_RUNGS:
        raise ValueError(f"expected {an.N_RUNGS} rows in all_rungs_143k.csv, got {len(all34_rows)}")

    expected_report = an.render_report(summary)
    got_report = (results_dir / "REPORT.md").read_text(encoding="utf-8")
    if got_report != expected_report:
        raise ValueError("REPORT.md differs from render_report(summary.json)")

    return {
        "verified_outputs": len(required),
        "per_rung_rows": len(per_rung_rows),
        "curve_rows": len(curve_rows),
        "all34_rows": len(all34_rows),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=an.RESULTS)
    args = parser.parse_args(argv)
    info = verify_results_dir(args.results_dir)
    print(f"[verify_outputs] OK: {info}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
