"""Shared style for the paper's figures. Palette validated 2026-07-27
(dataviz six-checks: lightness band, chroma floor, CVD dE 96.7 worst
adjacent, contrast >= 3:1 on white). Semantic assignment held constant
across figures: blue = trained model, orange = untrained twin."""

TRAINED = "#2a78d6"
UNTRAINED = "#eb6834"
VAL_TINT = "#4a3aa7"   # F1 region hue only, used at low alpha
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#eceae6"
SPINE = "#c8c6c0"
CONNECT = "#d8d7d3"


def apply(ax, xgrid=True):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(SPINE)
    ax.tick_params(colors=INK_2, labelsize=8, length=3)
    if xgrid:
        ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
