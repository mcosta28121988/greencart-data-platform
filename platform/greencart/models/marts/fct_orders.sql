WITH orders AS (
    SELECT * FROM {{ ref('int_orders_enriched') }}
),

order_lines AS (
    SELECT * FROM {{ ref('stg_order_lines') }}
),

-- Top category per order by revenue
top_category AS (
    SELECT
        order_id,
        category,
        SUM(line_total) AS category_revenue,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY SUM(line_total) DESC
        ) AS rn
    FROM order_lines
    GROUP BY order_id, category
),

final AS (
    SELECT
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
        tc.category AS primary_category,
        DATE_TRUNC('day', o.placed_at) AS placed_date,
        DATE_TRUNC('week', o.placed_at) AS placed_week,
        DATE_TRUNC('month', o.placed_at) AS placed_month,
        DAYOFWEEK(o.placed_at) AS placed_day_of_week,
        MONTH(o.placed_at) AS placed_month_number,

        -- Top category for this order
        YEAR(o.placed_at) AS placed_year

    FROM orders AS o
    LEFT JOIN top_category AS tc
        ON
            o.order_id = tc.order_id
            AND tc.rn = 1
)

SELECT * FROM final
