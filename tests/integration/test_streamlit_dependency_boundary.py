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
    ]
    for name in required:
        path = sample_dir / name
        assert path.exists(), name
        assert path.stat().st_size > 0
