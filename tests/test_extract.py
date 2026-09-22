import matplotlib

matplotlib.use("Agg")
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


def test_copy_bar() -> None:
    fig1, ax1 = plt.subplots()
    ax1.bar(["A", "B", "C"], [1, 2, 3])

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert len(ax2.patches) == 3

    plt.close(fig1)
    plt.close(fig2)


def test_copy_image() -> None:
    fig1, ax1 = plt.subplots()
    data = np.random.rand(5, 5)
    ax1.imshow(data, cmap="viridis")

    fig2, ax2 = plt.subplots()
    copy_axes_content(ax1, ax2)

    assert len(ax2.images) == 1

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
