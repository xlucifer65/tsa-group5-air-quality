"""Anomaly detection methods and cleaning helpers for the daily PM2.5 series."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.statespace.sarimax import SARIMAX


def rolling_zscore(residuals: pd.Series, window: int = 30, threshold: float = 3.0) -> pd.DataFrame:
    """Centered rolling Z-score of a residual series; flags |z| above the threshold."""
    resid = residuals.dropna()
    min_periods = max(3, window // 2)
    mean = resid.rolling(window, center=True, min_periods=min_periods).mean()
    std = resid.rolling(window, center=True, min_periods=min_periods).std()
    z = (resid - mean) / std.replace(0, np.nan)
    return pd.DataFrame({"zscore": z, "is_anomaly": z.abs() > threshold})


def stl_residual_anomalies(
    series: pd.Series, period: int = 7, window: int = 30, threshold: float = 3.0
) -> tuple[pd.DataFrame, STL]:
    """Rolling Z-score on the residuals of a robust STL decomposition."""
    fit = STL(series.dropna(), period=period, robust=True).fit()
    return rolling_zscore(fit.resid, window=window, threshold=threshold), fit


def sarima_residual_anomalies(
    train: pd.Series,
    series: pd.Series,
    order: tuple[int, int, int] = (2, 0, 2),
    threshold: float = 3.0,
) -> pd.DataFrame:
    """Flag points whose one-step SARIMAX residual exceeds `threshold` training sigmas.

    The model is fitted on `train` only and then applied to `series`, so the
    residual scale is not inflated by the anomalies being searched for.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = SARIMAX(train, order=order, trend="c").fit(disp=False, maxiter=200)
        applied = fit.apply(series)
    resid = applied.resid.iloc[order[0] + order[2] + 7 :]
    sigma = fit.resid.iloc[7:].std()
    z = resid / sigma
    return pd.DataFrame({"zscore": z, "is_anomaly": z.abs() > threshold})


def lag_features(series: pd.Series) -> pd.DataFrame:
    """Lag and rolling features used by the Isolation Forest."""
    features = pd.DataFrame(
        {
            "value": series,
            "lag1": series.shift(1),
            "lag7": series.shift(7),
            "diff1": series.diff(),
            "roll7_mean": series.rolling(7).mean(),
            "roll7_std": series.rolling(7).std(),
            "dev_roll30": series - series.rolling(30, min_periods=7).median(),
        }
    )
    return features.dropna()


def isolation_forest_anomalies(
    series: pd.Series, contamination: float = 0.03, random_state: int = 42
) -> pd.DataFrame:
    """Isolation Forest on lag and rolling features (lower score = more anomalous)."""
    features = lag_features(series)
    model = IsolationForest(
        n_estimators=300, contamination=contamination, random_state=random_state
    ).fit(features)
    return pd.DataFrame(
        {
            "score": pd.Series(model.score_samples(features), index=features.index),
            "is_anomaly": pd.Series(model.predict(features) == -1, index=features.index),
        }
    )


def combine_flags(flags: dict[str, pd.Series], index: pd.Index) -> pd.DataFrame:
    """Boolean matrix (one column per method) plus the number of agreeing methods."""
    table = pd.DataFrame({name: f.reindex(index, fill_value=False) for name, f in flags.items()})
    table = table.astype(bool)
    table["n_methods"] = table.sum(axis=1)
    return table


def overlap_table(flags: pd.DataFrame) -> pd.DataFrame:
    """Pairwise overlap (count of shared anomalies) between methods; diagonal = totals."""
    methods = [c for c in flags.columns if c != "n_methods"]
    matrix = pd.DataFrame(
        [[int((flags[a] & flags[b]).sum()) for b in methods] for a in methods],
        index=methods,
        columns=methods,
    )
    return matrix


def impute_anomalies(
    series: pd.Series, mask: pd.Series, method: str = "stl", period: int = 7
) -> pd.Series:
    """Replace flagged points by linear interpolation or by the STL trend + seasonal fit."""
    mask = mask.reindex(series.index, fill_value=False).astype(bool)
    if method == "linear":
        cleaned = series.copy()
        cleaned[mask] = np.nan
        return cleaned.interpolate(limit_direction="both")
    if method != "stl":
        raise ValueError("method must be 'linear' or 'stl'.")
    # Fit the STL on a first interpolated copy so the anomalies do not leak into the fit
    first_pass = series.copy()
    first_pass[mask] = np.nan
    first_pass = first_pass.interpolate(limit_direction="both")
    fit = STL(first_pass, period=period, robust=True).fit()
    cleaned = series.copy()
    cleaned[mask] = (fit.trend + fit.seasonal)[mask]
    return cleaned.clip(lower=0)
