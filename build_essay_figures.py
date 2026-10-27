"""Build the two summary figures for emergent-resolution-the-gradient.md.

Reads committed result files:
- analyses/matched-token-item-order/results/summary.json
- experiments/exp2g/results/verdict.json
- experiments/exp2h/results/verdict.json
- experiments/exp6/results/verdict.json
- experiments/exp7/campaign/statistics/analysis/analysis.json

Writes:
- figures/fig1_parameter_ladder.{pdf,png}
- figures/fig2_coarse_to_fine.{pdf,png}
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "paper"))

import figstyle as st  # noqa: E402

OUT_DIR = HERE / "figures"
OUT_DIR.mkdir(exist_ok=True)

BLUE = st.TRAINED       # #2a78d6 (OLMo-2 1B / primary highlight)
NAVY = "#174a8b"        # darker blue for Pythia-1B
ORANGE = st.UNTRAINED   # #eb6834 (linear probe / fine contrast)
TEAL = "#1f8a70"        # coarse availability / habit prior
GRAY = "#7a7873"


def build_figure_1():
    """Figure 1: Parameter-ladder item resolution at fixed 300B tokens (step143000)."""
    mt_summary = json.loads(
        (HERE / "analyses" / "matched-token-item-order" / "results" / "summary.json").read_text()
    )

    # Verified step143000 greedy-zero item buckets (410m=0 & 1b=0 at greedy k=1 across 9 R_CAP rungs, n=4,040 items)
    bins = [
        "0 / 256\n(n=1,650)",
        "1–2 / 256\n(n=808)",
        "3–15 / 256\n(n=1,192)",
        "16+ / 256\n(n=390)",
    ]
    rates_by_size = {
        "1.4b": [100.0 * 8 / 1650, 100.0 * 25 / 808, 100.0 * 112 / 1192, 100.0 * 97 / 390],
        "2.8b": [100.0 * 253 / 1650, 100.0 * 178 / 808, 100.0 * 289 / 1192, 100.0 * 143 / 390],
        "6.9b": [100.0 * 55 / 1650, 100.0 * 82 / 808, 100.0 * 244 / 1192, 100.0 * 140 / 390],
        "12b":  [100.0 * 77 / 1650, 100.0 * 79 / 808, 100.0 * 302 / 1192, 100.0 * 159 / 390],
    }
    sizes = ("1.4b", "2.8b", "6.9b", "12b")
    size_labels = {"1.4b": "1.4B", "2.8b": "2.8B", "6.9b": "6.9B", "12b": "12B"}
    size_colors = {
        "1.4b": "#8ab4f8",
        "2.8b": "#4a90d9",
        "6.9b": "#2a78d6",
        "12b": "#123f77",
    }

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.4, 3.85), gridspec_kw={"width_ratios": [1.02, 1.18]})

    # --- Panel A: Grouped bars across 1B sampling buckets ---
    for side in ("top", "right"):
        ax1.spines[side].set_visible(False)
    ax1.spines["left"].set_color(st.SPINE)
    ax1.spines["bottom"].set_color(st.SPINE)
    ax1.tick_params(colors=st.INK_2, labelsize=8, length=3)
    ax1.grid(axis="y", color=st.GRID, lw=0.8, zorder=0)
    ax1.set_axisbelow(True)

    x = np.arange(len(bins))
    width = 0.19
    offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]
    for offset, sz in zip(offsets, sizes):
        ax1.bar(
            x + offset,
            rates_by_size[sz],
            width=width * 0.92,
            color=size_colors[sz],
            label=f"Pythia {size_labels[sz]}",
            zorder=3,
        )

    ax1.set_xticks(x)
    ax1.set_xticklabels(bins, fontsize=7.8, color=st.INK)
    ax1.set_ylabel("Greedy (k=1) accuracy at larger scale (%)", fontsize=8.3, color=st.INK)
    ax1.set_xlabel(
        "Pythia-1B sampled hits out of 256 draws\n(items where 410M & 1B both score 0% at greedy decoding)",
        fontsize=7.8,
        color=st.INK_2,
    )
    ax1.set_ylim(0, 45)
    ax1.set_yticks([0, 10, 20, 30, 40])
    ax1.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax1.set_title(
        "A. Larger models resolve what 1B emits in its tail",
        fontsize=9.0,
        fontweight="bold",
        color=st.INK,
        loc="left",
        pad=8,
    )

    # --- Panel B: Per-rung stratified Somers' D across the 4-size ladder ---
    st.apply(ax2, xgrid=True)
    per_rung_py = mt_summary["primary_rcap_143k"]["pythia_1b_k256"]["per_rung"]
    per_rung_ol = mt_summary["primary_rcap_143k"]["olmo2_1b_k64"]["per_rung"]
    per_rung_pr = mt_summary["primary_rcap_143k"]["probe_1b"]["per_rung"]
    r_cap = list(per_rung_py.keys())

    rungs_sorted = sorted(
        r_cap,
        key=lambda r: 0.5 * (per_rung_py[r]["d"] + per_rung_ol[r]["d"]),
    )

    rung_ys = np.arange(len(rungs_sorted), dtype=float)
    summary_y = float(len(rungs_sorted)) + 0.85

    ax2.axvline(0.0, color=st.SPINE, lw=1.0, ls="--", zorder=1)
    ax2.axhline(len(rungs_sorted) - 0.12, color=st.GRID, lw=1.2, zorder=1)

    for y, r in zip(rung_ys, rungs_sorted):
        d_py = per_rung_py[r]["d"]
        d_ol = per_rung_ol[r]["d"]
        d_pr = per_rung_pr[r]["d"]
        ax2.plot([min(d_pr, d_py, d_ol), max(d_pr, d_py, d_ol)], [y, y], color=st.CONNECT, lw=1.6, zorder=1)
        ax2.scatter(
            [d_pr], [y], s=36, color=ORANGE, marker="s", zorder=2, edgecolors="white", linewidths=0.7,
            label="Pythia-1B linear probe (T=+.026)" if y == 0 else None,
        )
        ax2.scatter(
            [d_py], [y], s=44, color=NAVY, marker="o", zorder=3, edgecolors="white", linewidths=0.7,
            label="Pythia-1B sampled k=256 (T=+.218)" if y == 0 else None,
        )
        ax2.scatter(
            [d_ol], [y], s=44, color=BLUE, marker="D", zorder=4, edgecolors="white", linewidths=0.7,
            label="OLMo-2 1B sampled k=64 (T=+.278)" if y == 0 else None,
        )

    for pred_key, col, marker, dy in [
        ("probe_1b", ORANGE, "s", -0.18),
        ("pythia_1b_k256", NAVY, "o", 0.0),
        ("olmo2_1b_k64", BLUE, "D", +0.18),
    ]:
        row = mt_summary["primary_rcap_143k"][pred_key]
        t_val = row["stratified"]["T"]
        lo, hi = row["family_bootstrap"]["rung_mean_ci"]
        ax2.plot([lo, hi], [summary_y + dy, summary_y + dy], color=col, lw=2.0, zorder=3)
        ax2.scatter([t_val], [summary_y + dy], s=52, color=col, marker=marker, zorder=4, edgecolors="white", linewidths=0.8)

    all_yticks = list(rung_ys) + [summary_y]
    all_yticklabels = list(rungs_sorted) + ["Mean T (9 tasks)"]
    ax2.set_yticks(all_yticks)
    ax2.set_yticklabels(all_yticklabels, fontsize=7.7, fontfamily="monospace", color=st.INK)
    ax2.set_xlim(-0.24, 0.85)
    ax2.set_ylim(-0.7, summary_y + 0.55)
    ax2.set_xticks([-0.2, 0.0, 0.2, 0.4, 0.6, 0.8])
    ax2.set_xlabel(
        "Within-stratum concordance (Somers' D / T)\nacross 1.4B → 2.8B → 6.9B → 12B at 300B tokens",
        fontsize=7.8,
        color=st.INK_2,
    )
    ax2.legend(frameon=True, facecolor="white", edgecolor="none", framealpha=0.92, fontsize=6.9, loc="lower right", bbox_to_anchor=(1.01, 0.12))
    ax2.set_title(
        "B. Item-order concordance across parameter scale",
        fontsize=9.0,
        fontweight="bold",
        color=st.INK,
        loc="left",
        pad=8,
    )

    fig.tight_layout(w_pad=1.6)
    for ext in ("pdf", "png"):
        fig.savefig(OUT_DIR / f"fig1_parameter_ladder.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT_DIR}/fig1_parameter_ladder.pdf and .png")


def build_figure_2():
    """Figure 2: Sealed training-order forecasts across families (Exps 2g-2n, 6) & coarse-to-fine stages (Exp 7)."""
    exp2g = json.loads((HERE / "experiments" / "exp2g" / "results" / "verdict.json").read_text())
    exp2h = json.loads((HERE / "experiments" / "exp2h" / "results" / "verdict.json").read_text())
    exp6 = json.loads((HERE / "experiments" / "exp6" / "results" / "verdict.json").read_text())
    exp7 = json.loads(
        (HERE / "experiments" / "exp7" / "campaign" / "statistics" / "analysis" / "analysis.json").read_text()
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.4, 3.85), gridspec_kw={"width_ratios": [1.05, 1.15]})

    # --- Panel A: Sealed training-order forecasts across four model families ---
    st.apply(ax1, xgrid=True)
    s9 = exp6["secondaries"]["S9 two batteries"]

    # Rows from top to bottom:
    # 1-2: Pythia 2.8B & 6.9B (Exps 2g & 2h: sampler vs linear probe)
    # 3-6: Exp 6 benchmark battery (SmolLM3-3B, OLMo-2 7B, OLMo-2 13B, Comma v0.1 7B)
    row_labels = [
        "Pythia-2.8B (2g)",
        "Pythia-6.9B (2h)",
        "SmolLM3-3B (Exp 6)",
        "OLMo-2 7B (Exp 6)",
        "OLMo-2 13B (Exp 6)",
        "Comma v0.1 7B (Exp 6)",
    ]
    y_pos = np.arange(len(row_labels), dtype=float)[::-1]

    ax1.axvline(0.0, color=st.SPINE, lw=0.9, zorder=1)
    ax1.axvline(0.10, color=GRAY, lw=1.0, ls="--", zorder=1)
    ax1.axhline(3.5, color=st.GRID, lw=1.2, zorder=1)
    ax1.text(0.104, 5.35, ".10 bar", fontsize=7.0, color=GRAY, va="top")

    # Pythia 2.8B (2g) and 6.9B (2h): Pythia-1B sampler vs Pythia-1B probe
    t_2g_probe = exp2g["primary"]["stratified"]["T"]
    t_2g_samp = exp2g["secondaries"]["sampler_competitor"]["stratified"]["T"]
    t_2h_samp = exp2h["primary"]["stratified"]["T"]
    t_2h_probe = exp2h["secondaries"]["probe_competitor"]["stratified"]["T"]

    for y, t_pr, t_py in [(y_pos[0], t_2g_probe, t_2g_samp), (y_pos[1], t_2h_probe, t_2h_samp)]:
        ax1.plot([t_pr, t_py], [y, y], color=st.CONNECT, lw=1.8, zorder=1)
        ax1.scatter(
            [t_pr], [y], s=42, color=ORANGE, marker="s", zorder=2, edgecolors="white", linewidths=0.7,
            label="Pythia-1B linear probe" if y == y_pos[0] else None,
        )
        ax1.scatter(
            [t_py], [y], s=46, color=NAVY, marker="o", zorder=3, edgecolors="white", linewidths=0.7,
            label="Pythia-1B sampled" if y == y_pos[0] else None,
        )

    # Exp 6 four families: Pythia-1B (k=256) and OLMo-2 1B (k=64) on fresh benchmark tasks (plus 2c battery markers)
    exp6_keys = ["smollm3_3b", "olmo7b", "olmo13b", "comma_7b"]
    for y, okey in zip(y_pos[2:], exp6_keys):
        t_a = s9[f"A:{okey}"]["new_battery"]["T"]
        t_b = s9[f"B:{okey}"]["new_battery"]["T"]
        ax1.plot([min(t_a, t_b), max(t_a, t_b)], [y, y], color=st.CONNECT, lw=1.8, zorder=1)
        ax1.scatter([t_a], [y], s=46, color=NAVY, marker="o", zorder=3, edgecolors="white", linewidths=0.7)
        ax1.scatter(
            [t_b], [y], s=46, color=BLUE, marker="D", zorder=4, edgecolors="white", linewidths=0.7,
            label="OLMo-2 1B sampled" if y == y_pos[2] else None,
        )

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(row_labels, fontsize=7.8, color=st.INK)
    ax1.set_xlim(-0.06, 0.25)
    ax1.set_ylim(-0.55, 5.55)
    ax1.set_xticks([-0.05, 0.0, 0.05, 0.10, 0.15, 0.20, 0.25])
    ax1.set_xlabel(
        "Sealed training-order forecast (stratified Somers' T)\nall sampler forecasts p = 1e-4; probe null (-.02)",
        fontsize=7.8,
        color=st.INK_2,
    )
    ax1.legend(frameon=True, facecolor="white", edgecolor="none", framealpha=0.92, fontsize=7.0, loc="lower left", bbox_to_anchor=(0.01, 0.04))
    ax1.set_title(
        "A. Sealed training-order forecasts across families",
        fontsize=9.0,
        fontweight="bold",
        color=st.INK,
        loc="left",
        pad=8,
    )

    # --- Panel B: Exp 7 Coarse-to-Fine Resolution on unit conversion (S1 competitors) ---
    st.apply(ax2, xgrid=True)
    def rat(obj):
        return float(obj["numerator"]) / float(obj["denominator"])

    s1_py = exp7["secondaries"]["S1_competitors"]["pythia_1b"]["readings"]
    s1_ol = exp7["secondaries"]["S1_competitors"]["olmo2_1b"]["readings"]

    metrics = [
        ("Wrong-target habit\n(coarse number prior)", rat(s1_py["wrong"]["T"]), rat(s1_ol["wrong"]["T"])),
        ("Target-pair availability u\n(coarse answer neighborhood)", rat(s1_py["u"]["T"]), rat(s1_ol["u"]["T"])),
        ("Correct-target rate\n(unconditional hit rate)", rat(s1_py["rate"]["T"]), rat(s1_ol["rate"]["T"])),
        ("Raw target contrast d\n(unscaled prompt shift)", rat(s1_py["d"]["T"]), rat(s1_ol["d"]["T"])),
        ("Conditional selectivity x\n(fine counterfactual shift)", rat(s1_py["x"]["T"]), rat(s1_ol["x"]["T"])),
    ]
    ym = np.arange(len(metrics), dtype=float)[::-1]

    ax2.axvline(0.0, color=st.SPINE, lw=1.0, ls="--", zorder=1)
    ax2.axhline(1.5, color=st.GRID, lw=1.2, zorder=1)

    for y, (mlabel, v_py, v_ol) in zip(ym, metrics):
        ax2.plot([min(v_py, v_ol), max(v_py, v_ol)], [y, y], color=st.CONNECT, lw=2.0, zorder=2)
        dy = 0.08 if abs(v_py - v_ol) < 0.015 else 0.0
        ax2.scatter(
            [v_py], [y - dy], s=46, color=NAVY, marker="o", zorder=3, edgecolors="white", linewidths=0.8,
            label="Pythia-1B (k=64)" if y == ym[0] else None,
        )
        ax2.scatter(
            [v_ol], [y + dy], s=46, color=BLUE, marker="D", zorder=4, edgecolors="white", linewidths=0.8,
            label="OLMo-2 1B (k=64)" if y == ym[0] else None,
        )

    ax2.text(0.23, 2.35, "Coarse outline at 1B\nforecasts 3B (+)", fontsize=7.2, color=TEAL, ha="right", fontweight="bold")
    ax2.text(-0.20, 0.42, "Fine counterfactual\nabsent at 1B (–)", fontsize=7.2, color=ORANGE, ha="left", fontweight="bold")

    ax2.set_yticks(ym)
    ax2.set_yticklabels([m[0] for m in metrics], fontsize=7.6, color=st.INK)
    ax2.set_xlim(-0.22, 0.25)
    ax2.set_ylim(-0.55, 4.55)
    ax2.set_xticks([-0.2, -0.1, 0.0, 0.1, 0.2])
    ax2.set_xlabel(
        "Forecast of SmolLM3-3B 4-arm counterfactual emergence (T)\non unit conversion (50 joint-positive pairs, Exp 7)",
        fontsize=7.8,
        color=st.INK_2,
    )
    ax2.legend(frameon=True, facecolor="white", edgecolor="none", framealpha=0.92, fontsize=7.1, loc="lower right")
    ax2.set_title(
        "B. Coarse availability precedes fine counterfactuals",
        fontsize=9.0,
        fontweight="bold",
        color=st.INK,
        loc="left",
        pad=8,
    )

    fig.tight_layout(w_pad=1.6)
    for ext in ("pdf", "png"):
        fig.savefig(OUT_DIR / f"fig2_coarse_to_fine.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT_DIR}/fig2_coarse_to_fine.pdf and .png")


if __name__ == "__main__":
    build_figure_1()
    build_figure_2()
