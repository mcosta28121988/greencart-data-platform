WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

order_lines AS (
    SELECT * FROM {{ ref('stg_order_lines') }}
),

customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

order_totals AS (
    SELECT
        order_id,
        SUM(line_total) AS order_total,
        SUM(quantity) AS total_items,
        COUNT(order_line_id) AS total_lines
    FROM order_lines
    GROUP BY ALL
),

enriched AS (
    SELECT
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
        c.registered_at AS customer_registered_at,

        -- Derived order metrics
        ot.order_total,
        ot.total_items,
        ot.total_lines,

        -- Delivery metrics
        CASE
            WHEN o.delivered_at IS NOT NULL
                THEN DATEDIFF('day', o.placed_at, o.delivered_at)
        END AS days_to_deliver,

        -- Customer tenure at time of order
        DATEDIFF('day', c.registered_at, o.placed_at) AS days_since_registration

    FROM orders AS o
    LEFT JOIN customers AS c
        ON o.customer_id = c.customer_id
    LEFT JOIN order_totals AS ot
        ON o.order_id = ot.order_id
)

SELECT * FROM enriched
