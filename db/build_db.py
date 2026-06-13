"""Materialize the validated dataset into a DuckDB database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import duckdb

from src.data_loader import load_data

DB_PATH = Path(__file__).resolve().parent / "smartphones.db"


def build(db_path: Path = DB_PATH) -> None:
    df = load_data()  # noqa: F841 — referenced by DuckDB replacement scan
    con = duckdb.connect(str(db_path))
    con.execute("CREATE OR REPLACE TABLE smartphones AS SELECT * FROM df")
    n = con.execute("SELECT COUNT(*) FROM smartphones").fetchone()[0]
    con.close()
    print(f"Built {db_path} with {n} rows")


if __name__ == "__main__":
    build()
