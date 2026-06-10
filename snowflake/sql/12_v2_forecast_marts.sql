-- 12_v2_forecast_marts.sql
-- v2 app marts for Streamlit in Snowflake and Snowflake-transferable demos.
-- Synthetic demonstration data only. Not validated for clinical decision-making.

USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE TABLE MODEL.DIM_V2_MODEL_REGISTRY (
  model_id STRING,
  model_name STRING,
  version STRING,
  prediction_horizon STRING,
  intended_use STRING,
  training_data STRING,
  validation_status STRING,
  metrics STRING,
  top_driver_method STRING,
  data_freshness TIMESTAMP_NTZ,
  caveat STRING
);

INSERT OVERWRITE INTO MODEL.DIM_V2_MODEL_REGISTRY VALUES
  ('MODEL_INPT_OCC_V2', 'Probabilistic occupancy forecast', 'v2.0', '6-72 hours', 'Synthetic scenario planning and executive demonstration', 'Deterministic synthetic pediatric operations data', 'Synthetic validation only; not validated for clinical decision-making', 'MAE, interval coverage', 'Permutation importance and coefficient decomposition', CURRENT_TIMESTAMP(), 'Future production use requires local temporal validation, subgroup calibration, and governance approval.'),
  ('MODEL_INPT_DISCHARGE_V2', 'Discharge by time-band probability', 'v2.0', 'same day', 'Synthetic scenario planning and executive demonstration', 'Deterministic synthetic pediatric operations data', 'Synthetic validation only; not validated for clinical decision-making', 'Brier, calibration', 'Permutation importance and coefficient decomposition', CURRENT_TIMESTAMP(), 'Future production use requires local temporal validation, subgroup calibration, and governance approval.'),
  ('MODEL_INPT_PICU_V2', 'PICU/NICU pressure forecast', 'v2.0', '6-72 hours', 'Synthetic scenario planning and executive demonstration', 'Deterministic synthetic pediatric operations data', 'Synthetic validation only; not validated for clinical decision-making', 'MAE, threshold calibration', 'Permutation importance and coefficient decomposition', CURRENT_TIMESTAMP(), 'Future production use requires local temporal validation, subgroup calibration, and governance approval.'),
  ('MODEL_AMB_BACKLOG_V2', 'Ambulatory backlog forecast', 'v2.0', '4-26 weeks', 'Synthetic scenario planning and executive demonstration', 'Deterministic synthetic pediatric operations data', 'Synthetic validation only; not validated for clinical decision-making', 'MAE, pinball loss', 'Permutation importance and coefficient decomposition', CURRENT_TIMESTAMP(), 'Future production use requires local temporal validation, subgroup calibration, and governance approval.'),
  ('MODEL_AMB_NOSHOW_V2', 'No-show and late-cancel probability', 'v2.0', 'appointment date', 'Synthetic scenario planning and executive demonstration', 'Deterministic synthetic pediatric operations data', 'Synthetic validation only; not validated for clinical decision-making', 'AUROC, Brier, subgroup calibration', 'Permutation importance and coefficient decomposition', CURRENT_TIMESTAMP(), 'Future production use requires local temporal validation, subgroup calibration, and governance approval.'),
  ('MODEL_AMB_BREACH_V2', 'Urgent breach risk', 'v2.0', '1-12 weeks', 'Synthetic scenario planning and executive demonstration', 'Deterministic synthetic pediatric operations data', 'Synthetic validation only; not validated for clinical decision-making', 'PR-AUC, calibration', 'Permutation importance and coefficient decomposition', CURRENT_TIMESTAMP(), 'Future production use requires local temporal validation, subgroup calibration, and governance approval.');

