-- 03_generate_synthetic_data.sql
-- Creates compact synthetic data directly in Snowflake SQL for Snowsight-only setup.

USE DATABASE PEDIATRIC_AHA_DEMO;

TRUNCATE TABLE RAW_SYNTH.DIM_SITE;
INSERT INTO RAW_SYNTH.DIM_SITE (site_id, site_name, zone_name, latitude, longitude)
VALUES
  ('SITE_STOLLERY_INSPIRED', 'Stollery-inspired pediatric site', 'Edmonton zone proxy', 53.52, -113.52),
  ('SITE_ACH_INSPIRED', 'Alberta Children''s-inspired pediatric site', 'Calgary zone proxy', 51.06, -114.13),
  ('SITE_PROV_NETWORK', 'Provincial pediatric network proxy', 'Provincial network', 52.50, -113.50);

TRUNCATE TABLE RAW_SYNTH.DIM_UNIT;
INSERT INTO RAW_SYNTH.DIM_UNIT (unit_id, site_id, unit_name, service_line, physical_beds, baseline_occupancy, is_high_resource)
SELECT site_id || '_GEN', site_id, 'General pediatrics', 'general_pediatrics', 42, 0.84, FALSE FROM RAW_SYNTH.DIM_SITE
UNION ALL SELECT site_id || '_RESP', site_id, 'Respiratory cohort', 'respiratory', 28, 0.88, FALSE FROM RAW_SYNTH.DIM_SITE
UNION ALL SELECT site_id || '_SURG', site_id, 'Surgery', 'surgery', 34, 0.82, FALSE FROM RAW_SYNTH.DIM_SITE
UNION ALL SELECT site_id || '_PICU', site_id, 'PICU', 'PICU', 20, 0.78, TRUE FROM RAW_SYNTH.DIM_SITE
UNION ALL SELECT site_id || '_NICU', site_id, 'NICU', 'NICU', 36, 0.80, TRUE FROM RAW_SYNTH.DIM_SITE
UNION ALL SELECT site_id || '_MH', site_id, 'Mental health', 'mental_health', 18, 0.86, FALSE FROM RAW_SYNTH.DIM_SITE;

TRUNCATE TABLE RAW_SYNTH.FCT_BED_CENSUS_HOURLY;
INSERT INTO RAW_SYNTH.FCT_BED_CENSUS_HOURLY (
  census_hour_id, site_id, unit_id, service_line, ts_hour, census, physical_beds, staffed_beds,
  effective_beds, occupancy_pct, respiratory_multiplier, ed_boarders, predicted_discharges,
  discharge_confidence, staffing_gap_pct
)
SELECT
  UUID_STRING(),
  site_id,
  unit_id,
  service_line,
  ts_hour,
  census,
  physical_beds,
  staffed_beds,
  effective_beds,
  LEAST(1.25, census / NULLIF(effective_beds, 0)) AS occupancy_pct,
  respiratory_multiplier,
  GREATEST(0, ROUND((LEAST(1.25, census / NULLIF(effective_beds, 0)) - 0.92) * 18, 0)) AS ed_boarders,
  GREATEST(0, ROUND(census * 0.04, 0)) AS predicted_discharges,
  LEAST(0.95, GREATEST(0.35, 0.78 - GREATEST(0, LEAST(1.25, census / NULLIF(effective_beds, 0)) - 0.9) * 0.25)) AS discharge_confidence,
  staffing_gap_pct
FROM (
  SELECT
    u.site_id,
    u.unit_id,
    u.service_line,
    DATEADD(hour, seq.seq4, '2026-01-01'::TIMESTAMP_NTZ) AS ts_hour,
    GREATEST(0, ROUND(u.physical_beds * u.baseline_occupancy * (0.92 + UNIFORM(0, 18, RANDOM(42)) / 100), 0)) AS census,
    u.physical_beds,
    GREATEST(1, u.physical_beds - UNIFORM(0, 3, RANDOM(99))) AS staffed_beds,
    GREATEST(1, u.physical_beds - UNIFORM(1, 5, RANDOM(123))) AS effective_beds,
    CASE WHEN MONTH(DATEADD(hour, seq.seq4, '2026-01-01'::TIMESTAMP_NTZ)) IN (1, 2, 11, 12) THEN 1.35 ELSE 0.95 END AS respiratory_multiplier,
    UNIFORM(2, 11, RANDOM(456)) / 100 AS staffing_gap_pct
  FROM RAW_SYNTH.DIM_UNIT u,
  LATERAL (SELECT SEQ4() AS seq4 FROM TABLE(GENERATOR(ROWCOUNT => 168))) seq
) src;

TRUNCATE TABLE RAW_SYNTH.FCT_OCCUPANCY_SNAPSHOT;
INSERT INTO RAW_SYNTH.FCT_OCCUPANCY_SNAPSHOT
SELECT
  UUID_STRING(),
  site_id,
  MAX(ts_hour) AS snapshot_ts,
  SUM(census),
  SUM(physical_beds),
  SUM(staffed_beds),
  SUM(effective_beds),
  SUM(census) / NULLIF(SUM(effective_beds), 0),
  SUM(ed_boarders),
  SUM(predicted_discharges),
  AVG(discharge_confidence),
  AVG(staffing_gap_pct),
  TRUE
FROM RAW_SYNTH.FCT_BED_CENSUS_HOURLY
WHERE ts_hour = (SELECT MAX(ts_hour) FROM RAW_SYNTH.FCT_BED_CENSUS_HOURLY)
GROUP BY site_id;

