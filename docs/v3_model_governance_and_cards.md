# v3 Model Governance and Cards

The model registry uses synthetic demonstration data and is not validated for clinical decision-making.

## Required Assets

The registry contains 15 assets across operational forecasting and synthetic-only clinical surveillance:

- INPT_OCCUPANCY_FORECAST
- ED_BOARDING_FORECAST
- DISCHARGE_BY_TIME_BAND
- PICU_NICU_PRESSURE
- OR_CANCELLATION_RISK
- AMB_REFERRAL_DEMAND_FORECAST
- AMB_BACKLOG_FORECAST
- NO_SHOW_LATE_CANCEL_RISK
- URGENT_WAITLIST_BREACH_RISK
- DIAGNOSTIC_READINESS_RISK
- PEDIATRIC_EARLY_WARNING_SIGNAL
- SEPSIS_SURVEILLANCE_SIGNAL
- RARE_DISEASE_CASE_FINDING_SIGNAL
- READMISSION_REVISIT_RISK
- LONG_STAY_RISK

Each card includes purpose, intended and not-intended use, inputs, features, model class, training/config period, validation window, cadence, calibration, drift, subgroup review, thresholds, alert burden, FP/FN review, governance status, deployment status, owner, sponsor, review dates, warnings, caveats, fallback, rollback, related outputs, and synthetic evidence.
