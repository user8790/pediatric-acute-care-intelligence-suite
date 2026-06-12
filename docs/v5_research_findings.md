# V5 Research Findings: Pediatric Command Centre / Progression Hub

Date: 2026-06-11

Scope: public research only. This document translates public command-centre, progression-hub, Alberta context, and Snowflake data-platform patterns into product requirements for the synthetic Pediatric Acute Care Intelligence Suite showcase. It does not contain real patient, staff, provider, AHS, Connect Care, or confidential operational data.

Safety language: all examples and data in the showcase remain synthetic demonstration data and are not validated for clinical decision-making.

## Executive Takeaways

The showcase needs to behave less like a portfolio dashboard and more like a daily command surface. The strongest examples organize work around operational objects: site, unit, service, program, warning, source, model, scenario, transfer, discharge barrier, staffing constraint, and resource trade-off. A useful pediatric command centre should answer five questions continuously:

1. What changed since the last huddle?
2. Which object needs attention now?
3. What is the trusted lineage behind the number?
4. Which HR/workforce, finance/resource, and open-data constraints explain the pressure?
5. What happens if we pull this lever?

Design implication: v5 should make every global control change the visible operating surface. Static panels should be replaced by clickable object cards, drilldown drawers, context-sensitive charts, lineage badges, and scenario controls that visibly update outputs.

## Benchmarks

### Johns Hopkins Capacity Command Center

