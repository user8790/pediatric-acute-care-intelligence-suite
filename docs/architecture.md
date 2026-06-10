# Architecture

The suite has two product implementations over one canonical pediatric operations model.

## Version A: Showcase

- Stack: Vite, React, TypeScript, lucide icons, SVG/CSS chart primitives.
- Data: `apps/showcase/public/demo-data.json`, generated from deterministic synthetic CSVs.
- Fallback: bundled `src/data/fallbackDemoData.ts`.
- Purpose: executive and clinical operations storytelling with realistic interactions.

## Version B: Snowflake Streamlit

- Stack: native Streamlit, pandas, Snowpark session detection.
- Deployment: Snowsight SQL worksheets and Streamlit file upload/copy.
- Data: curated marts under `PEDIATRIC_AHA_DEMO.MART`.
- Fallback: local sample CSVs for workstation smoke testing only.

## Data Flow

1. Synthetic generator creates canonical dimensions, facts, model outputs, scenario outputs, quality checks, and app payloads.
2. Showcase reads static JSON for offline demos.
3. Streamlit apps query Snowflake marts when a Snowpark session exists.
4. Future real data maps into curated Snowflake views using the contracts in `packages/contracts`.

## Boundary

Raw future clinical/operational tables are never queried by apps. Apps query curated views or marts only.

