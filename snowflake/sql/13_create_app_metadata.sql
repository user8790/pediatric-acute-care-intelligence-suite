-- v3 app metadata.
USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE TABLE APP.V3_APP_METADATA (
  metadata_key STRING,
  metadata_value STRING,
  updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT OVERWRITE INTO APP.V3_APP_METADATA
SELECT * FROM VALUES
  ('app_version','v3.0','2026-06-11 08:30:00'::TIMESTAMP_NTZ),
  ('product_name','Provincial Pediatric Acute Care Intelligence Operating Layer','2026-06-11 08:30:00'::TIMESTAMP_NTZ),
  ('mode','Synthetic demonstration data','2026-06-11 08:30:00'::TIMESTAMP_NTZ),
  ('clinical_use','Not validated for clinical decision-making','2026-06-11 08:30:00'::TIMESTAMP_NTZ),
  ('source_boundary','Future real data maps through curated governed Snowflake views only.','2026-06-11 08:30:00'::TIMESTAMP_NTZ)
  AS t(metadata_key, metadata_value, updated_at);
