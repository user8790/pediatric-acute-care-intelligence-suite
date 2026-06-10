# v2 Testing Report

## Local Results

Validated on Windows from `C:\Users\carrc\OneDrive\Documents\Presentation 1`.

| Check | Command | Result |
| --- | --- | --- |
| V2 data generation | `python packages/synthetic/generate_v2_showcase_data.py` | Passed |
| Python tests | `python -m pytest` | Passed, 28 tests |
| Streamlit compile | `python -m py_compile ...` | Passed |
| Streamlit runtime smoke | local Streamlit HTTP checks on ports 8511 and 8512 | Passed |
| Showcase build | `pnpm run build:showcase` | Passed |
| Showcase browser smoke | local Vite dev server opened in browser | Passed; no app console errors |
| Showcase Playwright e2e | `pnpm --dir apps/showcase test:e2e` | Passed, 6 tests across desktop/mobile Chromium |

## Notes

- Browser console contained only React's development-tools informational message during local dev-server verification.
- No Snowflake warehouse execution was performed locally; SQL validation is static.
- Streamlit apps were validated in local/sample mode and are designed to query Snowflake v2 marts when running in Snowflake.

## Commands

```powershell
python packages/synthetic/generate_v2_showcase_data.py
python -m pytest
pnpm run build:showcase
pnpm --dir apps/showcase test:e2e
python -m py_compile apps/snowflake_streamlit/inpatient/streamlit_app.py apps/snowflake_streamlit/ambulatory/streamlit_app.py apps/snowflake_streamlit/shared/lib/common.py
```
