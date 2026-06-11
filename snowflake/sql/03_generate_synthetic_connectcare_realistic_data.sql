-- v3 synthetic operational seed rows. No real patient, staff, provider, or direct identifiers.
USE DATABASE PEDIATRIC_AHA_DEMO;

INSERT OVERWRITE INTO GOVERNANCE.V3_SOURCE_REGISTRY
SELECT * FROM VALUES
  ('SRC_UNIT_CENSUS','CANONICAL.VW_SYNTH_UNIT_CENSUS_HOURLY','unit-hour','site_id, unit_id, census, effective_beds','synthetic ids, timestamps, numeric measures','hourly','direct_operational_signal','medium aggregate','system posture, inpatient pressure','freshness, row count, timestamp logic, referential integrity, metric approval, small-cell suppression','CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_01'),
  ('SRC_ED_BOARDING','CANONICAL.VW_SYNTH_ED_BOARDING','ED boarding snapshot','site_id, unit_target, boarder_count','synthetic ids, timestamps, numeric measures','15 minutes','direct_operational_signal','medium aggregate','boarding forecast','freshness, row count, timestamp logic, referential integrity, metric approval, small-cell suppression','CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_02'),
  ('SRC_REFERRAL','CANONICAL.VW_SYNTH_REFERRAL','referral aggregate','site_id, program, priority, received_ts, status','synthetic ids, timestamps, categorical fields','daily','direct_operational_signal','high aggregate only','ambulatory demand','freshness, row count, timestamp logic, referential integrity, metric approval, small-cell suppression','CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_03'),
  ('SRC_MODEL_OUTPUT','MODEL.VW_SYNTH_MODEL_OUTPUT','asset-output','asset_id, output_ts, site_id, score, threshold','synthetic ids, timestamps, numeric measures, JSON','asset cadence','modelled_predictive_ai_asset','aggregate/model output','predictive assets and warnings','model card, threshold review, drift, calibration, rollback','CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_04'),
  ('SRC_LEARNING_MEMORY','APP.VW_SYNTH_LEARNING_SYSTEM_EVENT','learning event','event_id, event_type, app_area, related_ids, payload_json','synthetic ids, timestamps, JSON','event-driven','derived_operational_intelligence','metadata only','learning-system memory','auditability, write privilege, retention policy','CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_05')
  AS t(source_id, curated_view, grain, fields, field_types, cadence, classification, phi_sensitivity, dashboard_usage, validation_rules, future_mapping_placeholder);

INSERT OVERWRITE INTO RAW_SYNTH.V3_OPERATIONAL_SIGNAL
SELECT * FROM VALUES
  ('SIG-001','SRC_UNIT_CENSUS','2026-06-11 08:30:00'::TIMESTAMP_NTZ,'SITE_STOLLERY_INSPIRED','Respiratory','occupancy_pct',0.99,PARSE_JSON('{"classification":"derived","readiness":"review"}'),TRUE),
  ('SIG-002','SRC_ED_BOARDING','2026-06-11 08:30:00'::TIMESTAMP_NTZ,'SITE_STOLLERY_INSPIRED','ED','boarder_count',16,PARSE_JSON('{"classification":"direct","readiness":"ready"}'),TRUE),
  ('SIG-003','SRC_REFERRAL','2026-06-11 08:30:00'::TIMESTAMP_NTZ,'SITE_PROV_NETWORK','Neurology','urgent_breach_risk',0.41,PARSE_JSON('{"classification":"derived","readiness":"review"}'),TRUE),
  ('SIG-004','SRC_MODEL_OUTPUT','2026-06-11 08:30:00'::TIMESTAMP_NTZ,'SITE_PROV_NETWORK','PICU','score',0.76,PARSE_JSON('{"asset_id":"PICU_NICU_PRESSURE","classification":"modelled"}'),TRUE)
  AS t(signal_id, source_id, event_ts, site_id, unit_or_program, metric_name, metric_value, payload_json, synthetic_demo_flag);
