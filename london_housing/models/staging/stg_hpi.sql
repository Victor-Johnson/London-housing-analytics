
with source as (
    select * from {{ source('main', 'raw_hpi') }}
),

cleaned as (
    select
        "Date"          as date,
        "RegionName"    as region_name,
        "AreaCode"      as area_code,
        "AveragePrice"  as average_price,
        "Index"         as price_index,
        "IndexSA"       as price_index_sa,
        "1m%Change"     as change_1m_pct,
        "12m%Change"    as change_12m_pct,
        "SalesVolume"   as sales_volume,

-- property type breakdowns
"DetachedPrice" as detached_price,
"SemiDetachedPrice" as semi_detached_price,
"TerracedPrice" as terraced_price,
"FlatPrice" as flat_price,

-- buyer type
"FTBPrice" as first_time_buyer_price,
"FOOPrice" as former_owner_occupier_price,

-- transaction type
"CashPrice"      as cash_price,
        "MortgagePrice"  as mortgage_price,
        "NewPrice"       as new_build_price,
        "OldPrice"       as established_price,

        _source_file,
        _loaded_at

    from source
)

select * from cleaned