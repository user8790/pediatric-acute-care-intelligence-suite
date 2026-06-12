# V6 15-Lens Command Centre Review

Date: 2026-06-12

Scope: synthetic demonstration data only. The showcase remains not connected to real hospital systems and is not validated for clinical decision-making.

## Research Inputs

This pass used public research and product benchmarking from:

- Johns Hopkins Judy Reitz Capacity Command Center: command-centre staffing, bed-management, access-line, transport, huddles, operating metrics, and executive cadence.
- Johns Hopkins Epic Capacity Management Dashboard rollout: single real-time patient-flow view, standardized source of truth, and system governance.
- Children's Mercy Patient Progression Hub: pediatric progression hub, predictive analytics, co-located operations, discharge expediting, staffing needs, demand forecasting, and visible tile-based work.
- Tan Tock Seng Hospital / NCID C3 examples in Singapore: operations command centre, resource-flow visibility, hospital-to-institution coordination, and smart-hospital C3 progression from real-time visibility to predictive sensing.
- Singapore MOH HealthTech Instruction Manual and AI in Healthcare Guidelines: lifecycle governance, secure data use, public-health technology controls, and AI as augmentation rather than autonomous clinical authority.
- WHO ethics and governance of AI for health, NIST AI RMF, and FDA clinical decision support guidance: transparency, risk management, evidence, human oversight, monitoring, and decision-support boundaries.
- Japan digital-health and medical-DX public context: interoperability, health-data standardization, and high-quality health-data infrastructure as a prerequisite for safe AI and operational intelligence.

## Central Finding

The showcase is now credible as a pediatric command centre direction, but a decision-grade operating layer needs a workflow spine. The next maturity step is not more dashboards. It is a command desk that turns signals into packets of work:

1. What is the signal?
2. What does it mean?
3. Why should anyone trust it?
4. Who owns review?
5. Which scenario or action is feasible?
6. What safety or governance gate applies?
7. When is follow-up due?
8. What learning is written back?

## 15 Expert Lenses

1. World-class software architect and developer
   Finding: Page-level intelligence must become an operating-object model.
   Implemented: `decisionPackets`, `operatingCadence`, `escalationLanes`, and `expertLensReviews` are generated source-layer artifacts under v5 command context.

2. Principal frontend engineer
   Finding: Dense control surfaces must preserve orientation, stable layout, and clear affordances.
   Implemented: public `Command Desk` page with selectable packet worklist, selected-packet evidence, lens selector, huddle drawers, escalation cards, and stable chart dimensions.

3. Clinical informatician
   Finding: The product must separate observation, interpretation, and clinical action boundary.
   Implemented: packets include signal, interpretation, evidence-to-clear, safety gate, caveat, owner, and follow-up window.

4. Healthcare informatician
   Finding: Workflow state and writeback need to travel with each signal.
   Implemented: packet and cadence rows include huddle cadence, workflow state, writeback table, and learning metric.

5. Health AI safety and governance expert
   Finding: High-stakes AI must be blocked until validation, monitoring, human-factors, and rollback evidence exist.
   Implemented: governance holds are first-class packets and escalation lanes; blocked status is visible by design.

6. Data scientist
   Finding: Feature lineage, model links, and assumptions must be visible at decision time.
   Implemented: packet drawers show source badges, model chips, scenario links, and confidence language.

7. Statistician / modeller
   Finding: Uncertainty and validation evidence must be attached to action, not hidden in methods pages.
   Implemented: packets include confidence, expected impact, learning metric, and evidence-to-clear.

8. Queueing theory and patient flow expert
   Finding: Flow intelligence must distinguish arrival pressure, service rate, downstream capacity, and bottleneck location.
   Implemented: unit progression packets connect boarders, effective capacity, HR constraints, and scenario levers.

9. Acute care operations leader
   Finding: A command centre must show what needs review now, next shift, next clinic day, and which blocker needs sponsorship.
   Implemented: packet urgency and huddle cadence are visible in the Command Desk.

10. Pediatric clinical leader
    Finding: Pediatric specificity must be explicit rather than generic hospital operations language.
    Implemented: packet context and AI simulations preserve pediatric domains including respiratory, PICU/NICU, complex care, ambulatory follow-up, and neonatal safety boundaries.

11. Nursing / charge-flow leader
    Finding: Effective capacity and workload need to sit beside discharge barriers and staffing constraints.
    Implemented: unit packets and drawers expose effective beds, boarders, HR gaps, barriers, and follow-up metrics.

12. Human factors and UX expert
    Finding: The app should reduce cognitive work through consistent status grammar and next-action framing.
    Implemented: decision packets share urgency, owner, confidence, safety gate, source badges, and action capture.

13. Implementation scientist
    Finding: Adoption depends on huddle fit, local owner review, feedback loops, and spread/retire decisions.
    Implemented: command packets connect to operating cadence, follow-up windows, learning metrics, and action-learning loops.

14. Data engineering / interoperability expert
    Finding: Future feeds need curated views, canonical grains, source readiness, and dependency gates before workflow dependence.
    Implemented: packet evidence links to source IDs, model IDs, readiness badges, and governed writeback targets.

15. Executive health system strategist
    Finding: Executive value is the link between operating pressure, resource trade-off, governance blockers, and scalable learning.
    Implemented: Command Desk makes sponsorship lanes, finance/resource constraints, AI governance holds, and escalation reliability visible.

## Product Changes

- Added `Command Desk` as a public workspace.
- Added generated decision packets with urgency, owner, signal, interpretation, scenario link, safety gate, evidence-to-clear, HR/finance constraints, follow-up window, and learning metric.
- Added 15 expert-lens review rows as generated data and an interactive review board in the app.
- Added operating cadence rows for huddles and review boards.
- Added escalation lane rows for flow, HR, finance/resource, source readiness, and clinical-AI safety.
- Added packet, lens, huddle, and escalation drawers using the existing object-drawer pattern.
- Added local synthetic command-packet review capture into Learning Memory.
- Expanded chart catalog and Playwright coverage.

## Remaining Gaps

- Real operational data is still not connected; all examples remain synthetic.
- The packet workflow is a prototype representation, not a live huddle tasking system.
- Real implementation will need curated Snowflake views, role-based access, audit policy, data-quality SLAs, source-owner approvals, production writeback schemas, and workflow-owner signoff.
- Clinical-AI simulations remain blocked by default until local validation, subgroup calibration, monitoring, human-factors testing, and governance approval exist.
