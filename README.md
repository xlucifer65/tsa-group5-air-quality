# TSA Group 5: Air Quality Forecasting and Anomaly Detection

EPITA AIS-26-S2, Time Series Analysis project ([brief](https://github.com/EPITA-courses/time-series-analysis/blob/main/assignments/2_project.md)).

**Dataset:** OpenAQ air quality, Paris PM2.5, hourly readings resampled to daily means.

| Member | Ownership |
|---|---|
| Rayyan Ahemad Mohd | Repo, data pipeline, re-forecasting, integration |
| Prem Gudivada | Data exploration and decomposition |
| Yahya Sow | SARIMA and Prophet forecasting |
| Vishal Naveen | Anomaly detection |

## Structure
```
data/raw, data/processed   raw + cleaned daily series
notebooks/                 01_eda, 02_decomposition, 03_forecasting, 04_anomalies, 05_reforecast
src/                       shared loading, split, metrics, plotting
reports/figures/           exported plots
docs/                      work plan PDF
```

## Setup
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

## Workflow
One branch per person (`prem/eda`, `yahya/forecast`, `vishal/anomaly`, `rayyan/pipeline`), with a PR into `main` reviewed by one teammate. Tick items in [CHECKLIST.md](CHECKLIST.md) in the same PR that completes them.
