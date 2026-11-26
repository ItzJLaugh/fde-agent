import pandas as pd
import pytest

from fde_agent.baseline import compute_baseline


def _orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["a", "b", "c"],
            "order_status": ["delivered", "canceled", "delivered"],
        }
    )


def _items() -> pd.DataFrame:
    # order "a" has two items; "b" is canceled and must be excluded
    return pd.DataFrame(
        {
            "order_id": ["a", "a", "b", "c"],
            "price": [10.0, 20.0, 99.0, 40.0],
            "freight_value": [1.0, 2.0, 9.0, 4.0],
        }
    )


def test_counts_delivered_orders_only() -> None:
    assert compute_baseline(_orders(), _items()).orders == 2


def test_revenue_is_price_plus_freight_for_delivered() -> None:
    # a: 10+1 + 20+2 = 33, c: 40+4 = 44 → 77
    assert compute_baseline(_orders(), _items()).revenue == pytest.approx(77.0)


def test_aov_is_revenue_per_order() -> None:
    assert compute_baseline(_orders(), _items()).aov == pytest.approx(38.5)


def test_rejects_no_delivered_orders() -> None:
    orders = pd.DataFrame({"order_id": ["b"], "order_status": ["canceled"]})
    with pytest.raises(ValueError):
        compute_baseline(orders, _items())
