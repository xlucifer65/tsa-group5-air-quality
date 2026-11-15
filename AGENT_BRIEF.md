# Agent Brief: TSA Group 5 Project

## Context
EPITA AIS-26-S2 Time Series Analysis project, Group 5. Professor: Alaa Bakhti.
- Assignment brief (source of truth): https://github.com/EPITA-courses/time-series-analysis/blob/main/assignments/2_project.md
- Course repo (reuse its style and helpers, e.g. `tsa/anomaly_detection.py`): https://github.com/EPITA-courses/time-series-analysis
- Our repo: https://github.com/xlucifer65/tsa-group5-air-quality (local: `~/TSA-Group5`)
- Plan and task list: `docs/TSA_Group5_Work_Plan.pdf` and `CHECKLIST.md`. Follow them exactly.

**Goal:** forecasting and anomaly detection on OpenAQ air quality data (Paris PM2.5, hourly resampled to daily, about 2 to 3 years). Workflow: EDA (missing values, ADF, ACF/PACF), then decomposition (classical + STL), then SARIMA and Prophet (RMSE, MAE, AIC/BIC), then anomaly detection (Z-score, ARIMA residuals, one ML method), then clean the anomalies and re-forecast, then compare before vs after.

## Team and ownership
| Member | Branch | Owns |
|---|---|---|
| Rayyan (you work for him) | `rayyan/pipeline` | Repo, data pipeline, re-forecasting, integration |
| Prem | `prem/eda` | Phases 1 and 2: EDA and decomposition |
| Yahya | `yahya/forecast` | Phase 3: SARIMA and Prophet |
| Vishal | `vishal/anomaly` | Phase 4: anomaly detection |

## Your tasks, in order
1. **Work only inside `~/TSA-Group5`.** No files outside the repo.
2. **Create GitHub issues for the others' work:** one issue per checklist item in Phases 1 to 6, labeled by phase (`phase-1-eda`, etc.) and by owner (`owner:prem`, `owner:yahya`, `owner:vishal`, `owner:rayyan`), with a due date from `CHECKLIST.md` in the body and grouped under a milestone per phase. Assign people once they're collaborators.
3. **Add CI** in `.github/workflows/ci.yml`, running on every PR and on pushes to `main`:
   - Python 3.10, `pip install -r requirements.txt`
   - `ruff check src/`
   - `pytest` (add `tests/` with tests for `src/load_data.py` and the metrics)
   - Notebooks smoke-test: `jupyter nbconvert --to notebook --execute` on `notebooks/*.ipynb` (use a small sample dataset in CI so it runs fast)
   - Fail the check if any notebook has outputs larger than 5 MB
4. **Add repo rules:**
   - `.github/pull_request_template.md`: what changed, which checklist items it ticks, screenshots of plots, a confirmation that the notebook runs
   - `CONTRIBUTING.md`: the branch and PR rules below
   - `.github/CODEOWNERS`: notebooks map to their owners and `src/` to Rayyan
   - Branch protection on `main` (`gh api`): require a PR, one approving review and passing CI; no force pushes
5. **Do Rayyan's Phase 0 work** on branch `rayyan/pipeline`:
   - `src/load_data.py`: download OpenAQ PM2.5 for one Paris station (public S3 archive `openaq-data-archive`, or API v3 with an `OPENAQ_API_KEY` env var, never committed), resample to daily, and save `data/processed/pm25_paris_daily.csv`
   - `get_train_test()` with a fixed time split (last 90 days as test), which everyone imports
   - `src/metrics.py` (RMSE, MAE) and `src/plots.py`
   - Notebook stubs `01_eda` to `05_reforecast`, each with section headers matching the brief
6. **Open a PR** from `rayyan/pipeline` into `main`, tick the matching items in `CHECKLIST.md` in that same PR, and wait for CI to pass.

## Git, PR and merge rules (mandatory)
- Never commit directly to `main`. One branch per task, named `<owner>/<topic>`.
- Small commits with clear messages (`feat:`, `fix:`, `docs:`, `ci:`, `test:`).
- **Do not add any "Co-Authored-By: Claude" line to commits or PRs.**
- Every PR needs passing CI, one approving review from a teammate and a linked issue (`Closes #N`).
- Squash-merge only. Delete the branch after merging.
- Rebase on `main` before requesting review. Resolve conflicts yourself; never overwrite a teammate's notebook.
- Never commit raw data, `.env` files, API keys or large outputs.
- Never merge your own PR without Rayyan's approval.

## Done means
CI is green, the issues exist for everyone, protection rules are on, the Phase 0 PR is open, and you've reported back with the links (PR, issues, Actions run) plus anything that blocked you.
