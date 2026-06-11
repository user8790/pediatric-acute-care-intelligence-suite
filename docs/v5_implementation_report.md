# V5 Showcase Implementation Report

Date: 2026-06-11

## Scope

This v5 pass converts the showcase into a more interactive pediatric command centre / progression hub using synthetic demonstration data only. It remains not connected to real hospital systems and is not validated for clinical decision-making.

The Snowflake/Streamlit path was kept conservative: v5 adds generated aggregate CSV samples under `apps/snowflake_streamlit/shared/sample_data/`, but no showcase-only frontend tooling or runtime dependency was added to the Streamlit/Snowflake apps.

## Research Inputs

Detailed research notes and source links are in `docs/v5_research_findings.md`.

Key benchmarks used:

- Johns Hopkins Capacity Command Center and Epic Capacity Management Dashboard patterns.
- Children's Mercy Patient Progression Hub patterns.
- Public AHS ED wait-time logic.
- Alberta respiratory virus dashboard structure.
- Alberta Children's Hospital and Stollery public context.
- AQHI, wildfire smoke, weather/climate, population, and school-calendar context.
- Snowflake healthcare/life-sciences patterns for aggregating operational, workforce, model, and governance data.

## What Changed

- Added a v5 synthetic command-centre generator: `packages/synthetic/generate_v5_command_center_data.py`.
- Added app-ready v5 JSON assets under `apps/showcase/public/data/v5/`.
- Added v5 aggregate sample CSVs under `apps/snowflake_streamlit/shared/sample_data/`.
- Pointed the showcase data loader at `/data/v5`.
- Expanded global controls to include persona, site, horizon, service, unit, program, and scenario.
- Wired global controls into visible metrics, narratives, object lists, charts, warnings, model filtering, and scenario outputs.
- Rebuilt System Posture, Inpatient, Ambulatory, Predictive Assets, and Scenario Lab as object-centred workspaces.
- Added clickable drawers for metrics, sites, units, programs, model cards, source-readiness badges, warnings, and scenarios.
- Added direct/derived/modelled/open-data/HR/finance badges and clickable source stoplights.
- Expanded synthetic depth to 36 unit-site objects, 42 program-site objects, 52 weeks of public-context rows, 8 scenario anchors, and 10 scenario controls.
- Added open-data forecast lift fields for respiratory, AQHI/smoke, and school/calendar effects.
- Added a v5 data integration test suite and refreshed Playwright e2e coverage.

## Tooling And Packages

No new package or plugin dependency was added.

Existing tools used:

- `@playwright/test` already existed in `apps/showcase/package.json`; used for e2e smoke and interaction tests.
- `echarts` already existed; reused for interactive charts.
- Vite/TypeScript/React dependencies were unchanged.

## Commands Run

```powershell
python packages/synthetic/generate_v5_command_center_data.py
pnpm --dir apps/showcase exec tsc -b --pretty false
pnpm --dir apps/showcase build
python -m pytest tests/integration/test_v5_assets.py tests/integration/test_app_smoke.py
python -m pytest tests/integration/test_v5_assets.py
python -m pytest
pnpm --dir apps/showcase test:e2e
```

Browser inspection:

- Local preview served with `pnpm --dir apps/showcase preview:e2e`.
- Desktop and mobile Playwright/browser screenshots inspected.
- A first-viewport KPI layout issue was found visually and fixed by giving metric tiles explicit grid spans.

## Test Results

- Python tests: `46 passed`.
- V5 asset tests: `7 passed`.
- Showcase Playwright e2e: `14 passed` across desktop and mobile projects.
- Showcase production build: passed.

## Acceptance Mapping

- Buttons/toggles visibly work or were removed: global controls and scenario toggles are covered by Playwright.
- Site/persona/horizon changes are obvious: control narrative and metrics update in the command-centre lens.
- At least 20 meaningful interactive charts exist: Playwright counts at least 20 canvases across public workspace pages.
- Unit and program drawers exist: covered by Playwright.
- Model-card drawers exist: covered by Playwright.
- Scenario sliders change outputs: covered by Playwright.
- Open-data context affects at least 3 forecasts or scenario assumptions: respiratory, AQHI/smoke, and calendar lift fields are asserted in v5 asset tests.
- Synthetic data is larger and more realistic: v5 generator creates larger service/unit/program/open-context/scenario layers.
- App builds and Playwright smoke tests confirm key interactions: passed.

## Remaining Gaps

- Open-data rows are cached synthetic proxies based on public-context patterns; live public data connectors are still intentionally out of scope for the deployed showcase.
- HR and finance fields are resource proxies, not validated operating or cost-accounting measures.
- Scenario effects use transparent proxy coefficients and are suitable for product demonstration only.
- Streamlit/Snowflake apps have v5 sample data available, but their UI has not yet been rebuilt around SimPy/CIW or the full v5 command-centre object model.
- No production clinical, staffing, finance, or operational decision should be made from these assets.
