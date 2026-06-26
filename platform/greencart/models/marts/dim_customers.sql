with customers as (
    select * from {{ ref('stg_customers') }}
),

summary as (
    select * from {{ ref('int_customer_orders_summary') }}
),

final as (
    select
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.country,
        c.currency,
        c.city,
        c.registered_at,
        c.is_active,

        -- Order behaviour
        coalesce(s.total_orders, 0) as total_orders,
        coalesce(s.delivered_orders, 0) as delivered_orders,
        coalesce(s.cancelled_orders, 0) as cancelled_orders,
        coalesce(s.total_revenue, 0) as total_revenue,
        s.avg_order_value,
        s.first_order_at,
        s.last_order_at,
        coalesce(s.is_repeat_buyer, false) as is_repeat_buyer,
        s.days_between_first_and_last_order,

        -- Customer segment
        case
            when coalesce(s.total_orders, 0) = 0 then 'no_orders'
            when s.is_repeat_buyer = true
             and coalesce(s.total_revenue, 0) >= 500 then 'high_value'
            when s.is_repeat_buyer = true then 'repeat'
            else 'one_time'
        end as customer_segment

    from customers c
    left join summary s
        on c.customer_id = s.customer_id
)

select * from final
