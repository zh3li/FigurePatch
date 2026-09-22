"""Composition tree: operators, area assignment, and rendering."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Union

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from figpatch._layout import add_labels, estimate_figsize

if TYPE_CHECKING:
    from collections.abc import Callable

_PanelLike = Union["Panel", "Compose"]


def _repeat_cols(matrix: list[list[str]], factor: int) -> list[list[str]]:
    """Repeat each column in a 2D matrix by factor."""
    new_m = []
    for row in matrix:
        new_row = []
        for cell in row:
            new_row.extend([cell] * factor)
        new_m.append(new_row)
    return new_m


def _repeat_rows(matrix: list[list[str]], factor: int) -> list[list[str]]:
    """Repeat each row in a 2D matrix by factor."""
    new_m = []
    for row in matrix:
        for _ in range(factor):
            new_m.append(list(row))
    return new_m


def tree_to_mosaic(
    node: _PanelLike,
) -> tuple[list[list[str]], list[object], list[str]]:
    """Convert a composition tree into a 2D mosaic grid matrix.

    Returns ``(mosaic_matrix, ordered_panels, ordered_keys)`` where
    row 0 is the top row and row N-1 is the bottom row.
    """

    from figpatch._panel import Panel

    if isinstance(node, Panel) or getattr(node, "right", None) is None:
        leaf = node.left if isinstance(node, Compose) else node
        key = f"p_{id(leaf)}"
        return [[key]], [leaf], [key]

    children = node._collect_children()
    sub_mats: list[list[list[str]]] = []
    panels_list: list[object] = []
    keys_list: list[str] = []

    for child in children:
        mat, p_list, k_list = tree_to_mosaic(child)
        sub_mats.append(mat)
        panels_list.extend(p_list)
        keys_list.extend(k_list)

    if node.direction == "h":
        row_counts = [len(m) for m in sub_mats]
        target_rows = row_counts[0]
        for rc in row_counts[1:]:
            target_rows = math.lcm(target_rows, rc)

        expanded = [_repeat_rows(m, target_rows // len(m)) for m in sub_mats]
        result: list[list[str]] = []
        for r in range(target_rows):
            row: list[str] = []
            for m in expanded:
                row.extend(m[r])
            result.append(row)
        return result, panels_list, keys_list
    else:  # "v"
        col_counts = [len(m[0]) for m in sub_mats]
        target_cols = col_counts[0]
        for cc in col_counts[1:]:
            target_cols = math.lcm(target_cols, cc)

        expanded = [_repeat_cols(m, target_cols // len(m[0])) for m in sub_mats]
        result = []
        for m in expanded:
            result.extend(m)
        return result, panels_list, keys_list


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
        gap: float | None = None,
    ) -> Figure:
        """Render the composition tree to a Matplotlib Figure.

        Uses Matplotlib's native ``layout="constrained"`` to dynamically
        prevent overlaps and ensure all labels, titles, and ticks fit.

        Parameters
        ----------
        figsize
            Figure size in inches. Auto-calculated when ``None``.
        labels
            ``True`` for bold A, B, C... labels at top-left; a string for
            prefixed labels (e.g. ``"S"`` produces S1, S2, ...); or ``False``.
        gap
            Deprecated parameter retained for backwards compatibility.
        """

        mosaic, panels, keys = tree_to_mosaic(self)

        if figsize is None:
            figsize = estimate_figsize(mosaic)

        fig, axd = plt.subplot_mosaic(mosaic, figsize=figsize, layout="constrained")

        axes = []
        for panel_obj, key in zip(panels, keys, strict=True):
            ax = axd[key]
            panel_obj(ax)  # type: ignore[operator]
            axes.append(ax)

        add_labels(axes, labels)
        return fig

    def _collect_children(self) -> list[_PanelLike]:
        """Collect all children at the same composition level.

        When a child has the same direction as this node, its children
        are merged into the result so that all siblings share space equally.
        """

        if self.right is None:
            return [self.left]

        children: list[_PanelLike] = []
        for child in (self.left, self.right):
            if (
                isinstance(child, Compose)
                and child.direction == self.direction
                and child.right is not None
            ):
                children.extend(child._collect_children())
            else:
                children.append(child)
        return children

    def _flatten(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
    ) -> list[tuple[object, tuple[float, float, float, float]]]:
        """Recursively assign rectangular areas to every leaf panel (document order)."""

        if self.right is None:
            return [(self.left, (x, y, w, h))]

        children = self._collect_children()
        n = len(children)

        if self.direction == "h":
            panel_w = w / n
            result: list[tuple[object, tuple[float, float, float, float]]] = []
            for i, child in enumerate(children):
                result.extend(_flatten_node(child, x + i * panel_w, y, panel_w, h))
            return result
        else:
            panel_h = h / n
            result = []
            for i, child in enumerate(children):
                result.extend(_flatten_node(child, x, y + i * panel_h, w, panel_h))
            return result


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
    gap: float | None = None,
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
        Deprecated parameter retained for backwards compatibility.

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
