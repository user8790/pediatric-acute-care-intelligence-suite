-- 08_create_quality_checks.sql
-- Data quality views for app and analyst review.

USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE VIEW CONFIG.VW_QUALITY_CHECK_OCCUPANCY_BOUNDS AS
SELECT
  census_hour_id,
  site_id,
  unit_id,
  ts_hour,
  occupancy_pct,
  occupancy_pct BETWEEN 0 AND 1.5 AS passed
FROM CURATED.VW_BED_CENSUS_HOURLY;

CREATE OR REPLACE VIEW CONFIG.VW_QUALITY_CHECK_WAITLIST AS
SELECT
  waitlist_snapshot_id,
  site_id,
  program,
  week_start_date,
  waitlist_total,
  waitlist_total >= 0 AS passed
FROM CURATED.VW_WAITLIST_SNAPSHOT;

CREATE OR REPLACE VIEW CONFIG.VW_SOURCE_FRESHNESS AS
SELECT 'FCT_BED_CENSUS_HOURLY' AS table_name, MAX(ts_hour) AS latest_record_ts FROM CURATED.VW_BED_CENSUS_HOURLY
UNION ALL
SELECT 'FCT_WAITLIST_SNAPSHOT', MAX(week_start_date)::TIMESTAMP_NTZ FROM CURATED.VW_WAITLIST_SNAPSHOT;

