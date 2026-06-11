from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
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
        load_table_or_sample,
        panel_note,
        safe_metric,
        status_panel,
        try_store_learning_event,
    )
except Exception:  # pragma: no cover - local repo fallback
    from apps.snowflake_streamlit.shared.lib.common import (  # noqa: E402
        SYNTHETIC_NOTICE,
        load_table_or_sample,
        panel_note,
        safe_metric,
        status_panel,
        try_store_learning_event,
    )

st.set_page_config(page_title="AHA Gatekeeper Control Plane v3", layout="wide")

SOURCE_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.GOVERNANCE.V3_SOURCE_REGISTRY ORDER BY source_id"
READINESS_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.GOVERNANCE.V3_DIRECT_LINK_VALIDATION ORDER BY source_id"
METRIC_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.CONFIG.V3_METRIC_REGISTRY ORDER BY metric_id"
MODEL_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MODEL.V3_MODEL_REGISTRY ORDER BY asset_id"
LINEAGE_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.GOVERNANCE.V3_PANEL_LINEAGE ORDER BY panel_id"
ISSUE_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.GOVERNANCE.V3_GATEKEEPER_ISSUE ORDER BY severity DESC, issue_id"
EVENT_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.APP.V3_LEARNING_SYSTEM_EVENT ORDER BY created_at DESC"
SCENARIO_SQL = "SELECT * FROM PEDIATRIC_AHA_DEMO.MART.V3_SCENARIO ORDER BY scenario_id"

sources = load_table_or_sample(SOURCE_SQL, "v3_source_registry.csv")
readiness = load_table_or_sample(READINESS_SQL, "v3_direct_link_validation.csv")
metrics = load_table_or_sample(METRIC_SQL, "v3_metric_registry.csv")
models = load_table_or_sample(MODEL_SQL, "v3_model_registry.csv")
lineage = load_table_or_sample(LINEAGE_SQL, "v3_panel_lineage.csv")
issues = load_table_or_sample(ISSUE_SQL, "v3_gatekeeper_issues.csv")
events = load_table_or_sample(EVENT_SQL, "v3_learning_system_events.csv")
scenarios = load_table_or_sample(SCENARIO_SQL, "v3_scenarios.csv")

status_panel(
    sources.source,
    last_refresh=str(datetime.now(UTC).isoformat()),
    mart_available=sources.source.startswith("Snowflake"),
    scenario_write_available=sources.source.startswith("Snowflake"),
)

st.title("AHA Gatekeeper Control Plane v3")
st.caption(SYNTHETIC_NOTICE)

if sources.data.empty:
    st.error("No v3 Gatekeeper data found. Generate v3 assets or run the Snowflake setup scripts.")
    st.stop()


def count_status(data: pd.DataFrame, column: str, value: str) -> int:
    if data.empty or column not in data.columns:
        return 0
    return int((data[column].astype(str).str.lower() == value.lower()).sum())


mode = st.sidebar.radio("Mode", ["Executive lite", "Technical deep"], horizontal=False)
st.sidebar.caption("This app governs source links, derived metrics, modelled assets, warning logic, scenario outputs, and learning-system events.")

ready_sources = count_status(readiness.data, "overall_readiness", "ready")
review_sources = len(readiness.data) - ready_sources
approved_models = int(models.data.get("governance_status", pd.Series(dtype=str)).astype(str).str.contains("approved", case=False).sum()) if not models.data.empty else 0
review_models = len(models.data) - approved_models

tabs = st.tabs(
    [
        "Stoplight",
        "Direct Links",
        "Metric Registry",
        "Model Cards",
        "Dependency / Lineage",
        "Issues and Approvals",
        "Learning Memory",
    ]
)

