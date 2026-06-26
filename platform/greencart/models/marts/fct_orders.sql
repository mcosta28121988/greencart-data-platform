with orders as (
    select * from {{ ref('int_orders_enriched') }}
),

order_lines as (
    select * from {{ ref('stg_order_lines') }}
),

-- Top category per order by revenue
top_category as (
    select
        order_id,
        category,
        sum(line_total) as category_revenue,
        row_number() over (
            partition by order_id
            order by sum(line_total) desc
        ) as rn
    from order_lines
    group by order_id, category
),

final as (
    select
        o.order_id,
        o.customer_id,
        o.country,
        o.currency,
        o.status,
        o.placed_at,
        o.delivered_at,
        o.days_to_deliver,
        o.days_since_registration,
        o.order_total,
        o.total_items,
        o.total_lines,

        -- Date dimensions
        date_trunc('day', o.placed_at) as placed_date,
        date_trunc('week', o.placed_at) as placed_week,
        date_trunc('month', o.placed_at) as placed_month,
        dayofweek(o.placed_at) as placed_day_of_week,
        month(o.placed_at) as placed_month_number,
        year(o.placed_at) as placed_year,

        -- Top category for this order
        tc.category as primary_category

    from orders o
    left join top_category tc
        on o.order_id = tc.order_id
        and tc.rn = 1
)

select * from final
