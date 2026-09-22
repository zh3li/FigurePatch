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

OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
x = np.linspace(0, 10, 50)


@fp.panel
def panel_a(ax):
    ax.plot(x, np.sin(x), color="#0072B2")
    ax.set_xlabel("Time")
    ax.set_ylabel("Signal")


@fp.panel
def panel_b(ax):
    ax.scatter(x, rng.normal(0, 0.3, 50), s=12, color="#D55E00", alpha=0.7)
    ax.set_xlabel("Time")
    ax.set_ylabel("Noise")


@fp.panel
def panel_c(ax):
    ax.bar(range(5), rng.random(5), color="#009E73")
    ax.set_xlabel("Index")
    ax.set_ylabel("Value")


@fp.panel
def panel_d(ax):
    ax.hist(rng.normal(0, 1, 200), bins=20, color="#CC79A7")
    ax.set_xlabel("Value")
    ax.set_ylabel("Count")


@fp.panel
def panel_e(ax):
    ax.boxplot([rng.normal(0, 1, 30), rng.normal(1, 1.5, 30)], tick_labels=["A", "B"])
    ax.set_xlabel("Group")
    ax.set_ylabel("Response")


@fp.panel
def panel_f(ax):
    ax.plot(x, np.exp(-x / 3), color="#E69F00")
    ax.fill_between(x, 0, np.exp(-x / 3), alpha=0.2, color="#E69F00")
    ax.set_xlabel("Time")
    ax.set_ylabel("Decay")


fig = (panel_a | panel_b | panel_c | panel_d | panel_e | panel_f).render(figsize=(18, 3.5))
fig.savefig(OUTPUT / "grid_1x6.pdf")
fig.savefig(OUTPUT / "grid_1x6.png", dpi=150)
plt.close(fig)
print(f"Saved to {OUTPUT / 'grid_1x6.png'}")
