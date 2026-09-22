"""2x3 grid: 6 panels with different plot types.

Layout: (A | B | C) / (D | E | F)

Run with: uv run python examples/grid_2x3.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figpatch as fp
from _style import PALETTE, BLUE, SALMON, TEAL, SLATE, CRIMSON, BROWN, setup_ax, style

OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
x = np.linspace(0, 10, 100)


@fp.panel
def panel_a(ax):
    ax.plot(x, np.sin(x), color=BLUE, linewidth=1.0)
    ax.fill_between(x, np.sin(x) - 0.3, np.sin(x) + 0.3, alpha=0.15, color=BLUE)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Signal")
    setup_ax(ax)


@fp.panel
def panel_b(ax):
    ax.scatter(rng.normal(5, 2, 80), rng.normal(5, 2, 80), s=8, alpha=0.6, color=SALMON, edgecolors="none")
    ax.set_xlabel("Feature A")
    ax.set_ylabel("Feature B")
    setup_ax(ax)


@fp.panel
def panel_c(ax):
    groups = ["WT", "KO", "R1", "R2", "R3"]
    values = [3.2, 5.1, 4.0, 4.8, 3.9]
    errors = [0.3, 0.4, 0.25, 0.35, 0.2]
    ax.bar(groups, values, yerr=errors, capsize=2, color=TEAL, width=0.6)
    ax.set_xlabel("Genotype")
    ax.set_ylabel("Expression")
    setup_ax(ax)


@fp.panel
def panel_d(ax):
    data = rng.normal(0, 1, 500)
    ax.hist(data, bins=30, color=SLATE, edgecolor="white", linewidth=0.3)
    ax.set_xlabel("Value")
    ax.set_ylabel("Count")
    setup_ax(ax)


@fp.panel
def panel_e(ax):
    data = [rng.normal(0, 1, 50), rng.normal(1, 1.2, 50), rng.normal(0.5, 0.8, 50)]
    ax.boxplot(data, tick_labels=["A", "B", "C"], widths=0.5)
    ax.set_xlabel("Group")
    ax.set_ylabel("Response")
    setup_ax(ax)


@fp.panel
def panel_f(ax):
    ax.plot(x, np.cos(x), color=CRIMSON, linewidth=1.0)
    ax.plot(x, -np.cos(x), color=BROWN, linewidth=1.0)
    ax.fill_between(x, np.cos(x), -np.cos(x), alpha=0.1, color=CRIMSON)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    setup_ax(ax)


with style():
    fig = (panel_a | panel_b | panel_c) / (panel_d | panel_e | panel_f)
    fig = fig.render(figsize=(10, 6), gap=0.06)
    fig.savefig(OUTPUT / "grid_2x3.pdf")
    fig.savefig(OUTPUT / "grid_2x3.png", dpi=288, transparent=True)
    plt.close(fig)
print(f"Saved to {OUTPUT / 'grid_2x3.png'}")
