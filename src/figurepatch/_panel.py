"""Panel class and decorator for function-based composition."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from figurepatch._compose import Compose


class Panel:
    """A single panel wrapping a plotting function.

    Created via the :func:`panel` decorator.  Compose panels with ``|``
    (side-by-side) and ``/`` (stacked)::

        @panel
        def panel_a(ax):
            ax.plot(x, y)

        @panel
        def panel_b(ax):
            ax.scatter(x, y)

        fig = (panel_a | panel_b).render()
    """

    def __init__(self, func: "Callable[[Axes], None]", name: str | None = None) -> None:
        self._func = func
        self._name = name or getattr(func, "__name__", repr(func))

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"Panel({self._name})"

    def __call__(self, ax: "Axes") -> None:
        self._func(ax)

    def __or__(self, other: "Panel | Compose") -> "Compose":
        from figurepatch._compose import Compose, _validate_operand

        return Compose(self, _validate_operand(other, "|"), direction="h")

    def __truediv__(self, other: "Panel | Compose") -> "Compose":
        from figurepatch._compose import Compose, _validate_operand

        return Compose(self, _validate_operand(other, "/"), direction="v")

    def render(
        self,
        figsize: tuple[float, float] | None = None,
        labels: bool | str = False,
    ) -> "Figure":
        """Render this single panel as a Matplotlib Figure.

        Unlike :meth:`Compose.render`, panel labels are disabled by
        default — a lone panel is usually not lettered.
        """

        import matplotlib.pyplot as plt
        from figurepatch._layout import add_labels

        fig, ax = plt.subplots(figsize=figsize or (6.0, 4.0), layout="constrained")
        self._func(ax)
        add_labels([ax], labels)
        return fig


def panel(func: "Callable[[Axes], None]") -> Panel:
    """Decorator that wraps a plotting function into a :class:`Panel`."""

    return Panel(func)
