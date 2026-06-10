# v2 Known Limitations and Next Steps

## Limitations

- All hospital and model data is synthetic.
- Forecast and scenario outputs are plausible demonstrations, not validated estimates.
- Public context is cached and simplified.
- The showcase is static and does not run live services.
- Streamlit writeback depends on Snowflake privileges.
- No patient-level real data is included.
- Equity, travel burden, and fairness proxies are neutral synthetic planning signals and require local review before any production use.

## Recommended Next Pass

1. Validate the v2 Streamlit apps in an actual Snowflake account.
2. Add CI jobs for Python tests, data generation, SQL static checks, and showcase build.
3. Expand Playwright into screenshot baseline comparison for the six public showcase pages.
4. Expand Snowflake SQL synthetic data to populate all v2 marts directly instead of relying on derived placeholders.
5. Add real-data readiness workshops around curated views, field contracts, privacy review, and local model validation.
