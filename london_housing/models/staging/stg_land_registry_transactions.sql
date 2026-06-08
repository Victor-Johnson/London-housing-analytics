{{ config(MATERIALIZED='view')}}

with raw_transcations AS (
    SELECT * 
    FROM read_csv(
        'data/pp-*.csv',
        header=false,
        columns={
            'transaction_id': 'VARCHAR',
            'price':'BIGINT',
            'transfer_date':'TIMESTAMP',
            'postcode':'VARCHAR',
            'property_type':'VARCHAR',
            'is_new':'VARCHAR',
            'duration':'VARCHAR',
            'paon':'VARCHAR',
            'soan':'VARCHAR',
            'street':'VARCHAR',
            'locality':'VARCHAR',
            'county':'VARCHAR',
            'ppd_category_type':'VARCHAR',
            'record_status':'VARCHAR'
        }
    )
)

SELECT 
    -- PRIMARY KEY TO BE USED 
    transaction_id, 

    -- Core Metrics 
    price,
    CAST(transfer_date AS DATE) AS transfer_date,

    --Geography 
    postcode,
    poan,
    soan,
    street,
    locality,
    town_city,
    district,
    county,

    --Attributes
    property_type,
    CASE WHEN is_new = 'Y' THEN true ELSE false END AS is_new_build
    duration AS tenure,
    ppd_category_type,
    record_status

FROM raw_transactions 