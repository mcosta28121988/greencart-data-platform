from dataclasses import dataclass, field
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
    Represents a customer purchase event.
    Grain: one row per order.
    order_total is in the customer's local currency.
    """
    order_id: str
    customer_id: str
    country: str
    currency: str
    status: str                  # placed, delivered, cancelled
    order_total: float
    num_items: int
    placed_at: datetime
    delivered_at: Optional[datetime] = None


@dataclass
class Payment:
    """
    Represents the payment record for a placed or delivered order.
    Cancelled orders do not generate a payment.
    """
    payment_id: str
    order_id: str
    customer_id: str
    amount: float
    currency: str
    payment_method: str          # credit_card, debit_card, paypal
    paid_at: datetime
    status: str                  # completed, refunded