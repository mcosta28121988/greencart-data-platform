with source as (
    select * from {{ source('greencart_raw', 'CUSTOMERS') }}
),

renamed as (
    select
        CUSTOMER_ID                             as customer_id,
        FIRST_NAME                              as first_name,
        LAST_NAME                               as last_name,
        LOWER(EMAIL)                            as email,
        COUNTRY                                 as country,
        CURRENCY                                as currency,
        CITY                                    as city,
        REGISTERED_AT::timestamp_ntz            as registered_at,
        IS_ACTIVE::boolean                      as is_active
    from source
)

select * from renamed