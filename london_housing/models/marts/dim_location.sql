
with source as (
    select * from {{ ref('stg_transactions') }}
),

locations as (
    select distinct
        district,
        county,
        town_city
    from source
    where district is not null
)

select * from locations
order by district