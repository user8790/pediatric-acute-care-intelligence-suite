# v3 Snowflake Deployment, Snowsight No CLI

This deployment path uses synthetic demonstration data and is not validated for clinical decision-making.

## Ordered SQL

Run snowflake/sql/00_context_and_roles_template.sql through snowflake/sql/15_smoke_tests.sql in order. The v3-specific scripts are:

- 02_create_synthetic_source_tables.sql
- 03_generate_synthetic_connectcare_realistic_data.sql
- 04_create_canonical_views.sql
- 05_create_operational_marts.sql
- 06_create_model_and_prediction_tables.sql
- 07_create_metric_and_coefficient_registry.sql
- 08_create_direct_link_validation.sql
- 09_create_gatekeeper_control_plane_tables.sql
- 10_create_learning_system_writeback_tables.sql
- 11_create_scenario_tables_and_marts.sql
- 12_create_data_quality_checks.sql
- 13_create_app_metadata.sql
- 14_create_streamlit_objects_optional.sql
- 15_smoke_tests.sql

## Streamlit

Use apps/snowflake_streamlit/gatekeeper_control_plane, inpatient, and ambulatory. Baseline dependencies come from the Snowflake Anaconda channel. Advanced simulation or causal packages should remain optional adapters unless explicitly approved for the Snowflake runtime.
