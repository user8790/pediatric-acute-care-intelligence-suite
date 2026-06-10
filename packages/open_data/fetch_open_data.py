"""Fetch or refresh open-data snapshots with offline fallbacks.

The Streamlit in Snowflake apps do not call this module. They use cached snapshots only.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_fallback_snapshots(output_dir: str = "packages/open_data/cache/normalized") -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "source_id": "OPEN_RESP_CA",
                "week_start_date": "2026-01-05",
                "region": "Alberta",
                "influenza_activity_index": 11.2,
                "rsv_activity_index": 10.7,
                "fallback": True,
            },
            {
                "source_id": "OPEN_WEATHER_ECCC",
                "week_start_date": "2026-01-05",
                "region": "Edmonton-Calgary pediatric corridor proxy",
                "mean_temperature_c": -8.4,
                "aqhi_max": 3,
                "fallback": True,
            },
        ]
    ).to_csv(out / "open_context_fallback.csv", index=False)


if __name__ == "__main__":
    write_fallback_snapshots()

