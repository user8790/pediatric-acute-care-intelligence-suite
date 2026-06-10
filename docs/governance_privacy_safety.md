# Governance, Privacy, and Safety

## Required Labels

All app surfaces and documentation must retain:

- Synthetic demonstration data.
- Not connected to real hospital systems.
- Not validated for clinical decision-making.

## Privacy Controls

- No names, MRNs, health numbers, phone numbers, or addresses.
- Age bands instead of birth dates.
- Aggregate/cohort displays by default.
- Small-cell suppression helper available for future real data.
- Future integrations must use curated Snowflake views.

## Safety Controls

- Scenario recommendations are phrased as options.
- Clinical/safety indicators are synthetic demonstration indicators only.
- Every model output includes horizon, uncertainty, drivers, freshness, validation status, and caveat.
- Production use would require local validation, clinical governance, human-factors review, and model monitoring.

