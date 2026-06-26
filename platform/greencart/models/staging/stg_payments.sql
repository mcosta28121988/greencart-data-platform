WITH source AS (
    SELECT * FROM {{ source('greencart_raw', 'PAYMENTS') }}
),

renamed AS (
    SELECT
        payment_id,
        order_id,
        customer_id,
        amount::float AS amount,
        currency,
        paid_at::timestamp_ntz AS paid_at,
        LOWER(payment_method) AS payment_method,
        LOWER(status) AS status
    FROM source
)

SELECT * FROM renamed
