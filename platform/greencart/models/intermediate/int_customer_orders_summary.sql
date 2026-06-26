with orders as (
    select * from {{ ref('int_orders_enriched') }}
),

summary as (
    select
        customer_id,
        country,
        currency,
        city,
        customer_registered_at,
        
        count(order_id) as total_orders,
        count(
            case when status = 'delivered'
            then order_id end
        ) as delivered_orders,
        count(
            case when status = 'cancelled'
            then order_id end
        ) as cancelled_orders,

        sum(
            case when status = 'delivered'
            then order_total else 0 end
        ) as total_revenue,

        avg(
            case when status = 'delivered'
            then order_total end
        ) as avg_order_value,

        min(placed_at) as first_order_at,
        max(placed_at) as last_order_at,

        -- Repeat buyer flag
        case
            when count(order_id) > 1 then true
            else false
        end as is_repeat_buyer,

        -- Days between first and last order
        case
            when count(order_id) > 1
            then datediff('day', min(placed_at), max(placed_at))
        end as days_between_first_and_last_order

    from orders
    group by all
)

select * from summary
