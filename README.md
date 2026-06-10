# Pediatric Acute Care Intelligence Suite

Production-shaped prototype suite for pediatric inpatient and ambulatory operations intelligence, inspired by Stollery Children's Hospital / Alberta Children's Hospital operational patterns.

This is a synthetic demonstration. It is not connected to Alberta Health Services, Epic, Connect Care, Stollery, Alberta Children's Hospital, or Snowflake production data. It is not validated for clinical decision-making.

## What Is Included

- Version A: a TypeScript + React showcase app under `apps/showcase`.
- Version B: two Streamlit in Snowflake transferable apps under `apps/snowflake_streamlit`.
- Deterministic synthetic pediatric operations data generator under `packages/synthetic`.
- Transparent queueing, simulation, forecasting, modelling, data-quality, and explainability helpers under `packages/core`.
- SQL-first Snowflake setup scripts under `snowflake/sql`.
- Documentation for architecture, deployment, methods, safety, contracts, and future real-data mapping under `docs`.

## Quick Start

```powershell
python packages/synthetic/generate_synthetic_data.py
python -m pytest
pnpm install
pnpm run dev:showcase
```

The showcase app runs locally with cached generated data and built-in fallbacks.

## Streamlit Local Smoke

```powershell
streamlit run apps/snowflake_streamlit/inpatient/streamlit_app.py
streamlit run apps/snowflake_streamlit/ambulatory/streamlit_app.py
```

Local mode uses sample CSVs. In Snowflake, the apps query curated marts and write scenario runs when privileges allow.

## Snowflake Deployment Path

For no-CLI Snowsight deployment, start with:

- `docs/README_DEPLOY_SNowsight.md`
- `snowflake/sql/00_context_and_roles_template.sql`
- `snowflake/sql/01_create_database_schema.sql`

Run SQL scripts in order, then upload or paste the Streamlit files through Snowsight.

## Safety Boundary

- All hospital, patient-flow, staffing, safety, and clinic records are synthetic.
- No direct identifiers are generated.
- Patient-level examples, where present, use synthetic IDs and minimal fields.
- Real open data is used only for public context such as respiratory surveillance, weather, AQHI, population, and calendar effects.
- Future production mapping must use curated governed views, not direct PHI tables.

