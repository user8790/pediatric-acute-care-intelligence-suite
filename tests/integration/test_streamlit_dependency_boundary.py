from pathlib import Path


def test_snowflake_streamlit_path_has_no_advanced_des_references():
    forbidden = ("simpy", "ciw")
    for path in Path("apps/snowflake_streamlit").rglob("*"):
        if path.is_file() and path.suffix.lower() in {".py", ".yml", ".yaml", ".md", ".txt"}:
            text = path.read_text(encoding="utf-8").lower()
            for item in forbidden:
                assert item not in text, f"{item} leaked into {path}"


def test_streamlit_v2_sample_data_available():
    sample_dir = Path("apps/snowflake_streamlit/shared/sample_data")
    required = [
        "v2_inpatient_mission.csv",
        "v2_inpatient_flow.csv",
        "v2_inpatient_forecasts.csv",
        "v2_inpatient_scenarios.csv",
        "v2_ambulatory_mission.csv",
        "v2_ambulatory_access.csv",
        "v2_ambulatory_forecasts.csv",
        "v2_ambulatory_scenarios.csv",
        "v2_model_registry.csv",
        "v2_coefficient_registry.csv",
        "v2_data_quality.csv",
        "v3_source_registry.csv",
        "v3_direct_link_validation.csv",
        "v3_metric_registry.csv",
        "v3_model_registry.csv",
        "v3_panel_lineage.csv",
        "v3_learning_system_events.csv",
        "v3_gatekeeper_issues.csv",
        "v3_governance_approvals.csv",
        "v3_warning_logic_registry.csv",
        "v3_coefficient_registry.csv",
        "v3_data_quality_rules.csv",
        "v3_validation_drift.csv",
        "v3_release_rollback.csv",
        "v3_scenarios.csv",
        "v3_inpatient_unit_pressure.csv",
        "v3_ambulatory_program_access.csv",
    ]
    for name in required:
        path = sample_dir / name
        assert path.exists(), name
        assert path.stat().st_size > 0