Johns Hopkins describes the Judy Reitz Capacity Command Center as a system-level hub for patient throughput and clinical care, staffed by access-line, transport/communications, and bed-management specialists. The operating model includes daily bed-management huddles, executive operations huddles, optimization meetings, operating-metrics reviews, and specialty roles for barriers to flow. Source: [Johns Hopkins Medicine - Judy Reitz Capacity Command Center](https://www.hopkinsmedicine.org/emergency-medicine/c3).

Key design patterns for v5:

- Put bed placement, transfer pressure, discharge readiness, critical-care acceptability, and transport constraints into the same workspace.
- Represent work as live queues and objects, not passive summary cards.
- Include huddle cadence, owner/status, and escalation paths.
- Show current state plus near-future demand, not only history.

### Johns Hopkins Epic Capacity Management Dashboards

Johns Hopkins IT reported an enterprise rollout of Epic Capacity Management Dashboards that created a single real-time view of patient flow and throughput, with standardized data supporting access, flow, and length-of-stay decisions. Source: [Johns Hopkins IT - Epic Capacity Management Dashboards](https://it.johnshopkins.edu/featured-articles/epic-capacity-management-dashboards-go-live-system-wide/).

Key design patterns for v5:

- Treat the EHR-derived view as the operational source of truth, but do not stop there.
- Make data lineage and dashboard usage explicit.
- Show how a single operational object appears in multiple surfaces: huddle, warning queue, scenario, model card, and source readiness.

### Children's Mercy Patient Progression Hub

Children's Mercy describes a pediatric Patient Progression Hub using real-time data and predictive analytics to improve access, streamline patient flow, enhance discharge timeliness, determine staffing needs, and forecast demand. Its tile examples include capacity expediting by unit, patient status, risk of harm, discharge expediting, and flow administration. Source: [Children's Mercy - Patient Progression Hub](https://www.childrensmercy.org/about-us/patient-progression-hub/).

Key design patterns for v5:

- Add pediatric-specific progression objects: unit capacity, care progression gaps, discharge barriers, staffing need, demand forecast, and safety/warning signals.
- Let users click from a unit/program to the drivers that explain it.
- Make staff/workforce needs a first-class input, not a footnote.

### Hospital Command Centre Literature and Market Patterns

Recent command-centre literature and industry descriptions converge on centralized patient-flow orchestration, resource allocation, predictive staffing, logistics, and finance impact. This supports a v5 operating model that combines EHR-derived movement data, workforce capacity, finance/resource proxies, and public context. Useful public references include:

- [AHS ED wait-time logic](https://www.albertahealthservices.ca/waittimes/waittimes.aspx), which explicitly combines ED people waiting, acuity, and available resources.
- [Snowflake Healthcare and Life Sciences](https://www.snowflake.com/en/solutions/industries/healthcare-and-life-sciences/), which frames healthcare use cases around unifying siloed EHR/claims/other data and optimizing care delivery, staffing, and efficiency.
- [Deloitte - hospital command centers](https://www.deloitte.com/us/en/insights/industry/government-public-sector-services/imagining-virtual-command-center-for-federal-health-system.html), which frames command centres as centralized analytics hubs for capacity, inventory, and patient flow.

Key design patterns for v5:

- Add resource feasibility to every what-if: staffing, skill mix, overtime, allied-health dependency, operating-cost proxy, and resource ceiling.
- Make every modelled number auditable: features, coefficients or proxy coefficients, thresholds, validation, drift, alert burden, source readiness, caveats.
- Keep governance visible: direct, derived, modelled, open data, HR, finance, and governance badges.

## Alberta Public Context

The v5 synthetic data should feel Alberta-pediatric-realistic without using real operational data. Public context can shape synthetic assumptions, labels, open-data source readiness, and scenario levers.

### Pediatric Sites and Catchments

- Alberta Children's Hospital is an AHS facility in Calgary providing healthcare services for children under 18, including a 24/7 emergency department. Source: [AHS facility page](https://www.albertahealthservices.ca/findhealth/facility.aspx?id=1010904).
- Stollery Children's Hospital pediatric ED is described by AHS as the only specialized ED and referral centre for children in central and northern Alberta, available 24/7, serving children from birth up to their 18th birthday. Source: [AHS Stollery pediatric ED service page](https://www.albertahealthservices.ca/findhealth/Service.aspx?id=1067772&serviceAtFacilityID=1105308).

Design implication: model two site-specific pediatric command surfaces plus a network aggregate, with north/south catchment context and a public-context overlay.

### ED Wait-Time Logic

AHS explains estimated ED wait times as a software calculation using current facility data that compares people in the ED and acuity with the resources available and required to treat them. The published estimate is approximate, changes quickly, and does not apply to critically ill/injured patients. Source: [AHS ED wait times](https://www.albertahealthservices.ca/waittimes/waittimes.aspx).

Design implication: v5 should expose a synthetic "ED pressure logic" object using waiting volume, acuity mix, physician/nurse resource proxy, and bed-boarder feedback. It must not imply a clinical triage directive.

### Respiratory Virus Dashboard

Alberta's respiratory virus dashboard includes COVID-19, influenza, RSV, severe outcomes, laboratory testing, outbreaks, immunizations, variants, wastewater surveillance, and historical data. Source: [Alberta respiratory virus dashboard](https://www.alberta.ca/stats/dashboard/respiratory-virus-dashboard.htm).

Design implication: use cached synthetic respiratory activity to affect at least three visible surfaces: respiratory/PICU/NICU forecast, staffing surge assumptions, and ambulatory respiratory/diagnostics demand.

### AQHI, Weather, and Smoke

Environment Canada/AHS/Alberta partners publish AQHI conditions and forecasts. Alberta notes wildfire smoke can affect air quality, uses PM2.5 and other pollutants, and provides AQHI and smoke-monitoring information. Sources: [Environment Canada AQHI Edmonton](https://weather.gc.ca/airquality/pages/abaq-001_e.html), [Alberta wildfire smoke information](https://www.alberta.ca/wildfire-smoke-information), [ECCC historical climate data](https://climate.weather.gc.ca/).

Design implication: use synthetic AQHI/smoke and weather context to affect respiratory demand, virtual/outreach suitability, staff travel risk, and scenario feasibility.

### Population and Demographics

Statistics Canada table 17-10-0005-01 provides annual population estimates by age and gender for provinces and territories. Source: [Statistics Canada table 17-10-0005-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000501).

Design implication: use synthetic pediatric catchment weights by region/age band for expected demand, ambulatory waitlist pressure, and equity/travel guardrails.

### School and Holiday Calendars

Public school calendars list school-year holidays, breaks, PD days, and first/last instructional dates. Example source: [Edmonton Public Schools printable calendars](https://epsb.ca/calendars/printablecalendars/).

Design implication: use school calendar proxies for respiratory season mixing, family availability for discharge planning, ambulatory no-shows, and post-discharge follow-up scheduling.

## Snowflake Data Architecture Implications

For a future production version, curated Snowflake views should separate source domains and governance layers. v5 should rehearse the pattern synthetically.

Recommended source domains:

- EHR-derived operational: ADT events, bed status, unit census, ED visits, triage/accommodation status, orders, diagnostic readiness, procedures, appointments, referrals, waitlists, discharge milestones, transfer requests.
- HR/workforce: rostered shifts, filled shifts, sick calls, float pool, skill mix, overtime proxy, agency use proxy, provider/allied-health template availability.
- Finance/resource: variable staffing cost proxy, protected-bed cost proxy, diagnostic/procedure capacity proxy, overtime exposure, incremental clinic/session cost, resource ceiling.
- Open data/context: respiratory virus activity, AQHI/smoke, weather, pediatric population/catchment, school/holiday calendar.
- Governance: metric registry, model registry, coefficients, warning logic, validation/drift, release/rollback, direct-link validation, small-cell suppression.

Implementation requirements for v5:

- Every major number shows direct, derived, modelled, open-data, HR, finance, or governance badges.
- Clicking a badge opens source readiness and lineage.
- Every model card opens source fields, feature families, proxy coefficients, thresholds, calibration, validation, drift, alert burden, dashboard usage, and caveats.
- Scenarios must calculate feasibility against HR and finance constraints and show confidence intervals, sensitivity, trade-offs, and affected objects.
- Open-data context must change forecast/scenario assumptions visibly.

## V5 Product Requirements Derived From Research

1. Global controls must be real.
   Persona, site, horizon, service, unit, program, and scenario must change charts, metrics, narratives, and drawers. If a control cannot affect the page, it should be disabled or omitted.

2. The app should be object-centred.
   Sites, services, units, programs, warnings, scenarios, sources, and models should be clickable objects. Drawers should contain operational details, lineage, readiness, and actions.

3. Inpatient depth must include:
   capacity, census, staffed/effective beds, ED boarders, transfers, discharge barriers, predicted admissions/discharges, staffing/HR, finance/resource proxy, warnings, source readiness, and open-data context.

4. Ambulatory depth must include:
   referrals, triage, waitlist, third next available, template capacity, no-shows, diagnostics, follow-up, provider/allied-health capacity, HR/resource constraints, finance/resource proxy, and source readiness.

5. Scenario lab must be rebuilt around levers:
   inpatient, ambulatory, HR/workforce, finance/resource, open-data context, confidence intervals, sensitivity, trade-offs, and affected units/programs.

6. Synthetic data must expand:
   at least dozens of unit/program objects, hundreds of time-series rows, and app-ready overlays for HR, finance, open data, model warnings, and source readiness. All data remains aggregate and synthetic.

## Decision-Grade Refinement: Clinical AI Simulation Research Inputs

The next showcase layer adds four deep AI-tool-inspired implementation rehearsals. These are not production clinical tools. They are prototype pages that show how a pediatric intelligence layer could connect signal design, operational context, coefficients, thresholds, source readiness, validation, governance, action, and learning before any local clinical deployment.

### Triage and LOS Orchestration

Public ED wait-time logic already emphasizes that operational delay is a function of people waiting, acuity, and available resources. Pediatric ED and inpatient LOS research also shows that admission, ICU utilization, prolonged LOS, orders, disposition timing, diagnostics, and clinical context can be modelled from EHR data, but performance depends on missing-data handling, cohort definition, calibration, and workflow fit. Useful anchors include [AHS ED wait-time logic](https://www.albertahealthservices.ca/waittimes/waittimes.aspx), pediatric ED prolonged-LOS modelling in PubMed ([PMID 40203463](https://pubmed.ncbi.nlm.nih.gov/40203463/)), ED LOS data-mining work ([PMID 31808312](https://pubmed.ncbi.nlm.nih.gov/31808312/)), and real-time PICU LOS forecasting from updated orders ([PMID 22824935](https://pubmed.ncbi.nlm.nih.gov/22824935/)).

Design implication: the showcase should treat LOS orchestration as demand-and-supply operations intelligence, not as a clinical triage directive. It should show ED arrivals, acuity mix, bed blockers, diagnostic turnaround, staffing, effective bed supply, and resource ceilings together, with transparent proxy weights and confidence bands.

### Rare-Disease Case Finding

CHEO's public ThinkRare materials describe a rules-based/search algorithm that uses routinely collected clinical information to identify children who may have undiagnosed rare genetic disease for clinician review and possible referral. Public anchors include CHEO's national-expansion reporting, the University of Ottawa summary, and the PubMed-indexed Genetics in Medicine article ([PMID 40856103](https://pubmed.ncbi.nlm.nih.gov/40856103/)).

Design implication: the showcase should frame rare-disease intelligence as clinician-facing case-finding and pathway support. It should show phenotype-pattern logic, repeated utilization, referral gaps, diagnostic delay proxies, governance status, source readiness, genetic-testing capacity, and an implementation queue. It must avoid diagnostic claims.

### General Pediatric Deterioration Early Warning

Paediatric Early Warning Scores are widely used to detect physiological deterioration, but reviews emphasize mixed evidence, local variation, human-factors dependency, alert-burden risk, and the need for careful validation. Useful anchors include PubMed overviews and reviews ([PMID 30413488](https://pubmed.ncbi.nlm.nih.gov/30413488/), [PMID 31061010](https://pubmed.ncbi.nlm.nih.gov/31061010/), [PMID 37121311](https://pubmed.ncbi.nlm.nih.gov/37121311/)).

Design implication: the showcase should show an early-warning simulation as a silent-evaluation and governance design. It should include trend features, workload/staffing context, calibration, subgroup performance, alert burden, review workflow, and rollback dependencies. It must not present a bedside alarm.

### NEC Recognition Rehearsal

NEC prediction and neonatal AI literature shows active work across risk prediction, biomarkers, diagnosis/prognosis, and neonatal morbidity forecasting, but the clinical stakes and cohort sensitivity require especially strong safety and governance. Useful anchors include neonatal AI prediction review work ([PMID 35562414](https://pubmed.ncbi.nlm.nih.gov/35562414/)), NEC AI/ML reviews ([PMID 37303753](https://pubmed.ncbi.nlm.nih.gov/37303753/), [PMID 40310141](https://pubmed.ncbi.nlm.nih.gov/40310141/)), and diagnostic-challenge literature ([PMID 32855507](https://pubmed.ncbi.nlm.nih.gov/32855507/)).

Design implication: the showcase should make NEC an explicit "blocked until governed" prototype. It should show neonatal cohort definition, feeding and prematurity features, infection/inflammation signals, vitals/labs, imaging readiness, leakage controls, model-card caveats, silent validation, and neonatal safety review before any operational warning.

### Cross-Cutting Governance Requirements

The four simulation pages should share the same trust language:

- Aggregate synthetic demonstration data only.
- No direct personal identifiers in the display layer.
- Source readiness before model readiness.
- Proxy coefficients labelled as such until validated.
- Silent evaluation before alerts.
- Subgroup calibration, drift, alert-burden, and human-factors review before release.
- Clinical owner, analytics owner, governance owner, and rollback path required.

## International And Safety-Governance Refinement Inputs

This pass broadened the benchmark beyond North American command-centre examples. Publicly described Singapore C3 and smart-hospital patterns reinforce that command centres mature through stages: real-time visibility, predictive sensing, cross-institution coordination, operational escalation, and closed-loop learning. Japan's medical-DX and health-data modernization direction reinforces the same prerequisite: high-quality interoperable data infrastructure before operational AI should be trusted.

Design implications added in the 15-lens pass:

- The app needs an operating desk, not only domain pages.
- Signals should become reviewable decision packets with owner, urgency, evidence-to-clear, action options, safety gate, follow-up window, and learning metric.
- International command-centre examples emphasize cadence: huddles, executive reviews, source repair, clinical safety holds, and cross-site escalation.
- AI governance examples from WHO, NIST, FDA, and Singapore guidance emphasize transparency, lifecycle risk management, human oversight, monitoring, rollback, and clear non-autonomous decision-support boundaries.
- Implementation-science patterns emphasize fit with existing huddles, local champions, audit-and-feedback, adaptation, and spread/retire decisions.

The v6-style Command Desk was added to make those implications visible in the product.

## Implementation Notes And Gaps

This research is sufficient to guide v5. Remaining future gaps:

- Public sources do not provide real AHS pediatric command-centre configuration, and this showcase must not infer confidential local workflows.
- Public source availability changes over time; any production pipeline would require a governed open-data ingestion registry, caching, provenance, and refresh monitoring.
- HR and finance integration must be handled through approved workforce and finance marts with role-based governance; v5 uses synthetic resource proxies only.
- Clinical surveillance outputs must stay explicitly non-clinical until local validation, calibration, governance approval, and rollback procedures exist.
