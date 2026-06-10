"""Small deterministic simulation fallbacks for Snowflake-transferable scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class BedScenario:
    name: str
    hours: int = 72
    beds: int = 120
    initial_census: int = 105
    hourly_arrival_rate: float = 4.0
    mean_los_hours: float = 36.0
    respiratory_multiplier: float = 1.0
    discharge_improvement: float = 0.0
    seed: int = 20260610


def optional_engine_status() -> dict[str, bool]:
    """Detect showcase/research optional simulation packages without making them required."""

    status: dict[str, bool] = {}
    for module_name in ("mesa",):
        try:
            __import__(module_name)
            status[module_name] = True
        except Exception:
            status[module_name] = False
    return status


def simulate_bed_flow(scenario: BedScenario) -> dict[str, object]:
    """Pure-Python/numpy bed flow simulation with event departures."""

    rng = np.random.default_rng(scenario.seed)
    departures: list[float] = []
    for _ in range(scenario.initial_census):
        departures.append(float(rng.gamma(shape=2.0, scale=scenario.mean_los_hours / 2.0)))

    census_by_hour: list[int] = []
    boarders_by_hour: list[int] = []
    shortage_hours = 0
    boarder_hours = 0
    discharge_shift = 1.0 + max(scenario.discharge_improvement, 0.0)

    for hour in range(scenario.hours):
        departures = [d for d in departures if d > hour]
        hour_of_day = hour % 24
        arrival_shape = 1.15 if 10 <= hour_of_day <= 22 else 0.75
        arrivals = int(rng.poisson(scenario.hourly_arrival_rate * arrival_shape * scenario.respiratory_multiplier))
        discharges_boost = int(rng.poisson(max(0.0, scenario.discharge_improvement) * 2.0))
        departures = sorted(departures)[discharges_boost:]
        for _ in range(arrivals):
            los = rng.gamma(shape=2.2, scale=(scenario.mean_los_hours / discharge_shift) / 2.2)
            departures.append(hour + max(3.0, float(los)))

        census = len(departures)
        boarders = max(0, census - scenario.beds)
        if boarders:
            shortage_hours += 1
            boarder_hours += boarders
        census_by_hour.append(min(census, scenario.beds + boarders))
        boarders_by_hour.append(boarders)

    occupancy = np.array(census_by_hour, dtype=float) / max(scenario.beds, 1)
    return {
        "scenario": scenario.name,
        "hours": scenario.hours,
        "beds": scenario.beds,
        "mean_occupancy": float(np.mean(occupancy)),
        "p95_occupancy": float(np.quantile(occupancy, 0.95)),
        "probability_above_95": float(np.mean(occupancy > 0.95)),
        "shortage_hours": int(shortage_hours),
        "boarder_hours": int(boarder_hours),
        "census_by_hour": census_by_hour,
        "boarders_by_hour": boarders_by_hour,
        "engine": "numpy_fallback",
    }


def monte_carlo_bed_scenario(scenario: BedScenario, runs: int = 100) -> dict[str, float]:
    """Run replicated bed simulations and return confidence intervals."""

    results = []
    for i in range(runs):
        run = simulate_bed_flow(
            BedScenario(**{**scenario.__dict__, "seed": scenario.seed + i})
        )
        results.append(run)

    boarder_hours = np.array([r["boarder_hours"] for r in results], dtype=float)
    p95 = np.array([r["p95_occupancy"] for r in results], dtype=float)
    return {
        "runs": float(runs),
        "boarder_hours_mean": float(boarder_hours.mean()),
        "boarder_hours_p10": float(np.quantile(boarder_hours, 0.10)),
        "boarder_hours_p90": float(np.quantile(boarder_hours, 0.90)),
        "p95_occupancy_mean": float(p95.mean()),
        "p95_occupancy_p10": float(np.quantile(p95, 0.10)),
        "p95_occupancy_p90": float(np.quantile(p95, 0.90)),
    }


def simulate_clinic_backlog(
    weekly_referrals: Iterable[int],
    weekly_capacity: int,
    initial_backlog: int,
    no_show_rate: float = 0.08,
    overbook_slots: int = 0,
    seed: int = 20260610,
) -> dict[str, object]:
    """Simple ambulatory backlog simulation by week."""

    rng = np.random.default_rng(seed)
    backlog = int(initial_backlog)
    backlog_history: list[int] = []
    utilization_history: list[float] = []
    breach_risk_history: list[float] = []
    effective_capacity = max(0, weekly_capacity + overbook_slots)

    for referrals in weekly_referrals:
        arrivals = int(rng.poisson(max(referrals, 0)))
        show_capacity = int(round(effective_capacity * (1 - no_show_rate)))
        completed = min(backlog + arrivals, show_capacity)
        backlog = max(0, backlog + arrivals - completed)
        backlog_history.append(backlog)
        utilization_history.append(completed / max(effective_capacity, 1))
        breach_risk_history.append(min(0.95, backlog / max(weekly_capacity * 8, 1)))

    clearance_week = next((i + 1 for i, value in enumerate(backlog_history) if value == 0), None)
    return {
        "backlog_history": backlog_history,
        "utilization_history": utilization_history,
        "breach_risk_history": breach_risk_history,
        "final_backlog": backlog,
        "clearance_week": clearance_week,
        "engine": "numpy_fallback",
    }
