from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
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
        format_pct,
        load_table_or_sample,
        panel_note,
        safe_metric,
        status_panel,
        try_store_learning_event,
        try_store_scenario,
    )
except Exception:  # pragma: no cover - local repo fallback
    from apps.snowflake_streamlit.shared.lib.common import (  # noqa: E402
        SYNTHETIC_NOTICE,
        format_pct,
        load_table_or_sample,
        panel_note,
        safe_metric,
        status_panel,
        try_store_learning_event,
        try_store_scenario,
    )

st.set_page_config(page_title="Ambulatory Access Intelligence Centre v2", layout="wide")

MISSION_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_AMBULATORY_MISSION_CONTROL ORDER BY site_id"
ACCESS_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_AMBULATORY_ACCESS ORDER BY site_id, program"
FORECAST_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_AMBULATORY_FORECAST ORDER BY site_id, program, horizon_weeks"
SCENARIO_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_AMBULATORY_SCENARIO ORDER BY final_backlog"
REFERRAL_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_AMBULATORY_REFERRAL_TRIAGE ORDER BY week_start DESC, site_id, program"
SLOT_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_AMBULATORY_CLINIC_TEMPLATE ORDER BY week_start DESC, site_id, program"
FOLLOWUP_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_AMBULATORY_FOLLOWUP ORDER BY site_id, program"
DIAGNOSTIC_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_AMBULATORY_DIAGNOSTIC_DEPENDENCY ORDER BY missing_prerequisite_count DESC"
TRAVEL_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_AMBULATORY_TRAVEL ORDER BY travel_burden_index DESC"
QUALITY_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.MART_V2_DATA_QUALITY_STATUS ORDER BY table_name, check_name"
MODEL_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MODEL.DIM_V2_MODEL_REGISTRY ORDER BY model_id"
COEFFICIENT_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MODEL.DIM_V2_COEFFICIENT_REGISTRY ORDER BY coefficient_name"
V3_READINESS_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.GOVERNANCE.V3_DIRECT_LINK_VALIDATION ORDER BY source_id"
V3_MODEL_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MODEL.V3_MODEL_REGISTRY ORDER BY asset_id"
V3_EVENT_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.APP.V3_LEARNING_SYSTEM_EVENT ORDER BY created_at DESC"
V3_WARNING_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.CONFIG.V3_WARNING_LOGIC_REGISTRY ORDER BY warning_id"

mission = load_table_or_sample(MISSION_SQL, "v2_ambulatory_mission.csv")
access = load_table_or_sample(ACCESS_SQL, "v2_ambulatory_access.csv")
forecasts = load_table_or_sample(FORECAST_SQL, "v2_ambulatory_forecasts.csv")
scenarios = load_table_or_sample(SCENARIO_SQL, "v2_ambulatory_scenarios.csv")
referrals = load_table_or_sample(REFERRAL_SQL, "v2_ambulatory_referrals.csv")
slots = load_table_or_sample(SLOT_SQL, "v2_ambulatory_slots.csv")
followup = load_table_or_sample(FOLLOWUP_SQL, "v2_ambulatory_followup.csv")
diagnostics = load_table_or_sample(DIAGNOSTIC_SQL, "v2_ambulatory_diagnostics.csv")
travel = load_table_or_sample(TRAVEL_SQL, "v2_ambulatory_travel.csv")
quality = load_table_or_sample(QUALITY_SQL, "v2_data_quality.csv")
models = load_table_or_sample(MODEL_SQL, "v2_model_registry.csv")
coefficients = load_table_or_sample(COEFFICIENT_SQL, "v2_coefficient_registry.csv")
v3_readiness = load_table_or_sample(V3_READINESS_SQL, "v3_direct_link_validation.csv")
v3_models = load_table_or_sample(V3_MODEL_SQL, "v3_model_registry.csv")
v3_events = load_table_or_sample(V3_EVENT_SQL, "v3_learning_system_events.csv")
v3_warnings = load_table_or_sample(V3_WARNING_SQL, "v3_warning_logic_registry.csv")

last_refresh = None
if "data_freshness" in mission.data.columns and not mission.data.empty:
    last_refresh = str(mission.data["data_freshness"].iloc[0])

status_panel(
    mission.source,
    last_refresh=last_refresh,
    mart_available=mission.source.startswith("Snowflake"),
    scenario_write_available=mission.source.startswith("Snowflake"),
)

st.title("Ambulatory Access Intelligence Centre v2")
st.caption(SYNTHETIC_NOTICE)

if mission.data.empty:
    st.error("No ambulatory mission-control data found. Run the v2 Snowflake SQL setup or generate local samples.")
    st.stop()


