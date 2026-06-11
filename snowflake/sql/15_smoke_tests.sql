-- v3 smoke tests.
USE DATABASE PEDIATRIC_AHA_DEMO;

SELECT 'source_registry' AS test_name, COUNT(*) AS observed_rows FROM GOVERNANCE.V3_SOURCE_REGISTRY;
SELECT 'direct_link_validation' AS test_name, COUNT(*) AS observed_rows FROM GOVERNANCE.V3_DIRECT_LINK_VALIDATION;
SELECT 'model_registry' AS test_name, COUNT(*) AS observed_rows FROM MODEL.V3_MODEL_REGISTRY;
SELECT 'metric_registry' AS test_name, COUNT(*) AS observed_rows FROM CONFIG.V3_METRIC_REGISTRY;
SELECT 'learning_writeback_tables' AS test_name, COUNT(*) AS expected_tables
FROM INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'APP'
  AND table_name IN (
    'SCENARIO_RUN_LOG',
    'USER_ANNOTATION',
    'WARNING_ACKNOWLEDGEMENT',
    'METRIC_ISSUE_FLAG',
    'MODEL_REVIEW_NOTE',
    'GOVERNANCE_DECISION',
    'VALIDATION_REVIEW',
    'PANEL_FEEDBACK',
    'HUDDLE_REVIEW_EVENT',
    'LEARNING_SYSTEM_OUTCOME_REVIEW'
  );
