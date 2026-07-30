import duckdb

con = duckdb.connect("london_housing.duckdb")


con.execute("""
    LOAD httpfs;
    SET s3_endpoint='localhost:9000';
    SET s3_access_key_id='localuser';
    SET s3_secret_access_key='localpassword';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
""")

# Read ALL yearly files in one statement using glob
con.execute("""
    CREATE OR REPLACE TABLE raw_transactions AS
    SELECT
        *,
        current_timestamp AS _loaded_at,
        filename AS _source_file
    FROM read_csv_auto(
        's3://london-housing-raw/price-paid/pp-*.csv',
        header=false,
        filename=true,
        columns={
            'transaction_id': 'VARCHAR',
            'price':          'INTEGER',
            'date_of_transfer': 'DATE',
            'postcode':       'VARCHAR',
            'property_type':  'VARCHAR',
            'old_new':        'VARCHAR',
            'duration':       'VARCHAR',
            'paon':           'VARCHAR',
            'saon':           'VARCHAR',
            'street':         'VARCHAR',
            'locality':       'VARCHAR',
            'town_city':      'VARCHAR',
            'district':       'VARCHAR',
            'county':         'VARCHAR',
            'ppd_category_type': 'VARCHAR',
            'record_status':  'VARCHAR'
        }
    )
""")

count = con.execute("SELECT COUNT(*) FROM raw_transactions").fetchone()[0]
print(f"Loaded {count:,} total rows across all years")