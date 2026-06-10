from packages.core.simulation import BedScenario, optional_engine_status, simulate_bed_flow, simulate_clinic_backlog


def test_bed_simulation_reproducible():
    scenario = BedScenario(name="test", seed=123, hours=24, beds=40, initial_census=35)
    first = simulate_bed_flow(scenario)
    second = simulate_bed_flow(scenario)
    assert first["census_by_hour"] == second["census_by_hour"]
    assert first["boarder_hours"] == second["boarder_hours"]


def test_clinic_backlog_reproducible():
    first = simulate_clinic_backlog([20, 22, 24], 25, 60, seed=123)
    second = simulate_clinic_backlog([20, 22, 24], 25, 60, seed=123)
    assert first["backlog_history"] == second["backlog_history"]


def test_optional_engine_status_shape():
    status = optional_engine_status()
    assert {"simpy", "ciw", "mesa"}.issubset(status.keys())

