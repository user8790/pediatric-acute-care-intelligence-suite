"""Shared helpers for Streamlit in Snowflake and local sample mode."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

APP_VERSION = "0.1.0"
SYNTHETIC_NOTICE = "Synthetic demonstration data. Not validated for clinical decision-making."


@dataclass
class DataResult:
    data: pd.DataFrame
    source: str
    message: str


def optional_package_status() -> dict[str, bool]:
    status = {}
    for name in ("simpy", "ciw", "river", "dowhy", "mesa", "cleanlab"):
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


def status_panel(data_source: str) -> None:
    optional = optional_package_status()
    with st.sidebar:
        st.caption(SYNTHETIC_NOTICE)
        st.subheader("App status")
        st.write(
            {
                "data_source": data_source,
                "package_mode": "Snowflake Anaconda baseline + optional adapters",
                "app_version": APP_VERSION,
                "synthetic_real_data_mode": "synthetic demo",
            }
        )
        st.subheader("Optional packages")
        st.write(optional)


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def safe_metric(label: str, value: Any, delta: Any | None = None) -> None:
    try:
        st.metric(label, value, delta=delta)
    except Exception:
        st.write({label: value, "delta": delta})


def try_store_scenario(table_name: str, payload: dict[str, Any]) -> str:
    session = get_snowpark_session()
    if session is None:
        st.session_state.setdefault("scenario_runs", []).append(payload)
        return "Stored in Streamlit session state for local/sample mode."
    columns = ", ".join(payload.keys())
    values = ", ".join([repr(str(v)) for v in payload.values()])
    try:
        session.sql(f"INSERT INTO {table_name} ({columns}) SELECT {values}").collect()
        return f"Stored in {table_name}."
    except Exception as exc:  # pragma: no cover - depends on Snowflake privileges
        st.session_state.setdefault("scenario_runs", []).append(payload)
        return f"Snowflake write unavailable; stored in session state. Details: {exc}"
