import inspect

import matplotlib.pyplot as plt
import pytest

import figpatch as fp
from figpatch._compose import Compose


def test_panel_decorator_returns_panel() -> None:
    @fp.panel
    def p(ax):
        ax.plot([1], [1])

    assert isinstance(p, fp.Panel)
    assert p.name == "p"


def test_panel_custom_name() -> None:
    @fp.panel
    def p(ax):
        pass

    named = fp.Panel(p._func, name="custom")
    assert named.name == "custom"


def test_panel_repr() -> None:
    @fp.panel
    def my_panel(ax):
        pass

    assert "my_panel" in repr(my_panel)


def test_panel_call_executes_function() -> None:
    called = False

    @fp.panel
    def p(ax):
        nonlocal called
        called = True
        ax.plot([1, 2], [3, 4])

    fig, ax = plt.subplots()
    p(ax)
    assert called
    assert len(ax.lines) == 1
    plt.close(fig)


def test_panel_or_returns_compose() -> None:
    @fp.panel
    def a(ax):
        pass

    @fp.panel
    def b(ax):
        pass

    result = a | b
    assert isinstance(result, Compose)
    assert result.direction == "h"
    assert result.left is a
    assert result.right is b


def test_panel_truediv_returns_compose() -> None:
    @fp.panel
    def a(ax):
        pass

    @fp.panel
    def b(ax):
        pass

    result = a / b
    assert isinstance(result, Compose)
    assert result.direction == "v"
    assert result.left is a
    assert result.right is b


def test_panel_render_creates_figure() -> None:
    @fp.panel
    def p(ax):
        ax.plot([1, 2, 3], [4, 5, 6])
        ax.set_xlabel("X")

    fig = p.render()
    assert len(fig.axes) == 1
    assert fig.axes[0].get_xlabel() == "X"
    plt.close(fig)


def test_panel_render_labels_default_false() -> None:
    @fp.panel
    def p(ax):
        ax.plot([1], [1])

    fig = p.render()  # no explicit labels kwarg
    assert fig.axes[0].get_title(loc="left") == ""
    plt.close(fig)


def test_panel_render_custom_figsize() -> None:
    @fp.panel
    def p(ax):
        ax.plot([1], [1])

    fig = p.render(figsize=(10, 5))
    assert tuple(fig.get_size_inches()) == (10, 5)
    plt.close(fig)


def test_panel_render_gap_removed() -> None:
    @fp.panel
    def p(ax):
        ax.plot([1], [1])

    assert "gap" not in inspect.signature(fp.Panel.render).parameters
    with pytest.raises(TypeError):
        p.render(gap=0.1)


def test_panel_rejects_non_panel_operand() -> None:
    @fp.panel
    def p(ax):
        pass

    with pytest.raises(TypeError, match="unsupported operand"):
        p | "other"
