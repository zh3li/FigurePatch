"""Shared test configuration: force the non-interactive Agg backend."""

import matplotlib

matplotlib.use("Agg")
