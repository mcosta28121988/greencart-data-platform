with source as (
    select * from {{ source('greencart_raw', 'PAYMENTS') }}
),

renamed as (
    select
        PAYMENT_ID                              as payment_id,
        ORDER_ID                                as order_id,
        CUSTOMER_ID                             as customer_id,
        AMOUNT::float                           as amount,
        CURRENCY                                as currency,
        LOWER(PAYMENT_METHOD)                   as payment_method,
        PAID_AT::timestamp_ntz                  as paid_at,
        LOWER(STATUS)                           as status
    from source
)

select * from renamed