TRUNCATE TABLE RAW_SYNTH.FCT_WAITLIST_SNAPSHOT;
INSERT INTO RAW_SYNTH.FCT_WAITLIST_SNAPSHOT
SELECT
  UUID_STRING(),
  s.site_id,
  p.program,
  DATEADD(week, seq.seq4, '2026-01-05'::DATE),
  UNIFORM(90, 420, RANDOM(222)),
  UNIFORM(25, 210, RANDOM(223)),
  UNIFORM(18, 76, RANDOM(224)),
  UNIFORM(40, 160, RANDOM(225)),
  UNIFORM(12, 58, RANDOM(226)),
  UNIFORM(5, 31, RANDOM(227)) / 100,
  TRUE
FROM RAW_SYNTH.DIM_SITE s,
LATERAL (
  SELECT COLUMN1 AS program FROM VALUES
    ('respiratory'), ('cardiology'), ('neurology'), ('surgery_followup'),
    ('oncology_survivorship'), ('complex_care'), ('mental_health'), ('diagnostic_procedures')
) p,
LATERAL (SELECT SEQ4() AS seq4 FROM TABLE(GENERATOR(ROWCOUNT => 12))) seq;

TRUNCATE TABLE RAW_SYNTH.FCT_CLINIC_SLOT;
INSERT INTO RAW_SYNTH.FCT_CLINIC_SLOT
SELECT
  UUID_STRING(),
  site_id,
  program,
  week_start_date,
  slots_available,
  slots_available + UNIFORM(0, 4, RANDOM(301)),
  GREATEST(0, slots_available - UNIFORM(0, 8, RANDOM(302))),
  UNIFORM(4, 15, RANDOM(303)) / 100,
  UNIFORM(2, 7, RANDOM(304)) / 100,
  UNIFORM(5, 35, RANDOM(305)) / 100,
  UNIFORM(34, 58, RANDOM(306)) / 100,
  TRUE
FROM (
  SELECT site_id, program, week_start_date, UNIFORM(18, 48, RANDOM(300)) AS slots_available
  FROM RAW_SYNTH.FCT_WAITLIST_SNAPSHOT
) src;

TRUNCATE TABLE RAW_SYNTH.FCT_REFERRAL;
INSERT INTO RAW_SYNTH.FCT_REFERRAL
SELECT
  UUID_STRING(), site_id, program, week_start_date,
  UNIFORM(12, 38, RANDOM(401)),
  UNIFORM(1, 10, RANDOM(402)),
  UNIFORM(1, 7, RANDOM(403)),
  UNIFORM(82, 98, RANDOM(404)) / 100,
  UNIFORM(0, 3, RANDOM(405)),
  TRUE
FROM RAW_SYNTH.FCT_WAITLIST_SNAPSHOT;

TRUNCATE TABLE RAW_SYNTH.FCT_DISCHARGE_BARRIER;
INSERT INTO RAW_SYNTH.FCT_DISCHARGE_BARRIER
SELECT UUID_STRING(), s.site_id, b.barrier_type, UNIFORM(2, 22, RANDOM(510)), UNIFORM(4, 42, RANDOM(511)), TRUE
FROM RAW_SYNTH.DIM_SITE s,
LATERAL (SELECT COLUMN1 AS barrier_type FROM VALUES ('meds'), ('transport'), ('imaging'), ('consult'), ('family_readiness'), ('home_supports'), ('equipment')) b;

TRUNCATE TABLE RAW_SYNTH.FCT_MODEL_PREDICTION_INPATIENT;
INSERT INTO RAW_SYNTH.FCT_MODEL_PREDICTION_INPATIENT
SELECT
  UUID_STRING(), site_id, 'MODEL_INPT_OCC', horizon, 'occupancy_pct',
  LEAST(1.2, occupancy_pct + horizon * 0.0015),
  GREATEST(0, occupancy_pct + horizon * 0.0015 - 0.08),
  LEAST(1.35, occupancy_pct + horizon * 0.0015 + 0.10),
  'respiratory activity', 'staffing gap', 'discharge confidence',
  'synthetic demo only',
  TRUE
FROM RAW_SYNTH.FCT_OCCUPANCY_SNAPSHOT,
LATERAL (SELECT COLUMN1 AS horizon FROM VALUES (6), (12), (24), (48), (72));

TRUNCATE TABLE RAW_SYNTH.FCT_SIMULATION_RESULT_INPATIENT;
INSERT INTO RAW_SYNTH.FCT_SIMULATION_RESULT_INPATIENT
VALUES
  ('SIM_INPT_001', 'Current state baseline', 44, 18, 71, 1.02, TRUE),
  ('SIM_INPT_002', 'Respiratory surge', 83, 52, 124, 1.11, TRUE),
  ('SIM_INPT_003', 'Open surge beds', 19, 4, 34, 0.94, TRUE),
  ('SIM_INPT_004', 'Increase morning discharges', 27, 8, 48, 0.97, TRUE);

TRUNCATE TABLE RAW_SYNTH.FCT_SIMULATION_RESULT_AMBULATORY;
INSERT INTO RAW_SYNTH.FCT_SIMULATION_RESULT_AMBULATORY
VALUES
  ('SIM_AMB_001', 'Current access plan', 1010, 999, 0.96, 0.28, TRUE),
  ('SIM_AMB_002', 'Add clinics/sessions', 640, 999, 0.90, 0.18, TRUE),
  ('SIM_AMB_003', 'Guarded overbooking', 720, 999, 0.98, 0.21, TRUE),
  ('SIM_AMB_004', 'Reduce triage turnaround', 760, 999, 0.92, 0.19, TRUE);
