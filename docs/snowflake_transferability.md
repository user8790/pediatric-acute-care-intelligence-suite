# Snowflake Transferability

Version B is designed for a constrained Snowflake warehouse runtime and a user who can use Snowsight but cannot install local CLI tools.

## Principles

- SQL-first setup.
- `environment.yml` with `channels: [snowflake]`.
- Python 3.11.
- Native Streamlit only.
- No external network calls from the app.
- No custom components, external JavaScript, iframes, or map tiles.
- Query curated marts, not raw tables.
- Aggregate before display.

## Baseline Packages

The app environment uses packages found in the Snowflake Anaconda channel during the 2026-06-10 check:

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

Pending packages are documented in `apps/snowflake_streamlit/shared/environment_optional_pending.yml`.

