"""Processed order table: one row per reviewed order, one True/False column per flag.

Flags are the "inputs" of the truth table; LOW_REVIEW is the "output" (effect).
"""

import pandas as pd

from fde_agent.data import DATA_DIR, load_table

PROCESSED_DIR = DATA_DIR.parent / "processed"

# Each flag: name → plain-English rule (printed on charts and in evidence files).
FLAGS: dict[str, str] = {
    "not_delivered": "order_status is not 'delivered'",
    "late": "delivered after the estimated delivery date",
    "slow": "purchase → delivery took 21+ days",
    "high_freight": "freight is 30%+ of item price",
    "multi_item": "2+ items in the order",
    "multi_seller": "2+ sellers in the order",
    "interstate": "a seller is in a different state than the customer",
    "installments": "paid in 2+ installments",
    "boleto": "paid by boleto (bank slip)",
}
OUTCOME = "low_review"  # review score 1-2 (lowest score if the order has several)

SLOW_DAYS = 21
HIGH_FREIGHT_SHARE = 0.30


def build_order_table(
    orders: pd.DataFrame,
    items: pd.DataFrame,
    reviews: pd.DataFrame,
    payments: pd.DataFrame,
    customers: pd.DataFrame,
    sellers: pd.DataFrame,
) -> pd.DataFrame:
    """Pure transform (testable with tiny DataFrames). Returns flags + outcome."""
    o = orders.set_index("order_id")
    purchased = pd.to_datetime(o["order_purchase_timestamp"])
    delivered_at = pd.to_datetime(o["order_delivered_customer_date"])
    estimated = pd.to_datetime(o["order_estimated_delivery_date"])
    days_late = (delivered_at - estimated).dt.days
    days_to_deliver = (delivered_at - purchased).dt.days

    # order_items → per-order aggregates
    it = items.merge(sellers[["seller_id", "seller_state"]], on="seller_id", how="left")
    cust_state = o["customer_id"].map(
        customers.set_index("customer_id")["customer_state"]
    )
    it["customer_state"] = it["order_id"].map(cust_state)
    per_item = it.groupby("order_id")
    price = per_item["price"].sum()
    freight = per_item["freight_value"].sum()
    n_items = per_item.size()
    n_sellers = per_item["seller_id"].nunique()
    interstate = (
        (it["seller_state"] != it["customer_state"]).groupby(it["order_id"]).any()
    )

    pay = payments.groupby("order_id")
    max_installments = pay["payment_installments"].max()
    boleto = (payments["payment_type"] == "boleto").groupby(payments["order_id"]).any()

    worst_score = reviews.groupby("order_id")["review_score"].min()

    t = pd.DataFrame(index=worst_score.index.intersection(o.index))
    t.index.name = "order_id"
    idx = t.index
    t["not_delivered"] = o.loc[idx, "order_status"] != "delivered"
    t["late"] = days_late.reindex(idx).gt(0)
    t["slow"] = days_to_deliver.reindex(idx).ge(SLOW_DAYS)
    share = freight.reindex(idx) / price.reindex(idx)
    t["high_freight"] = share.ge(HIGH_FREIGHT_SHARE)
    t["multi_item"] = n_items.reindex(idx).gt(1)
    t["multi_seller"] = n_sellers.reindex(idx).gt(1)
    t["interstate"] = interstate.reindex(idx).eq(True)
    t["installments"] = max_installments.reindex(idx).gt(1)
    t["boleto"] = boleto.reindex(idx).eq(True)
    t[OUTCOME] = worst_score.reindex(idx).le(2)
    # numeric columns kept for the threshold charts
    t["days_late"] = days_late.reindex(idx)
    t["review_score"] = worst_score.reindex(idx)
    t["revenue"] = (price + freight).reindex(idx).fillna(0.0)
    return t


def order_table() -> pd.DataFrame:
    """Build from the real CSVs and cache to data/processed/orders.csv."""
    t = build_order_table(
        load_table("orders"),
        load_table("order_items"),
        load_table("order_reviews"),
        load_table("order_payments"),
        load_table("customers"),
        load_table("sellers"),
    )
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(PROCESSED_DIR / "orders.csv")
    return t
