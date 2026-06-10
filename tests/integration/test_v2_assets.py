import json
import re
from pathlib import Path


V2_DIR = Path("apps/showcase/public/data/v2")

REQUIRED_JSON = [
    "metadata.json",
    "inpatient_mission_control.json",
    "inpatient_flow.json",
    "inpatient_forecasts.json",
    "inpatient_scenarios.json",
    "ambulatory_mission_control.json",
    "ambulatory_access.json",
    "ambulatory_forecasts.json",
    "ambulatory_scenarios.json",
    "model_cards.json",
    "data_quality.json",
    "open_data_context.json",
    "coefficient_registry.json",
]

REQUIRED_COEFFICIENTS = {
    "arrival_rate_lambda",
    "service_rate_mu",
    "servers_resources",
    "utilization",
    "interarrival_variability",
    "service_variability",
    "erlang_c_wait_probability",
    "erlang_b_blocking_probability",
    "kingman_wait_hours",
    "allen_cunneen_wait_hours",
    "little_law",
    "discharge_completion_rate",
    "bed_turnaround_minutes",
    "effective_staffed_bed_coefficient",
    "isolation_constraint_factor",
    "step_down_constraint_factor",
    "respiratory_surge_multiplier",
    "weather_smoke_multiplier",
    "school_holiday_multiplier",
    "no_show_probability",
    "overbooking_coefficient",
    "diagnostic_dependency_delay",
    "protected_slot_coefficient",
    "virtual_care_conversion",
}


def load_json(name: str):
    return json.loads((V2_DIR / name).read_text(encoding="utf-8"))


def test_v2_json_assets_exist_and_are_non_empty():
    for name in REQUIRED_JSON:
        path = V2_DIR / name
        assert path.exists(), name
        payload = load_json(name)
        assert payload


def test_v2_scenario_output_shape():
    inpatient = load_json("inpatient_scenarios.json")["rows"]
    ambulatory = load_json("ambulatory_scenarios.json")["rows"]
    assert len(inpatient) >= 8
    assert len(ambulatory) >= 8
    for row in inpatient:
        assert {"scenario_name", "boarder_hours_mean", "boarder_hours_p10", "boarder_hours_p90", "impact_score"}.issubset(row)
    for row in ambulatory:
        assert {"scenario_name", "final_backlog", "backlog_p10", "backlog_p90", "impact_score"}.issubset(row)


def test_v2_coefficient_registry_complete():
    rows = load_json("coefficient_registry.json")["rows"]
    names = {row["coefficient_name"] for row in rows}
    assert REQUIRED_COEFFICIENTS.issubset(names)


def test_v2_model_cards_complete():
    rows = load_json("model_cards.json")["rows"]
    assert len(rows) >= 6
    required = {
        "model_id",
        "model_name",
        "version",
        "prediction_horizon",
        "intended_use",
        "training_data",
        "validation_status",
        "metrics",
        "data_freshness",
        "caveat",
    }
    for row in rows:
        assert required.issubset(row)
        assert "not validated" in row["validation_status"].lower()


def test_v2_assets_do_not_contain_direct_identifiers():
    text = "\n".join(path.read_text(encoding="utf-8") for path in V2_DIR.glob("*.json"))
    forbidden_patterns = [
        r"\bMRN\b",
        r"health number",
        r"\bphone\b",
        r"\baddress\b",
        r"\bpatient_name\b",
        r"\bfirst_name\b",
        r"\blast_name\b",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, text, flags=re.IGNORECASE), pattern
