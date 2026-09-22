"""Basic two-panel composition: panel_a | panel_b.

Run with: uv run python examples/basic_compose.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figurepatch as fp
from _style import BLUE, SALMON, setup_ax, style

OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

x = np.linspace(0, 10, 50)


@fp.panel
def panel_a(ax):
    ax.plot(x, np.sin(x), "o-", color=BLUE, linewidth=1.0, markersize=3)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Sine wave")
    setup_ax(ax)


@fp.panel
def panel_b(ax):
    ax.scatter(x, np.cos(x), color=SALMON, s=12)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Cosine wave")
    setup_ax(ax)


with style():
    fig = (panel_a | panel_b).render(figsize=(7.2, 3.2))
    fig.savefig(OUTPUT / "basic_compose.pdf")
    fig.savefig(OUTPUT / "basic_compose.png", dpi=288, transparent=True)
    plt.close(fig)
print(f"Saved to {OUTPUT / 'basic_compose.png'}")
