"""Composition tree: operators, area assignment, and rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from figpatch._layout import add_labels, estimate_figsize

if TYPE_CHECKING:
    from collections.abc import Callable

_PanelLike = Union["Panel", "Compose"]


class Compose:
    """A composition node in the layout tree.

    ``direction="h"`` splits the area left | right.
    ``direction="v"`` splits the area top / bottom.
    When ``right`` is ``None`` the node holds a single panel.
    """

    def __init__(
        self,
        left: _PanelLike,
        right: _PanelLike | None = None,
        direction: str = "h",
    ) -> None:
        self.left = left
        self.right = right
        self.direction = direction

    def __or__(self, other: _PanelLike) -> "Compose":
        return Compose(self, other, direction="h")

    def __truediv__(self, other: _PanelLike) -> "Compose":
        return Compose(self, other, direction="v")

    def render(
        self,
        figsize: tuple[float, float] | None = None,
        labels: bool | str = True,
        gap: float = 0.04,
    ) -> Figure:
        """Render the composition tree to a Matplotlib Figure.

        Parameters
        ----------
        figsize
            Figure size in inches. Auto-calculated when ``None``.
        labels
            ``True`` for A, B, C... labels; a string for prefixed labels
            (e.g. ``"S"`` produces S1, S2, ...).  ``False`` disables.
        gap
            Spacing between panels in figure-relative units (0–1).
        """

        panels_areas = self._flatten(0.0, 0.0, 1.0, 1.0)

        if figsize is None:
            figsize = estimate_figsize(panels_areas)

        fig = plt.figure(figsize=figsize)

        axes = []
        for panel, (x, y, w, h) in panels_areas:
            ax = fig.add_axes([x + gap / 2, y + gap / 2, w - gap, h - gap])
            panel(ax)
            axes.append(ax)

        add_labels(axes, labels)
        return fig

    def _flatten(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
    ) -> list[tuple[object, tuple[float, float, float, float]]]:
        """Recursively assign rectangular areas to every leaf panel."""

        if self.right is None:
            return [(self.left, (x, y, w, h))]

        if self.direction == "h":
            left_w = w / 2
            right_w = w - left_w
            left = _flatten_node(self.left, x, y, left_w, h)
            right = _flatten_node(self.right, x + left_w, y, right_w, h)
            return left + right
        else:
            top_h = h / 2
            bottom_h = h - top_h
            top = _flatten_node(self.left, x, y, w, top_h)
            bottom = _flatten_node(self.right, x, y + top_h, w, bottom_h)
            return top + bottom


def _flatten_node(
    node: _PanelLike,
    x: float,
    y: float,
    w: float,
    h: float,
) -> list[tuple[object, tuple[float, float, float, float]]]:
    """Flatten a Panel or Compose node into (panel, area) pairs."""

    if isinstance(node, Compose):
        return node._flatten(x, y, w, h)
    return [(node, (x, y, w, h))]


def compose(
    *items: Figure | object,
    direction: str = "h",
    figsize: tuple[float, float] | None = None,
    labels: bool | str = True,
    gap: float = 0.04,
) -> Figure:
    """Compose existing Matplotlib figures or axes into a single figure.

    Parameters
    ----------
    *items
        ``Figure`` or ``Axes`` objects to compose.
    direction
        ``"h"`` for horizontal layout, ``"v"`` for vertical.
    figsize
        Figure size in inches. Auto-calculated when ``None``.
    labels
        ``True`` for A, B, C... labels; a string prefix; or ``False``.
    gap
        Spacing between panels in figure-relative units.

    Returns
    -------
    matplotlib.figure.Figure
    """

    from figpatch._extract import collect_panels

    panels = collect_panels(*items)

    if len(panels) == 1:
        tree: Compose = Compose(panels[0], None)
    else:
        tree = Compose(panels[0], None)
        for p in panels[1:]:
            tree = Compose(tree, p, direction=direction)

    return tree.render(figsize=figsize, labels=labels, gap=gap)
