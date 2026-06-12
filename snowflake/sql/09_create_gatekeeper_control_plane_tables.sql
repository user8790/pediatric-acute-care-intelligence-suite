-- v3 AHA Gatekeeper control-plane tables.
USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE OR REPLACE TABLE GOVERNANCE.V3_PANEL_LINEAGE (
  panel_id STRING,
  title STRING,
  app_area STRING,
  classification STRING,
  source_view_ids STRING,
  metric_ids STRING,
  model_ids STRING,
  freshness STRING,
  readiness_status STRING,
  confidence STRING,
  caveat STRING,
  lineage_summary STRING
);

CREATE OR REPLACE TABLE GOVERNANCE.V3_GATEKEEPER_ISSUE (
  issue_id STRING,
  severity STRING,
  related_id STRING,
  status STRING,
  note STRING,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  synthetic_demo_flag BOOLEAN DEFAULT TRUE
);

CREATE OR REPLACE TABLE GOVERNANCE.V3_GATEKEEPER_DECISION (
  decision_id STRING,
  related_id STRING,
  decision STRING,
  reviewer_role STRING,
  created_at TIMESTAMP_NTZ,
  payload_json VARIANT,
  synthetic_demo_flag BOOLEAN
);

CREATE OR REPLACE TABLE GOVERNANCE.V3_GOVERNANCE_APPROVAL (
  decision_id STRING,
  related_id STRING,
  decision STRING,
  reviewer_role STRING,
  created_at TIMESTAMP_NTZ,
  payload_json VARIANT,
  synthetic_demo_flag BOOLEAN
);

CREATE OR REPLACE TABLE GOVERNANCE.V3_RELEASE_ROLLBACK (
  release_id STRING,
  asset_id STRING,
  panel_id STRING,
  release_status STRING,
  version STRING,
  canary_scope STRING,
  rollback_trigger STRING,
  rollback_action STRING,
  owner STRING,
  approved_at TIMESTAMP_NTZ,
  caveat STRING,
  synthetic_demo_flag BOOLEAN
);
