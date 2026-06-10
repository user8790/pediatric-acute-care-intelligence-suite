-- 01_create_database_schema.sql
-- Creates the synthetic demo database and schemas.

CREATE DATABASE IF NOT EXISTS PEDIATRIC_AHA_DEMO COMMENT = 'Synthetic pediatric operations intelligence demo. No PHI.';

CREATE SCHEMA IF NOT EXISTS PEDIATRIC_AHA_DEMO.RAW_SYNTH COMMENT = 'Synthetic source-shaped tables.';
CREATE SCHEMA IF NOT EXISTS PEDIATRIC_AHA_DEMO.CURATED COMMENT = 'Canonical governed views.';
CREATE SCHEMA IF NOT EXISTS PEDIATRIC_AHA_DEMO.MART COMMENT = 'Aggregated app query marts.';
CREATE SCHEMA IF NOT EXISTS PEDIATRIC_AHA_DEMO.APP COMMENT = 'Streamlit app objects and scenario logs.';
CREATE SCHEMA IF NOT EXISTS PEDIATRIC_AHA_DEMO.MODEL COMMENT = 'Model registry and output tables.';
CREATE SCHEMA IF NOT EXISTS PEDIATRIC_AHA_DEMO.CONFIG COMMENT = 'Scenario coefficients and quality thresholds.';

USE DATABASE PEDIATRIC_AHA_DEMO;

