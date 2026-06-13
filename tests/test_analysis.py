import pandas as pd

from src.data_loader import derive
from src import analysis


def _df():
    raw = pd.DataFrame({
        "id": [1, 2, 3],
        "brand": ["Samsung", "Samsung", "Apple"],
        "model": ["A", "B", "C"],
        "price_inr": [10000, 20000, 80000],
        "units_sold": [100, 200, 50],
        "rating": [4.0, 4.5, 4.8],
        "q1": [1, 2, 3], "q2": [1, 2, 3], "q3": [1, 2, 3], "q4": [1, 2, 3],
        "url": ["", "", ""],
        "display": ["", "", ""], "processor": ["", "", ""], "camera": ["", "", ""],
        "battery": ["", "", ""], "ram": ["", "", ""], "storage": ["", "", ""],
    })
    return derive(raw)


def test_kpis():
    k = analysis.kpis(_df())
    assert k["total_revenue"] == 10000*100 + 20000*200 + 80000*50
    assert k["total_units"] == 350
    assert k["num_brands"] == 2
    assert k["top_brand"] == "Samsung"


def test_kpis_empty_df():
    """kpis must not raise on an empty DataFrame and must return zeroed keys."""
    empty = pd.DataFrame(columns=_df().columns)
    k = analysis.kpis(empty)
    expected_keys = {
        "total_revenue", "total_units", "avg_rating",
        "top_brand", "top_brand_revenue", "num_brands", "num_segments",
    }
    assert set(k.keys()) == expected_keys
    assert k["total_revenue"] == 0
    assert k["total_units"] == 0
    assert k["avg_rating"] == 0.0
    assert k["top_brand"] == ""
    assert k["top_brand_revenue"] == 0
    assert k["num_brands"] == 0
    assert k["num_segments"] == 0


def test_brand_rollup_sorted_desc():
    b = analysis.brand_rollup(_df())
    assert list(b["brand"]) == ["Samsung", "Apple"]
    assert b.iloc[0]["revenue"] == 5_000_000


def _df_10_brands():
    """10 distinct brands, revenue increasing by brand index (brand_0 cheapest)."""
    rows = []
    for i in range(10):
        rows.append({
            "id": i + 1,
            "brand": f"Brand{i:02d}",
            "model": f"M{i}",
            "price_inr": 10_000 + i * 1_000,   # all in Budget/Mid-Range range
            "units_sold": (i + 1) * 10,         # revenue increases with i
            "rating": 4.0,
            "q1": 1, "q2": 1, "q3": 1, "q4": 1,
            "url": "", "display": "", "processor": "",
            "camera": "", "battery": "", "ram": "", "storage": "",
        })
    from src.data_loader import derive
    return derive(pd.DataFrame(rows))


def test_market_share_sums_consistent():
    """top-N share_pct should sum to < 100 when brands exist outside the top-N.

    This test verifies that the denominator is the TOTAL revenue across ALL brands,
    not just the top-N. With 10 brands and top=8, the 2 smallest are excluded from
    the numerator but still counted in the denominator, so share_pct.sum() < 100.
    """
    df = _df_10_brands()
    m = analysis.market_share(df, top=8)
    assert len(m) == 8, "should return exactly top=8 rows"
    assert m["share_pct"].sum() < 100, (
        "share_pct sum must be < 100 when not all brands are in top-N "
        "(total must be computed over ALL brands, not just top-N)"
    )


def test_quarterly_trend_columns():
    """quarterly_trend must expose exactly ['segment', 'quarter', 'units']."""
    q = analysis.quarterly_trend(_df())
    assert list(q.columns) == ["segment", "quarter", "units"], (
        f"unexpected columns: {list(q.columns)}"
    )


def test_quarterly_trend_units_scaled():
    q = analysis.quarterly_trend(_df())
    row = q[(q["segment"] == "Mid-Range") & (q["quarter"] == "q1")]
    assert int(row["units"].iloc[0]) == 2000


def test_segment_winners_keys():
    w = analysis.segment_winners(_df(), n=3)
    assert "Flagship" in w
    assert len(w["Budget"]) >= 1


def _df_segment_ordering():
    """One segment (Budget) with 5 products having known descending revenues."""
    rows = []
    # 5 Budget products (price_inr <= 15000), revenue = price * units
    revenues = [50_000, 40_000, 30_000, 20_000, 10_000]
    for i, rev in enumerate(revenues):
        price = 10_000
        units = rev // price
        rows.append({
            "id": i + 1,
            "brand": f"BrandX{i}",
            "model": f"Mdl{i}",
            "price_inr": price,
            "units_sold": units,
            "rating": 4.0,
            "q1": 1, "q2": 1, "q3": 1, "q4": 1,
            "url": "", "display": "", "processor": "",
            "camera": "", "battery": "", "ram": "", "storage": "",
        })
    from src.data_loader import derive
    return derive(pd.DataFrame(rows))


def test_segment_winners_n_limit_and_ordering():
    """segment_winners must return exactly n rows, sorted by revenue descending."""
    n = 3
    df = _df_segment_ordering()
    w = analysis.segment_winners(df, n=n)
    assert "Budget" in w, "Budget segment should be present"
    result = w["Budget"]
    assert len(result) == n, f"expected {n} rows, got {len(result)}"
    revenues = list(result["revenue"])
    assert revenues == sorted(revenues, reverse=True), (
        f"revenue column should be sorted descending, got {revenues}"
    )
