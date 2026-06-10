# Snowflake Transferability

The Streamlit/Snowflake track is designed for a constrained Snowflake warehouse runtime and a user who can use Snowsight but cannot install local CLI tools.

## Principles

- SQL-first setup.
- `environment.yml` with `channels: [snowflake]`.
- Python 3.11.
- Native Streamlit only.
- No custom components.
- No external network calls from the app.
- Query curated marts, not raw tables.
- Aggregate before display.
- Use precomputed scenario grids and coefficient tables for scenario depth.

## Baseline Packages

The app environments use:

- streamlit
- snowflake-snowpark-python
- pandas
- numpy
- scipy
- scikit-learn
- statsmodels
- altair
- plotly
- pyyaml

Pending optional packages are documented in `apps/snowflake_streamlit/shared/environment_optional_pending.yml` and are not required by the apps.

## v2 Marts

Streamlit v2 reads:

- `MART.MART_V2_INPATIENT_MISSION_CONTROL`
- `MART.MART_V2_INPATIENT_FLOW`
- `MART.MART_V2_INPATIENT_FORECAST`
- `MART.MART_V2_INPATIENT_SCENARIO`
- `MART.MART_V2_AMBULATORY_MISSION_CONTROL`
- `MART.MART_V2_AMBULATORY_ACCESS`
- `MART.MART_V2_AMBULATORY_FORECAST`
- `MART.MART_V2_AMBULATORY_SCENARIO`
- `MART.MART_V2_DATA_QUALITY_STATUS`
- `MODEL.DIM_V2_MODEL_REGISTRY`
- `MODEL.DIM_V2_COEFFICIENT_REGISTRY`

Public/local demo mode uses generated sample CSVs with the same v2 shape.
