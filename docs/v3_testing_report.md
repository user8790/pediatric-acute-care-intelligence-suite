# v3 Testing Report

This report covers synthetic demonstration data and is not validated for clinical decision-making.

## Planned Checks

- Generate v3 frontier assets.
- Python unit and integration tests.
- Showcase TypeScript and Vite production build.
- Showcase Playwright public-surface tests.
- Streamlit compile smoke for inpatient, ambulatory, shared helpers, and Gatekeeper.
- Snowflake SQL static checks.
- Documentation presence and safety language checks.

## Latest Local Results

- `python -m pytest`: 38 passed.
- `python -m pytest tests/integration/test_v3_assets.py tests/integration/test_streamlit_dependency_boundary.py tests/integration/test_snowflake_sql_static.py tests/integration/test_app_smoke.py`: 17 passed.
- `pnpm run build:showcase`: passed.
- `pnpm --dir apps/showcase test:e2e`: 8 passed across desktop and mobile Chromium.
- Playwright browser visual check: local preview rendered the v3 System Posture page at 1440 x 1100, Walkthrough remained hidden from public nav, readiness overlay showed the full catalog count, and no obvious overlaps or blank sections remained on the checked page.

## Added Coverage in This Pass

- Full v3 source catalog assertion for the 73 synthetic curated/source/governance view contracts.
- Expanded Gatekeeper payload assertions for warning logic, coefficients, data-quality rules, validation/drift, and release/rollback.
- Learning-system event-shape assertions for `related_metric_id`, `related_model_id`, `related_panel_id`, and `related_scenario_id`.
- Streamlit sample-data boundary assertions for the new v3 governance CSVs.
- Static SQL assertions for new registry tables and writeback relationship columns.
