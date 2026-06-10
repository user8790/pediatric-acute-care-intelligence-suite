from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        first_present_column,
        format_pct,
        load_table_or_sample,
        panel_note,
        safe_metric,
        status_panel,
        try_store_scenario,
    )
except Exception:  # pragma: no cover - local repo fallback
    from apps.snowflake_streamlit.shared.lib.common import (  # noqa: E402
        SYNTHETIC_NOTICE,
        first_present_column,
        format_pct,
        load_table_or_sample,
        panel_note,
        safe_metric,
        status_panel,
        try_store_scenario,
    )

st.set_page_config(page_title="Inpatient Command Centre v2", layout="wide")

MISSION_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_INPATIENT_MISSION_CONTROL ORDER BY site_id"
FLOW_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_INPATIENT_FLOW ORDER BY site_id, unit_id"
FORECAST_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_INPATIENT_FORECAST ORDER BY site_id, horizon_hours"
SCENARIO_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_INPATIENT_SCENARIO ORDER BY boarder_hours_mean"
OR_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_INPATIENT_OR_PACU ORDER BY date DESC, site_id"
HIGH_RESOURCE_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_INPATIENT_HIGH_RESOURCE ORDER BY site_id, service_line"
STAFFING_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_INPATIENT_STAFFING ORDER BY site_id, unit_id"
DISCHARGE_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_INPATIENT_DISCHARGE_BARRIERS ORDER BY active_count DESC"
HANDSHAKE_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_INPATIENT_HANDSHAKE ORDER BY ed_admissions_awaiting_bed DESC"
SAFETY_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_INPATIENT_SAFETY ORDER BY site_id, unit_id"
QUALITY_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_DATA_QUALITY_STATUS ORDER BY table_name, check_name"
MODEL_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MODEL.DIM_V2_MODEL_REGISTRY ORDER BY model_id"
COEFFICIENT_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MODEL.DIM_V2_COEFFICIENT_REGISTRY ORDER BY coefficient_name"

mission = load_table_or_sample(MISSION_SQL, "v2_inpatient_mission.csv")
flow = load_table_or_sample(FLOW_SQL, "v2_inpatient_flow.csv")
forecasts = load_table_or_sample(FORECAST_SQL, "v2_inpatient_forecasts.csv")
scenarios = load_table_or_sample(SCENARIO_SQL, "v2_inpatient_scenarios.csv")
or_pacu = load_table_or_sample(OR_SQL, "v2_inpatient_or_pacu.csv")
high_resource = load_table_or_sample(HIGH_RESOURCE_SQL, "v2_inpatient_high_resource.csv")
staffing = load_table_or_sample(STAFFING_SQL, "v2_inpatient_staffing.csv")
discharge = load_table_or_sample(DISCHARGE_SQL, "v2_inpatient_discharge_barriers.csv")
handshake = load_table_or_sample(HANDSHAKE_SQL, "v2_inpatient_handshake.csv")
safety = load_table_or_sample(SAFETY_SQL, "v2_inpatient_safety.csv")
quality = load_table_or_sample(QUALITY_SQL, "v2_data_quality.csv")
models = load_table_or_sample(MODEL_SQL, "v2_model_registry.csv")
coefficients = load_table_or_sample(COEFFICIENT_SQL, "v2_coefficient_registry.csv")

last_refresh = None
if "data_freshness" in mission.data.columns and not mission.data.empty:
    last_refresh = str(mission.data["data_freshness"].iloc[0])

status_panel(
    mission.source,
    last_refresh=last_refresh,
    mart_available=mission.source.startswith("Snowflake"),
    scenario_write_available=mission.source.startswith("Snowflake"),
)

st.title("Inpatient Command Centre v2")
st.caption(SYNTHETIC_NOTICE)

if mission.data.empty:
    st.error("No inpatient mission-control data found. Run the v2 Snowflake SQL setup or generate local samples.")
    st.stop()


def scope_site(data: pd.DataFrame, site_value: str) -> pd.DataFrame:
    if data.empty or site_value == "All sites" or "site_id" not in data.columns:
        return data
    return data[data["site_id"].astype(str) == site_value]


def numeric_sum(data: pd.DataFrame, column: str) -> float:
    if data.empty or column not in data.columns:
        return 0.0
    return float(pd.to_numeric(data[column], errors="coerce").fillna(0).sum())


def numeric_mean(data: pd.DataFrame, column: str) -> float:
    if data.empty or column not in data.columns:
        return 0.0
    return float(pd.to_numeric(data[column], errors="coerce").dropna().mean() or 0.0)


site_options = ["All sites"] + sorted(mission.data["site_id"].dropna().astype(str).unique().tolist())
persona = st.sidebar.selectbox(
    "Role view",
    ["Executive", "Site operations leader", "Patient-flow leader", "Unit manager", "Analytics / informatics / AI team"],
)
site = st.sidebar.selectbox("Site", site_options)
horizon = st.sidebar.selectbox("Planning horizon", ["Now", "Next 6 hours", "Next 24 hours", "Next 72 hours", "Next 14 days"])
st.sidebar.caption("Patient-level rows are suppressed by default. All displayed data is synthetic and aggregate.")

