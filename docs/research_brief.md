# Research Brief

Last checked: 2026-06-10

This prototype is a synthetic demonstration suite inspired by pediatric acute care operations. It does not use Alberta Health Services, Epic, Connect Care, Stollery, Alberta Children's Hospital, or other confidential hospital data. All hospital operations records are synthetic. Real open-data sources are used only as optional contextual signals and are cached with fallbacks.

## Current Platform Findings

### Streamlit in Snowflake

Snowflake's current Streamlit documentation says warehouse-runtime apps manage packages with Conda through an `environment.yml` file or the Snowsight package picker, and warehouse runtime dependencies are limited to the Snowflake Anaconda Channel. New Streamlit in Snowflake apps run Python 3.11 by default; warehouse runtimes can choose Python 3.9, 3.10, or 3.11. Snowflake recommends pinning critical packages and keeping dependency lists minimal.

Sources:

- Snowflake, "Manage dependencies for your Streamlit app": https://docs.snowflake.com/en/developer-guide/streamlit/app-development/dependency-management
- Snowflake, "About Streamlit in Snowflake": https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit
- Snowflake, "Using third-party packages from Anaconda": https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-packages
- Snowflake Anaconda channel: https://repo.anaconda.com/pkgs/snowflake/

Implication for Version B:

- Use `channels: [snowflake]`.
- Pin Python 3.11 and Streamlit to a supported warehouse version.
- Use only baseline Snowflake-channel packages in `environment.yml`.
- Treat River, DoWhy, Mesa, and Cleanlab as optional research/showcase adapters because they were not present in the checked Snowflake `linux-64` channel metadata on 2026-06-10. The Snowflake Streamlit path does not require advanced discrete-event simulation packages.
- Avoid external API calls, custom components, iframes, and external JavaScript in Streamlit apps. Load small aggregated marts or local sample CSVs only.

### Verified Snowflake Channel Baseline

Checked Snowflake channel metadata from:

- https://repo.anaconda.com/pkgs/snowflake/linux-64/repodata.json
- https://repo.anaconda.com/pkgs/snowflake/win-64/repodata.json
- https://repo.anaconda.com/pkgs/snowflake/noarch/repodata.json

Baseline packages found and suitable for this prototype:

- python
- streamlit
- snowflake-snowpark-python
- pandas
- numpy
- scipy
- scikit-learn
- statsmodels
- plotly
- altair
- pyyaml
- requests

Pending or optional packages not found in the checked Snowflake channel metadata:

- river
- dowhy
- mesa
- cleanlab

## Open-Data Sources Selected

The app distinguishes open context data from synthetic hospital operations data. Open data is never joined to patient-identifiable records in this prototype.

### Respiratory Virus Activity

Selected sources:

- Public Health Agency of Canada FluWatch+ respiratory virus surveillance: https://health-infobase.canada.ca/respiratory-virus-surveillance/
- Government of Alberta respiratory virus dashboard: https://www.alberta.ca/stats/dashboard/respiratory-virus-dashboard.htm

Use:

- Weekly respiratory surge multiplier.
- Seasonal demand context for inpatient, PICU/NICU, ED-admission, and ambulatory respiratory clinic scenarios.

Limitations:

- Public dashboards are surveillance summaries, not real-time hospital demand feeds.
- Recent weeks may be revised.
- For offline demo use, the repository stores compact normalized fallback snapshots.

### Weather and Air Quality

Selected sources:

- Meteorological Service of Canada GeoMet API: https://api.weather.gc.ca/openapi
- MSC Open Data Air Quality Health Index documentation: https://eccc-msc.github.io/open-data/msc-data/aqhi/readme_aqhi_en/
- Canada Open Government AQHI dataset record: https://open.canada.ca/data/en/dataset/a563e47d-6eb9-4f7f-933c-222ae49fe57f

Use:

- Temperature, smoke/PM2.5 or AQHI, and severe-weather context for demand stress and travel-burden scenarios.

Limitations:

- Weather and air-quality context is ecological. It should not be interpreted as patient-level risk.
- Streamlit in Snowflake version uses cached snapshots only.

### Population and Demographics

Selected source:

- Statistics Canada developer services and Web Data Service: https://www.statcan.gc.ca/en/developers

Use:

- Pediatric age-band denominators and regional demand context.

Limitations:

- Public demographic data is aggregated and geography-dependent.
- Future real-data implementation should maintain small-cell suppression and aggregation policies.

### Calendar, Holidays, and School Effects

Selected sources:

- Government of Alberta open data portal: https://open.alberta.ca/opendata
- Canada Open Government portal: https://open.canada.ca/data/

Use:

- Holiday and school-calendar multipliers in synthetic generator and scenario levers.

Limitations:

- Public calendars vary by school authority and may need local validation before operational use.

## Operations and Modelling Evidence

Hospital command-centre literature supports using centralized, near-real-time dashboards, predictive analytics, and standardized escalation workflows for capacity management, but evidence also highlights the need for careful data quality work and local validation.

Useful sources:

- Mebrahtu et al., "The impact of hospital command centre on patient flow and data quality: findings from the UK National Health Service," PubMed: https://pubmed.ncbi.nlm.nih.gov/37750687/
- Franklin et al., "Hospital Capacity Command Centers: A Benchmarking Survey on an Emerging Mechanism to Manage Patient Flow," PubMed: https://pubmed.ncbi.nlm.nih.gov/36781349/
- Johns Hopkins Medicine, Judy Reitz Capacity Command Center: https://www.hopkinsmedicine.org/emergency-medicine/c3
- Johns Hopkins Medicine, command center announcement: https://www.hopkinsmedicine.org/news/articles/2016/03/command-center-to-improve-patient-flow
- Cincinnati Children's Access Hub, described by Cincinnati Children's as a central capacity command center for access, capacity, flow, referrals, transfers, direct admits, and transport: https://www.cincinnatichildrens.org/professional/resources/access-hub
- SickKids SKAI Service, described as an enterprise service to develop, assess, monitor, and scale AI systems for patients, families, and staff: https://www.sickkids.ca/en/news/archive/2025/sickkids-launches-trailblazing-artificial-intelligence-program-for-paediatric-health/
- CHOP Arcus and pediatric sepsis surveillance work: https://www.research.chop.edu/cornerstone-blog/chop-researchers-co-leading-cdc-project-to-develop-national-pediatric-sepsis-surveillance-tool
- CHOP Arcus case study describing linkage of biological, clinical, research, and environmental data: https://aws.amazon.com/solutions/case-studies/chop-omics-case-study/

Design implications:

- The first screen should show current state, next risk, drivers, and options.
- Recommendations must be framed as scenarios, not clinical directives.
- Data freshness, caveats, and operational ownership should be visible.

## Simulation, Queueing, and Access Evidence

Discrete-event simulation and queueing are established approaches for healthcare flow, scheduling, and resource planning. For a transfer-friendly prototype, the methods should be transparent and reproducible before adding specialized packages.

Useful sources:

- Vázquez-Serrano et al., "Discrete-Event Simulation Modeling in Healthcare: A Comprehensive Review," International Journal of Environmental Research and Public Health, DOI 10.3390/ijerph182212262: https://www.mdpi.com/1660-4601/18/22/12262
- PubMed record for the same DES review: https://pubmed.ncbi.nlm.nih.gov/34832016/
- Green-style hospital queueing and patient-flow framing is summarized in queueing-science literature, e.g. "On Patient Flow in Hospitals: A Data-Based Queueing-Science Perspective": https://gality.net.technion.ac.il/files/2012/12/Patient-flow-main-EV.pdf
- Almaktoom et al., "Health care overbooking cost minimization model," PubMed: https://pubmed.ncbi.nlm.nih.gov/37560686/
- Robust overbooking for no-shows and cancellations in healthcare: https://www.mdpi.com/2227-7390/12/16/2563

Design implications:

- Include Erlang C for M/M/c when assumptions are acceptable.
- Include Kingman and Allen-Cunneen style approximations for higher-variance services.
- Include Monte Carlo simulation with confidence intervals.
- Use deterministic seeds and log scenario coefficients.
- Explain assumptions and limits in every app.

## Pediatric-Specific Considerations

Pediatric operations differ from adult operations because of age-band heterogeneity, respiratory seasonality, PICU/NICU constraints, guardian/family readiness, school calendar effects, procedural dependencies, and regional transfer/access patterns. Pediatric acute respiratory disease seasonality is especially relevant in Alberta demand modelling.

Useful source:

- Lukac et al., "Hospitalizations for all-cause pediatric acute respiratory diseases in Alberta, Canada, before, during, and after the COVID-19 pandemic," Lancet Regional Health - Americas, 2025, cited in CMAJ context: https://www.cmaj.ca/content/198/16/E612/F4

Design implications:

- Model winter respiratory surge explicitly.
- Keep pediatric age bands rather than precise ages by default.
- Use high-resource flow proxies carefully and label all clinical/safety signals as synthetic demonstration indicators.

## Product Assumptions

- The suite is a prototype for executive and technical evaluation, not clinical decision support.
- Synthetic data covers Stollery-inspired, Alberta Children's-inspired, and provincial network views.
- Future real-data integration happens through curated, de-identified or appropriately governed Snowflake views.
- No direct PHI, MRNs, health-card numbers, addresses, phone numbers, or patient names are generated.
- Streamlit in Snowflake apps are designed for Snowsight upload/copy workflows and no local installs on target AHS computers.

## Governance and Reporting Standards Added in the Quality Pass

The quality pass strengthened the app and documentation around standards named in the user's guidance:

- TRIPOD+AI for clinical prediction model reporting and validation transparency: https://www.tripod-statement.org/
- NIST AI Risk Management Framework for AI lifecycle risk management: https://www.nist.gov/itl/ai-risk-management-framework
- Health Canada/FDA/MHRA Good Machine Learning Practice guidance for AI/ML-enabled medical-device development: https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/good-machine-learning-practice-medical-device-development.html
- Alberta Health Information Act overview: https://www.alberta.ca/health-information-act
- SMART on FHIR documentation: https://docs.smarthealthit.org/
- CDS Hooks specification: https://cds-hooks.hl7.org/

## Streamlit Community Cloud Deployment Note

Streamlit Community Cloud documentation says dependency files are searched from the entrypoint directory first and that `environment.yml` has higher priority than `requirements.txt`. Because the Snowflake apps must keep Snowflake-channel `environment.yml` files, this repository now includes separate Community Cloud wrappers under `apps/streamlit_cloud`.

Source:

- Streamlit Community Cloud app dependencies: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies
