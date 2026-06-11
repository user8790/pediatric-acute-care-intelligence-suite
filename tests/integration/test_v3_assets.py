import json
import re
from pathlib import Path


V3_DIR = Path("apps/showcase/public/data/v3")

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
]

REQUIRED_MODELS = {
    "INPT_OCCUPANCY_FORECAST",
    "ED_BOARDING_FORECAST",
    "DISCHARGE_BY_TIME_BAND",
    "PICU_NICU_PRESSURE",
    "OR_CANCELLATION_RISK",
    "AMB_REFERRAL_DEMAND_FORECAST",
    "AMB_BACKLOG_FORECAST",
    "NO_SHOW_LATE_CANCEL_RISK",
    "URGENT_WAITLIST_BREACH_RISK",
    "DIAGNOSTIC_READINESS_RISK",
    "PEDIATRIC_EARLY_WARNING_SIGNAL",
    "SEPSIS_SURVEILLANCE_SIGNAL",
    "RARE_DISEASE_CASE_FINDING_SIGNAL",
    "READMISSION_REVISIT_RISK",
    "LONG_STAY_RISK",
}

REQUIRED_WRITEBACK_TABLES = {
    "APP.SCENARIO_RUN_LOG",
    "APP.USER_ANNOTATION",
    "APP.WARNING_ACKNOWLEDGEMENT",
    "APP.METRIC_ISSUE_FLAG",
    "APP.MODEL_REVIEW_NOTE",
    "APP.GOVERNANCE_DECISION",
    "APP.VALIDATION_REVIEW",
    "APP.PANEL_FEEDBACK",
    "APP.HUDDLE_REVIEW_EVENT",
    "APP.LEARNING_SYSTEM_OUTCOME_REVIEW",
}

REQUIRED_DOCS = [
    "docs/v3_product_vision.md",
    "docs/v3_frontier_platform_architecture.md",
    "docs/v3_connectcare_realistic_synthetic_wiring.md",
    "docs/v3_snowflake_learning_system_layer.md",
    "docs/v3_gatekeeper_control_plane.md",
    "docs/v3_direct_derived_modelled_classification.md",
    "docs/v3_direct_link_validation_stoplights.md",
    "docs/v3_model_governance_and_cards.md",
    "docs/v3_future_real_data_mapping.md",
    "docs/v3_snowflake_deployment_snowsight_no_cli.md",
    "docs/v3_showcase_demo_script.md",
    "docs/v3_streamlit_user_guide.md",
    "docs/v3_testing_report.md",
    "docs/v3_known_limitations_and_next_steps.md",
]


def load_json(name: str):
    return json.loads((V3_DIR / name).read_text(encoding="utf-8"))


def test_v3_json_assets_exist_and_are_non_empty():
    for name in REQUIRED_JSON:
        path = V3_DIR / name
        assert path.exists(), name
        assert load_json(name)


def test_v3_source_and_readiness_contract():
    sources = load_json("source_registry.json")["rows"]
    readiness = load_json("direct_link_validation.json")["rows"]
    assert len(sources) >= 20
    assert len(readiness) == len(sources)
    source_ids = {row["source_id"] for row in sources}
    assert {"SRC_UNIT_CENSUS", "SRC_REFERRAL", "SRC_MODEL_OUTPUT", "SRC_LEARNING_MEMORY"}.issubset(source_ids)
    required_readiness = {
        "source_view_present",
        "field_populated",
        "freshness",
        "row_count",
        "timestamp_logic",
        "referential_integrity",
        "metric_definition_approved",
        "small_cell_suppression",
        "overall_readiness",
    }
    for row in readiness:
        assert required_readiness.issubset(row)


def test_v3_metric_panel_classification_layers_present():
    metrics = load_json("metric_registry.json")["rows"]
    panels = load_json("panel_lineage.json")["rows"]
    classifications = {str(row["classification"]).lower() for row in metrics + panels}
    assert {"direct", "derived", "modelled"}.issubset(classifications)
    assert all("caveat" in row for row in panels)
    assert all("freshness" in row for row in panels)


def test_v3_model_registry_has_required_assets_and_governance_fields():
    rows = load_json("model_registry.json")["rows"]
    ids = {row["asset_id"] for row in rows}
    assert REQUIRED_MODELS == ids
    required = {
        "asset_id",
        "name",
        "domain",
        "output_type",
        "intended_use",
        "not_intended_use",
        "source_data",
        "features",
        "model_class",
        "training_config_window",
        "validation_window",
        "cadence",
        "calibration_status",
        "drift_status",
        "subgroup_performance",
        "thresholds",
        "alert_burden",
        "false_positive_false_negative_review",
        "governance_status",
        "deployment_status",
        "rollback_plan",
        "synthetic_evidence",
    }
    for row in rows:
        assert required.issubset(row)
        assert "clinical" in row["not_intended_use"].lower()


def test_v3_learning_system_writeback_shape():
    memory = load_json("learning_system_memory.json")
    table_names = {row["table_name"] for row in memory["writebackTables"]}
    assert REQUIRED_WRITEBACK_TABLES == table_names
    required_event_fields = {
        "event_id",
        "event_type",
        "created_at",
        "created_by",
        "app_area",
        "site_id",
        "unit_or_program",
        "related_ids",
        "status",
        "severity",
        "note",
        "payload_json",
        "synthetic_demo_flag",
    }
    for event in memory["events"]:
        assert required_event_fields.issubset(event)


def test_v3_assets_do_not_contain_direct_identifiers():
    text = "\n".join(path.read_text(encoding="utf-8") for path in V3_DIR.glob("*.json"))
    forbidden_patterns = [
        r"\bMRN\b",
        r"health[- ]?card",
        r"health number",
        r"\bphone\b",
        r"\baddress\b",
        r"\bpatient_name\b",
        r"\bfirst_name\b",
        r"\blast_name\b",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, text, flags=re.IGNORECASE), pattern


def test_v3_docs_exist_and_retain_safety_language():
    for doc in REQUIRED_DOCS:
        path = Path(doc)
        assert path.exists(), doc
        text = path.read_text(encoding="utf-8").lower()
        assert "synthetic" in text
        assert "not validated for clinical decision-making" in text
