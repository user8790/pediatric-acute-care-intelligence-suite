from pathlib import Path


SQL_DIR = Path("snowflake/sql")


def test_snowflake_sql_scripts_00_to_12_exist():
    for index in range(13):
        matches = list(SQL_DIR.glob(f"{index:02d}_*.sql"))
        assert matches, f"Missing SQL script {index:02d}"


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


def test_snowsight_doc_mentions_v2_sql_order():
    doc = Path("docs/README_DEPLOY_SNowsight.md").read_text(encoding="utf-8")
    assert "11_v2_scenario_marts.sql" in doc
    assert "12_v2_forecast_marts.sql" in doc
    assert "no local" in doc.lower()
