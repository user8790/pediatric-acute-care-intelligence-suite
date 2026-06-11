-- v3 scenario tables and marts.
USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE TABLE MART.V3_SCENARIO (
  scenario_id STRING,
  domain STRING,
  scenario_name STRING,
  impact_score FLOAT,
  effort_score FLOAT,
  operational_risk_score FLOAT,
  primary_outcome STRING,
  outcome_value FLOAT,
  readiness STRING,
  classification STRING,
  writeback_table STRING,
  synthetic_demo_flag BOOLEAN
);

CREATE OR REPLACE VIEW MART.V3_SCENARIO_FRONTIER AS
SELECT
  scenario_id,
  domain,
  scenario_name,
  impact_score,
  effort_score + operational_risk_score / 3 AS effort_risk_score,
  primary_outcome,
  outcome_value,
  readiness,
  classification
FROM MART.V3_SCENARIO;
