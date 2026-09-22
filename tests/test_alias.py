"""Test that figpatch alias matches figurepatch identically."""

import figpatch
import figurepatch


def test_alias_exports() -> None:
    assert figpatch.panel is figurepatch.panel
    assert figpatch.Panel is figurepatch.Panel
    assert figpatch.Compose is figurepatch.Compose
    assert figpatch.compose is figurepatch.compose
    assert figpatch.__version__ == figurepatch.__version__


def test_alias_runs_composition() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    @figpatch.panel
    def p1(ax):
        ax.plot([0, 1], [0, 1])

    @figurepatch.panel
    def p2(ax):
        ax.scatter([0, 1], [1, 0])

    # Interoperable composition
    fig = (p1 | p2).render(labels=True)
    assert len(fig.axes) == 2
    plt.close(fig)
