WITH orders AS (
    SELECT * FROM {{ ref('int_orders_enriched') }}
),

summary AS (
    SELECT
        customer_id,
        country,
        currency,
        city,
        customer_registered_at,

        COUNT(order_id) AS total_orders,
        COUNT(
            CASE
                WHEN status = 'delivered'
                    THEN order_id
            END
        ) AS delivered_orders,
        COUNT(
            CASE
                WHEN status = 'cancelled'
                    THEN order_id
            END
        ) AS cancelled_orders,

        SUM(
            CASE
                WHEN status = 'delivered'
                    THEN order_total
                ELSE 0
            END
        ) AS total_revenue,

        AVG(
            CASE
                WHEN status = 'delivered'
                    THEN order_total
            END
        ) AS avg_order_value,

        MIN(placed_at) AS first_order_at,
        MAX(placed_at) AS last_order_at,

        -- Repeat buyer flag
        COALESCE(COUNT(order_id) > 1, FALSE) AS is_repeat_buyer,

        -- Days between first and last order
        CASE
            WHEN COUNT(order_id) > 1
                THEN DATEDIFF('day', MIN(placed_at), MAX(placed_at))
        END AS days_between_first_and_last_order

    FROM orders
    GROUP BY ALL
)

SELECT * FROM summary
