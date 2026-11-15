import pytest

from src.metrics import mae, rmse


def test_forecast_metrics() -> None:
    actual = [1, 2, 3]
    predicted = [2, 2, 2]

    assert rmse(actual, predicted) == pytest.approx((2 / 3) ** 0.5)
    assert mae(actual, predicted) == pytest.approx(2 / 3)


def test_forecast_metrics_reject_mismatched_shapes() -> None:
    with pytest.raises(ValueError, match="same shape"):
        rmse([1, 2], [1])
