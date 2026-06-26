with orders as (
    select * from {{ ref('fct_orders') }}
    where status = 'delivered'
),

daily as (
    select
        placed_date as date,
        country,
        currency,
        primary_category,

        count(order_id) as total_orders,
        sum(order_total) as total_revenue,
        avg(order_total) as avg_order_value,
        sum(total_items) as total_items_sold,
        avg(days_to_deliver) as avg_days_to_deliver

    from orders
    group by
        placed_date,
        country,
        currency,
        primary_category
)

select * from daily
