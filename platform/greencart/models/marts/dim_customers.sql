WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

summary AS (
    SELECT * FROM {{ ref('int_customer_orders_summary') }}
),

final AS (
    SELECT
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
        s.avg_order_value,
        s.first_order_at,
        s.last_order_at,
        s.days_between_first_and_last_order,
        COALESCE(s.total_orders, 0) AS total_orders,
        COALESCE(s.delivered_orders, 0) AS delivered_orders,
        COALESCE(s.cancelled_orders, 0) AS cancelled_orders,
        COALESCE(s.total_revenue, 0) AS total_revenue,
        COALESCE(s.is_repeat_buyer, FALSE) AS is_repeat_buyer,

        -- Customer segment
        CASE
            WHEN COALESCE(s.total_orders, 0) = 0 THEN 'no_orders'
            WHEN
                s.is_repeat_buyer = TRUE
                AND COALESCE(s.total_revenue, 0) >= 500 THEN 'high_value'
            WHEN s.is_repeat_buyer = TRUE THEN 'repeat'
            ELSE 'one_time'
        END AS customer_segment

    FROM customers AS c
    LEFT JOIN summary AS s
        ON c.customer_id = s.customer_id
)

SELECT * FROM final
