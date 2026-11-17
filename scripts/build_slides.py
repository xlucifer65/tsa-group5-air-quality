"""Build the presentation deck from the figures and tables in reports/.

Usage: python scripts/build_slides.py  ->  docs/TSA_Group5_Slides.pptx
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports/figures"
OUT = ROOT / "docs/TSA_Group5_Slides.pptx"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.33), Inches(7.5)
BLANK = prs.slide_layouts[6]


def add_text(slide, text_lines, left, top, width, height, size=18):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = box.text_frame
    frame.word_wrap = True
    for i, line in enumerate(text_lines):
        para = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        para.text = line
        para.font.size = Pt(size)
        para.space_after = Pt(8)
    return box


def slide(title, bullets=None, image=None, speaker=None, notes=None):
    s = prs.slides.add_slide(BLANK)
    t = add_text(s, [title], 0.5, 0.3, 12.3, 0.9, size=32)
    t.text_frame.paragraphs[0].font.bold = True
    if image and bullets:
        add_text(s, ["• " + b for b in bullets], 0.5, 1.4, 4.6, 5.5, size=16)
        s.shapes.add_picture(str(FIG / image), Inches(5.3), Inches(1.4), width=Inches(7.6))
    elif image:
        s.shapes.add_picture(str(FIG / image), Inches(1.2), Inches(1.4), height=Inches(5.4))
    elif bullets:
        add_text(s, ["• " + b for b in bullets], 0.7, 1.5, 12, 5.5, size=20)
    if speaker:
        add_text(s, [f"Presenter: {speaker}"], 0.5, 6.95, 6, 0.4, size=11)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


slide(
    "Forecasting and Anomaly Detection: Paris PM2.5",
    [
        "EPITA AIS-26-S2, Time Series Analysis, Group 5",
        "Rayyan Ahemad Mohd, Prem Gudivada, Yahya Sow, Vishal Naveen",
        "Pipeline: EDA > decomposition > SARIMA/Prophet > anomalies > cleaning > re-forecast",
    ],
)
slide(
    "Dataset overview",
    [
        "Paris PM2.5, daily means, 2023-01-01 to 2025-10-30 (1034 days)",
        "20 isolated missing days, linear interpolation",
        "Fixed split: last 90 days = test (Aug-Oct 2025)",
        "Test period is a low-pollution season (mean 7.8 vs 11.1 µg/m³ in train)",
        "Source: see data/processed/SOURCE.txt",
    ],
    image="01_full_series.png",
    speaker="Rayyan",
)
slide(
    "Stationarity and ACF/PACF",
    [
        "ADF p = 0.0006, KPSS p >= 0.10: stationary, d = 0",
        "PACF cuts off after lag 1-3: AR component",
        "Weak weekly pattern (lag-7 ACF about 0.21)",
        "Seasonal differencing over-differences (ACF -0.54 at lag 7)",
    ],
    image="03_train_acf_pacf.png",
    speaker="Prem",
)
slide(
    "Decomposition: classical vs STL",
    [
        "Classical: additive vs multiplicative, period 7",
        "STL (robust) is not distorted by the pollution spikes",
        "Strong annual cycle (winter high), weak weekly cycle",
        "Residuals are larger in winter (heteroscedastic)",
    ],
    image="02_stl_robust.png",
    speaker="Prem",
)
slide(
    "Forecasting: ARIMA vs Prophet",
    [
        "ARIMA(2,0,2) by AIC, ARIMA(3,0,0) by BIC, no seasonal terms",
        "Prophet with weekly, yearly and French holidays",
        "Test RMSE: Prophet regularized 3.78, ARIMA 4.19, train-mean baseline 5.05",
        "Rolling-origin CV: ARIMA(2,0,2) most consistent (7.45)",
        "Gains over the mean baseline are modest at a 90-day horizon",
    ],
    image="03_prophet_forecast_vs_actual.png",
    speaker="Yahya",
)
slide(
    "Model comparison across folds",
    [
        "4 rolling 90-day windows",
        "Prophet regularized wins the final split but not the CV average",
        "Prediction intervals are unreliable: residuals are heavy-tailed",
        "Next step: log transform or weather regressors",
    ],
    image="03_cv_rmse_per_fold.png",
    speaker="Yahya",
)
slide(
    "Anomaly detection: three methods",
    [
        "Rolling Z-score on STL residuals",
        "ARIMA(2,0,2) residuals beyond 3 sigma",
        "Isolation Forest on lag and rolling features",
        "15 days agreed by >= 2 methods (1.5%)",
        "Mostly winter pollution episodes; a few low outliers",
    ],
    image="04_anomalies_overview.png",
    speaker="Vishal",
)
slide(
    "Cleaning and re-forecast",
    [
        "Agreed anomalies replaced by STL trend + seasonal",
        "Only the training set is cleaned; test left raw",
        "Refit ARIMA and Prophet, same settings",
    ],
    image="05_cleaning_effect.png",
    speaker="Rayyan",
)
slide(
    "Before vs after",
    [
        "No consistent improvement: ARIMA(3,0,0) -3.4%, Prophet additive -2.0%",
        "ARIMA(2,0,2) +12.7%, Prophet regularized +0.8%",
        "Calm test season, no anomalies in the test window",
        "AIC/BIC drop is expected and not comparable",
    ],
    image="05_before_after_rmse.png",
    speaker="Rayyan, Yahya",
)
slide(
    "Insights and recommendations",
    [
        "Annual seasonality dominates; weekly effect is small",
        "Simple ARIMA is competitive; use Prophet for the seasonal shape",
        "Detect anomalies with several methods and only clean agreed ones",
        "Cleaning matters most before forecasts that follow an episode",
        "Future work: weather regressors, log transform, per-fold cleaning",
    ],
    speaker="All",
)

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT)
print(f"Saved {OUT} ({len(prs.slides)} slides)")
