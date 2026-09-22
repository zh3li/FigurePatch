import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

import figpatch as fp
from figpatch._compose import Compose


def _make_panel(label="p"):
    @fp.panel
    def p(ax):
        ax.plot([1, 2], [3, 4])

    p.__name__ = label
    return p


def test_compose_or_returns_compose() -> None:
    a, b = _make_panel("a"), _make_panel("b")
    tree = a | b
    result = tree | _make_panel("c")
    assert isinstance(result, Compose)
    assert result.direction == "h"


def test_compose_truediv_returns_compose() -> None:
    a, b = _make_panel("a"), _make_panel("b")
    tree = a / b
    result = tree / _make_panel("c")
    assert isinstance(result, Compose)
    assert result.direction == "v"


def test_flatten_single_panel() -> None:
    a = _make_panel("a")
    tree = Compose(a, None)
    panels_areas = tree._flatten(0, 0, 1, 1)
    assert len(panels_areas) == 1
    assert panels_areas[0][1] == (0, 0, 1, 1)


def test_flatten_horizontal() -> None:
    a, b = _make_panel("a"), _make_panel("b")
    tree = a | b
    panels_areas = tree._flatten(0, 0, 1, 1)
    assert len(panels_areas) == 2
    _, area_a = panels_areas[0]
    _, area_b = panels_areas[1]
    assert area_a[2] == pytest.approx(0.5)  # width
    assert area_b[0] == pytest.approx(0.5)  # x offset


def test_flatten_vertical() -> None:
    a, b = _make_panel("a"), _make_panel("b")
    tree = a / b
    panels_areas = tree._flatten(0, 0, 1, 1)
    assert len(panels_areas) == 2
    _, area_a = panels_areas[0]
    _, area_b = panels_areas[1]
    assert area_a[3] == pytest.approx(0.5)  # height
    assert area_b[1] == pytest.approx(0.5)  # y offset


def test_flatten_nested_ab_over_c() -> None:
    a, b, c = _make_panel("a"), _make_panel("b"), _make_panel("c")
    tree = (a | b) / c
    panels_areas = tree._flatten(0, 0, 1, 1)
    assert len(panels_areas) == 3

    _, area_a = panels_areas[0]
    _, area_b = panels_areas[1]
    _, area_c = panels_areas[2]

    # a and b in top half
    assert area_a[1] == pytest.approx(0.0)
    assert area_b[1] == pytest.approx(0.0)
    assert area_a[3] == pytest.approx(0.5)  # height = half

    # c in bottom half, spans full width
    assert area_c[1] == pytest.approx(0.5)  # y offset
    assert area_c[2] == pytest.approx(1.0)  # full width
    assert area_c[3] == pytest.approx(0.5)  # height = half


def test_flatten_nested_a_over_bc() -> None:
    a, b, c = _make_panel("a"), _make_panel("b"), _make_panel("c")
    tree = a | (b / c)
    panels_areas = tree._flatten(0, 0, 1, 1)
    assert len(panels_areas) == 3

    _, area_a = panels_areas[0]
    _, area_b = panels_areas[1]
    _, area_c = panels_areas[2]

    # a spans full height on left
    assert area_a[0] == pytest.approx(0.0)
    assert area_a[2] == pytest.approx(0.5)  # width = half
    assert area_a[3] == pytest.approx(1.0)  # full height

    # b and c on right
    assert area_b[0] == pytest.approx(0.5)
    assert area_c[0] == pytest.approx(0.5)


def test_render_creates_correct_axes_count() -> None:
    a, b, c = _make_panel("a"), _make_panel("b"), _make_panel("c")
    tree = (a | b) / c
    fig = tree.render()
    assert len(fig.axes) == 3
    plt.close(fig)


def test_render_returns_figure() -> None:
    a, b = _make_panel("a"), _make_panel("b")
    fig = (a | b).render()
    assert isinstance(fig, Figure)
    plt.close(fig)


def test_render_labels_default() -> None:
    a, b = _make_panel("a"), _make_panel("b")
    fig = (a | b).render(labels=True)
    titles = [ax.get_title(loc="left") for ax in fig.axes]
    assert titles == ["A", "B"]
    plt.close(fig)


def test_render_no_labels() -> None:
    a, b = _make_panel("a"), _make_panel("b")
    fig = (a | b).render(labels=False)
    titles = [ax.get_title(loc="left") for ax in fig.axes]
    assert titles == ["", ""]
    plt.close(fig)


def test_render_prefix_labels() -> None:
    a, b = _make_panel("a"), _make_panel("b")
    fig = (a | b).render(labels="S")
    titles = [ax.get_title(loc="left") for ax in fig.axes]
    assert titles == ["S1", "S2"]
    plt.close(fig)


def test_render_custom_figsize() -> None:
    a, b = _make_panel("a"), _make_panel("b")
    fig = (a | b).render(figsize=(12, 6))
    assert tuple(fig.get_size_inches()) == (12, 6)
    plt.close(fig)


def test_render_auto_figsize() -> None:
    a, b = _make_panel("a"), _make_panel("b")
    fig = (a | b).render()
    w, h = fig.get_size_inches()
    assert w > 0
    assert h > 0
    plt.close(fig)


