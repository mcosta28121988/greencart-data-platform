WITH source AS (
    SELECT * FROM {{ source('greencart_raw', 'ORDER_LINES') }}
),

renamed AS (
    SELECT
        order_line_id,
        order_id,
        product_id,
        product_name,
        category,
        quantity::integer AS quantity,
        unit_price::float AS unit_price,
        line_total::float AS line_total
    FROM source
)

SELECT * FROM renamed
