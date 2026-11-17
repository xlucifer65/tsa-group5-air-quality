# Project Checklist

Tick an item (`[x]`) in the PR that completes it. The daily monitor reads this file.

## Phase 0: Setup | Rayyan | due 2026-11-17
- [ ] Claim OpenAQ in the Teams thread (names + dataset + link)
- [x] Create GitHub repo and skeleton
- [ ] Add Prem, Yahya, Vishal as collaborators
- [x] `src/load_data.py` producing the daily series in `data/processed/` plus a fixed train/test split
- [ ] Everyone can run the notebook from a fresh clone (All)

## Phase 1: Data exploration | Prem | due 2026-11-22
- [x] Full series, zoomed month, rolling mean/std plots
- [x] Missing values counted and imputation justified
- [x] ADF test on raw and differenced series
- [x] ACF/PACF plots with suggested orders

## Phase 2: Decomposition | Prem | due 2026-11-22
- [x] Classical seasonal_decompose (additive vs multiplicative)
- [x] STL decomposition
- [x] Written interpretation of trend, seasonality and residuals
- [x] Suggested SARIMA orders handed to Yahya

## Phase 3: Initial forecasting | Yahya | due 2026-11-25
- [x] Time-based train/test split (from src)
- [x] SARIMA fitted + residual diagnostics
- [x] Prophet with weekly/yearly seasonality + FR holidays
- [x] Metrics table: RMSE, MAE, AIC/BIC
- [x] Forecast vs actual plots with CIs

## Phase 4: Anomaly detection | Vishal | due 2026-11-27
- [x] Rolling Z-score on STL residuals
- [x] SARIMA residual anomalies (> 3 sigma)
- [x] ML method (Isolation Forest or LOF)
- [ ] (Optional) LSTM autoencoder
- [x] Anomaly plots + method-overlap table
- [x] Real-world cause discussion

## Phase 5: Re-forecasting after cleaning | Rayyan + Yahya | due 2026-11-30
- [x] Anomalies imputed
- [x] SARIMA and Prophet refit on cleaned data
- [x] Before vs after comparison table + conclusion

## Phase 6: Repo and slides | All | due 2026-12-03
- [x] README complete with results
- [x] Final notebook runs top to bottom
- [x] Slides (dataset Rayyan, decomposition Prem, forecasting Yahya, anomalies Vishal, insights All)
- [ ] Dry run with timing
