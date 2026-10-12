with source as (
    select * from {{ ref('stg_rents') }}
),

filtered as (
    select * from source
    where district is not null
    and rental_price is not null
),

with_trend as (
    select
        *,

        lag(rental_price, 1) over (
            partition by district
            order by time_period
        ) as prev_month_rental_price,

        round(
            (rental_price - lag(rental_price, 1) over (
                partition by district
                order by time_period
            )) / nullif(lag(rental_price, 1) over (
                partition by district
                order by time_period
            ), 0) * 100
        , 2) as mom_change_pct

    from filtered
)

select * from with_trend
