"""Artist extraction: re-create axes content from an existing figure."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import Collection
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.text import Text

if TYPE_CHECKING:
    from collections.abc import Callable


class AxesPanel:
    """A panel that re-creates the content of an existing axes."""

    def __init__(self, src_ax: Axes) -> None:
        self._src_ax = src_ax

    def __call__(self, ax: Axes) -> None:
        copy_axes_content(self._src_ax, ax)


def copy_axes_content(src_ax: Axes, dst_ax: Axes) -> None:
    """Copy all content from *src_ax* to *dst_ax*."""

    _copy_axes_props(src_ax, dst_ax)

    for line in src_ax.lines:
        _copy_line(line, dst_ax)

    for collection in src_ax.collections:
        _copy_collection(collection, dst_ax)

    for patch in src_ax.patches:
        _copy_patch(patch, dst_ax)

    for image in src_ax.images:
        _copy_image(image, dst_ax)

    for text in src_ax.texts:
        _copy_text(text, dst_ax)

    if src_ax.legend_ is not None:
        handles, labels = src_ax.get_legend_handles_labels()
        if labels:
            dst_ax.legend(handles, labels)


def _copy_axes_props(src_ax: Axes, dst_ax: Axes) -> None:
    """Copy axes-level properties (limits, scale, labels, spines)."""

    dst_ax.set_xlim(src_ax.get_xlim())
    dst_ax.set_ylim(src_ax.get_ylim())
    dst_ax.set_xscale(src_ax.get_xscale())
    dst_ax.set_yscale(src_ax.get_yscale())

    if src_ax.get_xlabel():
        dst_ax.set_xlabel(src_ax.get_xlabel())
    if src_ax.get_ylabel():
        dst_ax.set_ylabel(src_ax.get_ylabel())
    if src_ax.get_title():
        dst_ax.set_title(src_ax.get_title())

    dst_ax.set_facecolor(src_ax.get_facecolor())

    for name in ("top", "right", "bottom", "left"):
        src_spine = src_ax.spines[name]
        dst_spine = dst_ax.spines[name]
        dst_spine.set_visible(src_spine.get_visible())
        dst_spine.set_linewidth(src_spine.get_linewidth())

    src_ticks = src_ax.get_xticks()
    dst_ax.set_xticks(src_ticks)
    src_yticks = src_ax.get_yticks()
    dst_ax.set_yticks(src_yticks)


def _copy_line(line: Line2D, dst_ax: Axes) -> None:
    """Re-create a Line2D on *dst_ax*."""

    xdata = np.asarray(line.get_xdata())
    ydata = np.asarray(line.get_ydata())
    new_lines = dst_ax.plot(xdata, ydata)
    new_line = new_lines[0]

    new_line.set_color(line.get_color())
    new_line.set_linewidth(line.get_linewidth())
    new_line.set_linestyle(line.get_linestyle())
    new_line.set_marker(line.get_marker())
    new_line.set_markersize(line.get_markersize())
    new_line.set_markeredgecolor(line.get_markeredgecolor())
    new_line.set_markerfacecolor(line.get_markerfacecolor())
    new_line.set_alpha(line.get_alpha())
    new_line.set_label(line.get_label())
    new_line.set_zorder(line.get_zorder())
    new_line.set_visible(line.get_visible())


def _copy_collection(collection: Collection, dst_ax: Axes) -> None:
    """Re-create a Collection (e.g. scatter) on *dst_ax*."""

    offsets = collection.get_offsets()
    if len(offsets) == 0:
        return

    x = offsets[:, 0]
    y = offsets[:, 1]

    facecolors = collection.get_facecolor()
    edgecolors = collection.get_edgecolor()
    sizes = collection.get_sizes()
    alpha = collection.get_alpha()

    fc = facecolors if len(facecolors) > 1 else facecolors[0]
    ec = edgecolors if len(edgecolors) > 1 else edgecolors[0]
    s = sizes if len(sizes) > 1 else sizes[0]

    kwargs: dict[str, object] = {}
    if alpha is not None:
        kwargs["alpha"] = alpha

    if len(facecolors) <= 1:
        dst_ax.scatter(x, y, color=fc, s=s, edgecolors=ec, **kwargs)
    else:
        dst_ax.scatter(x, y, c=fc, s=s, edgecolors=ec, **kwargs)


def _copy_patch(patch: Patch, dst_ax: Axes) -> None:
    """Re-create a Patch (e.g. bar) on *dst_ax*."""

    if isinstance(patch, Rectangle):
        rect = Rectangle(
            (patch.get_x(), patch.get_y()),
            patch.get_width(),
            patch.get_height(),
            facecolor=patch.get_facecolor(),
            edgecolor=patch.get_edgecolor(),
            linewidth=patch.get_linewidth(),
            alpha=patch.get_alpha(),
        )
        dst_ax.add_patch(rect)
    else:
        new_patch = patch.__class__(
            patch.get_xy(),
            patch.get_width(),
            patch.get_height(),
            facecolor=patch.get_facecolor(),
            edgecolor=patch.get_edgecolor(),
            linewidth=patch.get_linewidth(),
            alpha=patch.get_alpha(),
        )
        dst_ax.add_patch(new_patch)


def _copy_image(image: AxesImage, dst_ax: Axes) -> None:
    """Re-create an AxesImage (imshow) on *dst_ax*."""

    kwargs: dict[str, object] = {
        "cmap": image.get_cmap(),
        "vmin": image.get_clim()[0],
        "vmax": image.get_clim()[1],
        "extent": image.get_extent(),
        "interpolation": image.get_interpolation(),
    }
    aspect = getattr(image, "_aspect", None)
    if aspect is not None:
        kwargs["aspect"] = aspect

    dst_ax.imshow(image.get_array(), **kwargs)


def _copy_text(text: Text, dst_ax: Axes) -> None:
    """Re-create a Text artist on *dst_ax*."""

    content = text.get_text()
    if not content:
        return

    pos = text.get_position()
    dst_ax.text(
        pos[0],
        pos[1],
        content,
        fontsize=text.get_fontsize(),
        color=text.get_color(),
        fontweight=text.get_fontweight(),
        fontstyle=text.get_fontstyle(),
        ha=text.get_horizontalalignment(),
        va=text.get_verticalalignment(),
        rotation=text.get_rotation(),
    )


def collect_panels(
    *items: Figure | Axes,
) -> list[AxesPanel]:
    """Extract AxesPanel objects from a mix of Figure and Axes inputs."""

    panels: list[AxesPanel] = []
    for item in items:
        if isinstance(item, Figure):
            for ax in item.axes:
                panels.append(AxesPanel(ax))
        elif isinstance(item, Axes):
            panels.append(AxesPanel(item))
        else:
            raise TypeError(
                f"Expected Figure or Axes, got {type(item).__name__}"
            )

    if not panels:
        raise ValueError("No axes found in the provided items")

    return panels
