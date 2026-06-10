# Agent Notes

This repository contains the Pediatric Acute Care Intelligence Suite prototype. It uses synthetic hospital operations data only.

Key guardrails:

- Do not add real patient, staff, physician, provider, MRN, health-card, address, phone, or direct identifier data.
- Keep all hospital facts synthetic unless a file is clearly marked as public open data.
- Future real-data integrations must pass through curated Snowflake views. Do not hardcode confidential AHS, Epic, Connect Care, or operational table names.
- Documentation and app footers must retain "synthetic demonstration data" and "not validated for clinical decision-making" language.
- Streamlit in Snowflake baseline dependencies must come from the Snowflake Anaconda channel.

Common local commands:

```powershell
python packages/synthetic/generate_synthetic_data.py
python -m pytest
pnpm install
pnpm run build:showcase
```

