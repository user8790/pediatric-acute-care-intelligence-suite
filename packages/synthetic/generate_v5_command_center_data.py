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
        source_row(
            "SRC_SYNTH_NICU_FEATURE_WINDOWS",
            "CANONICAL.VW_SYNTH_NICU_FEATURE_WINDOWS",
            "neonatal safety / surveillance",
            "unit-feature-window aggregate",
            "site_id, unit_id, feature_window_start, gestational_age_band_proxy, feeding_trajectory_proxy, abdominal_symptom_proxy, small_cell_suppressed",
            "hourly to daily synthetic replay",
            "derived_operational_intelligence",
            "NEC recognition rehearsal and neonatal safety implementation design",
            "sensitive aggregate only",
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
            "decision packet worklist",
            "expert lens review board",
            "operating cadence load",
            "escalation lane reliability",
        ],
        "interpretations": interpretation_rows(inpatient, ambulatory, scenarios, open_rows),
        "roleGuidance": role_guidance_rows(),
        "implementationReadiness": implementation_readiness_rows(scenarios),
        "actionLearningLoops": action_learning_loop_rows(inpatient, ambulatory, scenarios),
        "signalSimulations": signal_simulation_rows(open_rows),
        "expertLensReviews": expert_lens_review_rows(),
        "decisionPackets": decision_packet_rows(inpatient, ambulatory, scenarios, open_rows),
        "operatingCadence": operating_cadence_rows(),
        "escalationLanes": escalation_lane_rows(),
    }


