import uuid
import math
import random
from datetime import datetime, timedelta
from faker import Faker

from .config import SimulatorConfig, CURRENCY_MAP
from .models import Customer, Product, Order, OrderLine, Payment


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


def seeded_uuid(rng: random.Random) -> str:
    return str(uuid.UUID(int=rng.getrandbits(128), version=4))


def _day_weight(date: datetime) -> float:
    day_of_year = date.timetuple().tm_yday
    seasonal = 1.0 + 0.4 * math.sin(math.pi * (day_of_year - 80) / 365)
    black_friday_distance = abs(day_of_year - 330)
    black_friday = 1.0 + 3.0 * math.exp(-0.5 * (black_friday_distance ** 2) / 25)
    weekend = 1.15 if date.weekday() >= 5 else 1.0
    return seasonal * black_friday * weekend


def _sample_date(rng: random.Random, start: datetime, num_days: int) -> datetime:
    dates = [start + timedelta(days=i) for i in range(num_days)]
    weights = [_day_weight(d) for d in dates]
    return rng.choices(dates, weights=weights, k=1)[0]


class CustomerGenerator:
    def __init__(self, config: SimulatorConfig):
        self.config = config
        self.rng = random.Random(config.seed)
        self.faker_instances = {
            "AU": Faker("en_AU"),
            "US": Faker("en_US"),
            "UK": Faker("en_GB"),
        }
        for faker in self.faker_instances.values():
            faker.seed_instance(config.seed)

    def generate(self) -> list[Customer]:
        customers = []
        per_country = self.config.num_customers // len(self.config.countries)
        used_emails: set[str] = set()

        for country in self.config.countries:
            faker = self.faker_instances[country]
            currency = CURRENCY_MAP[country]

            for _ in range(per_country):
                registered_at = _sample_date(
                    self.rng, datetime(2023, 1, 1), self.config.num_days
                )
                email = faker.email()
                while email in used_emails:
                    email = faker.email()
                used_emails.add(email)

                customers.append(Customer(
                    customer_id=seeded_uuid(self.rng),
                    first_name=faker.first_name(),
                    last_name=faker.last_name(),
                    email=email,
                    country=country,
                    currency=currency,
                    city=faker.city(),
                    registered_at=registered_at,
                ))

        return customers


class ProductGenerator:
    def __init__(self, config: SimulatorConfig):
        self.config = config
        self.rng = random.Random(config.seed)

    def generate(self) -> list[Product]:
        products = []
        catalogue = PRODUCT_CATALOGUE * (
            self.config.num_products // len(PRODUCT_CATALOGUE) + 1
        )
        for i in range(self.config.num_products):
            name, category = catalogue[i]
            products.append(Product(
                product_id=seeded_uuid(self.rng),
                name=name,
                category=category,
                base_price_usd=round(self.rng.uniform(5.0, 120.0), 2),
            ))
        return products


class OrderGenerator:
    def __init__(self, config: SimulatorConfig):
        self.config = config
        self.rng = random.Random(config.seed)

    def generate(
        self,
        customers: list[Customer],
        products: list[Product],
    ) -> tuple[list[Order], list[OrderLine]]:
        orders = []
        order_lines = []
        start_date = datetime(2023, 1, 1)

        for customer in customers:
            num_orders = 1
            if self.rng.random() < self.config.repeat_purchase_rate:
                num_orders = self.rng.randint(2, 6)

            for _ in range(num_orders):
                placed_at = _sample_date(self.rng, start_date, self.config.num_days)

                if placed_at < customer.registered_at:
                    placed_at = customer.registered_at + timedelta(
                        days=self.rng.randint(1, 30)
                    )

                is_cancelled = self.rng.random() < self.config.cancellation_rate
                status = "cancelled" if is_cancelled else "delivered"
                delivered_at = None
                if not is_cancelled:
                    delivered_at = placed_at + timedelta(days=self.rng.randint(2, 14))

                order_id = seeded_uuid(self.rng)
                rate = EXCHANGE_RATES[customer.currency]
                num_lines = self.rng.randint(1, 5)
                selected_products = self.rng.choices(products, k=num_lines)

                for product in selected_products:
                    quantity = self.rng.randint(1, 3)
                    unit_price = round(product.base_price_usd * rate, 2)
                    line_total = round(unit_price * quantity, 2)

                    order_lines.append(OrderLine(
                        order_line_id=seeded_uuid(self.rng),
                        order_id=order_id,
                        product_id=product.product_id,
                        product_name=product.name,
                        category=product.category,
                        quantity=quantity,
                        unit_price=unit_price,
                        line_total=line_total,
                    ))

                orders.append(Order(
                    order_id=order_id,
                    customer_id=customer.customer_id,
                    country=customer.country,
                    currency=customer.currency,
                    status=status,
                    placed_at=placed_at,
                    delivered_at=delivered_at,
                ))

        return orders, order_lines


class PaymentGenerator:
    def __init__(self, config: SimulatorConfig):
        self.config = config
        self.rng = random.Random(config.seed)

    def generate(
        self,
        orders: list[Order],
        order_lines: list[OrderLine],
    ) -> list[Payment]:
        payments = []
        methods = ["credit_card", "debit_card", "paypal"]

        order_totals: dict[str, float] = {}
        for line in order_lines:
            order_totals[line.order_id] = round(
                order_totals.get(line.order_id, 0.0) + line.line_total, 2
            )

        for order in orders:
            if order.status == "cancelled":
                continue

            payments.append(Payment(
                payment_id=seeded_uuid(self.rng),
                order_id=order.order_id,
                customer_id=order.customer_id,
                amount=order_totals.get(order.order_id, 0.0),
                currency=order.currency,
                payment_method=self.rng.choice(methods),
                paid_at=order.placed_at,
                status="completed",
            ))

        return payments
