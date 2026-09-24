import inspect

import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

import figpatch as fp
from figpatch._compose import Compose, tree_to_mosaic
from figpatch._layout import estimate_figsize


def _make_panel(label="p"):
    @fp.panel
    def p(ax):
        ax.plot([1, 2], [3, 4])

    p.__name__ = label
    return p


def _make_panels(n):
    return [_make_panel(f"p{i}") for i in range(n)]


def _panels_keys(tree):
    mosaic, panels, keys = tree_to_mosaic(tree)
    return mosaic, panels, keys


# ---------------------------------------------------------------- operators


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


def test_operator_precedence_python_semantics() -> None:
    # '/' binds tighter than '|': a | b / c | d  ==  ((a | (b / c)) | d)
    a, b, c, d = _make_panels(4)
    assert (a | b / c | d).render() is not None
    left = a | (b / c)
    left = left | d
    m1, _, k1 = tree_to_mosaic(a | b / c | d)
    m2, _, k2 = tree_to_mosaic(((a | (b / c)) | d))
    assert m1 == m2
    assert k1 == k2


@pytest.mark.parametrize("op", ["|", "/"])
def test_operator_rejects_non_panel(op) -> None:
    p = _make_panel("a")
    with pytest.raises(TypeError, match="unsupported operand"):
        if op == "|":
            p | 5
        else:
            p / 5


def test_direction_validated() -> None:
    a, b = _make_panels(2)
    with pytest.raises(ValueError, match="direction must be"):
        Compose(a, b, direction="diagonal")


def test_repr_roundtrip_shape() -> None:
    a, b, c = _make_panels(3)
    text = repr((a | b) / c)
    assert "|" in text and "/" in text


# ------------------------------------------------------------ mosaic matrix


def test_mosaic_single_panel() -> None:
    a = _make_panel("a")
    mosaic, panels, keys = _panels_keys(Compose(a, None))
    assert mosaic == [[keys[0]]]
    assert panels == [a]


def test_mosaic_horizontal() -> None:
    a, b = _make_panels(2)
    mosaic, panels, keys = _panels_keys(a | b)
    assert mosaic == [[keys[0], keys[1]]]
    assert panels == [a, b]


def test_mosaic_vertical() -> None:
    a, b = _make_panels(2)
    mosaic, panels, keys = _panels_keys(a / b)
    assert mosaic == [[keys[0]], [keys[1]]]


def test_mosaic_nested_ab_over_c() -> None:
    a, b, c = _make_panels(3)
    mosaic, panels, keys = _panels_keys((a | b) / c)
    # c spans both columns of the bottom row
    assert mosaic == [[keys[0], keys[1]], [keys[2], keys[2]]]
    assert panels == [a, b, c]


def test_mosaic_nested_a_over_bc() -> None:
    a, b, c = _make_panels(3)
    mosaic, panels, keys = _panels_keys(a | (b / c))
    # a spans both rows of the left column
    assert mosaic == [[keys[0], keys[1]], [keys[0], keys[2]]]


def test_mosaic_keys_unique_per_occurrence() -> None:
    p = _make_panel("p")
    mosaic, panels, keys = tree_to_mosaic(p | p)
    assert len(keys) == 2
    assert len(set(keys)) == 2
    assert mosaic == [[keys[0], keys[1]]]
    assert panels == [p, p]


def test_mosaic_chain_three_horizontal() -> None:
    a, b, c = _make_panels(3)
    mosaic, _, keys = _panels_keys(a | b | c)
    assert mosaic == [[keys[0], keys[1], keys[2]]]


def test_mosaic_chain_three_vertical() -> None:
    a, b, c = _make_panels(3)
    mosaic, _, keys = _panels_keys(a / b / c)
    assert mosaic == [[keys[0]], [keys[1]], [keys[2]]]


def test_mosaic_2x3_grid() -> None:
    ps = _make_panels(6)
    mosaic, _, keys = _panels_keys((ps[0] | ps[1] | ps[2]) / (ps[3] | ps[4] | ps[5]))
    assert len(mosaic) == 2
    assert all(len(row) == 3 for row in mosaic)
    assert len(keys) == 6


def test_mosaic_3x3_grid() -> None:
    ps = _make_panels(9)
    mosaic, _, keys = _panels_keys(
        (ps[0] | ps[1] | ps[2]) / (ps[3] | ps[4] | ps[5]) / (ps[6] | ps[7] | ps[8])
    )
    assert len(mosaic) == 3
    assert all(len(row) == 3 for row in mosaic)
    assert len(keys) == 9


def test_mosaic_irregular_3_2_3_expands_to_lcm_columns() -> None:
    ps = _make_panels(8)
    mosaic, _, keys = _panels_keys((ps[0] | ps[1] | ps[2]) / (ps[3] | ps[4]) / (ps[5] | ps[6] | ps[7]))
    # lcm(3, 2, 3) == 6 columns; middle-row panels span 3 columns each
    assert all(len(row) == 6 for row in mosaic)
    assert mosaic[1] == [keys[3]] * 3 + [keys[4]] * 3
    assert len(keys) == 8


