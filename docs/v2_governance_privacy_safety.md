# v2 Governance, Privacy, and Safety

## Safety Boundary

- Synthetic demonstration data only.
- Not connected to real hospital systems.
- Not validated for clinical decision-making.
- No implication of production connection to AHS, Stollery, Alberta Children's Hospital, Connect Care, Epic, or production Snowflake.

## Privacy Boundary

The suite avoids names, MRNs, health numbers, direct addresses, phone numbers, and realistic direct identifiers. Future real-data work must use governed curated Snowflake views and aggregate marts.

## Governance Controls

- purpose limitation and role-based access;
- data minimisation and aggregate-first displays;
- audit logging for scenario runs;
- model cards and validation status;
- quality checks and direct-identifier scans;
- local temporal validation before operational use;
- subgroup calibration and alert/intervention monitoring;
- documented caveats in apps and docs.

## Standards Lens

Future production planning should consider Alberta HIA obligations, TRIPOD+AI, NIST AI RMF, GMLP, FHIR/SMART, CDS Hooks, and local clinical governance requirements.
