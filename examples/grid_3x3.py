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

OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
x = np.linspace(0, 10, 100)


@fp.panel
def panel_a(ax):
    ax.plot(x, np.sin(x), color="#0072B2", linewidth=1.5, label="sin")
    ax.plot(x, np.cos(x), color="#D55E00", linewidth=1.5, label="cos")
    ax.legend(fontsize=7)
    ax.set_xlabel("Time")
    ax.set_ylabel("Signal")


@fp.panel
def panel_b(ax):
    ax.scatter(rng.normal(5, 2, 60), rng.normal(5, 2, 60), s=15, alpha=0.6, color="#009E73")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")


@fp.panel
def panel_c(ax):
    groups = ["A", "B", "C", "D"]
    values = [3.2, 5.1, 4.0, 4.8]
    ax.bar(groups, values, color="#CC79A7")
    ax.set_xlabel("Group")
    ax.set_ylabel("Value")


@fp.panel
def panel_d(ax):
    ax.hist(rng.normal(0, 1, 400), bins=25, color="#E69F00", edgecolor="white", linewidth=0.4)
    ax.set_xlabel("Value")
    ax.set_ylabel("Count")


@fp.panel
def panel_e(ax):
    data = [rng.normal(0, 1, 40) for _ in range(4)]
    ax.boxplot(data, tick_labels=["W", "X", "Y", "Z"])
    ax.set_xlabel("Set")
    ax.set_ylabel("Response")


@fp.panel
def panel_f(ax):
    ax.imshow(rng.random((10, 10)), cmap="viridis", aspect="auto")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")


@fp.panel
def panel_g(ax):
    ax.stem(x[::5], np.exp(-x[::5] / 3), linefmt="#56B4E9", markerfmt="o", basefmt=" ")
    ax.set_xlabel("Time")
    ax.set_ylabel("Decay")


@fp.panel
def panel_h(ax):
    ax.step(x, np.cumsum(rng.random(100)), color="#0072B2", linewidth=1.5)
    ax.set_xlabel("Step")
    ax.set_ylabel("Cumulative")


@fp.panel
def panel_i(ax):
    sizes = [30, 25, 20, 15, 10]
    labels = ["A", "B", "C", "D", "E"]
    colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00"]
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.0f%%", textprops={"fontsize": 6})
    ax.set_aspect("equal")


fig = (
    (panel_a | panel_b | panel_c)
    / (panel_d | panel_e | panel_f)
    / (panel_g | panel_h | panel_i)
)
fig = fig.render(figsize=(12, 12))
fig.savefig(OUTPUT / "grid_3x3.pdf")
fig.savefig(OUTPUT / "grid_3x3.png", dpi=150)
plt.close(fig)
print(f"Saved to {OUTPUT / 'grid_3x3.png'}")