view = scope_site(mission.data, site)
flow_view = scope_site(flow.data, site)
forecast_view = scope_site(forecasts.data, site)
or_view = scope_site(or_pacu.data, site)
hr_view = scope_site(high_resource.data, site)
staffing_view = scope_site(staffing.data, site)
discharge_view = scope_site(discharge.data, site)
handshake_view = scope_site(handshake.data, site)
safety_view = scope_site(safety.data, site)

tabs = st.tabs(
    [
        "Mission Control",
        "Bed Flow",
        "Forecasts",
        "OR/PICU/NICU",
        "Staffing and Discharge Reliability",
        "Scenario Lab",
        "Data Quality",
        "Model Registry / Methods",
    ]
)

with tabs[0]:
    st.subheader("Current posture")
    totals = view.sum(numeric_only=True)
    census = float(totals.get("census", 0))
    effective_beds = max(float(totals.get("effective_beds", 1)), 1.0)
    physical_beds = float(totals.get("physical_beds", 0))
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        safe_metric("Occupancy", format_pct(census / effective_beds), "+2.4 pts")
    with c2:
        safe_metric("Effective beds", int(effective_beds), f"{int(physical_beds - effective_beds)} constrained")
    with c3:
        safe_metric("ED boarders", int(totals.get("ed_boarders", 0)), "+4")
    with c4:
        safe_metric("Predicted discharges", int(totals.get("predicted_discharges", 0)), "-3 vs target")
    with c5:
        safe_metric("Prob >95%", format_pct(numeric_mean(view, "prob_above_95")), "+8 pts")

    panel_note(
        "Interpretation",
        f"{persona} view, {horizon}: start with effective capacity, boarders, discharge reliability, and PICU/NICU pressure. Scenario options are planning comparisons, not directives.",
    )
    if not view.empty:
        driver_cols = [column for column in ["top_driver_1", "top_driver_2", "top_driver_3"] if column in view.columns]
        if driver_cols:
            st.write("Top drivers")
            st.dataframe(view[["site_id", *driver_cols]].drop_duplicates(), use_container_width=True, hide_index=True)
    if not flow_view.empty:
        fig = px.bar(
            flow_view,
            x="unit_name" if "unit_name" in flow_view.columns else "service_line",
            y="occupancy_pct",
            color="staffing_gap_pct" if "staffing_gap_pct" in flow_view.columns else None,
            labels={"occupancy_pct": "Occupancy", "staffing_gap_pct": "Staffing gap"},
            title="Unit occupancy and staffing pressure",
        )
        fig.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.subheader("Bed flow and ED-to-inpatient handshake")
    if not flow_view.empty:
        fig = px.imshow(
            flow_view.pivot_table(
                index="unit_name" if "unit_name" in flow_view.columns else "service_line",
                values="occupancy_pct",
                aggfunc="mean",
            ),
            text_auto=".0%",
            aspect="auto",
            color_continuous_scale="Tealrose",
            title="Unit pressure heatmap",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(flow_view, use_container_width=True, hide_index=True)
    if not handshake_view.empty:
        c1, c2 = st.columns([1, 1])
        with c1:
            fig = px.bar(
                handshake_view,
                x="unit_name" if "unit_name" in handshake_view.columns else "unit_id",
                y="ed_admissions_awaiting_bed",
                title="ED admissions awaiting bed",
            )
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.scatter(
                handshake_view,
                x="decision_to_bed_median_min",
                y="bed_to_arrival_median_min",
                size="ed_admissions_awaiting_bed",
                hover_name="unit_name" if "unit_name" in handshake_view.columns else None,
                title="Decision-to-bed versus bed-to-arrival",
            )
            st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    st.subheader("Forecasts and uncertainty")
    if not forecast_view.empty:
        fig = go.Figure()
        for site_id, site_forecast in forecast_view.groupby("site_id" if "site_id" in forecast_view.columns else forecast_view.index):
            ordered = site_forecast.sort_values("horizon_hours")
            fig.add_trace(go.Scatter(x=ordered["horizon_hours"], y=ordered["p90"], line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(
                go.Scatter(
                    x=ordered["horizon_hours"],
                    y=ordered["p10"],
                    fill="tonexty",
                    line=dict(width=0),
                    name=f"{site_id} interval",
                    hoverinfo="skip",
                )
            )
            fig.add_trace(go.Scatter(x=ordered["horizon_hours"], y=ordered["prediction"], mode="lines+markers", name=str(site_id)))
        fig.add_hline(y=0.95, line_dash="dash", line_color="#a23a42", annotation_text="95% threshold")
        fig.update_layout(title="Occupancy forecast ribbon", yaxis_tickformat=".0%", xaxis_title="Horizon hours")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(forecast_view, use_container_width=True, hide_index=True)
    panel_note(
        "Model caveat",
        "Forecasts are synthetic v2 model outputs. Production use would require local temporal validation, calibration, drift monitoring, and governance approval.",
    )

with tabs[3]:
    st.subheader("OR/PACU and high-resource flow")
    c1, c2 = st.columns([1, 1])
    with c1:
        if not or_view.empty:
            date_col = first_present_column(or_view, ["date", "case_date"])
            if date_col:
                recent_or = or_view.sort_values(date_col).tail(30)
                fig = px.line(recent_or, x=date_col, y=["post_op_bed_demand", "elective_cases", "urgent_cases"], title="Procedural demand and post-op bed need")
                st.plotly_chart(fig, use_container_width=True)
            st.dataframe(or_view.tail(20), use_container_width=True, hide_index=True)
    with c2:
        if not hr_view.empty:
            fig = px.bar(hr_view, x="service_line", y=["occupied", "high_resource_beds"], barmode="group", color_discrete_sequence=["#176b87", "#f2a65a"], title="PICU/NICU occupied versus capacity")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(hr_view, use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("Staffing and discharge reliability")
    c1, c2 = st.columns([1, 1])
    with c1:
        if not staffing_view.empty:
            fig = px.scatter(
                staffing_view,
                x="effective_beds_lost",
                y="workload_index",
                size="required_hours",
                hover_name="unit_name" if "unit_name" in staffing_view.columns else None,
                title="Staffing/workload pressure matrix",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(staffing_view, use_container_width=True, hide_index=True)
    with c2:
        if not discharge_view.empty:
            fig = px.bar(discharge_view, x="barrier", y="active_count", color="median_age_hours", title="Discharge barriers and ageing")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(discharge_view, use_container_width=True, hide_index=True)
    if not safety_view.empty:
        st.caption("Safety and reliability signals are synthetic aggregate planning indicators only.")
        st.dataframe(safety_view, use_container_width=True, hide_index=True)

with tabs[5]:
    st.subheader("Scenario lab")
    if scenarios.data.empty:
        st.warning("No v2 scenario grid available.")
    else:
        scenario_name = st.selectbox("Precomputed scenario", scenarios.data["scenario_name"].astype(str).tolist())
        selected = scenarios.data[scenarios.data["scenario_name"].astype(str) == scenario_name].iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            safe_metric("Boarder hours", int(selected.get("boarder_hours_mean", 0)))
        with c2:
            safe_metric("Bed shortage hours", int(selected.get("bed_shortage_hours", 0)))
        with c3:
            safe_metric("Discharge reliability", format_pct(float(selected.get("discharge_reliability", 0))))
        with c4:
            safe_metric("Cancellation risk", format_pct(float(selected.get("elective_cancellation_risk", 0))))
        fig = px.scatter(
            scenarios.data,
            x="impact_score",
            y="effort_score",
            size="boarder_hours_mean",
            color="operational_risk_score",
            hover_name="scenario_name",
            title="Scenario frontier: impact, effort, risk, and boarder hours",
        )
        st.plotly_chart(fig, use_container_width=True)
        stress = st.slider("Bounded demand stress sensitivity", 0.85, 1.20, 1.0, 0.01)
        adjusted = float(selected.get("boarder_hours_mean", 0)) * stress
        st.caption(f"Deterministic sensitivity fallback around precomputed grid: adjusted boarder hours {adjusted:.0f}.")
        payload = {
            "scenario_name": scenario_name,
            "app": "inpatient_v2",
            "site": site,
            "persona": persona,
            "horizon": horizon,
            "boarder_hours_mean": selected.get("boarder_hours_mean", 0),
            "demand_stress": stress,
        }
        if st.button("Store scenario run"):
            st.success(try_store_scenario("PEDIATRIC_AHA_DEMO.APP.SCENARIO_RUN_LOG", payload))
        st.dataframe(scenarios.data, use_container_width=True, hide_index=True)

with tabs[6]:
    st.subheader("Data quality")
    if not quality.data.empty:
        status_col = "status" if "status" in quality.data.columns else None
        if status_col:
            fig = px.histogram(quality.data, x=status_col, color=status_col, title="Quality check status")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(quality.data, use_container_width=True, hide_index=True)
    panel_note(
        "Identifier boundary",
        "The v2 synthetic generator avoids names, MRNs, health numbers, direct addresses, phone numbers, and direct identifiers. Future real-data mapping goes through curated governed views.",
    )

with tabs[7]:
    st.subheader("Model registry and methods")
    if not models.data.empty:
        st.dataframe(models.data, use_container_width=True, hide_index=True)
    if not coefficients.data.empty:
        fig = px.bar(coefficients.data.head(20), x="coefficient_name", y="default_value", title="Coefficient registry")
        fig.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(coefficients.data, use_container_width=True, hide_index=True)
    panel_note(
        "Methods caveat",
        "Streamlit/Snowflake uses SQL-precomputed scenario tables, coefficient registries, Snowflake-compatible analytics packages, and deterministic fallbacks. Advanced simulation packages are not required in this path.",
    )
