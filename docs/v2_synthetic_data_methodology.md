# v2 Synthetic Data Methodology

## Generator

`packages/synthetic/generate_v2_showcase_data.py` produces deterministic v2 assets with seed `20260610`.

Outputs include:

- 12-month synthetic context;
- hourly inpatient census slices;
- unit pressure, bed state, discharge barriers, ED handoff, OR/PACU, high-resource flow, staffing, and safety proxies;
- ambulatory access history, referrals, slots, follow-up, diagnostics, travel, and forecasts;
- model cards, coefficients, quality checks, open-data context, and scenario grids;
- app-ready JSON for the showcase;
- small CSV fallback marts for Streamlit.

## Realism Features

The generator includes pediatric service lines, unit types, seasonality, winter respiratory pressure, school calendar effects, day/hour patterns, OR schedule effects, staffing variation, isolation constraints, PICU/NICU bottlenecks, ambulatory template constraints, no-show variation, diagnostic dependency delay, and neutral geography/travel-burden proxies.

## Privacy Boundary

The generator does not create names, MRNs, health numbers, direct addresses, phone numbers, or direct identifiers. Synthetic surrogate IDs and aggregate rows are used. Patient-level rows are not exposed by default.
