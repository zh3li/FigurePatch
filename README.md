# figpatch

**Compose multi-panel Matplotlib figures with `|` and `/` operators.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB)](https://www.python.org/)
[![Matplotlib](https://img.shields.io/badge/built%20for-Matplotlib-11557C)](https://matplotlib.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-2EA44F)](LICENSE)
[![Status: alpha](https://img.shields.io/badge/status-alpha-EF8B2C)](#project-status)

figpatch brings R's [patchwork](https://github.com/thomasp85/patchwork) composition
syntax to Matplotlib. Wrap your plotting code in panels, then compose them with
operators. No gridspec, no `subplot_mosaic`, no manual positioning.

It is **not** a plotting API. Your Matplotlib, Seaborn, pandas, or domain library
continues to create the plots. figpatch handles the layout.

## Quick start

```bash
pip install figpatch
```

```python
import matplotlib.pyplot as plt
import figpatch as fp

@fp.panel
def panel_a(ax):
    ax.plot([1, 2, 3], [2, 4, 3])
    ax.set_xlabel("Time")

@fp.panel
def panel_b(ax):
    ax.scatter([1, 2, 3], [3, 1, 2])
    ax.set_xlabel("Feature")

fig = (panel_a | panel_b).render()
fig.savefig("figure.pdf")
```

## Why figpatch?

### Before: gridspec hell

```python
fig = plt.figure(figsize=(10, 8))
gs = fig.add_gridspec(2, 2)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, :])  # spans full width

ax1.plot(x, y1)
ax1.set_xlabel("Time")
ax2.scatter(x, y2)
ax2.set_xlabel("Feature A")
ax3.bar(x, y3)
ax3.set_xlabel("Group")

fig.tight_layout()
fig.savefig("figure.pdf")
```

### After: figpatch

```python
@fp.panel
def panel_a(ax):
    ax.plot(x, y1)
    ax.set_xlabel("Time")

@fp.panel
def panel_b(ax):
    ax.scatter(x, y2)
    ax.set_xlabel("Feature A")

@fp.panel
def panel_c(ax):
    ax.bar(x, y3)
    ax.set_xlabel("Group")

fig = ((panel_a | panel_b) / panel_c).render()
fig.savefig("figure.pdf")
```

The complex layout `(A | B) / C` where C spans the full width is handled
automatically — no manual `gridspec` or `colspan` needed.

## Features

- **Operator-based composition** — `|` for side-by-side, `/` for stacked
- **Nested layouts** — `(a | b) / c` where c spans full width, `a | (b / c)`
  where a spans full height
- **Function-based panels** — `@fp.panel` decorator wraps any plotting code
- **Figure-based composition** — `fp.compose(fig1, fig2)` for existing figures
- **Panel labels** — automatic A, B, C... labels (or custom prefixes like S1, S2)
- **Any Matplotlib-based library** — Seaborn, pandas, plotnine, etc.
- **Zero styling opinions** — bring your own style (SciencePlots, seaborn, etc.)
- **Minimal** — Matplotlib is the only runtime dependency

## API

### `@fp.panel`

Decorator that wraps a plotting function into a `Panel`:

```python
@fp.panel
def my_panel(ax):
    ax.plot(x, y)
    ax.set_xlabel("Time")
```

### Operators: `|` and `/`

```python
panel_a | panel_b      # side-by-side (horizontal)
panel_a / panel_b      # stacked (vertical)
(panel_a | panel_b) / panel_c   # A and B on top, C spans full width below
panel_a | (panel_b / panel_c)   # A on left spanning full height, B and C on right
```

### `.render()`

```python
fig = (panel_a | panel_b).render(
    figsize=(10, 4),     # auto-calculated if omitted
    labels=True,         # A, B, C... (default), "S" for S1/S2, False to disable
    gap=0.04,            # spacing between panels (figure-relative units)
)
```

### `fp.compose()`

Compose existing figures or axes without rewriting code:

```python
fig1, ax1 = plt.subplots()
ax1.plot(x, y)

fig2, ax2 = plt.subplots()
ax2.scatter(x, y)

fig = fp.compose(fig1, fig2, direction="h", labels=True)
fig.savefig("composed.pdf")
```

Supports `Figure` and `Axes` objects. Artist extraction handles lines, scatter
collections, bar patches, images, text, and legends.

## Compatibility

figpatch operates on `matplotlib.axes.Axes`, so it works at the end of any
Matplotlib-backed pipeline.

| Producer | Status |
| --- | --- |
| Matplotlib | Tested |
| Seaborn (axis-level) | Works — pass `ax` to `sns.lineplot`, `sns.scatterplot`, etc. |
| pandas plotting | Works — pass `ax` to `df.plot()` |
| Seaborn (figure-level) | Use `fp.compose()` on the returned figure |

## Examples

```bash
git clone https://github.com/l1zhe/figpatch.git
cd figpatch
uv sync

# Basic two-panel composition
uv run python examples/basic_compose.py

# Complex nested layout: (A | B) / C
uv run python examples/complex_layout.py

# Compose existing figures
uv run python examples/figure_compose.py
```

## Project status

figpatch `0.1.0` is a tested alpha. The API may change while it is exercised
against real scientific figures.

Roadmap:

- Custom width/height ratios (`plot_layout(widths=[2, 1])`)
- Shared axes across panels
- Complex artist types (contour, pcolormesh, 3D)
- Colorbar handling
- CLI

## Development

```bash
uv sync
uv run pytest
uv build
```

## Citation

If figpatch helps your research, please cite it:

```bibtex
@software{figpatch,
  author = {Zhe Li},
  title  = {figpatch: Compose multi-panel Matplotlib figures with | and / operators},
  year   = {2026},
  url    = {https://github.com/l1zhe/figpatch}
}
```

## License

figpatch is available under the [MIT License](LICENSE).
