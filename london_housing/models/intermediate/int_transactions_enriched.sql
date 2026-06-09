
with source as (
    select * from {{ ref('stg_transactions') }}
    where is_non_market_transfer = false
),

enriched_transactions as (
    select
        transaction_id,
        price,
        date_of_transfer,
        postcode,
        property_type,
        tenure,
        new_build_flag,
        address_line,
        town_city,
        district,
        county,
        ppd_category_type,
        record_status,
        is_non_market_transfer,
        postcode_quality_flag,
        _source_file,
        _loaded_at,


extract(year from date_of_transfer) as transaction_year,
        extract(month from date_of_transfer) as transaction_month_num,
        date_trunc('month', date_of_transfer) as transaction_month,
        round(price / 1000000.0, 2) as price_millions,
        case
            when price < 250000 then 'under_250k'
            when price < 500000 then '250k_to_500k'
            when price < 1000000 then '500k_to_1m'
            when price < 2000000 then '1m_to_2m'
            else 'above_2m'
        end as price_band

    from source
)

select * from enriched_transactions