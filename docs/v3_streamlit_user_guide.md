# v3 Streamlit User Guide

The Streamlit apps use synthetic demonstration data and are not validated for clinical decision-making.

## Apps

- apps/snowflake_streamlit/inpatient
- apps/snowflake_streamlit/ambulatory
- apps/snowflake_streamlit/gatekeeper_control_plane

## Gatekeeper

Use Executive lite for stoplights and Technical deep for registries, model cards, lineage, issues, and learning events. Local mode reads CSV samples from apps/snowflake_streamlit/shared/sample_data. Snowflake mode reads MART, MODEL, CONFIG, GOVERNANCE, QUALITY, OPEN_DATA, and APP objects.

## Writeback

The Gatekeeper form writes to Snowflake when a Snowpark session is available. If no session exists, it stores events in Streamlit session state for local demonstration.
