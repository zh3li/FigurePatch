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

OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

x = np.linspace(0, 10, 50)
rng = np.random.default_rng(42)


@fp.panel
def panel_a(ax):
    ax.plot(x, np.sin(x), color="#0072B2")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Signal")


@fp.panel
def panel_b(ax):
    ax.scatter(x, rng.normal(0, 0.3, len(x)), color="#D55E00", s=15)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Noise")


@fp.panel
def panel_c(ax):
    groups = ["WT", "KO", "R1", "R2"]
    values = [3.2, 5.1, 4.0, 4.8]
    errors = [0.3, 0.4, 0.25, 0.35]
    ax.bar(groups, values, yerr=errors, capsize=3, color=["#009E73", "#E69F00", "#56B4E9", "#CC79A7"])
    ax.set_xlabel("Genotype")
    ax.set_ylabel("Expression")


fig = ((panel_a | panel_b) / panel_c).render(figsize=(10, 8))
fig.savefig(OUTPUT / "complex_layout.pdf")
fig.savefig(OUTPUT / "complex_layout.png", dpi=150)
plt.close(fig)
print(f"Saved to {OUTPUT / 'complex_layout.pdf'}")
