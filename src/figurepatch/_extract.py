"""Artist extraction: re-create axes content from an existing figure."""

from __future__ import annotations

import copy as _copy
import warnings
from typing import TYPE_CHECKING

import numpy as np
from matplotlib.axes import Axes
from matplotlib.category import StrCategoryFormatter
from matplotlib.collections import (
    Collection,
    LineCollection,
    PathCollection,
    QuadMesh,
)
from matplotlib.contour import QuadContourSet
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Ellipse, Patch, Polygon, Rectangle, Wedge
from matplotlib.text import Text
from matplotlib.ticker import FixedFormatter

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


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
        _copy_text(text, src_ax, dst_ax)

    if src_ax.legend_ is not None:
        _copy_legend(src_ax, dst_ax)

    # Copied last so image artists (e.g. imshow) cannot override the
    # source aspect ratio.
    dst_ax.set_aspect(src_ax.get_aspect())


def _copy_axes_props(src_ax: Axes, dst_ax: Axes) -> None:
    """Copy axes-level properties (scale, labels, spines, ticks, limits).

    Limits are applied *after* ticks because ``set_xticks``/``set_yticks``
    otherwise expand the view to include every tick position.
    """

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

    _copy_ticks(src_ax, dst_ax, "x")
    _copy_ticks(src_ax, dst_ax, "y")

    dst_ax.set_xlim(src_ax.get_xlim())
    dst_ax.set_ylim(src_ax.get_ylim())


def _copy_ticks(src_ax: Axes, dst_ax: Axes, axis: str) -> None:
    """Copy major tick positions, plus labels for fixed/categorical axes."""

    src_axis = src_ax.xaxis if axis == "x" else src_ax.yaxis
    getter = src_ax.get_xticks if axis == "x" else src_ax.get_yticks
    setter = dst_ax.set_xticks if axis == "x" else dst_ax.set_yticks

    ticks = getter()
    formatter = src_axis.get_major_formatter()
    if isinstance(formatter, (FixedFormatter, StrCategoryFormatter)):
        try:
            labels = formatter.format_ticks(ticks)
        except Exception:
            setter(ticks)
        else:
            setter(ticks, labels=labels)
    else:
        setter(ticks)


def _copy_line(line: Line2D, dst_ax: Axes) -> None:
    """Re-create a Line2D on *dst_ax*."""

    xdata = np.asarray(line.get_xdata())
    ydata = np.asarray(line.get_ydata())
    new_lines = dst_ax.plot(xdata, ydata)
    new_line = new_lines[0]

    new_line.set_color(line.get_color())
    new_line.set_linewidth(line.get_linewidth())
    new_line.set_linestyle(line.get_linestyle())
    new_line.set_drawstyle(line.get_drawstyle())
    new_line.set_marker(line.get_marker())
    new_line.set_markersize(line.get_markersize())
    new_line.set_markeredgecolor(line.get_markeredgecolor())
    new_line.set_markerfacecolor(line.get_markerfacecolor())
    new_line.set_alpha(line.get_alpha())
    new_line.set_label(line.get_label())
    new_line.set_zorder(line.get_zorder())
    new_line.set_visible(line.get_visible())


def _copy_collection(collection: Collection, dst_ax: Axes) -> None:
    """Re-create a Collection on *dst_ax*, dispatching by collection kind.

    Scatter-like collections are rebuilt through ``Axes.scatter``;
    line collections, quad meshes, and poly collections are rebuilt
    directly.  Unsupported kinds are skipped with a warning instead of
    raising.
    """

    if isinstance(collection, QuadContourSet):
        warnings.warn(
            f"fp.compose: skipping unsupported collection "
            f"{type(collection).__name__!r} (contour plots); draw the "
            "contour inside a @fp.panel function instead",
            UserWarning,
            stacklevel=2,
        )
        return

    if isinstance(collection, QuadMesh):
        _copy_quadmesh(collection, dst_ax)
        return

    if isinstance(collection, LineCollection):
        segments = collection.get_segments()
        if segments:
            new = LineCollection(
                segments,
                colors=collection.get_colors(),
                linewidths=collection.get_linewidths(),
                linestyles=collection.get_linestyle(),
                alpha=collection.get_alpha(),
                zorder=collection.get_zorder(),
            )
            _carry_label(collection, new)
            dst_ax.add_collection(new)
        return

    offsets = collection.get_offsets()
    if isinstance(collection, PathCollection) and len(offsets) > 0:
        _copy_scatter(collection, offsets, dst_ax)
        return

    get_paths = getattr(collection, "get_paths", None)
    if get_paths is not None and get_paths():
        _copy_poly_collection(collection, get_paths(), dst_ax)
        return

    warnings.warn(
        f"fp.compose: skipping unsupported collection "
        f"{type(collection).__name__!r}",
        UserWarning,
        stacklevel=2,
    )


