"""Shared publication style for figpatch examples.

Inspired by cnsplots — minimalist, Helvetica-first, despined axes,
compact ticks, frameless legends, high-DPI transparent export.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

import matplotlib as mpl

if TYPE_CHECKING:
    from collections.abc import Iterator


_RC_PARAMS: dict[str, object] = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Helvetica Neue", "Arial", "Nimbus Sans", "Liberation Sans", "DejaVu Sans"],
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.titleweight": "bold",
    "axes.titlepad": 4,
    "axes.labelsize": 8,
    "axes.labelpad": 2,
    "axes.labelcolor": "black",
    "axes.linewidth": 0.5,
    "axes.edgecolor": "black",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "axes.xmargin": 0.05,
    "axes.ymargin": 0.05,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "xtick.color": "black",
    "ytick.color": "black",
    "xtick.major.size": 2,
    "ytick.major.size": 2,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.pad": 1,
    "ytick.major.pad": 1,
    "xtick.alignment": "center",
    "ytick.alignment": "center_baseline",
    "legend.fontsize": 7,
    "legend.frameon": False,
    "legend.markerscale": 0.5,
    "legend.handlelength": 0.7,
    "legend.handleheight": 0.7,
    "legend.handletextpad": 0.3,
    "lines.linewidth": 1.0,
    "lines.markersize": 3,
    "savefig.dpi": 288,
    "savefig.transparent": True,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.01,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
}

# Nature-inspired qualitative palette (ggsci NPG)
PALETTE = [
    "#E64B35",  # red
    "#4DBBD5",  # cyan
    "#00A087",  # teal
    "#3C5488",  # blue
    "#F39B7F",  # salmon
    "#8491B4",  # slate
    "#91D1C2",  # mint
    "#DC0000",  # crimson
    "#7E6148",  # brown
    "#B09C85",  # tan
]

# Named single colors from the palette
RED = PALETTE[0]
CYAN = PALETTE[1]
TEAL = PALETTE[2]
BLUE = PALETTE[3]
SALMON = PALETTE[4]
SLATE = PALETTE[5]
MINT = PALETTE[6]
CRIMSON = PALETTE[7]
BROWN = PALETTE[8]
TAN = PALETTE[9]

# Grayscale
GRAY = "#999999"
LIGHT_GRAY = "#CCCCCC"
DARK_GRAY = "#333333"


@contextmanager
def style() -> "Iterator[None]":
    """Temporarily apply publication styling while constructing figures."""
    with mpl.rc_context(_RC_PARAMS):
        yield


def setup_ax(ax) -> None:
    """Apply per-axes styling: despine, compact ticks, no grid."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)
        spine.set_color("black")
    ax.grid(False)
    ax.tick_params(
        axis="both",
        which="major",
        labelsize=7,
        width=0.6,
        length=2,
        pad=1,
    )
    ax.xaxis.label.set_fontsize(8)
    ax.yaxis.label.set_fontsize(8)
    ax.title.set_fontsize(8)
    ax.title.set_fontweight("bold")
    if ax.legend_ is not None:
        ax.legend_.set_frame_on(False)
        for text in ax.legend_.get_texts():
            text.set_fontsize(7)
