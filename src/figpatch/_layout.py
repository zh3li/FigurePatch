"""Layout utilities: figure size estimation and panel labels."""

from __future__ import annotations

import string
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence
    from matplotlib.axes import Axes


def estimate_figsize(
    layout_spec: Any,
    panel_w: float = 4.0,
    panel_h: float = 3.0,
) -> tuple[float, float]:
    """Estimate figure size (inches) from a mosaic matrix or panel areas."""

    # If passed a 2D mosaic matrix (list of lists of strings)
    if isinstance(layout_spec, list) and layout_spec and isinstance(layout_spec[0], list):
        nrows = len(layout_spec)
        max_cols = max(len(set(row)) for row in layout_spec)
        return (max(max_cols * panel_w, 4.0), max(nrows * panel_h, 3.0))

    # Backwards compatibility: passed a list of (panel, area) tuples
    if isinstance(layout_spec, list) and layout_spec and isinstance(layout_spec[0], tuple):
        x_starts = sorted({round(area[0], 6) for _, area in layout_spec})
        y_starts = sorted({round(area[1], 6) for _, area in layout_spec})
        ncols = max(len(x_starts), 1)
        nrows = max(len(y_starts), 1)
        return (max(ncols * panel_w, 4.0), max(nrows * panel_h, 3.0))

    return (8.0, 6.0)


def add_labels(axes: "Sequence[Axes]", labels: bool | str = True) -> None:
    """Add bold panel labels (A, B, C...) at the top-left of each axes."""

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
        ax.set_title(label, loc="left", fontsize=9, fontweight="bold")
