"""Compose existing figures with fp.compose().

Run with: uv run python examples/figure_compose.py
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

fig1, ax1 = plt.subplots()
ax1.plot(x, np.sin(x), color="#0072B2")
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Signal")
ax1.set_title("Sine")

fig2, ax2 = plt.subplots()
ax2.scatter(x, np.cos(x), color="#D55E00", s=20)
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Signal")
ax2.set_title("Cosine")

fig3, ax3 = plt.subplots()
ax3.bar(range(5), rng := np.random.default_rng(42).random(5), color="#009E73")
ax3.set_xlabel("Index")
ax3.set_ylabel("Value")
ax3.set_title("Bar")

composed = fp.compose(fig1, fig2, fig3, direction="h", figsize=(14, 4))
composed.savefig(OUTPUT / "figure_compose.pdf")
composed.savefig(OUTPUT / "figure_compose.png", dpi=150)
plt.close(fig1)
plt.close(fig2)
plt.close(fig3)
plt.close(composed)
print(f"Saved to {OUTPUT / 'figure_compose.pdf'}")
