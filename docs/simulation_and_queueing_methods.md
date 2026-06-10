# Simulation and Queueing Methods

## Queueing Coefficients

- `lambda`: arrival rate by hour/day/service/site.
- `mu`: service rate.
- `c`: servers/resources.
- `rho = lambda / (c * mu)`: utilization.
- `Ca2`: squared coefficient of variation for interarrival times.
- `Cs2`: squared coefficient of variation for service times.
- Wait probability, `Lq`, `Wq`, `W`, and Little's Law.
- Blocking probability via Erlang B where a loss system is appropriate.

## Implemented Methods

- Erlang C for M/M/c.
- Kingman approximation for G/G/1.
- Allen-Cunneen style approximation for G/G/c.
- Pure Python/numpy discrete-event fallback for bed flow.
- Weekly backlog simulation for ambulatory access.

## Optional Adapters

Advanced simulation packages are showcase-only or research-only. The Snowflake Streamlit path uses SQL-precomputed scenario tables, deterministic fallback formulas, and Snowflake-channel packages.

## Scenario Outputs

- Occupancy probability bands.
- Boarder hours.
- Bed shortage hours.
- Backlog size.
- Clearance week.
- Utilization.
- Breach probability proxy.
- Confidence intervals.

All scenario estimates are planning estimates, not directives.
