-- v3 operational marts for showcase and Streamlit surfaces.
USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE VIEW MART.V3_SYSTEM_POSTURE AS
SELECT
  site_id,
  MAX(event_ts) AS last_event_ts,
  SUM(IFF(metric_name = 'boarder_count', metric_value, 0)) AS ed_boarders,
  AVG(IFF(metric_name = 'occupancy_pct', metric_value, NULL)) AS occupancy_pct,
  AVG(IFF(metric_name = 'urgent_breach_risk', metric_value, NULL)) AS urgent_breach_risk,
  TRUE AS synthetic_demo_flag
FROM RAW_SYNTH.V3_OPERATIONAL_SIGNAL
GROUP BY site_id;

CREATE OR REPLACE VIEW MART.V3_INPATIENT_UNIT_PRESSURE AS
SELECT site_id, unit_or_program AS unit_name, metric_name, metric_value, payload_json, synthetic_demo_flag
FROM RAW_SYNTH.V3_OPERATIONAL_SIGNAL
WHERE source_id IN ('SRC_UNIT_CENSUS', 'SRC_ED_BOARDING');

CREATE OR REPLACE VIEW MART.V3_AMBULATORY_ACCESS AS
SELECT site_id, unit_or_program AS program, metric_name, metric_value, payload_json, synthetic_demo_flag
FROM RAW_SYNTH.V3_OPERATIONAL_SIGNAL
WHERE source_id = 'SRC_REFERRAL';
