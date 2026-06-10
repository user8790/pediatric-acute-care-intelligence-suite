# v2 Methods and Coefficients

## Method Families

- Forecast ribbons: precomputed synthetic point forecasts with p10/p90 intervals.
- Queueing coefficients: arrival rate, service rate, servers/resources, utilisation, Erlang C, Erlang B, Kingman, Allen-Cunneen, and Little's Law.
- Scenario grids: precomputed inpatient and ambulatory scenario outputs with uncertainty ranges.
- Deterministic fallbacks: bounded sensitivity calculations for Streamlit when writeback or full scenario marts are unavailable.
- Quality checks: freshness, primary key, bounds, missingness, timestamp logic, and direct-identifier scans.

## Required Coefficients

The v2 coefficient registry includes:

- arrival rate `lambda`;
- service rate `mu`;
- servers/resources `c`;
- utilisation `rho`;
- interarrival variability `Ca2`;
- service variability `Cs2`;
- Erlang C wait probability;
- Erlang B blocking probability;
- Kingman wait approximation;
- Allen-Cunneen wait approximation;
- Little's Law;
- discharge completion rate;
- bed-turnaround time;
- effective staffed bed coefficient;
- isolation constraint factor;
- step-down constraint factor;
- respiratory surge multiplier;
- weather/smoke multiplier;
- school/holiday multiplier;
- no-show probability;
- overbooking coefficient;
- diagnostic dependency delay;
- protected-slot coefficient;
- virtual-care conversion coefficient.

All values are synthetic demonstration values. Local calibration, temporal validation, subgroup review, and governance approval are required before operational use.
