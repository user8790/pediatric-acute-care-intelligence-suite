# V2 Gap Analysis and Upgrade Plan

Branch: `v2-ambitious-showcase-and-snowflake-depth`

This v2 expansion treats the first pass as a useful foundation. The repository already has a paired showcase and Streamlit architecture, deterministic synthetic data, core queueing and simulation helpers, Snowflake SQL scripts, Streamlit Cloud wrappers, documentation, and public demo deployments. V2 deepens that foundation into a more executive-ready and technically credible pediatric operations intelligence suite.

## What Already Exists

- A Vite/React showcase app with inpatient, ambulatory, simulation, methods, quality, and governance tabs.
- Two Streamlit apps for inpatient and ambulatory workflows, with Snowpark detection and local sample fallback.
- Synthetic data generation for canonical pediatric operations tables.
- Core queueing, simulation, forecasting, modelling, explainability, optimization, and data-quality helpers.
- Ordered Snowflake SQL setup scripts for Snowsight.
- Docs for research, architecture, deployment, safety, methods, and future real-data mapping.
- Public demo URLs for Vercel and Streamlit Community Cloud.

## V2 Product Deepening

### UX Sophistication

- Refactor the showcase into modular pages and feature folders.
- Add richer visual components using Apache ECharts through React.
- Add executive posture, bottleneck, scenario frontier, data lineage, definitions, and walkthrough patterns.
- Make persona, site, and horizon selections more meaningful.

### Synthetic Data Realism

- Add v2 app-ready JSON assets with 12-month context, historical trends, forecast ribbons, scenario grids, coefficient registries, model cards, and quality status.
- Keep detailed synthetic data precomputed and publish only compact aggregate slices to the browser.
- Preserve strict privacy boundaries: synthetic surrogate IDs only, no names, no direct identifiers.

### Simulation and Queueing Credibility

- Add scenario frontier, tornado/sensitivity, queueing coefficient registry, uncertainty intervals, bed-flow Monte Carlo summaries, backlog clearance estimates, and overbooking frontiers.
- Replace simple linear UI deltas as the primary scenario method with precomputed scenario result grids and coefficient-driven outputs.

### Open-Data Integration

- Refresh open-data source documentation and v2 open-context snapshots for respiratory activity, AQHI/weather, school/holiday context, population, and travel-burden proxies.
- Keep runtime behaviour offline/cache-first.

### Model Outputs and Explainability

- Add model-card completeness checks.
- Add UI cards that show model name/version, horizon, uncertainty, top drivers, freshness, validation status, and caveat.

### Snowflake Transferability

- Harden Streamlit apps around Snowflake marts, small aggregate dataframes, native Streamlit, pandas/numpy/scipy/sklearn/statsmodels-compatible methods, and deterministic fallback formulas.
- Add v2 Snowflake SQL scripts for scenario and forecast marts.
- Update the no-CLI Snowsight guide and add a Snowflake transfer checklist.

### Executive Demo Polish

- Add v2 product brief, executive demo script, architecture, methods/coefficient documentation, model cards, known limitations, and testing report.
- Use Canadian English, “pediatric,” and “data-informed.”

## Concrete File-Level Changes Planned

- `apps/showcase/package.json`: add richer visualisation dependencies.
- `apps/showcase/src/App.tsx`: reduce to route/state orchestration.
- `apps/showcase/src/pages/*`: add landing, inpatient, ambulatory, simulation, methods, quality/governance, and walkthrough pages.
- `apps/showcase/src/features/**`: add domain-specific modules.
- `apps/showcase/src/components/**`: add ECharts, KPI, posture, scenario, lineage, and model-card components.
- `apps/showcase/src/data/**`: add v2 data loader and fallback.
- `apps/showcase/public/data/v2/*.json`: add app-ready aggregate data assets.
- `packages/synthetic/generate_v2_showcase_data.py`: generate v2 JSON and Streamlit sample marts.
- `apps/snowflake_streamlit/shared/lib/common.py`: remove SimPy/Ciw detection and add richer status helpers.
- `apps/snowflake_streamlit/**/streamlit_app.py`: add richer tabs, charts, scenario grids, model caveats, and mart/sample queries.
- `apps/snowflake_streamlit/shared/environment_optional_pending.yml`: remove SimPy and Ciw.
- `snowflake/sql/11_v2_scenario_marts.sql` and `snowflake/sql/12_v2_forecast_marts.sql`: add v2 mart support.
- `docs/*v2*` and transfer docs: add executive-ready v2 documentation.
- `tests/**`: add v2 data, coefficient, model-card, SQL, and Snowflake-safe dependency checks.

## Snowflake Streamlit Package Boundary

The Streamlit/Snowflake path will no longer reference SimPy or Ciw. They will not be detected, displayed, documented as optional Snowflake packages, included in Streamlit environments, or imported by Streamlit apps. Any future use of advanced simulation packages must be isolated to showcase-only or research-only code.
