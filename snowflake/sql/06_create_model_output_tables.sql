-- 06_create_model_output_tables.sql
-- Model registry, output placeholders, and monitoring tables.

USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE TABLE MODEL.DIM_MODEL_REGISTRY (
  model_id STRING,
  model_name STRING,
  version STRING,
  owner STRING,
  intended_use STRING,
  prediction_horizon STRING,
  training_data STRING,
  validation_status STRING,
  caveat STRING,
  last_reviewed DATE
);

INSERT OVERWRITE INTO MODEL.DIM_MODEL_REGISTRY
VALUES
  ('MODEL_INPT_OCC', 'probabilistic occupancy forecast', '0.1.0', 'Synthetic prototype analytics team', 'Scenario planning and executive demonstration', '6-72 hours', 'Deterministic synthetic pediatric operations data', 'Not validated for clinical decision-making', 'Future production use requires local validation.', CURRENT_DATE()),
  ('MODEL_DISCHARGE', 'discharge by time-band probability', '0.1.0', 'Synthetic prototype analytics team', 'Scenario planning and executive demonstration', 'same day', 'Deterministic synthetic pediatric operations data', 'Not validated for clinical decision-making', 'Future production use requires local validation.', CURRENT_DATE()),
  ('MODEL_AMB_BACKLOG', 'ambulatory backlog forecast', '0.1.0', 'Synthetic prototype analytics team', 'Scenario planning and executive demonstration', '1-26 weeks', 'Deterministic synthetic pediatric operations data', 'Not validated for clinical decision-making', 'Future production use requires local validation.', CURRENT_DATE()),
  ('MODEL_NOSHOW', 'no-show late-cancel risk', '0.1.0', 'Synthetic prototype analytics team', 'Scenario planning and executive demonstration', 'appointment date', 'Deterministic synthetic pediatric operations data', 'Not validated for clinical decision-making', 'Future production use requires local validation.', CURRENT_DATE());

CREATE OR REPLACE TABLE MODEL.FCT_MODEL_MONITORING (
  model_id STRING,
  metric_name STRING,
  metric_value FLOAT,
  subgroup STRING,
  monitoring_ts TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  caveat STRING
);

CREATE OR REPLACE TABLE MODEL.FCT_PREDICTION_AUDIT (
  prediction_id STRING,
  model_id STRING,
  prediction_horizon STRING,
  data_freshness_ts TIMESTAMP_NTZ,
  top_driver_1 STRING,
  top_driver_2 STRING,
  top_driver_3 STRING,
  validation_status STRING
);

