import inspect

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

import figpatch as fp
from figpatch._extract import copy_axes_content


def test_copy_line() -> None:
    fig1, ax1 = plt.subplots()
    ax1.plot([1, 2, 3], [4, 5, 6], color="red", linewidth=2, label="data")
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.set_title("Test")

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert len(ax2.lines) == 1
    assert ax2.lines[0].get_color() == "red"
    assert ax2.lines[0].get_linewidth() == pytest.approx(2)
    assert ax2.lines[0].get_label() == "data"
    assert ax2.get_xlabel() == "X"
    assert ax2.get_ylabel() == "Y"
    assert ax2.get_title() == "Test"

    plt.close(fig1)
    plt.close(fig2)


def test_copy_line_drawstyle() -> None:
    fig1, ax1 = plt.subplots()
    ax1.plot([1, 2, 3], [1, 4, 9], drawstyle="steps-pre")

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert ax2.lines[0].get_drawstyle() == "steps-pre"
    plt.close(fig1)
    plt.close(fig2)


def test_copy_scatter() -> None:
    fig1, ax1 = plt.subplots()
    ax1.scatter([1, 2, 3], [4, 5, 6], c=["red", "green", "blue"], s=[10, 20, 30])

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert len(ax2.collections) == 1
    offsets = ax2.collections[0].get_offsets()
    assert len(offsets) == 3

    plt.close(fig1)
    plt.close(fig2)


def test_copy_scatter_value_mapped_colors() -> None:
    fig1, ax1 = plt.subplots()
    sc = ax1.scatter([1, 2, 3], [4, 5, 6], c=[10, 20, 30], s=[5, 10, 15], cmap="viridis")

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    dst = ax2.collections[0]
    assert len(dst.get_offsets()) == 3
    assert dst.get_clim() == sc.get_clim()
    fig1.canvas.draw()
    fig2.canvas.draw()
    np.testing.assert_allclose(dst.get_facecolor(), sc.get_facecolor())
    plt.close(fig1)
    plt.close(fig2)


def test_copy_scatter_marker_roundtrip() -> None:
    fig1, ax1 = plt.subplots()
    ax1.scatter([1, 2], [3, 4], marker="s")

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    src_path = ax1.collections[0].get_paths()[0]
    dst_path = ax2.collections[0].get_paths()[0]
    np.testing.assert_allclose(src_path.vertices, dst_path.vertices)
    plt.close(fig1)
    plt.close(fig2)


def test_copy_bar() -> None:
    fig1, ax1 = plt.subplots()
    ax1.bar(["A", "B", "C"], [1, 2, 3])

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert len(ax2.patches) == 3

    plt.close(fig1)
    plt.close(fig2)


def test_copy_bar_categorical_ticklabels() -> None:
    fig1, ax1 = plt.subplots()
    ax1.bar(["alpha", "beta", "gamma"], [1, 2, 3])

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert [t.get_text() for t in ax2.get_xticklabels()] == ["alpha", "beta", "gamma"]
    plt.close(fig1)
    plt.close(fig2)


def test_copy_preserves_view_limits_despite_locator_ticks() -> None:
    # Regression: set_yticks must not expand the destination limits to
    # include out-of-view locator tick positions.
    fig1, ax1 = plt.subplots()
    ax1.plot([0, 10], [0, 10])
    ax1.set_ylim(-0.5, 10.5)

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert ax2.get_ylim() == (-0.5, 10.5)
    plt.close(fig1)
    plt.close(fig2)


def test_copy_bar_patch_style() -> None:
    fig1, ax1 = plt.subplots()
    ax1.bar(["A", "B"], [1, 2], color="tab:orange", edgecolor="black", linewidth=2)

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    for src, dst in zip(ax1.patches, ax2.patches, strict=True):
        assert dst.get_facecolor() == src.get_facecolor()
        assert dst.get_edgecolor() == src.get_edgecolor()
        assert dst.get_linewidth() == src.get_linewidth()
    plt.close(fig1)
    plt.close(fig2)


def test_copy_pie_wedge_patches() -> None:
    fig1, ax1 = plt.subplots()
    ax1.pie([1, 2, 3])

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert len(ax2.patches) == 3
    assert ax2.get_aspect() == ax1.get_aspect()
    plt.close(fig1)
    plt.close(fig2)


