"""Generate v5 pediatric command-centre assets for the showcase.

The v5 payload is a synthetic, aggregate-only operating layer. It adds enough
service, unit, program, HR/workforce, finance/resource, and open-context depth
for the showcase to behave like a daily-use pediatric progression hub while
keeping the same governance boundary as earlier versions.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.synthetic import generate_v3_frontier_data as v3

OUT = ROOT / "apps" / "showcase" / "public" / "data" / "v5"
SAMPLE = ROOT / "apps" / "snowflake_streamlit" / "shared" / "sample_data"
NOW = "2026-06-11T08:30:00-07:00"

SITES = [
    ("SITE_STOLLERY_INSPIRED", "Stollery-inspired", "North provincial catchment", 1.08),
    ("SITE_ACH_INSPIRED", "Alberta Children's-inspired", "South provincial catchment", 1.0),
    ("SITE_PROV_NETWORK", "Provincial pediatric network", "Network aggregate", 0.72),
]

SERVICES = [
    ("general_pediatrics", "General pediatrics", "acute medicine", 34, 0.91, 0.62),
    ("respiratory", "Respiratory", "acute medicine", 30, 0.97, 0.91),
    ("surgery", "Surgery", "surgical", 26, 0.86, 0.42),
    ("picu", "PICU", "critical care", 16, 1.02, 0.52),
    ("nicu", "NICU", "critical care", 24, 0.95, 0.36),
    ("cardiology", "Cardiology", "medical specialty", 18, 0.88, 0.38),
    ("oncology", "Oncology", "medical specialty", 20, 0.9, 0.32),
    ("neurology", "Neurology", "medical specialty", 18, 0.87, 0.41),
    ("mental_health", "Mental health", "mental health", 22, 0.94, 0.28),
    ("complex_care", "Complex care", "complex care", 20, 0.93, 0.56),
    ("short_stay", "Short stay", "short stay", 20, 0.82, 0.48),
    ("procedural_recovery", "Procedural recovery", "procedural", 18, 0.79, 0.35),
]

PROGRAMS = [
    ("respiratory", "Respiratory", 610, 0.92, 0.82),
    ("cardiology", "Cardiology", 480, 0.74, 0.44),
    ("neurology", "Neurology", 720, 0.84, 0.58),
    ("surgery_follow_up", "Surgery follow-up", 690, 0.76, 0.36),
    ("oncology_survivorship", "Oncology survivorship", 380, 0.62, 0.3),
    ("complex_care", "Complex care", 810, 0.88, 0.55),
    ("mental_health", "Mental health", 1160, 0.96, 0.4),
    ("diabetes_endocrinology", "Diabetes/endocrinology", 760, 0.82, 0.34),
    ("gastroenterology", "Gastroenterology", 640, 0.78, 0.39),
    ("nephrology", "Nephrology", 360, 0.58, 0.25),
    ("rheumatology", "Rheumatology", 420, 0.67, 0.27),
    ("diagnostics", "Diagnostics", 910, 0.86, 0.45),
    ("post_discharge_follow_up", "Post-discharge follow-up", 520, 0.72, 0.5),
    ("virtual_outreach", "Virtual/outreach", 460, 0.64, 0.33),
]

INPATIENT_MODELS = [
    "INPT_OCCUPANCY_FORECAST",
    "PICU_NICU_PRESSURE",
    "DISCHARGE_BARRIER_RISK",
]

AMBULATORY_MODELS = [
    "AMBULATORY_ACCESS_FORECAST",
    "URGENT_WAITLIST_BREACH_RISK",
    "NO_SHOW_LATE_CANCEL_RISK",
]

OPEN_SOURCE_IDS = (
    "SRC_OPEN_RESPIRATORY_VIRUS_DASHBOARD,"
    "SRC_OPEN_AQHI_SMOKE_CONTEXT,"
    "SRC_OPEN_SCHOOL_HOLIDAY_CALENDAR,"
    "SRC_OPEN_STATCAN_PED_POPULATION"
)


def write_json(name: str, payload: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
    SAMPLE.mkdir(parents=True, exist_ok=True)
    path = SAMPLE / name
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    for row in rows[1:]:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def pct(value: float) -> float:
    return round(value, 3)


def source_row(
    source_id: str,
    curated_view: str,
    domain: str,
    grain: str,
    fields: str,
    cadence: str,
    classification: str,
    usage: str,
    sensitivity: str = "aggregate synthetic only",
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "curated_view": curated_view,
        "source_view_name": curated_view.split(".")[-1],
        "source_domain": domain,
        "grain": grain,
        "fields": fields,
        "field_types": "synthetic ids, categorical dimensions, timestamps, numeric measures, flags, and JSON payloads",
        "cadence": cadence,
        "classification": classification,
        "phi_sensitivity": sensitivity,
        "dashboard_usage": usage,
        "validation_rules": "view present, fields populated, freshness, row count, timestamp logic, denominator owner approval, small-cell suppression",
        "future_mapping_placeholder": f"CURATED_{source_id}_VIEW_MAPPING_TBD",
    }


def v5_sources() -> list[dict[str, Any]]:
    sources = v3.source_registry()
    extras = [
        source_row(
            "SRC_SYNTH_HR_SHIFT_ROSTER",
            "CANONICAL.VW_SYNTH_HR_SHIFT_ROSTER",
            "staffing / workforce",
            "site-unit-shift and site-program-day",
            "site_id, unit_or_program_id, role_group, required_hours, available_hours, absence_hours, overtime_hours, agency_hours",
            "shift to daily",
            "direct_operational_signal",
            "effective beds, program capacity, HR constraint overlays, scenario levers",
            "staff aggregate",
        ),
        source_row(
            "SRC_SYNTH_HR_FLOAT_POOL",
            "CANONICAL.VW_SYNTH_HR_FLOAT_POOL",
            "staffing / workforce",
            "site-role-day",
            "site_id, role_group, float_pool_hours, redeployable_hours, skill_match_rate, orientation_constraint_flag",
            "daily",
            "direct_operational_signal",
            "scenario float-pool and cross-coverage constraints",
            "staff aggregate",
        ),
        source_row(
            "SRC_SYNTH_FINANCE_COST_CENTER",
            "FINANCE.VW_SYNTH_COST_CENTER_DAY",
            "finance / resource",
            "site-cost-centre-day",
            "site_id, cost_center_group, worked_hours_cost, overtime_cost, agency_cost, supply_cost, resource_ceiling",
            "daily to monthly",
            "direct_operational_signal",
            "resource ceiling, marginal staffing cost, diagnostic and clinic template constraints",
            "finance aggregate",
        ),
        source_row(
            "SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE",
            "FINANCE.VW_SYNTH_RESOURCE_ENVELOPE",
            "finance / resource",
            "site-service-program-period",
            "site_id, service_line, program_id, budget_proxy, committed_proxy, available_proxy, variance_proxy",
            "weekly to monthly",
            "derived_operational_intelligence",
            "scenario feasibility, marginal resource use, trade-off cards",
            "finance aggregate",
        ),
        source_row(
            "SRC_OPEN_RESPIRATORY_VIRUS_DASHBOARD",
            "OPEN_DATA.VW_ALBERTA_RESPIRATORY_VIRUS_CONTEXT",
            "open data",
            "zone-week",
            "week_start, zone_proxy, rsv_index, influenza_index, covid_index, outbreak_proxy, lab_positivity_proxy",
            "weekly cached public context",
            "open_public_context",
            "forecast lift and respiratory-surge scenarios",
            "public open data",
        ),
        source_row(
            "SRC_OPEN_AQHI_SMOKE_CONTEXT",
            "OPEN_DATA.VW_AQHI_SMOKE_WEATHER_CONTEXT",
            "open data",
            "site-day",
            "date, site_id, aqhi_max_proxy, smoke_pm25_proxy, temperature_proxy, precipitation_proxy",
            "daily cached public context",
            "open_public_context",
            "respiratory demand, no-show reliability, outreach feasibility",
            "public open data",
        ),
        source_row(
            "SRC_OPEN_SCHOOL_HOLIDAY_CALENDAR",
            "OPEN_DATA.VW_SCHOOL_HOLIDAY_CALENDAR",
            "open data",
            "region-date",
            "date, region_proxy, school_break_flag, statutory_holiday_flag, exam_period_flag, pd_day_flag",
            "annual calendar with daily expansion",
            "open_public_context",
            "attendance patterns, ED demand, clinic template assumptions",
            "public open data",
        ),
        source_row(
            "SRC_OPEN_STATCAN_PED_POPULATION",
            "OPEN_DATA.VW_STATCAN_PED_POPULATION",
            "open data",
            "province-age-band-year",
            "year, age_band, province, population_estimate_proxy, growth_index",
            "annual cached public context",
            "open_public_context",
            "denominators and demand growth assumptions",
            "public open data",
        ),
        source_row(
            "SRC_OPEN_ED_WAIT_TIME_LOGIC",
            "OPEN_DATA.VW_AHS_ED_WAIT_TIME_STYLE_LOGIC",
            "open data",
            "site-minute",
            "site_id, calculated_at, queued_by_acuity_proxy, physician_service_rate_proxy, resource_constraint_proxy, estimated_wait_minutes",
            "2-minute synthetic replay of public-style calculation",
            "open_public_context",
            "ED-boarder and triage-to-physician wait-time style context",
            "public-method synthetic proxy",
        ),
    ]
    known = {row["source_id"] for row in sources}
    sources.extend(row for row in extras if row["source_id"] not in known)
    return sources


def v5_readiness(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = v3.direct_link_validation(sources)
    review_ids = {
        "SRC_SYNTH_HR_FLOAT_POOL",
        "SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE",
        "SRC_OPEN_AQHI_SMOKE_CONTEXT",
        "SRC_OPEN_ED_WAIT_TIME_LOGIC",
    }
    for row in rows:
        if row["source_id"] in review_ids:
            row["overall_readiness"] = "review"
            row["stoplight"] = "yellow"
            row["field_populated"] = "review"
            row["metric_definition_approved"] = "review"
            row["caveat"] = "Synthetic v5 readiness: requires local owner review before production use."
    return rows


def open_context_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = date(2025, 6, 16)
    for index in range(52):
        current = start + timedelta(days=7 * index)
        winter_peak = math.exp(-((index - 31) ** 2) / 115)
        smoke_peak = math.exp(-((index - 8) ** 2) / 38) + 0.6 * math.exp(-((index - 49) ** 2) / 32)
        school_break = current.month in {7, 8} or current.month == 12 and current.day >= 20 or current.month == 1 and current.day <= 5 or current.month == 3 and 20 <= current.day <= 31
        holiday = current.month == 12 and current.day >= 23 or current.month == 1 and current.day <= 2
        rows.append(
            {
                "week_index": index + 1,
                "week_start": current.isoformat(),
                "respiratory_activity_index": round(0.42 + 0.62 * winter_peak + 0.05 * math.sin(index / 2.6), 3),
                "rsv_index": round(0.2 + 0.78 * math.exp(-((index - 28) ** 2) / 78), 3),
                "influenza_index": round(0.16 + 0.68 * math.exp(-((index - 33) ** 2) / 95), 3),
                "covid_index": round(0.24 + 0.12 * math.sin(index / 4.3), 3),
                "aqhi_max_proxy": round(2.1 + 5.4 * smoke_peak + 0.4 * math.sin(index / 1.8), 2),
                "smoke_pm25_proxy": round(4.8 + 31 * smoke_peak, 1),
                "mean_temperature_c_proxy": round(6 + 19 * math.sin((index - 5) / 52 * 2 * math.pi), 1),
                "school_break_flag": school_break,
                "holiday_flag": holiday,
                "pediatric_population_index": round(1.0 + 0.018 * (index / 52), 3),
                "ed_wait_pressure_proxy": round(0.54 + 0.28 * winter_peak + 0.12 * smoke_peak + (0.07 if school_break else 0), 3),
                "source_ids": OPEN_SOURCE_IDS + ",SRC_OPEN_ED_WAIT_TIME_LOGIC",
                "classification": "open data",
                "source_readiness": "review" if smoke_peak > 0.75 else "ready",
            }
        )
    return rows


def latest_context(open_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return open_rows[-1]


def unit_payload(open_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    context = latest_context(open_rows)
    unit_rows: list[dict[str, Any]] = []
    pressure_rows: list[dict[str, Any]] = []
    timeline_rows: list[dict[str, Any]] = []
    flow_rows: list[dict[str, Any]] = []
    forecast_rows: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    source_ids = (
        "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_BED_STATUS,SRC_SYNTH_ED_VISITS,"
        "SRC_SYNTH_TRANSFER_REQUESTS,SRC_SYNTH_DISCHARGE_BARRIERS,SRC_SYNTH_HR_SHIFT_ROSTER,"
        "SRC_SYNTH_FINANCE_COST_CENTER," + OPEN_SOURCE_IDS
    )

    for site_index, (site_id, site_name, catchment, site_scale) in enumerate(SITES):
        for service_index, (service_id, service_name, service_group, base_beds, pressure, respiratory_weight) in enumerate(SERVICES):
            unit_id = f"{site_id}_{service_id}".upper()
            respiratory_lift = float(context["respiratory_activity_index"]) * respiratory_weight * 0.07
            smoke_lift = min(float(context["aqhi_max_proxy"]) / 10, 1.1) * respiratory_weight * 0.035
            calendar_lift = 0.035 if context["school_break_flag"] else 0.012
            occupancy = min(1.19, pressure + respiratory_lift + smoke_lift + calendar_lift + site_index * 0.012 - service_index * 0.004)
            physical_beds = max(8, int(base_beds * site_scale))
            staffed_beds = max(6, round(physical_beds * (0.92 - 0.02 * ((service_index + site_index) % 3))))
            effective_beds_lost = max(0, round((0.04 + 0.03 * (occupancy > 0.95) + 0.015 * site_index) * staffed_beds))
            effective_beds = max(4, staffed_beds - effective_beds_lost)
            census = min(physical_beds + 4, round(effective_beds * occupancy))
            gap_pct = pct(max(0.02, min(0.24, occupancy - 0.86 + 0.025 * ((service_index + 1) % 4))))
            ed_boarders = max(0, round((occupancy - 0.78) * 16 + respiratory_weight * 5 + site_index))
            transfer_in = max(0, round((occupancy - 0.74) * 5 + (1 if service_id in {"picu", "nicu", "cardiology"} else 0)))
            transfer_out = max(0, round((occupancy - 0.96) * 4))
            discharge_barriers = max(1, round(census * (0.15 + 0.03 * ((service_index + site_index) % 4))))
            predicted_admits = max(1, round(2 + census * (0.13 + respiratory_weight * 0.06)))
            predicted_discharges = max(1, round(census * (0.11 + 0.035 * (service_id in {"short_stay", "procedural_recovery"}))))
            hr_gap = round(staffed_beds * gap_pct * 5.8 + (2 if service_id in {"picu", "nicu"} else 0), 1)
            allied_gap = round(discharge_barriers * 0.7 + respiratory_weight * 1.8, 1)
            staffing_cost = round(hr_gap * 0.19 + transfer_in * 0.45 + (1.7 if occupancy > 1.0 else 0), 1)
            resource_ceiling = round(7.5 + staffed_beds * 0.18 + site_index * 1.2, 1)
            margin_pressure = round(max(0, staffing_cost - resource_ceiling * 0.62), 1)
            readiness = "review" if service_id in {"respiratory", "procedural_recovery"} or occupancy > 1.0 else "ready"
            tone = "high" if occupancy >= 1.0 or ed_boarders >= 8 else "watch" if occupancy >= 0.92 else "good"
            models = ",".join(INPATIENT_MODELS)
            warning_ids = []
            if occupancy >= 0.98:
                warning_ids.append(f"WARN_{unit_id}_OCCUPANCY")
            if hr_gap >= 9:
                warning_ids.append(f"WARN_{unit_id}_HR")
            row = {
                "site_id": site_id,
                "site_name": site_name,
                "catchment": catchment,
                "service_id": service_id,
                "service_line": service_name,
                "service_group": service_group,
                "unit_id": unit_id,
                "unit_name": f"{service_name} unit",
                "capacity": physical_beds,
                "physical_beds": physical_beds,
                "staffed_beds": staffed_beds,
                "effective_beds": effective_beds,
                "effective_beds_lost": effective_beds_lost,
                "census": census,
                "occupancy_pct": pct(census / effective_beds),
                "staffing_gap_pct": gap_pct,
                "ed_boarders": ed_boarders,
                "ed_admissions_awaiting_bed": ed_boarders,
                "consult_bottleneck_count": max(1, round(ed_boarders * 0.35 + transfer_in)),
                "transfer_in_requests": transfer_in,
                "transfer_out_requests": transfer_out,
                "discharge_barriers": discharge_barriers,
                "predicted_admissions_24h": predicted_admits,
                "predicted_discharges_24h": predicted_discharges,
                "rn_required": round(staffed_beds * 4.8, 1),
                "rn_available": round(staffed_beds * 4.8 - hr_gap, 1),
                "staffing_gap_hours": hr_gap,
                "required_hours": round(staffed_beds * 5.4 + census * 0.4, 1),
                "available_hours": round(staffed_beds * 5.4 + census * 0.4 - hr_gap, 1),
                "allied_health_gap_hours": allied_gap,
                "hr_risk_index": pct(min(1.2, gap_pct * 3.2 + allied_gap / 50)),
                "variable_staffing_cost_k": staffing_cost,
                "resource_ceiling_k": resource_ceiling,
                "margin_pressure_k": margin_pressure,
                "respiratory_context_index": context["respiratory_activity_index"],
                "aqhi_smoke_index": context["aqhi_max_proxy"],
                "school_calendar_pressure": 1 if context["school_break_flag"] else 0,
                "open_data_adjustment": pct(respiratory_lift + smoke_lift + calendar_lift),
                "source_readiness": readiness,
                "classification": "derived",
                "confidence": "medium-high" if readiness == "ready" else "medium",
                "tone": tone,
                "lineage_panel_id": "PANEL_INPATIENT_COMMAND",
                "source_ids": source_ids,
                "model_ids": models,
                "warning_ids": ",".join(warning_ids),
                "caveat": "Synthetic aggregate unit posture; not validated for clinical decision-making.",
            }
            unit_rows.append(row)
            pressure_rows.append(row.copy())
            flow_rows.append(
                {
                    **row,
                    "driver": service_name,
                    "pressure_score": round(row["occupancy_pct"] * 42 + ed_boarders * 2.2 + hr_gap * 1.1, 1),
                }
            )
            for hour in [0, 3, 6, 12, 18, 24, 48, 72]:
                horizon_lift = 0.015 * math.sin((hour + service_index * 3) / 11) + respiratory_weight * hour / 72 * 0.04
                prediction = max(0.45, min(1.25, row["occupancy_pct"] + horizon_lift))
                timeline_rows.append(
                    {
                        "site_id": site_id,
                        "service_id": service_id,
                        "service_line": service_name,
                        "unit_id": unit_id,
                        "unit_name": row["unit_name"],
                        "hour": hour,
                        "predicted_occupancy": pct(prediction),
                        "lower": pct(max(0.35, prediction - 0.055 - hour / 2200)),
                        "upper": pct(min(1.35, prediction + 0.065 + hour / 1900)),
                        "predicted_admissions": max(0, round(predicted_admits * (hour or 1) / 24)),
                        "predicted_discharges": max(0, round(predicted_discharges * (hour or 1) / 24)),
                        "staffing_gap_hours": round(hr_gap * (1 + hour / 180), 1),
                        "source_ids": source_ids,
                        "classification": "modelled",
                        "source_readiness": readiness,
                    }
                )
            for horizon in [6, 12, 24, 48, 72]:
                forecast_rows.append(
                    {
                        "site_id": site_id,
                        "service_id": service_id,
                        "service_line": service_name,
                        "unit_id": unit_id,
                        "unit_name": row["unit_name"],
                        "hour": horizon,
                        "forecast_value": pct(row["occupancy_pct"] + respiratory_weight * horizon / 900 + smoke_lift),
                        "lower": pct(row["occupancy_pct"] - 0.045),
                        "upper": pct(row["occupancy_pct"] + 0.085 + respiratory_weight * horizon / 1100),
                        "respiratory_open_data_lift": pct(respiratory_lift),
                        "aqhi_smoke_open_data_lift": pct(smoke_lift),
                        "calendar_open_data_lift": pct(calendar_lift),
                        "source_ids": source_ids,
                        "classification": "modelled",
                    }
                )
            for warning_id in warning_ids:
                warnings.append(
                    {
                        "warning_id": warning_id,
                        "site_id": site_id,
                        "site_name": site_name,
                        "service_id": service_id,
                        "service_line": service_name,
                        "unit_id": unit_id,
                        "unit_name": row["unit_name"],
                        "severity": "high" if warning_id.endswith("OCCUPANCY") else "medium",
                        "title": "Effective bed pressure" if warning_id.endswith("OCCUPANCY") else "Workforce constraint",
                        "message": (
                            f"{service_name} at {site_name} is projected above staffed capacity."
                            if warning_id.endswith("OCCUPANCY")
                            else f"{service_name} has {hr_gap} synthetic staffing gap hours in the next shift."
                        ),
                        "metric_id": "METRIC_OCCUPANCY" if warning_id.endswith("OCCUPANCY") else "METRIC_EFFECTIVE_STAFFED_BEDS",
                        "model_ids": models,
                        "source_ids": source_ids,
                        "source_readiness": readiness,
                        "classification": "modelled" if warning_id.endswith("OCCUPANCY") else "HR",
                        "recommended_action": "Open unit drawer, review discharge barriers, HR float-pool availability, and resource ceiling.",
                    }
                )
    return {
        "unitPressure": pressure_rows,
        "unitDetails": unit_rows,
        "unitTimeline": timeline_rows,
        "flowDrivers": flow_rows,
        "forecast": forecast_rows,
        "warnings": warnings,
    }


def ambulatory_payload(open_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    context = latest_context(open_rows)
    access_rows: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []
    timeline_rows: list[dict[str, Any]] = []
    no_show_rows: list[dict[str, Any]] = []
    forecast_rows: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    source_ids = (
        "SRC_SYNTH_REFERRALS,SRC_SYNTH_REFERRAL_TRIAGE,SRC_SYNTH_WAITLIST_SNAPSHOTS,"
        "SRC_SYNTH_CLINIC_TEMPLATES,SRC_SYNTH_PROVIDER_AVAILABILITY,SRC_SYNTH_NO_SHOW_LATE_CANCEL,"
        "SRC_SYNTH_DIAGNOSTIC_READINESS,SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE,"
        + OPEN_SOURCE_IDS
    )
    for site_index, (site_id, site_name, catchment, site_scale) in enumerate(SITES):
        for program_index, (program_id, program_name, base_waitlist, pressure, open_weight) in enumerate(PROGRAMS):
            referrals = round(base_waitlist * (0.115 + open_weight * 0.03) * site_scale)
            waitlist = round(base_waitlist * site_scale * (1 + 0.12 * pressure + 0.04 * site_index))
            urgent = round(waitlist * (0.12 + pressure * 0.05))
            routine = waitlist - urgent
            tna = max(3, round(18 + pressure * 54 + open_weight * float(context["respiratory_activity_index"]) * 9 - site_index * 2))
            template_capacity = max(20, round(referrals * (0.82 + 0.08 * (program_id in {"virtual_outreach", "post_discharge_follow_up"}))))
            provider_capacity = round(template_capacity * (0.9 - 0.04 * ((program_index + site_index) % 4)))
            allied_capacity = round(template_capacity * (0.32 + open_weight * 0.08))
            no_show = pct(0.055 + pressure * 0.032 + (float(context["aqhi_max_proxy"]) / 180) + (0.018 if context["school_break_flag"] else 0))
            diagnostics_ready = pct(max(0.48, min(0.94, 0.88 - pressure * 0.18 + (0.07 if program_id in {"post_discharge_follow_up", "virtual_outreach"} else 0))))
            followup_overdue = round(waitlist * (0.06 + pressure * 0.05))
            hr_gap = round(max(0, (template_capacity - provider_capacity) * 0.42 + pressure * 4.2), 1)
            resource_ceiling = round(6.8 + template_capacity * 0.045 + site_index * 0.7, 1)
            marginal_resource = round((referrals / 100) * 1.5 + hr_gap * 0.16 + (1 - diagnostics_ready) * 7, 1)
            readiness = "review" if program_id in {"diagnostics", "mental_health", "virtual_outreach"} else "ready"
            tone = "high" if tna >= 70 or urgent >= 130 else "watch" if tna >= 45 else "good"
            warning_ids = []
            if tna >= 64:
                warning_ids.append(f"WARN_{site_id}_{program_id}_TNA".upper())
            if diagnostics_ready < 0.66:
                warning_ids.append(f"WARN_{site_id}_{program_id}_DIAG".upper())
            row = {
                "site_id": site_id,
                "site_name": site_name,
                "catchment": catchment,
                "program_id": program_id,
                "program": program_name,
                "referrals_4w": referrals,
                "triage_volume_4w": round(referrals * 0.94),
                "urgent_referrals_4w": round(referrals * (0.18 + pressure * 0.06)),
                "waitlist_total": waitlist,
                "urgent_waitlist": urgent,
                "routine_waitlist": routine,
                "third_next_available_days": tna,
                "template_capacity_4w": template_capacity,
                "template_gap_4w": round(referrals - template_capacity),
                "no_show_rate": no_show,
                "diagnostic_readiness": diagnostics_ready,
                "followup_overdue": followup_overdue,
                "provider_capacity_sessions_4w": provider_capacity,
                "allied_health_capacity_sessions_4w": allied_capacity,
                "hr_gap_sessions_4w": hr_gap,
                "resource_ceiling_k": resource_ceiling,
                "marginal_resource_need_k": marginal_resource,
                "finance_pressure_k": round(max(0, marginal_resource - resource_ceiling * 0.55), 1),
                "respiratory_context_index": context["respiratory_activity_index"],
                "aqhi_smoke_index": context["aqhi_max_proxy"],
                "calendar_open_data_lift": pct(0.04 if context["school_break_flag"] else 0.012),
                "open_data_adjustment": pct(open_weight * float(context["respiratory_activity_index"]) * 0.04 + no_show),
                "urgent_breach_risk": pct(min(0.92, 0.16 + pressure * 0.4 + urgent / max(waitlist, 1) * 0.6)),
                "source_readiness": readiness,
                "classification": "derived",
                "confidence": "medium-high" if readiness == "ready" else "medium",
                "tone": tone,
                "lineage_panel_id": "PANEL_AMBULATORY_COMMAND",
                "source_ids": source_ids,
                "model_ids": ",".join(AMBULATORY_MODELS),
                "warning_ids": ",".join(warning_ids),
                "caveat": "Synthetic aggregate access metrics; no patient-level display.",
            }
            access_rows.append(row.copy())
            detail_rows.append(row)
            no_show_rows.append(
                {
                    **row,
                    "program": program_name,
                    "impact_score": round(35 + no_show * 260 + pressure * 18, 1),
                    "effort_score": round(1.6 + pressure * 3.5, 1),
                    "operational_risk_score": round(1.2 + (1 - diagnostics_ready) * 4, 1),
                    "recovered_slots": round(no_show * template_capacity * 0.35),
                }
            )
            for week in range(1, 27):
                seasonal = math.sin((week + program_index) / 5.4) * 0.08
                trend = 1 + week * 0.006 + open_weight * float(context["respiratory_activity_index"]) * 0.03
                forecast_waitlist = max(80, round(waitlist * trend * (1 + seasonal)))
                timeline_rows.append(
                    {
                        "site_id": site_id,
                        "site_name": site_name,
                        "program_id": program_id,
                        "program": program_name,
                        "week": week,
                        "week_start": (date(2026, 6, 15) + timedelta(days=(week - 1) * 7)).isoformat(),
                        "forecast_waitlist": forecast_waitlist,
                        "lower": round(forecast_waitlist * 0.91),
                        "upper": round(forecast_waitlist * 1.12),
                        "third_next_available_days": max(2, round(tna * (1 + seasonal * 0.5) + week * 0.45)),
                        "referral_forecast": round(referrals * (1 + open_weight * week / 90)),
                        "diagnostic_readiness": diagnostics_ready,
                        "source_ids": source_ids,
                        "classification": "modelled",
                        "source_readiness": readiness,
                    }
                )
            for week in [2, 4, 8, 12, 26]:
                forecast_rows.append(
                    {
                        "site_id": site_id,
                        "program_id": program_id,
                        "program": program_name,
                        "week": week,
                        "forecast_value": round(waitlist * (1 + pressure * week / 240 + open_weight * float(context["respiratory_activity_index"]) / 15)),
                        "lower": round(waitlist * 0.9),
                        "upper": round(waitlist * (1.08 + pressure * week / 180)),
                        "respiratory_open_data_lift": pct(open_weight * float(context["respiratory_activity_index"]) * 0.04),
                        "aqhi_smoke_open_data_lift": pct(float(context["aqhi_max_proxy"]) / 260),
                        "calendar_open_data_lift": pct(0.04 if context["school_break_flag"] else 0.012),
                        "source_ids": source_ids,
                        "classification": "modelled",
                    }
                )
            for warning_id in warning_ids:
                warnings.append(
                    {
                        "warning_id": warning_id,
                        "site_id": site_id,
                        "site_name": site_name,
                        "program_id": program_id,
                        "program": program_name,
                        "severity": "high" if warning_id.endswith("TNA") else "medium",
                        "title": "Access breach risk" if warning_id.endswith("TNA") else "Diagnostic readiness constraint",
                        "message": (
                            f"{program_name} TNA is {tna} synthetic days at {site_name}."
                            if warning_id.endswith("TNA")
                            else f"{program_name} diagnostics readiness is {round(diagnostics_ready * 100)}%."
                        ),
                        "metric_id": "METRIC_WAITLIST_PRESSURE" if warning_id.endswith("TNA") else "METRIC_DIAGNOSTIC_READINESS",
                        "model_ids": ",".join(AMBULATORY_MODELS),
                        "source_ids": source_ids,
                        "source_readiness": readiness,
                        "classification": "modelled",
                        "recommended_action": "Open program drawer, compare triage, template, diagnostics, HR, and resource constraints.",
                    }
                )
    return {
        "programAccess": access_rows,
        "programDetails": detail_rows,
        "programTimeline": timeline_rows,
        "noShowFrontier": no_show_rows,
        "forecast": forecast_rows,
        "warnings": warnings,
    }


def metric_registry() -> list[dict[str, Any]]:
    base = v3.metric_registry()
    extra = [
        ("METRIC_EFFECTIVE_STAFFED_BEDS", "Effective staffed beds", "sum(staffed_beds - effective_beds_lost)", "derived", "Patient Flow / HR", "approved"),
        ("METRIC_ED_BOARDERS", "ED boarders awaiting pediatric inpatient bed", "sum(ed_admissions_awaiting_bed)", "direct", "Patient Flow", "approved"),
        ("METRIC_HR_GAP_HOURS", "HR gap hours", "sum(required_hours - available_hours)", "HR", "Workforce", "review"),
        ("METRIC_FINANCE_RESOURCE_PRESSURE", "Resource pressure proxy", "marginal_resource_need_k versus resource_ceiling_k", "finance", "Finance partner", "review"),
        ("METRIC_OPEN_CONTEXT_LIFT", "Open-context forecast lift", "respiratory + AQHI/smoke + calendar adjustment", "open data", "Analytics", "approved"),
        ("METRIC_TNA", "Third next available", "synthetic template-derived days to third available appointment", "derived", "Ambulatory operations", "approved"),
    ]
    known = {row["metric_id"] for row in base}
    for metric_id, name, formula, classification, owner, validation in extra:
        if metric_id in known:
            continue
        base.append(
            {
                "metric_id": metric_id,
                "name": name,
                "formula": formula,
                "classification": classification,
                "owner": owner,
                "validation": validation,
                "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE," + OPEN_SOURCE_IDS,
                "lineage_summary": "Synthetic v5 command-centre metric; production use requires local definition owner approval.",
            }
        )
    return base


def model_registry() -> list[dict[str, Any]]:
    models = []
    for index, row in enumerate(v3.model_registry()):
        source_fields = [
            "site_id",
            "unit_id/program_id",
            "hour_ts/week_start",
            "census",
            "staffed_beds",
            "effective_beds",
            "referrals",
            "waitlist_total",
            "staffing_gap_hours",
            "resource_ceiling_k",
            "respiratory_activity_index",
            "aqhi_max_proxy",
            "school_break_flag",
        ]
        row = {
            **row,
            "source_fields": ", ".join(source_fields),
            "feature_families": "flow, capacity, staffing, discharge/access barriers, finance/resource proxy, public open-context, calendar, site/service seasonality",
            "proxy_coefficients": json.dumps(
                {
                    "occupancy": round(0.22 + index * 0.01, 3),
                    "staffing_gap": round(0.16 + (index % 4) * 0.018, 3),
                    "respiratory_activity": round(0.11 + (index % 5) * 0.012, 3),
                    "resource_ceiling": round(-0.08 - (index % 3) * 0.01, 3),
                    "school_break": round(0.04 + (index % 2) * 0.01, 3),
                }
            ),
            "threshold_logic": "Green below 80th synthetic percentile; watch above 80th; high above 92nd or if source readiness regresses.",
            "calibration": row.get("calibration_status", "review required"),
            "validation": row.get("subgroup_performance", "synthetic backtest by site, service, age-band proxy, season, and priority"),
            "drift": row.get("drift_status", "watch"),
            "source_lineage": "Curated synthetic Snowflake views only; no raw EHR table names, direct identifiers, or clinical decision automation.",
            "panels_using_it": row.get("panels", "system posture, inpatient, ambulatory, scenario lab, gatekeeper"),
            "source_ids": "SRC_MODEL_PREDICTIONS,SRC_MODEL_VALIDATION_RESULTS,SRC_MODEL_DRIFT_RESULTS,SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE," + OPEN_SOURCE_IDS,
        }
        models.append(row)
    return models


def scenario_payload(inpatient: dict[str, list[dict[str, Any]]], ambulatory: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    scenarios = [
        ("SCN-INPT-STEPDOWN", "inpatient", "Open protected step-down capacity", 86, 3.6, 2.4, "boarder_hours", 142),
        ("SCN-INPT-DISCHARGE", "inpatient", "Pull forward discharge barrier resolution", 74, 2.8, 2.0, "effective_bed_hours", 118),
        ("SCN-AMB-SLOTS", "ambulatory", "Protect urgent ambulatory slots", 82, 3.2, 2.3, "waitlist_days_reduced", 104),
        ("SCN-AMB-VIRTUAL", "ambulatory", "Shift eligible follow-up to virtual/outreach", 69, 2.6, 1.9, "templates_recovered", 76),
        ("SCN-HR-FLOAT", "HR/workforce", "Deploy pediatric float-pool hours", 78, 3.9, 3.1, "effective_capacity_gain", 92),
        ("SCN-HR-CROSSCOVER", "HR/workforce", "Cross-cover allied health bottlenecks", 64, 2.9, 2.7, "barriers_cleared", 58),
        ("SCN-FIN-RESOURCE", "finance/resource", "Release constrained surge resource envelope", 71, 4.4, 3.5, "feasible_capacity_gain", 84),
        ("SCN-OPEN-RESP", "open data", "Respiratory/AQHI surge pre-brief", 62, 2.1, 1.6, "forecast_error_reduced", 46),
    ]
    rows: list[dict[str, Any]] = []
    for scenario_id, domain, name, impact, effort, risk, outcome, value in scenarios:
        affected_units = ",".join(row["unit_id"] for row in inpatient["unitDetails"] if row["service_id"] in {"respiratory", "picu", "general_pediatrics", "short_stay"})[:360]
        affected_programs = ",".join(row["program_id"] for row in ambulatory["programDetails"] if row["program_id"] in {"respiratory", "post_discharge_follow_up", "diagnostics", "mental_health"})[:260]
        rows.append(
            {
                "scenario_id": scenario_id,
                "domain": domain,
                "scenario_name": name,
                "impact_score": impact,
                "effort_score": effort,
                "operational_risk_score": risk,
                "primary_outcome": outcome,
                "outcome_value": value,
                "baseline_value": round(value * 1.28),
                "scenario_value": value,
                "confidence_low": round(value * 0.82),
                "confidence_high": round(value * 1.18),
                "hr_hours_required": round(16 + effort * 7.5),
                "cost_k_required": round(8 + effort * 4.3 + risk * 2.2, 1),
                "resource_ceiling_k": round(22 + impact * 0.21, 1),
                "tradeoff": "Improves flow/access but consumes scarce workforce or resource envelope.",
                "affected_units": affected_units,
                "affected_programs": affected_programs,
                "readiness": "review" if "finance" in domain or "open" in domain else "ready",
                "classification": "modelled",
                "writeback_table": "APP.SCENARIO_RUN_LOG",
                "source_ids": "SRC_MODEL_PREDICTIONS,SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE," + OPEN_SOURCE_IDS,
            }
        )
    controls = [
        ("inpatient_stepdown_beds", "inpatient", 0, 12, 4, "beds", 5.8, 2.2, "SCN-INPT-STEPDOWN"),
        ("discharge_pull_forward_hours", "inpatient", 0, 8, 3, "hours", 7.4, 1.1, "SCN-INPT-DISCHARGE"),
        ("urgent_slot_protection_pct", "ambulatory", 0, 35, 12, "%", 4.9, 0.8, "SCN-AMB-SLOTS"),
        ("virtual_followup_shift_pct", "ambulatory", 0, 45, 16, "%", 3.2, 0.6, "SCN-AMB-VIRTUAL"),
        ("float_pool_hours", "HR/workforce", 0, 160, 48, "hours", 0.7, 0.18, "SCN-HR-FLOAT"),
        ("allied_cross_cover_sessions", "HR/workforce", 0, 42, 10, "sessions", 2.8, 0.5, "SCN-HR-CROSSCOVER"),
        ("resource_ceiling_release_k", "finance/resource", 0, 90, 24, "$k", 1.1, 1.0, "SCN-FIN-RESOURCE"),
        ("respiratory_forecast_lift_pct", "open data", -10, 35, 8, "%", 2.4, 0.2, "SCN-OPEN-RESP"),
        ("aqhi_smoke_lift_pct", "open data", -5, 25, 6, "%", 1.6, 0.12, "SCN-OPEN-RESP"),
        ("school_break_attendance_lift_pct", "open data", -8, 18, 4, "%", 1.1, 0.08, "SCN-OPEN-RESP"),
    ]
    control_rows = [
        {
            "control_id": control_id,
            "domain": domain,
            "min_value": min_value,
            "max_value": max_value,
            "default_value": default,
            "unit": unit,
            "impact_per_unit": impact_per_unit,
            "cost_k_per_unit": cost_per_unit,
            "scenario_id": scenario_id,
            "sensitivity_low": round(impact_per_unit * 0.66, 2),
            "sensitivity_high": round(impact_per_unit * 1.32, 2),
            "source_ids": "SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE," + OPEN_SOURCE_IDS,
        }
        for control_id, domain, min_value, max_value, default, unit, impact_per_unit, cost_per_unit, scenario_id in controls
    ]
    baselines = [
        {"metric": "boarder_hours", "baseline": 318, "classification": "derived", "source_ids": "SRC_SYNTH_ED_VISITS,SRC_SYNTH_UNIT_CENSUS_HOURLY"},
        {"metric": "effective_bed_hours", "baseline": 540, "classification": "derived", "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_HR_SHIFT_ROSTER"},
        {"metric": "waitlist_days_reduced", "baseline": 0, "classification": "modelled", "source_ids": "SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_CLINIC_TEMPLATES"},
        {"metric": "templates_recovered", "baseline": 0, "classification": "modelled", "source_ids": "SRC_SYNTH_CLINIC_TEMPLATES,SRC_SYNTH_PROVIDER_AVAILABILITY"},
        {"metric": "effective_capacity_gain", "baseline": 0, "classification": "HR", "source_ids": "SRC_SYNTH_HR_FLOAT_POOL"},
        {"metric": "feasible_capacity_gain", "baseline": 0, "classification": "finance", "source_ids": "SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE"},
    ]
    comparisons = [
        {
            "scenario_id": row["scenario_id"],
            "metric": row["primary_outcome"],
            "baseline": row["baseline_value"],
            "scenario": row["scenario_value"],
            "delta": round(row["baseline_value"] - row["scenario_value"], 1),
            "confidence_low": row["confidence_low"],
            "confidence_high": row["confidence_high"],
            "source_ids": row["source_ids"],
        }
        for row in rows
    ]
    return {"scenarios": rows, "comparisons": comparisons, "baselines": baselines, "controlRanges": control_rows}


def system_posture(inpatient: dict[str, list[dict[str, Any]]], ambulatory: dict[str, list[dict[str, Any]]], open_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    units = inpatient["unitDetails"]
    programs = ambulatory["programDetails"]
    census = sum(int(row["census"]) for row in units)
    effective = sum(int(row["effective_beds"]) for row in units)
    boarders = sum(int(row["ed_boarders"]) for row in units)
    hr_gap = sum(float(row["staffing_gap_hours"]) for row in units)
    waitlist = sum(int(row["waitlist_total"]) for row in programs)
    tna = sum(float(row["third_next_available_days"]) for row in programs) / len(programs)
    context = latest_context(open_rows)
    return {
        "kpis": [
            {
                "label": "Network occupancy",
                "value": f"{round(census / effective * 100, 1)}%",
                "detail": "Census divided by effective staffed beds after HR constraints",
                "delta": f"+{round(float(context['respiratory_activity_index']) * 5.2, 1)} pts open-context lift",
                "tone": "watch",
                "classification": "derived",
                "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_HR_SHIFT_ROSTER," + OPEN_SOURCE_IDS,
                "panel_id": "PANEL_SYSTEM_POSTURE",
            },
            {
                "label": "ED boarders",
                "value": str(boarders),
                "detail": "Synthetic admissions awaiting pediatric inpatient placement",
                "delta": f"{round(float(context['ed_wait_pressure_proxy']) * 100)}% public wait-style pressure",
                "tone": "high" if boarders > 150 else "watch",
                "classification": "direct",
                "source_ids": "SRC_SYNTH_ED_VISITS,SRC_OPEN_ED_WAIT_TIME_LOGIC",
                "panel_id": "PANEL_SYSTEM_POSTURE",
            },
            {
                "label": "HR gap hours",
                "value": f"{round(hr_gap)}h",
                "detail": "Required minus available role-group hours across visible units",
                "delta": "HR layer constrains staffed capacity",
                "tone": "watch",
                "classification": "HR",
                "source_ids": "SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_HR_FLOAT_POOL",
                "panel_id": "PANEL_SYSTEM_POSTURE",
            },
            {
                "label": "Ambulatory waitlist",
                "value": f"{round(waitlist / 1000, 1)}k",
                "detail": "Program waitlist and TNA pressure across synthetic network",
                "delta": f"{round(tna)}d average TNA",
                "tone": "watch",
                "classification": "derived",
                "source_ids": "SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_CLINIC_TEMPLATES," + OPEN_SOURCE_IDS,
                "panel_id": "PANEL_SYSTEM_POSTURE",
            },
            {
                "label": "Resource pressure",
                "value": f"${round(sum(float(row['margin_pressure_k']) for row in units) + sum(float(row['finance_pressure_k']) for row in programs))}k",
                "detail": "Marginal operating-resource pressure proxy",
                "delta": "Finance/resource constraint visible",
                "tone": "watch",
                "classification": "finance",
                "source_ids": "SRC_SYNTH_FINANCE_COST_CENTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE",
                "panel_id": "PANEL_SYSTEM_POSTURE",
            },
            {
                "label": "Open-context pressure",
                "value": f"{round(float(context['respiratory_activity_index']) * 100)}",
                "detail": "Respiratory, AQHI/smoke, school calendar, population context",
                "delta": f"AQHI proxy {context['aqhi_max_proxy']}",
                "tone": "watch" if float(context["aqhi_max_proxy"]) > 5 else "good",
                "classification": "open data",
                "source_ids": OPEN_SOURCE_IDS,
                "panel_id": "PANEL_SYSTEM_POSTURE",
            },
        ],
        "postureCards": [
            {"label": "Huddle posture", "value": "Progression hub mode", "detail": "Click any metric, unit, program, warning, source, or model to open object detail.", "tone": "steady"},
            {"label": "Source readiness", "value": "Green with review pockets", "detail": "HR float pool, resource envelope, AQHI/smoke, and ED wait logic remain synthetic review layers.", "tone": "watch"},
            {"label": "Public context", "value": "Forecast-affecting", "detail": "Respiratory, AQHI/smoke, and school calendar lifts alter visible forecasts and scenario assumptions.", "tone": "watch"},
        ],
        "whyChanged": [
            {"driver": "Respiratory virus context", "change": f"+{round(float(context['respiratory_activity_index']) * 5.2, 1)} occupancy pts", "contribution": 36, "evidence": "Cached Alberta respiratory-virus style context"},
            {"driver": "AQHI/smoke context", "change": f"+{round(float(context['aqhi_max_proxy']) / 2.4, 1)} access/respiratory pressure pts", "contribution": 21, "evidence": "Cached AQHI/smoke/weather context"},
            {"driver": "HR effective-bed constraint", "change": f"{round(hr_gap)} synthetic gap hours", "contribution": 27, "evidence": "Synthetic HR roster and float-pool aggregate"},
            {"driver": "Finance/resource ceiling", "change": "Scenario feasibility capped", "contribution": 16, "evidence": "Synthetic finance/resource envelope"},
        ],
    }


def command_center_context(
    inpatient: dict[str, list[dict[str, Any]]],
    ambulatory: dict[str, list[dict[str, Any]]],
    scenarios: dict[str, list[dict[str, Any]]],
    open_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    sites = []
    for site_id, site_name, catchment, _ in SITES:
        site_units = [row for row in inpatient["unitDetails"] if row["site_id"] == site_id]
        site_programs = [row for row in ambulatory["programDetails"] if row["site_id"] == site_id]
        sites.append(
            {
                "site_id": site_id,
                "site_name": site_name,
                "catchment": catchment,
                "occupancy_pct": pct(sum(row["census"] for row in site_units) / max(1, sum(row["effective_beds"] for row in site_units))),
                "ed_boarders": sum(row["ed_boarders"] for row in site_units),
                "waitlist_total": sum(row["waitlist_total"] for row in site_programs),
                "hr_gap_hours": round(sum(row["staffing_gap_hours"] for row in site_units), 1),
                "resource_pressure_k": round(sum(row["margin_pressure_k"] for row in site_units) + sum(row["finance_pressure_k"] for row in site_programs), 1),
                "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE",
            }
        )
    return {
        "sites": sites,
        "serviceLines": [
            {"service_id": service_id, "service_line": service_name, "service_group": group, "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_HR_SHIFT_ROSTER"}
            for service_id, service_name, group, *_ in SERVICES
        ],
        "programs": [
            {"program_id": program_id, "program": program_name, "source_ids": "SRC_SYNTH_REFERRALS,SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_CLINIC_TEMPLATES"}
            for program_id, program_name, *_ in PROGRAMS
        ],
        "openContext": open_rows,
        "edWaitLogic": [
            {
                "step": "triage_to_physician_proxy",
                "logic": "Synthetic public-style estimate based on queued acuity groups, physician service rate, and resource constraint.",
                "cadence": "2-minute public-style recalculation",
                "source_ids": "SRC_OPEN_ED_WAIT_TIME_LOGIC",
            },
            {
                "step": "bed_request_proxy",
                "logic": "ED boarder and unit capacity context feeds admission placement pressure, not total ED length of stay.",
                "cadence": "15-minute operating replay",
                "source_ids": "SRC_SYNTH_ED_VISITS,SRC_SYNTH_UNIT_CENSUS_HOURLY",
            },
        ],
        "scenarioAssumptions": scenarios["controlRanges"],
        "warnings": inpatient["warnings"] + ambulatory["warnings"],
        "lakehouseTables": [
            {"table": "CANONICAL.VW_SYNTH_UNIT_SERVICE_DAY", "rows": len(inpatient["unitDetails"]), "domain": "EHR-derived operations"},
            {"table": "CANONICAL.VW_SYNTH_UNIT_HORIZON_FORECAST", "rows": len(inpatient["unitTimeline"]), "domain": "modelled inpatient"},
            {"table": "CANONICAL.VW_SYNTH_AMBULATORY_PROGRAM_WEEK", "rows": len(ambulatory["programTimeline"]), "domain": "ambulatory operations"},
            {"table": "CANONICAL.VW_SYNTH_HR_SHIFT_ROSTER", "rows": len(inpatient["unitDetails"]) + len(ambulatory["programDetails"]), "domain": "HR/workforce"},
            {"table": "FINANCE.VW_SYNTH_RESOURCE_ENVELOPE", "rows": len(inpatient["unitDetails"]) + len(ambulatory["programDetails"]), "domain": "finance/resource"},
            {"table": "OPEN_DATA.VW_COMMAND_CONTEXT_WEEK", "rows": len(open_rows), "domain": "cached public context"},
        ],
        "chartCatalog": [
            "system kpi strip",
            "site command map",
            "open context trend",
            "unit heatmap",
            "unit forecast ribbon",
            "ED-to-inpatient flow",
            "discharge funnel",
            "HR workload matrix",
            "unit cost pressure",
            "unit source readiness",
            "ambulatory waitlist bars",
            "ambulatory access heatmap",
            "program forecast ribbon",
            "no-show scenario frontier",
            "diagnostic readiness bars",
            "provider/allied capacity bars",
            "scenario baseline comparison",
            "scenario sensitivity tornado",
            "scenario affected objects",
            "model validation/drift table",
            "model coefficient bars",
            "source readiness stoplights",
        ],
    }


def panel_lineage() -> list[dict[str, Any]]:
    rows = v3.panel_lineage()
    extra = [
        ("PANEL_COMMAND_CONTEXT", "Command centre context strip", "System Posture", "open data", "review"),
        ("PANEL_UNIT_DRAWER", "Unit drilldown drawer", "Inpatient", "derived", "ready"),
        ("PANEL_PROGRAM_DRAWER", "Program drilldown drawer", "Ambulatory", "derived", "ready"),
        ("PANEL_MODEL_DRAWER", "Model-card wiring drawer", "Predictive Assets", "modelled", "review"),
        ("PANEL_SCENARIO_WORKSPACE", "Scenario workspace controls", "Scenario Lab", "modelled", "review"),
    ]
    known = {row["panel_id"] for row in rows}
    for panel_id, title, app_area, classification, readiness in extra:
        if panel_id not in known:
            rows.append(
                {
                    "panel_id": panel_id,
                    "title": title,
                    "app_area": app_area,
                    "classification": classification,
                    "readiness_status": readiness,
                    "freshness": "15 minutes to weekly synthetic replay",
                    "confidence": "medium-high" if readiness == "ready" else "medium",
                    "caveat": "Synthetic demonstration data; not validated for clinical decision-making.",
                    "lineage_summary": "Combines direct, derived, modelled, HR, finance, and open-context layers through curated synthetic views.",
                    "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE," + OPEN_SOURCE_IDS,
                }
            )
    return rows


def main() -> None:
    open_rows = open_context_rows()
    sources = v5_sources()
    readiness = v5_readiness(sources)
    metrics = metric_registry()
    models = model_registry()
    inpatient = unit_payload(open_rows)
    ambulatory = ambulatory_payload(open_rows)
    scenarios = scenario_payload(inpatient, ambulatory)
    lineage = panel_lineage()
    warnings = v3.warning_logic_registry()
    coefficients = v3.coefficient_registry()
    quality_rules = v3.data_quality_rules()
    validation_drift = v3.validation_drift_payload(models)
    releases = v3.release_rollback_registry(models)
    gatekeeper = v3.gatekeeper_payload(models, sources, readiness, metrics, warnings, coefficients, quality_rules, validation_drift, releases)
    memory = v3.learning_memory_payload()
    wiring = v3.future_wiring_payload(sources)
    posture = system_posture(inpatient, ambulatory, open_rows)
    predictive = v3.predictive_assets_payload()
    command_context = command_center_context(inpatient, ambulatory, scenarios, open_rows)

    metadata = {
        "appVersion": "v5.0",
        "generatedAt": NOW,
        "mode": "Synthetic demonstration data",
        "clinicalUse": "Not validated for clinical decision-making",
        "historyWindow": "Synthetic 24-month replay plus 52-week cached public-context layer",
        "sourceBoundary": "Future real data maps through curated governed Snowflake views only.",
        "productName": "Pediatric Command Centre / Progression Hub",
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
    write_json("command_center_context.json", command_context)

    write_csv("v5_source_registry.csv", sources)
    write_csv("v5_direct_link_validation.csv", readiness)
    write_csv("v5_metric_registry.csv", metrics)
    write_csv("v5_model_registry.csv", models)
    write_csv("v5_panel_lineage.csv", lineage)
    write_csv("v5_inpatient_unit_details.csv", inpatient["unitDetails"])
    write_csv("v5_inpatient_unit_timeline.csv", inpatient["unitTimeline"])
    write_csv("v5_ambulatory_program_details.csv", ambulatory["programDetails"])
    write_csv("v5_ambulatory_program_timeline.csv", ambulatory["programTimeline"])
    write_csv("v5_open_context.csv", open_rows)
    write_csv("v5_scenarios.csv", scenarios["scenarios"])
    write_csv("v5_scenario_controls.csv", scenarios["controlRanges"])
    print(f"Wrote v5 command-centre assets to {OUT}")


if __name__ == "__main__":
    main()
