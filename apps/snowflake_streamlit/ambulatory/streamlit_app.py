from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.snowflake_streamlit.shared.lib.common import (  # noqa: E402
    SYNTHETIC_NOTICE,
    load_table_or_sample,
    safe_metric,
    status_panel,
    try_store_scenario,
)

st.set_page_config(page_title="Ambulatory Access Intelligence Centre", layout="wide")

ACCESS_SQL = """
SELECT *
FROM PEDIATRIC_AHA_DEMO.MART.MART_AMBULATORY_ACCESS_MISSION_CONTROL
ORDER BY site_id, program
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
FROM PEDIATRIC_AHA_DEMO.MART.MART_AMBULATORY_SIMULATION_SUMMARY
ORDER BY final_backlog DESC
"""

access = load_table_or_sample(ACCESS_SQL, "ambulatory_access.csv")
quality = load_table_or_sample(QUALITY_SQL, "data_quality_summary.csv")
models = load_table_or_sample(MODEL_SQL, "model_registry.csv")
sim = load_table_or_sample(SIM_SQL, "ambulatory_simulation_results.csv")
status_panel(access.source)

st.title("Ambulatory Access Intelligence Centre")
st.caption(SYNTHETIC_NOTICE)

if access.data.empty:
    st.error("No ambulatory access data found. Run the Snowflake setup SQL or generate local samples.")
    st.stop()

site_options = ["All sites"] + sorted(access.data["site_id"].dropna().astype(str).unique().tolist())
program_options = ["All programs"] + sorted(access.data["program"].dropna().astype(str).unique().tolist())
site = st.sidebar.selectbox("Site", site_options)
program = st.sidebar.selectbox("Program", program_options)

view = access.data
if site != "All sites":
    view = view[view["site_id"].astype(str) == site]
if program != "All programs":
    view = view[view["program"].astype(str) == program]

tabs = st.tabs(["Mission Control", "Access Detail", "Forecasts", "Simulation Lab", "Data Quality", "Model Registry / Methods"])

with tabs[0]:
    st.subheader("Access mission control")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        safe_metric("Waitlist", int(view["waitlist_total"].sum()))
    with c2:
        safe_metric("Median wait", f"{int(view['median_wait_days'].median())} days")
    with c3:
        safe_metric("Third next available", f"{int(view['third_next_available_days'].median())} days")
    with c4:
        safe_metric("Urgent breach risk", f"{view['urgent_breach_risk'].mean() * 100:.1f}%")
    st.dataframe(view, use_container_width=True, hide_index=True)

with tabs[1]:
    st.subheader("Referral, waitlist, and clinic utilization detail")
    st.bar_chart(view.set_index("program")[["waitlist_total", "waitlist_over_target"]])
    st.dataframe(view, use_container_width=True, hide_index=True)

with tabs[2]:
    st.subheader("Backlog forecast")
    st.write("Forecast tables can be populated from Snowflake model-output tables or the synthetic generator.")
    st.line_chart(view.set_index("program")[["median_wait_days", "p90_wait_days"]])

with tabs[3]:
    st.subheader("Simulation lab")
    c1, c2, c3 = st.columns(3)
    sessions = c1.slider("Added clinic sessions per week", 0, 20, 5)
    virtual = c2.slider("Virtual-care conversion share", 0, 40, 12)
    reminder = c3.slider("Reminder/navigation coverage", 0, 100, 50)
    result = {
        "scenario_name": "Streamlit ambulatory what-if",
        "added_sessions": sessions,
        "virtual_conversion_pct": virtual,
        "reminder_coverage_pct": reminder,
        "estimated_backlog_delta": -1 * (sessions * 38 + virtual * 5 + reminder * 2),
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

