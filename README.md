# London Housing — dbt + DuckDB Analytics

End-to-end analytics pipeline for UK residential property sales. Ingests HM Land Registry Price Paid data and the UK House Price Index (HPI) from S3, loads them into a local DuckDB file, and transforms them through a dbt model layer into analysis-ready fact and dimension tables.

## Data sources

| Source | Description |
| --- | --- |
| HM Land Registry Price Paid | Individual property transactions across England & Wales |
| UK House Price Index (HPI) | Monthly regional average prices and index values |

Both datasets are stored as CSV files in an S3 bucket and loaded into DuckDB via `ingest/load_raw.py`.

## Architecture

```text
S3 (raw CSVs)
    └── ingest/load_raw.py       # loads raw_transactions, raw_hpi into DuckDB
        └── staging/             # clean column names, cast types, decode codes
            └── intermediate/    # filter non-market transfers, add price bands & date parts
                └── marts/       # fct_transactions, fct_price_index, dim_location, dim_property, dim_time
```

## Quickstart

### 1. Environment setup

```bash
source env/bin/activate
pip install dbt-core dbt-duckdb duckdb python-dotenv pandas
```

### 2. Configure AWS credentials

Create a `.env` file in the project root:

```
AWS_KEY_ID=your_key
AWS_SECRET=your_secret
AWS_REGION=eu-west-2
AWS_BUCKET=your-bucket-name
```

### 3. Configure dbt profile

Add to `~/.dbt/profiles.yml`:

```yaml
london_housing:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../london_housing.duckdb
      threads: 1
```

### 4. Ingest raw data from S3

```bash
cd london_housing
python ingest/load_raw.py
```

This creates `raw_transactions` and `raw_hpi` tables in `london_housing.duckdb`.

### 5. Run dbt

```bash
dbt debug       # verify connection
dbt run         # build all models
dbt test        # run data quality tests
dbt docs generate && dbt docs serve
```

## Project structure

```text
london_housing/
├── ingest/
│   └── load_raw.py                     # S3 → DuckDB ingestion
├── models/
│   ├── staging/
│   │   ├── stg_transactions.sql        # decoded property types, tenure, address cleanup
│   │   └── stg_hpi.sql                 # renamed HPI columns, buyer/transaction type splits
│   ├── intermediate/
│   │   ├── int_transactions_enriched.sql  # filters non-market transfers, adds price bands
│   │   └── int_price_index.sql
│   └── marts/
│       ├── fct_transactions.sql
│       ├── fct_price_index.sql
│       ├── dim_location.sql
│       ├── dim_property.sql
│       └── dim_time.sql
└── utils/                              # schema sniffing and bucket inspection scripts
```

## Streamlit app

![London Housing Market Briefing](Pictures/app_screenshot.png)

## Resources

- [dbt docs](https://docs.getdbt.com)
- [Land Registry Price Paid Data](https://www.gov.uk/government/collections/price-paid-data)
- [UK House Price Index](https://www.gov.uk/government/collections/uk-house-price-index-reports)
