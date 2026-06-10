# v2 Architecture

## Tracks

### Showcase

- `apps/showcase/src/pages/`: overview, inpatient, ambulatory, simulation, methods, governance, walkthrough.
- `apps/showcase/src/components/`: product shell, KPI tiles, panels, structured lists, ECharts bridge, chart primitives.
- `apps/showcase/src/features/`: domain modules for inpatient, ambulatory, simulation, methods, and governance.
- `apps/showcase/src/data/`: v2 data contracts, loader, fallback data.
- `apps/showcase/public/data/v2/`: generated app-ready JSON assets.

The showcase is static and Vercel-friendly. Complex simulation and model outputs are precomputed at build time.

### Streamlit/Snowflake

- `apps/snowflake_streamlit/inpatient/streamlit_app.py`
- `apps/snowflake_streamlit/ambulatory/streamlit_app.py`
- `apps/snowflake_streamlit/shared/lib/common.py`
- `apps/snowflake_streamlit/shared/sample_data/v2_*.csv`

The Streamlit apps query Snowflake marts when available and use local sample CSVs for public/local demonstration. They avoid custom components and external calls.

### Snowflake

Scripts remain ordered for Snowsight:

1. Context and roles
2. Database/schema creation
3. Synthetic raw tables
4. Synthetic data
5. Curated views
6. Base marts
7. Model output tables
8. Coefficients/config
9. Quality checks
10. Optional Streamlit objects
11. Smoke tests
12. V2 scenario marts
13. V2 forecast marts

The canonical execution order is files `00` through `12`.

## Data Boundary

Future real data must map through curated governed views. The apps should query aggregate marts, not raw PHI tables. Patient-level detail is suppressed by default.
