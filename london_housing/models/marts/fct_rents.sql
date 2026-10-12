with source as (
    select * from {{ ref('int_rents_enriched') }}
),

fct_rents as (
    select
        time_period,
        district,
        region_name,
        rental_price,
        rental_price_one_bed,
        rental_price_two_bed,
        rental_price_three_bed,
        rental_price_four_or_more_bed,
        mom_change_pct
    from source
)

select * from fct_rents
