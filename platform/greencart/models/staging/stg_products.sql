with source as (
    select * from {{ source('greencart_raw', 'PRODUCTS') }}
),

renamed as (
    select
        PRODUCT_ID                              as product_id,
        NAME                                    as product_name,
        CATEGORY                                as category,
        BASE_PRICE_USD::float                   as base_price_usd,
        IS_ACTIVE::boolean                      as is_active
    from source
)

select * from renamed
