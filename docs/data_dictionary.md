# Data Dictionary

This dictionary lists the canonical table surface. Synthetic CSVs are written to `data/synthetic`.

## Core Dimensions

- `DIM_SITE`: site, zone, and latitude/longitude proxy.
- `DIM_UNIT`: unit, service line, physical beds, baseline occupancy, high-resource flag.
- `DIM_BED`: synthetic bed inventory and isolation/monitoring flags.
- `DIM_DATE`, `DIM_TIME_BLOCK`: calendar and shift structure.
- `DIM_AGE_BAND`: pediatric age bands only, not birth dates.
- `DIM_EQUITY_GEO_PROXY`: aggregate travel-burden proxy, not patient address.
- `DIM_MODEL`, `DIM_METRIC`, `DIM_SCENARIO`: model and scenario metadata.

## Inpatient Facts

Key dashboard facts:

- `FCT_BED_CENSUS_HOURLY`: census, staffed/effective beds, occupancy, boarders, discharge confidence.
- `FCT_OCCUPANCY_SNAPSHOT`: latest site-level mission-control snapshot.
- `FCT_DISCHARGE_BARRIER`: active barrier counts and aging.
- `FCT_MODEL_PREDICTION_INPATIENT`: forecast point and interval outputs.
- `FCT_SIMULATION_RESULT_INPATIENT`: scenario results and uncertainty bands.

Other required inpatient facts are generated with synthetic event/count templates for transferability.

## Ambulatory Facts

Key dashboard facts:

- `FCT_WAITLIST_SNAPSHOT`: waitlist, aging, third-next-available, urgent breach risk.
- `FCT_REFERRAL`: referral demand, urgent mix, triage turnaround, completeness.
- `FCT_CLINIC_SLOT`: capacity, bookings, completions, no-shows, virtual share.
- `FCT_MODEL_PREDICTION_AMBULATORY`: backlog forecasts.
- `FCT_SIMULATION_RESULT_AMBULATORY`: access scenario results.

Other required ambulatory facts are generated with synthetic event/count templates.

## Open-Data Context Facts

- `FCT_RESPIRATORY_VIRUS_ACTIVITY_OPEN`
- `FCT_WEATHER_AND_AIR_QUALITY_OPEN`
- `FCT_POPULATION_BY_AGE_REGION_OPEN`
- `FCT_SCHOOL_CALENDAR_OR_HOLIDAY_OPEN`
- `FCT_COMMUNITY_DEMAND_PROXY_OPEN`
- `FCT_PUBLIC_HEALTH_ALERT_OR_SEASONAL_EVENT_OPEN`

These are public context/fallback snapshots and are not real patient or hospital operations data.

