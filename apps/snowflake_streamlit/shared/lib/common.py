"""Shared helpers for Streamlit in Snowflake and local sample mode."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

APP_VERSION = "v3.0"
SYNTHETIC_NOTICE = "Synthetic demonstration data. Not validated for clinical decision-making."
SNOWFLAKE_SAFE_PACKAGES = ("river", "dowhy", "mesa", "cleanlab")
LEARNING_WRITEBACK_TABLES = {
    "APP.USER_ANNOTATION",
    "APP.WARNING_ACKNOWLEDGEMENT",
    "APP.METRIC_ISSUE_FLAG",
    "APP.MODEL_REVIEW_NOTE",
    "APP.GOVERNANCE_DECISION",
    "APP.VALIDATION_REVIEW",
    "APP.PANEL_FEEDBACK",
    "APP.HUDDLE_REVIEW_EVENT",
    "APP.LEARNING_SYSTEM_OUTCOME_REVIEW",
    "APP.SCENARIO_RUN_LOG",
}


@dataclass
class DataResult:
    data: pd.DataFrame
    source: str
    message: str


def optional_package_status() -> dict[str, bool]:
    status = {}
    for name in SNOWFLAKE_SAFE_PACKAGES:
        try:
            __import__(name)
            status[name] = True
        except Exception:
            status[name] = False
    return status


def get_snowpark_session() -> Any | None:
    try:
        from snowflake.snowpark.context import get_active_session

        return get_active_session()
    except Exception:
        return None


def sample_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "sample_data"


def load_table_or_sample(sql: str, sample_name: str) -> DataResult:
    session = get_snowpark_session()
    if session is not None:
        try:
            return DataResult(session.sql(sql).to_pandas(), "Snowflake curated mart", "Snowflake query succeeded")
        except Exception as exc:  # pragma: no cover - depends on Snowflake runtime
            st.warning(f"Snowflake mart query failed. Using local sample fallback. Details: {exc}")
    path = sample_dir() / sample_name
    if path.exists():
        return DataResult(pd.read_csv(path), "Local sample CSV", f"Loaded {path.name}")
    return DataResult(pd.DataFrame(), "No data", f"Missing sample file: {path}")


def status_panel(
    data_source: str,
    *,
    last_refresh: str | None = None,
    mart_available: bool | None = None,
    scenario_write_available: bool | None = None,
) -> None:
    optional = optional_package_status()
    with st.sidebar:
        st.caption(SYNTHETIC_NOTICE)
        st.subheader("App status")
        st.write(
            {
                "data_source": data_source,
                "last_refresh": last_refresh or "sample/local fallback",
                "package_mode": "Snowflake Anaconda baseline; no advanced DES runtime packages required",
                "app_version": APP_VERSION,
                "synthetic_real_data_mode": "synthetic demo",
                "snowflake_mart_available": mart_available if mart_available is not None else data_source.startswith("Snowflake"),
                "scenario_write_available": scenario_write_available if scenario_write_available is not None else get_snowpark_session() is not None,
            }
        )
        st.subheader("Optional packages")
        st.write(optional)
        st.caption("Streamlit/Snowflake path uses SQL marts, pandas/numpy/scipy/sklearn/statsmodels, Plotly/Altair, and deterministic fallbacks.")


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def safe_metric(label: str, value: Any, delta: Any | None = None) -> None:
    try:
        st.metric(label, value, delta=delta)
    except Exception:
        st.write({label: value, "delta": delta})


def panel_note(title: str, body: str) -> None:
    st.info(f"**{title}**\n\n{body}")


def first_present_column(data: pd.DataFrame, candidates: list[str]) -> str | None:
    for column in candidates:
        if column in data.columns:
            return column
    return None


def try_store_scenario(table_name: str, payload: dict[str, Any]) -> str:
    normalized = normalize_scenario_payload(payload)
    if table_name not in {"APP.SCENARIO_RUN_LOG", "PEDIATRIC_AHA_DEMO.APP.SCENARIO_RUN_LOG"}:
        st.session_state.setdefault("scenario_runs", []).append(normalized)
        return f"Unsupported scenario table {table_name}; stored in session state instead."
    session = get_snowpark_session()
    if session is None:
        st.session_state.setdefault("scenario_runs", []).append(normalized)
        return "Stored in Streamlit session state for local/sample mode."
    try:
        session.create_dataframe([normalized]).write.mode("append").save_as_table(table_name)
        return f"Stored in {table_name}."
    except Exception as exc:  # pragma: no cover - depends on Snowflake privileges
        st.session_state.setdefault("scenario_runs", []).append(normalized)
        return f"Snowflake write unavailable; stored in session state. Details: {exc}"


def normalize_scenario_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if "event_id" in payload and "event_type" in payload:
        return payload
    scenario_id = str(payload.get("scenario_id") or payload.get("scenario_name") or "scenario_run")
    return {
        "event_id": f"SCN-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}",
        "event_type": "scenario_run",
        "created_at": datetime.now(UTC).isoformat(),
        "created_by": "synthetic_snowflake_user",
        "app_area": str(payload.get("app") or "Scenario Simulation Lab"),
        "site_id": str(payload.get("site") or "SITE_PROV_NETWORK"),
        "unit_or_program": str(payload.get("program") or payload.get("unit_or_program") or "Network"),
        "related_ids": scenario_id,
        "related_metric_id": "",
        "related_model_id": "",
        "related_panel_id": "PANEL_SCENARIO_LAB",
        "related_scenario_id": scenario_id,
        "status": "submitted",
        "severity": "low",
        "note": f"Synthetic scenario run captured for {scenario_id}.",
        "payload_json": json.dumps({"synthetic_demo": True, "scenario_payload": payload}, default=str),
        "synthetic_demo_flag": True,
    }


def try_store_learning_event(table_name: str, payload: dict[str, Any]) -> str:
    if table_name not in LEARNING_WRITEBACK_TABLES:
        st.session_state.setdefault("learning_events", []).append(payload)
        return f"Unsupported writeback table {table_name}; stored in session state instead."
    session = get_snowpark_session()
    if session is None:
        st.session_state.setdefault("learning_events", []).append(payload)
        return "Stored in Streamlit session state for local/sample mode."
    try:
        session.create_dataframe([payload]).write.mode("append").save_as_table(table_name)
        return f"Stored in {table_name}."
    except Exception as exc:  # pragma: no cover - depends on Snowflake privileges
        st.session_state.setdefault("learning_events", []).append(payload)
        return f"Snowflake write unavailable; stored in session state. Details: {exc}"
