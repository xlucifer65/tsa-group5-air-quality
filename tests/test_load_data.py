import pandas as pd
import pytest

from src.load_data import get_train_test, normalize_measurements, resample_daily


def test_normalize_measurements_handles_openaq_records() -> None:
    measurements = [
        {"date": {"utc": "2026-01-01T10:00:00Z"}, "value": 10.5},
        {"date": {"utc": "2026-01-01T11:00:00Z"}, "value": 11},
        {"date": {"utc": "invalid"}, "value": 12},
    ]

    result = normalize_measurements(measurements)

    assert len(result) == 2
    assert result["pm25"].tolist() == [10.5, 11.0]
    assert result["date"].dt.tz is not None


def test_resample_daily_calculates_daily_mean() -> None:
    measurements = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2026-01-01T10:00:00Z", "2026-01-01T11:00:00Z", "2026-01-02T10:00:00Z"]
            ),
            "pm25": [10.0, 14.0, 20.0],
        }
    )

    result = resample_daily(measurements)

    assert result["pm25"].tolist() == [12.0, 20.0]


def test_get_train_test_uses_final_ninety_days() -> None:
    index = pd.date_range("2026-01-01", periods=100, freq="D")
    series = pd.Series(range(100), index=index, dtype=float)

    train, test = get_train_test(series, test_days=90)

    assert len(train) == 10
    assert len(test) == 90
    assert train.index.max() < test.index.min()


def test_get_train_test_rejects_series_without_training_data() -> None:
    series = pd.Series(range(90), index=pd.date_range("2026-01-01", periods=90, freq="D"))

    with pytest.raises(ValueError, match="more than 90"):
        get_train_test(series)
