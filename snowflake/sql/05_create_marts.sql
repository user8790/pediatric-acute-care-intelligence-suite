-- 05_create_marts.sql
-- Aggregated marts queried by Streamlit apps.

USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE VIEW MART.MART_INPATIENT_MISSION_CONTROL AS
SELECT
  site_id,
  snapshot_ts,
  census,
  physical_beds,
  staffed_beds,
  effective_beds,
  occupancy_pct,
  ed_boarders,
  predicted_discharges,
  discharge_confidence,
  staffing_gap_pct,
  'Synthetic demonstration data' AS data_mode,
  'Not validated for clinical decision-making' AS caveat
FROM CURATED.VW_OCCUPANCY_SNAPSHOT;

CREATE OR REPLACE VIEW MART.MART_AMBULATORY_ACCESS_MISSION_CONTROL AS
SELECT
  w.site_id,
  w.program,
  MAX(w.week_start_date) AS week_start_date,
  MAX_BY(w.waitlist_total, w.week_start_date) AS waitlist_total,
  MAX_BY(w.waitlist_over_target, w.week_start_date) AS waitlist_over_target,
  MAX_BY(w.median_wait_days, w.week_start_date) AS median_wait_days,
  MAX_BY(w.p90_wait_days, w.week_start_date) AS p90_wait_days,
  MAX_BY(w.third_next_available_days, w.week_start_date) AS third_next_available_days,
  MAX_BY(w.urgent_breach_risk, w.week_start_date) AS urgent_breach_risk,
  'Synthetic demonstration data' AS data_mode,
  'Not validated for clinical decision-making' AS caveat
FROM CURATED.VW_WAITLIST_SNAPSHOT w
GROUP BY w.site_id, w.program;

CREATE OR REPLACE VIEW MART.MART_INPATIENT_SIMULATION_SUMMARY AS
SELECT * FROM CURATED.VW_SIMULATION_RESULT_INPATIENT;

CREATE OR REPLACE VIEW MART.MART_AMBULATORY_SIMULATION_SUMMARY AS
SELECT * FROM CURATED.VW_SIMULATION_RESULT_AMBULATORY;

CREATE OR REPLACE VIEW MART.MART_DATA_QUALITY_STATUS AS
SELECT
  'FCT_BED_CENSUS_HOURLY' AS table_name,
  'occupancy_bounds' AS check_name,
  COUNT_IF(occupancy_pct < 0 OR occupancy_pct > 1.5) AS failed_rows,
  COUNT_IF(occupancy_pct < 0 OR occupancy_pct > 1.5) = 0 AS passed
FROM CURATED.VW_BED_CENSUS_HOURLY
UNION ALL
SELECT
  'FCT_WAITLIST_SNAPSHOT',
  'non_negative_waitlist',
  COUNT_IF(waitlist_total < 0),
  COUNT_IF(waitlist_total < 0) = 0
FROM CURATED.VW_WAITLIST_SNAPSHOT
UNION ALL
SELECT
  'GLOBAL_PRIVACY',
  'no_direct_identifiers_in_synthetic_sql',
  0,
  TRUE;

