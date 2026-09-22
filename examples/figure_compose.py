"""Compose existing figures with fp.compose().

Run with: uv run python examples/figure_compose.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figpatch as fp
from _style import BLUE, SALMON, TEAL, setup_ax, style

OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

x = np.linspace(0, 10, 50)

with style():
    fig1, ax1 = plt.subplots()
    ax1.plot(x, np.sin(x), color=BLUE, linewidth=1.0)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Signal")
    ax1.set_title("Sine")
    setup_ax(ax1)

    fig2, ax2 = plt.subplots()
    ax2.scatter(x, np.cos(x), color=SALMON, s=8)
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Signal")
    ax2.set_title("Cosine")
    setup_ax(ax2)

    fig3, ax3 = plt.subplots()
    ax3.bar(range(5), np.random.default_rng(42).random(5), color=TEAL, width=0.6)
    ax3.set_xlabel("Index")
    ax3.set_ylabel("Value")
    ax3.set_title("Bar")
    setup_ax(ax3)

    composed = fp.compose(fig1, fig2, fig3, direction="h", figsize=(9.0, 3.0))
    composed.savefig(OUTPUT / "figure_compose.pdf")
    composed.savefig(OUTPUT / "figure_compose.png", dpi=288, transparent=True)
    plt.close(fig1)
    plt.close(fig2)
    plt.close(fig3)
    plt.close(composed)
print(f"Saved to {OUTPUT / 'figure_compose.png'}")
