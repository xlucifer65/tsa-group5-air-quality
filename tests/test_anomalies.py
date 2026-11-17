import numpy as np
import pandas as pd
import pytest

from src.anomalies import (
    combine_flags,
    impute_anomalies,
    isolation_forest_anomalies,
    overlap_table,
    rolling_zscore,
)


@pytest.fixture
def series() -> pd.Series:
    rng = np.random.default_rng(0)
    index = pd.date_range("2024-01-01", periods=200, freq="D")
    values = 10 + 2 * np.sin(np.arange(200) * 2 * np.pi / 7) + rng.normal(0, 0.5, 200)
    values[100] = 40.0
    return pd.Series(values, index=index)


def test_rolling_zscore_flags_spike(series: pd.Series) -> None:
    flags = rolling_zscore(series, window=30, threshold=3.0)

    assert flags.loc[series.index[100], "is_anomaly"]
    assert flags["is_anomaly"].sum() <= 3


def test_isolation_forest_flags_spike(series: pd.Series) -> None:
    flags = isolation_forest_anomalies(series, contamination=0.03)

    assert flags.loc[series.index[100], "is_anomaly"]


def test_overlap_table_counts_shared_flags() -> None:
    index = pd.date_range("2024-01-01", periods=4, freq="D")
    flags = combine_flags(
        {
            "a": pd.Series([True, True, False], index=index[:3]),
            "b": pd.Series([True, False, True], index=index[:3]),
        },
        index,
    )

    assert flags["n_methods"].tolist() == [2, 1, 1, 0]
    matrix = overlap_table(flags)
    assert matrix.loc["a", "b"] == 1
    assert matrix.loc["a", "a"] == 2


@pytest.mark.parametrize("method", ["linear", "stl"])
def test_impute_anomalies_replaces_only_flagged_points(series: pd.Series, method: str) -> None:
    mask = pd.Series(False, index=series.index)
    mask.iloc[100] = True

    cleaned = impute_anomalies(series, mask, method=method)

    assert cleaned.iloc[100] < 20
    assert cleaned.drop(series.index[100]).equals(series.drop(series.index[100]))


def test_impute_anomalies_rejects_unknown_method(series: pd.Series) -> None:
    with pytest.raises(ValueError, match="method"):
        impute_anomalies(series, pd.Series(False, index=series.index), method="mean")
