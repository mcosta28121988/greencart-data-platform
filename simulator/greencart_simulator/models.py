from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Customer:
    """
    Represents a registered GreenCart customer.
    One customer belongs to one country for their lifetime.
    """
    customer_id: str
    first_name: str
    last_name: str
    email: str
    country: str
    currency: str
    city: str
    registered_at: datetime
    is_active: bool = True


@dataclass
class Product:
    """
    Represents a product in the GreenCart sustainable catalogue.
    Price is stored in USD — converted at order time by country.
    """
    product_id: str
    name: str
    category: str
    base_price_usd: float
    is_active: bool = True


@dataclass
class Order:
    """
    Represents a customer purchase event — the order header.
    Grain: one row per order.

    order_total is intentionally excluded here. It is derived
    from order_lines in the transformation layer rather than
    stored in the raw source. The raw layer carries facts,
    the warehouse layer carries derived metrics.
    """
    order_id: str
    customer_id: str
    country: str
    currency: str
    status: str                      # delivered, cancelled
    placed_at: datetime
    delivered_at: Optional[datetime] = None


@dataclass
class OrderLine:
    """
    Represents a single product line within an order.
    Grain: one row per product per order.

    This is the fact table that connects orders to products.
    Revenue, item counts and category breakdowns are all
    derived from this table in the transformation layer.
    """
    order_line_id: str
    order_id: str
    product_id: str
    product_name: str
    category: str
    quantity: int
    unit_price: float                # in local currency
    line_total: float                # quantity * unit_price


@dataclass
class Payment:
    """
    Represents the payment record for a delivered order.
    Cancelled orders do not generate a payment.
    """
    payment_id: str
    order_id: str
    customer_id: str
    amount: float                    # matches sum of order_lines.line_total
    currency: str
    payment_method: str              # credit_card, debit_card, paypal
    paid_at: datetime
    status: str                      # completed, refunded
