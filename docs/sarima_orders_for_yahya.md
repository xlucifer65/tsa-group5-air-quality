# Suggested SARIMA orders for Yahya (from Prem — Phase 1 / 2)

**Dataset:** Paris PM2.5 daily means (`data/processed/pm25_paris_daily.csv`)  
**Seasonal period:** 7 (weekly)

## Starter orders

| Piece | Suggestion | Why |
|---|---|---|
| `(p, d, q)` | `(1, 0, 1)` or `(1, 1, 1)` | PACF cuts off near lag 1 → AR(1); ACF decays with a short MA term. Use `d=1` only if ADF on raw fails at 5%. |
| `(P, D, Q, s)` | `(1, 1, 1, 7)` | Clear weekly seasonality in ACF at lags 7 / 14; seasonal differencing stabilizes the weekly pattern. |

**Confirmed from Prem’s ADF run:** raw series is stationary at 5% (`pvalue ≈ 2.7e-4`), so start with:

`SARIMA(1, 0, 1)(1, 1, 1, 7)`

## Notes for grid / auto_arima

- Keep `m=7`, `seasonal=True`.
- Search small box: `p,q ∈ {0,1,2}`, `P,Q ∈ {0,1}`, `d ∈ {0,1}`, `D ∈ {0,1}`.
- Prefer AIC/BIC on the **train** split from `src.load_data.get_train_test`.
- STL residuals (robust) show leftover spikes — expect Prophet holidays / anomaly cleaning to help later.

## Handoff

Prem → Yahya: start Phase 3 with the orders above; refine with residual ACF after the first fit.
