# v3 Frontier Platform Architecture

This architecture uses synthetic demonstration data and is not validated for clinical decision-making.

## Layers

1. Direct operational signals: curated source views with source-readiness stoplights.
2. Derived operational intelligence: metric registry cards with formulas, cadence, owner, validation, and caveats.
3. Modelled, predictive, and AI assets: model cards with validation, calibration, drift, threshold, alert-burden, subgroup, rollback, and evidence-trail controls.

## Runtime Surfaces

- Vercel showcase: ambitious public product surface with local-only memory interactions.
- Streamlit in Snowflake: practical Snowsight-compatible operating apps using Snowflake marts and sample CSV fallbacks.
- Snowflake SQL: schemas RAW_SYNTH, CANONICAL, MART, MODEL, CONFIG, GOVERNANCE, APP, QUALITY, and OPEN_DATA.

## Control Flow

Curated source readiness feeds metric cards. Metric cards feed panels. Modelled assets feed warning overlays only after Gatekeeper review. Scenario runs, acknowledgements, notes, flags, and decisions write to APP and GOVERNANCE tables.
