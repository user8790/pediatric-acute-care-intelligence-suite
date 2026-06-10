from packages.core.queueing import (
    allen_cunneen_ggc_wait,
    effective_staffed_beds,
    erlang_b_blocking_probability,
    erlang_c_wait_probability,
    little_law,
    mmc_metrics,
    overbooking_slots,
)


def test_erlang_c_stable_queue():
    wait_probability = erlang_c_wait_probability(arrival_rate=8, service_rate=3, servers=4)
    assert 0 < wait_probability < 1
    metrics = mmc_metrics(arrival_rate=8, service_rate=3, servers=4)
    assert metrics.expected_wait_time > 0
    assert metrics.expected_system_time > metrics.expected_wait_time


def test_little_law():
    assert little_law(4, 2.5) == 10


def test_allen_cunneen_returns_finite_for_stable_queue():
    metrics = allen_cunneen_ggc_wait(5, 2, 4, ca2=1.4, cs2=1.2)
    assert metrics.expected_wait_time > 0
    assert metrics.expected_system_time < 10


def test_blocking_probability_bounds():
    blocking = erlang_b_blocking_probability(4, 2, 5)
    assert 0 <= blocking <= 1


def test_effective_beds_and_overbooking():
    assert effective_staffed_beds(10, 9, staffing_gap=0.1, isolation_factor=0.95) == 7
    assert overbooking_slots(40, 0.2, risk_guardrail=0.1) == 4

