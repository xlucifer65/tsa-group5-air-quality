# SARIMA / ARIMA orders (updated on the real dataset)

**Dataset:** Paris PM2.5 daily means, 2023-01-01 to 2025-10-30 (1034 days, 20 isolated missing days filled by linear interpolation), `data/processed/pm25_paris_daily.csv`
**Split:** `src.load_data.get_train_test`, last 90 days as test (train: 2023-01-01 to 2025-08-01, 944 days)

> This file replaces an earlier version whose recommendation `SARIMA(1,0,1)(1,1,1,7)` over-differenced the series. Final orders come from the AIC/BIC search in `notebooks/03_forecasting.ipynb`.

## Final orders

| Model | Order | Selected by |
|---|---|---|
| ARIMA(2,0,2) | `(2, 0, 2)`, no seasonal part, constant included | AIC (5598.7) |
| ARIMA(3,0,0) | `(3, 0, 0)`, no seasonal part, constant included | BIC (5626.8) |

## Why these orders

- **d = 0:** the raw training series is stationary (ADF p = 0.0006, KPSS p ≥ 0.10).
- **D = 0 and no seasonal terms:** weekly seasonality is weak (lag-7 autocorrelation of about 0.21, day-of-week means differ by about 1.8 µg/m³). With `D = 1`, the ACF has a spike of about -0.54 at lag 7 and the fitted seasonal MA coefficient goes to about -1 (non-invertible): over-differencing. Weekly seasonal AR/MA terms do not improve AIC/BIC either.
- **p up to 3:** the PACF has a large spike at lag 1 and small values at lags 2-3.

## Search space (for reproducing)

`d = 0`, `p ∈ {0..3}`, `q ∈ {0..2}`, `P, Q ∈ {0, 1}`, `D = 0`, `s = 7`, with stationarity and invertibility enforced and a constant term. A first grid that also included `D = 1` without these constraints was misleading (see the notebook).

## Performance (see the notebook for details)

| Model | Test RMSE | CV mean RMSE (4 x 90-day windows) |
|---|---|---|
| ARIMA(2,0,2) | 4.19 | 7.45 |
| ARIMA(3,0,0) | 4.89 | 7.69 |
| Prophet (regularized) | 3.78 | 8.00 |
| Baseline: train mean | 5.05 | 8.24 |

ARIMA is the most consistent across windows, but no model beats the long-run-mean baseline by more than about 10% at a 90-day horizon.

## Known limitations

- Residuals still show autocorrelation at lag 28 (Ljung-Box) and are heteroscedastic and heavy-tailed (larger in winter), so prediction intervals are unreliable (they go below zero).
- A log transform and exogenous variables (weather) would be the natural next steps.