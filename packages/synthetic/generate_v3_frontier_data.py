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

SOURCE_GROUPS: list[dict[str, Any]] = [
    {
        "domain": "core encounter / movement",
        "schema": "CANONICAL",
        "classification": "direct_operational_signal",
        "sensitivity": "high aggregate only",
        "cadence": "15 minutes to hourly",
        "usage": "inpatient posture, ED-to-inpatient pressure, transfer flow, isolation and level-of-care constraints",
        "views": [
            "VW_SYNTH_ADT_EVENTS",
            "VW_SYNTH_INPATIENT_ENCOUNTERS",
            "VW_SYNTH_ED_VISITS",
            "VW_SYNTH_BED_STATUS",
            "VW_SYNTH_UNIT_CENSUS_HOURLY",
            "VW_SYNTH_TRANSFER_REQUESTS",
            "VW_SYNTH_PATIENT_CLASS_STATUS",
            "VW_SYNTH_LEVEL_OF_CARE",
            "VW_SYNTH_ISOLATION_STATUS",
        ],
    },
    {
        "domain": "orders / results / clinical process",
        "schema": "CANONICAL",
        "classification": "direct_operational_signal",
        "sensitivity": "sensitive aggregate",
        "cadence": "15 minutes to daily",
        "usage": "diagnostic readiness, discharge readiness, surveillance feature families, care-plan milestone context",
        "views": [
            "VW_SYNTH_ORDERS",
            "VW_SYNTH_LAB_RESULTS",
            "VW_SYNTH_IMAGING_ORDERS",
            "VW_SYNTH_MEDICATION_ORDERS",
            "VW_SYNTH_MAR_ADMINISTRATION",
            "VW_SYNTH_RESPIRATORY_SUPPORT",
            "VW_SYNTH_VITAL_SIGNS_AGG",
            "VW_SYNTH_CLINICAL_SCORES",
            "VW_SYNTH_SEPSIS_SCREENING",
            "VW_SYNTH_ALERT_EVENTS",
            "VW_SYNTH_CARE_PLAN_MILESTONES",
        ],
    },
    {
        "domain": "discharge",
        "schema": "CANONICAL",
        "classification": "direct_operational_signal",
        "sensitivity": "high aggregate only",
        "cadence": "hourly",
        "usage": "discharge reliability, predicted discharge capacity, barrier ageing, why-this-changed panels",
        "views": [
            "VW_SYNTH_DISCHARGE_MILESTONES",
            "VW_SYNTH_DISCHARGE_BARRIERS",
            "VW_SYNTH_PHARMACY_DISCHARGE_MED_STATUS",
            "VW_SYNTH_HOME_SUPPORT_STATUS",
            "VW_SYNTH_EQUIPMENT_STATUS",
            "VW_SYNTH_TRANSPORT_STATUS",
            "VW_SYNTH_FAMILY_READINESS_PROXY",
        ],
    },
    {
        "domain": "procedural",
        "schema": "CANONICAL",
        "classification": "direct_operational_signal",
        "sensitivity": "medium aggregate",
        "cadence": "daily plus intra-day updates",
        "usage": "OR/PACU pressure, post-op bed demand, cancellation risk, smoothing scenarios",
        "views": [
            "VW_SYNTH_OR_CASES",
            "VW_SYNTH_PACU_EVENTS",
            "VW_SYNTH_PROCEDURE_SCHEDULE",
            "VW_SYNTH_PROCEDURE_CANCELLATIONS",
            "VW_SYNTH_POST_OP_BED_DEMAND",
        ],
    },
    {
        "domain": "ambulatory",
        "schema": "CANONICAL",
        "classification": "direct_operational_signal",
        "sensitivity": "high aggregate only",
        "cadence": "daily to weekly",
        "usage": "referral demand, triage, waitlists, access, no-show reliability, diagnostics, virtual/outreach capacity",
        "views": [
            "VW_SYNTH_REFERRALS",
            "VW_SYNTH_REFERRAL_TRIAGE",
            "VW_SYNTH_WAITLIST_SNAPSHOTS",
            "VW_SYNTH_APPOINTMENTS",
            "VW_SYNTH_CLINIC_SLOTS",
            "VW_SYNTH_CLINIC_TEMPLATES",
            "VW_SYNTH_PROVIDER_AVAILABILITY",
            "VW_SYNTH_NO_SHOW_LATE_CANCEL",
            "VW_SYNTH_OVERDUE_FOLLOWUP",
            "VW_SYNTH_DIAGNOSTIC_READINESS",
            "VW_SYNTH_VIRTUAL_CARE_SUITABILITY",
            "VW_SYNTH_OUTREACH_CLINIC_CAPACITY",
        ],
    },
    {
        "domain": "staffing / workload",
        "schema": "CANONICAL",
        "classification": "direct_operational_signal",
        "sensitivity": "staff aggregate",
        "cadence": "shift to daily",
        "usage": "effective staffed beds, skill-mix constraint, workload pressure, surge staffing scenarios",
        "views": [
            "VW_SYNTH_STAFFING_ROSTER",
            "VW_SYNTH_STAFFING_GAPS",
            "VW_SYNTH_WORKLOAD_ACUITY",
            "VW_SYNTH_SKILL_MIX",
            "VW_SYNTH_FLOAT_POOL_AVAILABILITY",
        ],
    },
    {
        "domain": "safety / quality",
        "schema": "CANONICAL",
        "classification": "derived_operational_intelligence",
        "sensitivity": "sensitive aggregate",
        "cadence": "daily",
        "usage": "clinical-surveillance synthetic-only panels, readmission/revisit, documentation completeness, data-quality events",
        "views": [
            "VW_SYNTH_SAFETY_EVENTS_AGG",
            "VW_SYNTH_READMISSION_REVISIT",
            "VW_SYNTH_DOT_PHRASE_OR_DOC_COMPLETENESS_PROXY",
            "VW_SYNTH_DATA_QUALITY_EVENTS",
        ],
    },
    {
        "domain": "open data",
        "schema": "OPEN_DATA",
        "classification": "direct_operational_signal",
        "sensitivity": "public open data",
        "cadence": "daily to weekly",
        "usage": "respiratory/weather context, population denominator, calendar/school effects, community demand proxy",
        "views": [
            "VW_OPEN_RESPIRATORY_ACTIVITY",
            "VW_OPEN_WEATHER_AQHI",
            "VW_OPEN_POPULATION_DEMOGRAPHICS",
            "VW_OPEN_CALENDAR_HOLIDAY_SCHOOL",
            "VW_OPEN_COMMUNITY_DEMAND_PROXY",
        ],
    },
    {
        "domain": "model / governance / learning",
        "schema": "GOVERNANCE",
        "classification": "derived_operational_intelligence",
        "sensitivity": "metadata only",
        "cadence": "event-driven to scheduled",
        "usage": "feature registry, predictions, validation, drift, model cards, warnings, panels, scenarios, annotations, approvals",
        "views": [
            "VW_MODEL_FEATURE_STORE_SUMMARY",
            "VW_MODEL_PREDICTIONS",
            "VW_MODEL_VALIDATION_RESULTS",
            "VW_MODEL_DRIFT_RESULTS",
            "VW_MODEL_CARD_REGISTRY",
            "VW_METRIC_REGISTRY",
            "VW_WARNING_LOGIC_REGISTRY",
            "VW_PANEL_REGISTRY",
            "VW_COEFFICIENT_REGISTRY",
            "VW_DIRECT_LINKAGE_VALIDATION",
            "VW_LEARNING_SYSTEM_EVENTS",
            "VW_SCENARIO_RUNS",
            "VW_SCENARIO_RESULTS",
            "VW_USER_ANNOTATIONS",
            "VW_GOVERNANCE_APPROVALS",
        ],
    },
]

