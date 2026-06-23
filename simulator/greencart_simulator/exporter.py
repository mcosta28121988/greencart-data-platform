import os
import pandas as pd
from dataclasses import asdict
from .models import Customer, Product, Order, Payment


class ParquetExporter:
    """
    Converts domain model lists to Parquet files.
    One file per entity, written to the configured output directory.
    """
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export(
        self,
        customers: list[Customer],
        products: list[Product],
        orders: list[Order],
        payments: list[Payment],
    ) -> None:
        self._write(customers, "customers")
        self._write(products, "products")
        self._write(orders, "orders")
        self._write(payments, "payments")
        print(f"Exported to {self.output_dir}/")
        print(f"  customers : {len(customers):,} rows")
        print(f"  products  : {len(products):,} rows")
        print(f"  orders    : {len(orders):,} rows")
        print(f"  payments  : {len(payments):,} rows")

    def _write(self, records: list, name: str) -> None:
        df = pd.DataFrame([asdict(r) for r in records])
        path = os.path.join(self.output_dir, f"{name}.parquet")
        df.to_parquet(path, index=False)