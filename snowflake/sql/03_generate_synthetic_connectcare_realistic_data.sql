-- v3 synthetic operational seed rows. No real patient, staff, provider, or direct identifiers.
USE DATABASE PEDIATRIC_AHA_DEMO;

INSERT OVERWRITE INTO GOVERNANCE.V3_SOURCE_REGISTRY (
  source_id,
  curated_view,
  source_view_name,
  source_domain,
  grain,
  fields,
  field_types,
  cadence,
  classification,
  phi_sensitivity,
  dashboard_usage,
  validation_rules,
  future_mapping_placeholder
)
SELECT * FROM VALUES
  ('SRC_SYNTH_UNIT_CENSUS_HOURLY','CANONICAL.VW_SYNTH_UNIT_CENSUS_HOURLY','VW_SYNTH_UNIT_CENSUS_HOURLY','core encounter / movement','unit-hour','site_id, unit_id, hour_ts, census, physical_beds, staffed_beds, effective_beds','synthetic ids, timestamps, numeric measures','hourly','direct_operational_signal','medium aggregate','system posture, inpatient pressure','freshness, row count, timestamp logic, referential integrity, metric approval, small-cell suppression','CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_001'),
  ('SRC_SYNTH_ED_VISITS','CANONICAL.VW_SYNTH_ED_VISITS','VW_SYNTH_ED_VISITS','core encounter / movement','ED visit aggregate','visit_id, site_id, arrival_ts, decision_to_admit_ts, acuity_band','synthetic ids, timestamps, categorical fields','15 minutes','direct_operational_signal','medium aggregate','boarding forecast','freshness, row count, timestamp logic, referential integrity, metric approval, small-cell suppression','CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_002'),
  ('SRC_SYNTH_REFERRALS','CANONICAL.VW_SYNTH_REFERRALS','VW_SYNTH_REFERRALS','ambulatory','referral aggregate','referral_id, site_id, program, priority, received_ts, triage_status','synthetic ids, timestamps, categorical fields','daily','direct_operational_signal','high aggregate only','ambulatory demand','freshness, row count, timestamp logic, referential integrity, metric approval, small-cell suppression','CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_003'),
  ('SRC_MODEL_PREDICTIONS','MODEL.VW_MODEL_PREDICTIONS','VW_MODEL_PREDICTIONS','model / governance / learning','asset-output','asset_id, output_ts, site_id, score, threshold, explanation_json','synthetic ids, timestamps, numeric measures, JSON','asset cadence','modelled_predictive_ai_asset','aggregate/model output','predictive assets and warnings','model card, threshold review, drift, calibration, rollback','CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_004'),
  ('SRC_LEARNING_SYSTEM_EVENTS','APP.VW_LEARNING_SYSTEM_EVENTS','VW_LEARNING_SYSTEM_EVENTS','model / governance / learning','learning event','event_id, event_type, app_area, related_metric_id, related_model_id, related_panel_id, related_scenario_id, payload_json','synthetic ids, timestamps, JSON','event-driven','derived_operational_intelligence','metadata only','learning-system memory','auditability, write privilege, retention policy','CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_005')
  AS t(source_id, curated_view, source_view_name, source_domain, grain, fields, field_types, cadence, classification, phi_sensitivity, dashboard_usage, validation_rules, future_mapping_placeholder);

INSERT OVERWRITE INTO RAW_SYNTH.V3_OPERATIONAL_SIGNAL
SELECT * FROM VALUES
  ('SIG-001','SRC_SYNTH_UNIT_CENSUS_HOURLY','2026-06-11 08:30:00'::TIMESTAMP_NTZ,'SITE_STOLLERY_INSPIRED','Respiratory','occupancy_pct',0.99,PARSE_JSON('{"classification":"derived","readiness":"review"}'),TRUE),
  ('SIG-002','SRC_SYNTH_ED_VISITS','2026-06-11 08:30:00'::TIMESTAMP_NTZ,'SITE_STOLLERY_INSPIRED','ED','boarder_count',16,PARSE_JSON('{"classification":"direct","readiness":"ready"}'),TRUE),
  ('SIG-003','SRC_SYNTH_REFERRALS','2026-06-11 08:30:00'::TIMESTAMP_NTZ,'SITE_PROV_NETWORK','Neurology','urgent_breach_risk',0.41,PARSE_JSON('{"classification":"derived","readiness":"review"}'),TRUE),
  ('SIG-004','SRC_MODEL_PREDICTIONS','2026-06-11 08:30:00'::TIMESTAMP_NTZ,'SITE_PROV_NETWORK','PICU','score',0.76,PARSE_JSON('{"asset_id":"PICU_NICU_PRESSURE","classification":"modelled"}'),TRUE)
  AS t(signal_id, source_id, event_ts, site_id, unit_or_program, metric_name, metric_value, payload_json, synthetic_demo_flag);
