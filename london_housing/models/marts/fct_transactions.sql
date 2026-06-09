with source as (
    SELECT * FROM {{ ref('int_transactions_enriched') }}
),

fct_transactions as (
SELECT 
    transaction_id,
    price,
    price_millions,
    price_band,
    date_of_transfer,
    transaction_year,
    transaction_month_num,
    transaction_month,
    property_type,
    tenure,
    new_build_flag,
    address_line,
    postcode,
    district,
    county,
    ppd_category_type,
    record_status,
    _source_file
FROM source 
)

SELECT * FROM fct_transactions