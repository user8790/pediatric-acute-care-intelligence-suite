# Inpatient Dashboard Spec

## Mission Control

Operational question: what is happening now, what will happen in 6-72 hours, and what choices exist?

KPI set:

- Current occupancy by site.
- Staffed, physical, and effective beds.
- ED boarders awaiting inpatient bed.
- Predicted discharges and discharge confidence.
- PICU/NICU pressure proxies.
- Main risk drivers and scenario options.

## Detail Modules

- Bed flow and census: hourly census, heatmaps, bed status, isolation constraints.
- ED-to-inpatient handshake: admitted boarders, interval proxies, destination service.
- Procedural/OR/PACU impact: post-op bed demand and cancellation risk proxy.
- High-resource flow: PICU/NICU demand and step-down bottlenecks.
- Staffing and workload: scheduled versus required proxy and acuity-weighted workload.
- Safety and reliability: synthetic demonstration indicators only.
- Discharge system: barriers, barrier age, discharge reliability.
- Provincial pediatric network: cross-site capacity and transfer-pressure proxy.

All clinical/safety signals are synthetic and labelled as not clinical tools.

