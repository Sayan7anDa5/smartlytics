"""Load, validate, and derive fields for the smartphone dataset."""
from pathlib import Path

import pandas as pd

from src.config import SEGMENT_BIN_EDGES, SEGMENT_ORDER

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "smartphones.csv"

REQUIRED_COLUMNS = [
    "id", "brand", "model", "price_inr", "units_sold", "rating",
    "q1", "q2", "q3", "q4", "url",
    "display", "processor", "camera", "battery", "ram", "storage",
]


def _validate(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if not df["id"].is_unique:
        raise ValueError("Duplicate ids found")
    if (df["price_inr"] <= 0).any():
        raise ValueError("price_inr must be > 0")
    if (df["units_sold"] < 0).any():
        raise ValueError("units_sold must be >= 0")
    if not df["rating"].between(0, 5).all():
        raise ValueError("rating must be within [0, 5]")


def derive(df: pd.DataFrame) -> pd.DataFrame:
    """Validate then add segment, revenue, and perf_score."""
    _validate(df)
    df = df.copy()
    df["revenue"] = df["price_inr"] * df["units_sold"]
    df["segment"] = pd.cut(
        df["price_inr"],
        bins=SEGMENT_BIN_EDGES,
        labels=SEGMENT_ORDER,
        right=True,
        include_lowest=True,
    ).astype(str)

    # Computed once across the dataset, never per-row.
    max_rev = df["revenue"].max()
    max_units = df["units_sold"].max()
    df["perf_score"] = (
        (df["revenue"] / max_rev) * 40
        + (df["units_sold"] / max_units) * 35
        + (df["rating"] / 5) * 25
    ).round().astype(int)
    return df


def load_data(csv_path: Path = CSV_PATH) -> pd.DataFrame:
    """Read the CSV and return the validated, derived DataFrame."""
    df = pd.read_csv(csv_path)
    return derive(df)
