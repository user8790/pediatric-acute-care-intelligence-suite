# Future Real-Data Mapping

Future real data must map through curated governed Snowflake views only. Apps must not connect directly to raw PHI tables or confidential source schemas.

Use neutral placeholder view names in design and contracts:

- `VW_ADT_EVENTS`
- `VW_INPATIENT_ENCOUNTERS`
- `VW_BED_STATUS`
- `VW_ED_VISITS`
- `VW_OR_CASES`
- `VW_PACU`
- `VW_DISCHARGE_MILESTONES`
- `VW_DISCHARGE_BARRIERS`
- `VW_TRANSFER_REQUESTS`
- `VW_REFERRALS`
- `VW_REFERRAL_TRIAGE`
- `VW_WAITLIST`
- `VW_APPOINTMENTS`
- `VW_CLINIC_SLOTS`
- `VW_CLINIC_TEMPLATES`
- `VW_PROVIDER_AVAILABILITY`
- `VW_STAFFING`
- `VW_WORKLOAD_ACUITY`
- `VW_SAFETY_SIGNALS`
- `VW_OPEN_RESPIRATORY`
- `VW_OPEN_WEATHER_AQHI`
- `VW_OPEN_POPULATION`
- `VW_OPEN_CALENDAR`

Each mapping in `packages/contracts/source_to_canonical_mapping.yml` includes canonical field, type, grain, nullable flag, derivation logic, refresh expectation, privacy sensitivity, validation checks, aggregation rule, app usage, and implementation notes.

## Minimum Viable Real-Data Connection

1. Inpatient census and bed status only.
2. Add ADT and ED boarding.
3. Add discharge milestones and barriers.
4. Add OR/PACU.
5. Add ambulatory referrals, waitlists, and appointments.
6. Add staffing and workload.
7. Add model outputs and scenario logs.
8. Add governance, audit, model monitoring, and local validation.

## Production Principles

- Governed curated views before marts.
- Aggregate before app display.
- Small-cell and role-based suppression where needed.
- No direct identifiers in app marts.
- Patient-level drilldown only if locally approved and audited.
- Every model output needs freshness, validation status, and caveat.
