from .config import SimulatorConfig
from .generators import (
    CustomerGenerator,
    ProductGenerator,
    OrderGenerator,
    PaymentGenerator,
)
from .exporter import ParquetExporter


def run(config: SimulatorConfig, output_dir: str = "output") -> None:
    print(f"GreenCart Simulator v0.1")
    print(f"Seed: {config.seed} | Customers: {config.num_customers:,} | Days: {config.num_days}")
    print()

    print("Generating products...")
    products = ProductGenerator(config).generate()

    print("Generating customers...")
    customers = CustomerGenerator(config).generate()

    print("Generating orders and order lines...")
    orders, order_lines = OrderGenerator(config).generate(customers, products)

    print("Generating payments...")
    payments = PaymentGenerator(config).generate(orders, order_lines)

    print()
    ParquetExporter(output_dir).export(
        customers, products, orders, order_lines, payments
    )