def _carry_label(src: Collection, dst: Collection) -> None:
    """Copy the legend label unless it is the placeholder."""

    label = src.get_label()
    if label and label != "_nolegend_":
        dst.set_label(label)


def _copy_scatter(
    collection: PathCollection,
    offsets: "ArrayLike",
    dst_ax: Axes,
) -> None:
    """Re-create a scatter plot on *dst_ax* preserving sizes and colors."""

    offsets = np.asarray(offsets)
    x, y = offsets[:, 0], offsets[:, 1]

    sizes = collection.get_sizes()
    edgecolors = collection.get_edgecolor()
    facecolors = collection.get_facecolor()
    alpha = collection.get_alpha()

    kwargs: dict[str, object] = {}
    if alpha is not None:
        kwargs["alpha"] = alpha

    # Marker round-trip: a scatter PathCollection holds exactly one
    # (marker) path.
    paths = collection.get_paths()
    if len(paths) == 1:
        kwargs["marker"] = paths[0]

    # Value-mapped colours: rebuild the mapping instead of the
    # (draw-time) resolved facecolors.
    array = collection.get_array()
    if array is not None and np.asarray(array).size == len(offsets):
        vmin, vmax = collection.get_clim()
        dst_ax.scatter(
            x,
            y,
            c=np.asarray(array),
            s=sizes,
            cmap=collection.get_cmap(),
            vmin=vmin,
            vmax=vmax,
            edgecolors=edgecolors[0] if len(edgecolors) == 1 else edgecolors,
            linewidths=collection.get_linewidths()[0],
            **kwargs,
        )
    elif len(facecolors) > 1:
        dst_ax.scatter(x, y, c=facecolors, s=sizes, edgecolors=edgecolors, **kwargs)
    else:
        dst_ax.scatter(x, y, color=facecolors[0], s=sizes, edgecolors=edgecolors, **kwargs)

    if collection.get_label() and collection.get_label() != "_nolegend_":
        dst_ax.collections[-1].set_label(collection.get_label())


def _copy_poly_collection(
    collection: Collection,
    paths: list,
    dst_ax: Axes,
) -> None:
    """Re-create a path-based collection (fill_between, stackplot, hexbin).

    Uses :class:`~matplotlib.collections.PathCollection` so existing
    (possibly compound) paths round-trip unchanged.  Offset-driven
    collections (hexbin) keep their offsets and offset transform.
    """

    new = PathCollection(
        paths,
        facecolors=collection.get_facecolor(),
        edgecolors=collection.get_edgecolor(),
        linewidths=collection.get_linewidths(),
        alpha=collection.get_alpha(),
        zorder=collection.get_zorder(),
        transform=dst_ax.transData,
    )

    offsets = collection.get_offsets()
    if len(offsets) > 1:
        new.set_offsets(offsets)
        new.set_offset_transform(dst_ax.transData)
        get_sizes = getattr(collection, "get_sizes", None)
        if get_sizes is not None:
            sizes = get_sizes()
            if len(sizes) == len(offsets):
                new.set_sizes(sizes)

    # Value-mapped collections (e.g. hexbin) carry their colour mapping.
    array = collection.get_array()
    if array is not None and np.asarray(array).size > 0:
        new.set_array(np.asarray(array))
        new.set_cmap(collection.get_cmap())
        new.set_clim(*collection.get_clim())

    _carry_label(collection, new)
    dst_ax.add_collection(new)


def _copy_quadmesh(mesh: QuadMesh, dst_ax: Axes) -> None:
    """Re-create a QuadMesh (pcolormesh) on *dst_ax*."""

    coords = mesh.get_coordinates()
    array = np.ma.asarray(mesh.get_array())
    m, n = coords.shape[0] - 1, coords.shape[1] - 1
    if array.ndim == 1:
        array = array.reshape(m, n)
    dst_ax.pcolormesh(
        coords[..., 0],
        coords[..., 1],
        array,
        cmap=mesh.get_cmap(),
        norm=mesh.norm,
        shading="flat",
    )