def scope_site(data: pd.DataFrame, site_value: str) -> pd.DataFrame:
    if data.empty or site_value == "All sites" or "site_id" not in data.columns:
        return data
    return data[data["site_id"].astype(str) == site_value]


def scope_program(data: pd.DataFrame, program_value: str) -> pd.DataFrame:
    if data.empty or program_value == "All programs" or "program" not in data.columns:
        return data
    return data[data["program"].astype(str) == program_value]


def numeric_sum(data: pd.DataFrame, column: str) -> float:
    if data.empty or column not in data.columns:
        return 0.0
    return float(pd.to_numeric(data[column], errors="coerce").fillna(0).sum())


def numeric_mean(data: pd.DataFrame, column: str) -> float:
    if data.empty or column not in data.columns:
        return 0.0
    return float(pd.to_numeric(data[column], errors="coerce").dropna().mean() or 0.0)


site_options = ["All sites"] + sorted(mission.data["site_id"].dropna().astype(str).unique().tolist())
program_source = access.data if not access.data.empty and "program" in access.data.columns else referrals.data
program_options = ["All programs"] + sorted(program_source["program"].dropna().astype(str).unique().tolist()) if "program" in program_source.columns else ["All programs"]
persona = st.sidebar.selectbox(
    "Role view",
    ["Executive", "Ambulatory program leader", "Clinic operations leader", "Access hub", "Analytics / informatics / AI team"],
)
site = st.sidebar.selectbox("Site", site_options)
program = st.sidebar.selectbox("Program", program_options)
horizon = st.sidebar.selectbox("Planning horizon", ["Now", "Next 14 days", "Next 26 weeks"])
st.sidebar.caption("Patient-level rows are suppressed by default. All displayed data is synthetic and aggregate.")

view = scope_site(mission.data, site)
access_view = scope_program(scope_site(access.data, site), program)
forecast_view = scope_program(scope_site(forecasts.data, site), program)
referral_view = scope_program(scope_site(referrals.data, site), program)
slot_view = scope_program(scope_site(slots.data, site), program)
followup_view = scope_program(scope_site(followup.data, site), program)
diagnostic_view = scope_program(scope_site(diagnostics.data, site), program)
travel_view = scope_program(scope_site(travel.data, site), program)

tabs = st.tabs(
    [
        "Mission Control",
        "Referral and Triage",
        "Waitlist and Access",
        "Clinic Template",
        "Forecasts",
        "Scenario Lab",
        "Data Quality",
        "Model Registry / Methods",
        "v3 Source Readiness",
        "v3 Predictive Assets",
        "v3 Learning Notes",
    ]
)

