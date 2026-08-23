"""FROZEN analysis script — Experiment 1 truth table and PASS/FAIL verdict.

This file is committed and git-tagged (`exp1-analysis-frozen`) BEFORE any result-grade
data. It is not edited after data collection (design doc §4, "statistics hygiene"). It
binds only to the RunRecord schema (signatures/schema.py), never to signature
internals, so freezing it does not freeze the still-evolving task/model code.

It implements the preregistered §4 bar verbatim:

  Overall PASS (all three hold, replicated across >=5 seeds/config and >=3 sizes):
    1. S1 & S2 (continuous): 95% CIs for the grokking row and the Lubana-below row are
       DISJOINT, in the predicted direction (grokking higher), with Cohen's d >= 2.
    2. S3 (categorical): grokking reads present AND Lubana-below reads absent.
    3. The Lubana-above control row matches the resolution row (all three present).

  Reportable FAIL (any of):
    - an off-diagonal cell (a signature present on Lubana-below, or absent on grokking;
      covers S3's categorical failure),
    - overlapping CIs or Cohen's d < 2 on S1 or S2,
    - the control row diverging from the resolution row.

Phase A is excluded — it is a pipeline-debug system, not part of the scored table.
Run:  python analyze.py            # from experiments/exp1/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

from signatures.schema import SIZE_BUCKETS, RunRecord
from signatures.stats import cohens_d

# ---- FROZEN thresholds (design §4). Do not edit after the tag. --------------
MIN_SEEDS = 5
MIN_SIZES = 3
COHENS_D_BAR = 2.0
CI_CONF = 0.95
RESOLUTION = "grokking"
PERCOLATION = "lubana_below"
CONTROL = "lubana_above"
SCORED_SYSTEMS = (RESOLUTION, PERCOLATION, CONTROL)
CONTINUOUS = ("S1", "S2")  # magnitude-of-separation signatures

EXP_DIR = Path(__file__).resolve().parent


# ---- helpers ---------------------------------------------------------------

def _s1_value(rec: RunRecord) -> float:
    return rec.s1.accuracy


def _s2_value(rec: RunRecord) -> float:
    return rec.s2.rate_point


def _present(rec: RunRecord, sig: str) -> bool:
    return {"S1": rec.s1.present, "S2": rec.s2.present, "S3": rec.s3.present}[sig]


_VALUE = {"S1": _s1_value, "S2": _s2_value}


def mean_ci(values, conf: float = CI_CONF) -> tuple[float, float, float]:
    """(mean, lo, hi) two-sided Student-t CI. Degenerate (sd=0) -> (m, m, m)."""
    a = np.asarray(values, dtype=float)
    n = a.size
    if n < 2:
        raise ValueError("need >= 2 values for a CI")
    m = float(a.mean())
    sd = float(a.std(ddof=1))
    if sd == 0.0:
        return m, m, m
    half = student_t.ppf(1 - (1 - conf) / 2, n - 1) * sd / np.sqrt(n)
    return m, m - half, m + half


# ---- report types ----------------------------------------------------------

@dataclass
class ContinuousCheck:
    signature: str
    size: str
    resolution_ci: tuple[float, float, float]
    percolation_ci: tuple[float, float, float]
    cohens_d: float
    disjoint_and_directional: bool
    d_ok: bool

    @property
    def ok(self) -> bool:
        return self.disjoint_and_directional and self.d_ok


@dataclass
class AnalysisReport:
    verdict: str                       # "PASS" | "FAIL" | "INSUFFICIENT_DATA"
    findings: list[str] = field(default_factory=list)
    truth_table: dict = field(default_factory=dict)
    sizes_evaluated: list[str] = field(default_factory=list)
    seed_counts: dict = field(default_factory=dict)
    continuous_checks: list[ContinuousCheck] = field(default_factory=list)


# ---- core ------------------------------------------------------------------

def load_records(results_dir: str | Path = None) -> list[RunRecord]:
    results_dir = Path(results_dir) if results_dir else EXP_DIR / "results"
    return [RunRecord.load(p) for p in sorted(results_dir.rglob("*.json"))]


def _group(records):
    """(system, size) -> list[RunRecord], scored systems only."""
    groups: dict[tuple[str, str], list[RunRecord]] = {}
    for r in records:
        if r.system in SCORED_SYSTEMS:
            groups.setdefault((r.system, r.size_bucket), []).append(r)
    return groups


def _consensus(records, sig: str) -> str:
    flags = [_present(r, sig) for r in records]
    if not flags:
        return "—"
    frac = sum(flags) / len(flags)
    if frac == 1.0:
        return "present"
    if frac == 0.0:
        return "absent"
    return f"mixed({sum(flags)}/{len(flags)})"


def analyze(records, *, min_seeds=MIN_SEEDS, min_sizes=MIN_SIZES,
            d_bar=COHENS_D_BAR) -> AnalysisReport:
    groups = _group(records)
    seed_counts = {k: len(v) for k, v in groups.items()}

    # Truth table: consensus present/absent per scored system per signature.
    truth_table = {}
    for sysname in SCORED_SYSTEMS:
        recs = [r for (s, _sz), rs in groups.items() if s == sysname for r in rs]
        truth_table[sysname] = {sig: _consensus(recs, sig) for sig in ("S1", "S2", "S3")}

    # A size is evaluable only if all three scored rows have >= min_seeds seeds.
    # Order by magnitude (canonical SIZE_BUCKETS), not alphabetically.
    _size_key = lambda sz: SIZE_BUCKETS.index(sz) if sz in SIZE_BUCKETS else len(SIZE_BUCKETS)  # noqa: E731
    sizes = sorted({sz for (_s, sz) in groups}, key=_size_key)
    evaluable = [
        sz for sz in sizes
        if all(len(groups.get((sysname, sz), [])) >= min_seeds for sysname in SCORED_SYSTEMS)
    ]

    report = AnalysisReport(
        verdict="FAIL", truth_table=truth_table,
        sizes_evaluated=evaluable, seed_counts=seed_counts,
    )

    if len(evaluable) < min_sizes:
        report.verdict = "INSUFFICIENT_DATA"
        report.findings.append(
            f"only {len(evaluable)} size(s) with >={min_seeds} seeds across all scored "
            f"systems; design requires >={min_sizes}."
        )
        return report

    findings: list[str] = []

    for sz in evaluable:
        grok = groups[(RESOLUTION, sz)]
        perc = groups[(PERCOLATION, sz)]
        ctrl = groups[(CONTROL, sz)]

        # (1) continuous signatures: disjoint CIs, directional, d >= 2.
        for sig in CONTINUOUS:
            gv = [_VALUE[sig](r) for r in grok]
            pv = [_VALUE[sig](r) for r in perc]
            g_ci = mean_ci(gv)
            p_ci = mean_ci(pv)
            disjoint = g_ci[1] > p_ci[2]  # grokking lower bound above percolation upper
            d = cohens_d(gv, pv)
            chk = ContinuousCheck(
                signature=sig, size=sz, resolution_ci=g_ci, percolation_ci=p_ci,
                cohens_d=d, disjoint_and_directional=disjoint, d_ok=(d >= d_bar),
            )
            report.continuous_checks.append(chk)
            if not disjoint:
                findings.append(
                    f"[{sz}] {sig}: CIs overlap or wrong direction — grokking {g_ci} "
                    f"vs Lubana-below {p_ci} (reportable FAIL)."
                )
            if not chk.d_ok:
                findings.append(
                    f"[{sz}] {sig}: Cohen's d = {d:.2f} < {d_bar} — leaky separation "
                    f"(reportable FAIL)."
                )

        # (2) S3 categorical: grokking present, Lubana-below absent (per seed).
        if not all(r.s3.present for r in grok):
            n = sum(r.s3.present for r in grok)
            findings.append(
                f"[{sz}] S3 absent on grokking in {len(grok) - n}/{len(grok)} seeds — "
                f"off-diagonal (reportable FAIL)."
            )
        if any(r.s3.present for r in perc):
            n = sum(r.s3.present for r in perc)
            findings.append(
                f"[{sz}] S3 present on Lubana-below in {n}/{len(perc)} seeds — "
                f"off-diagonal (reportable FAIL)."
            )

        # off-diagonal on S1/S2 too: present on percolation, or absent on resolution.
        for sig in ("S1", "S2"):
            if any(_present(r, sig) for r in perc):
                n = sum(_present(r, sig) for r in perc)
                findings.append(
                    f"[{sz}] {sig} present on Lubana-below in {n}/{len(perc)} seeds — "
                    f"off-diagonal (reportable FAIL)."
                )
            if not all(_present(r, sig) for r in grok):
                n = sum(_present(r, sig) for r in grok)
                findings.append(
                    f"[{sz}] {sig} absent on grokking in {len(grok) - n}/{len(grok)} "
                    f"seeds — off-diagonal (reportable FAIL)."
                )

        # (3) control row matches the resolution row: all three present.
        for sig in ("S1", "S2", "S3"):
            if not all(_present(r, sig) for r in ctrl):
                n = sum(_present(r, sig) for r in ctrl)
                findings.append(
                    f"[{sz}] control (Lubana-above) {sig} present in only {n}/{len(ctrl)} "
                    f"seeds — control diverges from resolution (reportable FAIL)."
                )

    report.findings = findings
    report.verdict = "PASS" if not findings else "FAIL"
    return report


def format_report(report: AnalysisReport) -> str:
    lines = ["=" * 64, "Experiment 1 — Truth Table (scored systems)", "=" * 64]
    lines.append(f"{'system':<16}{'S1':>10}{'S2':>10}{'S3':>10}")
    for sysname in SCORED_SYSTEMS:
        row = report.truth_table.get(sysname, {})
        lines.append(f"{sysname:<16}"
                     f"{row.get('S1', '—'):>10}{row.get('S2', '—'):>10}{row.get('S3', '—'):>10}")
    lines.append("")
    lines.append(f"sizes evaluated (>= {MIN_SEEDS} seeds, all rows): "
                 f"{report.sizes_evaluated or 'none'}")
    if report.continuous_checks:
        lines.append("")
        lines.append("continuous separation (grokking vs Lubana-below):")
        for c in report.continuous_checks:
            lines.append(f"  [{c.size}] {c.signature}: d={c.cohens_d:.2f} "
                         f"disjoint={c.disjoint_and_directional} "
                         f"grok_CI={tuple(round(x,4) for x in c.resolution_ci)} "
                         f"perc_CI={tuple(round(x,4) for x in c.percolation_ci)}")
    lines.append("")
    lines.append(f"VERDICT: {report.verdict}")
    if report.findings:
        lines.append("findings:")
        for f in report.findings:
            lines.append(f"  - {f}")
    lines.append("=" * 64)
    return "\n".join(lines)


if __name__ == "__main__":
    recs = load_records()
    print(format_report(analyze(recs)))
