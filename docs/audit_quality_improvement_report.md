# Audit, Quality, and Improvement Report

Date: 2026-06-10

## Findings Addressed

1. Streamlit entrypoints were too repo-path dependent for Snowsight or Streamlit Community Cloud. The apps now search local app, staged shared, repo shared, and repo-root paths before falling back.
2. Streamlit Community Cloud would have selected Snowflake `environment.yml` files before `requirements.txt`. Dedicated wrapper entrypoints now avoid that deployment conflict.
3. The showcase had strong mission-control visuals but needed more of the pasted guidance: role-based posture, definitions, governance standards, equity/fairness, and future event-driven architecture cues.
4. The repository needed a root `vercel.json` so Vercel can build the Vite app from the monorepo root.
5. The docs needed a Streamlit Community Cloud deployment guide distinct from the Snowsight deployment path.

## Product Improvements

- Added inpatient posture cards for hospital flow, synthetic safety watch, and equity/family readiness.
- Added ambulatory posture cards for access, no-show reliability, and virtual/travel burden.
- Added role-based module stacks for inpatient command-centre and ambulatory access-hub workflows.
- Added metric definitions and governance controls directly in the showcase.
- Added a governance tab with Alberta HIA, TRIPOD+AI, NIST AI RMF, GMLP, and FHIR/SMART/CDS Hooks pathing.
- Added definitions/governance tabs to both Streamlit apps.
- Added Community Cloud wrappers and app-local dependencies.

## Remaining Production Risks

- The deployed Streamlit Community Cloud apps are sample-mode demos, not Snowflake warehouse-runtime apps.
- Snowflake SQL scripts are syntactically designed for Snowsight but not executed against a live Snowflake account in this pass.
- Clinical/safety indicators remain synthetic demonstrations and require clinical validation before any operational use.
- Streamlit Community Cloud publishing may require a browser login if the user is not already authenticated.

## Published Artifacts

- GitHub repository: https://github.com/user8790/pediatric-acute-care-intelligence-suite
- Vercel showcase: https://pediatric-acute-care-intelligence-s.vercel.app/
- Streamlit inpatient demo: https://pediatric-acute-care-inpatient.streamlit.app/
- Streamlit ambulatory demo: https://pediatric-acute-care-ambulatory.streamlit.app/

HTTP smoke checks returned `200 OK` for all three deployed app URLs after publication.