MODEL_SCHEMAS = {
    "VW_MODEL_FEATURE_STORE_SUMMARY": "MODEL",
    "VW_MODEL_PREDICTIONS": "MODEL",
    "VW_MODEL_VALIDATION_RESULTS": "MODEL",
    "VW_MODEL_DRIFT_RESULTS": "MODEL",
    "VW_MODEL_CARD_REGISTRY": "MODEL",
    "VW_METRIC_REGISTRY": "CONFIG",
    "VW_WARNING_LOGIC_REGISTRY": "CONFIG",
    "VW_PANEL_REGISTRY": "GOVERNANCE",
    "VW_COEFFICIENT_REGISTRY": "CONFIG",
    "VW_DIRECT_LINKAGE_VALIDATION": "GOVERNANCE",
    "VW_LEARNING_SYSTEM_EVENTS": "APP",
    "VW_SCENARIO_RUNS": "APP",
    "VW_SCENARIO_RESULTS": "MART",
    "VW_USER_ANNOTATIONS": "APP",
    "VW_GOVERNANCE_APPROVALS": "GOVERNANCE",
}


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


def source_id_for(view_name: str) -> str:
    return f"SRC_{view_name.removeprefix('VW_')}"


def source_schema(view_name: str, default_schema: str) -> str:
    return MODEL_SCHEMAS.get(view_name, default_schema)


def field_contract(view_name: str) -> tuple[str, str]:
    fields_by_keyword = [
        ("ADT", ("movement-event", "encounter_id, event_ts, site_id, unit_id, event_type, source_location, destination_location, synthetic_demo_flag")),
        ("ENCOUNTERS", ("encounter aggregate", "encounter_id, site_id, unit_id, admit_ts, discharge_ts, age_band, service_line, synthetic_demo_flag")),
        ("ED_VISITS", ("ED visit aggregate", "visit_id, site_id, arrival_ts, decision_to_admit_ts, admit_disposition, acuity_band, synthetic_demo_flag")),
        ("BED_STATUS", ("bed-hour", "site_id, unit_id, bed_type, bed_status, clean_ready_flag, isolation_capable_flag, updated_ts")),
        ("CENSUS", ("unit-hour", "site_id, unit_id, hour_ts, census, physical_beds, staffed_beds, effective_beds")),
        ("TRANSFER", ("transfer request", "request_id, origin_region, target_site_id, requested_level_of_care, status, request_ts, age_band")),
        ("ORDERS", ("order aggregate", "order_group_id, site_id, unit_or_program, order_category, order_status, order_ts, result_or_complete_ts")),
        ("RESULTS", ("result aggregate", "result_group_id, site_id, unit_or_program, result_category, collection_ts, result_ts, turnaround_minutes")),
        ("IMAGING", ("imaging order aggregate", "order_group_id, modality_group, ordered_ts, scheduled_ts, resulted_ts, readiness_status")),
        ("MEDICATION", ("medication order aggregate", "order_group_id, med_class_group, ordered_ts, verified_ts, dispense_status, discharge_related_flag")),
        ("MAR", ("administration aggregate", "admin_group_id, med_class_group, due_ts, administration_status, delay_minutes")),
        ("RESPIRATORY_SUPPORT", ("unit-shift aggregate", "site_id, unit_id, support_level_group, count, escalation_count, shift_start_ts")),
        ("VITAL_SIGNS", ("unit-hour aggregate", "site_id, unit_id, hour_ts, observation_count, abnormal_band_count, completeness_pct")),
        ("CLINICAL_SCORES", ("unit-day aggregate", "site_id, unit_id, score_family, score_band, count, reviewed_flag")),
        ("SEPSIS", ("screen-day aggregate", "site_id, unit_id, screen_status, positive_screen_count, review_status, small_cell_suppressed")),
        ("ALERT", ("alert event aggregate", "alert_id, alert_family, unit_or_program, alert_ts, severity, acknowledgement_status")),
        ("CARE_PLAN", ("milestone aggregate", "milestone_id, unit_or_program, milestone_type, due_ts, completed_ts, status")),
        ("DISCHARGE", ("discharge milestone aggregate", "encounter_id, milestone_type, milestone_ts, barrier_category, expected_discharge_band")),
        ("PHARMACY", ("discharge medication aggregate", "site_id, unit_id, medication_status, pending_count, median_age_hours")),
        ("HOME_SUPPORT", ("home-support aggregate", "site_id, program, request_status, pending_count, median_age_hours")),
        ("EQUIPMENT", ("equipment readiness aggregate", "site_id, program, equipment_group, readiness_status, pending_count")),
        ("TRANSPORT", ("transport readiness aggregate", "site_id, unit_or_program, transport_status, pending_count, median_age_hours")),
        ("FAMILY_READINESS", ("readiness proxy aggregate", "site_id, unit_or_program, readiness_band, count, caveat")),
        ("OR_", ("case-day aggregate", "case_id, site_id, procedure_group, scheduled_start_ts, case_status, post_op_bed_need")),
        ("PACU", ("PACU event aggregate", "case_id, site_id, pacu_arrival_ts, pacu_ready_ts, hold_minutes, bed_need")),
        ("PROCEDURE", ("procedure schedule aggregate", "case_id, procedure_group, scheduled_date, status, cancellation_reason_group")),
        ("REFERRAL", ("referral aggregate", "referral_id, site_id, program, priority, received_ts, triage_status, completeness_pct")),
        ("WAITLIST", ("program-week", "site_id, program, week_start, waitlist_total, over_target_count, median_wait_days, p90_wait_days")),
        ("APPOINTMENTS", ("appointment aggregate", "appointment_id, site_id, program, appointment_ts, status, appointment_type, completed_flag")),
        ("CLINIC", ("clinic-template aggregate", "site_id, program, template_date, slots_available, protected_urgent_slots, provider_group")),
        ("PROVIDER", ("provider group availability", "site_id, program, provider_group, available_sessions, constrained_sessions, week_start")),
        ("NO_SHOW", ("appointment reliability aggregate", "site_id, program, appointment_type, no_show_count, late_cancel_count, completed_count")),
        ("FOLLOWUP", ("follow-up aggregate", "site_id, program, overdue_count, median_overdue_days, priority_band")),
        ("DIAGNOSTIC", ("diagnostic readiness aggregate", "site_id, program, dependency_group, ready_count, missing_prerequisite_count, readiness_pct")),
        ("VIRTUAL", ("virtual suitability aggregate", "site_id, program, visit_type, suitable_count, converted_count, caveat")),
        ("OUTREACH", ("outreach capacity aggregate", "region_id, program, clinic_date, slots_available, travel_burden_band")),
        ("STAFFING", ("unit-shift staffing aggregate", "site_id, unit_id, shift_start_ts, required_hours, scheduled_hours, skill_mix_group")),
        ("WORKLOAD", ("unit-shift workload aggregate", "site_id, unit_id, workload_index, observation_level, isolation_factor")),
        ("SKILL_MIX", ("skill-mix aggregate", "site_id, unit_id, skill_group, required_hours, scheduled_hours")),
        ("FLOAT_POOL", ("float-pool aggregate", "site_id, shift_start_ts, available_hours, deployable_skill_groups")),
        ("SAFETY", ("safety aggregate", "site_id, unit_or_program, signal_family, count, severity_proxy, review_status")),
        ("READMISSION", ("revisit aggregate", "site_id, program_or_unit, revisit_window, observed_count, expected_count")),
        ("DOT_PHRASE", ("documentation completeness proxy", "site_id, unit_or_program, doc_family, completeness_pct, caveat")),
        ("DATA_QUALITY", ("quality event", "object_name, check_name, status, failed_rows, severity, detected_ts")),
        ("RESPIRATORY_ACTIVITY", ("region-week", "region_id, week_start, respiratory_activity_index, source_release_date")),
        ("WEATHER_AQHI", ("region-day", "region_id, date, temperature_c, aqhi_max, smoke_flag")),
        ("POPULATION", ("region-age-band", "region_id, age_band, population_count, vintage_year")),
        ("CALENDAR", ("date", "date, school_in_session_flag, holiday_flag, fiscal_period, season_label")),
        ("COMMUNITY", ("region-week", "region_id, week_start, demand_proxy_index, caveat")),
        ("FEATURE_STORE", ("asset-feature summary", "asset_id, feature_family, source_view, feature_count, freshness_minutes")),
        ("PREDICTIONS", ("asset-output", "asset_id, output_ts, site_id, unit_or_program, score, threshold, explanation_json")),
        ("VALIDATION", ("asset-validation run", "asset_id, validation_run_id, cohort_label, metric_name, metric_value, reviewed_status")),
        ("DRIFT", ("asset-drift run", "asset_id, drift_run_id, feature_family, drift_score, drift_status, checked_at")),
        ("MODEL_CARD", ("asset registry", "asset_id, model_name, governance_status, deployment_status, owner, next_review")),
        ("METRIC_REGISTRY", ("metric registry", "metric_id, formula, owner, validation_status, reviewed_date, caveat")),
        ("WARNING_LOGIC", ("warning registry", "warning_id, asset_id, threshold, severity, acknowledgement_required, rollback_flag")),
        ("PANEL_REGISTRY", ("panel registry", "panel_id, app_area, classification, source_ids, metric_ids, model_ids")),
        ("COEFFICIENT", ("coefficient registry", "coefficient_id, value, unit, owner, review_status, caveat")),
        ("DIRECT_LINKAGE", ("source validation", "source_id, field_name, readiness, freshness, row_count, small_cell_suppression")),
        ("LEARNING_SYSTEM", ("learning event", "event_id, event_type, created_at, created_by, related_metric_id, related_model_id, related_panel_id, related_scenario_id, payload_json")),
        ("SCENARIO_RUNS", ("scenario run", "scenario_run_id, scenario_id, created_at, created_by, inputs_json, outcome_json")),
        ("SCENARIO_RESULTS", ("scenario result", "scenario_id, outcome_name, baseline_value, scenario_value, p10, p90")),
        ("USER_ANNOTATIONS", ("annotation event", "event_id, created_at, app_area, related_ids, note, synthetic_demo_flag")),
        ("GOVERNANCE_APPROVALS", ("governance approval", "decision_id, related_id, decision, reviewer_role, created_at, payload_json")),
    ]
    for keyword, contract in fields_by_keyword:
        if keyword in view_name:
            return contract
    return "curated aggregate", "record_id, site_id, unit_or_program, event_ts, status, metric_value, synthetic_demo_flag"


