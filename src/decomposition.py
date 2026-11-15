from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from statsmodels.tsa.seasonal import STL, DecomposeResult, seasonal_decompose


@dataclass(frozen=True)
class DecompositionBundle:
    additive: DecomposeResult
    multiplicative: DecomposeResult
    stl: DecomposeResult


def classical_decompose(
    series: pd.Series, period: int = 7, model: str = "additive"
) -> DecomposeResult:
    clean = series.dropna()
    if model == "multiplicative" and (clean <= 0).any():
        raise ValueError("Multiplicative decomposition requires strictly positive values.")
    return seasonal_decompose(clean, model=model, period=period, extrapolate_trend="period")


def stl_decompose(
    series: pd.Series, period: int = 7, robust: bool = True
) -> DecomposeResult:
    return STL(series.dropna(), period=period, robust=robust).fit()


def run_all(series: pd.Series, period: int = 7) -> DecompositionBundle:
    return DecompositionBundle(
        additive=classical_decompose(series, period=period, model="additive"),
        multiplicative=classical_decompose(series, period=period, model="multiplicative"),
        stl=stl_decompose(series, period=period, robust=True),
    )


def residual_summary(result: DecomposeResult, name: str) -> dict[str, float | str]:
    resid = pd.Series(result.resid).dropna()
    seasonal = pd.Series(result.seasonal).dropna()
    return {
        "method": name,
        "resid_std": float(resid.std()),
        "resid_mean": float(resid.mean()),
        "seasonal_amp": float(seasonal.max() - seasonal.min()),
    }
