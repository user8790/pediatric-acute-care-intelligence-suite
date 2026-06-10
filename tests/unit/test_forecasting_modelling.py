from packages.core.forecasting import evaluate_forecast, moving_average_forecast, seasonal_naive_forecast
from packages.core.modelling import brier_score, no_show_probability, population_stability_index


def test_forecast_helpers():
    values = [1, 2, 3, 4]
    assert moving_average_forecast(values, horizon=2, window=2) == [3.5, 3.5]
    assert seasonal_naive_forecast(values, horizon=2, season_length=2) == [3.0, 4.0]
    metrics = evaluate_forecast([1, 2], [1.5, 1.5])
    assert metrics["mae"] == 0.5


def test_no_show_probability_bounds_and_drivers():
    result = no_show_probability({"lead_time_days": 45, "prior_missed_visits": 1, "distance_band_index": 2})
    assert 0 <= result["probability"] <= 1
    assert result["top_drivers"]


def test_brier_and_psi():
    assert brier_score([0, 1], [0.25, 0.75]) == 0.0625
    assert population_stability_index([1, 2, 3, 4, 5], [1, 2, 4, 5, 6]) >= 0

