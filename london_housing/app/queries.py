import duckdb
import os

DB_PATH = os.getenv(
    "DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "london_housing.duckdb")
)

def get_top_rising(month: str, min_transactions: int = 20, limit: int = 3):
    con = duckdb.connect(DB_PATH, read_only=True)
    result = con.execute("""
        select
            district,
            county,
            avg_price,
            mom_change_pct,
            transaction_count
        from fct_price_index
        where transfer_month = ?
        and transaction_count >= ?
        order by mom_change_pct desc
        limit ?
    """, [month, min_transactions, limit]).fetchall()
    con.close()
    return result

def get_district_prices():
    con = duckdb.connect(DB_PATH, read_only=True)
    result = con.execute("""
        SELECT
            district,
            county,
            avg_price,
            median_price,
            transaction_count
        FROM fct_price_index
        WHERE transfer_month = (SELECT MAX(transfer_month) FROM fct_price_index)
        AND transaction_count >= 20
        ORDER BY avg_price ASC
    """).fetchall()
    con.close()
    return result


def get_top_falling(month: str, min_transactions: int = 20, limit: int = 3):
    con = duckdb.connect(DB_PATH, read_only=True)
    result = con.execute("""
        select
            district,
            county,
            avg_price,
            mom_change_pct,
            transaction_count
        from fct_price_index
        where transfer_month = ?
        and transaction_count >= ?
        order by mom_change_pct asc
        limit ?
    """, [month, min_transactions, limit]).fetchall()
    con.close()
    return result