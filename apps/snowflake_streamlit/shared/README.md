# Snowflake Streamlit Shared Layer

The Streamlit apps use this shared helper package for:

- Snowpark session detection.
- Curated mart queries.
- Local CSV sample-mode fallback.
- Optional package detection.
- Scenario-run storage with Snowflake writeback when permitted.

The apps do not call external APIs and do not use custom Streamlit components.

