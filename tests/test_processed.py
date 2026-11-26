import pandas as pd

from fde_agent.processed import build_order_table


def _table() -> pd.DataFrame:
    orders = pd.DataFrame(
        {
            "order_id": ["on_time", "late", "canceled"],
            "customer_id": ["c1", "c2", "c3"],
            "order_status": ["delivered", "delivered", "canceled"],
            "order_purchase_timestamp": ["2018-01-01"] * 3,
            "order_delivered_customer_date": ["2018-01-05", "2018-01-30", None],
            "order_estimated_delivery_date": ["2018-01-10", "2018-01-20", "2018-01-10"],
        }
    )
    items = pd.DataFrame(
        {
            "order_id": ["on_time", "late", "late", "canceled"],
            "seller_id": ["s_sp", "s_sp", "s_rj", "s_sp"],
            "price": [100.0, 50.0, 50.0, 10.0],
            "freight_value": [10.0, 40.0, 40.0, 1.0],
        }
    )
    reviews = pd.DataFrame(
        {
            "order_id": ["on_time", "late", "late", "canceled"],
            "review_score": [5, 4, 1, 1],  # "late" has two reviews → keep the lowest
        }
    )
    payments = pd.DataFrame(
        {
            "order_id": ["on_time", "late", "canceled"],
            "payment_type": ["credit_card", "boleto", "credit_card"],
            "payment_installments": [1, 1, 3],
        }
    )
    customers = pd.DataFrame(
        {"customer_id": ["c1", "c2", "c3"], "customer_state": ["SP", "SP", "SP"]}
    )
    sellers = pd.DataFrame(
        {"seller_id": ["s_sp", "s_rj"], "seller_state": ["SP", "RJ"]}
    )
    return build_order_table(orders, items, reviews, payments, customers, sellers)


def test_one_row_per_reviewed_order() -> None:
    assert sorted(_table().index) == ["canceled", "late", "on_time"]


def test_delivery_flags() -> None:
    t = _table()
    assert t.loc["late", "late"] and not t.loc["on_time", "late"]
    assert t.loc["late", "slow"]  # 29 days ≥ 21
    assert t.loc["canceled", "not_delivered"] and not t.loc["late", "not_delivered"]


def test_order_shape_and_payment_flags() -> None:
    t = _table()
    assert t.loc["late", "multi_item"] and t.loc["late", "multi_seller"]
    assert t.loc["late", "interstate"] and not t.loc["on_time", "interstate"]
    assert t.loc["late", "high_freight"]  # 80 / 100 = 80% ≥ 30%
    assert t.loc["late", "boleto"] and t.loc["canceled", "installments"]


def test_low_review_uses_worst_score() -> None:
    t = _table()
    assert t.loc["late", "low_review"] and not t.loc["on_time", "low_review"]
