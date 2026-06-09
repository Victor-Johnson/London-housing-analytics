import duckdb
from dotenv import load_dotenv
import os

load_dotenv()

con = duckdb.connect()
con.execute(f"""
    INSTALL httpfs;
    LOAD httpfs;
    CREATE SECRET aws_secret (
        TYPE S3,
        KEY_ID '{os.getenv("AWS_KEY_ID")}',
        SECRET '{os.getenv("AWS_SECRET")}',
        REGION '{os.getenv("AWS_REGION")}'
    );
""")


for label, path in [
    ("Price Paid",   "s3://victor-london-housing-analytics/pp-2018.csv"),
    ("HPI",          "s3://victor-london-housing-analytics/UK-HPI-full-file-2025-01.csv"),
    ("Applications", "s3://victor-london-housing-analytics/Number-of-applications-in-England-and-Wales-divided-by-region-2026-04.csv"),
]:
    print(f"\n{'='*50}")
    print(f"{label}")
    print('='*50)
    rows = con.execute(f"""
        DESCRIBE SELECT * FROM read_csv_auto('{path}', header=true, sample_size=1000)
    """).fetchall()
    for r in rows:
        print(f"  {r[0]:<35} {r[1]}")