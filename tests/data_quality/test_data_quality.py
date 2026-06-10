import pandas as pd

from packages.core.data_quality import (
    primary_key_unique,
    scan_direct_identifiers,
    small_cell_suppress,
    valid_timestamp_order,
)


def test_primary_key_unique_detects_duplicates():
    df = pd.DataFrame({"id": ["a", "b", "b"]})
    result = primary_key_unique(df, "id")
    assert not result["passed"]
    assert result["failed_rows"] == 1


def test_timestamp_order():
    df = pd.DataFrame({"start": ["2026-01-01"], "end": ["2026-01-02"]})
    assert valid_timestamp_order(df, "start", "end")["passed"]


def test_direct_identifier_scan_and_suppression():
    df = pd.DataFrame({"synthetic_id": ["SYNTH_001"]})
    assert scan_direct_identifiers(df)["passed"]
    assert small_cell_suppress(3) == "<6"
    assert small_cell_suppress(8) == 8