def registry_classification(view_name: str, default_classification: str) -> str:
    if any(term in view_name for term in ["PREDICTIONS", "DRIFT", "VALIDATION", "MODEL_CARD", "FEATURE_STORE"]):
        return "modelled_predictive_ai_asset"
    if any(term in view_name for term in ["METRIC", "WARNING", "PANEL", "COEFFICIENT", "LEARNING", "SCENARIO", "ANNOTATIONS", "GOVERNANCE", "DATA_QUALITY"]):
        return "derived_operational_intelligence"
    return default_classification


def source_registry() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in SOURCE_GROUPS:
        for view_name in group["views"]:
            grain, fields = field_contract(view_name)
            schema = source_schema(view_name, group["schema"])
            rows.append(
                {
                    "source_id": source_id_for(view_name),
                    "curated_view": f"{schema}.{view_name}",
                    "source_view_name": view_name,
                    "source_domain": group["domain"],
                    "grain": grain,
                    "fields": fields,
                    "field_types": "synthetic ids, timestamps, categorical dimensions, numeric measures, Boolean flags, and JSON payloads",
                    "cadence": group["cadence"],
                    "classification": registry_classification(view_name, group["classification"]),
                    "phi_sensitivity": group["sensitivity"],
                    "dashboard_usage": group["usage"],
                    "validation_rules": "source view present, field populated, freshness, row count, timestamp logic, referential integrity, metric owner approval, small-cell suppression",
                    "future_mapping_placeholder": f"CONNECTCARE_OR_ENTERPRISE_MAPPING_TBD_{len(rows) + 1:03d}",
                }
            )
    return rows


