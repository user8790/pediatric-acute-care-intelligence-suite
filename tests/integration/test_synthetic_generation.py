from pathlib import Path

import numpy as np

from packages.core.config import SuiteConfig
from packages.synthetic.generate_synthetic_data import (
    AMBULATORY_FACTS,
    DIMENSIONS,
    INPATIENT_FACTS,
    build_ambulatory,
    build_dimensions,
    build_inpatient,
)


def test_synthetic_builders_cover_required_tables():
    config = SuiteConfig(days=7)
    rng = np.random.default_rng(config.seed)
    dimensions = build_dimensions(config, rng)
    inpatient = build_inpatient(config, dimensions, rng)
    ambulatory = build_ambulatory(config, dimensions, rng)
    assert set(DIMENSIONS).issubset(dimensions.keys())
    assert "FCT_BED_CENSUS_HOURLY" in inpatient
    assert "FCT_WAITLIST_SNAPSHOT" in ambulatory
    assert len(INPATIENT_FACTS) >= 20
    assert len(AMBULATORY_FACTS) >= 15


def test_generated_files_exist_after_demo_generation():
    expected = [
        Path("data/synthetic/dim_site.csv"),
        Path("data/synthetic/fct_bed_census_hourly.csv"),
        Path("apps/showcase/public/demo-data.json"),
        Path("apps/snowflake_streamlit/shared/sample_data/inpatient_mission.csv"),
    ]
    for path in expected:
        assert path.exists(), f"Missing generated artifact {path}"

