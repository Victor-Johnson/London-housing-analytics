with source as (
    select * from {{ source('main', 'raw_rents') }}
),

-- ONS and Land Registry name a handful of unitary authorities differently
-- (word order, punctuation, or a dropped "City of" prefix). Verified by
-- diffing against dim_location — this is the full set of mismatches, not a
-- guess. "Telford and Wrekin" has no Land Registry equivalent at all; the
-- source data itself only ever uses "Wrekin" for that authority's sales.
district_overrides as (
    select * from (values
        ('BRISTOL, CITY OF',           'CITY OF BRISTOL'),
        ('DERBY',                      'CITY OF DERBY'),
        ('HEREFORDSHIRE, COUNTY OF',   'HEREFORDSHIRE'),
        ('KINGSTON UPON HULL, CITY OF','CITY OF KINGSTON UPON HULL'),
        ('NOTTINGHAM',                 'CITY OF NOTTINGHAM'),
        ('PETERBOROUGH',               'CITY OF PETERBOROUGH'),
        ('PLYMOUTH',                   'CITY OF PLYMOUTH'),
        ('RHONDDA CYNON TAF',          'RHONDDA CYNON TAFF'),
        ('ST. HELENS',                 'ST HELENS'),
        ('TELFORD AND WREKIN',         'WREKIN'),
        ('VALE OF GLAMORGAN',          'THE VALE OF GLAMORGAN'),
        ('WESTMINSTER',                'CITY OF WESTMINSTER')
    ) as t(ons_name, land_registry_name)
),

cleaned as (
    select
        "Time period"       as time_period,
        "Area code"         as area_code,
        coalesce(ov.land_registry_name, upper(source."Area name")) as district,
        "Region or country name" as region_name,

        "Rental price"                    as rental_price,
        "Rental price one bed"            as rental_price_one_bed,
        "Rental price two bed"            as rental_price_two_bed,
        "Rental price three bed"          as rental_price_three_bed,
        "Rental price four or more bed"   as rental_price_four_or_more_bed,
        "Rental price detached"           as rental_price_detached,
        "Rental price semidetached"       as rental_price_semi_detached,
        "Rental price terraced"           as rental_price_terraced,
        "Rental price flat maisonette"    as rental_price_flat_maisonette,

        _source_file,
        _loaded_at

    from source
    left join district_overrides ov on upper(source."Area name") = ov.ons_name
)

select * from cleaned
