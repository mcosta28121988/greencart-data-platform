WITH source AS (
    SELECT * FROM {{ source('greencart_raw', 'ORDERS') }}
),

renamed AS (
    SELECT
        order_id,
        customer_id,
        country,
        currency,
        placed_at::timestamp_ntz AS placed_at,
        delivered_at::timestamp_ntz AS delivered_at,
        LOWER(status) AS status
    FROM source
)

SELECT * FROM renamed