def interpretation_rows(
    inpatient: dict[str, list[dict[str, Any]]],
    ambulatory: dict[str, list[dict[str, Any]]],
    scenarios: dict[str, list[dict[str, Any]]],
    open_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    context = latest_context(open_rows)
    top_units = sorted(inpatient["unitDetails"], key=lambda row: (row["occupancy_pct"], row["ed_boarders"], row["staffing_gap_hours"]), reverse=True)[:4]
    top_programs = sorted(ambulatory["programDetails"], key=lambda row: (row["third_next_available_days"], row["urgent_waitlist"]), reverse=True)[:4]
    rows: list[dict[str, Any]] = [
        {
            "signal_id": "SIG-SYSTEM-001",
            "signal_type": "system_posture",
            "object_type": "network",
            "object_id": "SITE_PROV_NETWORK",
            "persona": "Executive",
            "headline": "System pressure is being shaped by effective capacity, not physical beds alone.",
            "what_changed": "Network occupancy remains above the watch threshold after applying staffed/effective bed constraints.",
            "likely_drivers": "Respiratory activity, ED placement pressure, discharge barriers, and aggregate HR gap hours are moving together.",
            "review_action": "Use this as a huddle prioritization cue: confirm the highest-pressure units, ask whether barriers can be moved today, and check whether any scenario is feasible under HR and resource limits.",
            "confidence": "medium-high",
            "confidence_reason": "Direct synthetic capacity and staffing variables are ready; public-context and finance-resource variables remain review-grade.",
            "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_HR_SHIFT_ROSTER,SRC_OPEN_RESPIRATORY_VIRUS_DASHBOARD,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE",
            "model_ids": "INPT_OCCUPANCY_FORECAST,PICU_NICU_PRESSURE",
            "next_step": "Open the inpatient object list and compare action feasibility in the scenario lab.",
        },
        {
            "signal_id": "SIG-OPEN-001",
            "signal_type": "open_context",
            "object_type": "open_data",
            "object_id": "OPEN_CONTEXT",
            "persona": "Analytics / informatics / AI team",
            "headline": "Open-context variables are forecast-shaping, but should stay visibly separable from operational feeds.",
            "what_changed": f"Current respiratory index is {context['respiratory_activity_index']} and AQHI/smoke proxy is {context['aqhi_max_proxy']}.",
            "likely_drivers": "Cached respiratory-virus, AQHI/smoke, school-calendar, and pediatric-population context are adding small explicit lifts to demand and access forecasts.",
            "review_action": "Validate source refresh cadence, missingness, regional mapping, and whether the lift coefficients should be site-specific before any production use.",
            "confidence": "medium",
            "confidence_reason": "Public sources are conceptually credible, but local calibration and denominator ownership are pending.",
            "source_ids": OPEN_SOURCE_IDS,
            "model_ids": "INPT_OCCUPANCY_FORECAST,AMB_REFERRAL_DEMAND_FORECAST",
            "next_step": "Keep source badges visible and compare model performance with and without open-context features.",
        },
    ]
    for index, unit in enumerate(top_units):
        rows.append(
            {
                "signal_id": f"SIG-UNIT-{index + 1:03d}",
                "signal_type": "unit_pressure",
                "object_type": "unit",
                "object_id": unit["unit_id"],
                "persona": "Patient-flow leader" if index % 2 == 0 else "Unit manager",
                "headline": f"{unit['unit_name']} is a high-yield review target for today's progression huddle.",
                "what_changed": f"Occupancy is {round(unit['occupancy_pct'] * 100, 1)}%, with {unit['ed_boarders']} ED boarders and {unit['staffing_gap_hours']} synthetic HR gap hours.",
                "likely_drivers": "Effective-bed loss, respiratory/open-context pressure, ED boarders, and discharge barriers are aligned.",
                "review_action": "Consider a structured review of discharge barriers, role-group gaps, transfer requests, and whether a step-down or discharge-pull-forward scenario is feasible.",
                "confidence": unit["confidence"],
                "confidence_reason": "Capacity and HR variables are direct or derived synthetic signals; action impact remains modelled.",
                "source_ids": unit["source_ids"],
                "model_ids": unit["model_ids"],
                "next_step": "Open the unit drawer and inspect barriers, HR gap, cost ceiling, warnings, and model lineage.",
            }
        )
    for index, program in enumerate(top_programs):
        rows.append(
            {
                "signal_id": f"SIG-PROGRAM-{index + 1:03d}",
                "signal_type": "ambulatory_access",
                "object_type": "program",
                "object_id": program["program_id"],
                "persona": "Ambulatory program leader" if index % 2 == 0 else "Clinic operations leader",
                "headline": f"{program['program']} access pressure has a clear template-and-resource review path.",
                "what_changed": f"TNA is {program['third_next_available_days']} days, urgent waitlist is {program['urgent_waitlist']}, and diagnostics readiness is {round(program['diagnostic_readiness'] * 100)}%.",
                "likely_drivers": "Referral load, template capacity, diagnostics readiness, no-show reliability, provider sessions, and HR/resource gaps.",
                "review_action": "Review urgent-slot protection, diagnostics readiness, provider/allied-health capacity, and whether virtual/outreach substitution is appropriate for eligible follow-up.",
                "confidence": program["confidence"],
                "confidence_reason": "Referral, waitlist, and template variables are synthetic direct/derived signals; scenario impact remains modelled.",
                "source_ids": program["source_ids"],
                "model_ids": program["model_ids"],
                "next_step": "Open the program drawer and compare template, no-show, diagnostics, HR, and finance/resource constraints.",
            }
        )
    for scenario in scenarios["scenarios"][:4]:
        rows.append(
            {
                "signal_id": f"SIG-{scenario['scenario_id']}",
                "signal_type": "scenario_decision",
                "object_type": "scenario",
                "object_id": scenario["scenario_id"],
                "persona": "Site operations leader",
                "headline": f"{scenario['scenario_name']} has a visible feasibility and trade-off path.",
                "what_changed": f"Baseline {scenario['baseline_value']} compares with scenario {scenario['scenario_value']} for {scenario['primary_outcome']}.",
                "likely_drivers": "Scenario coefficients, HR hours required, resource cap, and affected unit/program exposure.",
                "review_action": "Treat the result as a planning comparison, not an order. Confirm staffing, resource, and clinical-operational feasibility before any action.",
                "confidence": "medium",
                "confidence_reason": "Scenario coefficients are transparent proxy values with confidence bands and governance caveats.",
                "source_ids": scenario["source_ids"],
                "model_ids": "INPT_OCCUPANCY_FORECAST,AMBULATORY_ACCESS_FORECAST",
                "next_step": "Open the scenario drawer, review affected objects, then capture a what-if for the learning log.",
            }
        )
    return rows


def role_guidance_rows() -> list[dict[str, Any]]:
    return [
        {
            "persona": "Executive",
            "value_question": "Where is the pediatric system exposed, what is driving it, and which trade-offs need executive attention?",
            "primary_view": "Network posture, site comparison, resource pressure, open-context trend, implementation-readiness exceptions.",
            "math_note": "Uses the same source metrics as every persona; only aggregation, language, and action framing change.",
            "recommended_actions": "Compare site posture, ask whether resource ceilings are constraining feasible actions, and sponsor governance decisions that unblock trusted signals.",
        },
        {
            "persona": "Site operations leader",
            "value_question": "Which site objects need a huddle decision today and which scenario is feasible?",
            "primary_view": "Site/unit/program objects, warnings, scenario feasibility, HR and finance constraints.",
            "math_note": "Site filters preserve the same formulas and coefficients while narrowing object scope.",
            "recommended_actions": "Review high-pressure units/programs, validate action feasibility, and capture scenario decisions for follow-up.",
        },
        {
            "persona": "Patient-flow leader",
            "value_question": "What is blocking progression and where would action create the most effective capacity?",
            "primary_view": "Unit heatmap, ED-to-inpatient flow, discharge funnel, predicted admits/discharges, affected units.",
            "math_note": "Flow interpretation emphasizes capacity, boarders, transfers, and discharge barriers without changing calculation logic.",
            "recommended_actions": "Open unit drawers, compare barriers and transfers, and use scenario lab to test discharge or step-down levers.",
        },
        {
            "persona": "Unit manager",
            "value_question": "What is changing on my unit and what review would be reasonable this shift?",
            "primary_view": "Unit drawer, staffing gap, effective beds, warnings, discharge barriers, source lineage.",
            "math_note": "Unit view uses direct unit-level rows where available and avoids changing thresholds by role.",
            "recommended_actions": "Review HR/allied gaps, discharge blockers, transfer requests, and source confidence before escalating.",
        },
        {
            "persona": "Ambulatory program leader",
            "value_question": "Where are referrals, waitlist, diagnostics, templates, and follow-up becoming unsafe operational pressure?",
            "primary_view": "Program object drawer, TNA, urgent waitlist, template gaps, diagnostics readiness, virtual/outreach scenario.",
            "math_note": "Program calculations use the same waitlist, referral, and capacity formulas across roles.",
            "recommended_actions": "Review urgent-slot protection, diagnostics readiness, and provider/allied-health capacity constraints.",
        },
        {
            "persona": "Clinic operations leader",
            "value_question": "Which templates, no-shows, diagnostics, and follow-up queues need operational tuning?",
            "primary_view": "Access heatmap, no-show frontier, provider capacity, diagnostics bars, program drawers.",
            "math_note": "Clinic lens changes emphasis from strategic backlog to template mechanics, not the underlying math.",
            "recommended_actions": "Compare template gap, no-show opportunity, and diagnostics readiness before changing clinic supply.",
        },
        {
            "persona": "Analytics / informatics / AI team",
            "value_question": "Can each signal be trusted, implemented, governed, monitored, and retired safely?",
            "primary_view": "Data & Model Readiness, model cards, coefficient registry, validation/drift, dependency graph, source badges.",
            "math_note": "Technical persona exposes formulas, coefficients, thresholds, feature families, validation status, and dependencies.",
            "recommended_actions": "Resolve blocked feeds, review metric definitions, validate coefficients, and maintain rollback/governance evidence.",
        },
    ]


def implementation_readiness_rows(scenarios: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rows = [
        ("synthetic_variable", "DEMO_UNIT_CENSUS", "Synthetic unit census and effective-bed variables", "ready", "ready", "not_connected", "Synthetic data product", "Keep visible as future-state ready while labelling synthetic.", "Map to curated census and bed-status views; validate denominator and timestamp logic."),
        ("synthetic_variable", "DEMO_AMB_WAITLIST", "Synthetic referral, waitlist, template, and TNA variables", "ready", "ready", "not_connected", "Synthetic data product", "Demonstrates future access command centre.", "Map referral, appointment, template, no-show, and diagnostics readiness views."),
        ("real_data_feed", "REAL_ADT_BED_STATUS", "ADT, bed status, unit census, transfer request feeds", "blocked", "simulated", "blocked", "Source integration", "Needs curated Snowflake views and source-owner signoff.", "Create read-only canonical views, freshness checks, and small-cell suppression."),
        ("real_data_feed", "REAL_HR_ROSTER", "HR roster, absence, float-pool, skill-mix feeds", "pending", "simulated", "pending", "Workforce analytics", "Sensitive staff aggregate feed requires explicit governance.", "Define aggregate role groups, minimum cell sizes, and refresh cadence."),
        ("real_data_feed", "REAL_FINANCE_ENVELOPE", "Cost centre, overtime, agency, and resource-envelope feeds", "pending", "simulated", "pending", "Finance partner", "Finance proxy is useful but not production accounting.", "Agree on resource proxy, budget period, and allowed operational display granularity."),
        ("metric_definition", "METRIC_EFFECTIVE_STAFFED_BEDS", "Effective staffed beds calculation", "review", "ready", "pending", "Patient Flow / HR", "Formula is transparent but needs local definition ownership.", "Approve physical/staffed/effective bed denominator and effective-bed-loss logic."),
        ("metric_definition", "METRIC_TNA", "Third-next-available and template capacity calculation", "review", "ready", "pending", "Ambulatory operations", "Synthetic formula is visible and useful for implementation rehearsal.", "Confirm template rules, provider leave handling, virtual slots, and urgent-slot carve-outs."),
        ("coefficient", "COEF_RESPIRATORY_LIFT", "Respiratory open-context forecast lift", "review", "ready", "pending", "Analytics", "Coefficient is plausible proxy, not locally calibrated.", "Backtest forecast with and without respiratory/AQHI/calendar features by site and season."),
        ("coefficient", "COEF_HR_CAPACITY", "HR constraint multiplier", "review", "ready", "pending", "Workforce analytics", "Useful for scenario feasibility but requires local staffing model review.", "Calibrate role-group hours, float-pool substitution, and overtime/agency constraints."),
        ("pending_model", "MODEL_RARE_DISEASE_CASE_FINDING", "Rare-disease case-finding simulation", "blocked", "prototype", "not_connected", "Clinical informatics / genetics", "Requires careful governance, precision review, and referral pathway design.", "Define eligible feature families, exclude identifiers, review alert burden, and create specialist review workflow."),
        ("pending_model", "MODEL_EARLY_WARNING_DETERIORATION", "General pediatric deterioration early-warning simulation", "blocked", "prototype", "not_connected", "Clinical safety", "Must not surface as clinical advice without rigorous local validation.", "Run silent evaluation, subgroup calibration, alert-burden review, and human-factors testing."),
        ("pending_model", "MODEL_NEC_RECOGNITION", "NEC recognition simulation", "blocked", "prototype", "not_connected", "Neonatal clinical safety", "High-stakes neonatal signal remains prototype-only.", "Define neonatal cohort, feature windows, escalation path, and safety review before any operational warning."),
        ("validation", "VALIDATION_BACKTEST", "Temporal backtest and calibration checks", "pending", "synthetic_pass", "pending", "Analytics / model risk", "Synthetic validation exists but production validation is not complete.", "Backtest by site, service, age-band proxy, season, equity/travel proxy, and alert threshold."),
        ("governance", "GOV_WARNING_RELEASE", "Warning release, acknowledgement, and rollback controls", "review", "defined", "pending", "AI governance", "Release pattern exists, but production policies and accountabilities must be approved.", "Define review board, approval evidence, canary scope, rollback trigger, and post-release monitoring."),
        ("dependency", "DEP_LEARNING_WRITEBACK", "Scenario, acknowledgement, outcome-review writeback tables", "review", "defined", "pending", "Snowflake app owner", "Learning loop tables are defined but not wired to production operations.", "Implement APP/GOVERNANCE schemas, role grants, audit policy, and retention rules."),
    ]
    for scenario in scenarios["scenarios"]:
        rows.append(
            (
                "scenario",
                scenario["scenario_id"],
                scenario["scenario_name"],
                scenario["readiness"],
                "ready",
                "pending",
                "Operations / analytics",
                "Scenario is useful for what-if rehearsal, but should not be treated as an operational directive.",
                "Validate coefficients, affected-object mapping, HR and resource constraints, and outcome follow-up cadence.",
            )
        )
    return [
        {
            "category": category,
            "item_id": item_id,
            "item": item,
            "status": status,
            "synthetic_demo_status": synthetic_status,
            "real_data_status": real_status,
            "owner": owner,
            "trust_note": trust_note,
            "next_implementation_step": next_step,
            "classification": "synthetic demo" if category == "synthetic_variable" else "implementation readiness",
        }
        for category, item_id, item, status, synthetic_status, real_status, owner, trust_note, next_step in rows
    ]


def action_learning_loop_rows(
    inpatient: dict[str, list[dict[str, Any]]],
    ambulatory: dict[str, list[dict[str, Any]]],
    scenarios: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    loops = [
        ("LOOP-UNIT-PRESSURE", "Unit progression pressure", "Patient-flow leader", inpatient["warnings"][0] if inpatient["warnings"] else {}, scenarios["scenarios"][0]),
        ("LOOP-AMB-ACCESS", "Ambulatory access breach", "Ambulatory program leader", ambulatory["warnings"][0] if ambulatory["warnings"] else {}, scenarios["scenarios"][2]),
        ("LOOP-HR-CONSTRAINT", "HR-constrained capacity", "Site operations leader", inpatient["warnings"][1] if len(inpatient["warnings"]) > 1 else {}, scenarios["scenarios"][4]),
        ("LOOP-MODEL-READINESS", "Model readiness exception", "Analytics / informatics / AI team", {"title": "Validation hold", "message": "A modelled signal is blocked until local validation and governance review are complete."}, scenarios["scenarios"][-1]),
    ]
    stages = [
        ("detect", "Signal detected", "System surfaces the signal with classification, confidence, and source badges.", "new"),
        ("review", "Team review", "Huddle or domain owner checks the drawer, lineage, drivers, and caveats.", "in review"),
        ("act", "Action considered", "Team compares scenario feasibility, HR/resource constraints, and operational trade-offs.", "decision support"),
        ("follow_up", "Follow-up check", "Outcome, exceptions, and unintended consequences are reviewed after the action window.", "pending"),
        ("learn", "Learning captured", "Scenario result, acknowledgement, and reviewer notes write back to governed tables.", "learning"),
        ("spread", "Spread or retire", "If useful, playbook is generalized; if noisy, coefficient/threshold is revised or retired.", "governance"),
    ]
    rows: list[dict[str, Any]] = []
    for loop_id, loop_name, owner, warning, scenario in loops:
        for stage_index, (stage_id, stage_name, description, status) in enumerate(stages, start=1):
            rows.append(
                {
                    "loop_id": loop_id,
                    "loop_name": loop_name,
                    "stage_index": stage_index,
                    "stage_id": stage_id,
                    "stage_name": stage_name,
                    "owner": owner,
                    "status": status,
                    "trigger": warning.get("title", loop_name),
                    "description": description,
                    "decision_support": scenario["scenario_name"],
                    "follow_up_metric": scenario["primary_outcome"],
                    "learning_output": "APP.SCENARIO_RUN_LOG, APP.WARNING_ACKNOWLEDGEMENT, APP.LEARNING_SYSTEM_OUTCOME_REVIEW",
                    "source_ids": warning.get("source_ids", scenario["source_ids"]),
                    "caveat": "Prototype learning loop content only; not connected to real operations.",
                }
            )
    return rows


def signal_simulation_rows(open_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest = latest_context(open_rows)
    configs = [
        {
            "simulation_id": "SIM-TRIAGE-LOS",
            "label": "Triage and LOS orchestration",
            "domain": "ED / inpatient flow",
            "inspiration": "Frontier LOS orchestration and ED triage queueing methods",
            "clinical_boundary": "Operational flow support only; does not replace triage, assessment, or physician judgement.",
            "target_question": "Which arrivals are likely to consume constrained downstream capacity, and what operational constraint is driving the queue?",
            "cohort": "Synthetic pediatric ED arrivals and admitted-boarder aggregates; no direct personal identifiers.",
            "primary_output": "predicted_los_hours",
            "threshold_logic": "Watch when predicted LOS exceeds service-adjusted 80th percentile; high when boarding risk and downstream capacity constraint align.",
            "validation_status": "synthetic silent replay only; real temporal validation pending",
            "governance_status": "prototype hold",
            "model_family": "survival/gradient boosting plus queueing constraint overlay",
            "feature_families": "arrival pattern, CTAS-style acuity band, bed capacity, consult bottleneck, diagnostics turnaround, staffing, transfer pressure, open context",
            "source_ids": "SRC_SYNTH_ED_VISITS,SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_TRANSFER_REQUESTS,SRC_SYNTH_HR_SHIFT_ROSTER,SRC_OPEN_ED_WAIT_TIME_LOGIC",
            "coefficients": [
                {"coefficient_name": "acuity_band_weight", "default_value": 0.31},
                {"coefficient_name": "boarder_queue_weight", "default_value": 0.27},
                {"coefficient_name": "diagnostic_turnaround_weight", "default_value": 0.16},
                {"coefficient_name": "staffed_capacity_weight", "default_value": -0.22},
                {"coefficient_name": "respiratory_context_weight", "default_value": 0.08},
            ],
            "factors": [
                {"factor": "ED arrivals", "demand": 96, "supply": 72, "pressure": 0.78},
                {"factor": "Admitted boarders", "demand": 31, "supply": 18, "pressure": 0.86},
                {"factor": "Consult queue", "demand": 22, "supply": 14, "pressure": 0.72},
                {"factor": "Diagnostic turnaround", "demand": 44, "supply": 35, "pressure": 0.63},
            ],
            "timeline": [{"hour": hour, "risk": round(0.42 + hour * 0.012 + float(latest["ed_wait_pressure_proxy"]) * 0.12, 3), "lower": round(0.35 + hour * 0.009, 3), "upper": round(0.5 + hour * 0.015, 3)} for hour in [0, 3, 6, 12, 18, 24, 48, 72]],
            "so_what": "The signal separates arrival pressure from downstream bed and consult constraints so teams can decide whether the bottleneck is triage room, diagnostics, consult, bed, transport, or staffing capacity.",
            "now_what": "Review the top constrained factor, compare a step-down/discharge scenario, and capture whether the queue actually improved after the huddle window.",
        },
        {
            "simulation_id": "SIM-RARE-DISEASE",
            "label": "Rare-disease case finding",
            "domain": "complex diagnostic pathway",
            "inspiration": "ThinkRare-style phenotype patterning and pediatric rare-disease diagnostic support",
            "clinical_boundary": "Case-finding queue only; no diagnosis, no automated referral, and no display of patient identifiers.",
            "target_question": "Which aggregate synthetic phenotype patterns might warrant specialist review of a cohort, pathway, or referral delay?",
            "cohort": "Synthetic de-identified feature bundles only; excludes direct chart or personal identifiers.",
            "primary_output": "review_priority_score",
            "threshold_logic": "Watch when phenotype burden, diagnostic odyssey duration, and repeated specialty touchpoints align; high requires human genetics/specialist review queue approval.",
            "validation_status": "prototype-only; requires precision, bias, referral-burden, and specialist review validation",
            "governance_status": "blocked for real data until clinical governance and family-impact review",
            "model_family": "phenotype embedding similarity plus rules-based pathway delay features",
            "feature_families": "problem clusters, repeated referrals, abnormal-result families, growth/development proxies, medication class patterns, family history proxy flags, utilization path length",
            "source_ids": "SRC_SYNTH_REFERRALS,SRC_SYNTH_ORDERS,SRC_SYNTH_LAB_RESULTS,SRC_SYNTH_CARE_PLAN_MILESTONES,SRC_MODEL_VALIDATION_RESULTS",
            "coefficients": [
                {"coefficient_name": "phenotype_cluster_similarity", "default_value": 0.34},
                {"coefficient_name": "multi_specialty_path_weight", "default_value": 0.18},
                {"coefficient_name": "diagnostic_odyssey_duration", "default_value": 0.21},
                {"coefficient_name": "abnormal_result_family_weight", "default_value": 0.15},
                {"coefficient_name": "equity_guardrail_penalty", "default_value": -0.09},
            ],
            "factors": [
                {"factor": "Phenotype cluster burden", "demand": 128, "supply": 36, "pressure": 0.81},
                {"factor": "Genetics review slots", "demand": 42, "supply": 18, "pressure": 0.88},
                {"factor": "Cross-specialty touchpoints", "demand": 76, "supply": 44, "pressure": 0.67},
                {"factor": "Family impact review", "demand": 34, "supply": 20, "pressure": 0.62},
            ],
            "timeline": [{"week": week, "risk": round(0.36 + week * 0.006 + math.sin(week / 5) * 0.04, 3), "lower": round(0.29 + week * 0.004, 3), "upper": round(0.44 + week * 0.007, 3)} for week in [1, 2, 4, 8, 12, 18, 26]],
            "so_what": "This is a pathway-learning tool: it asks whether patterns of delay and repeated touchpoints indicate a cohort that deserves specialist review, not whether a child has a specific disease.",
            "now_what": "Route only aggregate candidates to a governed review queue, measure false-positive burden, and tune thresholds with specialists before any live signal.",
        },
        {
            "simulation_id": "SIM-EARLY-WARNING",
            "label": "General deterioration early warning",
            "domain": "inpatient safety / surveillance",
            "inspiration": "Pediatric early warning and deterioration-risk surveillance methods",
            "clinical_boundary": "Synthetic surveillance rehearsal only; not a bedside alarm, diagnosis, or treatment recommendation.",
            "target_question": "Where might aggregate deterioration-risk signals, staffing pressure, and workload context align enough to warrant review of monitoring reliability?",
            "cohort": "Synthetic unit-level surveillance aggregates and score-band proxies; no identifiable child-level display.",
            "primary_output": "deterioration_review_risk",
            "threshold_logic": "Watch when score-band trend, respiratory support escalation, abnormal observation burden, and staffing gap align; high requires clinical safety review before display.",
            "validation_status": "synthetic calibration only; real subgroup calibration and alert-burden review blocked",
            "governance_status": "prototype hold",
            "model_family": "calibrated logistic/gradient boosting risk with alert-burden governor",
            "feature_families": "vital-sign completeness, respiratory support, abnormal score bands, escalation events, workload acuity, staffing gap, unit context",
            "source_ids": "SRC_SYNTH_VITAL_SIGNS_AGG,SRC_SYNTH_RESPIRATORY_SUPPORT,SRC_SYNTH_CLINICAL_SCORES,SRC_SYNTH_WORKLOAD_ACUITY,SRC_SYNTH_HR_SHIFT_ROSTER",
            "coefficients": [
                {"coefficient_name": "respiratory_support_escalation", "default_value": 0.29},
                {"coefficient_name": "score_band_trend", "default_value": 0.24},
                {"coefficient_name": "vital_completeness_gap", "default_value": 0.11},
                {"coefficient_name": "workload_acuity_weight", "default_value": 0.17},
                {"coefficient_name": "alert_burden_governor", "default_value": -0.13},
            ],
            "factors": [
                {"factor": "Respiratory escalation", "demand": 21, "supply": 16, "pressure": 0.7},
                {"factor": "Observation completeness", "demand": 88, "supply": 94, "pressure": 0.38},
                {"factor": "Workload acuity", "demand": 79, "supply": 61, "pressure": 0.74},
                {"factor": "Clinical review bandwidth", "demand": 18, "supply": 14, "pressure": 0.66},
            ],
            "timeline": [{"hour": hour, "risk": round(0.31 + hour * 0.01 + float(latest["respiratory_activity_index"]) * 0.08, 3), "lower": round(0.24 + hour * 0.007, 3), "upper": round(0.39 + hour * 0.012, 3)} for hour in [0, 3, 6, 12, 18, 24, 36, 48]],
            "so_what": "The prototype demonstrates how safety surveillance must sit beside capacity and workload context so leaders can separate signal quality from staffing strain and alert burden.",
            "now_what": "Run silent mode first, compare with existing escalation workflows, review false-positive burden, and require clinical safety approval before any alert display.",
        },
        {
            "simulation_id": "SIM-NEC",
            "label": "NEC recognition rehearsal",
            "domain": "neonatal safety / NICU",
            "inspiration": "Necrotizing enterocolitis early-recognition risk modelling and neonatal deterioration surveillance",
            "clinical_boundary": "Prototype-only neonatal surveillance rehearsal; not diagnostic, not an alarm, and not validated for care decisions.",
            "target_question": "Can a governed aggregate signal show how feeding, prematurity, infection/inflammation, vitals, labs, and imaging readiness might combine for NEC review?",
            "cohort": "Synthetic NICU aggregate feature windows; no infant identifiers, free-text extraction, names, direct dates, or bedside instructions.",
            "primary_output": "nec_review_risk",
            "threshold_logic": "Watch when feeding intolerance proxy, inflammatory/lab family, abdominal imaging readiness, and prematurity context align; high remains blocked until neonatal safety review.",
            "validation_status": "prototype-only; requires neonatal cohort definition, temporal leakage review, and silent validation",
            "governance_status": "blocked for live use",
            "model_family": "time-windowed logistic/gradient boosting ensemble with leakage guardrails",
            "feature_families": "gestational-age proxy, feeding trajectory, abdominal symptom proxy, lab/inflammation family, antibiotic/order family, imaging readiness, respiratory support, unit workload",
            "source_ids": "SRC_SYNTH_NICU_FEATURE_WINDOWS,SRC_SYNTH_LAB_RESULTS,SRC_SYNTH_IMAGING_ORDERS,SRC_SYNTH_MEDICATION_ORDERS,SRC_SYNTH_RESPIRATORY_SUPPORT,SRC_MODEL_VALIDATION_RESULTS",
            "coefficients": [
                {"coefficient_name": "feeding_intolerance_proxy", "default_value": 0.28},
                {"coefficient_name": "prematurity_context_weight", "default_value": 0.22},
                {"coefficient_name": "lab_inflammation_family", "default_value": 0.19},
                {"coefficient_name": "abdominal_imaging_readiness", "default_value": 0.14},
                {"coefficient_name": "temporal_leakage_penalty", "default_value": -0.18},
            ],
            "factors": [
                {"factor": "Feeding trajectory proxy", "demand": 18, "supply": 15, "pressure": 0.63},
                {"factor": "Lab/inflammation family", "demand": 26, "supply": 20, "pressure": 0.68},
                {"factor": "Imaging readiness", "demand": 11, "supply": 9, "pressure": 0.57},
                {"factor": "Neonatal review bandwidth", "demand": 9, "supply": 7, "pressure": 0.64},
            ],
            "timeline": [{"hour": hour, "risk": round(0.18 + hour * 0.008 + math.sin(hour / 8) * 0.025, 3), "lower": round(0.12 + hour * 0.005, 3), "upper": round(0.25 + hour * 0.01, 3)} for hour in [0, 3, 6, 12, 18, 24, 36, 48]],
            "so_what": "NEC is exactly the kind of high-stakes signal that should be shown as implementation design first: transparent variables, leakage guardrails, governance blocks, and no automated clinical instruction.",
            "now_what": "Define neonatal cohort windows, run silent validation, require neonatal clinical-safety review, and track whether any signal would have added useful review time without unsafe alert burden.",
        },
    ]
    for config in configs:
        baseline = 100 if "RARE" in config["simulation_id"] else 1
        config["baseline_vs_scenario"] = [
            {"label": "Baseline", "value": baseline, "classification": "derived"},
            {"label": "Scenario with governed signal", "value": round(baseline * 0.78, 2), "classification": "modelled"},
            {"label": "CI low", "value": round(baseline * 0.66, 2), "classification": "modelled"},
            {"label": "CI high", "value": round(baseline * 0.92, 2), "classification": "modelled"},
        ]
        config["implementation_steps"] = [
            "Define cohort and exclusion criteria without identifiers.",
            "Map curated aggregate fields through governed Snowflake views.",
            "Backtest silently with temporal validation and subgroup review.",
            "Review alert burden, false-positive impact, and human-factors risk.",
            "Approve release gate, owner, rollback trigger, and learning writeback.",
        ]
    return configs


def expert_lens_review_rows() -> list[dict[str, Any]]:
    lenses = [
        (
            "Software architect",
            "The product needs a durable operating-object model, not page-specific logic.",
            "Decision packets now provide a shared object that can be routed across posture, huddle, readiness, escalation, and learning surfaces.",
            "Architecture / platform",
            "Every major signal can be represented as packet, source, model, owner, action, and learning event.",
            "ready",
        ),
        (
            "Principal frontend engineer",
            "Dense command-centre experiences need stable controls, clear object affordances, and drilldowns that do not shift layout.",
            "The Command Desk uses selectable packet cards, compact status badges, drawer details, and charts with stable dimensions.",
            "Frontend",
            "Users can select a packet, open its evidence, and keep orientation without page jumps.",
            "ready",
        ),
        (
            "Clinical informatician",
            "Operational signals must separate observation, interpretation, and clinical action boundaries.",
            "Packets include interpretation, evidence-to-clear, safety gate, and a careful not-a-clinical-directive stance.",
            "Clinical informatics",
            "Each packet shows why it is visible, what review is reasonable, and what must not be inferred.",
            "review",
        ),
        (
            "Healthcare informatician",
            "Definitions, owners, workflow state, and writeback need to travel with every signal.",
            "The operating cadence rows map signals into huddles, outputs, and governed writeback tables.",
            "Healthcare informatics",
            "Huddle outputs and learning tables are explicit for each operating loop.",
            "review",
        ),
        (
            "Health AI safety",
            "Models should be blocked by default until validation, subgroup calibration, monitoring, and rollback evidence exist.",
            "Escalation lanes and readiness rows expose blocked model gates and required human review.",
            "AI governance",
            "High-stakes AI packets cannot appear as production-ready without validation and governance evidence.",
            "blocked",
        ),
        (
            "Data scientist",
            "Feature families, proxy weights, scenario effects, and uncertainty should be visible where decisions are made.",
            "Decision packets link to model cards, source badges, confidence language, and scenario IDs.",
            "Analytics",
            "A user can trace packet impact back to model and source assumptions.",
            "review",
        ),
        (
            "Statistician / modeller",
            "Forecasts and scenarios need uncertainty, sensitivity, calibration, denominator ownership, and drift review.",
            "Packets carry confidence, learning metric, expected impact, and evidence-to-clear fields.",
            "Model risk",
            "Each packet states what would make the signal trusted or retired.",
            "review",
        ),
        (
            "Queueing theory / flow",
            "Flow work must distinguish arrival pressure, service rate, buffers, downstream capacity, and bottleneck location.",
            "The triage/LOS and ED-boarder packets expose bottleneck and scenario levers rather than a generic pressure score.",
            "Patient flow analytics",
            "The selected packet identifies the constrained queue and the feasible lever.",
            "ready",
        ),
        (
            "Acute care operations",
            "A command centre must tell teams what to review this huddle and what can wait.",
            "Urgency, owner persona, cadence, follow-up window, and escalation lane are first-class packet fields.",
            "Operations",
            "The page can sort work into now, next shift, next day, and governance lanes.",
            "ready",
        ),
        (
            "Pediatric clinical leader",
            "Pediatric specificity matters: NICU/PICU, respiratory season, complex care, family travel, and child-specific safety.",
            "Packets and AI simulations include pediatric domains, safety gates, and open-context seasonality.",
            "Pediatric clinical leadership",
            "Pediatric service and unit context is visible in every clinical-adjacent signal.",
            "review",
        ),
        (
            "Nursing / charge-flow",
            "Charge and flow leaders need effective capacity, skill mix, workload, and discharge barriers in the same object.",
            "Unit packets combine boarders, effective beds, HR constraints, owner, action, and follow-up window.",
            "Nursing / flow",
            "A unit leader can identify what is blocking progression and what evidence to clear.",
            "ready",
        ),
        (
            "Human factors / UX",
            "The product should reduce cognitive work by making status, confidence, boundary, and next action immediately visible.",
            "Packet cards expose the same state grammar: urgency, confidence, owner, workflow state, safety gate.",
            "Human factors",
            "Users can compare packets without reading a long report first.",
            "review",
        ),
        (
            "Implementation scientist",
            "Adoption depends on fit with huddles, local champions, audit-and-feedback, and learning loops.",
            "Operating cadence and learning-loop rows show when signals are reviewed, who owns them, and how spread/retire decisions happen.",
            "Implementation",
            "Each packet has a follow-up window and learning metric.",
            "review",
        ),
        (
            "Data engineering / interoperability",
            "Future real feeds need curated views, canonical grains, source badges, and dependency gates before workflow dependence.",
            "Packets keep source IDs, model IDs, writeback targets, and readiness links together.",
            "Data platform",
            "Every packet can be traced to governed synthetic views and future Snowflake mappings.",
            "review",
        ),
        (
            "Executive strategist",
            "The executive surface must connect pressure, risk, resource choices, and implementation blockers to strategy.",
            "The Command Desk includes resource constraints, escalation lanes, governance blockers, and system-level learning.",
            "Executive leadership",
            "Leaders can see which decisions need sponsorship versus local action.",
            "ready",
        ),
    ]
    return [
        {
            "lens_id": f"LENS-{index:02d}",
            "lens": lens,
            "finding": finding,
            "improvement_added": improvement,
            "owner": owner,
            "acceptance_signal": acceptance,
            "status": status,
            "priority": index,
            "source_inspiration": "International command-centre, smart-hospital, clinical AI governance, patient-flow, and implementation-science patterns.",
        }
        for index, (lens, finding, improvement, owner, acceptance, status) in enumerate(lenses, start=1)
    ]


def decision_packet_rows(
    inpatient: dict[str, list[dict[str, Any]]],
    ambulatory: dict[str, list[dict[str, Any]]],
    scenarios: dict[str, list[dict[str, Any]]],
    open_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    context = latest_context(open_rows)
    scenario_by_id = {row["scenario_id"]: row for row in scenarios["scenarios"]}
    unit_warnings = sorted(inpatient["warnings"], key=lambda row: row.get("severity_rank", row.get("risk_score", 0)), reverse=True)[:3]
    program_warnings = sorted(ambulatory["warnings"], key=lambda row: row.get("severity_rank", row.get("risk_score", 0)), reverse=True)[:3]
    packets: list[dict[str, Any]] = []

    def add_packet(
        packet_id: str,
        packet_name: str,
        packet_type: str,
        urgency: str,
        object_type: str,
        object_id: str,
        site_id: str,
        service_or_program: str,
        signal: str,
        interpretation: str,
        primary_driver: str,
        now_what: str,
        owner_persona: str,
        scenario_id: str,
        confidence: str,
        source_ids: str,
        model_ids: str,
        hr_constraint: str,
        finance_constraint: str,
        expected_impact: float,
        workflow_state: str,
        huddle_cadence: str,
        follow_up_window: str,
        safety_gate: str,
        learning_metric: str,
    ) -> None:
        scenario = scenario_by_id.get(scenario_id, {})
        packets.append(
            {
                "packet_id": packet_id,
                "packet_name": packet_name,
                "packet_type": packet_type,
                "urgency": urgency,
                "object_type": object_type,
                "object_id": object_id,
                "site_id": site_id,
                "service_or_program": service_or_program,
                "signal": signal,
                "interpretation": interpretation,
                "primary_driver": primary_driver,
                "now_what": now_what,
                "owner_persona": owner_persona,
                "scenario_id": scenario_id,
                "scenario_name": scenario.get("scenario_name", "No scenario linked"),
                "confidence": confidence,
                "evidence_to_clear": "Confirm source freshness, denominator ownership, HR/resource feasibility, clinical-operational owner review, and follow-up metric.",
                "action_options": "Review drawer, compare scenario, assign owner, capture acknowledgement, schedule outcome review.",
                "safety_gate": safety_gate,
                "workflow_state": workflow_state,
                "huddle_cadence": huddle_cadence,
                "follow_up_window": follow_up_window,
                "learning_metric": learning_metric,
                "expected_impact": expected_impact,
                "hr_constraint": hr_constraint,
                "finance_constraint": finance_constraint,
                "queue_pressure": round(float(context["ed_wait_pressure_proxy"]) + expected_impact / 180, 3),
                "readiness": "review" if urgency != "Governance hold" else "blocked",
                "classification": "decision support",
                "source_ids": source_ids,
                "model_ids": model_ids,
                "writeback_table": "APP.COMMAND_DECISION_PACKET_LOG",
                "caveat": "Synthetic command packet only; not connected to real operations and not validated for clinical decision-making.",
            }
        )

    for index, warning in enumerate(unit_warnings, start=1):
        unit = next((row for row in inpatient["unitDetails"] if row["unit_id"] == warning.get("unit_id")), {})
        add_packet(
            f"PKT-UNIT-{index:03d}",
            f"{warning.get('title', unit.get('unit_name', 'Unit pressure'))} packet",
            "unit progression",
            "Now huddle",
            "unit",
            str(warning.get("unit_id", unit.get("unit_id", ""))),
            str(warning.get("site_id", unit.get("site_id", ""))),
            str(unit.get("service_line", warning.get("service_line", "inpatient"))),
            str(warning.get("message", "Unit pressure signal")),
            "Effective capacity, boarders, transfer pressure, and HR gap are aligned enough to warrant progression review.",
            "effective-bed loss plus staffed-capacity constraint",
            "Open the unit drawer, clear discharge blockers, and compare protected step-down or discharge pull-forward scenarios.",
            "Patient-flow leader",
            "SCN-INPT-STEPDOWN" if index == 1 else "SCN-INPT-DISCHARGE",
            str(unit.get("confidence", "medium")),
            str(warning.get("source_ids", unit.get("source_ids", ""))),
            str(warning.get("model_ids", unit.get("model_ids", "INPT_OCCUPANCY_FORECAST"))),
            f"{round(float(unit.get('staffing_gap_hours', 0)), 1)} aggregate gap hours",
            f"${round(float(unit.get('margin_pressure_k', 0)), 1)}k marginal pressure",
            round(18 + float(unit.get("ed_boarders", 0)) * 2.8, 1),
            "review in huddle",
            "Every 4 hours",
            "6-24 hours",
            "No action without local flow/charge review and source freshness check.",
            "boarder-hours avoided and discharge barrier resolution",
        )

    for index, warning in enumerate(program_warnings, start=1):
        program = next((row for row in ambulatory["programDetails"] if row["program_id"] == warning.get("program_id")), {})
        add_packet(
            f"PKT-PROG-{index:03d}",
            f"{warning.get('title', program.get('program', 'Program access'))} packet",
            "ambulatory access",
            "Next clinic day",
            "program",
            str(warning.get("program_id", program.get("program_id", ""))),
            str(warning.get("site_id", program.get("site_id", ""))),
            str(program.get("program", warning.get("program", "ambulatory"))),
            str(warning.get("message", "Program access signal")),
            "Referral load, urgent queue, template gap, and diagnostics readiness point to a concrete access review.",
            "template capacity plus diagnostics readiness",
            "Open the program drawer, protect urgent slots, and test virtual/outreach or diagnostics-ready template options.",
            "Ambulatory program leader",
            "SCN-AMB-SLOTS" if index == 1 else "SCN-AMB-VIRTUAL",
            str(program.get("confidence", "medium")),
            str(warning.get("source_ids", program.get("source_ids", ""))),
            str(warning.get("model_ids", program.get("model_ids", "AMBULATORY_ACCESS_FORECAST"))),
            f"{round(float(program.get('hr_gap_sessions_4w', 0)), 1)} session gap",
            f"${round(float(program.get('finance_pressure_k', 0)), 1)}k access pressure",
            round(12 + float(program.get("urgent_waitlist", 0)) * 0.35, 1),
            "owner review",
            "Weekly access huddle",
            "7-14 days",
            "No template change without program-owner review and equity/no-show impact check.",
            "urgent waitlist days avoided and TNA movement",
        )

    add_packet(
        "PKT-GOV-001",
        "Model readiness exception packet",
        "governance",
        "Governance hold",
        "model",
        "MODEL_EARLY_WARNING_DETERIORATION",
        "SITE_PROV_NETWORK",
        "AI safety",
        "A high-stakes synthetic signal is useful for design but blocked for live use.",
        "Model evidence is incomplete; silent validation, subgroup calibration, alert burden, and rollback gates are not approved.",
        "validation and governance evidence",
        "Keep the signal in implementation-readiness mode, run silent evaluation, and document release gates before any operational display.",
        "Analytics / informatics / AI team",
        "SCN-HR-FLOAT",
        "medium",
        "SRC_SYNTH_VITAL_SIGNS_AGG,SRC_SYNTH_RESPIRATORY_SUPPORT,SRC_SYNTH_HR_SHIFT_ROSTER,SRC_MODEL_VALIDATION_RESULTS",
        "MODEL_EARLY_WARNING_DETERIORATION",
        "clinical review bandwidth not approved",
        "no approved resource envelope for alert response",
        8.5,
        "blocked until governance",
        "AI governance board",
        "30-90 days",
        "Blocked until validation, human-factors, equity, monitoring, and rollback evidence exists.",
        "silent PPV, alert burden, subgroup calibration, and override review",
    )
    return packets


def operating_cadence_rows() -> list[dict[str, Any]]:
    cadences = [
        ("HUD-ED-BED", "ED-to-bed progression huddle", "Every 4 hours", "Patient-flow leader", "ED charge, bed manager, site operations, unit charge", "ED boarders, unit pressure, transfer requests", "owner, constraint, next review", 35, 6, "Boarder threshold or critical-care constraint", "APP.HUDDLE_DECISION_LOG", "ready", 0.86),
        ("HUD-DISCHARGE", "Discharge barrier sweep", "Twice daily", "Charge / flow leadership", "unit charge, pharmacy, allied health, transport", "barriers, discharge forecast, allied gaps", "barrier action list and due window", 28, 5, "barrier queue above expected range", "APP.BARRIER_ACTION_LOG", "ready", 0.82),
        ("HUD-ACCESS", "Ambulatory access huddle", "Weekly plus exception review", "Ambulatory program leader", "program manager, clinic operations, diagnostics, analytics", "TNA, urgent waitlist, template gaps", "template decision and follow-up metric", 42, 7, "urgent queue or TNA breach", "APP.ACCESS_ACTION_LOG", "review", 0.78),
        ("HUD-AI-GOV", "AI signal governance review", "Monthly / release gate", "Analytics / informatics / AI team", "clinical safety, privacy, data engineering, model owner", "validation, drift, source readiness, alert burden", "release, hold, retire, or silent-test decision", 55, 4, "model drift, blocked source, or high-stakes release", "GOVERNANCE.MODEL_REVIEW_NOTE", "blocked", 0.62),
        ("HUD-EXEC", "Provincial pediatric operations review", "Daily weekday", "Executive", "site leadership, finance, HR, clinical operations", "system posture, resource envelope, escalations", "sponsor decision or remove blocker", 45, 8, "cross-site constraint or resource trade-off", "APP.EXECUTIVE_DECISION_LOG", "review", 0.8),
    ]
    return [
        {
            "huddle_id": huddle_id,
            "cadence_name": cadence_name,
            "cadence": cadence,
            "owner": owner,
            "participants": participants,
            "input_objects": inputs,
            "expected_outputs": outputs,
            "decision_window_minutes": minutes,
            "packets_reviewed": packets,
            "escalation_triggers": triggers,
            "writeback_table": writeback,
            "status": status,
            "reliability_score": reliability,
            "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE",
        }
        for huddle_id, cadence_name, cadence, owner, participants, inputs, outputs, minutes, packets, triggers, writeback, status, reliability in cadences
    ]


def escalation_lane_rows() -> list[dict[str, Any]]:
    lanes = [
        ("ESC-FLOW", "Flow escalation", "Boarders, effective-bed loss, or transfer pressure exceeds watch threshold.", "Patient-flow leader", "confirm bed plan, discharge barrier owner, and transport constraint", "charge and site leader review", 30, 4, "review", 0.84, "boarder-hours avoided"),
        ("ESC-HR", "Workforce escalation", "Role-group gap threatens effective capacity or scenario feasibility.", "Site operations / HR", "confirm skill mix, float-pool fit, overtime risk, and redeployment limit", "aggregate workforce governance", 60, 3, "review", 0.76, "effective beds recovered"),
        ("ESC-FIN", "Resource escalation", "Scenario exceeds synthetic finance/resource envelope.", "Executive / finance partner", "decide whether resource ceiling is real constraint, deferrable work, or sponsor decision", "finance proxy not accounting truth", 240, 2, "pending", 0.7, "resource-approved actions"),
        ("ESC-SAFETY", "Clinical safety escalation", "High-stakes AI or safety signal lacks validation evidence.", "Clinical safety / AI governance", "hold display, run silent review, validate subgroup performance, confirm rollback", "blocked until governance approval", 43200, 1, "blocked", 0.58, "release gates cleared"),
        ("ESC-DATA", "Source readiness escalation", "Feed, metric definition, timestamp, or small-cell suppression check fails.", "Data engineering / interoperability", "repair curated view, document owner, rerun validation, update readiness badge", "curated Snowflake view only", 1440, 5, "review", 0.79, "source checks passing"),
    ]
    return [
        {
            "lane_id": lane_id,
            "lane": lane,
            "trigger": trigger,
            "owner": owner,
            "next_action": action,
            "safety_gate": safety_gate,
            "escalation_sla_minutes": sla,
            "active_packets": active_packets,
            "readiness": readiness,
            "reliability_score": reliability,
            "learning_metric": metric,
            "source_ids": "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE,SRC_MODEL_VALIDATION_RESULTS",
        }
        for lane_id, lane, trigger, owner, action, safety_gate, sla, active_packets, readiness, reliability, metric in lanes
    ]


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
