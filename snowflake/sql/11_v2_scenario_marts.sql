-- 11_v2_scenario_marts.sql
-- v2 coefficient registry, scenario grids, and scenario run log.
-- Synthetic demonstration data only. Not validated for clinical decision-making.

USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE TABLE MODEL.DIM_V2_COEFFICIENT_REGISTRY (
  coefficient_name STRING,
  symbol STRING,
  definition STRING,
  default_value FLOAT,
  source STRING,
  caveat STRING
);

INSERT OVERWRITE INTO MODEL.DIM_V2_COEFFICIENT_REGISTRY VALUES
  ('arrival_rate_lambda', 'lambda', 'Arrivals per hour/day/service/site.', 4.2, 'synthetic v2 configuration', 'Demonstration coefficient; calibrate locally before operational use.'),
  ('service_rate_mu', 'mu', 'Completions per resource per time unit.', 0.26, 'synthetic v2 configuration', 'Demonstration coefficient; calibrate locally before operational use.'),
  ('servers_resources', 'c', 'Beds, rooms, providers, or constrained resources.', 12, 'synthetic v2 configuration', 'Resource meaning depends on workflow.'),
  ('utilization', 'rho', 'lambda / (c * mu).', 0.89744, 'synthetic v2 configuration', 'Queueing approximation only.'),
  ('interarrival_variability', 'Ca2', 'Squared coefficient of variation for interarrival times.', 1.15, 'synthetic v2 configuration', 'Estimate from synthetic arrivals.'),
  ('service_variability', 'Cs2', 'Squared coefficient of variation for service times.', 1.32, 'synthetic v2 configuration', 'Estimate from synthetic LOS/service times.'),
  ('erlang_c_wait_probability', 'Erlang C', 'M/M/c wait probability.', 0.157, 'synthetic v2 configuration', 'Approximation for planning.'),
  ('erlang_b_blocking_probability', 'Erlang B', 'Loss-system blocking probability.', 0.063, 'synthetic v2 configuration', 'Approximation for planning.'),
  ('kingman_wait_hours', 'Kingman', 'G/G/1 wait approximation.', 1.84, 'synthetic v2 configuration', 'Approximation for planning.'),
  ('allen_cunneen_wait_hours', 'Allen-Cunneen', 'G/G/c wait approximation.', 0.42, 'synthetic v2 configuration', 'Approximation for planning.'),
  ('little_law', 'L=lambda W', 'System size relationship.', 9.7, 'synthetic v2 configuration', 'Relationship, not a causal estimate.'),
  ('discharge_completion_rate', 'delta_discharge', 'Hourly discharge completion coefficient.', 0.055, 'synthetic v2 configuration', 'Calibrate by local discharge milestones.'),
  ('bed_turnaround_minutes', 'turnaround', 'EVS/bed clean turnaround.', 72, 'synthetic v2 configuration', 'Calibrate by local bed-management timestamps.'),
  ('effective_staffed_bed_coefficient', 'effective_beds', 'Capacity after staffing constraints.', 0.91, 'synthetic v2 configuration', 'Staffed capacity is context-specific.'),
  ('isolation_constraint_factor', 'isolation', 'Respiratory/isolation bed constraint.', 0.96, 'synthetic v2 configuration', 'Use as aggregate proxy only.'),
  ('step_down_constraint_factor', 'stepdown', 'PICU/NICU step-down constraint.', 0.93, 'synthetic v2 configuration', 'Use as aggregate proxy only.'),
  ('respiratory_surge_multiplier', 'resp_surge', 'Respiratory activity demand multiplier.', 1.35, 'synthetic v2 configuration', 'Public context proxy only.'),
  ('weather_smoke_multiplier', 'weather_smoke', 'Weather/AQHI/smoke demand multiplier.', 1.07, 'synthetic v2 configuration', 'Ecological context only.'),
  ('school_holiday_multiplier', 'school_holiday', 'School and holiday demand multiplier.', 1.05, 'synthetic v2 configuration', 'Calendar context only.'),
  ('no_show_probability', 'p_no_show', 'Appointment no-show probability.', 0.088, 'synthetic v2 configuration', 'Requires local validation and fairness monitoring.'),
  ('overbooking_coefficient', 'overbook', 'Guarded overbooking coefficient.', 0.09, 'synthetic v2 configuration', 'Use with safety guardrails.'),
  ('diagnostic_dependency_delay', 'dx_delay', 'Median diagnostic dependency delay in days.', 14, 'synthetic v2 configuration', 'Local diagnostic constraints vary.'),
  ('protected_slot_coefficient', 'urgent_slots', 'Urgent-slot protection coefficient.', 0.16, 'synthetic v2 configuration', 'Monitor access trade-offs.'),
  ('virtual_care_conversion', 'virtual', 'Share of visits suitable for virtual conversion.', 0.27, 'synthetic v2 configuration', 'Requires clinical and equity review.');

