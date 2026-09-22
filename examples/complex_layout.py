"""Complex nested layout: (panel_a | panel_b) / panel_c.

panel_c spans the full width automatically.

Run with: uv run python examples/complex_layout.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figpatch as fp
from _style import BLUE, SALMON, TEAL, PALETTE, setup_ax, style

OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

x = np.linspace(0, 10, 50)
rng = np.random.default_rng(42)


@fp.panel
def panel_a(ax):
    ax.plot(x, np.sin(x), color=BLUE, linewidth=1.0)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Signal")
    setup_ax(ax)


@fp.panel
def panel_b(ax):
    ax.scatter(x, rng.normal(0, 0.3, len(x)), color=SALMON, s=8, alpha=0.7)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Noise")
    setup_ax(ax)


@fp.panel
def panel_c(ax):
    groups = ["WT", "KO", "R1", "R2"]
    values = [3.2, 5.1, 4.0, 4.8]
    errors = [0.3, 0.4, 0.25, 0.35]
    ax.bar(groups, values, yerr=errors, capsize=2, color=[BLUE, SALMON, TEAL, PALETTE[5]], width=0.6)
    ax.set_xlabel("Genotype")
    ax.set_ylabel("Expression")
    setup_ax(ax)


with style():
    fig = ((panel_a | panel_b) / panel_c).render(figsize=(7, 6), gap=0.06)
    fig.savefig(OUTPUT / "complex_layout.pdf")
    fig.savefig(OUTPUT / "complex_layout.png", dpi=288, transparent=True)
    plt.close(fig)
print(f"Saved to {OUTPUT / 'complex_layout.png'}")
