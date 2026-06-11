# v3 Known Limitations and Next Steps

The v3 prototype uses synthetic demonstration data and is not validated for clinical decision-making.

## Known Limitations

- Synthetic data is realistic enough for product and governance rehearsal, not operational truth.
- Vercel showcase memory is local browser state; Snowflake writeback is represented in SQL and Streamlit patterns.
- Gatekeeper approvals are synthetic and do not represent institutional review.
- Clinical surveillance assets are synthetic-only and must not be interpreted as clinical decision support.
- Streamlit/Snowsight keeps a conservative dependency baseline; advanced simulation, causal, agent, and data-cleaning packages should be isolated as optional adapters.

## Next Steps

- Add richer Streamlit pages for v3 inpatient and ambulatory readiness overlays.
- Load v3 model cards directly from Snowflake seed data.
- Add browser screenshots to the testing report after deployment.
- Expand scenario simulation with optional research adapters outside the Snowflake baseline path.
