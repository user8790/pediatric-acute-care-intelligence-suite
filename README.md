# Pediatric Acute Care Intelligence Suite

Production-shaped v2 prototype suite for pediatric inpatient and ambulatory operations intelligence, inspired by Alberta pediatric operational patterns.

This is a synthetic demonstration. It is not connected to Alberta Health Services, Epic, Connect Care, Stollery, Alberta Children's Hospital, or Snowflake production data. It is not validated for clinical decision-making.

## What Is Included

- Showcase track: a modular TypeScript + React product experience under `apps/showcase`.
- Streamlit/Snowflake track: two conservative transferable apps under `apps/snowflake_streamlit`.
- Deterministic synthetic pediatric operations data generator under `packages/synthetic`.
- Transparent queueing, simulation, forecasting, modelling, data-quality, and explainability helpers under `packages/core`.
- SQL-first Snowflake setup scripts under `snowflake/sql`.
- Documentation for architecture, deployment, methods, safety, contracts, and future real-data mapping under `docs`.

## Quick Start

```powershell
python packages/synthetic/generate_synthetic_data.py
python packages/synthetic/generate_v2_showcase_data.py
python -m pytest
pnpm install
pnpm run dev:showcase
```

The showcase app runs locally with cached generated data and built-in fallbacks.

Start with `docs/v2_product_brief.md`, `docs/v2_executive_demo_script.md`, and `docs/v2_gap_analysis_and_upgrade_plan.md` for the v2 product story.

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

Run SQL scripts `00` through `12` in order, then upload or paste the Streamlit files through Snowsight.

## Streamlit Community Cloud Demo Path

For public/sample-mode Streamlit Cloud demos, use:

- `docs/README_DEPLOY_STREAMLIT_CLOUD.md`
- Inpatient entrypoint: `apps/streamlit_cloud/inpatient/streamlit_app.py`
- Ambulatory entrypoint: `apps/streamlit_cloud/ambulatory/streamlit_app.py`

These wrappers avoid the Snowflake `environment.yml` dependency behavior and run with committed synthetic sample CSVs.

## Vercel Showcase Deployment

The root `vercel.json` builds the showcase app from the monorepo root:

```powershell
pnpm install --frozen-lockfile
pnpm run build:showcase
```

Output directory: `apps/showcase/dist`.

Published apps:

- Showcase: https://pediatric-acute-care-intelligence-s.vercel.app/
- Streamlit inpatient: https://pediatric-acute-care-inpatient.streamlit.app/
- Streamlit ambulatory: https://pediatric-acute-care-ambulatory.streamlit.app/

## Safety Boundary

- All hospital, patient-flow, staffing, safety, and clinic records are synthetic.
- No direct identifiers are generated.
- Patient-level examples, where present, use synthetic IDs and minimal fields.
- Real open data is used only for public context such as respiratory surveillance, weather, AQHI, population, and calendar effects.
- Future production mapping must use curated governed views, not direct PHI tables.
