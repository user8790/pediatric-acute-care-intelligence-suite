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
  name STRING,
  value FLOAT,
  units STRING,
  owner STRING,
  review_status STRING,
  caveat STRING,
  synthetic_demo_flag BOOLEAN
);
