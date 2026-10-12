"""
Catches the gap that let `fct_rents` ship in code before the data behind it
existed on the VPS: the app deployed fine (it's just Python), but nobody
verified the *database* the deployed code points at actually has every table
the pages query. A broken deploy or refresh should fail loudly here instead
of waiting for a user to click into a crashing page.

Skipped wherever the real DuckDB warehouse isn't present (e.g. the GitHub
Actions CI runner, which has no ~1GB .duckdb file) — this is a smoke test for
an environment with real data, not a unit test. Run it for real with:
    cd london_housing && pytest app/tests/test_schema_health.py -v
on your dev machine, or on the VPS via the `refresh`/`app` Docker image.
"""

import os

import duckdb
import pytest

from app.queries import DB_PATH

# Every table a Streamlit page queries directly. Add to this when a new page
# or query function starts depending on a new mart.
REQUIRED_TABLES = [
    "fct_transactions",
    "fct_price_index",
    "fct_rents",
    "dim_location",
]

pytestmark = pytest.mark.skipif(
    not os.path.exists(DB_PATH),
    reason=f"No DuckDB warehouse at {DB_PATH} — this check only runs where real data lives.",
)


def test_all_required_tables_exist():
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        existing = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    finally:
        con.close()

    missing = [t for t in REQUIRED_TABLES if t not in existing]
    assert not missing, (
        f"Missing tables in {DB_PATH}: {missing}. "
        "Run the relevant ingest script (e.g. load_rents.py) and `dbt run` before deploying."
    )


def test_required_tables_are_not_empty():
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        existing = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
        empty = []
        for table in REQUIRED_TABLES:
            if table not in existing:
                continue  # already reported by test_all_required_tables_exist
            count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if count == 0:
                empty.append(table)
    finally:
        con.close()

    assert not empty, f"Tables exist but have zero rows: {empty}"
