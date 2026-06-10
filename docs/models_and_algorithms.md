# Models and Algorithms

The prototype favors transparent methods over fragile complexity.

## Baselines

- Seasonal naive forecast.
- Moving average forecast.
- Hour-of-day and day-of-week seasonal baseline.
- Queueing baseline using Erlang C, Kingman, and Allen-Cunneen style formulas.

## Forecasting

- Occupancy forecast with interval bands.
- Admission and discharge proxy forecasts.
- Clinic demand and backlog forecasts.

## Classification/Risk

- Discharge by time-band probability scaffold.
- Long-stay risk scaffold, synthetic only.
- No-show/late-cancel risk.
- Referral breach risk.
- Elective cancellation risk.
- Diagnostic readiness risk.
- Staffing gap risk.

## Drift and Quality

Optional River/Cleanlab adapters are detected if available. Baseline fallback methods include:

- Population stability index.
- Missingness drift.
- Volume drift.
- Impossible timestamp checks.
- Duplicate referral heuristics.
- Status contradiction checks.

## Explainability

Every model card includes model name/version, horizon, intended use, validation status, and caveat. Driver decomposition uses feature contributions or transparent scenario coefficients.

