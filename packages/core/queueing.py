"""Transparent queueing formulas used by the prototype."""

from __future__ import annotations

import math
from dataclasses import dataclass


EPSILON = 1e-12


@dataclass(frozen=True)
class QueueMetrics:
    utilization: float
    wait_probability: float
    expected_queue_length: float
    expected_wait_time: float
    expected_system_time: float
    expected_system_size: float
    method: str


def utilization(arrival_rate: float, service_rate: float, servers: int = 1) -> float:
    """Return rho = lambda / (c * mu)."""

    if servers <= 0:
        raise ValueError("servers must be positive")
    if service_rate <= 0:
        raise ValueError("service_rate must be positive")
    return arrival_rate / (servers * service_rate)


def little_law(arrival_rate: float, system_time: float) -> float:
    """Little's Law: L = lambda * W."""

    if arrival_rate < 0 or system_time < 0:
        raise ValueError("arrival_rate and system_time must be non-negative")
    return arrival_rate * system_time


def erlang_c_wait_probability(arrival_rate: float, service_rate: float, servers: int) -> float:
    """M/M/c wait probability using the Erlang C formula."""

    if arrival_rate < 0:
        raise ValueError("arrival_rate must be non-negative")
    rho = utilization(arrival_rate, service_rate, servers)
    if arrival_rate == 0:
        return 0.0
    if rho >= 1:
        return 1.0

    offered_load = arrival_rate / service_rate
    terms = [offered_load**n / math.factorial(n) for n in range(servers)]
    tail = (offered_load**servers / math.factorial(servers)) * (1 / (1 - rho))
    return tail / (sum(terms) + tail)


def mmc_metrics(arrival_rate: float, service_rate: float, servers: int) -> QueueMetrics:
    """Return M/M/c metrics in the same time unit as the rates."""

    rho = utilization(arrival_rate, service_rate, servers)
    pw = erlang_c_wait_probability(arrival_rate, service_rate, servers)
    if arrival_rate == 0:
        return QueueMetrics(rho, 0.0, 0.0, 0.0, 1 / service_rate, 0.0, "M/M/c Erlang C")
    if rho >= 1:
        # Saturated systems do not have finite steady-state waits.
        return QueueMetrics(rho, 1.0, math.inf, math.inf, math.inf, math.inf, "M/M/c saturated")
    expected_wait = pw / (servers * service_rate - arrival_rate)
    expected_queue = arrival_rate * expected_wait
    expected_system_time = expected_wait + 1 / service_rate
    expected_system_size = little_law(arrival_rate, expected_system_time)
    return QueueMetrics(
        utilization=rho,
        wait_probability=pw,
        expected_queue_length=expected_queue,
        expected_wait_time=expected_wait,
        expected_system_time=expected_system_time,
        expected_system_size=expected_system_size,
        method="M/M/c Erlang C",
    )


def kingman_gg1_wait(
    arrival_rate: float,
    service_rate: float,
    ca2: float = 1.0,
    cs2: float = 1.0,
) -> QueueMetrics:
    """Kingman approximation for G/G/1 waiting time."""

    rho = utilization(arrival_rate, service_rate, 1)
    if arrival_rate == 0:
        return QueueMetrics(rho, 0.0, 0.0, 0.0, 1 / service_rate, 0.0, "G/G/1 Kingman")
    if rho >= 1:
        return QueueMetrics(rho, 1.0, math.inf, math.inf, math.inf, math.inf, "G/G/1 saturated")
    variability = max(ca2 + cs2, 0) / 2
    expected_wait = variability * (rho / (1 - rho)) * (1 / service_rate)
    return QueueMetrics(
        utilization=rho,
        wait_probability=min(1.0, rho + 0.1 * variability),
        expected_queue_length=little_law(arrival_rate, expected_wait),
        expected_wait_time=expected_wait,
        expected_system_time=expected_wait + 1 / service_rate,
        expected_system_size=little_law(arrival_rate, expected_wait + 1 / service_rate),
        method="G/G/1 Kingman",
    )


def allen_cunneen_ggc_wait(
    arrival_rate: float,
    service_rate: float,
    servers: int,
    ca2: float = 1.0,
    cs2: float = 1.0,
) -> QueueMetrics:
    """Allen-Cunneen style approximation for G/G/c queues."""

    if servers == 1:
        return kingman_gg1_wait(arrival_rate, service_rate, ca2, cs2)
    rho = utilization(arrival_rate, service_rate, servers)
    if arrival_rate == 0:
        return QueueMetrics(rho, 0.0, 0.0, 0.0, 1 / service_rate, 0.0, "G/G/c Allen-Cunneen")
    if rho >= 1:
        return QueueMetrics(rho, 1.0, math.inf, math.inf, math.inf, math.inf, "G/G/c saturated")
    variability = max(ca2 + cs2, 0) / 2
    exponent = math.sqrt(2 * (servers + 1)) - 1
    expected_wait = variability * (rho**exponent / (servers * service_rate * (1 - rho)))
    wait_probability = min(1.0, erlang_c_wait_probability(arrival_rate, service_rate, servers) * variability)
    return QueueMetrics(
        utilization=rho,
        wait_probability=wait_probability,
        expected_queue_length=little_law(arrival_rate, expected_wait),
        expected_wait_time=expected_wait,
        expected_system_time=expected_wait + 1 / service_rate,
        expected_system_size=little_law(arrival_rate, expected_wait + 1 / service_rate),
        method="G/G/c Allen-Cunneen",
    )


def erlang_b_blocking_probability(arrival_rate: float, service_rate: float, servers: int) -> float:
    """Blocking probability for an M/M/c/c loss system."""

    if servers <= 0:
        raise ValueError("servers must be positive")
    if arrival_rate < 0:
        raise ValueError("arrival_rate must be non-negative")
    offered_load = arrival_rate / max(service_rate, EPSILON)
    b = 1.0
    for c in range(1, servers + 1):
        b = (offered_load * b) / (c + offered_load * b)
    return b


def effective_staffed_beds(
    physical_beds: int,
    staffed_beds: int,
    staffing_gap: float = 0.0,
    isolation_factor: float = 1.0,
    stepdown_constraint_factor: float = 1.0,
) -> int:
    """Capacity after staffing, isolation, and step-down constraints."""

    if physical_beds < 0 or staffed_beds < 0:
        raise ValueError("bed counts must be non-negative")
    gap_factor = max(0.0, min(1.0, 1.0 - staffing_gap))
    constrained = min(physical_beds, staffed_beds) * gap_factor * isolation_factor * stepdown_constraint_factor
    return max(0, math.floor(constrained))


def overbooking_slots(capacity: int, no_show_probability: float, risk_guardrail: float = 0.12) -> int:
    """Simple overbooking coefficient with an explicit overflow guardrail."""

    if capacity < 0:
        raise ValueError("capacity must be non-negative")
    no_show_probability = min(max(no_show_probability, 0.0), 0.6)
    risk_guardrail = min(max(risk_guardrail, 0.0), 0.5)
    return math.floor(capacity * min(no_show_probability, risk_guardrail))

