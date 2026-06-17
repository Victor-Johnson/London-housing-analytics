with source as (
    SELECT * FROM {{ ref('int_transactions_enriched') }}
),

time_reference_table AS (
    SELECT DISTINCT
        transaction_year,
        transaction_month_num,
        transaction_month,
        CASE 
            WHEN transaction_month_num in (12 ,1, 2)  THEN  'winter'
            WHEN transaction_month_num in (3, 4, 5) THEN 'spring'
            WHEN transaction_month_num in (6, 7, 8) THEN 'summer'  
            ELSE  'autumn'
        END as season
    FROM source
)

SELECT * FROM time_reference_table
ORDER BY season ASC