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

REQUIRED_SOURCE_VIEWS = {
    "VW_SYNTH_ADT_EVENTS",
    "VW_SYNTH_INPATIENT_ENCOUNTERS",
    "VW_SYNTH_ED_VISITS",
    "VW_SYNTH_BED_STATUS",
    "VW_SYNTH_UNIT_CENSUS_HOURLY",
    "VW_SYNTH_TRANSFER_REQUESTS",
    "VW_SYNTH_PATIENT_CLASS_STATUS",
    "VW_SYNTH_LEVEL_OF_CARE",
    "VW_SYNTH_ISOLATION_STATUS",
    "VW_SYNTH_ORDERS",
    "VW_SYNTH_LAB_RESULTS",
    "VW_SYNTH_IMAGING_ORDERS",
    "VW_SYNTH_MEDICATION_ORDERS",
    "VW_SYNTH_MAR_ADMINISTRATION",
    "VW_SYNTH_RESPIRATORY_SUPPORT",
    "VW_SYNTH_VITAL_SIGNS_AGG",
    "VW_SYNTH_CLINICAL_SCORES",
    "VW_SYNTH_SEPSIS_SCREENING",
    "VW_SYNTH_ALERT_EVENTS",
    "VW_SYNTH_CARE_PLAN_MILESTONES",
    "VW_SYNTH_DISCHARGE_MILESTONES",
    "VW_SYNTH_DISCHARGE_BARRIERS",
    "VW_SYNTH_PHARMACY_DISCHARGE_MED_STATUS",
    "VW_SYNTH_HOME_SUPPORT_STATUS",
    "VW_SYNTH_EQUIPMENT_STATUS",
    "VW_SYNTH_TRANSPORT_STATUS",
    "VW_SYNTH_FAMILY_READINESS_PROXY",
    "VW_SYNTH_OR_CASES",
    "VW_SYNTH_PACU_EVENTS",
    "VW_SYNTH_PROCEDURE_SCHEDULE",
    "VW_SYNTH_PROCEDURE_CANCELLATIONS",
    "VW_SYNTH_POST_OP_BED_DEMAND",
    "VW_SYNTH_REFERRALS",
    "VW_SYNTH_REFERRAL_TRIAGE",
    "VW_SYNTH_WAITLIST_SNAPSHOTS",
    "VW_SYNTH_APPOINTMENTS",
    "VW_SYNTH_CLINIC_SLOTS",
    "VW_SYNTH_CLINIC_TEMPLATES",
    "VW_SYNTH_PROVIDER_AVAILABILITY",
    "VW_SYNTH_NO_SHOW_LATE_CANCEL",
    "VW_SYNTH_OVERDUE_FOLLOWUP",
    "VW_SYNTH_DIAGNOSTIC_READINESS",
    "VW_SYNTH_VIRTUAL_CARE_SUITABILITY",
    "VW_SYNTH_OUTREACH_CLINIC_CAPACITY",
    "VW_SYNTH_STAFFING_ROSTER",
    "VW_SYNTH_STAFFING_GAPS",
    "VW_SYNTH_WORKLOAD_ACUITY",
    "VW_SYNTH_SKILL_MIX",
    "VW_SYNTH_FLOAT_POOL_AVAILABILITY",
    "VW_SYNTH_SAFETY_EVENTS_AGG",
    "VW_SYNTH_READMISSION_REVISIT",
    "VW_SYNTH_DOT_PHRASE_OR_DOC_COMPLETENESS_PROXY",
    "VW_SYNTH_DATA_QUALITY_EVENTS",
    "VW_OPEN_RESPIRATORY_ACTIVITY",
    "VW_OPEN_WEATHER_AQHI",
    "VW_OPEN_POPULATION_DEMOGRAPHICS",
    "VW_OPEN_CALENDAR_HOLIDAY_SCHOOL",
    "VW_OPEN_COMMUNITY_DEMAND_PROXY",
    "VW_MODEL_FEATURE_STORE_SUMMARY",
    "VW_MODEL_PREDICTIONS",
    "VW_MODEL_VALIDATION_RESULTS",
    "VW_MODEL_DRIFT_RESULTS",
    "VW_MODEL_CARD_REGISTRY",
    "VW_METRIC_REGISTRY",
    "VW_WARNING_LOGIC_REGISTRY",
    "VW_PANEL_REGISTRY",
    "VW_COEFFICIENT_REGISTRY",
    "VW_DIRECT_LINKAGE_VALIDATION",
    "VW_LEARNING_SYSTEM_EVENTS",
    "VW_SCENARIO_RUNS",
    "VW_SCENARIO_RESULTS",
    "VW_USER_ANNOTATIONS",
    "VW_GOVERNANCE_APPROVALS",
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
    "docs/v3_tooling_and_package_register.md",
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
    assert len(sources) >= len(REQUIRED_SOURCE_VIEWS)
    assert len(readiness) == len(sources)
    source_views = {row["source_view_name"] for row in sources}
    assert REQUIRED_SOURCE_VIEWS.issubset(source_views)
    required_readiness = {
        "source_view_present",
        "source_view_name",
        "source_domain",
        "field_populated",
        "freshness",
        "row_count",
        "timestamp_logic",
        "referential_integrity",
        "metric_definition_approved",
        "small_cell_suppression",
        "overall_readiness",
        "stoplight",
    }
    for row in readiness:
        assert required_readiness.issubset(row)
    assert {"green", "yellow", "gray"}.issubset({row["stoplight"] for row in readiness})


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
        "related_metric_id",
        "related_model_id",
        "related_panel_id",
        "related_scenario_id",
        "status",
        "severity",
        "note",
        "payload_json",
        "synthetic_demo_flag",
    }
    for event in memory["events"]:
        assert required_event_fields.issubset(event)


def test_v3_gatekeeper_has_expanded_registries():
    gatekeeper = load_json("gatekeeper_control_plane.json")
    for key in [
        "controlPlane",
        "dependencyEdges",
        "issues",
        "approvals",
        "warningLogic",
        "coefficients",
        "dataQualityRules",
        "validationDrift",
        "releaseRollback",
    ]:
        assert key in gatekeeper
        assert gatekeeper[key], key


def test_v3_workspace_has_drilldown_source_layers_and_scenario_controls():
    inpatient = load_json("inpatient_intelligence.json")
    ambulatory = load_json("ambulatory_intelligence.json")
    scenarios = load_json("scenario_lab.json")

    assert len(inpatient["unitDetails"]) >= 12
    assert len(inpatient["unitTimeline"]) >= len(inpatient["unitDetails"]) * 6
    assert len(ambulatory["programDetails"]) >= 6
    assert len(ambulatory["programTimeline"]) >= len(ambulatory["programDetails"]) * 6
    assert {row["domain"] for row in scenarios["baselines"]} == {"inpatient", "ambulatory"}
    assert {row["domain"] for row in scenarios["controlRanges"]} == {"inpatient", "ambulatory"}

    for row in inpatient["unitDetails"] + ambulatory["programDetails"]:
        assert row["source_ids"]
        assert row["primary_metric_ids"]
        assert row["model_ids"]
        assert "synthetic aggregate" in row["caveat"].lower()

    for control in scenarios["controlRanges"]:
        assert control["min"] <= control["default"] <= control["max"]
        assert control["source_id"].startswith("SRC_")


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