CREATE OR REPLACE TABLE CONFIG.V2_SCENARIO_PARAMETERS (
  scenario_id STRING,
  scenario_name STRING,
  product_area STRING,
  lever_name STRING,
  default_value FLOAT,
  lower_bound FLOAT,
  upper_bound FLOAT,
  interpretation STRING,
  caveat STRING
);

INSERT OVERWRITE INTO CONFIG.V2_SCENARIO_PARAMETERS VALUES
  ('V2_INPT_BASE', 'Current state baseline', 'inpatient', 'baseline', 1, 1, 1, 'Comparator for inpatient scenario grid.', 'Synthetic planning comparator.'),
  ('V2_INPT_SURGE', 'Open staffed surge beds', 'inpatient', 'additional_effective_beds', 8, 0, 30, 'Adds effective beds when staffing supports them.', 'Requires staffing and safety review.'),
  ('V2_INPT_DISCHARGE', 'Increase morning discharges', 'inpatient', 'discharge_completion_rate', 0.07, 0.03, 0.12, 'Improves discharge reliability by time band.', 'Does not replace local discharge planning.'),
  ('V2_INPT_STEPOWN', 'Protect PICU/NICU step-down capacity', 'inpatient', 'step_down_constraint_factor', 0.98, 0.85, 1.0, 'Protects high-resource flow.', 'Requires clinical review.'),
  ('V2_AMB_BASE', 'Current access plan', 'ambulatory', 'baseline', 1, 1, 1, 'Comparator for ambulatory scenario grid.', 'Synthetic planning comparator.'),
  ('V2_AMB_SESSIONS', 'Add clinic sessions', 'ambulatory', 'added_sessions', 5, 0, 20, 'Adds weekly clinic capacity.', 'Requires provider/room constraints review.'),
  ('V2_AMB_OVERBOOK', 'Guarded overbooking', 'ambulatory', 'overbooking_coefficient', 0.09, 0, 0.16, 'Uses no-show risk with overflow guardrails.', 'Requires fairness and safety guardrails.'),
  ('V2_AMB_DIAGNOSTIC', 'Diagnostic readiness improvement', 'ambulatory', 'diagnostic_dependency_delay', 9, 3, 30, 'Reduces pre-visit dependency delays.', 'Requires diagnostic partner review.'),
  ('V2_AMB_OUTREACH', 'Outreach/regional clinic', 'ambulatory', 'virtual_care_conversion', 0.32, 0, 0.55, 'Improves regional access options.', 'Requires family burden and equity review.');

CREATE OR REPLACE TABLE MART.MART_V2_INPATIENT_SCENARIO (
  scenario_name STRING,
  impact_score NUMBER,
  effort_score NUMBER,
  operational_risk_score NUMBER,
  fairness_proxy_delta FLOAT,
  boarder_hours_mean NUMBER,
  boarder_hours_p10 NUMBER,
  boarder_hours_p90 NUMBER,
  bed_shortage_hours NUMBER,
  elective_cancellation_risk FLOAT,
  discharge_reliability FLOAT,
  picu_nicu_pressure FLOAT,
  caveat STRING
);

