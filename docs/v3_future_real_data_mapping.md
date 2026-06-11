# v3 Future Real-Data Mapping

Future mapping guidance uses synthetic demonstration data and is not validated for clinical decision-making.

## Rules

- Start with read-only curated Snowflake views.
- Do not hardcode confidential AHS, Epic, Connect Care, or operational table names.
- Validate source freshness, row counts, timestamp logic, metric definitions, referential integrity, and small-cell suppression before showing operational panels.
- Separate direct, derived, and modelled layers in code, docs, SQL, and UI.
- Keep modelled outputs disabled or caveated until Gatekeeper approval is recorded.

## Phases

1. Direct source validation.
2. Derived mart and metric registry approval.
3. Modelled asset validation, alert-burden review, and rollback.
4. Learning-system writeback in Snowflake APP and GOVERNANCE schemas.
