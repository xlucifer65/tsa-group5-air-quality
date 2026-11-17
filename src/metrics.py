"""Shared forecast evaluation metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _validated_arrays(
    actual: pd.Series | np.ndarray, predicted: pd.Series | np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.asarray(predicted, dtype=float)
    if actual_values.shape != predicted_values.shape:
        raise ValueError("actual and predicted values must have the same shape.")
    if actual_values.size == 0:
        raise ValueError("actual and predicted values cannot be empty.")
    return actual_values, predicted_values


def rmse(actual: pd.Series | np.ndarray, predicted: pd.Series | np.ndarray) -> float:
    """Calculate root mean squared error."""
    actual_values, predicted_values = _validated_arrays(actual, predicted)
    return float(np.sqrt(np.mean((actual_values - predicted_values) ** 2)))


def mae(actual: pd.Series | np.ndarray, predicted: pd.Series | np.ndarray) -> float:
    """Calculate mean absolute error."""
    actual_values, predicted_values = _validated_arrays(actual, predicted)
    return float(np.mean(np.abs(actual_values - predicted_values)))
