with source as (
    SELECT * FROM {{ ref('stg_transactions')}}
),

properties_table AS (
    SELECT DISTINCT
        property_type,
        tenure,
        new_build_flag
    from source 
    WHERE property_type IS NOT NULL 
)

SELECT * FROM properties_table
ORDER BY property_type