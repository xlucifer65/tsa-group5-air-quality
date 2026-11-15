"""Load OpenAQ Paris PM2.5 measurements as a daily time series."""

from __future__ import annotations

import argparse
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pandas as pd
import requests

API_URL_TEMPLATE = (
    "https://api.openaq.org/v3/locations/{location_id}/sensors/{sensor_id}/measurements"
)
DEFAULT_OUTPUT_PATH = Path("data/processed/pm25_paris_daily.csv")
DATE_COLUMN = "date"
VALUE_COLUMN = "pm25"


def _measurement_timestamp(measurement: dict[str, Any]) -> str | None:
    date = measurement.get("date")
    if isinstance(date, dict):
        return date.get("utc") or date.get("local")
    return measurement.get("datetime") or measurement.get("date_utc")


def normalize_measurements(measurements: Iterable[dict[str, Any]]) -> pd.DataFrame:
    """Convert OpenAQ API measurement records into timestamped PM2.5 values."""
    records = [
        {
            DATE_COLUMN: _measurement_timestamp(measurement),
            VALUE_COLUMN: measurement.get("value"),
        }
        for measurement in measurements
        if _measurement_timestamp(measurement) is not None
    ]
    frame = pd.DataFrame(records, columns=[DATE_COLUMN, VALUE_COLUMN])
    if frame.empty:
        return frame

    frame[DATE_COLUMN] = pd.to_datetime(frame[DATE_COLUMN], utc=True, errors="coerce")
    frame[VALUE_COLUMN] = pd.to_numeric(frame[VALUE_COLUMN], errors="coerce")
    return frame.dropna().sort_values(DATE_COLUMN).reset_index(drop=True)


def fetch_openaq_measurements(
    location_id: int,
    sensor_id: int,
    start: str,
    end: str,
    api_key: str | None = None,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    """Download all PM2.5 measurements for an OpenAQ location sensor."""
    key = api_key or os.getenv("OPENAQ_API_KEY")
    if not key:
        raise ValueError("OPENAQ_API_KEY must be set to download data from OpenAQ API v3.")

    client = session or requests.Session()
    url = API_URL_TEMPLATE.format(location_id=location_id, sensor_id=sensor_id)
    headers = {"X-API-Key": key}
    page = 1
    records: list[dict[str, Any]] = []

    while True:
        response = client.get(
            url,
            headers=headers,
            params={
                "date_from": start,
                "date_to": end,
                "limit": 1_000,
                "page": page,
            },
            timeout=30,
        )
        response.raise_for_status()
        batch = response.json().get("results", [])
        if not batch:
            break
        records.extend(batch)
        if len(batch) < 1_000:
            break
        page += 1

    return normalize_measurements(records)


def resample_daily(measurements: pd.DataFrame) -> pd.DataFrame:
    """Resample timestamped PM2.5 measurements to UTC daily means."""
    required_columns = {DATE_COLUMN, VALUE_COLUMN}
    missing_columns = required_columns.difference(measurements.columns)
    if missing_columns:
        raise ValueError(f"Measurements are missing required columns: {sorted(missing_columns)}")

    daily = (
        measurements.assign(**{DATE_COLUMN: pd.to_datetime(measurements[DATE_COLUMN], utc=True)})
        .set_index(DATE_COLUMN)[VALUE_COLUMN]
        .resample("D")
        .mean()
        .rename(VALUE_COLUMN)
        .reset_index()
    )
    daily[DATE_COLUMN] = daily[DATE_COLUMN].dt.tz_localize(None)
    return daily


def save_daily_series(daily: pd.DataFrame, output_path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    """Save a daily PM2.5 series in the shared project format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(output_path, index=False)
    return output_path


def load_daily_series(path: Path = DEFAULT_OUTPUT_PATH) -> pd.Series:
    """Load the shared PM2.5 daily series with a sorted daily index."""
    daily = pd.read_csv(path, parse_dates=[DATE_COLUMN])
    if set(daily.columns) != {DATE_COLUMN, VALUE_COLUMN}:
        raise ValueError(f"{path} must contain only '{DATE_COLUMN}' and '{VALUE_COLUMN}' columns.")
    return daily.set_index(DATE_COLUMN)[VALUE_COLUMN].sort_index().asfreq("D")


def get_train_test(
    series: pd.Series | None = None,
    path: Path = DEFAULT_OUTPUT_PATH,
    test_days: int = 90,
) -> tuple[pd.Series, pd.Series]:
    """Return all but the final 90 days and the final 90 days, chronologically."""
    if test_days <= 0:
        raise ValueError("test_days must be positive.")
    values = load_daily_series(path) if series is None else series.sort_index().asfreq("D")
    if len(values) <= test_days:
        raise ValueError(f"Series must contain more than {test_days} daily observations.")
    return values.iloc[:-test_days], values.iloc[-test_days:]


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and save OpenAQ Paris PM2.5 daily data.")
    parser.add_argument("--location-id", type=int, required=True)
    parser.add_argument("--sensor-id", type=int, required=True)
    parser.add_argument("--start", required=True, help="ISO-8601 UTC start timestamp.")
    parser.add_argument("--end", required=True, help="ISO-8601 UTC end timestamp.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    measurements = fetch_openaq_measurements(
        args.location_id, args.sensor_id, args.start, args.end
    )
    output = save_daily_series(resample_daily(measurements), args.output)
    print(f"Saved {len(measurements)} measurements as a daily series to {output}")


if __name__ == "__main__":
    main()
