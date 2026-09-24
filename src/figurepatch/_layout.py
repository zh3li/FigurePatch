"""Layout utilities: figure size estimation and panel labels."""

from __future__ import annotations

import string
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from matplotlib.axes import Axes


def estimate_figsize(
    mosaic: list[list[str]],
    panel_w: float = 4.0,
    panel_h: float = 3.0,
) -> tuple[float, float]:
    """Estimate figure size (inches) from a mosaic matrix.

    Columns are counted per row (``len(row)``) so that spanning panels
    expand the estimate to the true grid width.
    """

    if not mosaic:
        return (max(panel_w, 4.0), max(panel_h, 3.0))

    nrows = len(mosaic)
    ncols = max(len(row) for row in mosaic)
    return (max(ncols * panel_w, 4.0), max(nrows * panel_h, 3.0))


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
