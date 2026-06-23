import pytest
from greencart_simulator.config import SimulatorConfig
from greencart_simulator.generators import (
    CustomerGenerator,
    ProductGenerator,
    OrderGenerator,
    PaymentGenerator,
)


@pytest.fixture
def config():
    return SimulatorConfig(num_customers=99, num_products=20, num_days=90)


@pytest.fixture
def products(config):
    return ProductGenerator(config).generate()


@pytest.fixture
def customers(config):
    return CustomerGenerator(config).generate()


@pytest.fixture
def orders(config, customers, products):
    return OrderGenerator(config).generate(customers, products)


@pytest.fixture
def payments(config, orders):
    return PaymentGenerator(config).generate(orders)


class TestCustomerGenerator:
    def test_customer_count(self, customers, config):
        expected = (config.num_customers // 3) * 3
        assert len(customers) == expected

    def test_valid_countries(self, customers):
        valid = {"AU", "US", "UK"}
        assert all(c.country in valid for c in customers)

    def test_currency_matches_country(self, customers):
        mapping = {"AU": "AUD", "US": "USD", "UK": "GBP"}
        assert all(c.currency == mapping[c.country] for c in customers)

    def test_no_duplicate_emails(self, customers):
        emails = [c.email for c in customers]
        assert len(emails) == len(set(emails))

    def test_no_duplicate_ids(self, customers):
        ids = [c.customer_id for c in customers]
        assert len(ids) == len(set(ids))

    def test_registered_at_within_range(self, customers, config):
        from datetime import datetime
        start = datetime(2023, 1, 1)
        for c in customers:
            assert c.registered_at >= start


class TestProductGenerator:
    def test_product_count(self, products, config):
        assert len(products) == config.num_products

    def test_price_is_positive(self, products):
        assert all(p.base_price_usd > 0 for p in products)

    def test_price_within_range(self, products):
        assert all(5.0 <= p.base_price_usd <= 120.0 for p in products)

    def test_no_duplicate_ids(self, products):
        ids = [p.product_id for p in products]
        assert len(ids) == len(set(ids))

    def test_all_products_active(self, products):
        assert all(p.is_active for p in products)


class TestOrderGenerator:
    def test_all_customers_have_at_least_one_order(self, customers, orders):
        customer_ids_with_orders = {o.customer_id for o in orders}
        all_customer_ids = {c.customer_id for c in customers}
        assert all_customer_ids == customer_ids_with_orders

    def test_valid_statuses(self, orders):
        valid = {"placed", "delivered", "cancelled"}
        assert all(o.status in valid for o in orders)

    def test_order_total_is_positive(self, orders):
        assert all(o.order_total > 0 for o in orders)

    def test_num_items_is_positive(self, orders):
        assert all(o.num_items > 0 for o in orders)

    def test_no_duplicate_ids(self, orders):
        ids = [o.order_id for o in orders]
        assert len(ids) == len(set(ids))

    def test_delivered_orders_have_delivery_date(self, orders):
        for o in orders:
            if o.status == "delivered":
                assert o.delivered_at is not None

    def test_cancelled_orders_have_no_delivery_date(self, orders):
        for o in orders:
            if o.status == "cancelled":
                assert o.delivered_at is None

    def test_delivery_after_placement(self, orders):
        for o in orders:
            if o.delivered_at:
                assert o.delivered_at > o.placed_at

    def test_order_placed_after_customer_registered(self, customers, orders):
        reg_map = {c.customer_id: c.registered_at for c in customers}
        for o in orders:
            assert o.placed_at >= reg_map[o.customer_id]


class TestPaymentGenerator:
    def test_cancelled_orders_have_no_payment(self, orders, payments):
        cancelled_ids = {o.order_id for o in orders if o.status == "cancelled"}
        payment_order_ids = {p.order_id for p in payments}
        assert cancelled_ids.isdisjoint(payment_order_ids)

    def test_payment_amount_matches_order(self, orders, payments):
        order_totals = {o.order_id: o.order_total for o in orders}
        for p in payments:
            assert p.amount == order_totals[p.order_id]

    def test_valid_payment_methods(self, payments):
        valid = {"credit_card", "debit_card", "paypal"}
        assert all(p.payment_method in valid for p in payments)

    def test_valid_statuses(self, payments):
        valid = {"completed", "refunded"}
        assert all(p.status in valid for p in payments)

    def test_no_duplicate_ids(self, payments):
        ids = [p.payment_id for p in payments]
        assert len(ids) == len(set(ids))


class TestDeterminism:
    def test_same_seed_same_output(self):
        config = SimulatorConfig(seed=42, num_customers=99)
        customers_a = CustomerGenerator(config).generate()
        customers_b = CustomerGenerator(config).generate()
        assert [c.customer_id for c in customers_a] == [
            c.customer_id for c in customers_b
        ]

    def test_different_seeds_different_output(self):
        config_a = SimulatorConfig(seed=42, num_customers=99)
        config_b = SimulatorConfig(seed=99, num_customers=99)
        customers_a = CustomerGenerator(config_a).generate()
        customers_b = CustomerGenerator(config_b).generate()
        assert [c.customer_id for c in customers_a] != [
            c.customer_id for c in customers_b
        ]