CREATE OR REPLACE VIEW MART.MART_V2_INPATIENT_MISSION_CONTROL AS
SELECT
  site_id,
  site_id AS site_name,
  census,
  physical_beds,
  effective_beds,
  occupancy_pct,
  ed_boarders,
  predicted_discharges,
  staffing_gap_pct,
  LEAST(GREATEST((occupancy_pct - 0.80) * 2.2, 0.02), 0.92) AS prob_above_95,
  LEAST(GREATEST(occupancy_pct + 0.02, 0.72), 1.08) AS picu_nicu_pressure,
  CURRENT_TIMESTAMP() AS data_freshness,
  'respiratory activity' AS top_driver_1,
  'effective staffed capacity' AS top_driver_2,
  'discharge reliability' AS top_driver_3,
  data_mode,
  caveat
FROM MART.MART_INPATIENT_MISSION_CONTROL;

CREATE OR REPLACE VIEW MART.MART_V2_INPATIENT_FLOW AS
SELECT
  c.site_id,
  c.unit_id,
  COALESCE(u.unit_name, c.service_line) AS unit_name,
  c.service_line,
  c.census,
  c.physical_beds,
  c.effective_beds,
  c.occupancy_pct,
  c.staffing_gap_pct,
  c.ed_boarders,
  c.predicted_discharges,
  c.respiratory_multiplier,
  c.ts_hour AS data_freshness
FROM CURATED.VW_BED_CENSUS_HOURLY c
LEFT JOIN RAW_SYNTH.DIM_UNIT u
  ON c.unit_id = u.unit_id
QUALIFY ROW_NUMBER() OVER (PARTITION BY c.site_id, c.unit_id ORDER BY c.ts_hour DESC) = 1;

CREATE OR REPLACE VIEW MART.MART_V2_INPATIENT_FORECAST AS
SELECT
  site_id,
  prediction_horizon_hours AS horizon_hours,
  'occupancy_forecast_gradient_boosted_synth' AS model_name,
  'v2.0' AS model_version,
  prediction,
  p10,
  p90,
  LEAST(GREATEST((prediction - 0.88) * 2.8, 0.03), 0.96) AS threshold_probability,
  top_driver_1,
  top_driver_2,
  top_driver_3,
  CURRENT_TIMESTAMP() AS freshness,
  validation_status,
  'Scenario planning estimate only.' AS caveat
FROM CURATED.VW_MODEL_PREDICTION_INPATIENT
WHERE metric_name = 'occupancy_pct';

CREATE OR REPLACE VIEW MART.MART_V2_INPATIENT_OR_PACU AS
WITH days AS (
  SELECT DATEADD(day, -SEQ4(), CURRENT_DATE()) AS date_value
  FROM TABLE(GENERATOR(ROWCOUNT => 60))
),
sites AS (
  SELECT site_id FROM RAW_SYNTH.DIM_SITE
)
SELECT
  d.date_value AS date,
  s.site_id,
  IFF(DAYOFWEEKISO(d.date_value) <= 5, 16, 3) AS elective_cases,
  IFF(DAYOFWEEKISO(d.date_value) <= 5, 4, 5) AS urgent_cases,
  IFF(DAYOFWEEKISO(d.date_value) <= 5, 7, 3) AS post_op_bed_demand,
  IFF(DAYOFWEEKISO(d.date_value) <= 5, 0.14, 0.08) AS pacu_hold_risk,
  IFF(DAYOFWEEKISO(d.date_value) <= 5, 0.08, 0.04) AS cancellation_risk
FROM days d
CROSS JOIN sites s;

CREATE OR REPLACE VIEW MART.MART_V2_INPATIENT_HIGH_RESOURCE AS
SELECT
  site_id,
  service_line,
  MAX(physical_beds) AS high_resource_beds,
  MAX(census) AS occupied,
  3 AS step_down_ready_waiting,
  2 AS transfer_in_requests,
  8 AS ventilator_proxy_demand_synth,
  1.22 AS respiratory_surge_sensitivity
FROM MART.MART_V2_INPATIENT_FLOW
WHERE UPPER(service_line) IN ('PICU', 'NICU')
GROUP BY site_id, service_line;

