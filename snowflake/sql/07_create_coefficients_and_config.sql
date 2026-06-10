-- 07_create_coefficients_and_config.sql
-- Transparent coefficients for queueing, simulation, and scenario levers.

USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE TABLE CONFIG.QUEUEING_COEFFICIENTS (
  coefficient_name STRING,
  coefficient_symbol STRING,
  definition STRING,
  default_value FLOAT,
  caveat STRING
);

INSERT OVERWRITE INTO CONFIG.QUEUEING_COEFFICIENTS
VALUES
  ('arrival rate', 'lambda', 'Arrivals per time unit by site/service/hour.', 4.0, 'Estimate from synthetic data.'),
  ('service rate', 'mu', 'Completions per server/resource/time unit.', 0.25, 'Estimate from synthetic data.'),
  ('servers/resources', 'c', 'Beds, rooms, providers, or constrained resources.', 12, 'Resource type depends on workflow.'),
  ('interarrival variability', 'Ca2', 'Squared coefficient of variation for interarrival times.', 1, 'Fallback uses Poisson assumption.'),
  ('service variability', 'Cs2', 'Squared coefficient of variation for service times.', 1.2, 'LOS and clinic service times are variable.'),
  ('respiratory surge multiplier', 'resp_surge', 'Seasonal multiplier for respiratory demand.', 1.35, 'Public context proxy only.'),
  ('weather seasonality coefficient', 'weather', 'Weather and air-quality context multiplier.', 1.05, 'Ecological context only.'),
  ('travel burden modifier', 'travel', 'Aggregated access-friction proxy.', 1.08, 'Use carefully and monitor fairness.');

CREATE OR REPLACE TABLE CONFIG.SCENARIO_LIBRARY (
  scenario_id STRING,
  scenario_name STRING,
  product_area STRING,
  lever_name STRING,
  default_value FLOAT,
  lower_bound FLOAT,
  upper_bound FLOAT,
  interpretation STRING
);

INSERT OVERWRITE INTO CONFIG.SCENARIO_LIBRARY
VALUES
  ('SCN_RESP_SURGE', 'Respiratory surge', 'inpatient', 'respiratory_multiplier', 1.35, 0.8, 1.8, 'Models winter respiratory pressure.'),
  ('SCN_SURGE_BEDS', 'Open surge beds', 'inpatient', 'additional_beds', 8, 0, 30, 'Adds effective beds if staffing supports them.'),
  ('SCN_DISCHARGE', 'Increase morning discharges', 'inpatient', 'discharge_support_pct', 10, 0, 30, 'Moves discharge completion earlier.'),
  ('SCN_ADD_CLINIC', 'Add clinics/sessions', 'ambulatory', 'added_sessions', 5, 0, 20, 'Adds weekly clinic capacity.'),
  ('SCN_OVERBOOK', 'Guarded overbooking', 'ambulatory', 'overbook_slots', 4, 0, 12, 'Uses no-show risk with overflow guardrails.'),
  ('SCN_TRIAGE', 'Reduce triage turnaround', 'ambulatory', 'triage_days_reduced', 2, 0, 10, 'Improves referral readiness and urgent-slot routing.');

CREATE OR REPLACE TABLE CONFIG.APP_METADATA (
  app_version STRING,
  synthetic_mode BOOLEAN,
  clinical_use_status STRING,
  last_config_update DATE
);

INSERT OVERWRITE INTO CONFIG.APP_METADATA
VALUES ('0.1.0', TRUE, 'Not validated for clinical decision-making', CURRENT_DATE());

