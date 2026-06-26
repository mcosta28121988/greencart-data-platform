WITH orders AS (
    SELECT * FROM {{ ref('fct_orders') }}
    WHERE status = 'delivered'
),

daily AS (
    SELECT
        placed_date AS date,
        country,
        currency,
        primary_category,

        COUNT(order_id) AS total_orders,
        SUM(order_total) AS total_revenue,
        AVG(order_total) AS avg_order_value,
        SUM(total_items) AS total_items_sold,
        AVG(days_to_deliver) AS avg_days_to_deliver

    FROM orders
    GROUP BY
        placed_date,
        country,
        currency,
        primary_category
)

SELECT * FROM daily
