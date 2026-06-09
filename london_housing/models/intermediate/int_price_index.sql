
with source as (
    select * from {{ ref('stg_transactions') }}
),

filtered as (
    select * from source
    where is_non_market_transfer = false
    and postcode_quality_flag = 'valid'
),

monthly_prices as (
    select
        date_trunc('month', date_of_transfer) as transfer_month,
        district,
        county,
        count(*) as transaction_count,
        avg(price) as avg_price,
        median(price) as median_price,
        min(price) as min_price,
        max(price) as max_price
    from filtered
    group by
        date_trunc('month', date_of_transfer),
        district,
        county
),

with_index as (
    select
        *,
        lag(avg_price, 1) over (
            partition by district
            order by transfer_month
        ) as prev_month_avg_price,

        round(
            (avg_price - lag(avg_price, 1) over (
                partition by district
                order by transfer_month
            )) / nullif(lag(avg_price, 1) over (
                partition by district
                order by transfer_month
            ), 0) * 100
        , 2) as mom_change_pct,

        avg(avg_price) over (
            partition by district
            order by transfer_month
            rows between 2 preceding and current row
        ) as rolling_3m_avg_price

    from monthly_prices
)

select * from with_index