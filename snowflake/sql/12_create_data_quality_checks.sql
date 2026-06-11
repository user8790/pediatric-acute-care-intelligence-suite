-- v3 data-quality checks for synthetic operational layer.
USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE TABLE QUALITY.V3_DATA_QUALITY_CHECK (
  check_id STRING,
  object_name STRING,
  check_name STRING,
  status STRING,
  failed_rows NUMBER,
  severity STRING,
  last_checked_at TIMESTAMP_NTZ,
  owner STRING,
  synthetic_demo_flag BOOLEAN
);

CREATE OR REPLACE TABLE GOVERNANCE.V3_DATA_QUALITY_RULE (
  check_id STRING,
  source_id STRING,
  rule_name STRING,
  rule_type STRING,
  severity STRING,
  threshold STRING,
  status STRING,
  failed_rows NUMBER,
  last_run_at TIMESTAMP_NTZ,
  owner STRING,
  caveat STRING,
  synthetic_demo_flag BOOLEAN
);

CREATE OR REPLACE VIEW QUALITY.V3_SMALL_CELL_SUPPRESSION_REVIEW AS
SELECT source_id, small_cell_suppression, overall_readiness, caveat
FROM GOVERNANCE.V3_DIRECT_LINK_VALIDATION
WHERE small_cell_suppression <> 'pass' OR overall_readiness <> 'ready';
