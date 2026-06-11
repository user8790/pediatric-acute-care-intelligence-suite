-- v3 direct-link validation stoplight.
USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE TABLE GOVERNANCE.V3_DIRECT_LINK_VALIDATION (
  source_id STRING,
  source_view_present STRING,
  field_populated STRING,
  freshness STRING,
  row_count STRING,
  timestamp_logic STRING,
  referential_integrity STRING,
  metric_definition_approved STRING,
  small_cell_suppression STRING,
  overall_readiness STRING,
  freshness_minutes NUMBER,
  row_count_value NUMBER,
  owner STRING,
  last_reviewed_at TIMESTAMP_NTZ,
  caveat STRING
);

CREATE OR REPLACE VIEW GOVERNANCE.V3_DIRECT_LINK_STOPLIGHT AS
SELECT
  source_id,
  overall_readiness,
  IFF(overall_readiness = 'ready', 'green', IFF(overall_readiness = 'blocked', 'red', 'amber')) AS stoplight,
  freshness,
  row_count,
  metric_definition_approved,
  small_cell_suppression,
  caveat
FROM GOVERNANCE.V3_DIRECT_LINK_VALIDATION;
