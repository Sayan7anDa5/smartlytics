"""Pure aggregation functions shared by the notebook and the dashboard."""
import pandas as pd

QUARTERS = ["q1", "q2", "q3", "q4"]


def brand_rollup(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby("brand", as_index=False)
        .agg(revenue=("revenue", "sum"), units=("units_sold", "sum"))
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )
    return out


def segment_rollup(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby("segment", as_index=False)
        .agg(revenue=("revenue", "sum"), units=("units_sold", "sum"))
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )
    return out


def market_share(df: pd.DataFrame, top: int = 8) -> pd.DataFrame:
    b = brand_rollup(df)
    total = b["revenue"].sum()
    b = b.head(top).copy()
    b["share_pct"] = (b["revenue"] / total * 100).round(1)
    return b


def quarterly_trend(df: pd.DataFrame) -> pd.DataFrame:
    melted = df.melt(
        id_vars=["segment"], value_vars=QUARTERS,
        var_name="quarter", value_name="units_k",
    )
    out = melted.groupby(["segment", "quarter"], as_index=False)["units_k"].sum()
    out["units"] = out["units_k"] * 1000
    return out.drop(columns="units_k")


def segment_winners(df: pd.DataFrame, n: int = 3) -> dict:
    return {
        seg: g.sort_values("revenue", ascending=False).head(n).reset_index(drop=True)
        for seg, g in df.groupby("segment")
    }


def kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_revenue": 0,
            "total_units": 0,
            "avg_rating": 0.0,
            "top_brand": "",
            "top_brand_revenue": 0,
            "num_brands": 0,
            "num_segments": 0,
        }
    b = brand_rollup(df)
    top = b.iloc[0]
    return {
        "total_revenue": int(df["revenue"].sum()),
        "total_units": int(df["units_sold"].sum()),
        "avg_rating": round(float(df["rating"].mean()), 1),
        "top_brand": str(top["brand"]),
        "top_brand_revenue": int(top["revenue"]),
        "num_brands": int(df["brand"].nunique()),
        "num_segments": int(df["segment"].nunique()),
    }
