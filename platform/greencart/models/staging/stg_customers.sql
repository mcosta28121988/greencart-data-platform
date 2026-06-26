WITH source AS (
    SELECT * FROM {{ source('greencart_raw', 'CUSTOMERS') }}
),

renamed AS (
    SELECT
        customer_id,
        first_name,
        last_name,
        country,
        currency,
        city,
        registered_at::timestamp_ntz AS registered_at,
        is_active::boolean AS is_active,
        LOWER(email) AS email
    FROM source
)

SELECT * FROM renamed
