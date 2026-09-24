import matplotlib.pyplot as plt
import pytest

from figpatch._layout import add_labels, estimate_figsize


def test_estimate_figsize_single_panel() -> None:
    w, h = estimate_figsize([["a"]])
    assert w == pytest.approx(4.0)
    assert h == pytest.approx(3.0)


def test_estimate_figsize_two_horizontal() -> None:
    w, h = estimate_figsize([["a", "b"]])
    assert w == pytest.approx(8.0)
    assert h == pytest.approx(3.0)


def test_estimate_figsize_two_vertical() -> None:
    w, h = estimate_figsize([["a"], ["b"]])
    assert w == pytest.approx(4.0)
    assert h == pytest.approx(6.0)


def test_estimate_figsize_2x2_grid() -> None:
    w, h = estimate_figsize([["a", "b"], ["c", "d"]])
    assert w == pytest.approx(8.0)
    assert h == pytest.approx(6.0)


def test_estimate_figsize_spanning_counts_columns_per_row() -> None:
    # Regression: a spanning key repeats within a row; the column count
    # must come from len(row), not the number of unique keys.
    mosaic = [["a", "b"], ["c", "c"]]
    w, h = estimate_figsize(mosaic)
    assert w == pytest.approx(8.0)
    assert h == pytest.approx(6.0)


def test_estimate_figsize_minimum_floor() -> None:
    w, h = estimate_figsize([["a"]], panel_w=1.0, panel_h=0.5)
    assert w == pytest.approx(4.0)
    assert h == pytest.approx(3.0)


def _get_labels(axes):
    """Extract panel label text from axes."""
    return [ax.get_title(loc="left") for ax in axes]


def test_add_labels_letters() -> None:
    fig, axes = plt.subplots(1, 3)
    add_labels(axes, True)
    assert _get_labels(axes) == ["A", "B", "C"]
    plt.close(fig)


def test_add_labels_prefix() -> None:
    fig, axes = plt.subplots(1, 3)
    add_labels(axes, "S")
    assert _get_labels(axes) == ["S1", "S2", "S3"]
    plt.close(fig)


def test_add_labels_disabled() -> None:
    fig, axes = plt.subplots(1, 2)
    add_labels(axes, False)
    assert _get_labels(axes) == ["", ""]
    plt.close(fig)


def test_add_labels_more_than_26() -> None:
    fig, axes = plt.subplots(1, 28)
    add_labels(axes, True)
    labels = _get_labels(axes)
    assert labels[0] == "A"
    assert labels[25] == "Z"
    assert labels[26] == "27"
    assert labels[27] == "28"
    plt.close(fig)
