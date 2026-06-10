# Streamlit Community Cloud Entrypoints

These wrappers are for Streamlit Community Cloud deployment from GitHub.

They intentionally live outside `apps/snowflake_streamlit/*` because Streamlit Community Cloud searches the app entrypoint directory for dependency files and prioritizes `environment.yml` ahead of `requirements.txt`. The Snowflake Streamlit apps must keep their Snowflake-channel `environment.yml` files, so these wrappers provide clean Community Cloud entrypoints with simple pip requirements.

Deploy as two separate Streamlit apps:

- Inpatient entrypoint: `apps/streamlit_cloud/inpatient/streamlit_app.py`
- Ambulatory entrypoint: `apps/streamlit_cloud/ambulatory/streamlit_app.py`

Both wrappers run the production-shaped Snowflake-transferable apps in local/sample mode using committed synthetic CSVs.

