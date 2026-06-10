# Synthetic Data Methodology

The generator is deterministic with seed `20260610`.

## What It Simulates

- Multi-site pediatric network: Stollery-inspired, Alberta Children's-inspired, provincial network proxy.
- Pediatric units: general pediatrics, respiratory, surgery, PICU, NICU, mental health.
- Hourly census, staffed/effective beds, occupancy, boarders, discharge confidence.
- Ambulatory referrals, waitlists, slots, no-show risk, third-next-available, breach risk.
- Winter respiratory seasonality, school-calendar effects, day/night patterns.
- Staffing gaps, isolation constraints, high-resource step-down constraints.
- Synthetic data-quality imperfections and quality checks.

## What It Does Not Generate

- Names.
- MRNs.
- Health-card numbers.
- Phone numbers.
- Addresses.
- Real patient-level data.

## Reproducibility

Run:

```powershell
python packages/synthetic/generate_synthetic_data.py
```

Outputs:

- `data/synthetic/*.csv`
- `apps/showcase/public/demo-data.json`
- `apps/snowflake_streamlit/shared/sample_data/*.csv`

