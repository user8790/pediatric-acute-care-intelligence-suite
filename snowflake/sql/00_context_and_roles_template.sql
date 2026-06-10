-- Pediatric Acute Care Intelligence Suite
-- 00_context_and_roles_template.sql
--
-- Run in Snowsight as an account/role with permission to create a demo database.
-- Replace role/warehouse names with local approved values.
-- This script intentionally avoids Snowflake CLI assumptions.

-- Example only:
-- USE ROLE <APPROVED_DEMO_OWNER_ROLE>;
-- USE WAREHOUSE <APPROVED_ANALYTICS_WAREHOUSE>;

-- Optional role pattern:
-- CREATE ROLE IF NOT EXISTS PEDIATRIC_AHA_DEMO_OWNER;
-- CREATE ROLE IF NOT EXISTS PEDIATRIC_AHA_DEMO_READER;
-- GRANT ROLE PEDIATRIC_AHA_DEMO_READER TO ROLE PEDIATRIC_AHA_DEMO_OWNER;

SELECT CURRENT_ROLE() AS current_role, CURRENT_WAREHOUSE() AS current_warehouse, CURRENT_REGION() AS current_region;

