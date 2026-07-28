"""Figure 1: the basis-starved split, as a schematic. Items live on a
grid of surface-component values; holding out values of each component
partitions items into probe training (all components kept), starved
validation (all components held out), and a discarded mixed zone. No
data — geometry only.

    python paper/fig1_schematic.py  # writes paper/figures/fig1_split.{pdf,png}
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import figstyle as st

N, HELD = 10, 3
KEPT = N - HELD
HERE = Path(__file__).resolve().parent

fig, ax = plt.subplots(figsize=(5.4, 5.4))
ax.set_aspect("equal")

for i in range(N):          # component 1 value index (x)
    for j in range(N):      # component 2 value index (y)
        held_i, held_j = i >= KEPT, j >= KEPT
        if not held_i and not held_j:
            fc, hatch = (*plt.matplotlib.colors.to_rgb(st.TRAINED), 0.16), None
        elif held_i and held_j:
            fc, hatch = (*plt.matplotlib.colors.to_rgb(st.VAL_TINT), 0.22), None
        else:
            fc, hatch = (0, 0, 0, 0.03), "///"
        ax.add_patch(Rectangle((i, j), 1, 1, facecolor=fc, hatch=hatch,
                               edgecolor="white", linewidth=1.5))

ax.set_xlim(-0.1, N + 0.1)
ax.set_ylim(-0.1, N + 0.1)
ax.axis("off")

ax.text(KEPT / 2, KEPT / 2, "probe training\n(all components kept)",
        ha="center", va="center", fontsize=9, color=st.INK)
ax.text(KEPT + HELD / 2, KEPT + HELD / 2,
        "starved\nvalidation\n(all held out)", ha="center", va="center",
        fontsize=8, color=st.INK)
ax.text(KEPT + HELD / 2, KEPT / 2, "discarded\n(mixed)", ha="center",
        va="center", fontsize=8, color=st.INK_2, rotation=90)
ax.text(KEPT / 2, KEPT + HELD / 2, "discarded (mixed)", ha="center",
        va="center", fontsize=8, color=st.INK_2)

# held-out brackets on both axes
for lo, hi, axis in ((KEPT, N, "x"), (KEPT, N, "y")):
    if axis == "x":
        ax.plot([lo + 0.08, hi - 0.08], [-0.45, -0.45], color=st.INK_2,
                lw=1.2)
        ax.text((lo + hi) / 2, -0.85, "held-out values", ha="center",
                va="top", fontsize=8, color=st.INK_2)
    else:
        ax.plot([-0.45, -0.45], [lo + 0.08, hi - 0.08], color=st.INK_2,
                lw=1.2)
        ax.text(-0.85, (lo + hi) / 2, "held-out values", ha="right",
                va="center", fontsize=8, color=st.INK_2, rotation=90)

ax.text(N / 2, -1.7, "surface component 1 values", ha="center",
        fontsize=9, color=st.INK)
ax.text(-1.7, N / 2, "surface component 2 values", va="center",
        ha="center", fontsize=9, color=st.INK, rotation=90)

ax.set_xlim(-2.2, N + 0.3)
ax.set_ylim(-2.4, N + 0.3)

out = HERE / "figures"
out.mkdir(exist_ok=True)
for ext in ("pdf", "png"):
    fig.savefig(out / f"fig1_split.{ext}", dpi=300, bbox_inches="tight")
print(f"wrote {out}/fig1_split.pdf and .png")
