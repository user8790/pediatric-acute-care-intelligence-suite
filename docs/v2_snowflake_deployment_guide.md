# v2 Snowflake Deployment Guide

This guide assumes Snowsight access and no local Snowflake CLI on the target computer.

## SQL Order

Run worksheets in order:

1. `snowflake/sql/00_context_and_roles_template.sql`
2. `snowflake/sql/01_create_database_schema.sql`
3. `snowflake/sql/02_create_tables.sql`
4. `snowflake/sql/03_generate_synthetic_data.sql`
5. `snowflake/sql/04_create_curated_views.sql`
6. `snowflake/sql/05_create_marts.sql`
7. `snowflake/sql/06_create_model_output_tables.sql`
8. `snowflake/sql/07_create_coefficients_and_config.sql`
9. `snowflake/sql/08_create_quality_checks.sql`
10. `snowflake/sql/09_create_streamlit_objects_optional.sql` if using Snowflake-managed Streamlit object setup.
11. `snowflake/sql/10_smoke_tests.sql`
12. `snowflake/sql/11_v2_scenario_marts.sql`
13. `snowflake/sql/12_v2_forecast_marts.sql`

## App Files

Create two Streamlit apps in Snowsight under `PEDIATRIC_AHA_DEMO.APP`:

- Inpatient Command Centre v2.
- Ambulatory Access Intelligence Centre v2.

Upload or paste:

- the relevant `streamlit_app.py`;
- the matching `environment.yml`;
- shared files from `apps/snowflake_streamlit/shared/lib/`.

## Package Boundary

The Streamlit/Snowflake apps use Streamlit, Snowpark, pandas, numpy, scipy, scikit-learn, statsmodels, Altair, Plotly, PyYAML, and standard library tools. Scenario depth comes from SQL marts, coefficient tables, precomputed grids, and deterministic fallbacks.

## Troubleshooting

- Missing marts: rerun scripts `05`, `11`, and `12`.
- Missing model cards or coefficients: rerun scripts `11` and `12`.
- Permission error: grant `USAGE` on database/schemas and `SELECT` on `MART`, `MODEL`, and `CONFIG`.
- Scenario writeback unavailable: grant `INSERT` on `APP.SCENARIO_RUN_LOG`; the app will otherwise keep local session-state runs.
- Package error: confirm the app uses the supplied `environment.yml` with the Snowflake channel.
- Warehouse error: select an active warehouse before opening the app.
