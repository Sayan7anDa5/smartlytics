# Smartphone Sales Analytics

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://smartphone-sales-analytics.streamlit.app)

An end-to-end data-analyst project on FY2025 smartphone sales in the Indian market.
A single CSV feeds a validating pandas pipeline, a DuckDB/SQL query layer, a Jupyter
EDA notebook, and an interactive Streamlit dashboard that ranks the top-performing
products across the Budget, Mid-Range, Premium, and Flagship price segments.

**🔗 Live demo:** https://smartphone-sales-analytics.streamlit.app

**Built with:** Python · pandas · DuckDB (SQL) · Plotly · Streamlit · Jupyter

## Dataset

`data/smartphones.csv` — 60 products with price, units sold, rating, quarterly sales,
and key specs. Price segments: Budget (<=₹15K), Mid-Range (₹15–30K), Premium (₹30–50K),
Flagship (>₹50K).

## Setup

    python3 -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt          # runtime (dashboard + SQL)
    pip install -r requirements-dev.txt      # adds tests + notebook tooling

## Usage

- Dashboard: `streamlit run app.py`
- Build the DuckDB database: `python db/build_db.py` (writes `db/smartphones.db`)
- Run SQL: `duckdb db/smartphones.db < sql/queries.sql` (requires the DuckDB CLI)
- EDA notebook: `jupyter notebook notebooks/analysis.ipynb` (needs requirements-dev.txt)
- Tests: `pytest` (needs requirements-dev.txt)

## Deployment

The dashboard is deployed on [Streamlit Community Cloud](https://streamlit.io/cloud):
push to `master`, then point a new app at `app.py` — Cloud installs `requirements.txt`
and serves it. Every push to `master` redeploys automatically.

## Layout

| Path | Purpose |
|------|---------|
| `data/smartphones.csv` | Single source of truth |
| `src/config.py` | Segment bins and color config |
| `src/data_loader.py` | Load, validate, derive (segment, revenue, perf_score) |
| `src/analysis.py` | Shared aggregation functions |
| `db/build_db.py`, `sql/queries.sql` | DuckDB + reference SQL |
| `notebooks/analysis.ipynb` | Exploratory analysis |
| `app.py` | Streamlit dashboard |
| `tests/` | pytest suite |
