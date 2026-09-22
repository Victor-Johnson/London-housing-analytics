"""
Monthly refresh pipeline:
  1. Download the latest Price Paid monthly update from Land Registry
  2. Upload to S3 with a dated key (pp-YYYY-MM.csv)
  3. Load new rows from S3 into DuckDB via httpfs
  4. Run dbt

Run on the 15th of each month — Land Registry typically publishes mid-month.
Verify the source URL at: https://www.gov.uk/government/collections/price-paid-data

Usage:
  python refresh.py            # full run
  python refresh.py --dry-run  # validate every step without writing anything
"""

import subprocess
import sys
import os
import datetime
import argparse
import duckdb
import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "london_housing.duckdb")
BUCKET = os.getenv("AWS_BUCKET", "victor-london-housing-analytics")
REGION = os.getenv("AWS_REGION", "eu-west-2")

MONTHLY_UPDATE_URL = (
    "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com"
    "/pp-monthly-update-new-version.csv"
)

COLUMN_TYPES = {
    "column00": "VARCHAR",
    "column01": "BIGINT",
    "column02": "TIMESTAMP",
    "column03": "VARCHAR",
    "column04": "VARCHAR",
    "column05": "VARCHAR",
    "column06": "VARCHAR",
    "column07": "VARCHAR",
    "column08": "VARCHAR",
    "column09": "VARCHAR",
    "column10": "VARCHAR",
    "column11": "VARCHAR",
    "column12": "VARCHAR",
    "column13": "VARCHAR",
    "column14": "VARCHAR",
    "column15": "VARCHAR",
}


def check_url(url: str) -> None:
    print(f"[check] Land Registry URL...")
    r = requests.head(url, timeout=15, allow_redirects=True)
    r.raise_for_status()
    size_mb = int(r.headers.get("Content-Length", 0)) / 1_000_000
    print(f"  ✓ reachable — {size_mb:.1f} MB")


def check_s3() -> None:
    print(f"[check] S3 credentials and bucket access...")
    client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET"),
        region_name=REGION,
    )
    resp = client.list_objects_v2(Bucket=BUCKET, MaxKeys=1)
    objects = resp.get("KeyCount", 0)
    print(f"  ✓ bucket reachable — {objects} object(s) sampled")


def check_new_rows(tmp: str) -> int:
    print(f"[check] Counting new rows against existing DB...")
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        new = con.execute(f"""
            SELECT COUNT(*) FROM read_csv_auto(
                '{tmp}',
                header=false,
                columns={COLUMN_TYPES}
            )
            WHERE column00 NOT IN (SELECT transaction_id FROM raw_transactions)
        """).fetchone()[0]
        total_csv = con.execute(f"""
            SELECT COUNT(*) FROM read_csv_auto('{tmp}', header=false, columns={COLUMN_TYPES})
        """).fetchone()[0]
        print(f"  ✓ {total_csv:,} rows in CSV — {new:,} would be new")
        return new
    finally:
        con.close()


def download(url: str, dest: str) -> None:
    print("Downloading from Land Registry...")
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    size_mb = os.path.getsize(dest) / 1_000_000
    print(f"  ✓ {size_mb:.1f} MB downloaded")


def upload_to_s3(local_path: str, s3_key: str) -> str:
    print(f"Uploading to s3://{BUCKET}/{s3_key} ...")
    client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET"),
        region_name=REGION,
    )
    client.upload_file(local_path, BUCKET, s3_key)
    s3_uri = f"s3://{BUCKET}/{s3_key}"
    print(f"  ✓ uploaded to {s3_uri}")
    return s3_uri


def append_from_s3(s3_uri: str) -> int:
    print(f"Loading from {s3_uri} into DuckDB...")
    con = duckdb.connect(DB_PATH)
    try:
        con.execute(f"""
            INSTALL httpfs;
            LOAD httpfs;
            CREATE SECRET IF NOT EXISTS aws_secret (
                TYPE S3,
                KEY_ID '{os.getenv("AWS_KEY_ID")}',
                SECRET '{os.getenv("AWS_SECRET")}',
                REGION '{REGION}'
            );
        """)

        before = con.execute("SELECT COUNT(*) FROM raw_transactions").fetchone()[0]

        con.execute(f"""
            INSERT INTO raw_transactions
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
                '{s3_uri}' AS _source_file,
                current_timestamp AS _loaded_at
            FROM read_csv_auto(
                '{s3_uri}',
                header=false,
                columns={COLUMN_TYPES}
            )
            WHERE column00 NOT IN (SELECT transaction_id FROM raw_transactions)
        """)

        after = con.execute("SELECT COUNT(*) FROM raw_transactions").fetchone()[0]
        new_rows = after - before
        print(f"  ✓ {new_rows:,} new rows inserted ({after:,} total)")
        return new_rows
    finally:
        con.close()


def verify_db() -> None:
    print("[verify] Checking DB state after run...")
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        total = con.execute("SELECT COUNT(*) FROM raw_transactions").fetchone()[0]
        latest = con.execute(
            "SELECT MAX(date_of_transfer) FROM raw_transactions"
        ).fetchone()[0]
        latest_month = con.execute(
            "SELECT MAX(transfer_month) FROM fct_price_index"
        ).fetchone()[0]
        print(f"  raw_transactions : {total:,} rows, latest transfer: {latest}")
        print(f"  fct_price_index  : latest month = {latest_month}")
    finally:
        con.close()


def run_dbt() -> None:
    print("Running dbt...")
    dbt_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(["dbt", "run"], cwd=dbt_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print("dbt run failed:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    print("  ✓ dbt run complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Validate all steps without writing anything")
    args = parser.parse_args()

    month_key = datetime.date.today().strftime("pp-%Y-%m.csv")
    tmp = f"/tmp/{month_key}"

    try:
        if args.dry_run:
            print("=== DRY RUN — no data will be written ===\n")
            check_url(MONTHLY_UPDATE_URL)
            check_s3()
            download(MONTHLY_UPDATE_URL, tmp)
            check_new_rows(tmp)
            print("\n✓ All checks passed — run without --dry-run to execute.")
        else:
            download(MONTHLY_UPDATE_URL, tmp)
            s3_uri = upload_to_s3(tmp, month_key)
            new_rows = append_from_s3(s3_uri)
            if new_rows == 0:
                print("No new rows — already up to date, skipping dbt run.")
            else:
                run_dbt()
            verify_db()
            print("\nRefresh complete.")
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
