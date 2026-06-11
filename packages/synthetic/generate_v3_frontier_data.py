"""Generate v3 frontier operating-layer assets for the showcase and Streamlit samples.

The payloads stay synthetic and aggregate. They are intentionally shaped like a
future Snowflake-backed product contract: source readiness, derived metrics,
model governance, panel lineage, scenario outputs, and learning-system memory.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "apps" / "showcase" / "public" / "data" / "v3"
SAMPLE = ROOT / "apps" / "snowflake_streamlit" / "shared" / "sample_data"
NOW = "2026-06-11T08:30:00-07:00"

SITES = [
    ("SITE_STOLLERY_INSPIRED", "Stollery-inspired", "North provincial catchment"),
    ("SITE_ACH_INSPIRED", "Alberta Children's-inspired", "South provincial catchment"),
    ("SITE_PROV_NETWORK", "Provincial pediatric network", "Network aggregate"),
]


def write_json(name: str, payload: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
    SAMPLE.mkdir(parents=True, exist_ok=True)
    path = SAMPLE / name
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def source_registry() -> list[dict[str, Any]]:
    definitions = [
        (
            "SRC_ADT_ENCOUNTER",
            "CANONICAL.VW_SYNTH_ADT_ENCOUNTER",
            "encounter event",
            "encounter_id, site_id, unit_id, event_ts, event_type, admit_source, disposition",
            "15 minutes",
            "direct_operational_signal",
            "high aggregate only",
            "inpatient flow, ED boarding, occupancy",
        ),
        (
            "SRC_BED_STATUS",
            "CANONICAL.VW_SYNTH_BED_STATUS",
            "bed-hour",
            "site_id, unit_id, bed_type, status, effective_bed_flag, updated_ts",
            "hourly",
            "direct_operational_signal",
            "low aggregate",
            "effective capacity, source-readiness stoplights",
        ),
        (
            "SRC_UNIT_CENSUS",
            "CANONICAL.VW_SYNTH_UNIT_CENSUS_HOURLY",
            "unit-hour",
            "site_id, unit_id, census, physical_beds, effective_beds, staffed_beds",
            "hourly",
            "direct_operational_signal",
            "medium aggregate",
            "today posture, inpatient pressure, model features",
        ),
        (
            "SRC_ED_BOARDING",
            "CANONICAL.VW_SYNTH_ED_BOARDING",
            "ED boarding snapshot",
            "site_id, decision_to_admit_ts, bed_ready_ts, unit_target, boarder_count",
            "15 minutes",
            "direct_operational_signal",
            "medium aggregate",
            "boarding forecast, command summary",
        ),
        (
            "SRC_DISCHARGE_MILESTONE",
            "CANONICAL.VW_SYNTH_DISCHARGE_MILESTONE",
            "encounter milestone",
            "encounter_id, milestone_type, milestone_ts, barrier_category, expected_discharge_band",
            "hourly",
            "direct_operational_signal",
            "high aggregate only",
            "discharge reliability, why-this-changed",
        ),
        (
            "SRC_OR_PACU",
            "CANONICAL.VW_SYNTH_OR_PACU_FLOW",
            "case-day",
            "site_id, case_id, procedure_group, pacu_hold_min, post_op_bed_need, cancellation_reason",
            "daily",
            "direct_operational_signal",
            "medium aggregate",
            "OR cancellation risk, PICU/NICU pressure",
        ),
        (
            "SRC_TRANSFER_REQUEST",
            "CANONICAL.VW_SYNTH_TRANSFER_REQUEST",
            "transfer request",
            "request_id, origin_region, target_site_id, requested_level_of_care, status, age_band",
            "hourly",
            "direct_operational_signal",
            "high aggregate only",
            "provincial network posture",
        ),
        (
            "SRC_STAFFING_ROSTER",
            "CANONICAL.VW_SYNTH_STAFFING_ROSTER",
            "unit-shift",
            "site_id, unit_id, shift_start_ts, required_hours, scheduled_hours, skill_mix_group",
            "daily",
            "direct_operational_signal",
            "staff aggregate",
            "effective staffed bed coefficient",
        ),
        (
            "SRC_WORKLOAD_ACUITY",
            "CANONICAL.VW_SYNTH_WORKLOAD_ACUITY",
            "unit-shift",
            "site_id, unit_id, workload_index, observation_level, isolation_factor",
            "shift",
            "direct_operational_signal",
            "medium aggregate",
            "pressure scoring, staffing risk",
        ),
        (
            "SRC_REFERRAL",
            "CANONICAL.VW_SYNTH_REFERRAL",
            "referral",
            "referral_id, site_id, program, priority, received_ts, triage_complete_ts, status",
            "daily",
            "direct_operational_signal",
            "high aggregate only",
            "ambulatory demand, urgent breach risk",
        ),
        (
            "SRC_WAITLIST",
            "CANONICAL.VW_SYNTH_WAITLIST_SNAPSHOT",
            "program-week",
            "site_id, program, waitlist_total, waitlist_over_target, median_wait_days, p90_wait_days",
            "weekly",
            "direct_operational_signal",
            "medium aggregate",
            "ambulatory access posture",
        ),
        (
            "SRC_CLINIC_TEMPLATE",
            "CANONICAL.VW_SYNTH_CLINIC_TEMPLATE",
            "clinic-session",
            "site_id, program, template_date, slots_available, protected_urgent_slots, provider_group",
            "weekly",
            "direct_operational_signal",
            "low aggregate",
            "third-next-available, scenario capacity",
        ),
        (
            "SRC_APPOINTMENT",
            "CANONICAL.VW_SYNTH_APPOINTMENT",
            "appointment",
            "appointment_id, program, appointment_ts, appointment_type, completed_flag, no_show_flag",
            "daily",
            "direct_operational_signal",
            "high aggregate only",
            "no-show risk, slot utilization",
        ),
        (
            "SRC_DIAGNOSTIC_DEPENDENCY",
            "CANONICAL.VW_SYNTH_DIAGNOSTIC_DEPENDENCY",
            "dependency",
            "dependency_id, program, modality_group, due_ts, complete_ts, readiness_status",
            "daily",
            "direct_operational_signal",
            "medium aggregate",
            "diagnostic readiness risk",
        ),
        (
            "SRC_SAFETY_QUALITY_SIGNAL",
            "CANONICAL.VW_SYNTH_SAFETY_QUALITY_SIGNAL",
            "signal-day",
            "site_id, unit_or_program, signal_family, count, severity_proxy, review_status",
            "daily",
            "derived_operational_intelligence",
            "sensitive aggregate",
            "clinical surveillance synthetic-only panels",
        ),
        (
            "SRC_PUBLIC_RESPIRATORY",
            "OPEN_DATA.VW_SYNTH_RESPIRATORY_ACTIVITY",
            "region-week",
            "region_id, week_start, respiratory_activity_index, source_release_date",
            "weekly",
            "direct_operational_signal",
            "public open data",
            "seasonal context, surge multipliers",
        ),
        (
            "SRC_PUBLIC_WEATHER_AQHI",
            "OPEN_DATA.VW_SYNTH_WEATHER_AQHI",
            "region-day",
            "region_id, date, temperature_c, aqhi_max, smoke_flag",
            "daily",
            "direct_operational_signal",
            "public open data",
            "weather/smoke context",
        ),
        (
            "SRC_MODEL_OUTPUT",
            "MODEL.VW_SYNTH_MODEL_OUTPUT",
            "asset-output",
            "asset_id, output_ts, site_id, unit_or_program, score, threshold, explanation_json",
            "asset cadence",
            "modelled_predictive_ai_asset",
            "aggregate/model output",
            "predictive asset layer, warning logic",
        ),
        (
            "SRC_GOVERNANCE_EVENTS",
            "GOVERNANCE.VW_SYNTH_GOVERNANCE_EVENT",
            "governance event",
            "event_id, related_asset_id, event_type, status, decision, payload_json",
            "event-driven",
            "derived_operational_intelligence",
            "metadata only",
            "Gatekeeper control plane, evidence trail",
        ),
        (
            "SRC_LEARNING_MEMORY",
            "APP.VW_SYNTH_LEARNING_SYSTEM_EVENT",
            "learning event",
            "event_id, event_type, app_area, related_ids, status, severity, payload_json",
            "event-driven",
            "derived_operational_intelligence",
            "metadata only",
            "notes, acknowledgements, scenario memory",
        ),
    ]
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(definitions):
        source_id, view_name, grain, fields, cadence, classification, sensitivity, usage = item
        rows.append(
            {
                "source_id": source_id,
                "curated_view": view_name,
                "grain": grain,
                "fields": fields,
                "field_types": "synthetic ids, timestamps, categorical dimensions, numeric measures, JSON payloads",
                "cadence": cadence,
                "classification": classification,
                "phi_sensitivity": sensitivity,
                "dashboard_usage": usage,
                "validation_rules": "freshness, row count, timestamp logic, referential integrity, metric owner approval, small-cell suppression",
                "future_mapping_placeholder": f"CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_{index + 1:02d}",
            }
        )
    return rows


def direct_link_validation(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    review_sources = {"SRC_DIAGNOSTIC_DEPENDENCY", "SRC_TRANSFER_REQUEST", "SRC_PUBLIC_WEATHER_AQHI"}
    for index, source in enumerate(sources):
        status = "review" if source["source_id"] in review_sources else "ready"
        rows.append(
            {
                "source_id": source["source_id"],
                "source_view_present": "pass",
                "field_populated": "review" if status == "review" else "pass",
                "freshness": "review" if source["source_id"] == "SRC_PUBLIC_WEATHER_AQHI" else "pass",
                "row_count": "pass",
                "timestamp_logic": "review" if source["source_id"] == "SRC_TRANSFER_REQUEST" else "pass",
                "referential_integrity": "pass",
                "metric_definition_approved": "review" if source["source_id"] == "SRC_DIAGNOSTIC_DEPENDENCY" else "pass",
                "small_cell_suppression": "pass",
                "overall_readiness": status,
                "freshness_minutes": 15 + index * 6,
                "row_count_value": 1200 + index * 83,
                "owner": "Synthetic data product steward",
                "last_reviewed_at": NOW,
                "caveat": "Synthetic readiness demonstration; production use needs source-by-source signoff.",
            }
        )
    return rows


def metric_registry() -> list[dict[str, Any]]:
    metrics = [
        ("METRIC_OCCUPANCY", "Network occupancy", "sum(census) / sum(effective_beds)", "SRC_UNIT_CENSUS,SRC_BED_STATUS", "hourly", "Patient Flow", "approved", "direct"),
        ("METRIC_ED_BOARDING", "ED boarder hours", "sum(boarder_count * elapsed_hours)", "SRC_ED_BOARDING,SRC_ADT_ENCOUNTER", "15 minutes", "ED/Inpatient", "approved", "derived"),
        ("METRIC_DISCHARGE_RELIABILITY", "Discharge reliability", "completed_discharges_by_1600 / expected_discharges", "SRC_DISCHARGE_MILESTONE", "hourly", "Patient Flow", "approved", "derived"),
        ("METRIC_EFFECTIVE_STAFFED_BEDS", "Effective staffed beds", "physical_beds * staffing_factor * isolation_factor", "SRC_BED_STATUS,SRC_STAFFING_ROSTER,SRC_WORKLOAD_ACUITY", "hourly", "Operations", "approved", "derived"),
        ("METRIC_PICU_NICU_PRESSURE", "PICU/NICU pressure", "weighted occupancy + transfer demand + step-down constraint", "SRC_UNIT_CENSUS,SRC_TRANSFER_REQUEST", "hourly", "Critical Care", "review", "derived"),
        ("METRIC_OR_CANCELLATION_RISK", "OR cancellation risk", "post-op bed demand gap + PACU hold + staffing constraint", "SRC_OR_PACU,SRC_UNIT_CENSUS", "daily", "Perioperative", "approved", "modelled"),
        ("METRIC_WAITLIST_PRESSURE", "Waitlist pressure", "weighted over-target referrals by priority and age", "SRC_WAITLIST,SRC_REFERRAL", "weekly", "Ambulatory", "approved", "derived"),
        ("METRIC_THIRD_NEXT_AVAILABLE", "Third next available", "third open eligible appointment slot from clinic template", "SRC_CLINIC_TEMPLATE,SRC_APPOINTMENT", "weekly", "Ambulatory", "approved", "derived"),
        ("METRIC_NO_SHOW_GUARDRAIL", "No-show guardrail", "predicted missed visits constrained by equity and priority rules", "SRC_APPOINTMENT,SRC_REFERRAL", "daily", "Ambulatory", "review", "modelled"),
        ("METRIC_DIAGNOSTIC_READINESS", "Diagnostic readiness", "complete dependencies / required dependencies", "SRC_DIAGNOSTIC_DEPENDENCY", "daily", "Ambulatory", "review", "derived"),
        ("METRIC_SURVEILLANCE_WARNING", "Clinical surveillance warning", "synthetic signal above governed threshold", "SRC_SAFETY_QUALITY_SIGNAL,SRC_MODEL_OUTPUT", "daily", "Surveillance", "review", "modelled"),
        ("METRIC_GATEKEEPER_HEALTH", "Governance control health", "ready assets / active assets with unresolved issues weighted by severity", "SRC_GOVERNANCE_EVENTS,SRC_MODEL_OUTPUT", "event-driven", "Analytics Governance", "approved", "derived"),
    ]
    return [
        {
            "metric_id": metric_id,
            "name": name,
            "formula": formula,
            "source_fields": sources,
            "cadence": cadence,
            "owner": owner,
            "validation": validation,
            "caveat": "Synthetic metric card; local definition review required before production adoption.",
            "reviewed_date": "2026-06-11",
            "classification": classification,
        }
        for metric_id, name, formula, sources, cadence, owner, validation, classification in metrics
    ]


def model_registry() -> list[dict[str, Any]]:
    assets = [
        ("INPT_OCCUPANCY_FORECAST", "Inpatient occupancy forecast", "Operational", "probability and interval", "Active; governed threshold"),
        ("ED_BOARDING_FORECAST", "ED boarding forecast", "Operational", "hourly boarder-hour forecast", "Active; monitored"),
        ("DISCHARGE_BY_TIME_BAND", "Discharge by time-band", "Operational", "same-day probability", "Validation hold"),
        ("PICU_NICU_PRESSURE", "PICU/NICU pressure", "Operational", "critical care pressure score", "Active; executive warning"),
        ("OR_CANCELLATION_RISK", "OR cancellation risk", "Operational", "case-day risk score", "Review before alerting"),
        ("AMB_REFERRAL_DEMAND_FORECAST", "Ambulatory referral demand forecast", "Operational", "weekly demand forecast", "Active; planning only"),
        ("AMB_BACKLOG_FORECAST", "Ambulatory backlog forecast", "Operational", "waitlist projection", "Active; planning only"),
        ("NO_SHOW_LATE_CANCEL_RISK", "No-show and late-cancel risk", "Operational", "appointment risk score", "Guardrailed; no individual action"),
        ("URGENT_WAITLIST_BREACH_RISK", "Urgent waitlist breach risk", "Operational", "program-week probability", "Active; huddle review"),
        ("DIAGNOSTIC_READINESS_RISK", "Diagnostic readiness risk", "Operational", "dependency gap score", "Validation hold"),
        ("PEDIATRIC_EARLY_WARNING_SIGNAL", "Pediatric early warning signal", "Clinical surveillance synthetic-only", "unit-day warning", "Synthetic only; not clinical"),
        ("SEPSIS_SURVEILLANCE_SIGNAL", "Sepsis surveillance signal", "Clinical surveillance synthetic-only", "surveillance flag", "Synthetic only; warning label"),
        ("RARE_DISEASE_CASE_FINDING_SIGNAL", "Rare disease case-finding signal", "Clinical surveillance synthetic-only", "evidence-trail candidate", "Synthetic only; small-cell protected"),
        ("READMISSION_REVISIT_RISK", "Readmission/revisit risk", "Clinical surveillance synthetic-only", "aggregate risk band", "Synthetic only; program review"),
        ("LONG_STAY_RISK", "Long-stay risk", "Clinical surveillance synthetic-only", "encounter cohort risk", "Synthetic only; no direct care use"),
    ]
    rows: list[dict[str, Any]] = []
    for index, (asset_id, name, domain, output_type, deploy_status) in enumerate(assets):
        rows.append(
            {
                "asset_id": asset_id,
                "name": name,
                "domain": domain,
                "output_type": output_type,
                "intended_use": "Synthetic operational planning, governance rehearsal, and model-card demonstration.",
                "not_intended_use": "No clinical diagnosis, treatment, triage, staffing directive, or automated Connect Care action.",
                "source_data": "Curated synthetic Snowflake views; no raw EHR tables and no direct identifiers.",
                "features": "occupancy, bed status, ADT timing, discharge barriers, staffing, public context, ambulatory demand, governed synthetic safety signals",
                "model_class": ["gradient boosted trees", "Bayesian hierarchical forecast", "queueing simulation", "rules plus calibrated score"][index % 4],
                "training_config_window": "2024-07-01 to 2026-03-31 synthetic",
                "validation_window": "2026-04-01 to 2026-06-10 synthetic backtest",
                "cadence": ["hourly", "daily", "weekly"][index % 3],
                "calibration_status": "synthetic-calibrated" if index % 5 else "review required",
                "drift_status": "stable" if index % 4 else "watch",
                "subgroup_performance": "reviewed across site, age-band, program, priority, and season proxies",
                "thresholds": "warning threshold set by governance registry; huddle acknowledgement required for high severity",
                "alert_burden": f"{3 + index % 6} expected aggregate warnings/week in synthetic replay",
                "false_positive_false_negative_review": "synthetic adjudication notes available in governance evidence trail",
                "governance_status": "approved for demo" if index % 3 else "review queued",
                "deployment_status": deploy_status,
                "owner": "Synthetic analytics product owner",
                "sponsor": "Provincial pediatric operations sponsor",
                "last_reviewed": "2026-06-11",
                "next_review": "2026-07-11",
                "panels": "system posture, domain dashboard, Gatekeeper control plane",
                "warnings": "All outputs marked synthetic-only and not validated for clinical decision-making.",
                "caveats": "Requires local validation, subgroup calibration, alert-burden review, and rollback plan.",
                "fallback": "Hide warning layer and revert to direct/derived operational metrics.",
                "rollback_plan": "Disable asset flag in CONFIG.MODEL_DEPLOYMENT_REGISTRY and remove panel warning widgets.",
                "related_outputs": "panel lineage, source readiness, scenario lab, learning-system event log",
                "evidence_trail": f"GOV-EVID-{index + 1:03d}",
                "synthetic_evidence": f"Backtest replay, calibration card, drift check, and reviewer note set {index + 1:02d}.",
            }
        )
    return rows


def panel_lineage() -> list[dict[str, Any]]:
    panels = [
        ("PANEL_SYSTEM_POSTURE", "Today pediatric system posture", "System Posture", "derived", "SRC_UNIT_CENSUS,SRC_ED_BOARDING,SRC_WAITLIST,SRC_MODEL_OUTPUT", "METRIC_OCCUPANCY,METRIC_ED_BOARDING,METRIC_WAITLIST_PRESSURE", "INPT_OCCUPANCY_FORECAST,PICU_NICU_PRESSURE"),
        ("PANEL_INPATIENT_COMMAND", "Inpatient command", "Inpatient Intelligence", "derived", "SRC_UNIT_CENSUS,SRC_BED_STATUS,SRC_DISCHARGE_MILESTONE,SRC_OR_PACU", "METRIC_OCCUPANCY,METRIC_DISCHARGE_RELIABILITY,METRIC_EFFECTIVE_STAFFED_BEDS", "INPT_OCCUPANCY_FORECAST,ED_BOARDING_FORECAST,DISCHARGE_BY_TIME_BAND"),
        ("PANEL_AMBULATORY_COMMAND", "Ambulatory command", "Ambulatory Access Intelligence", "derived", "SRC_REFERRAL,SRC_WAITLIST,SRC_CLINIC_TEMPLATE,SRC_APPOINTMENT", "METRIC_WAITLIST_PRESSURE,METRIC_THIRD_NEXT_AVAILABLE,METRIC_NO_SHOW_GUARDRAIL", "AMB_BACKLOG_FORECAST,NO_SHOW_LATE_CANCEL_RISK,URGENT_WAITLIST_BREACH_RISK"),
        ("PANEL_PREDICTIVE_ASSETS", "Clinical surveillance and predictive assets", "Predictive Asset Layer", "modelled", "SRC_SAFETY_QUALITY_SIGNAL,SRC_MODEL_OUTPUT", "METRIC_SURVEILLANCE_WARNING", "PEDIATRIC_EARLY_WARNING_SIGNAL,SEPSIS_SURVEILLANCE_SIGNAL,RARE_DISEASE_CASE_FINDING_SIGNAL,READMISSION_REVISIT_RISK,LONG_STAY_RISK"),
        ("PANEL_SCENARIO_LAB", "Scenario simulation lab", "Scenario Simulation Lab", "modelled", "SRC_UNIT_CENSUS,SRC_WAITLIST,SRC_STAFFING_ROSTER,SRC_PUBLIC_RESPIRATORY", "METRIC_OCCUPANCY,METRIC_WAITLIST_PRESSURE", "INPT_OCCUPANCY_FORECAST,AMB_BACKLOG_FORECAST"),
        ("PANEL_GATEKEEPER", "AHA Gatekeeper control plane", "AHA Gatekeeper Control Plane", "derived", "SRC_GOVERNANCE_EVENTS,SRC_MODEL_OUTPUT,SRC_LEARNING_MEMORY", "METRIC_GATEKEEPER_HEALTH", "all active assets"),
        ("PANEL_MEMORY", "Learning-system memory", "Learning System Memory", "derived", "SRC_LEARNING_MEMORY,SRC_GOVERNANCE_EVENTS", "METRIC_GATEKEEPER_HEALTH", "scenario and acknowledgement outputs"),
        ("PANEL_WIRING", "Future real-data wiring", "Future Real-Data Wiring", "direct", "all curated source placeholders", "source-readiness stoplight", "no model dependency"),
    ]
    rows: list[dict[str, Any]] = []
    for index, (panel_id, title, app_area, classification, sources, metrics, models) in enumerate(panels):
        rows.append(
            {
                "panel_id": panel_id,
                "title": title,
                "app_area": app_area,
                "classification": classification,
                "source_view_ids": sources,
                "metric_ids": metrics,
                "model_ids": models,
                "freshness": "15-90 minutes synthetic replay",
                "readiness_status": "ready" if index not in {2, 3} else "review",
                "confidence": ["high", "medium-high", "medium", "review"][index % 4],
                "caveat": "Synthetic demonstration data; not validated for clinical decision-making.",
                "lineage_summary": "Direct source readiness feeds derived metrics; modelled outputs carry model cards, warning labels, and rollback paths.",
            }
        )
    return rows


def system_posture() -> dict[str, Any]:
    kpis = [
        {"label": "Network occupancy", "value": "93.4%", "detail": "Effective staffed beds across synthetic pediatric network", "delta": "+2.8 pts", "tone": "watch", "panel_id": "PANEL_SYSTEM_POSTURE"},
        {"label": "ED boarder hours", "value": "186", "detail": "Next 24h forecast, synthetic", "delta": "+21", "tone": "high", "panel_id": "PANEL_SYSTEM_POSTURE"},
        {"label": "Ambulatory backlog", "value": "8,940", "detail": "Waitlist records in aggregate synthetic marts", "delta": "+4.6%", "tone": "watch", "panel_id": "PANEL_AMBULATORY_COMMAND"},
        {"label": "Governed active assets", "value": "15", "detail": "Model cards with review state and fallback", "delta": "3 review", "tone": "neutral", "panel_id": "PANEL_GATEKEEPER"},
    ]
    posture_cards = [
        {"label": "Why this changed", "value": "Respiratory + staffing + discharge reliability", "detail": "Occupancy moved because effective beds fell while respiratory demand and discharge barriers rose.", "tone": "watch"},
        {"label": "Huddle mode", "value": "3 decisions", "detail": "Protect PICU step-down, advance discharge barriers, add urgent ambulatory slots.", "tone": "steady"},
        {"label": "Readiness overlay", "value": "17 ready / 3 review", "detail": "Diagnostic dependency, transfers, and weather/AQHI need source-owner review.", "tone": "watch"},
        {"label": "Learning memory", "value": "12 events this week", "detail": "Scenario runs, warning acknowledgements, issue flags, and governance decisions are captured.", "tone": "steady"},
    ]
    why_changed = [
        {"driver": "Respiratory activity", "change": "+7.2%", "contribution": 34, "evidence": "OPEN_DATA.VW_SYNTH_RESPIRATORY_ACTIVITY rose above seasonal baseline."},
        {"driver": "Effective staffed beds", "change": "-11 beds", "contribution": 29, "evidence": "CANONICAL.VW_SYNTH_STAFFING_ROSTER shows skill-mix gaps in PICU/NICU and respiratory units."},
        {"driver": "Discharge reliability", "change": "-4.8 pts", "contribution": 22, "evidence": "Discharge milestone barriers concentrated in pharmacy, transport, and family readiness."},
        {"driver": "Ambulatory diagnostic readiness", "change": "-6.1 pts", "contribution": 15, "evidence": "Dependency completion lag affects complex care and neurology backlogs."},
    ]
    return {"kpis": kpis, "postureCards": posture_cards, "whyChanged": why_changed}


def inpatient_payload() -> dict[str, list[dict[str, Any]]]:
    unit_rows: list[dict[str, Any]] = []
    units = [
        ("Respiratory", 0.99, 0.12, 16, "review"),
        ("General pediatrics", 0.94, 0.08, 11, "ready"),
        ("PICU", 0.96, 0.10, 5, "review"),
        ("NICU", 0.90, 0.06, 3, "ready"),
        ("Surgery", 0.86, 0.04, 2, "ready"),
        ("Mental health", 0.92, 0.09, 4, "ready"),
    ]
    for site_id, site_name, _ in SITES:
        for unit, occupancy, staffing_gap, boarders, readiness in units:
            unit_rows.append(
                {
                    "site_id": site_id,
                    "site_name": site_name,
                    "unit_name": unit,
                    "occupancy_pct": occupancy + (0.015 if site_id == "SITE_STOLLERY_INSPIRED" else -0.008 if site_id == "SITE_ACH_INSPIRED" else 0),
                    "staffing_gap_pct": staffing_gap,
                    "ed_boarders": boarders,
                    "effective_beds_lost": round(staffing_gap * 42),
                    "source_readiness": readiness,
                    "classification": "derived",
                    "freshness": "15 min",
                    "confidence": "medium-high",
                    "caveat": "Synthetic unit pressure; small cells suppressed.",
                    "lineage_panel_id": "PANEL_INPATIENT_COMMAND",
                }
            )
    flow_drivers = [
        {"driver": "Pharmacy discharge barrier", "active_count": 38, "median_age_hours": 17.2, "readiness": "ready", "classification": "derived"},
        {"driver": "Transport and portering", "active_count": 31, "median_age_hours": 13.5, "readiness": "ready", "classification": "derived"},
        {"driver": "Family readiness", "active_count": 26, "median_age_hours": 22.1, "readiness": "ready", "classification": "derived"},
        {"driver": "PICU step-down constraint", "active_count": 14, "median_age_hours": 29.4, "readiness": "review", "classification": "derived"},
    ]
    forecast = [
        {"horizon_hours": horizon, "occupancy_forecast": round(0.92 + index * 0.012, 3), "p10": round(0.87 + index * 0.01, 3), "p90": round(0.98 + index * 0.015, 3), "prob_above_95": round(0.36 + index * 0.09, 3), "asset_id": "INPT_OCCUPANCY_FORECAST"}
        for index, horizon in enumerate([6, 12, 24, 48, 72])
    ]
    warnings = [
        {"warning_id": "WARN-INPT-001", "severity": "high", "asset_id": "PICU_NICU_PRESSURE", "message": "PICU/NICU pressure above governed synthetic threshold; review transfer-in and step-down queue.", "status": "acknowledgement required"},
        {"warning_id": "WARN-INPT-002", "severity": "medium", "asset_id": "DISCHARGE_BY_TIME_BAND", "message": "16:00 discharge confidence below synthetic target; review pharmacy and transport barriers.", "status": "open"},
    ]
    return {"unitPressure": unit_rows, "flowDrivers": flow_drivers, "forecast": forecast, "warnings": warnings}


def ambulatory_payload() -> dict[str, list[dict[str, Any]]]:
    programs = [
        ("Complex care", 1480, 71, 0.34, 0.78, "review"),
        ("Neurology", 1320, 86, 0.41, 0.72, "review"),
        ("Cardiology", 940, 49, 0.19, 0.87, "ready"),
        ("Respiratory", 1185, 58, 0.28, 0.84, "ready"),
        ("Surgery follow-up", 1615, 64, 0.26, 0.81, "ready"),
        ("Mental health", 1210, 91, 0.47, 0.69, "review"),
        ("Diagnostic procedures", 1190, 76, 0.39, 0.64, "review"),
    ]
    access: list[dict[str, Any]] = []
    frontier: list[dict[str, Any]] = []
    for program, waitlist, tna, breach, readiness, source_ready in programs:
        access.append(
            {
                "program": program,
                "waitlist_total": waitlist,
                "third_next_available_days": tna,
                "urgent_breach_risk": breach,
                "diagnostic_readiness": readiness,
                "source_readiness": source_ready,
                "classification": "derived",
                "freshness": "weekly plus daily referral delta",
                "confidence": "medium",
                "caveat": "Synthetic aggregate access metrics; no patient-level display.",
                "lineage_panel_id": "PANEL_AMBULATORY_COMMAND",
            }
        )
        frontier.append(
            {
                "program": program,
                "guarded_overbook_pct": round(0.03 + breach * 0.09, 3),
                "expected_recovered_slots": round(waitlist * (0.018 + breach * 0.012)),
                "equity_guardrail": "requires review" if breach > 0.38 else "within guardrail",
                "no_show_risk": round(0.07 + breach * 0.18, 3),
                "asset_id": "NO_SHOW_LATE_CANCEL_RISK",
            }
        )
    forecast = [
        {"horizon_weeks": week, "backlog_forecast": 9100 + week * 18 - (120 if week >= 8 else 0), "p10": 8700 + week * 10, "p90": 9600 + week * 28, "asset_id": "AMB_BACKLOG_FORECAST"}
        for week in [1, 2, 4, 8, 13, 26]
    ]
    warnings = [
        {"warning_id": "WARN-AMB-001", "severity": "medium", "asset_id": "URGENT_WAITLIST_BREACH_RISK", "message": "Neurology and mental health urgent breach risk exceeds synthetic huddle threshold.", "status": "open"},
        {"warning_id": "WARN-AMB-002", "severity": "medium", "asset_id": "DIAGNOSTIC_READINESS_RISK", "message": "Diagnostic readiness is constraining complex care and diagnostic procedure access.", "status": "validation hold"},
    ]
    return {"programAccess": access, "noShowFrontier": frontier, "forecast": forecast, "warnings": warnings}


def predictive_assets_payload() -> dict[str, list[dict[str, Any]]]:
    signals = [
        {"signal_id": "SIG-PEWS-001", "asset_id": "PEDIATRIC_EARLY_WARNING_SIGNAL", "unit_or_program": "Respiratory", "score": 0.76, "threshold": 0.70, "severity": "medium", "readiness": "review", "classification": "modelled"},
        {"signal_id": "SIG-SEPSIS-001", "asset_id": "SEPSIS_SURVEILLANCE_SIGNAL", "unit_or_program": "PICU", "score": 0.64, "threshold": 0.62, "severity": "high", "readiness": "review", "classification": "modelled"},
        {"signal_id": "SIG-RARE-001", "asset_id": "RARE_DISEASE_CASE_FINDING_SIGNAL", "unit_or_program": "Complex care", "score": 0.58, "threshold": 0.55, "severity": "low", "readiness": "synthetic only", "classification": "modelled"},
        {"signal_id": "SIG-READMIT-001", "asset_id": "READMISSION_REVISIT_RISK", "unit_or_program": "General pediatrics", "score": 0.31, "threshold": 0.28, "severity": "medium", "readiness": "review", "classification": "modelled"},
        {"signal_id": "SIG-LONGSTAY-001", "asset_id": "LONG_STAY_RISK", "unit_or_program": "Surgery", "score": 0.44, "threshold": 0.40, "severity": "medium", "readiness": "review", "classification": "modelled"},
    ]
    evidence = [
        {"trail_id": "EVID-SEPSIS-001", "asset_id": "SEPSIS_SURVEILLANCE_SIGNAL", "evidence_step": "Governed threshold crossed", "detail": "Aggregate synthetic signal rose above threshold; display warning label and require acknowledgement."},
        {"trail_id": "EVID-SEPSIS-001", "asset_id": "SEPSIS_SURVEILLANCE_SIGNAL", "evidence_step": "False positive review", "detail": "Synthetic replay shows 2 high-burden weeks; threshold review is queued."},
        {"trail_id": "EVID-RARE-001", "asset_id": "RARE_DISEASE_CASE_FINDING_SIGNAL", "evidence_step": "Small-cell protection", "detail": "Candidate counts are suppressed and displayed only as evidence-trail status."},
    ]
    return {"signals": signals, "evidenceTrails": evidence}


def scenario_lab_payload() -> dict[str, list[dict[str, Any]]]:
    scenarios = [
        {"scenario_id": "SCN-INPT-001", "domain": "inpatient", "scenario_name": "Protect PICU step-down beds", "impact_score": 88, "effort_score": 3.4, "operational_risk_score": 2.2, "primary_outcome": "boarder_hours", "outcome_value": 128, "readiness": "review", "classification": "modelled", "writeback_table": "APP.SCENARIO_RUN_LOG"},
        {"scenario_id": "SCN-INPT-002", "domain": "inpatient", "scenario_name": "Pharmacy discharge acceleration", "impact_score": 76, "effort_score": 2.8, "operational_risk_score": 1.8, "primary_outcome": "boarder_hours", "outcome_value": 142, "readiness": "ready", "classification": "modelled", "writeback_table": "APP.SCENARIO_RUN_LOG"},
        {"scenario_id": "SCN-INPT-003", "domain": "inpatient", "scenario_name": "Respiratory surge bed conversion", "impact_score": 81, "effort_score": 4.2, "operational_risk_score": 3.1, "primary_outcome": "occupancy_pct", "outcome_value": 91, "readiness": "review", "classification": "modelled", "writeback_table": "APP.SCENARIO_RUN_LOG"},
        {"scenario_id": "SCN-AMB-001", "domain": "ambulatory", "scenario_name": "Urgent slot protection", "impact_score": 84, "effort_score": 2.7, "operational_risk_score": 1.6, "primary_outcome": "backlog", "outcome_value": 8060, "readiness": "ready", "classification": "modelled", "writeback_table": "APP.SCENARIO_RUN_LOG"},
        {"scenario_id": "SCN-AMB-002", "domain": "ambulatory", "scenario_name": "No-show guardrail overbooking", "impact_score": 72, "effort_score": 2.3, "operational_risk_score": 2.5, "primary_outcome": "recovered_slots", "outcome_value": 214, "readiness": "review", "classification": "modelled", "writeback_table": "APP.SCENARIO_RUN_LOG"},
        {"scenario_id": "SCN-AMB-003", "domain": "ambulatory", "scenario_name": "Diagnostic readiness huddle", "impact_score": 79, "effort_score": 3.1, "operational_risk_score": 1.9, "primary_outcome": "ready_referrals", "outcome_value": 398, "readiness": "review", "classification": "modelled", "writeback_table": "APP.SCENARIO_RUN_LOG"},
    ]
    comparisons = [
        {"comparison_id": "CMP-001", "name": "Flow reliability bundle", "baseline": "186 boarder hours", "scenario": "128 boarder hours", "decision": "candidate for huddle review"},
        {"comparison_id": "CMP-002", "name": "Access recovery bundle", "baseline": "8,940 backlog", "scenario": "8,060 backlog", "decision": "candidate for program review"},
    ]
    return {"scenarios": scenarios, "comparisons": comparisons}


def gatekeeper_payload(models: list[dict[str, Any]], sources: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    control = [
        {"area": "Direct source readiness", "ready": 17, "review": 3, "blocked": 0, "mode": "executive lite"},
        {"area": "Metric definitions", "ready": 9, "review": 3, "blocked": 0, "mode": "technical deep"},
        {"area": "Model cards", "ready": 10, "review": 5, "blocked": 0, "mode": "technical deep"},
        {"area": "Warning logic", "ready": 6, "review": 4, "blocked": 0, "mode": "executive lite"},
        {"area": "Learning writebacks", "ready": 10, "review": 0, "blocked": 0, "mode": "technical deep"},
    ]
    dependencies: list[dict[str, Any]] = []
    for source in sources[:10]:
        dependencies.append({"from": source["source_id"], "to": "PANEL_SYSTEM_POSTURE", "relationship": "feeds direct readiness"})
    for model in models:
        dependencies.append({"from": model["asset_id"], "to": "PANEL_PREDICTIVE_ASSETS", "relationship": "governed output"})
    issues = [
        {"issue_id": "ISSUE-001", "severity": "medium", "related_id": "SRC_DIAGNOSTIC_DEPENDENCY", "status": "open", "note": "Definition owner must approve diagnostic readiness denominator."},
        {"issue_id": "ISSUE-002", "severity": "high", "related_id": "SEPSIS_SURVEILLANCE_SIGNAL", "status": "review queued", "note": "Alert-burden review required before public warning display."},
        {"issue_id": "ISSUE-003", "severity": "medium", "related_id": "NO_SHOW_LATE_CANCEL_RISK", "status": "guardrail review", "note": "Equity and travel-burden guardrail needs signoff before scenario promotion."},
    ]
    approvals = [
        {"decision_id": "GOV-DEC-001", "related_id": "INPT_OCCUPANCY_FORECAST", "decision": "approved for demo", "reviewer_role": "analytics governance", "created_at": NOW},
        {"decision_id": "GOV-DEC-002", "related_id": "PICU_NICU_PRESSURE", "decision": "approved with warning label", "reviewer_role": "operations sponsor", "created_at": NOW},
        {"decision_id": "GOV-DEC-003", "related_id": "SEPSIS_SURVEILLANCE_SIGNAL", "decision": "synthetic-only hold", "reviewer_role": "clinical safety reviewer", "created_at": NOW},
    ]
    return {"controlPlane": control, "dependencyEdges": dependencies, "issues": issues, "approvals": approvals}


def learning_memory_payload() -> dict[str, list[dict[str, Any]]]:
    tables = [
        "APP.SCENARIO_RUN_LOG",
        "APP.USER_ANNOTATION",
        "APP.WARNING_ACKNOWLEDGEMENT",
        "APP.METRIC_ISSUE_FLAG",
        "APP.MODEL_REVIEW_NOTE",
        "APP.GOVERNANCE_DECISION",
        "APP.VALIDATION_REVIEW",
        "APP.PANEL_FEEDBACK",
        "APP.HUDDLE_REVIEW_EVENT",
        "APP.LEARNING_SYSTEM_OUTCOME_REVIEW",
    ]
    events = [
        ("EVT-001", "scenario_run", "Scenario Simulation Lab", "SCN-INPT-001", "complete", "medium", "PICU step-down scenario reduced synthetic boarder hours."),
        ("EVT-002", "warning_acknowledgement", "Inpatient Intelligence", "WARN-INPT-001", "acknowledged", "high", "Operations huddle acknowledged PICU/NICU warning."),
        ("EVT-003", "metric_issue_flag", "Ambulatory Access Intelligence", "METRIC_DIAGNOSTIC_READINESS", "open", "medium", "Diagnostic readiness denominator requires owner review."),
        ("EVT-004", "model_review_note", "Predictive Asset Layer", "SEPSIS_SURVEILLANCE_SIGNAL", "review queued", "high", "Synthetic surveillance warning remains not clinical-use."),
        ("EVT-005", "governance_decision", "AHA Gatekeeper Control Plane", "PICU_NICU_PRESSURE", "approved with caveat", "medium", "Warning label and rollback path required."),
        ("EVT-006", "panel_feedback", "System Posture", "PANEL_SYSTEM_POSTURE", "complete", "low", "Executive mode should keep stoplight overlay visible."),
    ]
    rows: list[dict[str, Any]] = []
    for index, (event_id, event_type, app_area, related_id, status, severity, note) in enumerate(events):
        rows.append(
            {
                "event_id": event_id,
                "event_type": event_type,
                "created_at": NOW,
                "created_by": "synthetic_snowflake_user",
                "app_area": app_area,
                "site_id": SITES[index % len(SITES)][0],
                "unit_or_program": ["PICU", "Respiratory", "Complex care", "Network", "Neurology", "System"][index],
                "related_ids": related_id,
                "status": status,
                "severity": severity,
                "note": note,
                "payload_json": json.dumps({"synthetic_demo": True, "source": "v3 generator", "event_table": tables[index % len(tables)]}),
                "synthetic_demo_flag": True,
                "writeback_table": tables[index % len(tables)],
            }
        )
    return {"events": rows, "writebackTables": [{"table_name": table, "required": True, "status": "defined"} for table in tables]}


def future_wiring_payload(sources: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    phases = [
        {"phase": "1. Read-only curated views", "scope": "Census, ADT events, bed status, waitlist snapshots, referral demand", "governance_gate": "source readiness stoplight all green"},
        {"phase": "2. Derived marts", "scope": "Metric registry, coefficient registry, operational marts, quality checks", "governance_gate": "metric owner review and small-cell suppression"},
        {"phase": "3. Modelled assets", "scope": "Forecasts, warning logic, scenario coefficients, model cards", "governance_gate": "validation, calibration, alert-burden, rollback"},
        {"phase": "4. Learning writeback", "scope": "Scenario runs, annotations, acknowledgements, review decisions, outcome reviews", "governance_gate": "Snowflake APP/GOVERNANCE write privileges and audit policy"},
    ]
    mappings = [
        {
            "source_id": source["source_id"],
            "future_mapping_placeholder": source["future_mapping_placeholder"],
            "first_validation": "source view present, fields populated, freshness, row count",
            "production_note": "Map only through curated governed views; never hardcode confidential operational table names.",
        }
        for source in sources
    ]
    return {"phases": phases, "mappings": mappings}


def main() -> None:
    sources = source_registry()
    readiness = direct_link_validation(sources)
    metrics = metric_registry()
    models = model_registry()
    lineage = panel_lineage()
    posture = system_posture()
    inpatient = inpatient_payload()
    ambulatory = ambulatory_payload()
    predictive = predictive_assets_payload()
    scenarios = scenario_lab_payload()
    gatekeeper = gatekeeper_payload(models, sources)
    memory = learning_memory_payload()
    wiring = future_wiring_payload(sources)

    metadata = {
        "appVersion": "v3.0",
        "generatedAt": NOW,
        "mode": "Synthetic demonstration data",
        "clinicalUse": "Not validated for clinical decision-making",
        "historyWindow": "Synthetic 24-month operating-layer replay",
        "sourceBoundary": "Future real data maps through curated governed Snowflake views only.",
        "productName": "Provincial Pediatric Acute Care Intelligence Operating Layer",
    }

    write_json("metadata.json", metadata)
    write_json("source_registry.json", {"rows": sources})
    write_json("direct_link_validation.json", {"rows": readiness})
    write_json("metric_registry.json", {"rows": metrics})
    write_json("model_registry.json", {"rows": models})
    write_json("panel_lineage.json", {"rows": lineage})
    write_json("system_posture.json", posture)
    write_json("inpatient_intelligence.json", inpatient)
    write_json("ambulatory_intelligence.json", ambulatory)
    write_json("predictive_assets.json", predictive)
    write_json("scenario_lab.json", scenarios)
    write_json("gatekeeper_control_plane.json", gatekeeper)
    write_json("learning_system_memory.json", memory)
    write_json("future_real_data_wiring.json", wiring)

    write_csv("v3_source_registry.csv", sources)
    write_csv("v3_direct_link_validation.csv", readiness)
    write_csv("v3_metric_registry.csv", metrics)
    write_csv("v3_model_registry.csv", models)
    write_csv("v3_panel_lineage.csv", lineage)
    write_csv("v3_learning_system_events.csv", memory["events"])
    write_csv("v3_gatekeeper_issues.csv", gatekeeper["issues"])
    write_csv("v3_scenarios.csv", scenarios["scenarios"])
    write_csv("v3_inpatient_unit_pressure.csv", inpatient["unitPressure"])
    write_csv("v3_ambulatory_program_access.csv", ambulatory["programAccess"])
    print(f"Wrote v3 frontier assets to {OUT}")


if __name__ == "__main__":
    main()
