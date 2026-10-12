import duckdb
import pytest

from app import queries


@pytest.fixture
def fixture_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "fixture.duckdb")
    con = duckdb.connect(db_path)
    con.execute("""
        CREATE TABLE fct_price_index (
            transfer_month DATE,
            district VARCHAR,
            county VARCHAR,
            avg_price DOUBLE,
            median_price DOUBLE,
            mom_change_pct DOUBLE,
            transaction_count INTEGER
        )
    """)
    con.execute("""
        INSERT INTO fct_price_index VALUES
            ('2024-01-01', 'Hackney',    'Greater London', 500000, 480000,  12.0, 40),
            ('2024-01-01', 'Barking',    'Greater London', 250000, 240000,  -8.0, 30),
            ('2024-01-01', 'Camden',     'Greater London', 700000, 690000,   3.0, 25),
            ('2024-01-01', 'Croydon',    'Greater London', 350000, 340000,   1.0,  5),
            ('2024-02-01', 'Hackney',    'Greater London', 520000, 500000,   4.0, 35)
    """)
    con.close()
    monkeypatch.setattr(queries, "DB_PATH", db_path)
    return db_path


def test_get_top_rising_filters_by_min_transactions_and_orders_desc(fixture_db):
    rising = queries.get_top_rising("2024-01-01", min_transactions=20, limit=3)

    districts = [r[0] for r in rising]
    assert "Croydon" not in districts  # only 5 transactions, below threshold
    assert districts == ["Hackney", "Camden", "Barking"]  # descending mom_change_pct


def test_get_top_falling_orders_ascending(fixture_db):
    falling = queries.get_top_falling("2024-01-01", min_transactions=20, limit=2)

    districts = [r[0] for r in falling]
    assert districts == ["Barking", "Camden"]


def test_get_district_prices_uses_latest_month_only(fixture_db):
    rows = queries.get_district_prices()

    districts = [r[0] for r in rows]
    assert "Hackney" in districts
    assert "Barking" not in districts  # not present in the latest month, 2024-02
    assert "Croydon" not in districts  # below the 20-transaction threshold


@pytest.fixture
def fixture_rents_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "fixture_rents.duckdb")
    con = duckdb.connect(db_path)
    con.execute("""
        CREATE TABLE fct_rents (
            time_period DATE,
            district VARCHAR,
            region_name VARCHAR,
            rental_price BIGINT,
            rental_price_one_bed BIGINT,
            rental_price_two_bed BIGINT,
            rental_price_three_bed BIGINT,
            rental_price_four_or_more_bed BIGINT,
            mom_change_pct DOUBLE
        )
    """)
    con.execute("""
        INSERT INTO fct_rents VALUES
            ('2024-01-01', 'HACKNEY', 'London', 1800, 1500, 1900, 2400, 3000,  2.0),
            ('2024-01-01', 'BURNLEY', 'North West', 650, 500, 700, 850, 1000, -1.0),
            ('2024-02-01', 'HACKNEY', 'London', 1850, 1550, 1950, 2450, 3050,  2.8),
            ('2024-02-01', 'BURNLEY', 'North West', 680, 520, 720, 870, 1020,  4.6)
    """)
    con.close()
    monkeypatch.setattr(queries, "DB_PATH", db_path)
    return db_path


def test_get_district_rents_uses_latest_month_only(fixture_rents_db):
    rows = queries.get_district_rents()

    districts = [r[0] for r in rows]
    assert districts == ["BURNLEY", "HACKNEY"]  # sorted ascending by rental_price

    burnley = next(r for r in rows if r[0] == "BURNLEY")
    assert burnley[2] == 680  # rental_price — the February value, not January's 650
