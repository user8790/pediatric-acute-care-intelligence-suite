"""Distribution helpers for deterministic synthetic data generation."""

from __future__ import annotations

from datetime import datetime

import numpy as np


def winter_respiratory_multiplier(timestamp: datetime) -> float:
    """Seasonal multiplier peaking in Jan/Feb and late Nov/Dec."""

    month = timestamp.month
    if month in (1, 2):
        return 1.45
    if month in (11, 12):
        return 1.35
    if month in (3, 10):
        return 1.15
    return 0.9


def school_day_multiplier(timestamp: datetime) -> float:
    if timestamp.weekday() >= 5:
        return 0.86
    if timestamp.month in (7, 8):
        return 0.92
    return 1.05


def bounded_normal(rng: np.random.Generator, mean: float, sd: float, low: float, high: float) -> float:
    return float(min(high, max(low, rng.normal(mean, sd))))


def beta_rate(rng: np.random.Generator, mean: float, concentration: float = 40) -> float:
    alpha = max(mean * concentration, 0.1)
    beta = max((1 - mean) * concentration, 0.1)
    return float(rng.beta(alpha, beta))

