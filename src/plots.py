from __future__ import annotations

from pathlib import Path

import matplotlib.axes
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import DecomposeResult


FIGURES_DIR = Path("reports/figures")


def plot_series(
    series: pd.Series, title: str, ylabel: str = "PM2.5 (µg/m³)"
) -> matplotlib.axes.Axes:
    axis = series.plot(figsize=(12, 4), title=title, ylabel=ylabel, xlabel="Date")
    axis.figure.tight_layout()
    return axis


def save_figure(axis: matplotlib.axes.Axes, filename: str) -> Path:
    output_path = FIGURES_DIR / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    axis.figure.savefig(output_path, bbox_inches="tight", dpi=120)
    return output_path


def save_current_figure(filename: str) -> Path:
    output_path = FIGURES_DIR / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.gcf().savefig(output_path, bbox_inches="tight", dpi=120)
    return output_path


def plot_rolling(
    series: pd.Series,
    roll_mean: pd.Series,
    roll_std: pd.Series,
    title: str = "Rolling mean and std",
) -> matplotlib.axes.Axes:
    _, axis = plt.subplots(figsize=(12, 4))
    axis.plot(series.index, series.values, label="PM2.5", alpha=0.5, linewidth=1)
    axis.plot(roll_mean.index, roll_mean.values, label="Rolling mean", linewidth=1.5)
    axis.plot(roll_std.index, roll_std.values, label="Rolling std", linewidth=1.2)
    axis.set_title(title)
    axis.set_ylabel("PM2.5 (µg/m³)")
    axis.set_xlabel("Date")
    axis.legend()
    axis.figure.tight_layout()
    return axis


def plot_acf_pacf(series: pd.Series, lags: int = 40) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    plot_acf(series.dropna(), lags=lags, ax=axes[0])
    plot_pacf(series.dropna(), lags=lags, ax=axes[1], method="ywm")
    axes[0].set_title("ACF")
    axes[1].set_title("PACF")
    fig.tight_layout()
    return fig


def plot_decompose(result: DecomposeResult, title: str) -> plt.Figure:
    fig = result.plot()
    fig.suptitle(title, y=1.02)
    fig.set_size_inches(10, 8)
    fig.tight_layout()
    return fig
