"""Demo model helpers with simple transparent fallbacks."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import exp

import numpy as np


def logistic(x: float) -> float:
    return 1.0 / (1.0 + exp(-x))


def no_show_probability(features: Mapping[str, float]) -> dict[str, object]:
    """Transparent fallback no-show model for synthetic ambulatory demos."""

    score = -2.5
    drivers: list[tuple[str, float]] = []
    lead_time = float(features.get("lead_time_days", 14))
    prior_misses = float(features.get("prior_missed_visits", 0))
    distance_band = float(features.get("distance_band_index", 1))
    virtual = float(features.get("is_virtual", 0))
    morning = float(features.get("is_morning", 0))

    contributions = {
        "long booking lead time": 0.025 * max(0, lead_time - 14),
        "prior missed visits": 0.55 * prior_misses,
        "travel burden proxy": 0.18 * distance_band,
        "virtual appointment": -0.22 * virtual,
        "morning appointment": -0.08 * morning,
    }
    for name, value in contributions.items():
        score += value
        drivers.append((name, value))
    probability = min(0.85, max(0.02, logistic(score)))
    return {
        "model_name": "transparent_no_show_v0",
        "probability": probability,
        "top_drivers": sorted(drivers, key=lambda item: abs(item[1]), reverse=True)[:3],
        "validation_status": "synthetic demo only",
    }


def brier_score(actual: Sequence[int], probabilities: Sequence[float]) -> float:
    a = np.array(actual, dtype=float)
    p = np.array(probabilities, dtype=float)
    if len(a) != len(p):
        raise ValueError("actual and probabilities must have equal length")
    return float(np.mean((a - p) ** 2))


def population_stability_index(expected: Sequence[float], observed: Sequence[float], buckets: int = 10) -> float:
    """Population stability index for drift monitoring."""

    e = np.array(expected, dtype=float)
    o = np.array(observed, dtype=float)
    if len(e) == 0 or len(o) == 0:
        return 0.0
    quantiles = np.quantile(e, np.linspace(0, 1, buckets + 1))
    quantiles[0] -= 1e-9
    quantiles[-1] += 1e-9
    e_counts, _ = np.histogram(e, bins=quantiles)
    o_counts, _ = np.histogram(o, bins=quantiles)
    e_pct = np.maximum(e_counts / max(e_counts.sum(), 1), 1e-6)
    o_pct = np.maximum(o_counts / max(o_counts.sum(), 1), 1e-6)
    return float(np.sum((o_pct - e_pct) * np.log(o_pct / e_pct)))

