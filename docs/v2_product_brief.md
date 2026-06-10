# v2 Product Brief

## Purpose

The Pediatric Acute Care Intelligence Suite v2 is a synthetic, executive-ready prototype for pediatric inpatient flow and ambulatory access. It is designed to make operational posture, forecast risk, bottlenecks, options, uncertainty, and caveats visible in one product experience.

The suite has two tracks:

- **Showcase app:** polished Vite/React product experience for public demonstration, executive walkthroughs, methods exploration, governance review, and scenario comparison.
- **Streamlit/Snowflake apps:** conservative, Snowflake-transferable operational tools for inpatient and ambulatory use, backed by curated marts, v2 sample fallbacks, and SQL-precomputed scenarios.

## Product Questions

The v2 experience is organised around seven questions:

- What is happening now?
- What is likely to happen next?
- Why is risk changing?
- Where is the bottleneck?
- What options are available?
- What are the trade-offs?
- How confident are we, and what caveats matter?

## Intended Use

The prototype supports data-informed planning conversations, demonstration, education, and technical transfer planning. It is not connected to AHS, Stollery, Alberta Children's Hospital, Connect Care, Epic, or a production Snowflake account.

All hospital, patient-flow, staffing, clinic, referral, safety, and model outputs are synthetic. The suite is not validated for clinical decision-making.

## v2 Additions

- Modular showcase app with overview, inpatient, ambulatory, simulation, methods, governance, and walkthrough pages.
- V2 generated JSON assets under `apps/showcase/public/data/v2/`.
- Rich ECharts-based visualisations for forecast ribbons, heatmaps, Sankey-style flow, scenario frontiers, sensitivity charts, and public context.
- Snowflake-safe Streamlit v2 apps with mission-control first tabs, Plotly charts, scenario grids, quality tabs, and model/method tabs.
- V2 SQL scripts for scenario marts, forecast marts, model cards, coefficients, quality status, and scenario run logging.
- Expanded transferability docs and contracts for future governed curated views.
