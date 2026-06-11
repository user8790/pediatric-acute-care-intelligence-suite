# v3 Snowflake Learning System Layer

The learning layer uses synthetic demonstration data and is not validated for clinical decision-making.

## Writeback Tables

The required Snowflake writeback contract is:

- APP.SCENARIO_RUN_LOG
- APP.USER_ANNOTATION
- APP.WARNING_ACKNOWLEDGEMENT
- APP.METRIC_ISSUE_FLAG
- APP.MODEL_REVIEW_NOTE
- APP.GOVERNANCE_DECISION
- APP.VALIDATION_REVIEW
- APP.PANEL_FEEDBACK
- APP.HUDDLE_REVIEW_EVENT
- APP.LEARNING_SYSTEM_OUTCOME_REVIEW

Each event includes event_id, event_type, created_at, created_by, app_area, site_id, unit_or_program, related_ids, status, severity, note, payload_json, and synthetic_demo_flag.

## Scope

This is not Connect Care writeback. It is Snowflake-side operational intelligence memory for scenario replay, review notes, issue flags, acknowledgements, governance decisions, validation reviews, huddle events, and outcome review.