CREATE OR REPLACE VIEW MART.MART_V2_INPATIENT_STAFFING AS
SELECT
  site_id,
  unit_id,
  unit_name,
  ROUND(effective_beds * 2.8, 1) AS scheduled_hours,
  ROUND(census * IFF(UPPER(service_line) IN ('PICU', 'NICU'), 3.4, 2.95), 1) AS required_hours,
  GREATEST(physical_beds - effective_beds, 0) AS effective_beds_lost,
  ROUND(occupancy_pct * IFF(UPPER(service_line) IN ('PICU', 'NICU'), 1.16, 1.0), 3) AS workload_index
FROM MART.MART_V2_INPATIENT_FLOW;

CREATE OR REPLACE VIEW MART.MART_V2_INPATIENT_DISCHARGE_BARRIERS AS
SELECT
  site_id,
  barrier_type AS barrier,
  active_count,
  median_age_hours,
  median_age_hours * 2.1 AS p90_age_hours
FROM CURATED.VW_DISCHARGE_BARRIER;

CREATE OR REPLACE VIEW MART.MART_V2_INPATIENT_HANDSHAKE AS
SELECT
  site_id,
  unit_id,
  unit_name,
  ed_boarders AS ed_admissions_awaiting_bed,
  90 + ed_boarders * 8 AS decision_to_bed_median_min,
  35 + IFF(occupancy_pct > 0.95, 15, 0) AS bed_to_arrival_median_min,
  CEIL(ed_boarders / 3) AS consult_bottleneck_count
FROM MART.MART_V2_INPATIENT_FLOW;

CREATE OR REPLACE VIEW MART.MART_V2_INPATIENT_SAFETY AS
SELECT
  site_id,
  unit_id,
  unit_name,
  CEIL(occupancy_pct * 2) AS deterioration_watch_synth,
  IFF(LOWER(service_line) IN ('respiratory', 'picu'), 2, 1) AS sepsis_screen_signal_synth,
  1 AS medication_process_signal_synth,
  0.055 AS readmission_revisit_proxy
FROM MART.MART_V2_INPATIENT_FLOW;

CREATE OR REPLACE VIEW MART.MART_V2_AMBULATORY_MISSION_CONTROL AS
SELECT
  site_id,
  SUM(waitlist_total) AS waitlist_total,
  SUM(waitlist_over_target) AS waitlist_over_target,
  MEDIAN(median_wait_days) AS median_wait_days,
  MEDIAN(p90_wait_days) AS p90_wait_days,
  MEDIAN(third_next_available_days) AS third_next_available_days,
  AVG(urgent_breach_risk) AS urgent_breach_risk,
  SUM(ROUND(waitlist_total / 30) - ROUND(waitlist_total / 34)) AS demand_capacity_gap,
  CURRENT_TIMESTAMP() AS data_freshness,
  'referral demand' AS top_driver_1,
  'template capacity' AS top_driver_2,
  'no-show/late-cancel risk' AS top_driver_3,
  'Synthetic demonstration data' AS data_mode,
  'Not validated for clinical decision-making' AS caveat
FROM MART.MART_AMBULATORY_ACCESS_MISSION_CONTROL
GROUP BY site_id;

CREATE OR REPLACE VIEW MART.MART_V2_AMBULATORY_ACCESS AS
SELECT
  site_id,
  program,
  waitlist_total,
  waitlist_over_target,
  median_wait_days,
  p90_wait_days,
  third_next_available_days,
  urgent_breach_risk,
  ROUND(waitlist_total / 30) - ROUND(waitlist_total / 34) AS demand_capacity_gap,
  caveat
FROM MART.MART_AMBULATORY_ACCESS_MISSION_CONTROL;

