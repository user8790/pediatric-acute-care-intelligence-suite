# Snowflake Transfer Checklist

## Before Access

- Confirm purpose, audience, and approved demonstration scope.
- Confirm no production PHI will be used in the prototype.
- Confirm Snowsight access, role, warehouse, and database naming.

## SQL Setup

- Run scripts `00` through `12` in order.
- Confirm `PEDIATRIC_AHA_DEMO` schemas exist: `RAW_SYNTH`, `CURATED`, `MART`, `APP`, `MODEL`, `CONFIG`.
- Confirm v2 objects exist:
  - `MART.MART_V2_INPATIENT_MISSION_CONTROL`
  - `MART.MART_V2_INPATIENT_FORECAST`
  - `MART.MART_V2_INPATIENT_SCENARIO`
  - `MART.MART_V2_AMBULATORY_MISSION_CONTROL`
  - `MART.MART_V2_AMBULATORY_FORECAST`
  - `MART.MART_V2_AMBULATORY_SCENARIO`
  - `MODEL.DIM_V2_MODEL_REGISTRY`
  - `MODEL.DIM_V2_COEFFICIENT_REGISTRY`
  - `APP.SCENARIO_RUN_LOG`

## App Setup

- Create inpatient and ambulatory Streamlit apps in Snowsight.
- Upload/paste app files and shared helper files.
- Use the supplied Snowflake-channel `environment.yml`.
- Confirm status panel shows Snowflake mart availability.

## Real-Data Readiness

- Use governed curated views only.
- Start with census and bed status.
- Add ADT and ED boarding.
- Add discharge milestones and barriers.
- Add OR/PACU.
- Add ambulatory referrals, waitlists, and appointments.
- Add staffing/workload.
- Add model outputs, scenario logs, monitoring, and governance review.

## Go/No-Go

Do not proceed to real-data validation until privacy, security, clinical governance, data quality, and model-validation owners have approved the scope.
