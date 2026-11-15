"""Shared plotting helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib.axes
import pandas as pd


def plot_series(
    series: pd.Series, title: str, ylabel: str = "PM2.5 (µg/m³)"
) -> matplotlib.axes.Axes:
    """Plot a time series using the project's common labels."""
    axis = series.plot(figsize=(12, 4), title=title, ylabel=ylabel, xlabel="Date")
    axis.figure.tight_layout()
    return axis


def save_figure(axis: matplotlib.axes.Axes, filename: str) -> Path:
    """Save a plot under the shared figures directory."""
    output_path = Path("reports/figures") / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    axis.figure.savefig(output_path, bbox_inches="tight")
    return output_path
