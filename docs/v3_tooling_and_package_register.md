# v3 Tooling and Package Register

Synthetic demonstration data only. Not validated for clinical decision-making.

This register records the free/open-source packages and Codex plugins used for the v3 showcase, Streamlit/Snowflake path, testing, build, and deployment work. No paid APIs, paid plugins, trial-only services, metered model APIs, stored secrets, or runtime dependencies on external SaaS services were added to the deployed showcase.

## Showcase Runtime and Build

| Package/tool | License | Why it is present | Affects |
| --- | --- | --- | --- |
| React / React DOM | MIT | Public showcase UI and stateful product surfaces. | Showcase runtime |
| Vite | MIT | Fast local dev server and static production build for Vercel. | Showcase build |
| @vitejs/plugin-react | MIT | React transform support in the Vite build. | Showcase build |
| TypeScript | Apache-2.0 | Static checking for the showcase app contract. | Showcase build/tests |
| Apache ECharts | Apache-2.0 | Interactive charts for forecasts, heatmaps, scenario frontiers, and governance visuals. | Showcase runtime |
| lucide-react | ISC | Consistent iconography for controls, tabs, and status panels. | Showcase runtime |

## Testing and Verification

| Package/tool | License | Why it is present | Affects |
| --- | --- | --- | --- |
| @playwright/test | Apache-2.0 | Browser-based smoke and public-page verification, including the Walkthrough-tab public-hide guard. | Showcase tests |
| pytest | MIT | Python integration tests for generated assets, Snowflake SQL static checks, and Streamlit compile checks. | Tests |
| Codex Browser/Playwright skill | Local Codex tooling | Visual/browser QA during development; does not ship with the app. | Verification only |

## Streamlit and Snowflake Path

| Package/tool | License | Why it is present | Affects |
| --- | --- | --- | --- |
| Streamlit | Apache-2.0 | Snowflake-transferable operational dashboards and Streamlit Community Cloud prototypes. | Streamlit runtime |
| pandas | BSD-3-Clause | Local sample CSV loading and Snowflake result handling. | Streamlit runtime |
| numpy | BSD-3-Clause | Numeric support in Streamlit Cloud requirements. | Streamlit runtime |
| Plotly | MIT | Streamlit charts for mission control, Gatekeeper, and source-readiness views. | Streamlit runtime |
| Altair | BSD-3-Clause | Optional Streamlit Cloud chart dependency already listed for app compatibility. | Streamlit runtime |
| Snowpark Python | Apache-2.0 | Used only inside Snowflake runtime when an active session exists; local mode falls back to sample CSV/session state. | Snowflake Streamlit path |

Snowflake Streamlit apps remain conservative: v3 additions are CSV/SQL/readiness/registry tables and standard Streamlit visualizations. Showcase-only tooling such as Vite, React, ECharts, and Playwright is not imported by the Streamlit/Snowflake apps.

## Codex Plugins and Deployment Tools

| Tool/plugin | Cost/secrets posture | Why it was used | Affects |
| --- | --- | --- | --- |
| GitHub plugin / `git` CLI | Uses the user's authenticated GitHub context; no credentials stored in repo. | Commit, push, and PR workflow. | Repository publication |
| Vercel plugin / CLI | Uses the user's authenticated Vercel context; no credentials stored in repo. | Static showcase production deployment. | Showcase deployment |
| Chrome plugin | Uses the user's existing Chrome sign-in only when needed for authenticated website verification. | Streamlit login/deployment verification fallback. | Verification/deployment only |

## Package Changes in This Pass

No new npm, Python, Codex plugin, MCP server, paid API, or external SaaS runtime package was added in this pass. The pass expanded generated synthetic assets, Streamlit sample CSVs, SQL schemas, tests, and documentation around packages already present in the repository.

## Removal Decision

No package was removed. Each listed package still materially supports the product: ECharts and Plotly for richer charts, Playwright for browser verification, React/Vite/TypeScript for the showcase, and Streamlit/pandas/numpy/Altair for Snowflake-transferable app paths.
