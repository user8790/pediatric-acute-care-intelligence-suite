from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[3]
APP_DIR = Path(__file__).resolve().parent
for candidate in (
    APP_DIR / "lib",
    APP_DIR / "shared" / "lib",
    APP_DIR.parent / "shared" / "lib",
    ROOT,
):
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

try:
    from common import (  # type: ignore  # noqa: E402
        SYNTHETIC_NOTICE,
        format_pct,
        load_table_or_sample,
        safe_metric,
        status_panel,
        try_store_scenario,
    )
except Exception:  # pragma: no cover - local repo fallback
    from apps.snowflake_streamlit.shared.lib.common import (  # noqa: E402
        SYNTHETIC_NOTICE,
        format_pct,
        load_table_or_sample,
        safe_metric,
        status_panel,
        try_store_scenario,
    )

st.set_page_config(page_title="Inpatient Command Centre", layout="wide")

MISSION_SQL = """
SELECT *
FROM PEDIATRIC_AHA_DEMO.MART.MART_INPATIENT_MISSION_CONTROL
ORDER BY site_id
"""
QUALITY_SQL = """
SELECT *
FROM PEDIATRIC_AHA_DEMO.MART.MART_DATA_QUALITY_STATUS
ORDER BY table_name, check_name
"""
MODEL_SQL = """
SELECT *
FROM PEDIATRIC_AHA_DEMO.MODEL.DIM_MODEL_REGISTRY
ORDER BY model_id
"""
SIM_SQL = """
SELECT *
FROM PEDIATRIC_AHA_DEMO.MART.MART_INPATIENT_SIMULATION_SUMMARY
ORDER BY boarder_hours_mean DESC
"""

mission = load_table_or_sample(MISSION_SQL, "inpatient_mission.csv")
quality = load_table_or_sample(QUALITY_SQL, "data_quality_summary.csv")
models = load_table_or_sample(MODEL_SQL, "model_registry.csv")
sim = load_table_or_sample(SIM_SQL, "inpatient_simulation_results.csv")
status_panel(mission.source)

st.title("Inpatient Command Centre")
st.caption(SYNTHETIC_NOTICE)

if mission.data.empty:
    st.error("No inpatient mission-control data found. Run the Snowflake setup SQL or generate local samples.")
    st.stop()

persona = st.sidebar.selectbox(
    "Role view",
    ["Executive", "Site operations", "Patient flow", "Unit manager", "Analytics"],
)
site_options = ["All sites"] + sorted(mission.data["site_id"].dropna().astype(str).unique().tolist())
site = st.sidebar.selectbox("Site", site_options)
view = mission.data if site == "All sites" else mission.data[mission.data["site_id"].astype(str) == site]

tabs = st.tabs(
    [
        "Mission Control",
        "Flow Detail",
        "Forecasts",
        "Simulation Lab",
        "Data Quality",
        "Model Registry / Methods",
        "Definitions / Governance",
    ]
)

with tabs[0]:
    st.subheader("Current state")
    c1, c2, c3, c4 = st.columns(4)
    totals = view.sum(numeric_only=True)
    with c1:
        safe_metric("Census", int(totals.get("census", 0)))
    with c2:
        eff_beds = max(float(totals.get("effective_beds", 1)), 1.0)
        safe_metric("Occupancy", format_pct(float(totals.get("census", 0)) / eff_beds))
    with c3:
        safe_metric("ED boarders", int(totals.get("ed_boarders", 0)))
    with c4:
        safe_metric("Predicted discharges", int(totals.get("predicted_discharges", 0)))
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.info("Scenario options are planning estimates, not directives.")
    st.caption(f"Current role view: {persona}. Unit-level detail remains aggregate synthetic data.")

with tabs[1]:
    st.subheader("Flow and capacity")
    flow = view[["site_id", "census", "physical_beds", "staffed_beds", "effective_beds", "ed_boarders"]].copy()
    st.bar_chart(flow.set_index("site_id")[["census", "effective_beds", "physical_beds"]])
    st.dataframe(flow, use_container_width=True, hide_index=True)

with tabs[2]:
    st.subheader("Forecast and drivers")
    st.write("Forecast marts are created by SQL setup and can be extended with model-output tables.")
    st.dataframe(view, use_container_width=True, hide_index=True)

with tabs[3]:
    st.subheader("Simulation lab")
    c1, c2 = st.columns(2)
    surge_beds = c1.slider("Additional surge beds", 0, 30, 8)
    discharge_support = c2.slider("Discharge support improvement", 0, 25, 10)
    result = {
        "scenario_name": "Streamlit inpatient what-if",
        "additional_surge_beds": surge_beds,
        "discharge_support_pct": discharge_support,
        "estimated_boarder_hour_delta": -1 * (surge_beds * 2 + discharge_support * 1.5),
    }
    st.write(result)
    if st.button("Store scenario run"):
        st.success(try_store_scenario("PEDIATRIC_AHA_DEMO.APP.SCENARIO_RUN_LOG", result))
    st.dataframe(sim.data, use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("Data quality")
    if not quality.data.empty:
        st.dataframe(quality.data, use_container_width=True, hide_index=True)
    else:
        st.warning("No quality summary available.")

with tabs[5]:
    st.subheader("Model registry and methods")
    st.dataframe(models.data, use_container_width=True, hide_index=True)

with tabs[6]:
    st.subheader("Definitions and governance")
    st.write(
        {
            "Effective beds": "Physical capacity after staffing, isolation, and step-down constraints.",
            "ED boarding": "Admitted ED patients awaiting inpatient bed assignment or arrival.",
            "Safety signals": "Synthetic demonstration indicators only, not clinical decision support.",
            "Future standards path": "FHIR, SMART on FHIR, CDS Hooks, DICOM/ImagingStudy, curated Snowflake views.",
            "Governance rail": "Alberta HIA, TRIPOD+AI, NIST AI RMF, GMLP, subgroup calibration, and audit logs.",
        }
    )
    st.warning("No real patient data is included. Future real-data use requires local governance and validation.")