def test_copy_circle_patch() -> None:
    from matplotlib.patches import Circle

    fig1, ax1 = plt.subplots()
    ax1.add_patch(Circle((1, 2), 3, facecolor="tab:red"))

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    dst = ax2.patches[0]
    assert isinstance(dst, Circle)
    assert dst.center == (1, 2)
    assert dst.radius == 3
    plt.close(fig1)
    plt.close(fig2)


def test_copy_polygon_patch() -> None:
    from matplotlib.patches import Polygon

    fig1, ax1 = plt.subplots()
    ax1.add_patch(Polygon([(0, 0), (1, 0), (0.5, 1)], facecolor="tab:blue"))

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert isinstance(ax2.patches[0], Polygon)
    np.testing.assert_allclose(ax2.patches[0].get_xy(), ax1.patches[0].get_xy())
    plt.close(fig1)
    plt.close(fig2)


def test_copy_image() -> None:
    fig1, ax1 = plt.subplots()
    data = np.random.rand(5, 5)
    ax1.imshow(data, cmap="viridis")

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert len(ax2.images) == 1
    np.testing.assert_allclose(ax2.images[0].get_array(), data)

    plt.close(fig1)
    plt.close(fig2)


def test_copy_image_origin_lower() -> None:
    # Regression: origin was not copied, flipping images vertically.
    fig1, ax1 = plt.subplots()
    ax1.imshow(np.random.rand(4, 4), origin="lower", aspect="auto")

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert ax2.images[0].origin == "lower"
    assert ax2.get_aspect() == "auto"
    plt.close(fig1)
    plt.close(fig2)


def test_copy_axes_limits() -> None:
    fig1, ax1 = plt.subplots()
    ax1.plot([1, 2, 3], [4, 5, 6])
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 20)

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert ax2.get_xlim() == (0, 10)
    assert ax2.get_ylim() == (0, 20)

    plt.close(fig1)
    plt.close(fig2)


def test_copy_text_axes_transform() -> None:
    # Regression: transform-anchored text landed in data coordinates.
    fig1, ax1 = plt.subplots()
    ax1.plot([0, 10], [0, 10])
    ax1.text(0.5, 0.5, "note", transform=ax1.transAxes)

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert ax2.texts[0].get_transform() is ax2.transAxes
    plt.close(fig1)
    plt.close(fig2)


def test_copy_text_data_transform_unchanged() -> None:
    fig1, ax1 = plt.subplots()
    ax1.plot([0, 10], [0, 10])
    ax1.text(2, 5, "point")

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert ax2.texts[0].get_transform() is ax2.transData
    assert ax2.texts[0].get_position() == (2, 5)
    plt.close(fig1)
    plt.close(fig2)


def test_copy_legend() -> None:
    fig1, ax1 = plt.subplots()
    ax1.plot([1, 2], [3, 4], label="series")
    ax1.legend()

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert ax2.legend_ is not None
    texts = ax2.legend_.get_texts()
    assert len(texts) == 1
    assert texts[0].get_text() == "series"

    plt.close(fig1)
    plt.close(fig2)


def test_copy_legend_loc_and_title() -> None:
    # Regression: legend was rebuilt with default loc and no title.
    fig1, ax1 = plt.subplots()
    ax1.plot([1, 2], [3, 4], label="series")
    ax1.legend(loc="lower right", title="runs")

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert ax2.legend_._loc == ax1.legend_._loc
    assert ax2.legend_.get_title().get_text() == "runs"
    plt.close(fig1)
    plt.close(fig2)


def test_copy_fill_between() -> None:
    fig1, ax1 = plt.subplots()
    ax1.fill_between([0, 1, 2], [1, 1, 1], [2, 2, 2], color="tab:blue")

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert len(ax2.collections) == 1
    assert len(ax2.collections[0].get_paths()) == 1
    plt.close(fig1)
    plt.close(fig2)


def test_copy_stackplot() -> None:
    fig1, ax1 = plt.subplots()
    ax1.stackplot([0, 1, 2], [[1, 1, 1], [2, 2, 2]])

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert len(ax2.collections) == 2
    plt.close(fig1)
    plt.close(fig2)


