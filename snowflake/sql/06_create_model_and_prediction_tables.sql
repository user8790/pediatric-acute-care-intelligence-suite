-- v3 model registry and synthetic prediction outputs.
USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE TABLE MODEL.V3_MODEL_REGISTRY (
  asset_id STRING,
  name STRING,
  domain STRING,
  output_type STRING,
  intended_use STRING,
  not_intended_use STRING,
  source_data STRING,
  features STRING,
  model_class STRING,
  training_config_window STRING,
  validation_window STRING,
  cadence STRING,
  calibration_status STRING,
  drift_status STRING,
  subgroup_performance STRING,
  thresholds STRING,
  alert_burden STRING,
  false_positive_false_negative_review STRING,
  governance_status STRING,
  deployment_status STRING,
  owner STRING,
  sponsor STRING,
  last_reviewed DATE,
  next_review DATE,
  panels STRING,
  warnings STRING,
  caveats STRING,
  fallback STRING,
  rollback_plan STRING,
  related_outputs STRING,
  evidence_trail STRING,
  synthetic_evidence STRING
);

CREATE OR REPLACE TABLE MODEL.V3_PREDICTION_OUTPUT (
  output_id STRING,
  asset_id STRING,
  output_ts TIMESTAMP_NTZ,
  site_id STRING,
  unit_or_program STRING,
  score FLOAT,
  threshold FLOAT,
  severity STRING,
  explanation_json VARIANT,
  synthetic_demo_flag BOOLEAN
);
