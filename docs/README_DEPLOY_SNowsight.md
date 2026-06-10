# Deploying in Snowsight Without Local Installs

This guide assumes the target user has Snowflake/Snowsight access but cannot install Snowflake CLI or local development tools on the target computer.

## 1. Run SQL Worksheets in Order

Open Snowsight Worksheets and run:

1. `snowflake/sql/00_context_and_roles_template.sql`
2. `snowflake/sql/01_create_database_schema.sql`
3. `snowflake/sql/02_create_tables.sql`
4. `snowflake/sql/03_generate_synthetic_data.sql`
5. `snowflake/sql/04_create_curated_views.sql`
6. `snowflake/sql/05_create_marts.sql`
7. `snowflake/sql/06_create_model_output_tables.sql`
8. `snowflake/sql/07_create_coefficients_and_config.sql`
9. `snowflake/sql/08_create_quality_checks.sql`
10. `snowflake/sql/10_smoke_tests.sql`

Script 09 is optional if creating Streamlit objects with staged files.

## 2. Create Streamlit Apps in Snowsight

Create two Streamlit apps under `PEDIATRIC_AHA_DEMO.APP`:

- Inpatient Command Centre.
- Ambulatory Access Intelligence Centre.

For each app, paste or upload:

- `streamlit_app.py`
- `environment.yml`
- `pages/`
- the shared helper files from `apps/snowflake_streamlit/shared/lib/`

The environment files use the Snowflake channel and Python 3.11.

## 3. Confirm Data Access

The app role needs `USAGE` on database/schemas and `SELECT` on `PEDIATRIC_AHA_DEMO.MART` and `PEDIATRIC_AHA_DEMO.MODEL`.

Optional writeback requires insert on `PEDIATRIC_AHA_DEMO.APP.SCENARIO_RUN_LOG`.

## 4. Validate

Open each app and confirm the status panel shows:

- Data source: Snowflake curated mart.
- Synthetic/real-data mode: synthetic demo.
- Optional package availability.
- App version.

If tables are missing, the app shows a safe setup message.