def test_copy_errorbar() -> None:
    fig1, ax1 = plt.subplots()
    ax1.errorbar([1, 2], [1, 2], yerr=0.2)

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert len(ax2.lines) == 1
    assert len(ax2.collections) == 1
    n_src = len(ax1.collections[0].get_segments())
    n_dst = len(ax2.collections[0].get_segments())
    assert n_dst == n_src
    plt.close(fig1)
    plt.close(fig2)


def test_copy_pcolormesh() -> None:
    fig1, ax1 = plt.subplots()
    mesh = ax1.pcolormesh(np.random.rand(4, 5), cmap="viridis")

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    dst = ax2.collections[0]
    assert type(dst).__name__ == "QuadMesh"
    assert dst.get_clim() == mesh.get_clim()
    np.testing.assert_allclose(np.asarray(dst.get_array()), np.asarray(mesh.get_array()))
    plt.close(fig1)
    plt.close(fig2)


def test_copy_hexbin() -> None:
    fig1, ax1 = plt.subplots()
    ax1.hexbin([1, 2, 3, 4, 1.5], [1, 2, 1, 2, 1.5], gridsize=3)

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    src, dst = ax1.collections[0], ax2.collections[0]
    assert len(dst.get_offsets()) == len(src.get_offsets())
    plt.close(fig1)
    plt.close(fig2)


def test_copy_violinplot() -> None:
    fig1, ax1 = plt.subplots()
    ax1.violinplot([[1, 2], [2, 3]])

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert len(ax2.collections) == len(ax1.collections)
    assert len(ax2.lines) == len(ax1.lines)
    plt.close(fig1)
    plt.close(fig2)


def test_copy_contour_warns_and_skips() -> None:
    fig1, ax1 = plt.subplots()
    ax1.contourf(np.random.rand(5, 5))

    fig2, ax2 = plt.subplots()
    with pytest.warns(UserWarning, match="contour"):
        copy_axes_content(ax1, ax2)

    assert len(ax2.collections) == 0
    plt.close(fig1)
    plt.close(fig2)


def test_compose_skips_colorbar_axes() -> None:
    # Regression: colorbar axes were promoted to grid panels.
    src, ax = plt.subplots()
    im = ax.imshow(np.random.rand(4, 4))
    src.colorbar(im)

    out = fp.compose(src, labels=False)
    assert len(out.axes) == 1
    assert len(out.axes[0].images) == 1
    plt.close(src)
    plt.close(out)


def test_compose_two_figures() -> None:
    fig1, ax1 = plt.subplots()
    ax1.plot([1, 2, 3], [4, 5, 6])
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Signal")

    fig2, ax2 = plt.subplots()
    ax2.scatter([1, 2, 3], [6, 5, 4])
    ax2.set_xlabel("Feature")
    ax2.set_ylabel("Count")

    composed = fp.compose(fig1, fig2, direction="h", labels=True)
    assert isinstance(composed, Figure)
    assert len(composed.axes) == 2
    assert composed.axes[0].get_xlabel() == "Time"
    assert composed.axes[1].get_xlabel() == "Feature"
    assert len(composed.axes[0].lines) == 1
    assert len(composed.axes[1].collections) == 1

    plt.close(fig1)
    plt.close(fig2)
    plt.close(composed)


def test_compose_vertical() -> None:
    fig1, ax1 = plt.subplots()
    ax1.plot([1, 2], [3, 4])

    fig2, ax2 = plt.subplots()
    ax2.plot([1, 2], [5, 6])

    composed = fp.compose(fig1, fig2, direction="v", labels=False)
    assert len(composed.axes) == 2

    plt.close(fig1)
    plt.close(fig2)
    plt.close(composed)


def test_compose_rejects_invalid_type() -> None:
    with pytest.raises(TypeError, match="Figure or Axes"):
        fp.compose("not a figure")


def test_copy_axes_content_signature() -> None:
    # Guard the public extraction entry point against accidental
    # signature drift (text copying now needs the source axes).
    params = inspect.signature(copy_axes_content).parameters
    assert list(params) == ["src_ax", "dst_ax"]
