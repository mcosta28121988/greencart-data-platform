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
def orders_and_lines(config, customers, products):
    return OrderGenerator(config).generate(customers, products)


@pytest.fixture
def orders(orders_and_lines):
    return orders_and_lines[0]


@pytest.fixture
def order_lines(orders_and_lines):
    return orders_and_lines[1]


@pytest.fixture
def payments(config, orders, order_lines):
    return PaymentGenerator(config).generate(orders, order_lines)


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
        valid = {"delivered", "cancelled"}
        assert all(o.status in valid for o in orders)

    def test_no_duplicate_order_ids(self, orders):
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


class TestOrderLineGenerator:
    def test_every_order_has_at_least_one_line(self, orders, order_lines):
        order_ids_with_lines = {ol.order_id for ol in order_lines}
        all_order_ids = {o.order_id for o in orders}
        assert all_order_ids == order_ids_with_lines

    def test_no_duplicate_line_ids(self, order_lines):
        ids = [ol.order_line_id for ol in order_lines]
        assert len(ids) == len(set(ids))

    def test_line_total_equals_quantity_times_price(self, order_lines):
        for ol in order_lines:
            expected = round(ol.quantity * ol.unit_price, 2)
            assert ol.line_total == expected

    def test_unit_price_is_positive(self, order_lines):
        assert all(ol.unit_price > 0 for ol in order_lines)

    def test_quantity_within_range(self, order_lines):
        assert all(1 <= ol.quantity <= 3 for ol in order_lines)

    def test_all_lines_reference_valid_orders(self, orders, order_lines):
        order_ids = {o.order_id for o in orders}
        for ol in order_lines:
            assert ol.order_id in order_ids

    def test_all_lines_reference_valid_products(self, products, order_lines):
        product_ids = {p.product_id for p in products}
        for ol in order_lines:
            assert ol.product_id in product_ids


class TestPaymentGenerator:
    def test_cancelled_orders_have_no_payment(self, orders, payments):
        cancelled_ids = {o.order_id for o in orders if o.status == "cancelled"}
        payment_order_ids = {p.order_id for p in payments}
        assert cancelled_ids.isdisjoint(payment_order_ids)

    def test_payment_amount_matches_order_lines_total(self, order_lines, payments):
        order_totals: dict[str, float] = {}
        for ol in order_lines:
            order_totals[ol.order_id] = round(
                order_totals.get(ol.order_id, 0.0) + ol.line_total, 2
            )
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
