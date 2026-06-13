# Smartphone Sales Analytics

Data-analyst project exploring FY2025 smartphone sales in the Indian market across
brands and price segments — built with pandas, DuckDB (SQL), Jupyter, and Streamlit.

## Dataset

`data/smartphones.csv` — 60 products with price, units sold, rating, quarterly sales,
and key specs. Price segments: Budget (<=₹15K), Mid-Range (₹15–30K), Premium (₹30–50K),
Flagship (>₹50K).

## Setup

    python3 -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt

## Usage

- Tests: `pytest`
- Build the DuckDB database: `python db/build_db.py` (writes `db/smartphones.db`)
- Run SQL: `duckdb db/smartphones.db < sql/queries.sql` (requires the DuckDB CLI)
- EDA notebook: `jupyter notebook notebooks/analysis.ipynb`
- Dashboard: `streamlit run app.py`

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
