"""Forecasting helpers with dependency-light fallbacks."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def moving_average_forecast(values: Sequence[float], horizon: int, window: int = 7) -> list[float]:
    if horizon <= 0:
        return []
    if not values:
        return [0.0] * horizon
    window_values = list(values)[-max(1, window) :]
    return [float(np.mean(window_values))] * horizon


def seasonal_naive_forecast(values: Sequence[float], horizon: int, season_length: int = 24) -> list[float]:
    if horizon <= 0:
        return []
    if not values:
        return [0.0] * horizon
    history = list(values)
    result: list[float] = []
    for i in range(horizon):
        idx = len(history) - season_length + (i % season_length)
        if idx < 0:
            result.append(float(np.mean(history)))
        else:
            result.append(float(history[idx]))
    return result


def prediction_band(point_forecast: Sequence[float], residual_std: float, z: float = 1.28) -> list[dict[str, float]]:
    return [
        {"point": float(v), "lower": float(v - z * residual_std), "upper": float(v + z * residual_std)}
        for v in point_forecast
    ]


def evaluate_forecast(actual: Sequence[float], predicted: Sequence[float]) -> dict[str, float]:
    a = np.array(actual, dtype=float)
    p = np.array(predicted, dtype=float)
    if len(a) != len(p):
        raise ValueError("actual and predicted must have equal length")
    error = a - p
    denom = (np.abs(a) + np.abs(p)) / 2
    smape = np.mean(np.where(denom == 0, 0, np.abs(error) / denom))
    return {
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "smape": float(smape),
    }

