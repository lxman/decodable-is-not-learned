"""Figure 2: per-capability trained vs untrained starved-probe margins,
both sizes, from paper/fig2_data.json (which recomputes from the
committed fit files under tag exp2b-closed).

    python paper/fig2_plot.py   # writes paper/figures/fig2_margins.{pdf,png}
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt

import figstyle as st

HERE = Path(__file__).resolve().parent
rows = json.loads((HERE / "fig2_data.json").read_text())

attrited = [r for r in rows if r["fate"] == "attrited"]
survivors = [r for r in rows if r["fate"] == "survivor"]
attrited.sort(key=lambda r: (r["untrained_410m"] + r["untrained_1b"]) / 2)
survivors.sort(key=lambda r: (r["trained_410m"] + r["trained_1b"]) / 2)
GAP = 1.6  # blank rows between the two blocks
ordered = survivors + [None] * 1 + attrited  # bottom-to-top on the axis


def ypos():
    ys, caps, y = [], [], 0.0
    for r in ordered:
        if r is None:
            y += GAP
            continue
        ys.append(y)
        caps.append(r["capability"])
        y += 1.0
    return ys, caps


ys, caps = ypos()
fig, axes = plt.subplots(1, 2, figsize=(7.0, 7.6), sharey=True)

for ax, size, title in zip(axes, ("410m", "1b"), ("410M", "1B")):
    st.apply(ax)
    data = [r for r in ordered if r is not None]
    for y, r in zip(ys, data):
        un, tr = r[f"untrained_{size}"], r[f"trained_{size}"]
        ax.plot([un, tr], [y, y], color=st.CONNECT, lw=2, zorder=1,
                solid_capstyle="round")
        if abs(tr - un) < 0.01:  # coincident: orange ring under blue dot
            ax.scatter([un], [y], s=78, color=st.UNTRAINED, zorder=2)
            ax.scatter([tr], [y], s=34, color=st.TRAINED, zorder=3,
                       edgecolors="white", linewidths=1.0)
        else:
            ax.scatter([un], [y], s=48, color=st.UNTRAINED, zorder=2,
                       edgecolors="white", linewidths=1.0)
            ax.scatter([tr], [y], s=48, color=st.TRAINED, zorder=3,
                       edgecolors="white", linewidths=1.0)
    ax.set_title(title, fontsize=10, color=st.INK, pad=8)
    ax.set_xlim(-0.04, 1.02)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0", ".25", ".5", ".75", "1"])
    div_y = len(survivors) - 0.5 + GAP / 2
    ax.axhline(div_y, color=st.GRID, lw=1)

axes[0].set_yticks(ys)
axes[0].set_yticklabels(caps, fontsize=8, fontfamily="monospace",
                        color=st.INK)
axes[0].set_ylim(-0.8, ys[-1] + 0.8)

# direct labels on the topmost row (strongest leaker), legend for the rest
top = attrited[-1]
axes[0].annotate("untrained", (top["untrained_410m"], ys[-1]),
                 xytext=(-6, 9), textcoords="offset points", ha="right",
                 fontsize=7.5, color=st.UNTRAINED)
axes[0].annotate("trained", (top["trained_410m"], ys[-1]),
                 xytext=(6, 9), textcoords="offset points", ha="left",
                 fontsize=7.5, color=st.TRAINED)

# block labels in the right panel's open space
axes[1].text(0.99, ys[len(survivors) + len(attrited) - 1] - 1.8,
             f"attrited ({len(attrited)})", ha="right", fontsize=8.5,
             color=st.INK_2, transform=axes[1].get_yaxis_transform())
axes[1].text(0.99, ys[len(survivors) - 1] - 1.6,
             f"survivors ({len(survivors)})", ha="right", fontsize=8.5,
             color=st.INK_2, transform=axes[1].get_yaxis_transform())

fig.supxlabel("starved-probe margin (mean of 5 seeds)", fontsize=9,
              color=st.INK_2)
fig.tight_layout()

out = HERE / "figures"
out.mkdir(exist_ok=True)
for ext in ("pdf", "png"):
    fig.savefig(out / f"fig2_margins.{ext}", dpi=300, bbox_inches="tight")
print(f"wrote {out}/fig2_margins.pdf and .png "
      f"({len(attrited)} attrited, {len(survivors)} survivors)")
