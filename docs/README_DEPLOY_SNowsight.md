# Deploying in Snowsight Without Local Installs

This guide assumes the target user has Snowflake/Snowsight access but cannot install Snowflake CLI, Git, Python, Node, or other local development tools on the target computer.
No local installs are required for the Snowsight deployment path.

The apps use synthetic demonstration data and are not validated for clinical decision-making.

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
10. `snowflake/sql/09_create_streamlit_objects_optional.sql` if creating Streamlit objects through SQL/staged files
11. `snowflake/sql/10_smoke_tests.sql`
12. `snowflake/sql/11_v2_scenario_marts.sql`
13. `snowflake/sql/12_v2_forecast_marts.sql`

If a later script fails because an earlier object is missing, rerun the missing earlier script and then rerun the failed script.

## 2. Create Streamlit Apps in Snowsight

Create two Streamlit apps under `PEDIATRIC_AHA_DEMO.APP`:

- Inpatient Command Centre v2.
- Ambulatory Access Intelligence Centre v2.

For each app, paste or upload:

- the relevant `streamlit_app.py`;
- `environment.yml`;
- the shared helper files from `apps/snowflake_streamlit/shared/lib/`;
- optional `pages/` files if you want the companion methods pages.

The environment files use the Snowflake channel and Python 3.11.

## 3. Confirm Data Access

The app role needs:

- `USAGE` on database and schemas;
- `SELECT` on `PEDIATRIC_AHA_DEMO.MART`;
- `SELECT` on `PEDIATRIC_AHA_DEMO.MODEL`;
- `SELECT` on `PEDIATRIC_AHA_DEMO.CONFIG`;
- optional `INSERT` on `PEDIATRIC_AHA_DEMO.APP.SCENARIO_RUN_LOG`.

## 4. Validate in the App

Open each app and confirm the sidebar status panel shows:

- data source: Snowflake curated mart;
- app version: v2.0;
- synthetic/real-data mode: synthetic demo;
- Snowflake mart availability: true;
- scenario-write availability: true if the role has insert privileges.

## 5. Troubleshooting

- **Missing tables:** run scripts `05`, `11`, and `12` again.
- **Missing v2 model registry or coefficients:** run scripts `11` and `12`.
- **Package unavailable:** confirm the app is using the supplied `environment.yml` with the Snowflake channel.
- **No warehouse selected:** choose an active warehouse in Snowsight.
- **Permission error:** confirm role grants on database, schemas, marts, model, config, and app log table.
- **Scenario write fails:** grant insert on `APP.SCENARIO_RUN_LOG`; the app will otherwise fall back to session-state storage.
- **Public/local app shows CSV source:** that is expected outside Snowflake or when Snowflake queries fail.
