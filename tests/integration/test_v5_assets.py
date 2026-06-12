import json
import re
from pathlib import Path


V5_DIR = Path("apps/showcase/public/data/v5")

REQUIRED_JSON = [
    "metadata.json",
    "source_registry.json",
    "direct_link_validation.json",
    "metric_registry.json",
    "model_registry.json",
    "panel_lineage.json",
    "system_posture.json",
    "inpatient_intelligence.json",
    "ambulatory_intelligence.json",
    "predictive_assets.json",
    "scenario_lab.json",
    "gatekeeper_control_plane.json",
    "learning_system_memory.json",
    "future_real_data_wiring.json",
    "command_center_context.json",
]

REQUIRED_SERVICES = {
    "General pediatrics",
    "Respiratory",
    "Surgery",
    "PICU",
    "NICU",
    "Cardiology",
    "Oncology",
    "Neurology",
    "Mental health",
    "Complex care",
    "Short stay",
    "Procedural recovery",
}

REQUIRED_PROGRAMS = {
    "Respiratory",
    "Cardiology",
    "Neurology",
    "Surgery follow-up",
    "Oncology survivorship",
    "Complex care",
    "Mental health",
    "Diabetes/endocrinology",
    "Gastroenterology",
    "Nephrology",
    "Rheumatology",
    "Diagnostics",
    "Post-discharge follow-up",
    "Virtual/outreach",
}

OPEN_CONTEXT_SOURCES = {
    "SRC_OPEN_RESPIRATORY_VIRUS_DASHBOARD",
    "SRC_OPEN_AQHI_SMOKE_CONTEXT",
    "SRC_OPEN_SCHOOL_HOLIDAY_CALENDAR",
    "SRC_OPEN_STATCAN_PED_POPULATION",
    "SRC_OPEN_ED_WAIT_TIME_LOGIC",
}


def load_json(name: str):
    return json.loads((V5_DIR / name).read_text(encoding="utf-8"))


def walk_strings(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)
    elif isinstance(value, str):
        yield value


def test_v5_json_assets_exist_and_are_non_empty():
    for name in REQUIRED_JSON:
        path = V5_DIR / name
        assert path.exists(), name
        assert load_json(name)


def test_v5_metadata_and_command_center_context():
    metadata = load_json("metadata.json")
    command = load_json("command_center_context.json")
    assert metadata["appVersion"] == "v5.0"
    assert metadata["mode"] == "Synthetic demonstration data"
    assert "Not validated for clinical decision-making" in metadata["clinicalUse"]
    assert len(command["sites"]) == 3
    assert len(command["openContext"]) >= 52
    assert len(command["chartCatalog"]) >= 20
    assert len(command["lakehouseTables"]) >= 6
    assert len(command["interpretations"]) >= 10
    assert len(command["roleGuidance"]) == 7
    assert len(command["implementationReadiness"]) >= 20
    assert len(command["actionLearningLoops"]) >= 20
    assert len(command["signalSimulations"]) == 4


def test_v5_service_unit_and_program_depth():
    inpatient = load_json("inpatient_intelligence.json")
    ambulatory = load_json("ambulatory_intelligence.json")
    units = inpatient["unitDetails"]
    programs = ambulatory["programDetails"]
    assert len(units) >= 36
    assert len(programs) >= 42
    assert REQUIRED_SERVICES.issubset({row["service_line"] for row in units})
    assert REQUIRED_PROGRAMS.issubset({row["program"] for row in programs})

    required_unit_fields = {
        "capacity",
        "census",
        "staffed_beds",
        "effective_beds",
        "ed_boarders",
        "transfer_in_requests",
        "discharge_barriers",
        "predicted_admissions_24h",
        "predicted_discharges_24h",
        "staffing_gap_hours",
        "variable_staffing_cost_k",
        "source_readiness",
        "source_ids",
    }
    required_program_fields = {
        "referrals_4w",
        "triage_volume_4w",
        "waitlist_total",
        "third_next_available_days",
        "template_capacity_4w",
        "no_show_rate",
        "diagnostic_readiness",
        "provider_capacity_sessions_4w",
        "hr_gap_sessions_4w",
        "marginal_resource_need_k",
        "source_readiness",
        "source_ids",
    }
    for row in units:
        assert required_unit_fields.issubset(row)
    for row in programs:
        assert required_program_fields.issubset(row)