def test_render_calls_panel_functions() -> None:
    @fp.panel
    def panel_a(ax):
        ax.plot([1, 2, 3], [4, 5, 6])
        ax.set_xlabel("Time")

    @fp.panel
    def panel_b(ax):
        ax.scatter([1, 2], [3, 4])
        ax.set_xlabel("Feature")

    fig = (panel_a | panel_b).render()
    assert fig.axes[0].get_xlabel() == "Time"
    assert fig.axes[1].get_xlabel() == "Feature"
    assert len(fig.axes[0].lines) == 1
    assert len(fig.axes[1].collections) == 1
    plt.close(fig)


def test_chain_three_horizontal() -> None:
    a, b, c = _make_panel("a"), _make_panel("b"), _make_panel("c")
    tree = a | b | c
    panels_areas = tree._flatten(0, 0, 1, 1)
    assert len(panels_areas) == 3
    for _, area in panels_areas:
        assert area[2] == pytest.approx(1 / 3)  # equal width
    plt.close(tree.render())


def test_chain_six_horizontal() -> None:
    panels = [_make_panel(f"p{i}") for i in range(6)]
    tree = panels[0]
    for p in panels[1:]:
        tree = tree | p
    areas = tree._flatten(0, 0, 1, 1)
    assert len(areas) == 6
    for _, area in areas:
        assert area[2] == pytest.approx(1 / 6)
    plt.close(tree.render())


def test_chain_three_vertical() -> None:
    a, b, c = _make_panel("a"), _make_panel("b"), _make_panel("c")
    tree = a / b / c
    areas = tree._flatten(0, 0, 1, 1)
    assert len(areas) == 3
    for _, area in areas:
        assert area[3] == pytest.approx(1 / 3)  # equal height
    plt.close(tree.render())


def test_flatten_2x3_grid() -> None:
    ps = [_make_panel(f"p{i}") for i in range(6)]
    tree = (ps[0] | ps[1] | ps[2]) / (ps[3] | ps[4] | ps[5])
    areas = tree._flatten(0, 0, 1, 1)
    assert len(areas) == 6
    for _, area in areas:
        assert area[2] == pytest.approx(1 / 3)  # width
        assert area[3] == pytest.approx(1 / 2)  # height
    plt.close(tree.render())


def test_flatten_3x2_grid() -> None:
    ps = [_make_panel(f"p{i}") for i in range(6)]
    tree = (ps[0] | ps[1]) / (ps[2] | ps[3]) / (ps[4] | ps[5])
    areas = tree._flatten(0, 0, 1, 1)
    assert len(areas) == 6
    for _, area in areas:
        assert area[2] == pytest.approx(1 / 2)  # width
        assert area[3] == pytest.approx(1 / 3)  # height
    plt.close(tree.render())


def test_flatten_3x3_grid() -> None:
    ps = [_make_panel(f"p{i}") for i in range(9)]
    tree = (ps[0] | ps[1] | ps[2]) / (ps[3] | ps[4] | ps[5]) / (ps[6] | ps[7] | ps[8])
    areas = tree._flatten(0, 0, 1, 1)
    assert len(areas) == 9
    for _, area in areas:
        assert area[2] == pytest.approx(1 / 3)  # width
        assert area[3] == pytest.approx(1 / 3)  # height
    plt.close(tree.render())


def test_flatten_irregular_3_2_3() -> None:
    ps = [_make_panel(f"p{i}") for i in range(8)]
    tree = (ps[0] | ps[1] | ps[2]) / (ps[3] | ps[4]) / (ps[5] | ps[6] | ps[7])
    areas = tree._flatten(0, 0, 1, 1)
    assert len(areas) == 8

    # Row 1: 3 panels, each 1/3 width
    for i in range(3):
        assert areas[i][1][2] == pytest.approx(1 / 3)
        assert areas[i][1][3] == pytest.approx(1 / 3)

    # Row 2: 2 panels, each 1/2 width
    for i in range(3, 5):
        assert areas[i][1][2] == pytest.approx(1 / 2)
        assert areas[i][1][3] == pytest.approx(1 / 3)

    # Row 3: 3 panels, each 1/3 width
    for i in range(5, 8):
        assert areas[i][1][2] == pytest.approx(1 / 3)
        assert areas[i][1][3] == pytest.approx(1 / 3)

    plt.close(tree.render())


def test_render_3x3_axes_count() -> None:
    ps = [_make_panel(f"p{i}") for i in range(9)]
    tree = (ps[0] | ps[1] | ps[2]) / (ps[3] | ps[4] | ps[5]) / (ps[6] | ps[7] | ps[8])
    fig = tree.render()
    assert len(fig.axes) == 9
    plt.close(fig)


def test_compose_figures_horizontal() -> None:
    fig1, ax1 = plt.subplots()
    ax1.plot([1, 2, 3], [4, 5, 6])
    ax1.set_xlabel("Time")

    fig2, ax2 = plt.subplots()
    ax2.scatter([1, 2], [3, 4])
    ax2.set_xlabel("Feature")

    composed = fp.compose(fig1, fig2, direction="h")
    assert isinstance(composed, Figure)
    assert len(composed.axes) == 2
    assert composed.axes[0].get_xlabel() == "Time"
    assert composed.axes[1].get_xlabel() == "Feature"

    plt.close(fig1)
    plt.close(fig2)
    plt.close(composed)
