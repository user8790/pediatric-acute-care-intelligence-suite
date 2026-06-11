from pathlib import Path


SQL_DIR = Path("snowflake/sql")


def test_snowflake_sql_scripts_00_to_12_exist():
    for index in range(13):
        matches = list(SQL_DIR.glob(f"{index:02d}_*.sql"))
        assert matches, f"Missing SQL script {index:02d}"


def test_v3_snowflake_sql_scripts_00_to_15_exist():
    required = [
        "00_context_and_roles_template.sql",
        "01_create_database_schema.sql",
        "02_create_synthetic_source_tables.sql",
        "03_generate_synthetic_connectcare_realistic_data.sql",
        "04_create_canonical_views.sql",
        "05_create_operational_marts.sql",
        "06_create_model_and_prediction_tables.sql",
        "07_create_metric_and_coefficient_registry.sql",
        "08_create_direct_link_validation.sql",
        "09_create_gatekeeper_control_plane_tables.sql",
        "10_create_learning_system_writeback_tables.sql",
        "11_create_scenario_tables_and_marts.sql",
        "12_create_data_quality_checks.sql",
        "13_create_app_metadata.sql",
        "14_create_streamlit_objects_optional.sql",
        "15_smoke_tests.sql",
    ]
    for name in required:
        assert (SQL_DIR / name).exists(), name


def test_v2_sql_contains_required_objects():
    sql_11 = (SQL_DIR / "11_v2_scenario_marts.sql").read_text(encoding="utf-8")
    sql_12 = (SQL_DIR / "12_v2_forecast_marts.sql").read_text(encoding="utf-8")
    required = [
        "DIM_V2_COEFFICIENT_REGISTRY",
        "MART_V2_INPATIENT_SCENARIO",
        "MART_V2_AMBULATORY_SCENARIO",
        "SCENARIO_RUN_LOG",
        "DIM_V2_MODEL_REGISTRY",
        "MART_V2_INPATIENT_MISSION_CONTROL",
        "MART_V2_INPATIENT_FORECAST",
        "MART_V2_AMBULATORY_MISSION_CONTROL",
        "MART_V2_AMBULATORY_FORECAST",
        "MART_V2_DATA_QUALITY_STATUS",
    ]
    combined = f"{sql_11}\n{sql_12}"
    for object_name in required:
        assert object_name in combined


def test_v3_sql_contains_required_objects():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in SQL_DIR.glob("*.sql"))
    required = [
        "RAW_SYNTH",
        "CANONICAL",
        "MART",
        "MODEL",
        "CONFIG",
        "GOVERNANCE",
        "APP",
        "QUALITY",
        "OPEN_DATA",
        "V3_SOURCE_REGISTRY",
        "V3_DIRECT_LINK_VALIDATION",
        "V3_METRIC_REGISTRY",
        "V3_MODEL_REGISTRY",
        "V3_PANEL_LINEAGE",
        "V3_GATEKEEPER_ISSUE",
        "V3_GATEKEEPER_DECISION",
        "SCENARIO_RUN_LOG",
        "USER_ANNOTATION",
        "WARNING_ACKNOWLEDGEMENT",
        "METRIC_ISSUE_FLAG",
        "MODEL_REVIEW_NOTE",
        "GOVERNANCE_DECISION",
        "VALIDATION_REVIEW",
        "PANEL_FEEDBACK",
        "HUDDLE_REVIEW_EVENT",
        "LEARNING_SYSTEM_OUTCOME_REVIEW",
    ]
    for object_name in required:
        assert object_name in combined


def test_snowsight_doc_mentions_v2_sql_order():
    doc = Path("docs/README_DEPLOY_SNowsight.md").read_text(encoding="utf-8")
    assert "11_v2_scenario_marts.sql" in doc
    assert "12_v2_forecast_marts.sql" in doc
    assert "no local" in doc.lower()