INSERT OVERWRITE INTO MART.MART_V2_INPATIENT_SCENARIO VALUES
  ('Current state baseline', 16, 1, 1, 0.00, 86, 53, 114, 22, 0.17, 0.75, 0.95, 'Synthetic scenario grid.'),
  ('Open staffed surge beds', 46, 3, 2, 0.02, 54, 34, 71, 14, 0.11, 0.81, 0.86, 'Requires staffed capacity.'),
  ('Increase morning discharges', 39, 2, 1, 0.03, 61, 38, 81, 15, 0.12, 0.80, 0.88, 'Requires local discharge workflow review.'),
  ('Add evening/weekend discharge support', 51, 3, 2, 0.04, 49, 30, 65, 12, 0.10, 0.82, 0.85, 'Requires staffing and partner review.'),
  ('Protect PICU/NICU step-down capacity', 56, 4, 2, 0.01, 44, 27, 58, 10, 0.09, 0.83, 0.84, 'Requires clinical governance.'),
  ('Reduce bed turnaround by 20 minutes', 34, 2, 1, 0.00, 66, 41, 87, 16, 0.13, 0.79, 0.90, 'Requires EVS/transport feasibility.'),
  ('Smooth elective OR load', 41, 4, 3, 0.02, 58, 36, 77, 14, 0.08, 0.80, 0.88, 'Requires surgical access trade-off review.'),
  ('Inter-site transfer support', 49, 5, 3, 0.05, 51, 32, 67, 13, 0.10, 0.82, 0.86, 'Requires provincial coordination.');

CREATE OR REPLACE TABLE MART.MART_V2_AMBULATORY_SCENARIO (
  scenario_name STRING,
  impact_score NUMBER,
  effort_score NUMBER,
  operational_risk_score NUMBER,
  fairness_proxy_delta FLOAT,
  final_backlog NUMBER,
  backlog_p10 NUMBER,
  backlog_p90 NUMBER,
  clearance_weeks NUMBER,
  urgent_breach_risk FLOAT,
  slot_utilization FLOAT,
  no_show_adjusted_capacity NUMBER,
  caveat STRING
);

INSERT OVERWRITE INTO MART.MART_V2_AMBULATORY_SCENARIO VALUES
  ('Current access plan', 29, 1, 1, 0.00, 1260, 982, 1486, 18, 0.30, 0.81, 420, 'Synthetic scenario grid.'),
  ('Add clinic sessions', 53, 3, 2, 0.02, 850, 663, 1003, 12, 0.20, 0.89, 488, 'Requires provider/room review.'),
  ('Rebalance new/follow-up slots', 48, 2, 2, 0.01, 940, 733, 1109, 13, 0.22, 0.87, 473, 'Monitor follow-up reliability.'),
  ('Guarded overbooking', 50, 3, 3, -0.01, 910, 710, 1074, 13, 0.22, 0.88, 478, 'Requires guardrails and fairness monitoring.'),
  ('Reminder/navigation support', 45, 2, 1, 0.05, 980, 764, 1156, 14, 0.23, 0.86, 466, 'Requires family-centred implementation.'),
  ('Protected urgent slots', 41, 3, 2, 0.04, 1060, 827, 1251, 15, 0.25, 0.85, 453, 'Monitor routine wait trade-offs.'),
  ('Diagnostic readiness improvement', 57, 4, 2, 0.03, 790, 616, 932, 11, 0.19, 0.90, 498, 'Requires diagnostic partner review.'),
  ('Outreach/regional clinic', 52, 5, 3, 0.08, 870, 679, 1027, 12, 0.21, 0.88, 485, 'Requires outreach feasibility review.');

CREATE OR REPLACE TABLE APP.SCENARIO_RUN_LOG (
  scenario_name STRING,
  app STRING,
  site STRING,
  program STRING,
  persona STRING,
  horizon STRING,
  boarder_hours_mean FLOAT,
  final_backlog FLOAT,
  demand_stress FLOAT,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