with tabs[0]:
    st.subheader("Access mission control")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        safe_metric("Waitlist", int(numeric_sum(view, "waitlist_total")), "+3.8%")
    with c2:
        safe_metric("Over target", int(numeric_sum(view, "waitlist_over_target")), "+110")
    with c3:
        safe_metric("Median wait", f"{numeric_mean(view, 'median_wait_days'):.0f} days", "+5")
    with c4:
        safe_metric("Third next available", f"{numeric_mean(view, 'third_next_available_days'):.0f} days", "-2 projected")
    with c5:
        safe_metric("Urgent breach risk", format_pct(numeric_mean(view, "urgent_breach_risk")), "+4 pts")
    panel_note(
        "Interpretation",
        f"{persona} view, {horizon}: pair waitlist ageing with TNA, no-show-adjusted capacity, diagnostic readiness, and travel-burden context.",
    )
    if not view.empty:
        driver_cols = [column for column in ["top_driver_1", "top_driver_2", "top_driver_3"] if column in view.columns]
        if driver_cols:
            st.write("Top drivers")
            st.dataframe(view[["site_id", *driver_cols]].drop_duplicates(), use_container_width=True, hide_index=True)
    if not access_view.empty:
        fig = px.bar(access_view, x="program", y="waitlist_total", color="urgent_breach_risk", title="Waitlist and urgent breach-risk proxy")
        st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.subheader("Referral and triage intelligence")
    if not referral_view.empty:
        recent = referral_view.sort_values("week_start").tail(80) if "week_start" in referral_view.columns else referral_view
        fig = px.line(recent, x="week_start", y="new_referrals", color="program", title="Referral demand trend")
        st.plotly_chart(fig, use_container_width=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            fig = px.bar(referral_view, x="program", y="urgent_referrals", title="Urgent referral mix")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.scatter(referral_view, x="triage_median_days", y="referral_completeness_pct", size="new_referrals", color="program", title="Triage turnaround and referral completeness")
            fig.update_layout(yaxis_tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(referral_view, use_container_width=True, hide_index=True)

with tabs[2]:
    st.subheader("Waitlist and access")
    if not access_view.empty:
        c1, c2 = st.columns([1, 1])
        with c1:
            fig = px.bar(access_view, x="program", y=["waitlist_total", "waitlist_over_target"], barmode="group", title="Waitlist ageing by program")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.scatter(access_view, x="median_wait_days", y="p90_wait_days", size="waitlist_total", color="urgent_breach_risk", hover_name="program", title="Median and p90 wait-time distribution")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(access_view, use_container_width=True, hide_index=True)

with tabs[3]:
    st.subheader("Clinic template and slot utilization")
    if not slot_view.empty:
        recent_slots = slot_view.sort_values("week_start").tail(80) if "week_start" in slot_view.columns else slot_view
        fig = px.bar(recent_slots, x="program", y=["slots_available", "completed_visits"], barmode="group", title="Available slots and completed visits")
        st.plotly_chart(fig, use_container_width=True)
        fig = px.scatter(
            slot_view,
            x="no_show_rate",
            y="new_visit_share",
            size="slots_available",
            color="provider_constraint",
            hover_name="program",
            title="No-show risk, new/follow-up balance, and provider constraints",
        )
        fig.update_layout(xaxis_tickformat=".0%", yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(slot_view, use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("Forecasts and uncertainty")
    if not forecast_view.empty:
        fig = go.Figure()
        group_key = "program" if program == "All programs" and "program" in forecast_view.columns else "site_id"
        for group, group_forecast in forecast_view.groupby(group_key):
            ordered = group_forecast.sort_values("horizon_weeks")
            fig.add_trace(go.Scatter(x=ordered["horizon_weeks"], y=ordered["p90"], line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(
                go.Scatter(
                    x=ordered["horizon_weeks"],
                    y=ordered["p10"],
                    fill="tonexty",
                    line=dict(width=0),
                    name=f"{group} interval",
                    hoverinfo="skip",
                )
            )
            fig.add_trace(go.Scatter(x=ordered["horizon_weeks"], y=ordered["prediction"], mode="lines+markers", name=str(group)))
        fig.update_layout(title="Backlog forecast ribbon", xaxis_title="Horizon weeks", yaxis_title="Forecast backlog")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(forecast_view, use_container_width=True, hide_index=True)
    panel_note(
        "Model caveat",
        "Forecasts are synthetic v2 model outputs. Production use would require local validation, subgroup calibration, and monitoring.",
    )

with tabs[5]:
    st.subheader("Scenario lab")
    if scenarios.data.empty:
        st.warning("No v2 ambulatory scenario grid available.")
    else:
        scenario_name = st.selectbox("Precomputed scenario", scenarios.data["scenario_name"].astype(str).tolist())
        selected = scenarios.data[scenarios.data["scenario_name"].astype(str) == scenario_name].iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            safe_metric("Final backlog", int(selected.get("final_backlog", 0)))
        with c2:
            safe_metric("Clearance weeks", int(selected.get("clearance_weeks", 0)))
        with c3:
            safe_metric("Urgent breach risk", format_pct(float(selected.get("urgent_breach_risk", 0))))
        with c4:
            safe_metric("Slot utilization", format_pct(float(selected.get("slot_utilization", 0))))
        fig = px.scatter(
            scenarios.data,
            x="impact_score",
            y="effort_score",
            size="final_backlog",
            color="fairness_proxy_delta",
            hover_name="scenario_name",
            title="Scenario frontier: impact, effort, backlog, and fairness proxy",
        )
        st.plotly_chart(fig, use_container_width=True)
        stress = st.slider("Bounded demand stress sensitivity", 0.85, 1.20, 1.0, 0.01)
        adjusted = float(selected.get("final_backlog", 0)) * stress
        st.caption(f"Deterministic sensitivity fallback around precomputed grid: adjusted final backlog {adjusted:.0f}.")
        payload = {
            "scenario_name": scenario_name,
            "app": "ambulatory_v2",
            "site": site,
            "program": program,
            "persona": persona,
            "horizon": horizon,
            "final_backlog": selected.get("final_backlog", 0),
            "demand_stress": stress,
        }
        if st.button("Store scenario run"):
            st.success(try_store_scenario("PEDIATRIC_AHA_DEMO.APP.SCENARIO_RUN_LOG", payload))
        st.dataframe(scenarios.data, use_container_width=True, hide_index=True)

with tabs[6]:
    st.subheader("Data quality")
    if not quality.data.empty:
        if "status" in quality.data.columns:
            fig = px.histogram(quality.data, x="status", color="status", title="Quality check status")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(quality.data, use_container_width=True, hide_index=True)
    if not diagnostic_view.empty or not travel_view.empty or not followup_view.empty:
        st.write("Access readiness, travel, and follow-up quality lenses")
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.dataframe(diagnostic_view, use_container_width=True, hide_index=True)
        with c2:
            st.dataframe(travel_view, use_container_width=True, hide_index=True)
        with c3:
            st.dataframe(followup_view, use_container_width=True, hide_index=True)
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

with tabs[8]:
    st.subheader("v3 ambulatory source readiness")
    readiness_view = v3_readiness.data.copy()
    if not readiness_view.empty and "source_domain" in readiness_view.columns:
        readiness_view = readiness_view[
            readiness_view["source_domain"].astype(str).str.contains("ambulatory|model / governance|open data", case=False, regex=True, na=False)
        ]
    if not readiness_view.empty:
        fig = px.histogram(readiness_view, x="overall_readiness", color="source_domain", title="v3 source-readiness overlay for ambulatory panels")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(readiness_view, use_container_width=True, hide_index=True)
    panel_note(
        "v3 source boundary",
        "The access centre can read v3 referral, waitlist, clinic-template, diagnostic-readiness, and governance views without adding showcase-only dependencies.",
    )

with tabs[9]:
    st.subheader("v3 predictive assets and governed warning logic")
    ambulatory_asset_tokens = ["AMB_", "NO_SHOW", "URGENT", "DIAGNOSTIC"]
    model_view = v3_models.data.copy()
    if not model_view.empty and "asset_id" in model_view.columns:
        model_view = model_view[model_view["asset_id"].astype(str).str.contains("|".join(ambulatory_asset_tokens), regex=True, na=False)]
        st.dataframe(model_view, use_container_width=True, hide_index=True)
    warning_view = v3_warnings.data.copy()
    if not warning_view.empty and "asset_id" in warning_view.columns:
        warning_view = warning_view[warning_view["asset_id"].astype(str).str.contains("|".join(ambulatory_asset_tokens), regex=True, na=False)]
        fig = px.histogram(warning_view, x="severity", color="status", title="Ambulatory-linked v3 warning rules")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(warning_view, use_container_width=True, hide_index=True)
    panel_note(
        "Access safety boundary",
        "No-show and waitlist-breach assets are planning and huddle aids only. They must not automate individual scheduling action without local governance.",
    )

with tabs[10]:
    st.subheader("v3 learning-system notes")
    event_view = v3_events.data.copy()
    if not event_view.empty and "related_panel_id" in event_view.columns:
        event_view = event_view[event_view["related_panel_id"].astype(str).isin(["PANEL_AMBULATORY_COMMAND", "PANEL_SCENARIO_LAB"])]
    st.dataframe(event_view, use_container_width=True, hide_index=True)
    with st.form("ambulatory-v3-learning-note"):
        related_metric_id = st.text_input("Related metric id", value="METRIC_WAITLIST_PRESSURE")
        related_model_id = st.text_input("Related model id", value="URGENT_WAITLIST_BREACH_RISK")
        related_panel_id = st.text_input("Related panel id", value="PANEL_AMBULATORY_COMMAND")
        related_scenario_id = st.text_input("Related scenario id", value="SCN-AMB-001")
        note = st.text_area("Synthetic note", value="Ambulatory huddle reviewed urgent-slot protection and diagnostic readiness.")
        submitted = st.form_submit_button("Store v3 learning note")
    if submitted:
        payload = {
            "event_id": f"AMB-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            "event_type": "huddle_review_event",
            "created_at": datetime.now(UTC).isoformat(),
            "created_by": "synthetic_snowflake_user",
            "app_area": "Ambulatory Access Intelligence",
            "site_id": site if site != "All sites" else "SITE_PROV_NETWORK",
            "unit_or_program": program if program != "All programs" else "Access centre",
            "related_ids": ",".join(value for value in [related_metric_id, related_model_id, related_panel_id, related_scenario_id] if value),
            "related_metric_id": related_metric_id,
            "related_model_id": related_model_id,
            "related_panel_id": related_panel_id,
            "related_scenario_id": related_scenario_id,
            "status": "submitted",
            "severity": "medium",
            "note": note,
            "payload_json": json.dumps({"synthetic_demo": True, "app": "ambulatory_access_centre"}),
            "synthetic_demo_flag": True,
        }
        st.success(try_store_learning_event("APP.HUDDLE_REVIEW_EVENT", payload))
