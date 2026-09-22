"""3x3 grid: 9 panels with different plot types.

Layout: (A|B|C) / (D|E|F) / (G|H|I)

Run with: uv run python examples/grid_3x3.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figpatch as fp
from _style import PALETTE, BLUE, SALMON, TEAL, SLATE, CRIMSON, BROWN, MINT, setup_ax, style

OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
x = np.linspace(0, 10, 100)


@fp.panel
def panel_a(ax):
    ax.plot(x, np.sin(x), color=BLUE, linewidth=1.0, label="sin")
    ax.plot(x, np.cos(x), color=SALMON, linewidth=1.0, label="cos")
    ax.legend(fontsize=6, markerscale=0.5, handlelength=0.7)
    ax.set_xlabel("Time")
    ax.set_ylabel("Signal")
    setup_ax(ax)


@fp.panel
def panel_b(ax):
    ax.scatter(rng.normal(5, 2, 60), rng.normal(5, 2, 60), s=6, alpha=0.6, color=TEAL, edgecolors="none")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    setup_ax(ax)


@fp.panel
def panel_c(ax):
    groups = ["A", "B", "C", "D"]
    values = [3.2, 5.1, 4.0, 4.8]
    ax.bar(groups, values, color=SLATE, width=0.6)
    ax.set_xlabel("Group")
    ax.set_ylabel("Value")
    setup_ax(ax)


@fp.panel
def panel_d(ax):
    ax.hist(rng.normal(0, 1, 400), bins=25, color=CRIMSON, edgecolor="white", linewidth=0.3)
    ax.set_xlabel("Value")
    ax.set_ylabel("Count")
    setup_ax(ax)


@fp.panel
def panel_e(ax):
    data = [rng.normal(0, 1, 40) for _ in range(4)]
    ax.boxplot(data, tick_labels=["W", "X", "Y", "Z"], widths=0.5)
    ax.set_xlabel("Set")
    ax.set_ylabel("Response")
    setup_ax(ax)


@fp.panel
def panel_f(ax):
    ax.imshow(rng.random((10, 10)), cmap="viridis", aspect="auto")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    setup_ax(ax)


@fp.panel
def panel_g(ax):
    ax.stem(x[::5], np.exp(-x[::5] / 3), linefmt=BLUE, markerfmt="o", basefmt=" ")
    ax.set_xlabel("Time")
    ax.set_ylabel("Decay")
    setup_ax(ax)


@fp.panel
def panel_h(ax):
    ax.step(x, np.cumsum(rng.random(100)), color=MINT, linewidth=1.0)
    ax.set_xlabel("Step")
    ax.set_ylabel("Cumulative")
    setup_ax(ax)


@fp.panel
def panel_i(ax):
    sizes = [30, 25, 20, 15, 10]
    labels = ["A", "B", "C", "D", "E"]
    colors = [BLUE, SALMON, TEAL, SLATE, CRIMSON]
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.0f%%", textprops={"fontsize": 5})
    ax.set_aspect("equal")


with style():
    fig = (
        (panel_a | panel_b | panel_c)
        / (panel_d | panel_e | panel_f)
        / (panel_g | panel_h | panel_i)
    )
    fig = fig.render(figsize=(10, 10), gap=0.06)
    fig.savefig(OUTPUT / "grid_3x3.pdf")
    fig.savefig(OUTPUT / "grid_3x3.png", dpi=288, transparent=True)
    plt.close(fig)
print(f"Saved to {OUTPUT / 'grid_3x3.png'}")