def test_mosaic_coprime_blowup_guarded() -> None:
    ps = _make_panels(28)
    groups = [ps[0:2], ps[2:5], ps[5:10], ps[10:17], ps[17:28]]  # 2,3,5,7,11
    rows = []
    for g in groups:
        t = g[0]
        for x in g[1:]:
            t = t | x
        rows.append(t)
    tree = rows[0]
    for r in rows[1:]:
        tree = tree / r
    with pytest.raises(ValueError, match="regroup siblings"):
        tree.render()


# ----------------------------------------------------------------- rendering


def test_render_creates_correct_axes_count() -> None:
    a, b, c = _make_panels(3)
    fig = (a | b) / c
    out = fig.render()
    assert len(out.axes) == 3
    plt.close(out)


def test_render_returns_figure() -> None:
    a, b = _make_panels(2)
    out = (a | b).render()
    assert isinstance(out, Figure)
    plt.close(out)


def test_render_reused_panel_produces_distinct_axes() -> None:
    p = _make_panel("p")
    out = (p | p).render()
    assert len(out.axes) == 2
    for ax in out.axes:
        assert len(ax.lines) == 1
    plt.close(out)

    out = (p | _make_panel("q") | p).render()
    assert len(out.axes) == 3
    plt.close(out)


def test_render_spanning_axes_geometry() -> None:
    a, b, c = _make_panels(3)
    out = ((a | b) / c).render()
    out.canvas.draw()  # realise constrained-layout positions
    pos = {i: ax.get_position() for i, ax in enumerate(out.axes)}
    # top two share the top half; c spans the full bottom width
    assert pos[2].x0 == pytest.approx(pos[0].x0)
    assert pos[2].x1 == pytest.approx(pos[1].x1)
    assert pos[0].y0 > pos[2].y1
    plt.close(out)


def _get_labels(axes):
    return [ax.get_title(loc="left") for ax in axes]


def test_render_labels_default_true() -> None:
    a, b = _make_panels(2)
    out = (a | b).render()  # no explicit labels kwarg
    assert _get_labels(out.axes) == ["A", "B"]
    plt.close(out)


def test_render_no_labels() -> None:
    a, b = _make_panels(2)
    out = (a | b).render(labels=False)
    assert _get_labels(out.axes) == ["", ""]
    plt.close(out)


def test_render_prefix_labels() -> None:
    a, b = _make_panels(2)
    out = (a | b).render(labels="S")
    assert _get_labels(out.axes) == ["S1", "S2"]
    plt.close(out)


def test_render_custom_figsize() -> None:
    a, b = _make_panels(2)
    out = (a | b).render(figsize=(12, 6))
    assert tuple(out.get_size_inches()) == (12, 6)
    plt.close(out)


def test_render_auto_figsize_regular_grid() -> None:
    ps = _make_panels(6)
    out = ((ps[0] | ps[1] | ps[2]) / (ps[3] | ps[4] | ps[5])).render()
    w, h = out.get_size_inches()
    assert w == pytest.approx(12.0)  # 3 columns x 4.0
    assert h == pytest.approx(6.0)  # 2 rows x 3.0
    plt.close(out)


def test_render_auto_figsize_spanning_layout() -> None:
    # Regression: columns must be counted per row (len(row)), not by
    # unique keys — spanning panels expand the true grid width.
    ps = _make_panels(6)
    tree = ((ps[0] | ps[1]) / ps[2]) | (ps[3] / (ps[4] | ps[5]))
    mosaic, _, _ = tree_to_mosaic(tree)
    assert max(len(row) for row in mosaic) == 4
    assert estimate_figsize(mosaic) == (16.0, 6.0)
    out = tree.render()
    assert out.get_size_inches()[0] == pytest.approx(16.0)
    plt.close(out)


def test_render_calls_panel_functions() -> None:
    @fp.panel
    def panel_a(ax):
        ax.plot([1, 2, 3], [4, 5, 6])
        ax.set_xlabel("Time")

    @fp.panel
    def panel_b(ax):
        ax.scatter([1, 2], [3, 4])
        ax.set_xlabel("Feature")

    out = (panel_a | panel_b).render()
    assert out.axes[0].get_xlabel() == "Time"
    assert out.axes[1].get_xlabel() == "Feature"
    assert len(out.axes[0].lines) == 1
    assert len(out.axes[1].collections) == 1
    plt.close(out)


# -------------------------------------------------------------- API surface


def test_gap_parameter_removed() -> None:
    a, b = _make_panels(2)
    assert "gap" not in inspect.signature(Compose.render).parameters
    assert "gap" not in inspect.signature(fp.compose).parameters
    with pytest.raises(TypeError):
        (a | b).render(gap=0.1)


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
