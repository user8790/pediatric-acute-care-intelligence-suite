# Deploying the Streamlit Versions on Streamlit Community Cloud

Last checked: 2026-06-10.

Streamlit Community Cloud deploys from GitHub and searches for dependencies in the app entrypoint directory first. It prioritizes `environment.yml` ahead of `requirements.txt`, so this repo provides separate Community Cloud wrappers under `apps/streamlit_cloud`.

Deploy two apps from the same GitHub repository:

| App | Main file path |
|---|---|
| Inpatient Command Centre | `apps/streamlit_cloud/inpatient/streamlit_app.py` |
| Ambulatory Access Intelligence Centre | `apps/streamlit_cloud/ambulatory/streamlit_app.py` |

The apps use committed synthetic sample data and do not require Snowflake credentials. The Snowflake-transferable apps remain under `apps/snowflake_streamlit` with Snowflake-channel `environment.yml` files for Snowsight.

Current published demo URLs:

- Inpatient: https://pediatric-acute-care-inpatient.streamlit.app/
- Ambulatory: https://pediatric-acute-care-ambulatory.streamlit.app/

## Notes

- Do not commit Streamlit secrets.
- If connecting to Snowflake in a future Streamlit Cloud deployment, add secrets through the Streamlit Cloud app settings.
- These Community Cloud deployments are demonstration/sample-mode deployments, not the Snowsight warehouse-runtime deployment.
