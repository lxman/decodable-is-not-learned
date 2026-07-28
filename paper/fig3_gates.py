"""Figure 3: gate arithmetic. Panel (a): per-capability untrained fire
counts vs the floor-rate expectation, from the committed m2_report.json.
Panel (b): the floor-signature predicate geometry — the permutation
null, the 3-SD near_null bar, and the distribution of the maximum of
2,500 null draws. The two observed shuffled-fire positions (3.6 and 4.7
null SD) are transcribed from the exp2b ledger entry of 2026-07-25
(PROGRESS.md, "Gate 3 complete"); every other number is computed here.

    python paper/fig3_gates.py   # writes paper/figures/fig3_gates.{pdf,png}
"""

import json
from collections import Counter
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

import figstyle as st

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
report = json.loads(
    (REPO / "experiments" / "exp2b" / "results" / "m2_report.json").read_text())

N_PERM = 2500
FAMILY = {"410m": 18, "1b": 14}
RATE = {s: f / (N_PERM + 1) for s, f in FAMILY.items()}
per_cap_expect = 5 * RATE["410m"] + 5 * RATE["1b"]          # 10 fits/cap
total_expect = 125 * RATE["410m"] + 125 * RATE["1b"]        # 250 fits

leaks = Counter(rec[0] for rec in report["gate1"]["leaks"])
n_gate1 = sum(leaks.values())
n_gate3 = len(report["gate3"]["leaks"])
gate3_p = report["gate3"]["count_p"]
OBSERVED_SD = (3.6, 4.7)  # ledger 2026-07-25, see docstring

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.6))

# --- panel a: fires per capability vs floor expectation -----------------
caps = sorted(leaks, key=leaks.get)
ys = range(len(caps))
st.apply(ax1)
ax1.hlines(ys, 0, [leaks[c] for c in caps], color=st.CONNECT, lw=2,
           zorder=1)
ax1.scatter([leaks[c] for c in caps], list(ys), s=46, color=st.UNTRAINED,
            zorder=3, edgecolors="white", linewidths=1.0)
ax1.axvline(per_cap_expect, color=st.INK_2, lw=1, ls=(0, (4, 3)), zorder=2)
ax1.annotate(f"floor expectation\n{per_cap_expect:.3f} fires/capability",
             (per_cap_expect, len(caps) - 1.1), xytext=(10, 0),
             textcoords="offset points", fontsize=7.5, color=st.INK_2)
ax1.set_yticks(list(ys))
ax1.set_yticklabels(caps, fontsize=8, fontfamily="monospace", color=st.INK)
ax1.set_xlim(0, 10.4)
ax1.set_xticks(range(0, 11, 2))
ax1.set_xlabel("untrained fires (of 10 fits)", fontsize=8.5, color=st.INK_2)
ax1.set_title(f"(a) gate 1: {n_gate1} structural fires / 250, "
              f"expected {total_expect:.1f}", fontsize=9, color=st.INK,
              pad=8, loc="left")
ax1.text(10.2, 0.2,
         f"shuffled gate: {n_gate3} / 250 fires,\n"
         f"expected {total_expect:.1f} — count test p = {gate3_p:.2f}",
         ha="right", fontsize=7.5, color=st.INK_2)

# --- panel b: the predicate geometry ------------------------------------
st.apply(ax2)
x = np.linspace(0, 6, 600)
null_pdf = norm.pdf(x)
max_pdf = N_PERM * norm.pdf(x) * norm.cdf(x) ** (N_PERM - 1)
p_below_bar = norm.cdf(3) ** N_PERM
e_max = float(np.trapezoid(x * max_pdf, x))

ax2.fill_between(x[x <= 3], 0, 2.0, color=st.TRAINED, alpha=0.07, lw=0)
ax2.plot(x, null_pdf, color=st.INK_2, lw=1.6)
ax2.plot(x, max_pdf, color=st.UNTRAINED, lw=2)
ax2.axvline(3, color=st.INK_2, lw=1, ls=(0, (4, 3)))
ax2.scatter(OBSERVED_SD, [0.02, 0.02], s=46, color=st.UNTRAINED,
            zorder=3, edgecolors="white", linewidths=1.0)
ax2.annotate("permutation null", (0.75, norm.pdf(0.75)), xytext=(6, 6),
             textcoords="offset points", fontsize=7.5, color=st.INK_2)
ax2.annotate("max of 2,500 null draws\n" rf"(mean $\approx$ {e_max:.1f} SD)",
             (4.1, 0.9), fontsize=7.5, color=st.UNTRAINED)
ax2.annotate('"near null" bar: 3 SD\n'
             rf"P(max below bar) $\approx$ {p_below_bar:.2f}",
             (2.9, 1.55), ha="right", fontsize=7.5, color=st.INK_2)
ax2.annotate("observed shuffled fires", (4.7, 0.02), xytext=(12, 6),
             textcoords="offset points", fontsize=7.5, ha="left",
             color=st.UNTRAINED)
ax2.set_xlim(0, 6)
ax2.set_ylim(0, 2.0)
ax2.set_yticks([])
ax2.set_xlabel("accuracy, in null SD above the null mean", fontsize=8.5,
               color=st.INK_2)
ax2.set_title("(b) the floor-signature contradiction", fontsize=9,
              color=st.INK, pad=8, loc="left")

fig.tight_layout(w_pad=3)
out = HERE / "figures"
out.mkdir(exist_ok=True)
for ext in ("pdf", "png"):
    fig.savefig(out / f"fig3_gates.{ext}", dpi=300, bbox_inches="tight")
print(f"wrote {out}/fig3_gates.pdf and .png | gate1 {n_gate1} fires, "
      f"{len(caps)} capabilities; gate3 {n_gate3} fires p={gate3_p:.3f}; "
      f"E[max]={e_max:.2f} SD; P(max<3)={p_below_bar:.3f}")
