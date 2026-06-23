import uuid
import random
from datetime import datetime, timedelta
from faker import Faker

from .config import SimulatorConfig, CURRENCY_MAP
from .models import Customer, Product, Order, Payment


EXCHANGE_RATES = {
    "AUD": 1.52,
    "USD": 1.00,
    "GBP": 0.79,
}

PRODUCT_CATALOGUE = [
    ("Reusable Water Bottle", "Kitchen"),
    ("Bamboo Toothbrush Set", "Personal Care"),
    ("Organic Cotton Tote Bag", "Accessories"),
    ("Solar Phone Charger", "Electronics"),
    ("Beeswax Food Wraps", "Kitchen"),
    ("Recycled Notebook", "Stationery"),
    ("Natural Soy Candle", "Home"),
    ("Compostable Phone Case", "Electronics"),
    ("Hemp Backpack", "Accessories"),
    ("Zero Waste Starter Kit", "Home"),
    ("Organic Lip Balm", "Personal Care"),
    ("Stainless Steel Straw Set", "Kitchen"),
    ("Upcycled Denim Wallet", "Accessories"),
    ("Bamboo Cutting Board", "Kitchen"),
    ("Natural Rubber Yoga Mat", "Fitness"),
    ("Organic Cotton Socks", "Clothing"),
    ("Recycled Plastic Sunglasses", "Accessories"),
    ("Wooden Phone Stand", "Electronics"),
    ("Biodegradable Soap Bar", "Personal Care"),
    ("Cork Yoga Block", "Fitness"),
]


class CustomerGenerator:
    def __init__(self, config: SimulatorConfig):
        self.config = config
        self.faker_instances = {
            "AU": Faker("en_AU"),
            "US": Faker("en_US"),
            "UK": Faker("en_GB"),
        }
        random.seed(config.seed)
        for faker in self.faker_instances.values():
            faker.seed_instance(config.seed)

    def generate(self) -> list[Customer]:
        customers = []
        # Distribute customers across countries
        per_country = self.config.num_customers // len(self.config.countries)

        for country in self.config.countries:
            faker = self.faker_instances[country]
            currency = CURRENCY_MAP[country]

            for _ in range(per_country):
                registered_at = datetime(2023, 1, 1) + timedelta(
                    days=random.randint(0, self.config.num_days)
                )
                customers.append(Customer(
                    customer_id=str(uuid.uuid4()),
                    first_name=faker.first_name(),
                    last_name=faker.last_name(),
                    email=faker.email(),
                    country=country,
                    currency=currency,
                    city=faker.city(),
                    registered_at=registered_at,
                ))

        return customers


class ProductGenerator:
    def __init__(self, config: SimulatorConfig):
        self.config = config
        random.seed(config.seed)

    def generate(self) -> list[Product]:
        products = []
        catalogue = PRODUCT_CATALOGUE * (
            self.config.num_products // len(PRODUCT_CATALOGUE) + 1
        )

        for i in range(self.config.num_products):
            name, category = catalogue[i]
            products.append(Product(
                product_id=str(uuid.uuid4()),
                name=name,
                category=category,
                base_price_usd=round(random.uniform(5.0, 120.0), 2),
            ))

        return products


class OrderGenerator:
    def __init__(self, config: SimulatorConfig):
        self.config = config
        random.seed(config.seed)

    def generate(
        self,
        customers: list[Customer],
        products: list[Product],
    ) -> list[Order]:
        orders = []
        start_date = datetime(2023, 1, 1)

        for customer in customers:
            # Every customer places at least one order
            num_orders = 1
            if random.random() < self.config.repeat_purchase_rate:
                num_orders = random.randint(2, 6)

            for _ in range(num_orders):
                placed_at = start_date + timedelta(
                    days=random.randint(0, self.config.num_days)
                )
                # Order must be after customer registered
                if placed_at < customer.registered_at:
                    placed_at = customer.registered_at + timedelta(
                        days=random.randint(1, 30)
                    )

                num_items = random.randint(1, 5)
                selected = random.choices(products, k=num_items)
                rate = EXCHANGE_RATES[customer.currency]
                order_total = round(
                    sum(p.base_price_usd * rate for p in selected), 2
                )

                is_cancelled = random.random() < self.config.cancellation_rate
                status = "cancelled" if is_cancelled else "delivered"
                delivered_at = None
                if not is_cancelled:
                    delivered_at = placed_at + timedelta(
                        days=random.randint(2, 14)
                    )

                orders.append(Order(
                    order_id=str(uuid.uuid4()),
                    customer_id=customer.customer_id,
                    country=customer.country,
                    currency=customer.currency,
                    status=status,
                    order_total=order_total,
                    num_items=num_items,
                    placed_at=placed_at,
                    delivered_at=delivered_at,
                ))

        return orders


class PaymentGenerator:
    def __init__(self, config: SimulatorConfig):
        self.config = config
        random.seed(config.seed)

    def generate(self, orders: list[Order]) -> list[Payment]:
        payments = []
        methods = ["credit_card", "debit_card", "paypal"]

        for order in orders:
            # Cancelled orders do not generate payments
            if order.status == "cancelled":
                continue

            payments.append(Payment(
                payment_id=str(uuid.uuid4()),
                order_id=order.order_id,
                customer_id=order.customer_id,
                amount=order.order_total,
                currency=order.currency,
                payment_method=random.choice(methods),
                paid_at=order.placed_at,
                status="completed",
            ))

        return payments