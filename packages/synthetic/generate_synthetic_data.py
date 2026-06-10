"""Generate deterministic synthetic pediatric operations data.

The generator intentionally avoids names, MRNs, health numbers, addresses, and phone numbers.
All IDs are synthetic surrogate keys.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.core.config import (
    AGE_BANDS,
    AMBULATORY_PROGRAMS,
    SERVICE_LINES,
    SITES,
    SuiteConfig,
)
from packages.core.data_quality import (
    non_negative,
    primary_key_unique,
    scan_direct_identifiers,
    summarize_checks,
)
from packages.core.explainability import synthetic_model_card
from packages.core.optimization import ambulatory_scenario_options, inpatient_scenario_options
from packages.core.queueing import effective_staffed_beds, overbooking_slots
from packages.core.simulation import BedScenario, monte_carlo_bed_scenario, simulate_clinic_backlog
from packages.synthetic.distributions import (
    beta_rate,
    bounded_normal,
    school_day_multiplier,
    winter_respiratory_multiplier,
)


DIMENSIONS = [
    "DIM_DATE",
    "DIM_TIME_BLOCK",
    "DIM_SITE",
    "DIM_ZONE_OR_REGION",
    "DIM_UNIT",
    "DIM_BED",
    "DIM_SERVICE_LINE",
    "DIM_SPECIALTY",
    "DIM_PROVIDER_GROUP",
    "DIM_CLINIC",
    "DIM_CLINIC_TEMPLATE",
    "DIM_DIAGNOSIS_GROUP",
    "DIM_PROCEDURE_GROUP",
    "DIM_ACUITY_LEVEL",
    "DIM_AGE_BAND",
    "DIM_EQUITY_GEO_PROXY",
    "DIM_OPEN_DATA_SOURCE",
    "DIM_SCENARIO",
    "DIM_MODEL",
    "DIM_METRIC",
]

INPATIENT_FACTS = [
    "FCT_ADT_EVENT",
    "FCT_INPATIENT_ENCOUNTER",
    "FCT_BED_CENSUS_HOURLY",
    "FCT_BED_STATUS_HOURLY",
    "FCT_OCCUPANCY_SNAPSHOT",
    "FCT_ED_TO_INPATIENT_FLOW",
    "FCT_OR_CASE",
    "FCT_PACU_AND_PROCEDURAL_RECOVERY",
    "FCT_TRANSFER_REQUEST",
    "FCT_DISCHARGE_READINESS",
    "FCT_DISCHARGE_BARRIER",
    "FCT_LENGTH_OF_STAY",
    "FCT_STAFFING_ROSTER_SYNTH",
    "FCT_STAFFING_GAP_SYNTH",
    "FCT_WORKLOAD_ACUITY_SYNTH",
    "FCT_LAB_ORDER_TURNAROUND_SYNTH",
    "FCT_IMAGING_TURNAROUND_SYNTH",
    "FCT_PHARMACY_DISCHARGE_MED_SYNTH",
    "FCT_TRANSPORT_OR_PORTERING_SYNTH",
    "FCT_SAFETY_SIGNAL_SYNTH",
    "FCT_READMISSION_SYNTH",
    "FCT_MODEL_PREDICTION_INPATIENT",
    "FCT_SIMULATION_RUN_INPATIENT",
    "FCT_SIMULATION_RESULT_INPATIENT",
]

AMBULATORY_FACTS = [
    "FCT_REFERRAL",
    "FCT_REFERRAL_TRIAGE",
    "FCT_WAITLIST_SNAPSHOT",
    "FCT_APPOINTMENT",
    "FCT_CLINIC_SLOT",
    "FCT_CLINIC_TEMPLATE_CAPACITY",
    "FCT_PROVIDER_AVAILABILITY_SYNTH",
    "FCT_NO_SHOW_OR_LATE_CANCEL_SYNTH",
    "FCT_OVERDUE_FOLLOWUP_SYNTH",
    "FCT_DIAGNOSTIC_QUEUE_SYNTH",
    "FCT_PROCEDURE_QUEUE_SYNTH",
    "FCT_VIRTUAL_CARE_SYNTH",
    "FCT_POST_DISCHARGE_FOLLOWUP_SYNTH",
    "FCT_MODEL_PREDICTION_AMBULATORY",
    "FCT_SIMULATION_RUN_AMBULATORY",
    "FCT_SIMULATION_RESULT_AMBULATORY",
]

OPEN_FACTS = [
    "FCT_RESPIRATORY_VIRUS_ACTIVITY_OPEN",
    "FCT_WEATHER_AND_AIR_QUALITY_OPEN",
    "FCT_POPULATION_BY_AGE_REGION_OPEN",
    "FCT_SCHOOL_CALENDAR_OR_HOLIDAY_OPEN",
    "FCT_COMMUNITY_DEMAND_PROXY_OPEN",
    "FCT_PUBLIC_HEALTH_ALERT_OR_SEASONAL_EVENT_OPEN",
]


UNIT_TEMPLATES = [
    ("GEN", "General pediatrics", "general_pediatrics", 42, 0.84),
    ("RESP", "Respiratory cohort", "respiratory", 28, 0.88),
    ("SURG", "Surgery", "surgery", 34, 0.82),
    ("PICU", "PICU", "PICU", 20, 0.78),
    ("NICU", "NICU", "NICU", 36, 0.80),
    ("MH", "Mental health", "mental_health", 18, 0.86),
]


def _write(df: pd.DataFrame, output_dir: Path, table_name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_dir / f"{table_name.lower()}.csv", index=False)


def build_dimensions(config: SuiteConfig, rng: np.random.Generator) -> dict[str, pd.DataFrame]:
    dates = pd.date_range(config.start_date, periods=config.days, freq="D")
    dim_date = pd.DataFrame(
        {
            "date_id": [d.strftime("%Y%m%d") for d in dates],
            "date": [d.date().isoformat() for d in dates],
            "week_start_date": [d.to_period("W").start_time.date().isoformat() for d in dates],
            "month": [d.month for d in dates],
            "day_of_week": [d.day_name() for d in dates],
            "is_weekend": [d.weekday() >= 5 for d in dates],
            "synthetic_school_day": [school_day_multiplier(d.to_pydatetime()) > 1 for d in dates],
        }
    )
    time_blocks = pd.DataFrame(
        {
            "time_block_id": [f"TB_{hour:02d}" for hour in range(24)],
            "hour": list(range(24)),
            "time_block_label": [f"{hour:02d}:00-{hour:02d}:59" for hour in range(24)],
            "shift": [
                "night" if hour < 7 else "day" if hour < 19 else "evening"
                for hour in range(24)
            ],
        }
    )
    dim_site = pd.DataFrame(SITES)
    dim_zone = pd.DataFrame(
        [{"zone_id": f"ZONE_{i+1}", "zone_name": site["zone"]} for i, site in enumerate(SITES)]
    )
    units = []
    beds = []
    for site in SITES:
        scale = 0.45 if site["site_id"] == "SITE_PROV_NETWORK" else 1.0
        for suffix, unit_name, service_line, beds_count, baseline in UNIT_TEMPLATES:
            unit_beds = max(8, int(round(beds_count * scale)))
            unit_id = f"{site['site_id']}_{suffix}"
            units.append(
                {
                    "unit_id": unit_id,
                    "site_id": site["site_id"],
                    "unit_name": unit_name,
                    "service_line": service_line,
                    "physical_beds": unit_beds,
                    "baseline_occupancy": baseline,
                    "is_high_resource": service_line in {"PICU", "NICU"},
                }
            )
            for bed_num in range(1, unit_beds + 1):
                beds.append(
                    {
                        "bed_id": f"{unit_id}_BED_{bed_num:03d}",
                        "unit_id": unit_id,
                        "site_id": site["site_id"],
                        "is_isolation_capable": bool(rng.random() < 0.22),
                        "is_monitored": service_line in {"PICU", "NICU", "cardiology"},
                        "synthetic_demo": True,
                    }
                )
    dim_unit = pd.DataFrame(units)
    dim_bed = pd.DataFrame(beds)

    generic = {
        "DIM_SERVICE_LINE": pd.DataFrame(
            [{"service_line_id": f"SL_{i+1:02d}", "service_line": s} for i, s in enumerate(SERVICE_LINES)]
        ),
        "DIM_SPECIALTY": pd.DataFrame(
            [{"specialty_id": f"SPEC_{i+1:02d}", "specialty": s} for i, s in enumerate(AMBULATORY_PROGRAMS)]
        ),
        "DIM_PROVIDER_GROUP": pd.DataFrame(
            [
                {"provider_group_id": "PG_PHYS", "provider_group": "physician group synthetic"},
                {"provider_group_id": "PG_NP", "provider_group": "nurse practitioner group synthetic"},
                {"provider_group_id": "PG_AH", "provider_group": "allied health group synthetic"},
            ]
        ),
        "DIM_CLINIC": pd.DataFrame(
            [
                {
                    "clinic_id": f"{site['site_id']}_CLINIC_{program.upper()[:4]}",
                    "site_id": site["site_id"],
                    "program": program,
                    "clinic_name": f"{program.replace('_', ' ').title()} clinic synthetic",
                }
                for site in SITES
                for program in AMBULATORY_PROGRAMS
            ]
        ),
        "DIM_CLINIC_TEMPLATE": pd.DataFrame(
            [
                {
                    "clinic_template_id": f"TEMPLATE_{program.upper()[:4]}_{kind}",
                    "program": program,
                    "template_type": kind,
                    "new_visit_share": 0.42 if kind == "balanced" else 0.55,
                }
                for program in AMBULATORY_PROGRAMS
                for kind in ("balanced", "access_recovery")
            ]
        ),
        "DIM_DIAGNOSIS_GROUP": pd.DataFrame(
            [{"diagnosis_group_id": f"DG_{i+1:02d}", "diagnosis_group": s} for i, s in enumerate(SERVICE_LINES)]
        ),
        "DIM_PROCEDURE_GROUP": pd.DataFrame(
            [
                {"procedure_group_id": "PROC_DAY", "procedure_group": "day procedure synthetic"},
                {"procedure_group_id": "PROC_INPATIENT", "procedure_group": "inpatient procedure synthetic"},
                {"procedure_group_id": "PROC_DIAGNOSTIC", "procedure_group": "diagnostic procedure synthetic"},
            ]
        ),
        "DIM_ACUITY_LEVEL": pd.DataFrame(
            [
                {"acuity_level_id": "ACU_LOW", "acuity_level": "low"},
                {"acuity_level_id": "ACU_MOD", "acuity_level": "moderate"},
                {"acuity_level_id": "ACU_HIGH", "acuity_level": "high"},
                {"acuity_level_id": "ACU_CRIT", "acuity_level": "critical"},
            ]
        ),
        "DIM_AGE_BAND": pd.DataFrame(
            [{"age_band_id": f"AGE_{i+1:02d}", "age_band": band} for i, band in enumerate(AGE_BANDS)]
        ),
        "DIM_EQUITY_GEO_PROXY": pd.DataFrame(
            [
                {"equity_geo_proxy_id": "GEO_URBAN", "distance_band": "urban_0_30km", "travel_burden_index": 1},
                {"equity_geo_proxy_id": "GEO_REGIONAL", "distance_band": "regional_30_150km", "travel_burden_index": 2},
                {"equity_geo_proxy_id": "GEO_REMOTE", "distance_band": "remote_150km_plus", "travel_burden_index": 3},
            ]
        ),
        "DIM_OPEN_DATA_SOURCE": pd.DataFrame(
            [
                {"open_data_source_id": "OPEN_RESP_CA", "source_name": "PHAC FluWatch+"},
                {"open_data_source_id": "OPEN_RESP_AB", "source_name": "Alberta respiratory virus dashboard"},
                {"open_data_source_id": "OPEN_WEATHER_ECCC", "source_name": "ECCC GeoMet and AQHI"},
                {"open_data_source_id": "OPEN_STATCAN", "source_name": "Statistics Canada WDS"},
            ]
        ),
        "DIM_SCENARIO": pd.DataFrame(
            [
                {"scenario_id": "SCN_BASE", "scenario_name": "Current state baseline"},
                {"scenario_id": "SCN_RESP_SURGE", "scenario_name": "Respiratory surge"},
                {"scenario_id": "SCN_SURGE_BEDS", "scenario_name": "Open surge beds"},
                {"scenario_id": "SCN_ADD_CLINIC", "scenario_name": "Add ambulatory clinic sessions"},
                {"scenario_id": "SCN_OVERBOOK", "scenario_name": "Guarded overbooking"},
            ]
        ),
        "DIM_MODEL": pd.DataFrame(
            [
                synthetic_model_card("MODEL_INPT_OCC", "probabilistic occupancy forecast", "6-72 hours").to_dict(),
                synthetic_model_card("MODEL_DISCHARGE", "discharge by time-band probability", "same day").to_dict(),
                synthetic_model_card("MODEL_AMB_BACKLOG", "ambulatory backlog forecast", "1-26 weeks").to_dict(),
                synthetic_model_card("MODEL_NOSHOW", "no-show late-cancel risk", "appointment date").to_dict(),
            ]
        ),
        "DIM_METRIC": pd.DataFrame(
            [
                {"metric_id": "MET_OCC", "metric_name": "Occupancy percent"},
                {"metric_id": "MET_BOARD", "metric_name": "ED boarder hours"},
                {"metric_id": "MET_WAIT", "metric_name": "Wait time days"},
                {"metric_id": "MET_BACKLOG", "metric_name": "Waitlist backlog"},
                {"metric_id": "MET_QUALITY", "metric_name": "Data quality score"},
            ]
        ),
    }
    return {
        "DIM_DATE": dim_date,
        "DIM_TIME_BLOCK": time_blocks,
        "DIM_SITE": dim_site,
        "DIM_ZONE_OR_REGION": dim_zone,
        "DIM_UNIT": dim_unit,
        "DIM_BED": dim_bed,
        **generic,
    }


def build_inpatient(config: SuiteConfig, dimensions: dict[str, pd.DataFrame], rng: np.random.Generator) -> dict[str, pd.DataFrame]:
    hours = pd.date_range(config.start_date, periods=config.days * 24, freq="h")
    rows = []
    bed_status = []
    staffing_rows = []
    workload_rows = []
    safety_rows = []
    for _, unit in dimensions["DIM_UNIT"].iterrows():
        for ts in hours:
            resp = winter_respiratory_multiplier(ts.to_pydatetime())
            school = school_day_multiplier(ts.to_pydatetime())
            hour_shape = 1.07 if 10 <= ts.hour <= 22 else 0.94
            staffing_gap = beta_rate(rng, 0.055 if ts.weekday() < 5 else 0.075, 65)
            isolation_factor = 1.0 - (0.04 * (resp - 1.0) if unit.service_line == "respiratory" else 0.015)
            stepdown = 0.94 if unit.service_line in {"PICU", "NICU"} and resp > 1.25 else 1.0
            staffed = max(1, int(unit.physical_beds - rng.integers(0, 3)))
            effective = effective_staffed_beds(
                int(unit.physical_beds),
                staffed,
                staffing_gap=staffing_gap,
                isolation_factor=isolation_factor,
                stepdown_constraint_factor=stepdown,
            )
            baseline = float(unit.baseline_occupancy)
            pressure = baseline * (0.92 + 0.1 * resp) * school * hour_shape
            if unit.service_line in {"PICU", "NICU"}:
                pressure += 0.03 * (resp - 1)
            census = int(round(max(0, rng.normal(pressure * max(effective, 1), 2.2))))
            census = min(census, int(unit.physical_beds * 1.15))
            occupancy_pct = census / max(effective, 1)
            ed_boarders = max(0, int(round((occupancy_pct - 0.92) * 18 + rng.normal(1.5, 1.4))))
            discharge_confidence = bounded_normal(rng, 0.76 - max(0, occupancy_pct - 0.9) * 0.35, 0.08, 0.35, 0.95)
            predicted_discharges = max(0, int(rng.poisson(max(0.4, census * (0.045 if 7 <= ts.hour <= 15 else 0.018)))))
            rows.append(
                {
                    "census_hour_id": f"CENSUS_{unit.unit_id}_{ts.strftime('%Y%m%d%H')}",
                    "site_id": unit.site_id,
                    "unit_id": unit.unit_id,
                    "service_line": unit.service_line,
                    "ts_hour": ts.isoformat(),
                    "census": census,
                    "physical_beds": int(unit.physical_beds),
                    "staffed_beds": staffed,
                    "effective_beds": effective,
                    "occupancy_pct": round(occupancy_pct, 4),
                    "respiratory_multiplier": resp,
                    "ed_boarders": ed_boarders,
                    "predicted_discharges": predicted_discharges,
                    "discharge_confidence": round(discharge_confidence, 3),
                    "staffing_gap_pct": round(staffing_gap, 4),
                    "synthetic_demo": True,
                }
            )
            bed_status.append(
                {
                    "bed_status_hour_id": f"BEDSTAT_{unit.unit_id}_{ts.strftime('%Y%m%d%H')}",
                    "site_id": unit.site_id,
                    "unit_id": unit.unit_id,
                    "ts_hour": ts.isoformat(),
                    "clean_beds": max(0, effective - census),
                    "beds_cleaning": int(rng.poisson(1.2)),
                    "isolation_blocked_beds": max(0, int(unit.physical_beds - effective)),
                    "synthetic_demo": True,
                }
            )
            staffing_rows.append(
                {
                    "staffing_gap_id": f"STFGAP_{unit.unit_id}_{ts.strftime('%Y%m%d%H')}",
                    "site_id": unit.site_id,
                    "unit_id": unit.unit_id,
                    "ts_hour": ts.isoformat(),
                    "scheduled_staffing_hours": round(float(effective * 2.8), 1),
                    "required_staffing_hours": round(float(max(census, 1) * 3.05), 1),
                    "staffing_gap_pct": round(staffing_gap, 4),
                    "skill_mix_proxy": bounded_normal(rng, 0.86, 0.06, 0.55, 1.0),
                    "synthetic_demo": True,
                }
            )
            workload_rows.append(
                {
                    "workload_id": f"WORK_{unit.unit_id}_{ts.strftime('%Y%m%d%H')}",
                    "site_id": unit.site_id,
                    "unit_id": unit.unit_id,
                    "ts_hour": ts.isoformat(),
                    "acuity_weighted_workload_index": round(float(occupancy_pct * (1.12 if unit.is_high_resource else 1.0)), 3),
                    "synthetic_demo": True,
                }
            )
            if ts.hour == 8:
                safety_rows.append(
                    {
                        "safety_signal_id": f"SAFE_{unit.unit_id}_{ts.strftime('%Y%m%d')}",
                        "site_id": unit.site_id,
                        "unit_id": unit.unit_id,
                        "event_date": ts.date().isoformat(),
                        "deterioration_watch_count_synth": max(0, int(rng.poisson(max(0.4, occupancy_pct * 1.6)))),
                        "sepsis_screen_signal_count_synth": max(0, int(rng.poisson(0.5 if unit.service_line != "PICU" else 1.1))),
                        "medication_process_signal_count_synth": max(0, int(rng.poisson(0.7))),
                        "synthetic_demo": True,
                    }
                )

    census_df = pd.DataFrame(rows)
    latest_ts = census_df["ts_hour"].max()
    snapshot = (
        census_df[census_df["ts_hour"] == latest_ts]
        .groupby(["site_id"], as_index=False)
        .agg(
            census=("census", "sum"),
            physical_beds=("physical_beds", "sum"),
            staffed_beds=("staffed_beds", "sum"),
            effective_beds=("effective_beds", "sum"),
            ed_boarders=("ed_boarders", "sum"),
            predicted_discharges=("predicted_discharges", "sum"),
            discharge_confidence=("discharge_confidence", "mean"),
            staffing_gap_pct=("staffing_gap_pct", "mean"),
        )
    )
    snapshot["occupancy_pct"] = snapshot["census"] / snapshot["effective_beds"].clip(lower=1)
    snapshot["snapshot_ts"] = latest_ts
    snapshot["synthetic_demo"] = True
    snapshot.insert(0, "occupancy_snapshot_id", [f"SNAP_{i+1:03d}" for i in range(len(snapshot))])

    forecast_rows = []
    for _, site_row in snapshot.iterrows():
        for horizon in (6, 12, 24, 48, 72):
            drift = 0.015 * np.log1p(horizon) * (1.0 if "STOLLERY" in site_row.site_id else 0.85)
            point = min(1.18, float(site_row.occupancy_pct) + drift)
            forecast_rows.append(
                {
                    "model_prediction_id": f"PRED_INPT_{site_row.site_id}_{horizon}",
                    "site_id": site_row.site_id,
                    "model_id": "MODEL_INPT_OCC",
                    "prediction_horizon_hours": horizon,
                    "metric_name": "occupancy_pct",
                    "prediction": round(point, 4),
                    "p10": round(max(0, point - 0.08), 4),
                    "p90": round(min(1.35, point + 0.1), 4),
                    "top_driver_1": "respiratory activity",
                    "top_driver_2": "staffing gap",
                    "top_driver_3": "discharge confidence",
                    "validation_status": "synthetic demo only",
                    "synthetic_demo": True,
                }
            )
    prediction_df = pd.DataFrame(forecast_rows)

    discharge_barriers = []
    barriers = ["meds", "transport", "imaging", "consult", "family_readiness", "home_supports", "equipment"]
    for _, site in pd.DataFrame(SITES).iterrows():
        for barrier in barriers:
            discharge_barriers.append(
                {
                    "discharge_barrier_id": f"BAR_{site.site_id}_{barrier.upper()}",
                    "site_id": site.site_id,
                    "barrier_type": barrier,
                    "active_count": int(rng.poisson(8 if barrier in {"meds", "transport"} else 5)),
                    "median_age_hours": round(float(rng.gamma(2.0, 9.0)), 1),
                    "synthetic_demo": True,
                }
            )

    return {
        "FCT_BED_CENSUS_HOURLY": census_df,
        "FCT_BED_STATUS_HOURLY": pd.DataFrame(bed_status),
        "FCT_OCCUPANCY_SNAPSHOT": snapshot,
        "FCT_MODEL_PREDICTION_INPATIENT": prediction_df,
        "FCT_STAFFING_GAP_SYNTH": pd.DataFrame(staffing_rows),
        "FCT_STAFFING_ROSTER_SYNTH": pd.DataFrame(staffing_rows).rename(columns={"staffing_gap_id": "staffing_roster_id"}),
        "FCT_WORKLOAD_ACUITY_SYNTH": pd.DataFrame(workload_rows),
        "FCT_SAFETY_SIGNAL_SYNTH": pd.DataFrame(safety_rows),
        "FCT_DISCHARGE_BARRIER": pd.DataFrame(discharge_barriers),
    }


def build_ambulatory(config: SuiteConfig, dimensions: dict[str, pd.DataFrame], rng: np.random.Generator) -> dict[str, pd.DataFrame]:
    weeks = pd.date_range(config.start_date, periods=max(1, config.days // 7), freq="W-MON")
    waitlist_rows = []
    referral_rows = []
    slot_rows = []
    prediction_rows = []
    appointment_rows = []
    for site in SITES:
        for program in AMBULATORY_PROGRAMS:
            backlog = int(rng.integers(90, 280))
            for week_idx, week in enumerate(weeks):
                seasonal = winter_respiratory_multiplier(week.to_pydatetime()) if program == "respiratory" else 1.0
                referrals = int(rng.poisson((18 + 7 * rng.random()) * seasonal))
                capacity = int(rng.integers(18, 42))
                no_show_rate = beta_rate(rng, 0.075 + (0.035 if program == "mental_health" else 0.0), 80)
                completed = int(min(backlog + referrals, round(capacity * (1 - no_show_rate))))
                backlog = max(0, backlog + referrals - completed)
                third_next = int(max(3, rng.normal(backlog / max(capacity, 1) * 7, 5)))
                urgent_breach = min(0.85, backlog / max(capacity * 18, 1) + rng.normal(0, 0.015))
                waitlist_rows.append(
                    {
                        "waitlist_snapshot_id": f"WAIT_{site['site_id']}_{program}_{week_idx:03d}",
                        "site_id": site["site_id"],
                        "program": program,
                        "week_start_date": week.date().isoformat(),
                        "waitlist_total": backlog,
                        "waitlist_over_target": int(backlog * min(0.72, urgent_breach + 0.2)),
                        "median_wait_days": int(max(5, third_next * 1.35)),
                        "p90_wait_days": int(max(10, third_next * 2.4)),
                        "third_next_available_days": third_next,
                        "urgent_breach_risk": round(float(max(0, urgent_breach)), 3),
                        "synthetic_demo": True,
                    }
                )
                referral_rows.append(
                    {
                        "referral_id": f"REF_{site['site_id']}_{program}_{week_idx:03d}",
                        "site_id": site["site_id"],
                        "program": program,
                        "week_start_date": week.date().isoformat(),
                        "new_referrals": referrals,
                        "urgent_referrals": int(referrals * beta_rate(rng, 0.18, 30)),
                        "triage_turnaround_median_days": round(float(rng.gamma(2.0, 1.2)), 1),
                        "referral_completeness_pct": round(bounded_normal(rng, 0.91, 0.04, 0.7, 0.99), 3),
                        "duplicate_referral_count_synth": int(rng.poisson(0.25)),
                        "synthetic_demo": True,
                    }
                )
                slot_rows.append(
                    {
                        "clinic_slot_id": f"SLOT_{site['site_id']}_{program}_{week_idx:03d}",
                        "site_id": site["site_id"],
                        "program": program,
                        "week_start_date": week.date().isoformat(),
                        "slots_available": capacity,
                        "slots_booked": min(capacity + overbooking_slots(capacity, no_show_rate), capacity + 4),
                        "completed_visits": completed,
                        "no_show_rate": round(no_show_rate, 3),
                        "late_cancel_rate": round(beta_rate(rng, 0.035, 90), 3),
                        "virtual_share": round(beta_rate(rng, 0.22 if program != "diagnostic_procedures" else 0.08, 60), 3),
                        "new_visit_share": round(beta_rate(rng, 0.43, 50), 3),
                        "synthetic_demo": True,
                    }
                )
                appointment_rows.append(
                    {
                        "appointment_id": f"APPT_{site['site_id']}_{program}_{week_idx:03d}",
                        "site_id": site["site_id"],
                        "program": program,
                        "appointment_week": week.date().isoformat(),
                        "appointments_scheduled": capacity,
                        "appointments_completed": completed,
                        "appointments_no_show_or_late_cancel": max(0, capacity - completed),
                        "synthetic_demo": True,
                    }
                )
            latest = waitlist_rows[-1]
            for horizon in (4, 8, 12, 26):
                prediction_rows.append(
                    {
                        "model_prediction_id": f"PRED_AMB_{site['site_id']}_{program}_{horizon}",
                        "site_id": site["site_id"],
                        "program": program,
                        "model_id": "MODEL_AMB_BACKLOG",
                        "prediction_horizon_weeks": horizon,
                        "metric_name": "waitlist_total",
                        "prediction": int(latest["waitlist_total"] * max(0.62, 1 - horizon * 0.018)),
                        "p10": int(latest["waitlist_total"] * max(0.52, 1 - horizon * 0.028)),
                        "p90": int(latest["waitlist_total"] * max(0.75, 1 - horizon * 0.008)),
                        "top_driver_1": "referral demand",
                        "top_driver_2": "template capacity",
                        "top_driver_3": "no-show/late-cancel rate",
                        "validation_status": "synthetic demo only",
                        "synthetic_demo": True,
                    }
                )
    waitlist = pd.DataFrame(waitlist_rows)
    referrals = pd.DataFrame(referral_rows)
    slots = pd.DataFrame(slot_rows)
    return {
        "FCT_WAITLIST_SNAPSHOT": waitlist,
        "FCT_REFERRAL": referrals,
        "FCT_REFERRAL_TRIAGE": referrals.rename(columns={"referral_id": "referral_triage_id"}),
        "FCT_CLINIC_SLOT": slots,
        "FCT_CLINIC_TEMPLATE_CAPACITY": slots.rename(columns={"clinic_slot_id": "clinic_template_capacity_id"}),
        "FCT_APPOINTMENT": pd.DataFrame(appointment_rows),
        "FCT_MODEL_PREDICTION_AMBULATORY": pd.DataFrame(prediction_rows),
        "FCT_NO_SHOW_OR_LATE_CANCEL_SYNTH": slots[
            ["clinic_slot_id", "site_id", "program", "week_start_date", "no_show_rate", "late_cancel_rate", "synthetic_demo"]
        ].rename(columns={"clinic_slot_id": "no_show_late_cancel_id"}),
    }


def build_open_data(config: SuiteConfig) -> dict[str, pd.DataFrame]:
    weeks = pd.date_range(config.start_date, periods=max(1, config.days // 7), freq="W-MON")
    rows_resp = []
    rows_weather = []
    rows_pop = []
    rows_calendar = []
    for week in weeks:
        multiplier = winter_respiratory_multiplier(week.to_pydatetime())
        rows_resp.append(
            {
                "open_resp_id": f"OPEN_RESP_{week.strftime('%Y%W')}",
                "week_start_date": week.date().isoformat(),
                "region": "Alberta synthetic context",
                "influenza_activity_index": round(multiplier * 8.5, 2),
                "rsv_activity_index": round(multiplier * 7.9, 2),
                "source_name": "Fallback snapshot modelled from public surveillance pattern",
                "synthetic_context_fallback": True,
            }
        )
        rows_weather.append(
            {
                "open_weather_id": f"OPEN_WEATHER_{week.strftime('%Y%W')}",
                "week_start_date": week.date().isoformat(),
                "region": "Alberta pediatric corridor proxy",
                "mean_temperature_c": round(float(5 + 14 * np.sin(week.dayofyear / 365 * 6.28)), 1),
                "aqhi_max": 3 if week.month not in (5, 6, 7, 8) else 6,
                "source_name": "Fallback snapshot inspired by ECCC GeoMet/AQHI fields",
                "synthetic_context_fallback": True,
            }
        )
        rows_calendar.append(
            {
                "open_calendar_id": f"OPEN_CAL_{week.strftime('%Y%W')}",
                "week_start_date": week.date().isoformat(),
                "school_in_session_proxy": week.month not in (7, 8),
                "holiday_week_proxy": week.month == 12 or week.month == 1 and week.day < 7,
                "source_name": "Fallback calendar proxy",
                "synthetic_context_fallback": True,
            }
        )
    for site in SITES:
        for band in AGE_BANDS:
            rows_pop.append(
                {
                    "open_population_id": f"OPEN_POP_{site['site_id']}_{band}",
                    "site_id": site["site_id"],
                    "age_band": band,
                    "population_proxy": 10000 + len(band) * 750,
                    "source_name": "Fallback population proxy for Statistics Canada WDS mapping",
                    "synthetic_context_fallback": True,
                }
            )
    community = pd.DataFrame(rows_resp).copy()
    community["community_demand_proxy_id"] = community["open_resp_id"].str.replace("OPEN_RESP", "OPEN_COMM", regex=False)
    community["demand_proxy_index"] = community["influenza_activity_index"] + community["rsv_activity_index"]
    alerts = pd.DataFrame(rows_resp).copy()
    alerts["public_health_alert_id"] = alerts["open_resp_id"].str.replace("OPEN_RESP", "OPEN_ALERT", regex=False)
    alerts["seasonal_event_label"] = np.where(alerts["rsv_activity_index"] > 10, "respiratory surge watch", "seasonal baseline")
    return {
        "FCT_RESPIRATORY_VIRUS_ACTIVITY_OPEN": pd.DataFrame(rows_resp),
        "FCT_WEATHER_AND_AIR_QUALITY_OPEN": pd.DataFrame(rows_weather),
        "FCT_POPULATION_BY_AGE_REGION_OPEN": pd.DataFrame(rows_pop),
        "FCT_SCHOOL_CALENDAR_OR_HOLIDAY_OPEN": pd.DataFrame(rows_calendar),
        "FCT_COMMUNITY_DEMAND_PROXY_OPEN": community,
        "FCT_PUBLIC_HEALTH_ALERT_OR_SEASONAL_EVENT_OPEN": alerts,
    }


def generic_fact(table_name: str, rng: np.random.Generator, rows: int = 36) -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=rows, freq="D")
    return pd.DataFrame(
        {
            f"{table_name.lower()}_id": [f"{table_name}_{i:04d}" for i in range(rows)],
            "site_id": [SITES[i % len(SITES)]["site_id"] for i in range(rows)],
            "event_ts": [ts.isoformat() for ts in timestamps],
            "service_line": [SERVICE_LINES[i % len(SERVICE_LINES)] for i in range(rows)],
            "synthetic_count": rng.integers(0, 20, size=rows),
            "synthetic_rate": np.round(rng.random(rows), 3),
            "data_quality_flag": np.where(rng.random(rows) < 0.03, "review", "ok"),
            "synthetic_demo": True,
        }
    )


def build_simulation_outputs(rng: np.random.Generator) -> dict[str, pd.DataFrame]:
    inpatient_rows = []
    scenarios = [
        BedScenario(name="Current state baseline", beds=122, initial_census=110, hourly_arrival_rate=3.8),
        BedScenario(name="Respiratory surge", beds=122, initial_census=116, hourly_arrival_rate=4.6, respiratory_multiplier=1.28),
        BedScenario(name="Open surge beds", beds=132, initial_census=116, hourly_arrival_rate=4.4),
        BedScenario(name="Increase morning discharges", beds=122, initial_census=116, hourly_arrival_rate=4.2, discharge_improvement=0.16),
    ]
    for i, scenario in enumerate(scenarios):
        mc = monte_carlo_bed_scenario(BedScenario(**{**scenario.__dict__, "seed": 20260610 + i * 100}), runs=60)
        inpatient_rows.append(
            {
                "simulation_result_id": f"SIM_INPT_{i+1:03d}",
                "scenario_name": scenario.name,
                "boarder_hours_mean": round(mc["boarder_hours_mean"], 1),
                "boarder_hours_p10": round(mc["boarder_hours_p10"], 1),
                "boarder_hours_p90": round(mc["boarder_hours_p90"], 1),
                "p95_occupancy_mean": round(mc["p95_occupancy_mean"], 3),
                "synthetic_demo": True,
            }
        )
    referrals = [90 + int(rng.normal(0, 8)) for _ in range(26)]
    amb_scenarios = [
        ("Current access plan", 88, 820, 0.09, 0),
        ("Add clinics/sessions", 104, 820, 0.09, 0),
        ("Guarded overbooking", 88, 820, 0.09, 8),
        ("Reduce triage turnaround", 94, 760, 0.08, 0),
    ]
    ambulatory_rows = []
    for i, (name, capacity, backlog, no_show, overbook) in enumerate(amb_scenarios):
        sim = simulate_clinic_backlog(referrals, capacity, backlog, no_show, overbook, seed=20260610 + i)
        ambulatory_rows.append(
            {
                "simulation_result_id": f"SIM_AMB_{i+1:03d}",
                "scenario_name": name,
                "final_backlog": int(sim["final_backlog"]),
                "clearance_week": sim["clearance_week"] or 999,
                "mean_utilization": round(float(np.mean(sim["utilization_history"])), 3),
                "breach_probability_proxy": round(float(np.mean(sim["breach_risk_history"])), 3),
                "synthetic_demo": True,
            }
        )
    runs_inpatient = pd.DataFrame(
        [{"simulation_run_id": row["simulation_result_id"].replace("RESULT", "RUN"), "scenario_name": row["scenario_name"], "synthetic_demo": True} for row in inpatient_rows]
    )
    runs_ambulatory = pd.DataFrame(
        [{"simulation_run_id": row["simulation_result_id"].replace("RESULT", "RUN"), "scenario_name": row["scenario_name"], "synthetic_demo": True} for row in ambulatory_rows]
    )
    return {
        "FCT_SIMULATION_RUN_INPATIENT": runs_inpatient,
        "FCT_SIMULATION_RESULT_INPATIENT": pd.DataFrame(inpatient_rows),
        "FCT_SIMULATION_RUN_AMBULATORY": runs_ambulatory,
        "FCT_SIMULATION_RESULT_AMBULATORY": pd.DataFrame(ambulatory_rows),
    }


def build_showcase_payload(
    inpatient: dict[str, pd.DataFrame],
    ambulatory: dict[str, pd.DataFrame],
    dimensions: dict[str, pd.DataFrame],
    simulations: dict[str, pd.DataFrame],
    quality: pd.DataFrame,
) -> dict[str, object]:
    snapshot = inpatient["FCT_OCCUPANCY_SNAPSHOT"]
    latest_census = inpatient["FCT_BED_CENSUS_HOURLY"].sort_values("ts_hour").tail(18)
    forecast = inpatient["FCT_MODEL_PREDICTION_INPATIENT"]
    latest_wait = (
        ambulatory["FCT_WAITLIST_SNAPSHOT"].sort_values("week_start_date").groupby(["site_id", "program"], as_index=False).tail(1)
    )
    latest_slots = (
        ambulatory["FCT_CLINIC_SLOT"].sort_values("week_start_date").groupby(["site_id", "program"], as_index=False).tail(1)
    )
    inpatient_kpis = [
        {"label": "Occupancy", "value": round(float(snapshot["occupancy_pct"].mean() * 100), 1), "unit": "%", "trend": "+3.8"},
        {"label": "Effective beds", "value": int(snapshot["effective_beds"].sum()), "unit": "beds", "trend": "-7"},
        {"label": "ED boarders", "value": int(snapshot["ed_boarders"].sum()), "unit": "patients", "trend": "+5"},
        {"label": "Discharge confidence", "value": round(float(snapshot["discharge_confidence"].mean() * 100), 1), "unit": "%", "trend": "-4.2"},
    ]
    ambulatory_kpis = [
        {"label": "Waitlist", "value": int(latest_wait["waitlist_total"].sum()), "unit": "referrals", "trend": "+6.4"},
        {"label": "Median wait", "value": int(latest_wait["median_wait_days"].median()), "unit": "days", "trend": "+2"},
        {"label": "Third next available", "value": int(latest_wait["third_next_available_days"].median()), "unit": "days", "trend": "+3"},
        {"label": "No-show risk", "value": round(float(latest_slots["no_show_rate"].mean() * 100), 1), "unit": "%", "trend": "-0.7"},
    ]
    site_metric = snapshot.iloc[0].to_dict()
    access_metric = {
        "waitlist_total": float(latest_wait["waitlist_total"].sum()),
        "third_next_available_days": float(latest_wait["third_next_available_days"].median()),
        "no_show_rate": float(latest_slots["no_show_rate"].mean()),
        "urgent_breach_risk": float(latest_wait["urgent_breach_risk"].mean()),
    }
    return {
        "metadata": {
            "appVersion": SuiteConfig().app_version,
            "generatedAt": pd.Timestamp.now(tz="UTC").isoformat(),
            "mode": "Synthetic demonstration data",
            "clinicalUse": "Not validated for clinical decision-making",
        },
        "inpatientKpis": inpatient_kpis,
        "ambulatoryKpis": ambulatory_kpis,
        "siteSnapshots": snapshot.round(4).to_dict(orient="records"),
        "inpatientForecast": forecast.to_dict(orient="records"),
        "unitPressure": latest_census[
            ["site_id", "unit_id", "service_line", "occupancy_pct", "ed_boarders", "staffing_gap_pct"]
        ].round(4).to_dict(orient="records"),
        "dischargeBarriers": inpatient["FCT_DISCHARGE_BARRIER"].to_dict(orient="records"),
        "staffing": inpatient["FCT_STAFFING_GAP_SYNTH"].tail(36).round(4).to_dict(orient="records"),
        "safetySignals": inpatient["FCT_SAFETY_SIGNAL_SYNTH"].tail(30).to_dict(orient="records"),
        "ambulatoryAccess": latest_wait.to_dict(orient="records"),
        "clinicUtilization": latest_slots.to_dict(orient="records"),
        "referralTrend": ambulatory["FCT_REFERRAL"].tail(80).to_dict(orient="records"),
        "simulationInpatient": simulations["FCT_SIMULATION_RESULT_INPATIENT"].to_dict(orient="records"),
        "simulationAmbulatory": simulations["FCT_SIMULATION_RESULT_AMBULATORY"].to_dict(orient="records"),
        "quality": quality.to_dict(orient="records"),
        "modelCards": dimensions["DIM_MODEL"].to_dict(orient="records"),
        "inpatientOptions": inpatient_scenario_options(site_metric),
        "ambulatoryOptions": ambulatory_scenario_options(access_metric),
    }


def build_quality_summary(
    all_tables: dict[str, pd.DataFrame],
    inpatient: dict[str, pd.DataFrame],
    ambulatory: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    checks = []
    for name, df in all_tables.items():
        id_cols = [c for c in df.columns if c.endswith("_id")]
        if id_cols:
            result = primary_key_unique(df, id_cols[0])
            result["table_name"] = name
            checks.append(result)
        no_id = scan_direct_identifiers(df)
        no_id["table_name"] = name
        checks.append(no_id)
    for result in non_negative(inpatient["FCT_BED_CENSUS_HOURLY"], ["census", "physical_beds", "staffed_beds", "effective_beds"]):
        result["table_name"] = "FCT_BED_CENSUS_HOURLY"
        checks.append(result)
    for result in non_negative(ambulatory["FCT_WAITLIST_SNAPSHOT"], ["waitlist_total", "median_wait_days", "p90_wait_days"]):
        result["table_name"] = "FCT_WAITLIST_SNAPSHOT"
        checks.append(result)
    return summarize_checks(checks)[["table_name", "check", "passed", "failed_rows"]]


def main() -> None:
    config = SuiteConfig()
    rng = np.random.default_rng(config.seed)
    output_dir = Path(config.output_dir)
    showcase_public = Path(config.showcase_public_dir)
    streamlit_sample = Path(config.streamlit_sample_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    showcase_public.mkdir(parents=True, exist_ok=True)
    streamlit_sample.mkdir(parents=True, exist_ok=True)

    dimensions = build_dimensions(config, rng)
    inpatient = build_inpatient(config, dimensions, rng)
    ambulatory = build_ambulatory(config, dimensions, rng)
    open_data = build_open_data(config)
    simulations = build_simulation_outputs(rng)
    all_tables: dict[str, pd.DataFrame] = {**dimensions, **inpatient, **ambulatory, **open_data, **simulations}

    for fact_name in INPATIENT_FACTS + AMBULATORY_FACTS + OPEN_FACTS:
        if fact_name not in all_tables:
            all_tables[fact_name] = generic_fact(fact_name, rng)

    quality = build_quality_summary(all_tables, inpatient, ambulatory)
    all_tables["DATA_QUALITY_SUMMARY"] = quality

    for table_name in DIMENSIONS + INPATIENT_FACTS + AMBULATORY_FACTS + OPEN_FACTS + ["DATA_QUALITY_SUMMARY"]:
        _write(all_tables[table_name], output_dir, table_name)

    # Streamlit sample marts.
    inpatient["FCT_OCCUPANCY_SNAPSHOT"].to_csv(streamlit_sample / "inpatient_mission.csv", index=False)
    (
        ambulatory["FCT_WAITLIST_SNAPSHOT"]
        .sort_values("week_start_date")
        .groupby(["site_id", "program"], as_index=False)
        .tail(1)
        .to_csv(streamlit_sample / "ambulatory_access.csv", index=False)
    )
    quality.to_csv(streamlit_sample / "data_quality_summary.csv", index=False)
    dimensions["DIM_MODEL"].to_csv(streamlit_sample / "model_registry.csv", index=False)
    simulations["FCT_SIMULATION_RESULT_INPATIENT"].to_csv(streamlit_sample / "inpatient_simulation_results.csv", index=False)
    simulations["FCT_SIMULATION_RESULT_AMBULATORY"].to_csv(streamlit_sample / "ambulatory_simulation_results.csv", index=False)

    payload = build_showcase_payload(inpatient, ambulatory, dimensions, simulations, quality)
    (showcase_public / "demo-data.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Generated {len(all_tables)} tables into {output_dir}")
    print(f"Wrote showcase payload to {showcase_public / 'demo-data.json'}")


if __name__ == "__main__":
    main()
