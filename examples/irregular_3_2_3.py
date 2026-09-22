"""Irregular layout: 3+2+3 panels in 3 rows.

Layout: (A | B | C) / (D | E) / (F | G | H)

Row 1 has 3 equal columns, row 2 has 2 wider columns, row 3 has 3 again.

Run with: uv run python examples/irregular_3_2_3.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figpatch as fp
from _style import BLUE, SALMON, TEAL, SLATE, CRIMSON, BROWN, MINT, setup_ax, style

OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
x = np.linspace(0, 10, 100)


@fp.panel
def panel_a(ax):
    ax.plot(x, np.sin(x), color=BLUE, linewidth=1.0)
    ax.set_xlabel("Time")
    ax.set_ylabel("Signal")
    setup_ax(ax)


@fp.panel
def panel_b(ax):
    ax.scatter(rng.normal(5, 2, 60), rng.normal(5, 2, 60), s=6, alpha=0.6, color=SALMON, edgecolors="none")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    setup_ax(ax)


@fp.panel
def panel_c(ax):
    ax.bar(["W", "X", "Y", "Z"], [3, 5, 4, 4.5], color=TEAL, width=0.6)
    ax.set_xlabel("Group")
    ax.set_ylabel("Value")
    setup_ax(ax)


@fp.panel
def panel_d(ax):
    data = rng.random((8, 8))
    im = ax.imshow(data, cmap="viridis", aspect="auto")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    setup_ax(ax)
    fig = ax.get_figure()
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)


@fp.panel
def panel_e(ax):
    parts = rng.normal(0, 1, (4, 40))
    ax.boxplot(parts.T, tick_labels=["A", "B", "C", "D"], widths=0.5)
    ax.set_xlabel("Set")
    ax.set_ylabel("Response")
    setup_ax(ax)


@fp.panel
def panel_f(ax):
    ax.hist(rng.normal(0, 1, 300), bins=25, color=CRIMSON, edgecolor="white", linewidth=0.3)
    ax.set_xlabel("Value")
    ax.set_ylabel("Count")
    setup_ax(ax)


@fp.panel
def panel_g(ax):
    ax.plot(x, np.cumsum(rng.random(100)), color=MINT, linewidth=1.0)
    ax.set_xlabel("Step")
    ax.set_ylabel("Cumulative")
    setup_ax(ax)


@fp.panel
def panel_h(ax):
    ax.stem(x[::4], np.exp(-x[::4] / 3), linefmt=BROWN, markerfmt="o", basefmt=" ")
    ax.set_xlabel("Time")
    ax.set_ylabel("Decay")
    setup_ax(ax)


with style():
    fig = (
        (panel_a | panel_b | panel_c)
        / (panel_d | panel_e)
        / (panel_f | panel_g | panel_h)
    )
    fig = fig.render(figsize=(10, 10), gap=0.06)
    fig.savefig(OUTPUT / "irregular_3_2_3.pdf")
    fig.savefig(OUTPUT / "irregular_3_2_3.png", dpi=288, transparent=True)
    plt.close(fig)
print(f"Saved to {OUTPUT / 'irregular_3_2_3.png'}")
