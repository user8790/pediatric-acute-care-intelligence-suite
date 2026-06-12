# v3 Connect Care-Realistic Synthetic Wiring

The wiring uses synthetic demonstration data and is not validated for clinical decision-making.

## Synthetic Curated Views

The v3 source registry defines EHR-like and operations-like curated views for ADT encounters, bed status, unit census, ED boarding, discharge milestones, OR/PACU flow, transfer requests, staffing, workload acuity, referrals, waitlists, clinic templates, appointments, diagnostic dependencies, safety/quality signals, public respiratory context, weather/AQHI context, model outputs, governance events, and learning memory.

Each source declares:

- Grain.
- Fields and field types.
- Cadence.
- Classification.
- PHI sensitivity.
- Dashboard usage.
- Validation rules.
- Future mapping placeholder.

Future real integrations must replace placeholders only through governed curated views. Confidential AHS, Epic, Connect Care, or operational table names must not be hardcoded.
