with source as (
    select * from {{ ref('stg_transactions') }}
    WHERE is_non_market_transfer = false
),

enriched_transactions as (
    select
        date_of_transfer,
        EXTRACT(YEAR FROM date_of_transfer) AS transaction_year,
        EXTRACT(MONTH FROM date_of_transfer) AS transaction_month_num,
        round(price/1000000.0,2) AS price_millions,
        CASE 
            WHEN price < 250000 THEN 'under_250k'
            WHEN price < 500000 THEN '250k to 500k'
            WHEN price < 1000000 THEN '500k_to_1m'
            WHEN price < 2000000 THEN '1m_to_2m'
            ELSE  'Above_2M'
        
        END AS price_band
    FROM source 
)

SELECT * FROM enriched_transactions



