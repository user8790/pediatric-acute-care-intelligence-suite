"""Reusable data-quality checks with privacy-oriented helpers."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping

import pandas as pd


DIRECT_IDENTIFIER_PATTERNS = [
    re.compile(r"\b\d{4}[- ]?\d{3}[- ]?\d{3}\b"),  # health-number-like
    re.compile(r"\b\d{3}[- ]?\d{3}[- ]?\d{4}\b"),  # phone-like
    re.compile(r"\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b"),  # name-like "Last, First"
]


def primary_key_unique(df: pd.DataFrame, key: str) -> dict[str, object]:
    duplicate_count = int(df.duplicated(subset=[key]).sum()) if key in df else len(df)
    return {
        "check": f"{key}_unique",
        "passed": duplicate_count == 0,
        "failed_rows": duplicate_count,
    }


def valid_timestamp_order(df: pd.DataFrame, start_col: str, end_col: str) -> dict[str, object]:
    if start_col not in df or end_col not in df:
        return {"check": f"{start_col}_before_{end_col}", "passed": False, "failed_rows": len(df)}
    starts = pd.to_datetime(df[start_col], errors="coerce")
    ends = pd.to_datetime(df[end_col], errors="coerce")
    failed = int(((starts.notna()) & (ends.notna()) & (ends < starts)).sum())
    return {"check": f"{start_col}_before_{end_col}", "passed": failed == 0, "failed_rows": failed}


def non_negative(df: pd.DataFrame, columns: Iterable[str]) -> list[dict[str, object]]:
    results = []
    for column in columns:
        if column not in df:
            results.append({"check": f"{column}_non_negative", "passed": False, "failed_rows": len(df)})
            continue
        failed = int((pd.to_numeric(df[column], errors="coerce") < 0).sum())
        results.append({"check": f"{column}_non_negative", "passed": failed == 0, "failed_rows": failed})
    return results


def scan_direct_identifiers(df: pd.DataFrame) -> dict[str, object]:
    text = " ".join(df.astype(str).fillna("").head(10000).to_numpy().ravel())
    matches = sum(1 for pattern in DIRECT_IDENTIFIER_PATTERNS if pattern.search(text))
    return {"check": "no_direct_identifiers", "passed": matches == 0, "failed_rows": matches}


def small_cell_suppress(value: int | float, threshold: int = 6) -> str | int | float:
    if 0 < value < threshold:
        return f"<{threshold}"
    return value


def summarize_checks(checks: Iterable[Mapping[str, object]]) -> pd.DataFrame:
    rows = list(checks)
    if not rows:
        return pd.DataFrame(columns=["check", "passed", "failed_rows"])
    return pd.DataFrame(rows)

