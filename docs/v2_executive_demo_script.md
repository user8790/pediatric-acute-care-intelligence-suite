# v2 Executive Demo Script

## 3-Minute Overview

1. Open the showcase overview.
2. State the boundary: synthetic pediatric operations data only, not validated for clinical decision-making.
3. Show the current inpatient occupancy, ambulatory waitlist, urgent breach-risk proxy, and quality status.
4. Explain that the suite moves from posture to drivers to scenario options.
5. Close by showing the governance path: future real data would arrive through curated governed Snowflake views only.

## 10-Minute Walkthrough

1. **Overview:** frame the product as a data-informed planning surface for pediatric operations.
2. **Inpatient:** show occupancy, effective beds, ED boarders, PICU/NICU pressure, discharge barriers, and the ED-to-inpatient handoff network.
3. **Ambulatory:** show waitlist ageing, third-next-available, referral demand, clinic template constraints, diagnostics, and travel/virtual-care lens.
4. **Simulation:** compare scenario frontiers by impact, effort, operational risk, fairness proxy, and uncertainty.
5. **Methods:** show model cards, coefficients, queueing approximations, public context, and caveats.
6. **Governance:** show identifier boundary, quality checks, no direct identifiers, and the curated-view real-data path.

Suggested close: v2 is a credible conversation prototype. It does not make clinical decisions; it shows what a governed, locally validated product could look like.

## 20-Minute Deep Dive

Use the 10-minute path, then add:

- coefficient registry and queueing methods;
- Snowflake SQL script order and v2 marts;
- Streamlit/Snowflake package boundary;
- minimum viable real-data connection path;
- data-quality and model-monitoring requirements;
- local validation and governance gates before any production use.
