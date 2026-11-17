from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from statsmodels.tsa.stattools import adfuller


@dataclass(frozen=True)
class MissingReport:
    expected_days: int
    observed_days: int
    missing_timestamps: int
    missing_values: int
    missing_dates: pd.DatetimeIndex


@dataclass(frozen=True)
class AdfResult:
    label: str
    adf_stat: float
    pvalue: float
    used_lag: int
    nobs: int
    is_stationary_5pct: bool


def count_missing(series: pd.Series) -> MissingReport:
    values = series.sort_index().asfreq("D")
    missing_dates = values.index[values.isna()]
    return MissingReport(
        expected_days=len(values),
        observed_days=int(values.notna().sum()),
        missing_timestamps=int(values.isna().sum()),
        missing_values=int(series.isna().sum()),
        missing_dates=missing_dates,
    )


def impute_linear(series: pd.Series) -> pd.Series:
    # Linear interp for short gaps; ffill/bfill only at edges.
    # Prefer this over forward-fill (flat segments inflate ACF lag 1).
    filled = series.sort_index().asfreq("D").interpolate(method="linear")
    return filled.ffill().bfill()


def rolling_mean_std(
    series: pd.Series, window: int = 7
) -> tuple[pd.Series, pd.Series]:
    roll = series.rolling(window=window, min_periods=1)
    return roll.mean(), roll.std()


def run_adf(series: pd.Series, label: str) -> AdfResult:
    clean = series.dropna()
    stat, pvalue, used_lag, nobs, *_ = adfuller(clean, autolag="AIC")
    return AdfResult(
        label=label,
        adf_stat=float(stat),
        pvalue=float(pvalue),
        used_lag=int(used_lag),
        nobs=int(nobs),
        is_stationary_5pct=bool(pvalue < 0.05),
    )


def adf_table(raw: pd.Series) -> pd.DataFrame:
    results = [
        run_adf(raw, "raw"),
        run_adf(raw.diff(), "diff_1"),
    ]
    return pd.DataFrame(
        [
            {
                "series": r.label,
                "adf_stat": r.adf_stat,
                "pvalue": r.pvalue,
                "used_lag": r.used_lag,
                "nobs": r.nobs,
                "stationary_5pct": r.is_stationary_5pct,
            }
            for r in results
        ]
    )


def suggest_sarima_orders(
    seasonal_period: int = 7,
    prefer_diff: bool = False,
    seasonal_diff: int = 0,
) -> dict[str, tuple[int, int, int] | tuple[int, int, int, int]]:
    """Starter orders for a SARIMA search (not final orders).

    d is 1 only if the raw series failed the ADF test. Seasonal differencing is
    off by default: when the seasonal pattern is weak, D=1 over-differences the
    series (strongly negative ACF at the seasonal lag). The final orders should
    be selected by AIC/BIC on the training set (see 03_forecasting.ipynb).
    """
    d = 1 if prefer_diff else 0
    return {
        "order": (1, d, 1),
        "seasonal_order": (1, seasonal_diff, 1, seasonal_period),
    }