"""Shared ARIMA and Prophet forecasting helpers (same settings as notebook 03)."""

from __future__ import annotations

import logging
import warnings

import numpy as np
import pandas as pd
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX

from src.metrics import mae, rmse

ARIMA_ORDERS = {"ARIMA(2,0,2)": (2, 0, 2), "ARIMA(3,0,0)": (3, 0, 0)}


def fit_arima(train: pd.Series, order: tuple[int, int, int]):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return SARIMAX(train, order=order, trend="c").fit(disp=False, maxiter=200)


def prophet_forecast(train: pd.Series, future_index: pd.Index, **kwargs) -> pd.DataFrame:
    """Prophet with weekly + yearly seasonality and French holidays."""
    logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
    logging.getLogger("prophet").setLevel(logging.WARNING)
    params = {
        "seasonality_mode": "additive",
        "weekly_seasonality": True,
        "yearly_seasonality": True,
        "daily_seasonality": False,
    }
    params.update(kwargs)
    model = Prophet(**params)
    model.add_country_holidays(country_name="FR")
    model.fit(train.rename_axis("ds").reset_index(name="y"))
    return model.predict(pd.DataFrame({"ds": future_index}))


def evaluate_models(train: pd.Series, test: pd.Series) -> pd.DataFrame:
    """Fit the final ARIMA and Prophet models on `train` and score them on `test`."""
    rows = []
    for name, order in ARIMA_ORDERS.items():
        fit = fit_arima(train, order)
        pred = fit.get_forecast(steps=len(test)).predicted_mean.values
        rows.append(
            {
                "model": name,
                "RMSE": rmse(test, pred),
                "MAE": mae(test, pred),
                "AIC": fit.aic,
                "BIC": fit.bic,
            }
        )
    for name, kwargs in {
        "Prophet (additive)": {},
        "Prophet (regularized)": {"yearly_seasonality": 4, "holidays_prior_scale": 1.0},
    }.items():
        pred = prophet_forecast(train, test.index, **kwargs)["yhat"].values
        rows.append(
            {"model": name, "RMSE": rmse(test, pred), "MAE": mae(test, pred), "AIC": np.nan, "BIC": np.nan}
        )
    return pd.DataFrame(rows).set_index("model")
