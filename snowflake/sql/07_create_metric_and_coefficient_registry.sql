-- v3 metric, coefficient, and threshold registry.
USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE TABLE CONFIG.V3_METRIC_REGISTRY (
  metric_id STRING,
  name STRING,
  formula STRING,
  source_fields STRING,
  cadence STRING,
  owner STRING,
  validation STRING,
  caveat STRING,
  reviewed_date DATE,
  classification STRING
);

CREATE OR REPLACE TABLE CONFIG.V3_COEFFICIENT_REGISTRY (
  coefficient_id STRING,
  coefficient_name STRING,
  applies_to STRING,
  value FLOAT,
  unit STRING,
  lower_bound FLOAT,
  upper_bound FLOAT,
  owner STRING,
  review_status STRING,
  reviewed_at TIMESTAMP_NTZ,
  caveat STRING,
  synthetic_demo_flag BOOLEAN
);

CREATE OR REPLACE TABLE CONFIG.V3_WARNING_LOGIC_REGISTRY (
  warning_id STRING,
  asset_id STRING,
  metric_id STRING,
  panel_id STRING,
  condition STRING,
  threshold STRING,
  severity STRING,
  acknowledgement_required BOOLEAN,
  alert_burden_cap_per_week NUMBER,
  rollback_flag BOOLEAN,
  owner STRING,
  status STRING,
  caveat STRING,
  synthetic_demo_flag BOOLEAN
);