def test_v5_open_data_and_scenario_controls_are_forecast_affecting():
    sources = load_json("source_registry.json")["rows"]
    source_ids = {row["source_id"] for row in sources}
    assert OPEN_CONTEXT_SOURCES.issubset(source_ids)

    open_context = load_json("command_center_context.json")["openContext"]
    assert {"respiratory_activity_index", "aqhi_max_proxy", "school_break_flag", "pediatric_population_index"}.issubset(open_context[0])

    inpatient_forecast = load_json("inpatient_intelligence.json")["forecast"]
    ambulatory_forecast = load_json("ambulatory_intelligence.json")["forecast"]
    for key in ["respiratory_open_data_lift", "aqhi_smoke_open_data_lift", "calendar_open_data_lift"]:
        assert any(float(row[key]) > 0 for row in inpatient_forecast), key
        assert any(float(row[key]) > 0 for row in ambulatory_forecast), key

    scenario = load_json("scenario_lab.json")
    domains = {row["domain"] for row in scenario["controlRanges"]}
    assert {"inpatient", "ambulatory", "HR/workforce", "finance/resource", "open data"}.issubset(domains)
    assert all({"impact_per_unit", "cost_k_per_unit", "sensitivity_low", "sensitivity_high"}.issubset(row) for row in scenario["controlRanges"])


def test_v5_model_cards_have_wiring_fields():
    models = load_json("model_registry.json")["rows"]
    required = {
        "source_fields",
        "feature_families",
        "proxy_coefficients",
        "threshold_logic",
        "calibration",
        "validation",
        "drift",
        "alert_burden",
        "source_lineage",
        "panels_using_it",
        "source_ids",
    }
    for model in models:
        assert required.issubset(model)
        json.loads(model["proxy_coefficients"])


def test_v5_decision_support_readiness_and_signal_simulations():
    command = load_json("command_center_context.json")
    for row in command["interpretations"]:
        assert {"what_changed", "likely_drivers", "review_action", "confidence", "confidence_reason", "next_step"}.issubset(row)

    readiness_categories = {row["category"] for row in command["implementationReadiness"]}
    assert {
        "synthetic_variable",
        "real_data_feed",
        "metric_definition",
        "coefficient",
        "pending_model",
        "validation",
        "governance",
        "dependency",
    }.issubset(readiness_categories)
    assert any(row["real_data_status"] in {"blocked", "not_connected"} for row in command["implementationReadiness"])

    labels = {row["label"] for row in command["signalSimulations"]}
    assert {
        "Triage and LOS orchestration",
        "Rare-disease case finding",
        "General deterioration early warning",
        "NEC recognition rehearsal",
    } == labels
    for row in command["signalSimulations"]:
        assert {"coefficients", "factors", "timeline", "implementation_steps", "clinical_boundary", "threshold_logic"}.issubset(row)
        assert len(row["coefficients"]) >= 5
        assert len(row["factors"]) >= 4
        assert "identifier" in row["cohort"] or "identifiable" in row["cohort"]


def test_v5_classification_and_source_readiness_layers_present():
    payloads = [
        load_json("metric_registry.json")["rows"],
        load_json("model_registry.json")["rows"],
        load_json("panel_lineage.json")["rows"],
        load_json("inpatient_intelligence.json")["unitDetails"],
        load_json("ambulatory_intelligence.json")["programDetails"],
    ]
    text = " ".join(str(row.get("classification", "")) for payload in payloads for row in payload).lower()
    for layer in ["direct", "derived", "modelled", "open data", "hr", "finance"]:
        assert layer in text

    readiness = load_json("direct_link_validation.json")["rows"]
    assert {"green", "yellow", "gray"}.issubset({row["stoplight"] for row in readiness})


def test_v5_contains_no_obvious_direct_identifiers():
    combined = "\n".join(walk_strings([load_json(name) for name in REQUIRED_JSON]))
    forbidden = [
        r"\bMRN\b",
        r"\bhealth card\b",
        r"\bphone\b",
        r"\baddress\b",
        r"\bdate of birth\b",
        r"\bpatient name\b",
    ]
    for pattern in forbidden:
        assert not re.search(pattern, combined, flags=re.IGNORECASE), pattern
