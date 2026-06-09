
with source as (
    select * from {{ source('main', 'raw_transactions') }}
),

cleaned as (
    select
        transaction_id,
        price,

-- cast timestamp to date
cast(date_of_transfer as date) as date_of_transfer,
postcode,

-- readable property type
case property_type
    when 'D' then 'detached'
    when 'S' then 'semi_detached'
    when 'T' then 'terraced'
    when 'F' then 'flat_maisonette'
    when 'O' then 'other'
    else 'unknown'
end as property_type,
case old_new
    when 'Y' then 'new_build'
    when 'N' then 'established'
    else 'unknown'
end as new_build_flag,
case duration
    when 'F' then 'freehold'
    when 'L' then 'leasehold'
    else 'unknown'
end as tenure,

-- flag records with missing postcodes for downstream filtering
case
    when postcode is null
    and ppd_category_type = 'B' then 'bulk_transfer'
    when postcode is null then 'missing_postcode'
    else 'valid'
end as postcode_quality_flag,

-- building clean address
trim(
    coalesce(saon || ' ', '') || coalesce(paon || ' ', '') || coalesce(street, '')
) as address_line,
town_city,
district,
county,
ppd_category_type,
record_status,

-- flag non-market transfers 
case
            when price <= 1    then true
            when ppd_category_type = 'B' then true
            else false
        end as is_non_market_transfer,

        _source_file,
        _loaded_at

    from source
)

select * from cleaned