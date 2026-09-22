"""Basic two-panel composition: panel_a | panel_b.

Run with: uv run python examples/basic_compose.py
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


@fp.panel
def panel_a(ax):
    ax.plot(x, np.sin(x), "o-", color="#0072B2")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Sine wave")


@fp.panel
def panel_b(ax):
    ax.scatter(x, np.cos(x), color="#D55E00", s=20)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Cosine wave")


fig = (panel_a | panel_b).render(figsize=(10, 4))
fig.savefig(OUTPUT / "basic_compose.pdf")
fig.savefig(OUTPUT / "basic_compose.png", dpi=150)
plt.close(fig)
print(f"Saved to {OUTPUT / 'basic_compose.pdf'}")
