# TSA Group 5: Air Quality Forecasting and Anomaly Detection

EPITA AIS-26-S2, Time Series Analysis project ([brief](https://github.com/EPITA-courses/time-series-analysis/blob/main/assignments/2_project.md)).

**Dataset:** OpenAQ air quality, Paris PM2.5, hourly readings resampled to daily means.

| Member | Ownership |
|---|---|
| Rayyan Ahemad Mohd | Repo, data pipeline, re-forecasting, integration |
| Prem Gudivada | Data exploration and decomposition |
| Yahya Sow | SARIMA and Prophet forecasting |
| Vishal Naveen | Anomaly detection |

## Problem
Forecast daily PM2.5 in Paris with SARIMA and Prophet, detect anomalies with several methods, clean them, re-forecast, and measure whether cleaning improved the forecast.

## Dataset
Paris PM2.5, daily means, 2023-01-01 to 2025-10-30 (1034 days, 20 isolated missing days filled by linear interpolation). The committed series in `data/processed/pm25_paris_daily.csv` comes from the Open-Meteo air-quality service (see `data/processed/SOURCE.txt`), as a stand-in until an OpenAQ station series is produced with `python -m src.load_data` (needs `OPENAQ_API_KEY`). Train/test split: last 90 days are the test set (`src.load_data.get_train_test`).

## Results summary

| Step | Finding |
|---|---|
| Stationarity | Raw series stationary (ADF p = 0.0006), so d = 0. Weak weekly seasonality; strong annual cycle. |
| Decomposition | Robust STL handles pollution spikes better than classical decomposition; residuals are larger in winter. |
| Forecasting (90-day test) | Prophet regularized RMSE 3.78, ARIMA(2,0,2) 4.19, ARIMA(3,0,0) 4.89, train-mean baseline 5.05. ARIMA(2,0,2) has the best rolling-origin CV mean (7.45). |
| Anomalies | Rolling Z-score on STL residuals, ARIMA 3-sigma residuals and Isolation Forest; 15 days (1.5%) agreed by at least two methods, mostly winter pollution episodes. |
| Cleaning | No consistent improvement on the calm test window (RMSE change from -3.4% to +12.7% depending on the model); see `notebooks/05_reforecast.ipynb`. |

Tables are in `reports/tables/` and figures in `reports/figures/`. Slides: `docs/TSA_Group5_Slides.pptx` (regenerate with `python scripts/build_slides.py`).

## Structure
```
data/raw, data/processed   raw + cleaned daily series
notebooks/                 01_eda, 02_decomposition, 03_forecasting, 04_anomalies, 05_reforecast
src/                       shared loading, split, metrics, plotting, anomalies, forecasting
tests/                     pytest suite (CI)
scripts/                   notebook output check, slide builder
reports/figures, tables/   exported plots and result tables
docs/                      work plan PDF, SARIMA orders note, slides
```

## Running the notebooks
Run `01_eda` to `05_reforecast` in order from the repo root (or from `notebooks/`); each notebook is independent and reads `data/processed/pm25_paris_daily.csv`. Notebook 03 (cross-validation) and 05 (16 model fits) take a few minutes.

## Setup
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

## Workflow
One branch per person (`prem/eda`, `yahya/forecast`, `vishal/anomaly`, `rayyan/pipeline`), with a PR into `main` reviewed by one teammate. Tick items in [CHECKLIST.md](CHECKLIST.md) in the same PR that completes them.
