with source as (
    select * from {{ source('greencart_raw', 'ORDER_LINES') }}
),

renamed as (
    select
        ORDER_LINE_ID as order_line_id,
        ORDER_ID as order_id,
        PRODUCT_ID as product_id,
        PRODUCT_NAME as product_name,
        CATEGORY as category,
        QUANTITY::integer as quantity,
        UNIT_PRICE::float as unit_price,
        LINE_TOTAL::float as line_total
    from source
)

select * from renamed
