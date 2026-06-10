# Future Real-Data Mapping

Future real data must map through curated views only. Do not connect apps directly to PHI tables or confidential source schemas.

Placeholder curated views:

- `VW_ADT_EVENTS`
- `VW_INPATIENT_ENCOUNTERS`
- `VW_BED_STATUS`
- `VW_ED_VISITS`
- `VW_OR_CASES`
- `VW_DISCHARGE_MILESTONES`
- `VW_REFERRALS`
- `VW_APPOINTMENTS`
- `VW_WAITLIST`
- `VW_CLINIC_TEMPLATES`
- `VW_PROVIDER_AVAILABILITY`
- `VW_STAFFING`
- `VW_OPEN_RESPIRATORY`
- `VW_OPEN_WEATHER`
- `VW_OPEN_POPULATION`

For each mapping, `packages/contracts/source_to_canonical_mapping.yml` defines:

- canonical field
- expected type
- nullable
- derivation logic
- privacy sensitivity
- aggregation level
- validation checks
- implementation notes

Implementation guidance:

1. Create governed curated views in Snowflake.
2. Replace synthetic raw views with curated view definitions.
3. Keep marts aggregated.
4. Run data quality checks.
5. Validate models locally before exposing predictions.
6. Keep patient-level detail out of executive dashboards by default.

