with orders as (
    select * from {{ ref('stg_orders') }}
),

order_lines as (
    select * from {{ ref('stg_order_lines') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

order_totals as (
    select
        order_id,
        sum(line_total) as order_total,
        sum(quantity) as total_items,
        count(order_line_id) as total_lines
    from order_lines
    group by all
),

enriched as (
    select
        o.order_id,
        o.customer_id,
        o.country,
        o.currency,
        o.status,
        o.placed_at,
        o.delivered_at,

        -- Customer context
        c.first_name,
        c.last_name,
        c.city,
        c.registered_at as customer_registered_at,

        -- Derived order metrics
        ot.order_total,
        ot.total_items,
        ot.total_lines,

        -- Delivery metrics
        case
            when o.delivered_at is not null
            then datediff('day', o.placed_at, o.delivered_at)
        end as days_to_deliver,

        -- Customer tenure at time of order
        datediff('day', c.registered_at, o.placed_at) as days_since_registration

    from orders o
    left join customers c
        on o.customer_id = c.customer_id
    left join order_totals ot
        on o.order_id = ot.order_id
)

select * from enriched
