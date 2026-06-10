# v2 Open Data Catalog

## Runtime Policy

The apps do not require live open-data availability at runtime. Public context is cached/precomputed into synthetic-friendly snapshots.

## Catalog Areas

| Area | Candidate Source Type | v2 Use | Runtime |
| --- | --- | --- | --- |
| Respiratory activity | Public respiratory virus surveillance | Seasonal pediatric demand context | Cached fallback |
| Weather | Public weather observations/forecasts | Travel and demand context | Cached fallback |
| AQHI / smoke | Public air-quality and wildfire-smoke context | Respiratory and travel proxy | Cached fallback |
| Population | Statistics Canada pediatric age-band and regional demographics | Denominator/context only | Cached fallback |
| Calendar | Public holidays and school-calendar context | Demand and clinic patterns | Cached fallback |

## Boundary

Open data is ecological and contextual. It is not a patient-level predictor by itself and should be reviewed for fairness, geography, and interpretation risks before production use.
