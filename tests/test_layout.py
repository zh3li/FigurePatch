import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from figpatch._layout import add_labels, estimate_figsize


def test_estimate_figsize_single_panel() -> None:
    panels_areas = [(None, (0.0, 0.0, 1.0, 1.0))]
    w, h = estimate_figsize(panels_areas)
    assert w == pytest.approx(4.0)
    assert h == pytest.approx(3.0)


def test_estimate_figsize_two_horizontal() -> None:
    panels_areas = [
        (None, (0.0, 0.0, 0.5, 1.0)),
        (None, (0.5, 0.0, 0.5, 1.0)),
    ]
    w, h = estimate_figsize(panels_areas)
    assert w == pytest.approx(8.0)
    assert h == pytest.approx(3.0)


def test_estimate_figsize_two_vertical() -> None:
    panels_areas = [
        (None, (0.0, 0.0, 1.0, 0.5)),
        (None, (0.0, 0.5, 1.0, 0.5)),
    ]
    w, h = estimate_figsize(panels_areas)
    assert w == pytest.approx(4.0)
    assert h == pytest.approx(6.0)


def test_estimate_figsize_2x2_grid() -> None:
    panels_areas = [
        (None, (0.0, 0.0, 0.5, 0.5)),
        (None, (0.5, 0.0, 0.5, 0.5)),
        (None, (0.0, 0.5, 0.5, 0.5)),
        (None, (0.5, 0.5, 0.5, 0.5)),
    ]
    w, h = estimate_figsize(panels_areas)
    assert w == pytest.approx(8.0)
    assert h == pytest.approx(6.0)


def test_add_labels_letters() -> None:
    fig, axes = plt.subplots(1, 3)
    add_labels(axes, True)
    titles = [ax.get_title(loc="left") for ax in axes]
    assert titles == ["A", "B", "C"]
    plt.close(fig)


def test_add_labels_prefix() -> None:
    fig, axes = plt.subplots(1, 3)
    add_labels(axes, "S")
    titles = [ax.get_title(loc="left") for ax in axes]
    assert titles == ["S1", "S2", "S3"]
    plt.close(fig)


def test_add_labels_disabled() -> None:
    fig, axes = plt.subplots(1, 2)
    add_labels(axes, False)
    titles = [ax.get_title(loc="left") for ax in axes]
    assert titles == ["", ""]
    plt.close(fig)


def test_add_labels_more_than_26() -> None:
    fig, axes = plt.subplots(1, 28)
    add_labels(axes, True)
    assert axes[0].get_title(loc="left") == "A"
    assert axes[25].get_title(loc="left") == "Z"
    assert axes[26].get_title(loc="left") == "27"
    assert axes[27].get_title(loc="left") == "28"
    plt.close(fig)
