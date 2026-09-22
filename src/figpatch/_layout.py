"""Layout utilities: figure size estimation and panel labels."""

from __future__ import annotations

import string
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from matplotlib.axes import Axes


def estimate_figsize(
    panels_areas: list[tuple[object, tuple[float, float, float, float]]],
    panel_w: float = 4.0,
    panel_h: float = 3.0,
) -> tuple[float, float]:
    """Estimate figure size (inches) from a flattened list of (panel, area) pairs."""

    x_starts = sorted({round(area[0], 6) for _, area in panels_areas})
    y_starts = sorted({round(area[1], 6) for _, area in panels_areas})
    ncols = len(x_starts)
    nrows = len(y_starts)
    return (max(ncols * panel_w, 4.0), max(nrows * panel_h, 3.0))


def add_labels(axes: "Sequence[Axes]", labels: bool | str = True) -> None:
    """Add panel labels (A, B, C...) to axes in reading order."""

    if not labels:
        return

    if labels is True:
        prefix = ""
        use_letters = True
    else:
        prefix = str(labels)
        use_letters = False

    for i, ax in enumerate(axes):
        if use_letters:
            label = string.ascii_uppercase[i] if i < 26 else str(i + 1)
        else:
            label = f"{prefix}{i + 1}"
        ax.set_title(label, loc="left", fontsize=11, fontweight="bold")
