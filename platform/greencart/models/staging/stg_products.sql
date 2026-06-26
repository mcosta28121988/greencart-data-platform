WITH source AS (
    SELECT * FROM {{ source('greencart_raw', 'PRODUCTS') }}
),

renamed AS (
    SELECT
        product_id,
        name AS product_name,
        category,
        base_price_usd::float AS base_price_usd,
        is_active::boolean AS is_active
    FROM source
)

SELECT * FROM renamed
