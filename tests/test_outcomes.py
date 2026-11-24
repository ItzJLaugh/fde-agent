import pytest

from fde_agent.outcomes import average_minutes, minutes_saved


def test_average_minutes() -> None:
    assert average_minutes([2.0, 4.0, 6.0]) == pytest.approx(4.0)


def test_average_minutes_rejects_empty() -> None:
    with pytest.raises(ValueError):
        average_minutes([])


def test_minutes_saved() -> None:
    assert minutes_saved(baseline=7.5, current=5.0) == pytest.approx(2.5)
