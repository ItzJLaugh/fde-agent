"""Outcome metrics measured against a baseline."""

from collections.abc import Sequence


def average_minutes(durations: Sequence[float]) -> float:
    """Mean call-handling time in minutes. O(n) time, O(1) extra space."""
    if not durations:
        raise ValueError("durations must not be empty")
    return sum(durations) / len(durations)


def minutes_saved(baseline: float, current: float) -> float:
    """Minutes saved per call versus the baseline (negative means slower)."""
    return baseline - current