def direct_link_validation(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    review_sources = {
        "SRC_SYNTH_TRANSFER_REQUESTS",
        "SRC_SYNTH_DIAGNOSTIC_READINESS",
        "SRC_SYNTH_NO_SHOW_LATE_CANCEL",
        "SRC_SYNTH_SEPSIS_SCREENING",
        "SRC_OPEN_WEATHER_AQHI",
        "SRC_MODEL_VALIDATION_RESULTS",
        "SRC_MODEL_DRIFT_RESULTS",
    }
    not_mapped_sources = {
        "SRC_SYNTH_FAMILY_READINESS_PROXY",
        "SRC_SYNTH_DOT_PHRASE_OR_DOC_COMPLETENESS_PROXY",
        "SRC_OPEN_COMMUNITY_DEMAND_PROXY",
    }
    for index, source in enumerate(sources):
        if source["source_id"] in not_mapped_sources:
            status = "not_mapped"
            stoplight = "gray"
        elif source["source_id"] in review_sources:
            status = "review"
            stoplight = "yellow"
        else:
            status = "ready"
            stoplight = "green"
        rows.append(
            {
                "source_id": source["source_id"],
                "source_view_name": source["source_view_name"],
                "curated_view": source["curated_view"],
                "source_domain": source["source_domain"],
                "source_view_present": "not_mapped" if status == "not_mapped" else "pass",
                "field_populated": "review" if status == "review" else "not_mapped" if status == "not_mapped" else "pass",
                "freshness": "review" if source["source_id"] in {"SRC_OPEN_WEATHER_AQHI", "SRC_MODEL_DRIFT_RESULTS"} else "not_mapped" if status == "not_mapped" else "pass",
                "row_count": "not_mapped" if status == "not_mapped" else "pass",
                "timestamp_logic": "review" if source["source_id"] == "SRC_SYNTH_TRANSFER_REQUESTS" else "not_mapped" if status == "not_mapped" else "pass",
                "referential_integrity": "pass",
                "metric_definition_approved": "review" if source["source_id"] == "SRC_SYNTH_DIAGNOSTIC_READINESS" else "not_mapped" if status == "not_mapped" else "pass",
                "small_cell_suppression": "review" if source["source_id"] == "SRC_SYNTH_SEPSIS_SCREENING" else "pass",
                "overall_readiness": status,
                "stoplight": stoplight,
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
        ("METRIC_OCCUPANCY", "Network occupancy", "sum(census) / sum(effective_beds)", "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_BED_STATUS", "hourly", "Patient Flow", "approved", "direct"),
        ("METRIC_ED_BOARDING", "ED boarder hours", "sum(boarder_count * elapsed_hours)", "SRC_SYNTH_ED_VISITS,SRC_SYNTH_ADT_EVENTS,SRC_SYNTH_PATIENT_CLASS_STATUS", "15 minutes", "ED/Inpatient", "approved", "derived"),
        ("METRIC_DISCHARGE_RELIABILITY", "Discharge reliability", "completed_discharges_by_1600 / expected_discharges", "SRC_SYNTH_DISCHARGE_MILESTONES,SRC_SYNTH_DISCHARGE_BARRIERS", "hourly", "Patient Flow", "approved", "derived"),
        ("METRIC_EFFECTIVE_STAFFED_BEDS", "Effective staffed beds", "physical_beds * staffing_factor * isolation_factor", "SRC_SYNTH_BED_STATUS,SRC_SYNTH_STAFFING_ROSTER,SRC_SYNTH_WORKLOAD_ACUITY,SRC_SYNTH_ISOLATION_STATUS", "hourly", "Operations", "approved", "derived"),
        ("METRIC_PICU_NICU_PRESSURE", "PICU/NICU pressure", "weighted occupancy + transfer demand + step-down constraint", "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_TRANSFER_REQUESTS,SRC_SYNTH_LEVEL_OF_CARE", "hourly", "Critical Care", "review", "derived"),
        ("METRIC_OR_CANCELLATION_RISK", "OR cancellation risk", "post-op bed demand gap + PACU hold + staffing constraint", "SRC_SYNTH_OR_CASES,SRC_SYNTH_PACU_EVENTS,SRC_SYNTH_POST_OP_BED_DEMAND", "daily", "Perioperative", "approved", "modelled"),
        ("METRIC_WAITLIST_PRESSURE", "Waitlist pressure", "weighted over-target referrals by priority and age", "SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_REFERRALS,SRC_SYNTH_REFERRAL_TRIAGE", "weekly", "Ambulatory", "approved", "derived"),
        ("METRIC_THIRD_NEXT_AVAILABLE", "Third next available", "third open eligible appointment slot from clinic template", "SRC_SYNTH_CLINIC_TEMPLATES,SRC_SYNTH_CLINIC_SLOTS,SRC_SYNTH_APPOINTMENTS", "weekly", "Ambulatory", "approved", "derived"),
        ("METRIC_NO_SHOW_GUARDRAIL", "No-show guardrail", "predicted missed visits constrained by equity and priority rules", "SRC_SYNTH_NO_SHOW_LATE_CANCEL,SRC_SYNTH_PROVIDER_AVAILABILITY,SRC_SYNTH_REFERRALS", "daily", "Ambulatory", "review", "modelled"),
        ("METRIC_DIAGNOSTIC_READINESS", "Diagnostic readiness", "complete dependencies / required dependencies", "SRC_SYNTH_DIAGNOSTIC_READINESS,SRC_SYNTH_IMAGING_ORDERS,SRC_SYNTH_LAB_RESULTS", "daily", "Ambulatory", "review", "derived"),
        ("METRIC_SURVEILLANCE_WARNING", "Clinical surveillance warning", "synthetic signal above governed threshold", "SRC_SYNTH_SAFETY_EVENTS_AGG,SRC_SYNTH_SEPSIS_SCREENING,SRC_MODEL_PREDICTIONS", "daily", "Surveillance", "review", "modelled"),
        ("METRIC_GATEKEEPER_HEALTH", "Governance control health", "ready assets / active assets with unresolved issues weighted by severity", "SRC_DIRECT_LINKAGE_VALIDATION,SRC_GOVERNANCE_APPROVALS,SRC_LEARNING_SYSTEM_EVENTS", "event-driven", "Analytics Governance", "approved", "derived"),
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
        ("PANEL_SYSTEM_POSTURE", "Today pediatric system posture", "System Posture", "derived", "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_ED_VISITS,SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_MODEL_PREDICTIONS", "METRIC_OCCUPANCY,METRIC_ED_BOARDING,METRIC_WAITLIST_PRESSURE", "INPT_OCCUPANCY_FORECAST,PICU_NICU_PRESSURE"),
        ("PANEL_INPATIENT_COMMAND", "Inpatient command", "Inpatient Intelligence", "derived", "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_BED_STATUS,SRC_SYNTH_DISCHARGE_MILESTONES,SRC_SYNTH_PACU_EVENTS", "METRIC_OCCUPANCY,METRIC_DISCHARGE_RELIABILITY,METRIC_EFFECTIVE_STAFFED_BEDS", "INPT_OCCUPANCY_FORECAST,ED_BOARDING_FORECAST,DISCHARGE_BY_TIME_BAND"),
        ("PANEL_AMBULATORY_COMMAND", "Ambulatory command", "Ambulatory Access Intelligence", "derived", "SRC_SYNTH_REFERRALS,SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_CLINIC_TEMPLATES,SRC_SYNTH_APPOINTMENTS", "METRIC_WAITLIST_PRESSURE,METRIC_THIRD_NEXT_AVAILABLE,METRIC_NO_SHOW_GUARDRAIL", "AMB_BACKLOG_FORECAST,NO_SHOW_LATE_CANCEL_RISK,URGENT_WAITLIST_BREACH_RISK"),
        ("PANEL_PREDICTIVE_ASSETS", "Clinical surveillance and predictive assets", "Predictive Asset Layer", "modelled", "SRC_SYNTH_SAFETY_EVENTS_AGG,SRC_SYNTH_SEPSIS_SCREENING,SRC_MODEL_PREDICTIONS,SRC_MODEL_CARD_REGISTRY", "METRIC_SURVEILLANCE_WARNING", "PEDIATRIC_EARLY_WARNING_SIGNAL,SEPSIS_SURVEILLANCE_SIGNAL,RARE_DISEASE_CASE_FINDING_SIGNAL,READMISSION_REVISIT_RISK,LONG_STAY_RISK"),
        ("PANEL_SCENARIO_LAB", "Scenario simulation lab", "Scenario Simulation Lab", "modelled", "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_STAFFING_ROSTER,SRC_OPEN_RESPIRATORY_ACTIVITY", "METRIC_OCCUPANCY,METRIC_WAITLIST_PRESSURE", "INPT_OCCUPANCY_FORECAST,AMB_BACKLOG_FORECAST"),
        ("PANEL_GATEKEEPER", "AHA Gatekeeper control plane", "AHA Gatekeeper Control Plane", "derived", "SRC_GOVERNANCE_APPROVALS,SRC_MODEL_CARD_REGISTRY,SRC_LEARNING_SYSTEM_EVENTS,SRC_WARNING_LOGIC_REGISTRY", "METRIC_GATEKEEPER_HEALTH", "all active assets"),
        ("PANEL_MEMORY", "Learning-system memory", "Learning System Memory", "derived", "SRC_LEARNING_SYSTEM_EVENTS,SRC_GOVERNANCE_APPROVALS,SRC_USER_ANNOTATIONS", "METRIC_GATEKEEPER_HEALTH", "scenario and acknowledgement outputs"),
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
        {"label": "Readiness overlay", "value": "63 green / 7 yellow / 3 gray", "detail": "Full v3 source catalog is wired with explicit owner-review and not-yet-mapped states.", "tone": "watch"},
        {"label": "Learning memory", "value": "12 events this week", "detail": "Scenario runs, warning acknowledgements, issue flags, and governance decisions are captured.", "tone": "steady"},
    ]
    why_changed = [
        {"driver": "Respiratory activity", "change": "+7.2%", "contribution": 34, "evidence": "OPEN_DATA.VW_OPEN_RESPIRATORY_ACTIVITY rose above seasonal baseline."},
        {"driver": "Effective staffed beds", "change": "-11 beds", "contribution": 29, "evidence": "CANONICAL.VW_SYNTH_STAFFING_ROSTER shows skill-mix gaps in PICU/NICU and respiratory units."},
        {"driver": "Discharge reliability", "change": "-4.8 pts", "contribution": 22, "evidence": "Discharge milestone barriers concentrated in pharmacy, transport, and family readiness."},
        {"driver": "Ambulatory diagnostic readiness", "change": "-6.1 pts", "contribution": 15, "evidence": "Dependency completion lag affects complex care and neurology backlogs."},
    ]
    return {"kpis": kpis, "postureCards": posture_cards, "whyChanged": why_changed}


def inpatient_payload() -> dict[str, list[dict[str, Any]]]:
    unit_rows: list[dict[str, Any]] = []
    unit_details: list[dict[str, Any]] = []
    unit_timeline: list[dict[str, Any]] = []
    units = [
        ("Respiratory", "acute medicine", 0.99, 0.12, 16, "review"),
        ("General pediatrics", "acute medicine", 0.94, 0.08, 11, "ready"),
        ("PICU", "critical care", 0.96, 0.10, 5, "review"),
        ("NICU", "critical care", 0.90, 0.06, 3, "ready"),
        ("Surgery", "surgical", 0.86, 0.04, 2, "ready"),
        ("Mental health", "mental health", 0.92, 0.09, 4, "ready"),
    ]
    for site_id, site_name, _ in SITES:
        site_adjustment = 0.015 if site_id == "SITE_STOLLERY_INSPIRED" else -0.008 if site_id == "SITE_ACH_INSPIRED" else 0
        for unit_index, (unit, service_line, occupancy, staffing_gap, boarders, readiness) in enumerate(units):
            adjusted_occupancy = occupancy + site_adjustment
            unit_id = f"{site_id.replace('SITE_', '')}_{unit.upper().replace(' ', '_').replace('/', '_')}"
            effective_beds = 24 + unit_index * 4 + (8 if service_line == "critical care" else 0)
            staffed_beds = round(effective_beds * (1 + staffing_gap))
            census = round(adjusted_occupancy * effective_beds)
            unit_rows.append(
                {
                    "site_id": site_id,
                    "site_name": site_name,
                    "unit_id": unit_id,
                    "unit_name": unit,
                    "service_line": service_line,
                    "occupancy_pct": occupancy + (0.015 if site_id == "SITE_STOLLERY_INSPIRED" else -0.008 if site_id == "SITE_ACH_INSPIRED" else 0),
                    "staffing_gap_pct": staffing_gap,
                    "ed_boarders": boarders,
                    "effective_beds_lost": round(staffing_gap * 42),
                    "census": census,
                    "effective_beds": effective_beds,
                    "staffed_beds": staffed_beds,
                    "source_readiness": readiness,
                    "classification": "derived",
                    "freshness": "15 min",
                    "confidence": "medium-high",
                    "caveat": "Synthetic unit pressure; small cells suppressed.",
                    "lineage_panel_id": "PANEL_INPATIENT_COMMAND",
                    "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_BED_STATUS,SRC_SYNTH_STAFFING_ROSTER,SRC_SYNTH_ED_VISITS",
                }
            )
            unit_details.append(
                {
                    "site_id": site_id,
                    "site_name": site_name,
                    "unit_id": unit_id,
                    "unit_name": unit,
                    "service_line": service_line,
                    "level_of_care_mix": "critical care weighted" if service_line == "critical care" else "acute inpatient weighted",
                    "census": census,
                    "effective_beds": effective_beds,
                    "physical_beds": effective_beds + round(staffing_gap * 18) + 2,
                    "staffed_beds": staffed_beds,
                    "isolation_blocked_beds": max(0, round(adjusted_occupancy * 5) - 2),
                    "observation_level_pressure": round(0.18 + staffing_gap + unit_index * 0.015, 3),
                    "respiratory_support_count": max(1, round(census * (0.22 if unit == "Respiratory" else 0.08))),
                    "transfer_in_requests": max(0, boarders // 4 + (2 if service_line == "critical care" else 0)),
                    "step_down_ready": max(0, round(boarders * (0.34 if service_line == "critical care" else 0.12))),
                    "discharge_barriers": max(2, round(census * (0.16 + staffing_gap))),
                    "pharmacy_pending": max(1, round(census * 0.08)),
                    "transport_pending": max(1, round(census * 0.05)),
                    "staffing_gap_hours": round(staffing_gap * 180, 1),
                    "skill_mix_gap": "RN/RRT" if unit in {"Respiratory", "PICU"} else "RN/clinical aide",
                    "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_BED_STATUS,SRC_SYNTH_LEVEL_OF_CARE,SRC_SYNTH_ISOLATION_STATUS,SRC_SYNTH_STAFFING_ROSTER,SRC_SYNTH_WORKLOAD_ACUITY,SRC_SYNTH_DISCHARGE_BARRIERS",
                    "primary_metric_ids": "METRIC_OCCUPANCY,METRIC_EFFECTIVE_STAFFED_BEDS,METRIC_DISCHARGE_RELIABILITY",
                    "model_ids": "INPT_OCCUPANCY_FORECAST,ED_BOARDING_FORECAST,DISCHARGE_BY_TIME_BAND",
                    "caveat": "Synthetic aggregate unit drilldown. No patient-level rows, direct identifiers, or clinical decisioning.",
                }
            )
            for horizon_index, horizon in enumerate([0, 6, 12, 24, 36, 48, 60, 72]):
                relief = max(0, horizon_index - 2) * 0.006
                unit_timeline.append(
                    {
                        "site_id": site_id,
                        "unit_id": unit_id,
                        "unit_name": unit,
                        "horizon_hours": horizon,
                        "occupancy_pct": round(min(1.08, adjusted_occupancy + horizon_index * 0.008 - relief), 3),
                        "ed_boarders": max(0, boarders + horizon_index - round(relief * 40)),
                        "staffing_gap_pct": round(max(0.01, staffing_gap + (0.01 if horizon in {12, 24} else -0.004 if horizon >= 48 else 0)), 3),
                        "discharge_expected": max(1, round(census * (0.05 + horizon_index * 0.018))),
                        "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_ED_VISITS,SRC_SYNTH_DISCHARGE_MILESTONES",
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
    return {
        "unitPressure": unit_rows,
        "unitDetails": unit_details,
        "unitTimeline": unit_timeline,
        "flowDrivers": flow_drivers,
        "forecast": forecast,
        "warnings": warnings,
    }


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
    program_details: list[dict[str, Any]] = []
    program_timeline: list[dict[str, Any]] = []
    for program_index, (program, waitlist, tna, breach, readiness, source_ready) in enumerate(programs):
        program_id = f"PROGRAM_{program.upper().replace(' ', '_').replace('-', '_')}"
        access.append(
            {
                "program_id": program_id,
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
                "source_ids": "SRC_SYNTH_REFERRALS,SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_CLINIC_TEMPLATES,SRC_SYNTH_APPOINTMENTS,SRC_SYNTH_DIAGNOSTIC_READINESS",
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
        program_details.append(
            {
                "program_id": program_id,
                "program": program,
                "site_scope": "provincial synthetic aggregate",
                "waitlist_total": waitlist,
                "urgent_waitlist": round(waitlist * (0.13 + breach * 0.1)),
                "over_target_count": round(waitlist * (0.22 + breach * 0.2)),
                "third_next_available_days": tna,
                "p90_wait_days": round(tna * (1.8 + breach)),
                "new_referrals_4wk": round(waitlist * (0.11 + program_index * 0.006)),
                "triage_median_days": round(3 + breach * 16),
                "slots_available_4wk": round(waitlist * (0.08 + readiness * 0.03)),
                "protected_urgent_slots": round(18 + breach * 52),
                "no_show_rate": round(0.08 + breach * 0.18, 3),
                "late_cancel_rate": round(0.04 + breach * 0.07, 3),
                "diagnostic_readiness": readiness,
                "missing_prerequisites": round(waitlist * (1 - readiness) * 0.24),
                "virtual_suitability": round(0.18 + readiness * 0.42, 3),
                "travel_burden_index": round(0.22 + program_index * 0.08 + breach * 0.3, 3),
                "source_ids": "SRC_SYNTH_REFERRALS,SRC_SYNTH_REFERRAL_TRIAGE,SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_CLINIC_SLOTS,SRC_SYNTH_NO_SHOW_LATE_CANCEL,SRC_SYNTH_DIAGNOSTIC_READINESS,SRC_SYNTH_VIRTUAL_CARE_SUITABILITY",
                "primary_metric_ids": "METRIC_WAITLIST_PRESSURE,METRIC_THIRD_NEXT_AVAILABLE,METRIC_NO_SHOW_GUARDRAIL,METRIC_DIAGNOSTIC_READINESS",
                "model_ids": "AMB_REFERRAL_DEMAND_FORECAST,AMB_BACKLOG_FORECAST,URGENT_WAITLIST_BREACH_RISK,DIAGNOSTIC_READINESS_RISK",
                "caveat": "Synthetic aggregate program drilldown. No patient-level rows, direct identifiers, or automated scheduling action.",
            }
        )
        for week_index, week in enumerate([0, 1, 2, 4, 8, 13, 18, 26]):
            scenario_relief = max(0, week_index - 2) * (12 + readiness * 8)
            program_timeline.append(
                {
                    "program_id": program_id,
                    "program": program,
                    "horizon_weeks": week,
                    "waitlist_total": max(100, round(waitlist + week * (12 + breach * 18) - scenario_relief)),
                    "third_next_available_days": max(10, round(tna + week * 0.5 - scenario_relief * 0.05)),
                    "urgent_breach_risk": round(min(0.72, max(0.04, breach + week_index * 0.012 - readiness * 0.03)), 3),
                    "diagnostic_readiness": round(min(0.96, readiness + week_index * 0.012), 3),
                    "source_ids": "SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_CLINIC_TEMPLATES,SRC_SYNTH_DIAGNOSTIC_READINESS",
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
    return {
        "programAccess": access,
        "programDetails": program_details,
        "programTimeline": program_timeline,
        "noShowFrontier": frontier,
        "forecast": forecast,
        "warnings": warnings,
    }


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
    baselines = [
        {
            "domain": "inpatient",
            "boarder_hours": 186,
            "occupancy_pct": 0.934,
            "effective_beds": 318,
            "staff_gap_hours": 182,
            "operating_cost_k": 0,
            "hr_shifts": 0,
            "finance_budget_k": 280,
            "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_ED_VISITS,SRC_SYNTH_STAFFING_ROSTER,SRC_SYNTH_DISCHARGE_BARRIERS",
        },
        {
            "domain": "ambulatory",
            "backlog": 8940,
            "urgent_breach_risk": 0.337,
            "third_next_available_days": 71,
            "recovered_slots": 0,
            "operating_cost_k": 0,
            "hr_shifts": 0,
            "finance_budget_k": 220,
            "source_ids": "SRC_SYNTH_REFERRALS,SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_CLINIC_TEMPLATES,SRC_SYNTH_DIAGNOSTIC_READINESS",
        },
    ]
    control_ranges = [
        {"control_id": "stepdown_beds", "domain": "inpatient", "label": "Protected step-down beds", "min": 0, "max": 14, "default": 5, "unit": "beds", "hr_per_unit": 0.7, "cost_k_per_unit": 4.2, "source_id": "SRC_SYNTH_LEVEL_OF_CARE"},
        {"control_id": "pharmacy_acceleration", "domain": "inpatient", "label": "Pharmacy acceleration", "min": 0, "max": 35, "default": 12, "unit": "% faster", "hr_per_unit": 0.08, "cost_k_per_unit": 0.9, "source_id": "SRC_SYNTH_PHARMACY_DISCHARGE_MED_STATUS"},
        {"control_id": "staffing_shifts", "domain": "inpatient", "label": "Added staffing shifts", "min": 0, "max": 28, "default": 8, "unit": "shifts", "hr_per_unit": 1.0, "cost_k_per_unit": 3.1, "source_id": "SRC_SYNTH_STAFFING_GAPS"},
        {"control_id": "surge_beds", "domain": "inpatient", "label": "Respiratory surge conversion", "min": 0, "max": 12, "default": 4, "unit": "beds", "hr_per_unit": 1.5, "cost_k_per_unit": 6.7, "source_id": "SRC_OPEN_RESPIRATORY_ACTIVITY"},
        {"control_id": "urgent_slots", "domain": "ambulatory", "label": "Protected urgent slots", "min": 0, "max": 160, "default": 48, "unit": "slots", "hr_per_unit": 0.08, "cost_k_per_unit": 0.55, "source_id": "SRC_SYNTH_CLINIC_SLOTS"},
        {"control_id": "virtual_conversion", "domain": "ambulatory", "label": "Virtual-suitable conversion", "min": 0, "max": 30, "default": 10, "unit": "%", "hr_per_unit": 0.12, "cost_k_per_unit": 1.2, "source_id": "SRC_SYNTH_VIRTUAL_CARE_SUITABILITY"},
        {"control_id": "diagnostic_huddle", "domain": "ambulatory", "label": "Diagnostic readiness lift", "min": 0, "max": 35, "default": 14, "unit": "%", "hr_per_unit": 0.18, "cost_k_per_unit": 1.8, "source_id": "SRC_SYNTH_DIAGNOSTIC_READINESS"},
        {"control_id": "guarded_overbook", "domain": "ambulatory", "label": "Guardrailed overbook", "min": 0, "max": 8, "default": 3, "unit": "%", "hr_per_unit": 0.22, "cost_k_per_unit": 1.1, "source_id": "SRC_SYNTH_NO_SHOW_LATE_CANCEL"},
    ]
    return {"scenarios": scenarios, "comparisons": comparisons, "baselines": baselines, "controlRanges": control_ranges}


def warning_logic_registry() -> list[dict[str, Any]]:
    warnings = [
        ("WARN-RULE-001", "INPT_OCCUPANCY_FORECAST", "METRIC_OCCUPANCY", "PANEL_INPATIENT_COMMAND", "prob_above_95 >= 0.55 and ED boarders increasing", "0.55", "high", "approved"),
        ("WARN-RULE-002", "PICU_NICU_PRESSURE", "METRIC_PICU_NICU_PRESSURE", "PANEL_SYSTEM_POSTURE", "pressure_score >= 0.70 or transfer requests open > 6h", "0.70", "high", "approved"),
        ("WARN-RULE-003", "DISCHARGE_BY_TIME_BAND", "METRIC_DISCHARGE_RELIABILITY", "PANEL_INPATIENT_COMMAND", "same-day discharge probability < 0.62 by 11:00", "0.62", "medium", "review"),
        ("WARN-RULE-004", "OR_CANCELLATION_RISK", "METRIC_OR_CANCELLATION_RISK", "PANEL_INPATIENT_COMMAND", "post-op bed demand exceeds staffed bed buffer", "4 beds", "medium", "approved"),
        ("WARN-RULE-005", "URGENT_WAITLIST_BREACH_RISK", "METRIC_WAITLIST_PRESSURE", "PANEL_AMBULATORY_COMMAND", "urgent breach probability >= 0.35 for two snapshots", "0.35", "medium", "approved"),
        ("WARN-RULE-006", "DIAGNOSTIC_READINESS_RISK", "METRIC_DIAGNOSTIC_READINESS", "PANEL_AMBULATORY_COMMAND", "missing prerequisite rate >= 0.22", "0.22", "medium", "review"),
        ("WARN-RULE-007", "PEDIATRIC_EARLY_WARNING_SIGNAL", "METRIC_SURVEILLANCE_WARNING", "PANEL_PREDICTIVE_ASSETS", "aggregate synthetic surveillance score above governed threshold", "0.70", "medium", "review"),
        ("WARN-RULE-008", "SEPSIS_SURVEILLANCE_SIGNAL", "METRIC_SURVEILLANCE_WARNING", "PANEL_PREDICTIVE_ASSETS", "synthetic sepsis signal exceeds threshold and alert burden cap", "0.62", "high", "hold"),
        ("WARN-RULE-009", "RARE_DISEASE_CASE_FINDING_SIGNAL", "METRIC_SURVEILLANCE_WARNING", "PANEL_PREDICTIVE_ASSETS", "candidate signal visible only when small-cell suppression passes", "suppressed", "low", "hold"),
        ("WARN-RULE-010", "NO_SHOW_LATE_CANCEL_RISK", "METRIC_NO_SHOW_GUARDRAIL", "PANEL_AMBULATORY_COMMAND", "guarded overbook proposal exceeds equity/travel guardrail", "0.08", "medium", "review"),
    ]
    return [
        {
            "warning_id": warning_id,
            "asset_id": asset_id,
            "metric_id": metric_id,
            "panel_id": panel_id,
            "condition": condition,
            "threshold": threshold,
            "severity": severity,
            "acknowledgement_required": severity in {"high", "medium"},
            "alert_burden_cap_per_week": [4, 3, 6, 5, 7, 5, 2, 1, 0, 8][index],
            "rollback_flag": status in {"hold", "review"},
            "owner": "Synthetic analytics governance",
            "status": status,
            "caveat": "Synthetic warning logic only; not validated for clinical decision-making.",
        }
        for index, (warning_id, asset_id, metric_id, panel_id, condition, threshold, severity, status) in enumerate(warnings)
    ]


def coefficient_registry() -> list[dict[str, Any]]:
    coefficients = [
        ("COEF-BED-001", "Staffing factor", "METRIC_EFFECTIVE_STAFFED_BEDS", 0.82, "multiplier", 0.65, 1.0, "approved"),
        ("COEF-BED-002", "Isolation constraint", "METRIC_EFFECTIVE_STAFFED_BEDS", 0.93, "multiplier", 0.75, 1.0, "approved"),
        ("COEF-FLOW-001", "Boarder hour penalty", "METRIC_ED_BOARDING", 1.25, "weighted hour", 0.8, 1.8, "approved"),
        ("COEF-FLOW-002", "Pharmacy barrier ageing", "METRIC_DISCHARGE_RELIABILITY", 0.18, "probability decrement", 0.05, 0.35, "review"),
        ("COEF-CC-001", "PICU transfer demand", "METRIC_PICU_NICU_PRESSURE", 0.34, "pressure weight", 0.1, 0.6, "review"),
        ("COEF-AMB-001", "Urgent referral weight", "METRIC_WAITLIST_PRESSURE", 2.4, "priority weight", 1.5, 3.5, "approved"),
        ("COEF-AMB-002", "Diagnostic dependency gap", "METRIC_DIAGNOSTIC_READINESS", 0.29, "risk weight", 0.1, 0.5, "review"),
        ("COEF-AMB-003", "No-show guardrail", "METRIC_NO_SHOW_GUARDRAIL", 0.08, "maximum overbook share", 0.0, 0.12, "review"),
        ("COEF-SIM-001", "Respiratory surge elasticity", "SCENARIO_SIMULATION", 0.41, "scenario weight", 0.2, 0.7, "approved"),
        ("COEF-SAFE-001", "Synthetic surveillance cap", "METRIC_SURVEILLANCE_WARNING", 2.0, "warnings per week", 0.0, 4.0, "hold"),
    ]
    return [
        {
            "coefficient_id": coefficient_id,
            "coefficient_name": name,
            "applies_to": applies_to,
            "value": value,
            "unit": unit,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "owner": "Synthetic metric governance",
            "review_status": status,
            "reviewed_at": NOW,
            "caveat": "Coefficient values are synthetic and require local validation before production use.",
        }
        for coefficient_id, name, applies_to, value, unit, lower_bound, upper_bound, status in coefficients
    ]


def data_quality_rules() -> list[dict[str, Any]]:
    rules = [
        ("DQ-001", "SRC_SYNTH_UNIT_CENSUS_HOURLY", "hourly census completeness", "freshness", "high", ">= 95% expected unit-hours", "pass", 0),
        ("DQ-002", "SRC_SYNTH_BED_STATUS", "bed status legal values", "domain", "high", "no unknown bed_status", "pass", 0),
        ("DQ-003", "SRC_SYNTH_ADT_EVENTS", "movement timestamp sequence", "timestamp", "high", "destination after source event", "pass", 0),
        ("DQ-004", "SRC_SYNTH_TRANSFER_REQUESTS", "transfer request status chronology", "timestamp", "medium", "status_ts not before request_ts", "review", 11),
        ("DQ-005", "SRC_SYNTH_DIAGNOSTIC_READINESS", "dependency denominator approval", "definition", "medium", "owner-approved denominator", "review", 7),
        ("DQ-006", "SRC_SYNTH_SEPSIS_SCREENING", "small cell suppression", "privacy", "high", "counts below threshold suppressed", "review", 2),
        ("DQ-007", "SRC_OPEN_WEATHER_AQHI", "public release freshness", "freshness", "low", "<= 24h lag", "review", 1),
        ("DQ-008", "SRC_MODEL_DRIFT_RESULTS", "latest drift result present", "governance", "medium", "active models checked daily", "review", 5),
        ("DQ-009", "SRC_WARNING_LOGIC_REGISTRY", "warning rollback field", "contract", "medium", "rollback action populated", "pass", 0),
        ("DQ-010", "SRC_LEARNING_SYSTEM_EVENTS", "writeback audit fields", "contract", "medium", "created_by and related ids populated", "pass", 0),
    ]
    return [
        {
            "check_id": check_id,
            "source_id": source_id,
            "rule_name": rule_name,
            "rule_type": rule_type,
            "severity": severity,
            "threshold": threshold,
            "status": status,
            "failed_rows": failed_rows,
            "last_run_at": NOW,
            "owner": "Synthetic data quality steward",
            "caveat": "Synthetic data-quality check; production checks must be approved by source owner.",
        }
        for check_id, source_id, rule_name, rule_type, severity, threshold, status, failed_rows in rules
    ]


def validation_drift_payload(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, model in enumerate(models):
        review_hold = "synthetic-only" in str(model["deployment_status"]).lower() or index % 5 == 0
        rows.append(
            {
                "asset_id": model["asset_id"],
                "validation_run_id": f"VAL-DRIFT-{index + 1:03d}",
                "primary_metric": "MAPE" if model["domain"] == "Operational" else "synthetic precision",
                "primary_metric_value": round(0.071 + (index % 6) * 0.013, 3),
                "calibration_status": model["calibration_status"],
                "subgroup_review": model["subgroup_performance"],
                "drift_score": round(0.08 + (index % 5) * 0.04, 3),
                "drift_status": model["drift_status"],
                "alert_burden": model["alert_burden"],
                "release_gate": "hold" if review_hold else "pass with caveat",
                "reviewer": "Synthetic model risk reviewer",
                "last_run_at": NOW,
                "caveat": "Synthetic validation and drift evidence; not validated for clinical decision-making.",
            }
        )
    return rows


def release_rollback_registry(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "release_id": f"REL-{index + 1:03d}",
            "asset_id": model["asset_id"],
            "panel_id": "PANEL_PREDICTIVE_ASSETS" if "surveillance" in str(model["domain"]).lower() else "PANEL_SYSTEM_POSTURE",
            "release_status": "hold" if "Synthetic only" in str(model["deployment_status"]) or "Validation hold" in str(model["deployment_status"]) else "approved for demo",
            "version": f"v3.0.{index + 1}",
            "canary_scope": "single synthetic site and aggregate replay",
            "rollback_trigger": "drift watch, alert burden breach, reviewer rejection, or source readiness regression",
            "rollback_action": model["rollback_plan"],
            "owner": model["owner"],
            "approved_at": NOW if "approved" in str(model["governance_status"]) else "",
            "caveat": "Release and rollback registry is synthetic demonstration data only.",
        }
        for index, model in enumerate(models)
    ]


def gatekeeper_payload(
    models: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    readiness: list[dict[str, Any]],
    metrics: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    coefficients: list[dict[str, Any]],
    quality_rules: list[dict[str, Any]],
    validation_drift: list[dict[str, Any]],
    releases: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    source_ready = sum(row["overall_readiness"] == "ready" for row in readiness)
    source_review = sum(row["overall_readiness"] == "review" for row in readiness)
    source_gray = sum(row["overall_readiness"] == "not_mapped" for row in readiness)
    metrics_ready = sum(row["validation"] == "approved" for row in metrics)
    metrics_review = len(metrics) - metrics_ready
    models_ready = sum("approved" in str(row["governance_status"]) for row in models)
    models_review = len(models) - models_ready
    warnings_ready = sum(row["status"] == "approved" for row in warnings)
    warnings_review = sum(row["status"] == "review" for row in warnings)
    warnings_hold = sum(row["status"] == "hold" for row in warnings)
    quality_ready = sum(row["status"] == "pass" for row in quality_rules)
    quality_review = len(quality_rules) - quality_ready
    drift_ready = sum(row["release_gate"] != "hold" for row in validation_drift)
    drift_hold = len(validation_drift) - drift_ready
    control = [
        {"area": "Direct source readiness", "ready": source_ready, "review": source_review, "blocked": source_gray, "mode": "executive lite"},
        {"area": "Metric definitions", "ready": metrics_ready, "review": metrics_review, "blocked": 0, "mode": "technical deep"},
        {"area": "Model cards", "ready": models_ready, "review": models_review, "blocked": 0, "mode": "technical deep"},
        {"area": "Warning logic", "ready": warnings_ready, "review": warnings_review, "blocked": warnings_hold, "mode": "executive lite"},
        {"area": "Coefficient registry", "ready": sum(row["review_status"] == "approved" for row in coefficients), "review": sum(row["review_status"] == "review" for row in coefficients), "blocked": sum(row["review_status"] == "hold" for row in coefficients), "mode": "technical deep"},
        {"area": "Data quality rules", "ready": quality_ready, "review": quality_review, "blocked": 0, "mode": "technical deep"},
        {"area": "Validation and drift", "ready": drift_ready, "review": 0, "blocked": drift_hold, "mode": "technical deep"},
        {"area": "Learning writebacks", "ready": 10, "review": 0, "blocked": 0, "mode": "technical deep"},
    ]
    dependencies: list[dict[str, Any]] = []
    for source in sources[:20]:
        dependencies.append({"from": source["source_id"], "to": "PANEL_SYSTEM_POSTURE", "relationship": "feeds direct readiness"})
    for model in models:
        dependencies.append({"from": model["asset_id"], "to": "PANEL_PREDICTIVE_ASSETS", "relationship": "governed output"})
    for warning in warnings:
        dependencies.append({"from": warning["warning_id"], "to": warning["panel_id"], "relationship": "controls warning display"})
    issues = [
        {"issue_id": "ISSUE-001", "severity": "medium", "related_id": "SRC_SYNTH_DIAGNOSTIC_READINESS", "status": "open", "note": "Definition owner must approve diagnostic readiness denominator."},
        {"issue_id": "ISSUE-002", "severity": "high", "related_id": "SEPSIS_SURVEILLANCE_SIGNAL", "status": "review queued", "note": "Alert-burden review required before public warning display."},
        {"issue_id": "ISSUE-003", "severity": "medium", "related_id": "NO_SHOW_LATE_CANCEL_RISK", "status": "guardrail review", "note": "Equity and travel-burden guardrail needs signoff before scenario promotion."},
        {"issue_id": "ISSUE-004", "severity": "medium", "related_id": "SRC_MODEL_DRIFT_RESULTS", "status": "open", "note": "Latest drift result must be present for every active model before alert promotion."},
    ]
    approvals = [
        {"decision_id": "GOV-DEC-001", "related_id": "INPT_OCCUPANCY_FORECAST", "decision": "approved for demo", "reviewer_role": "analytics governance", "created_at": NOW},
        {"decision_id": "GOV-DEC-002", "related_id": "PICU_NICU_PRESSURE", "decision": "approved with warning label", "reviewer_role": "operations sponsor", "created_at": NOW},
        {"decision_id": "GOV-DEC-003", "related_id": "SEPSIS_SURVEILLANCE_SIGNAL", "decision": "synthetic-only hold", "reviewer_role": "clinical safety reviewer", "created_at": NOW},
    ]
    return {
        "controlPlane": control,
        "dependencyEdges": dependencies,
        "issues": issues,
        "approvals": approvals,
        "warningLogic": warnings,
        "coefficients": coefficients,
        "dataQualityRules": quality_rules,
        "validationDrift": validation_drift,
        "releaseRollback": releases,
    }


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
        ("EVT-001", "scenario_run", "Scenario Simulation Lab", "", "", "PANEL_SCENARIO_LAB", "SCN-INPT-001", "complete", "medium", "PICU step-down scenario reduced synthetic boarder hours."),
        ("EVT-002", "warning_acknowledgement", "Inpatient Intelligence", "METRIC_PICU_NICU_PRESSURE", "PICU_NICU_PRESSURE", "PANEL_INPATIENT_COMMAND", "", "acknowledged", "high", "Operations huddle acknowledged PICU/NICU warning."),
        ("EVT-003", "metric_issue_flag", "Ambulatory Access Intelligence", "METRIC_DIAGNOSTIC_READINESS", "", "PANEL_AMBULATORY_COMMAND", "", "open", "medium", "Diagnostic readiness denominator requires owner review."),
        ("EVT-004", "model_review_note", "Predictive Asset Layer", "METRIC_SURVEILLANCE_WARNING", "SEPSIS_SURVEILLANCE_SIGNAL", "PANEL_PREDICTIVE_ASSETS", "", "review queued", "high", "Synthetic surveillance warning remains not clinical-use."),
        ("EVT-005", "governance_decision", "AHA Gatekeeper Control Plane", "METRIC_PICU_NICU_PRESSURE", "PICU_NICU_PRESSURE", "PANEL_GATEKEEPER", "", "approved with caveat", "medium", "Warning label and rollback path required."),
        ("EVT-006", "panel_feedback", "System Posture", "", "", "PANEL_SYSTEM_POSTURE", "", "complete", "low", "Executive mode should keep stoplight overlay visible."),
        ("EVT-007", "validation_review", "AHA Gatekeeper Control Plane", "METRIC_SURVEILLANCE_WARNING", "PEDIATRIC_EARLY_WARNING_SIGNAL", "PANEL_PREDICTIVE_ASSETS", "", "hold", "high", "Synthetic surveillance signal held pending alert-burden review."),
        ("EVT-008", "huddle_review_event", "Ambulatory Access Intelligence", "METRIC_WAITLIST_PRESSURE", "URGENT_WAITLIST_BREACH_RISK", "PANEL_AMBULATORY_COMMAND", "SCN-AMB-001", "complete", "medium", "Urgent slot protection scenario promoted for program huddle."),
        ("EVT-009", "learning_outcome_review", "Scenario Simulation Lab", "METRIC_OCCUPANCY", "INPT_OCCUPANCY_FORECAST", "PANEL_SCENARIO_LAB", "SCN-INPT-002", "complete", "medium", "Pharmacy acceleration scenario retained after synthetic outcome review."),
        ("EVT-010", "user_annotation", "Future Real-Data Wiring", "", "", "PANEL_WIRING", "", "open", "low", "Source-owner mapping placeholder recorded for future curated-view review."),
    ]
    rows: list[dict[str, Any]] = []
    for index, (event_id, event_type, app_area, related_metric_id, related_model_id, related_panel_id, related_scenario_id, status, severity, note) in enumerate(events):
        related_ids = ",".join(
            value for value in [related_metric_id, related_model_id, related_panel_id, related_scenario_id] if value
        )
        rows.append(
            {
                "event_id": event_id,
                "event_type": event_type,
                "created_at": NOW,
                "created_by": "synthetic_snowflake_user",
                "app_area": app_area,
                "site_id": SITES[index % len(SITES)][0],
                "unit_or_program": ["PICU", "Respiratory", "Complex care", "Network", "Neurology", "System", "PICU", "Neurology", "Pharmacy", "Governance"][index],
                "related_ids": related_ids,
                "related_metric_id": related_metric_id,
                "related_model_id": related_model_id,
                "related_panel_id": related_panel_id,
                "related_scenario_id": related_scenario_id,
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
    warnings = warning_logic_registry()
    coefficients = coefficient_registry()
    quality_rules = data_quality_rules()
    validation_drift = validation_drift_payload(models)
    releases = release_rollback_registry(models)
    posture = system_posture()
    inpatient = inpatient_payload()
    ambulatory = ambulatory_payload()
    predictive = predictive_assets_payload()
    scenarios = scenario_lab_payload()
    gatekeeper = gatekeeper_payload(
        models,
        sources,
        readiness,
        metrics,
        warnings,
        coefficients,
        quality_rules,
        validation_drift,
        releases,
    )
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
    write_csv("v3_governance_approvals.csv", gatekeeper["approvals"])
    write_csv("v3_warning_logic_registry.csv", warnings)
    write_csv("v3_coefficient_registry.csv", coefficients)
    write_csv("v3_data_quality_rules.csv", quality_rules)
    write_csv("v3_validation_drift.csv", validation_drift)
    write_csv("v3_release_rollback.csv", releases)
    write_csv("v3_scenarios.csv", scenarios["scenarios"])
    write_csv("v3_inpatient_unit_pressure.csv", inpatient["unitPressure"])
    write_csv("v3_inpatient_unit_details.csv", inpatient["unitDetails"])
    write_csv("v3_inpatient_unit_timeline.csv", inpatient["unitTimeline"])
    write_csv("v3_ambulatory_program_access.csv", ambulatory["programAccess"])
    write_csv("v3_ambulatory_program_details.csv", ambulatory["programDetails"])
    write_csv("v3_ambulatory_program_timeline.csv", ambulatory["programTimeline"])
    print(f"Wrote v3 frontier assets to {OUT}")


if __name__ == "__main__":
    main()