with tabs[0]:
    st.subheader("Executive control surface" if mode == "Executive lite" else "Control-plane health")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        safe_metric("Ready sources", ready_sources, f"{review_sources} review")
    with c2:
        safe_metric("Model assets", len(models.data), f"{review_models} review")
    with c3:
        safe_metric("Metric cards", len(metrics.data), "definition-owned")
    with c4:
        safe_metric("Learning events", len(events.data), "writeback-ready")
    panel_note(
        "Gatekeeper rule",
        "Public panels should show direct/derived/modelled classification, source-readiness, freshness, confidence, caveats, and lineage before users trust the output.",
    )
    if not readiness.data.empty:
        fig = px.histogram(readiness.data, x="overall_readiness", color="overall_readiness", title="Direct-link readiness")
        st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.subheader("Direct operational source validation")
    display_cols = [
        "source_id",
        "source_view_present",
        "field_populated",
        "freshness",
        "row_count",
        "timestamp_logic",
        "referential_integrity",
        "metric_definition_approved",
        "small_cell_suppression",
        "overall_readiness",
    ]
    st.dataframe(readiness.data[[column for column in display_cols if column in readiness.data.columns]], use_container_width=True, hide_index=True)
    st.subheader("Synthetic curated source registry")
    st.dataframe(sources.data, use_container_width=True, hide_index=True)

with tabs[2]:
    st.subheader("Derived metric cards")
    st.dataframe(metrics.data, use_container_width=True, hide_index=True)
    if not metrics.data.empty and "classification" in metrics.data.columns:
        fig = px.histogram(metrics.data, x="classification", color="validation", title="Metric classification and validation status")
        st.plotly_chart(fig, use_container_width=True)

with tabs[3]:
    st.subheader("Model governance cards")
    selected_asset = st.selectbox("Asset", models.data["asset_id"].tolist() if "asset_id" in models.data.columns else [])
    if selected_asset:
        card = models.data[models.data["asset_id"].astype(str) == selected_asset].head(1).T
        st.dataframe(card, use_container_width=True)
    st.dataframe(models.data, use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("Panel lineage")
    st.dataframe(lineage.data, use_container_width=True, hide_index=True)
    if not lineage.data.empty and {"app_area", "classification"}.issubset(lineage.data.columns):
        fig = px.histogram(lineage.data, x="app_area", color="classification", title="Panel classification by app area")
        st.plotly_chart(fig, use_container_width=True)

with tabs[5]:
    st.subheader("Issue and approval workflow")
    st.dataframe(issues.data, use_container_width=True, hide_index=True)
    if not issues.data.empty and "severity" in issues.data.columns:
        fig = px.histogram(issues.data, x="severity", color="status", title="Open governance issues")
        st.plotly_chart(fig, use_container_width=True)

with tabs[6]:
    st.subheader("Learning-system writeback rehearsal")
    st.dataframe(events.data, use_container_width=True, hide_index=True)
    with st.form("learning-event-form"):
        event_type = st.selectbox(
            "Event type",
            [
                "user_annotation",
                "warning_acknowledgement",
                "metric_issue_flag",
                "model_review_note",
                "governance_decision",
                "validation_review",
                "panel_feedback",
                "huddle_review_event",
                "learning_system_outcome_review",
            ],
        )
        related_id = st.text_input("Related source, metric, model, warning, panel, or scenario id", value="INPT_OCCUPANCY_FORECAST")
        note = st.text_area("Synthetic note", value="Reviewed in Gatekeeper v3 demonstration.")
        table_name = st.selectbox(
            "Writeback table",
            [
                "APP.USER_ANNOTATION",
                "APP.WARNING_ACKNOWLEDGEMENT",
                "APP.METRIC_ISSUE_FLAG",
                "APP.MODEL_REVIEW_NOTE",
                "APP.GOVERNANCE_DECISION",
                "APP.VALIDATION_REVIEW",
                "APP.PANEL_FEEDBACK",
                "APP.HUDDLE_REVIEW_EVENT",
                "APP.LEARNING_SYSTEM_OUTCOME_REVIEW",
            ],
        )
        submitted = st.form_submit_button("Store synthetic event")
    if submitted:
        payload = {
            "event_id": f"STREAMLIT-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            "event_type": event_type,
            "created_at": datetime.now(UTC).isoformat(),
            "created_by": "synthetic_snowflake_user",
            "app_area": "AHA Gatekeeper Control Plane",
            "site_id": "SITE_PROV_NETWORK",
            "unit_or_program": "Network",
            "related_ids": related_id,
            "status": "submitted",
            "severity": "low",
            "note": note,
            "payload_json": json.dumps({"synthetic_demo": True, "app": "gatekeeper_control_plane"}),
            "synthetic_demo_flag": True,
        }
        st.success(try_store_learning_event(table_name, payload))

with st.expander("Scenario register feeding Gatekeeper", expanded=False):
    st.dataframe(scenarios.data, use_container_width=True, hide_index=True)
