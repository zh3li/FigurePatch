"""Composition tree: operators, area assignment, and rendering."""

from __future__ import annotations

import itertools
import math
from typing import Union

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from figurepatch._layout import add_labels, estimate_figsize

_PanelLike = Union["Panel", "Compose"]

# Guard against pathological least-common-multiple blowups, e.g. sibling
# groups with coprime panel counts (2 | 3 | 5 | 7 | 11 columns).
_MAX_MOSAIC_CELLS = 2000


def _validate_operand(other: object, op: str) -> _PanelLike:
    """Return *other* if it can act as a panel; raise a helpful TypeError."""

    from figurepatch._panel import Panel

    if isinstance(other, (Panel, Compose)) or callable(other):
        return other  # type: ignore[return-value]
    raise TypeError(
        f"unsupported operand type for '{op}': {type(other).__name__!r}; "
        "expected a Panel, Compose, or a callable taking an Axes"
    )


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

    Every leaf *occurrence* is assigned a unique sequential key, so the
    same panel object may safely appear multiple times in one
    composition (``p | p`` yields two independent axes).
    """

    from figurepatch._panel import Panel

    counter = itertools.count()
    panels: list[object] = []

    def leaf_key(leaf: object) -> str:
        key = f"p{next(counter)}"
        panels.append(leaf)
        return key

    def build(n: _PanelLike) -> tuple[list[list[str]], list[str]]:
        if isinstance(n, Panel) or getattr(n, "right", None) is None:
            leaf = n.left if isinstance(n, Compose) else n
            key = leaf_key(leaf)
            return [[key]], [key]

        children = n._collect_children()
        sub_mats: list[list[list[str]]] = []
        keys_list: list[str] = []

        for child in children:
            mat, k_list = build(child)
            sub_mats.append(mat)
            keys_list.extend(k_list)

        if n.direction == "h":
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
            return result, keys_list
        else:  # "v"
            col_counts = [len(m[0]) for m in sub_mats]
            target_cols = col_counts[0]
            for cc in col_counts[1:]:
                target_cols = math.lcm(target_cols, cc)

            expanded = [_repeat_cols(m, target_cols // len(m[0])) for m in sub_mats]
            result = []
            for m in expanded:
                result.extend(m)
            return result, keys_list

    mosaic, keys = build(node)

    n_cells = len(mosaic) * len(mosaic[0])
    if n_cells > _MAX_MOSAIC_CELLS:
        raise ValueError(
            f"layout expands to a {len(mosaic)}x{len(mosaic[0])} grid "
            f"({n_cells} cells) for {len(panels)} panels; regroup siblings "
            "with parentheses so neighbouring groups share factors "
            "(e.g. prefer equal panel counts per row)"
        )

    return mosaic, panels, keys


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
        if direction not in ("h", "v"):
            raise ValueError(f"direction must be 'h' or 'v', got {direction!r}")
        self.left = left
        self.right = right
        self.direction = direction

    def __repr__(self) -> str:
        op = "|" if self.direction == "h" else "/"
        if self.right is None:
            return f"Compose({self.left!r})"
        return f"Compose({self.left!r} {op} {self.right!r})"

    def __or__(self, other: _PanelLike) -> "Compose":
        return Compose(self, _validate_operand(other, "|"), direction="h")

    def __truediv__(self, other: _PanelLike) -> "Compose":
        return Compose(self, _validate_operand(other, "/"), direction="v")

    def render(
        self,
        figsize: tuple[float, float] | None = None,
        labels: bool | str = True,
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


def compose(
    *items: Figure | plt.Axes,
    direction: str = "h",
    figsize: tuple[float, float] | None = None,
    labels: bool | str = True,
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

    Returns
    -------
    matplotlib.figure.Figure
    """

    from figurepatch._extract import collect_panels

    panels = collect_panels(*items)

    tree: Compose = Compose(panels[0], None)
    for p in panels[1:]:
        tree = Compose(tree, p, direction=direction)

    return tree.render(figsize=figsize, labels=labels)