CREATE OR REPLACE VIEW MART.MART_V2_AMBULATORY_FORECAST AS
SELECT
  site_id,
  program,
  prediction_horizon_weeks AS horizon_weeks,
  'ambulatory_backlog_forecast_synth' AS model_name,
  'v2.0' AS model_version,
  prediction,
  p10,
  p90,
  LEAST(GREATEST(prediction / 2200, 0.03), 0.72) AS breach_probability,
  top_driver_1,
  top_driver_2,
  top_driver_3,
  CURRENT_TIMESTAMP() AS freshness,
  validation_status,
  'Backlog forecast is a planning estimate.' AS caveat
FROM CURATED.VW_MODEL_PREDICTION_AMBULATORY
WHERE metric_name = 'waitlist_total';

CREATE OR REPLACE VIEW MART.MART_V2_AMBULATORY_REFERRAL_TRIAGE AS
SELECT
  site_id,
  program,
  week_start_date AS week_start,
  new_referrals,
  urgent_referrals,
  triage_turnaround_median_days AS triage_median_days,
  referral_completeness_pct,
  duplicate_referral_count_synth AS duplicate_or_leakage_synth
FROM CURATED.VW_REFERRAL;

CREATE OR REPLACE VIEW MART.MART_V2_AMBULATORY_CLINIC_TEMPLATE AS
SELECT
  site_id,
  program,
  week_start_date AS week_start,
  slots_available,
  slots_booked,
  completed_visits,
  slots_available - completed_visits AS cancelled,
  no_show_rate,
  late_cancel_rate,
  new_visit_share,
  0.18 AS room_constraint,
  0.22 AS provider_constraint,
  0.14 AS nurse_allied_constraint
FROM CURATED.VW_CLINIC_SLOT;

CREATE OR REPLACE VIEW MART.MART_V2_AMBULATORY_FOLLOWUP AS
SELECT
  site_id,
  program,
  ROUND(waitlist_total * 0.06) AS overdue_followup,
  0.78 AS post_discharge_followup_on_time_pct,
  0.82 AS surveillance_interval_reliability
FROM MART.MART_AMBULATORY_ACCESS_MISSION_CONTROL;

CREATE OR REPLACE VIEW MART.MART_V2_AMBULATORY_DIAGNOSTIC_DEPENDENCY AS
SELECT
  site_id,
  program,
  ROUND(waitlist_total * 0.04) AS missing_prerequisite_count,
  14 AS median_dependency_delay_days,
  0.74 AS pre_visit_ready_pct,
  35 AS protected_slot_scenario_gain
FROM MART.MART_AMBULATORY_ACCESS_MISSION_CONTROL;

CREATE OR REPLACE VIEW MART.MART_V2_AMBULATORY_TRAVEL AS
SELECT
  site_id,
  program,
  0.28 AS virtual_suitable_share,
  0.24 AS regional_or_remote_share,
  1.38 AS travel_burden_index,
  1.08 AS weather_sensitivity
FROM MART.MART_AMBULATORY_ACCESS_MISSION_CONTROL;

CREATE OR REPLACE VIEW MART.MART_V2_DATA_QUALITY_STATUS AS
SELECT
  table_name,
  check_name,
  IFF(passed, 'pass', 'review') AS status,
  failed_rows,
  CURRENT_TIMESTAMP() AS last_checked,
  'synthetic prototype data quality' AS owner
FROM MART.MART_DATA_QUALITY_STATUS
UNION ALL
SELECT
  'GLOBAL_PRIVACY',
  'direct_identifier_scan',
  'pass',
  0,
  CURRENT_TIMESTAMP(),
  'synthetic prototype data quality';

CREATE OR REPLACE TABLE CONFIG.APP_METADATA (
  app_version STRING,
  synthetic_mode BOOLEAN,
  clinical_use_status STRING,
  last_config_update DATE
);

INSERT OVERWRITE INTO CONFIG.APP_METADATA
VALUES ('v2.0', TRUE, 'Not validated for clinical decision-making', CURRENT_DATE());
