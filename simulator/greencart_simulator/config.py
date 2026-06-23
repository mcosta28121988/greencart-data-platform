from dataclasses import dataclass
from typing import Optional


@dataclass
class SimulatorConfig:
    """
    Central configuration for a GreenCart simulation run.
    All generator components receive this config — nothing is hardcoded.
    """
    seed: int = 42
    num_customers: int = 1000
    num_products: int = 200
    num_days: int = 365
    countries: tuple = ("AU", "US", "UK")

    # Business behaviour knobs
    repeat_purchase_rate: float = 0.35   # 35% of customers buy more than once
    cancellation_rate: float = 0.05      # 5% of orders are cancelled
    

CURRENCY_MAP = {
    "AU": "AUD",
    "US": "USD",
    "UK": "GBP",
}

COUNTRY_NAMES = {
    "AU": "Australia",
    "US": "United States",
    "UK": "United Kingdom",
}