import matplotlib

matplotlib.use("Agg")
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


def test_panel_render_custom_figsize() -> None:
    @fp.panel
    def p(ax):
        ax.plot([1], [1])

    fig = p.render(figsize=(10, 5))
    assert tuple(fig.get_size_inches()) == (10, 5)
    plt.close(fig)
