import duckdb

DB_PATH = "/Users/victorjohnson/Desktop/portfolio/2026/london_housing/london_housing/london_housing.duckdb"

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