def _patch_style_kwargs(patch: Patch) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "facecolor": patch.get_facecolor(),
        "edgecolor": patch.get_edgecolor(),
        "linewidth": patch.get_linewidth(),
        "alpha": patch.get_alpha(),
        "zorder": patch.get_zorder(),
    }
    return kwargs


def _copy_patch(patch: Patch, dst_ax: Axes) -> None:
    """Re-create a Patch on *dst_ax*, dispatching by patch kind."""

    style = _patch_style_kwargs(patch)

    if isinstance(patch, Rectangle):
        new: Patch = Rectangle(
            (patch.get_x(), patch.get_y()),
            patch.get_width(),
            patch.get_height(),
            **style,
        )
    elif isinstance(patch, Circle):
        new = Circle(patch.center, patch.radius, **style)
    elif isinstance(patch, Ellipse):
        new = Ellipse(
            patch.center,
            patch.width,
            patch.height,
            angle=patch.angle,
            **style,
        )
    elif isinstance(patch, Wedge):
        new = Wedge(
            patch.center,
            patch.r,
            patch.theta1,
            patch.theta2,
            **style,
        )
    elif isinstance(patch, Polygon):
        new = Polygon(patch.get_xy(), **style)
    else:
        # Generic fallback (FancyBboxPatch, ArrowPatch, ...): shallow
        # copy, re-targeted to the destination axes.
        new = _copy.copy(patch)
        new.set_transform(dst_ax.transData)

    if patch.get_label() and patch.get_label() != "_nolegend_":
        new.set_label(patch.get_label())
    dst_ax.add_patch(new)


def _copy_image(image: AxesImage, dst_ax: Axes) -> None:
    """Re-create an AxesImage (imshow) on *dst_ax*.

    The aspect ratio is handled at the axes level (see
    :func:`copy_axes_content`).
    """

    kwargs: dict[str, object] = {
        "cmap": image.get_cmap(),
        "vmin": image.get_clim()[0],
        "vmax": image.get_clim()[1],
        "extent": image.get_extent(),
        "interpolation": image.get_interpolation(),
        "origin": getattr(image, "origin", None),
    }

    dst_ax.imshow(image.get_array(), **kwargs)


def _copy_text(text: Text, src_ax: Axes, dst_ax: Axes) -> None:
    """Re-create a Text artist on *dst_ax*, preserving its coordinate space."""

    content = text.get_text()
    if not content:
        return

    pos = text.get_position()
    style: dict[str, object] = {
        "fontsize": text.get_fontsize(),
        "color": text.get_color(),
        "fontweight": text.get_fontweight(),
        "fontstyle": text.get_fontstyle(),
        "ha": text.get_horizontalalignment(),
        "va": text.get_verticalalignment(),
        "rotation": text.get_rotation(),
    }

    transform = text.get_transform()
    if transform is src_ax.transAxes:
        style["transform"] = dst_ax.transAxes
    elif transform is src_ax.figure.transFigure:
        style["transform"] = dst_ax.figure.transFigure

    dst_ax.text(pos[0], pos[1], content, **style)


def _copy_legend(src_ax: Axes, dst_ax: Axes) -> None:
    """Re-create the legend from the copied artists, preserving placement."""

    handles, labels = dst_ax.get_legend_handles_labels()
    if not labels:
        return

    src_leg = src_ax.legend_
    kwargs: dict[str, object] = {}

    loc = getattr(src_leg, "_loc", None)
    if loc is not None:
        kwargs["loc"] = loc
    title = src_leg.get_title().get_text()
    if title:
        kwargs["title"] = title
    if src_leg.get_texts():
        kwargs["fontsize"] = src_leg.get_texts()[0].get_fontsize()

    dst_ax.legend(handles, labels, **kwargs)


def _colorbar_axes(fig: Figure) -> set:
    """Axes hosting colorbars, found via their mappable linkage."""

    found = set()
    for ax in fig.axes:
        for mappable in (*ax.images, *ax.collections):
            cb = getattr(mappable, "colorbar", None)
            if cb is not None and getattr(cb, "ax", None) is not None:
                found.add(cb.ax)
    return found


def collect_panels(
    *items: Figure | Axes,
) -> list[AxesPanel]:
    """Extract AxesPanel objects from a mix of Figure and Axes inputs.

    Colorbar axes are excluded: they decorate a panel rather than form
    one of their own.
    """

    panels: list[AxesPanel] = []
    for item in items:
        if isinstance(item, Figure):
            skip = _colorbar_axes(item)
            for ax in item.axes:
                if ax in skip:
                    continue
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
