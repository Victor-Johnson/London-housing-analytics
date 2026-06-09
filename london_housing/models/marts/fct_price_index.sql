
with source as (
    select * from {{ ref('int_price_index') }}
),

final as (
    select
        transfer_month,
        district,
        county,
        transaction_count,
        avg_price,
        median_price,
        min_price,
        max_price,
        prev_month_avg_price,
        mom_change_pct,
        rolling_3m_avg_price,

        case
            when mom_change_pct > 15  then 'rising'
            when mom_change_pct < -15 then 'falling'
            when mom_change_pct is null then 'insufficient_data'
            else 'stable'
        end as price_trend

    from source
)

select * from final