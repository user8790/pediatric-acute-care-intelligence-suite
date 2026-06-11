# v3 Testing Report

This report covers synthetic demonstration data and is not validated for clinical decision-making.

## Planned Checks

- Generate v3 frontier assets.
- Python unit and integration tests.
- Showcase TypeScript and Vite production build.
- Showcase Playwright public-surface tests.
- Streamlit compile smoke for inpatient, ambulatory, shared helpers, and Gatekeeper.
- Snowflake SQL static checks.
- Documentation presence and safety language checks.

## Latest Local Results

- `python -m pytest`: 37 passed.
- `pnpm run build:showcase`: passed.
- `pnpm --dir apps/showcase test:e2e`: 8 passed across desktop and mobile Chromium.
- Playwright browser visual check: local preview rendered the v3 System Posture page, Walkthrough remained hidden from public nav, driver cards were corrected after screenshot review, and no obvious overlaps or blank sections remained on the checked page.
