with source as (
    select * from {{ source('greencart_raw', 'ORDERS') }}
),

renamed as (
    select
        ORDER_ID                                as order_id,
        CUSTOMER_ID                             as customer_id,
        COUNTRY                                 as country,
        CURRENCY                                as currency,
        LOWER(STATUS)                           as status,
        PLACED_AT::timestamp_ntz                as placed_at,
        DELIVERED_AT::timestamp_ntz             as delivered_at
    from source
)

select * from renamed
