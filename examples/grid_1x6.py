"""1x6 single row: 6 panels side by side.

Layout: A | B | C | D | E | F

Run with: uv run python examples/grid_1x6.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figpatch as fp
from _style import BLUE, SALMON, TEAL, SLATE, CRIMSON, BROWN, setup_ax, style

OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
x = np.linspace(0, 10, 50)


@fp.panel
def panel_a(ax):
    ax.plot(x, np.sin(x), color=BLUE, linewidth=1.0)
    ax.set_xlabel("Time")
    ax.set_ylabel("Signal")
    setup_ax(ax)


@fp.panel
def panel_b(ax):
    ax.scatter(x, rng.normal(0, 0.3, 50), s=6, color=SALMON, alpha=0.7, edgecolors="none")
    ax.set_xlabel("Time")
    ax.set_ylabel("Noise")
    setup_ax(ax)


@fp.panel
def panel_c(ax):
    ax.bar(range(5), rng.random(5), color=TEAL, width=0.6)
    ax.set_xlabel("Index")
    ax.set_ylabel("Value")
    setup_ax(ax)


@fp.panel
def panel_d(ax):
    ax.hist(rng.normal(0, 1, 200), bins=20, color=SLATE, edgecolor="white", linewidth=0.3)
    ax.set_xlabel("Value")
    ax.set_ylabel("Count")
    setup_ax(ax)


@fp.panel
def panel_e(ax):
    ax.boxplot([rng.normal(0, 1, 30), rng.normal(1, 1.5, 30)], tick_labels=["A", "B"], widths=0.5)
    ax.set_xlabel("Group")
    ax.set_ylabel("Response")
    setup_ax(ax)


@fp.panel
def panel_f(ax):
    ax.plot(x, np.exp(-x / 3), color=CRIMSON, linewidth=1.0)
    ax.fill_between(x, 0, np.exp(-x / 3), alpha=0.1, color=CRIMSON)
    ax.set_xlabel("Time")
    ax.set_ylabel("Decay")
    setup_ax(ax)


with style():
    fig = (panel_a | panel_b | panel_c | panel_d | panel_e | panel_f).render(figsize=(14, 3), gap=0.06)
    fig.savefig(OUTPUT / "grid_1x6.pdf")
    fig.savefig(OUTPUT / "grid_1x6.png", dpi=288, transparent=True)
    plt.close(fig)
print(f"Saved to {OUTPUT / 'grid_1x6.png'}")
