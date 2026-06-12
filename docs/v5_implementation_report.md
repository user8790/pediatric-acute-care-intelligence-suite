# V5 Showcase Implementation Report

Date: 2026-06-11

Update: 2026-06-12 decision-grade refinement pass.

Update: 2026-06-12 15-lens command-desk operating-layer pass.

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

## Decision-Grade Refinement Pass

This pass keeps the v5 design language and object-centred workspace, then adds the next layer of trust and usefulness:

- Added concise "so what / now what" interpretation objects for key operational signals. Each interpretation includes what is changing, likely drivers, review/action prompts, confidence language, role emphasis, and signal ownership.
- Added clearer role value for executive/provincial leadership, site/program leadership, charge/flow leadership, clinical leadership, and Analytics / Healthcare Informatics / AI governance. The math remains shared; the product lens changes by persona.
- Added a public `Data & Model Readiness` page focused on implementation transparency. It shows synthetic demo readiness, real-feed status, calculation status, coefficient status, pending model status, validation status, governance status, owners, blockers, and next implementation steps.
- Added an action-and-learning loop that traces a signal from detection, review, action, follow-up, learning, and spread. The loop appears in the scenario lab and the AI signal simulation workspace.
- Added a dedicated `AI Signals` workspace with four ultra-deep synthetic implementation rehearsals:
  - Triage and LOS orchestration.
  - Rare-disease case-finding simulation inspired by ThinkRare-style phenotype patterning.
  - General deterioration early-warning simulation.
  - NEC recognition rehearsal for neonatal safety implementation design.
- Added transparent proxy coefficients, feature families, demand/supply factors, threshold logic, validation/governance state, confidence trajectory charts, implementation steps, and source lineage for each AI signal simulation.
- Preserved the safety boundary: all AI signal pages use aggregate synthetic demonstration data, do not display direct personal identifiers, and are not validated for clinical decision-making.

## Implementation Transparency Additions

The new readiness section intentionally shows many real-data items as pending, blocked, or not connected. That is the desired implementation posture: synthetic future-state variables can appear ready in the demo while production feeds, coefficients, models, validation, governance, and release gates remain honest about real-world work still required.

The readiness registry now covers:

- Synthetic demo variables and generated source-layer assets.
- Real data feeds and curated Snowflake-view dependencies.
- Metric definitions and calculation ownership.
- Proxy coefficients and future coefficient validation work.
- Pending models and release-gate blockers.
- Validation, drift monitoring, alert-burden, and subgroup calibration status.
- Governance, clinical safety, privacy, and rollback dependencies.
- Next implementation steps for every readiness object.

## Clinical Signal Simulation Boundaries

The four AI signal pages are implementation prototypes. They are designed to show what decision-grade transparency could look like before any production clinical use:

- The triage/LOS orchestration page is an operational demand-and-supply rehearsal, not a triage directive.
- The rare-disease page is a governed case-finding workflow concept, not a diagnostic claim.
- The early-warning page is a silent-evaluation and alert-burden design, not a bedside alarm.
- The NEC page is a neonatal safety implementation design with blocked governance status by default.

Each page shows clinical boundary language, source readiness, model-family assumptions, proxy coefficients, threshold logic, validation state, governance state, affected operational objects, and next implementation steps.

## 15-Lens Command-Desk Pass

Detailed review notes are in `docs/v6_15_lens_command_centre_review.md`.

This pass advances the showcase from object-centred dashboard to operating workbench:

- Added public `Command Desk` page.
- Added generated `expertLensReviews`, `decisionPackets`, `operatingCadence`, and `escalationLanes` to the command-centre context.
- Added decision-packet worklist with urgency, owner, signal, interpretation, scenario link, evidence-to-clear, safety gate, HR/finance constraints, follow-up window, and learning metric.
- Added packet, expert-lens, huddle, and escalation drawers using the existing object-drawer pattern.
- Added interactive 15-lens review board reflecting software architecture, frontend, informatics, AI safety, modelling, queueing, operations, pediatric, nursing, human factors, implementation science, interoperability, and executive strategy lenses.
- Added huddle/cadence and escalation-lane surfaces so signals move toward review, action, follow-up, and organizational learning.
- Added local synthetic command-packet review capture into the Learning Memory page.

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
Direct-identifier guardrail scan over v5 showcase assets and edited showcase source
```

Browser inspection:

- Local preview served with `pnpm --dir apps/showcase preview:e2e`.
- Desktop and mobile Playwright/browser screenshots inspected.
- A first-viewport KPI layout issue was found visually and fixed by giving metric tiles explicit grid spans.

## Test Results

- Python tests: `47 passed`.
- V5 asset tests: `8 passed`.
- Showcase Playwright e2e: `16 passed` across desktop and mobile projects.
- Showcase production build: passed.
- Direct-identifier guardrail scan over generated v5 showcase assets and edited showcase source: no matches.

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
- So what / now what interpretation exists for key signals: generated interpretation rows are asserted in v5 asset tests and visible in System Posture, Inpatient, and Ambulatory workspaces.
- Role differentiation is visible without changing the underlying math: persona-specific role guidance is generated and shown in the workspace.
- Implementation readiness is explicit: `Data & Model Readiness` page and readiness registry are covered by Playwright.
- Action-and-learning loop is visible: scenario and AI signal pages show detection-to-spread stages.
- Four ultra-deep AI signal simulation pages exist: covered by v5 asset tests and Playwright.
- Command Desk operating layer exists: generated packets, expert lenses, huddles, and escalation lanes are asserted in v5 asset tests and covered by Playwright.

## Remaining Gaps

- Open-data rows are cached synthetic proxies based on public-context patterns; live public data connectors are still intentionally out of scope for the deployed showcase.
- HR and finance fields are resource proxies, not validated operating or cost-accounting measures.
- Scenario effects use transparent proxy coefficients and are suitable for product demonstration only.
- AI signal simulations are not clinical decision support; they require silent evaluation, local calibration, safety/governance review, human-factors testing, alert-burden review, release gates, rollback procedures, and monitoring before any production consideration.
- Streamlit/Snowflake apps have v5 sample data available, but their UI has not yet been rebuilt around SimPy/CIW or the full v5 command-centre object model.
- No production clinical, staffing, finance, or operational decision should be made from these assets.
