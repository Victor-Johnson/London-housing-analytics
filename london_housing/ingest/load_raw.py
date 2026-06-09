import duckdb
from dotenv import load_dotenv
import os
import pandas as pd 
import numpy as np 

load_dotenv()

BUCKET = "victor-london-housing-analytics"

con = duckdb.connect("london_housing.duckdb")

con.execute(f"""
    INSTALL httpfs;
    LOAD httpfs;
    CREATE SECRET IF NOT EXISTS aws_secret (
        TYPE S3,
        KEY_ID '{os.getenv("AWS_KEY_ID")}',
        SECRET '{os.getenv("AWS_SECRET")}',
        REGION '{os.getenv("AWS_REGION")}'
    );
""")

# ── 1. Price Paid ─────────────────────────────────────────────
print("Loading Price Paid data...")

con.execute(f"""
    CREATE OR REPLACE TABLE raw_transactions AS
    SELECT
        column00  AS transaction_id,
        column01  AS price,
        column02  AS date_of_transfer,
        column03  AS postcode,
        column04  AS property_type,
        column05  AS old_new,
        column06  AS duration,
        column07  AS paon,
        column08  AS saon,
        column09  AS street,
        column10  AS locality,
        column11  AS town_city,
        column12  AS district,
        column13  AS county,
        column14  AS ppd_category_type,
        column15  AS record_status,
        filename  AS _source_file,
        current_timestamp AS _loaded_at
    FROM read_csv_auto(
        's3://{BUCKET}/pp-*.csv',
        header=false,
        filename=true,
        columns={{
            'column00': 'VARCHAR',
            'column01': 'BIGINT',
            'column02': 'TIMESTAMP',
            'column03': 'VARCHAR',
            'column04': 'VARCHAR',
            'column05': 'VARCHAR',
            'column06': 'VARCHAR',
            'column07': 'VARCHAR',
            'column08': 'VARCHAR',
            'column09': 'VARCHAR',
            'column10': 'VARCHAR',
            'column11': 'VARCHAR',
            'column12': 'VARCHAR',
            'column13': 'VARCHAR',
            'column14': 'VARCHAR',
            'column15': 'VARCHAR'
        }}
    )
""")

count = con.execute("SELECT COUNT(*) FROM raw_transactions").fetchone()[0]
print(f"  → {count:,} rows loaded")

# ── 2. HPI ────────────────────────────────────────────────────
print("Loading HPI data...")

con.execute(f"""
    CREATE OR REPLACE TABLE raw_hpi AS
    SELECT
        *,
        filename AS _source_file,
        current_timestamp AS _loaded_at
    FROM read_csv_auto(
        's3://{BUCKET}/UK-HPI-full-file-*.csv',
        header=true,
        filename=true
    )
""")

count = con.execute("SELECT COUNT(*) FROM raw_hpi").fetchone()[0]
print(f"  → {count:,} rows loaded")

# ── 3. Sanity checks ──────────────────────────────────────────
print("\nSanity checks:")

print("\nPrice Paid — year breakdown:")
con.execute("""
    SELECT
        year(date_of_transfer) AS year,
        count(*) AS transactions,
        min(price) AS min_price,
        max(price) AS max_price
    FROM raw_transactions
    GROUP BY 1
    ORDER BY 1
""").df().to_string(index=False)

rows = con.execute("""
    SELECT
        year(date_of_transfer) AS year,
        count(*) AS transactions,
        min(price) AS min_price,
        max(price) AS max_price
    FROM raw_transactions
    GROUP BY 1
    ORDER BY 1
""").fetchall()
for r in rows:
    print(f"  {r[0]}  {r[1]:>10,} transactions   £{r[2]:>10,} – £{r[3]:,}")

print("\nHPI — date range and regions:")
rows = con.execute("""
    SELECT
        min("Date") AS earliest,
        max("Date") AS latest,
        count(distinct "RegionName") AS regions
    FROM raw_hpi
""").fetchall()
for r in rows:
    print(f"  {r[0]} → {r[1]}   {r[2]} regions")

con.close()
print("\nDone.")