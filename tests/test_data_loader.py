import pandas as pd
import pytest

from src.data_loader import load_data, derive, REQUIRED_COLUMNS


def _raw():
    return pd.DataFrame({
        "id": [1, 2],
        "brand": ["Samsung", "Apple"],
        "model": ["Galaxy X", "iPhone Y"],
        "price_inr": [12000, 80000],
        "units_sold": [100, 50],
        "rating": [4.2, 4.6],
        "q1": [10, 5], "q2": [10, 5], "q3": [10, 5], "q4": [10, 5],
        "url": ["http://a", "http://b"],
        "display": ["", ""], "processor": ["", ""], "camera": ["", ""],
        "battery": ["", ""], "ram": ["", ""], "storage": ["", ""],
    })


def test_load_data_returns_60_rows():
    df = load_data()
    assert len(df) == 60
    assert df["id"].is_unique


def test_required_columns_present():
    df = load_data()
    for col in REQUIRED_COLUMNS:
        assert col in df.columns


def test_derive_adds_revenue_segment_perf_score():
    df = derive(_raw())
    assert df.loc[0, "revenue"] == 12000 * 100
    assert df.loc[0, "segment"] == "Budget"
    assert df.loc[1, "segment"] == "Flagship"
    assert {"revenue", "segment", "perf_score"} <= set(df.columns)


def test_segment_boundaries():
    df = _raw().copy()
    df["price_inr"] = [15000, 15001]
    out = derive(df)
    assert out.loc[0, "segment"] == "Budget"
    assert out.loc[1, "segment"] == "Mid-Range"


def test_perf_score_is_int_0_to_100():
    df = derive(_raw())
    assert df["perf_score"].dtype.kind in "iu"
    assert df["perf_score"].between(0, 100).all()


def test_invalid_rating_raises():
    df = _raw()
    df.loc[0, "rating"] = 9.0
    with pytest.raises(ValueError):
        derive(df)


def test_negative_price_raises():
    df = _raw()
    df.loc[0, "price_inr"] = -1
    with pytest.raises(ValueError):
        derive(df)
