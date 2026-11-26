"""Baseline revenue metrics: the "before" numbers every hypothesis is sized against."""

from dataclasses import dataclass

import pandas as pd

from fde_agent.data import load_table


@dataclass(frozen=True)
class Baseline:
    revenue: float  # R$, price + freight_value, delivered orders only
    orders: int  # delivered orders
    aov: float  # average order value = revenue / orders


def compute_baseline(orders: pd.DataFrame, items: pd.DataFrame) -> Baseline:
    """Pure calculation, so tests can pass small hand-made DataFrames."""
    delivered_ids = orders.loc[orders["order_status"] == "delivered", "order_id"]
    delivered_items = items[items["order_id"].isin(delivered_ids)]

    revenue = float((delivered_items["price"] + delivered_items["freight_value"]).sum())
    n_orders = int(delivered_ids.nunique())
    if n_orders == 0:
        raise ValueError("no delivered orders")
    return Baseline(revenue=revenue, orders=n_orders, aov=revenue / n_orders)


def baseline() -> Baseline:
    """Baseline from the real Olist CSVs in data/raw/."""
    return compute_baseline(load_table("orders"), load_table("order_items"))
