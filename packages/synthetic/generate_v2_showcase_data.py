"""Generate compact v2 app-ready synthetic assets.

The v2 showcase can be ambitious, but deployed payloads should remain small. This
script precomputes 12-month synthetic histories, forecast ribbons, scenario grids,
coefficient registries, model cards, and Snowflake/Streamlit sample marts.
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

from packages.core.queueing import (  # noqa: E402
    allen_cunneen_ggc_wait,
    erlang_b_blocking_probability,
    erlang_c_wait_probability,
    kingman_gg1_wait,
    utilization,
)
from packages.synthetic.distributions import school_day_multiplier, winter_respiratory_multiplier  # noqa: E402


SEED = 20260610
SITES = [
    ("SITE_STOLLERY_INSPIRED", "Stollery-inspired", "Edmonton zone proxy"),
    ("SITE_ACH_INSPIRED", "Alberta Children's-inspired", "Calgary zone proxy"),
    ("SITE_PROV_NETWORK", "Provincial network", "Provincial pediatric network"),
]
UNITS = [
    ("General pediatrics", "general_pediatrics", 42, 0.86),
    ("Respiratory", "respiratory", 28, 0.90),
    ("Surgery", "surgery", 34, 0.82),
    ("PICU", "PICU", 20, 0.80),
    ("NICU", "NICU", 36, 0.82),
    ("Mental health", "mental_health", 18, 0.87),
    ("Oncology", "oncology", 18, 0.78),
    ("Cardiology", "cardiology", 16, 0.81),
]
PROGRAMS = [
    "respiratory",
    "cardiology",
    "neurology",
    "surgery_followup",
    "oncology_survivorship",
    "complex_care",
    "mental_health",
    "diagnostic_procedures",
]


def records(df: pd.DataFrame) -> list[dict[str, object]]:
    return json.loads(df.to_json(orient="records", date_format="iso"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def make_inpatient(rng: np.random.Generator, now: pd.Timestamp) -> dict[str, pd.DataFrame]:
    hours = pd.date_range(now - pd.Timedelta(days=365), periods=365 * 24, freq="h")
    hourly_rows: list[dict[str, object]] = []
    latest_rows: list[dict[str, object]] = []
    bed_rows: list[dict[str, object]] = []
    discharge_rows: list[dict[str, object]] = []
    handshake_rows: list[dict[str, object]] = []
    or_rows: list[dict[str, object]] = []
    high_rows: list[dict[str, object]] = []
    staffing_rows: list[dict[str, object]] = []
    safety_rows: list[dict[str, object]] = []

    for site_id, site_name, zone in SITES:
        scale = 0.55 if site_id == "SITE_PROV_NETWORK" else 1.0
        for unit_name, service_line, physical_beds, baseline in UNITS:
            beds = max(8, int(round(physical_beds * scale)))
            unit_id = f"{site_id}_{service_line.upper()}"
            sampled_hours = hours[::6]
            for ts in sampled_hours:
                resp = winter_respiratory_multiplier(ts.to_pydatetime())
                school = school_day_multiplier(ts.to_pydatetime())
                hour_effect = 1.06 if 9 <= ts.hour <= 22 else 0.93
                weekend = 0.96 if ts.weekday() >= 5 else 1.0
                staffing_gap = float(np.clip(rng.normal(0.055 + (0.02 if ts.weekday() >= 5 else 0), 0.025), 0, 0.18))
                isolation_factor = 1 - (0.04 * max(resp - 1, 0) if service_line == "respiratory" else 0.012)
                stepdown_factor = 0.93 if service_line in {"PICU", "NICU"} and resp > 1.2 else 1.0
                effective_beds = max(1, int(np.floor(beds * (1 - staffing_gap) * isolation_factor * stepdown_factor)))
                pressure = baseline * resp * school * hour_effect * weekend
                census = int(np.clip(rng.normal(pressure * effective_beds, 2.4), 0, beds * 1.16))
                occ = census / effective_beds
                boarders = max(0, int(round((occ - 0.91) * 13 + rng.normal(1.2, 1.1))))
                discharges = max(0, int(rng.poisson(census * (0.055 if 7 <= ts.hour <= 15 else 0.018))))
                hourly_rows.append(
                    {
                        "ts": ts.isoformat(),
                        "site_id": site_id,
                        "site_name": site_name,
                        "zone": zone,
                        "unit_id": unit_id,
                        "unit_name": unit_name,
                        "service_line": service_line,
                        "census": census,
                        "physical_beds": beds,
                        "effective_beds": effective_beds,
                        "occupancy_pct": round(occ, 4),
                        "staffing_gap_pct": round(staffing_gap, 4),
                        "ed_boarders": boarders,
                        "predicted_discharges": discharges,
                        "respiratory_multiplier": resp,
                    }
                )

            latest = hourly_rows[-1]
            latest_rows.append(latest)
            clean_beds = max(0, int(latest["effective_beds"]) - int(latest["census"]))
            bed_rows.append(
                {
                    "site_id": site_id,
                    "unit_id": unit_id,
                    "unit_name": unit_name,
                    "service_line": service_line,
                    "clean_ready": clean_beds,
                    "occupied": int(latest["census"]),
                    "cleaning": int(rng.poisson(1.4)),
                    "isolation_blocked": max(0, int(latest["physical_beds"]) - int(latest["effective_beds"])),
                    "monitored_or_high_resource": service_line in {"PICU", "NICU", "cardiology"},
                }
            )
            for barrier in ["pharmacy", "transport", "imaging", "consult", "family_readiness", "home_supports", "equipment"]:
                discharge_rows.append(
                    {
                        "site_id": site_id,
                        "unit_id": unit_id,
                        "barrier": barrier,
                        "active_count": int(rng.poisson(4 + int(latest["occupancy_pct"] > 0.95) * 2)),
                        "median_age_hours": round(float(rng.gamma(2.0, 8.5)), 1),
                        "p90_age_hours": round(float(rng.gamma(2.4, 13.0)), 1),
                    }
                )
            handshake_rows.append(
                {
                    "site_id": site_id,
                    "unit_id": unit_id,
                    "unit_name": unit_name,
                    "ed_admissions_awaiting_bed": int(latest["ed_boarders"]),
                    "decision_to_bed_median_min": int(np.clip(rng.normal(115 + int(latest["ed_boarders"]) * 12, 25), 35, 360)),
                    "bed_to_arrival_median_min": int(np.clip(rng.normal(38 + int(latest["occupancy_pct"] > 0.95) * 15, 11), 8, 120)),
                    "consult_bottleneck_count": int(rng.poisson(1.2 + int(latest["ed_boarders"]) / 5)),
                }
            )
            staffing_rows.append(
                {
                    "site_id": site_id,
                    "unit_id": unit_id,
                    "unit_name": unit_name,
                    "scheduled_hours": round(int(latest["effective_beds"]) * 2.8, 1),
                    "required_hours": round(int(latest["census"]) * (3.4 if service_line in {"PICU", "NICU"} else 2.95), 1),
                    "effective_beds_lost": max(0, int(latest["physical_beds"]) - int(latest["effective_beds"])),
                    "workload_index": round(float(latest["occupancy_pct"]) * (1.16 if service_line in {"PICU", "NICU"} else 1.0), 3),
                }
            )
            safety_rows.append(
                {
                    "site_id": site_id,
                    "unit_id": unit_id,
                    "unit_name": unit_name,
                    "deterioration_watch_synth": int(rng.poisson(0.8 + float(latest["occupancy_pct"]) * 1.2)),
                    "sepsis_screen_signal_synth": int(rng.poisson(0.4 + (0.8 if service_line in {"PICU", "respiratory"} else 0))),
                    "medication_process_signal_synth": int(rng.poisson(0.7)),
                    "readmission_revisit_proxy": round(float(np.clip(rng.normal(0.055, 0.018), 0.01, 0.14)), 3),
                }
            )

        for day in pd.date_range(now - pd.Timedelta(days=90), periods=91, freq="D"):
            weekday = day.weekday()
            or_rows.append(
                {
                    "date": day.date().isoformat(),
                    "site_id": site_id,
                    "elective_cases": int(rng.poisson(16 if weekday < 5 else 3)),
                    "urgent_cases": int(rng.poisson(4 if weekday < 5 else 5)),
                    "post_op_bed_demand": int(rng.poisson(7 if weekday < 5 else 3)),
                    "pacu_hold_risk": round(float(np.clip(rng.normal(0.13 if weekday < 5 else 0.08, 0.035), 0.01, 0.45)), 3),
                    "cancellation_risk": round(float(np.clip(rng.normal(0.08 if weekday < 5 else 0.04, 0.025), 0.0, 0.32)), 3),
                }
            )
        for service_line in ["PICU", "NICU"]:
            high_rows.append(
                {
                    "site_id": site_id,
                    "service_line": service_line,
                    "high_resource_beds": 20 if service_line == "PICU" else 36,
                    "occupied": int(rng.integers(15, 23 if service_line == "PICU" else 38)),
                    "step_down_ready_waiting": int(rng.poisson(3.4)),
                    "transfer_in_requests": int(rng.poisson(2.2)),
                    "ventilator_proxy_demand_synth": int(rng.poisson(8 if service_line == "PICU" else 6)),
                    "respiratory_surge_sensitivity": round(float(rng.normal(1.22, 0.08)), 3),
                }
            )

    hourly = pd.DataFrame(hourly_rows)
    latest = pd.DataFrame(latest_rows)
    mission = (
        latest.groupby(["site_id", "site_name"], as_index=False)
        .agg(
            census=("census", "sum"),
            physical_beds=("physical_beds", "sum"),
            effective_beds=("effective_beds", "sum"),
            ed_boarders=("ed_boarders", "sum"),
            predicted_discharges=("predicted_discharges", "sum"),
            staffing_gap_pct=("staffing_gap_pct", "mean"),
            respiratory_multiplier=("respiratory_multiplier", "mean"),
        )
    )
    mission["occupancy_pct"] = mission["census"] / mission["effective_beds"].clip(lower=1)
    mission["picu_nicu_pressure"] = [0.87, 0.91, 0.82]
    mission["prob_above_95"] = np.clip((mission["occupancy_pct"] - 0.80) * 2.2, 0.02, 0.92)
    mission["data_freshness"] = now.isoformat()
    mission["top_driver_1"] = "respiratory activity"
    mission["top_driver_2"] = "effective staffed capacity"
    mission["top_driver_3"] = "discharge reliability"

    forecast_rows = []
    for _, row in mission.iterrows():
        for horizon in [6, 12, 24, 48, 72]:
            drift = 0.006 * np.log1p(horizon) + (0.025 if row["respiratory_multiplier"] > 1.2 else 0)
            point = min(1.24, float(row["occupancy_pct"]) + drift)
            forecast_rows.append(
                {
                    "site_id": row["site_id"],
                    "horizon_hours": horizon,
                    "model_name": "occupancy_forecast_gradient_boosted_synth",
                    "model_version": "v2.0",
                    "prediction": round(point, 4),
                    "p10": round(max(0, point - 0.065 - horizon / 1800), 4),
                    "p90": round(min(1.35, point + 0.075 + horizon / 1600), 4),
                    "threshold_probability": round(float(np.clip((point - 0.88) * 2.8, 0.03, 0.96)), 3),
                    "top_drivers": ["respiratory activity", "staffing gap", "predicted discharges"],
                    "freshness": now.isoformat(),
                    "validation_status": "Synthetic v2 demonstration; not clinically validated",
                    "caveat": "Scenario planning estimate only.",
                }
            )
    return {
        "hourly": hourly,
        "mission": mission,
        "flow_latest": latest,
        "bed_status": pd.DataFrame(bed_rows),
        "discharge_barriers": pd.DataFrame(discharge_rows),
        "handshake": pd.DataFrame(handshake_rows),
        "or_pacu": pd.DataFrame(or_rows),
        "high_resource": pd.DataFrame(high_rows),
        "staffing": pd.DataFrame(staffing_rows),
        "safety": pd.DataFrame(safety_rows),
        "forecasts": pd.DataFrame(forecast_rows),
    }


def make_ambulatory(rng: np.random.Generator, now: pd.Timestamp) -> dict[str, pd.DataFrame]:
    weeks = pd.date_range(now - pd.Timedelta(weeks=52), periods=53, freq="W-MON")
    access_rows: list[dict[str, object]] = []
    referral_rows: list[dict[str, object]] = []
    slot_rows: list[dict[str, object]] = []
    follow_rows: list[dict[str, object]] = []
    diagnostic_rows: list[dict[str, object]] = []
    travel_rows: list[dict[str, object]] = []
    forecast_rows: list[dict[str, object]] = []

    for site_id, site_name, zone in SITES:
        for program in PROGRAMS:
            backlog = int(rng.integers(140, 420))
            for week in weeks:
                seasonal = winter_respiratory_multiplier(week.to_pydatetime()) if program == "respiratory" else 1.0
                referrals = int(rng.poisson((20 + rng.integers(0, 13)) * seasonal))
                capacity = int(rng.integers(22, 54))
                no_show = float(np.clip(rng.normal(0.08 + (0.035 if program == "mental_health" else 0), 0.025), 0.02, 0.24))
                completed = min(backlog + referrals, int(round(capacity * (1 - no_show))))
                backlog = max(0, backlog + referrals - completed)
                tna = int(np.clip(backlog / max(capacity, 1) * 6.6 + rng.normal(4, 3), 3, 140))
                urgent_breach = float(np.clip(backlog / max(capacity * 18, 1), 0.02, 0.86))
                access_rows.append(
                    {
                        "week_start": week.date().isoformat(),
                        "site_id": site_id,
                        "site_name": site_name,
                        "program": program,
                        "waitlist_total": backlog,
                        "waitlist_over_target": int(backlog * min(0.72, urgent_breach + 0.16)),
                        "median_wait_days": int(np.clip(tna * 1.24, 4, 200)),
                        "p90_wait_days": int(np.clip(tna * 2.55, 12, 360)),
                        "third_next_available_days": tna,
                        "urgent_breach_risk": round(urgent_breach, 3),
                        "demand_capacity_gap": referrals - completed,
                    }
                )
                referral_rows.append(
                    {
                        "week_start": week.date().isoformat(),
                        "site_id": site_id,
                        "program": program,
                        "new_referrals": referrals,
                        "urgent_referrals": int(referrals * np.clip(rng.normal(0.19, 0.05), 0.05, 0.45)),
                        "triage_median_days": round(float(np.clip(rng.gamma(2.1, 1.2), 0.2, 14)), 1),
                        "referral_completeness_pct": round(float(np.clip(rng.normal(0.91, 0.045), 0.72, 0.99)), 3),
                        "duplicate_or_leakage_synth": int(rng.poisson(0.32)),
                    }
                )
                slot_rows.append(
                    {
                        "week_start": week.date().isoformat(),
                        "site_id": site_id,
                        "program": program,
                        "slots_available": capacity,
                        "slots_booked": min(capacity + 5, int(capacity * (1 + min(no_show, 0.12)))),
                        "completed_visits": completed,
                        "cancelled": max(0, capacity - completed - int(round(capacity * no_show))),
                        "no_show_rate": round(no_show, 3),
                        "late_cancel_rate": round(float(np.clip(rng.normal(0.035, 0.015), 0.0, 0.12)), 3),
                        "new_visit_share": round(float(np.clip(rng.normal(0.43, 0.08), 0.2, 0.72)), 3),
                        "room_constraint": round(float(np.clip(rng.normal(0.18, 0.07), 0.02, 0.45)), 3),
                        "provider_constraint": round(float(np.clip(rng.normal(0.22, 0.08), 0.03, 0.55)), 3),
                        "nurse_allied_constraint": round(float(np.clip(rng.normal(0.14, 0.05), 0.02, 0.42)), 3),
                    }
                )
            latest = access_rows[-1]
            for horizon in [4, 8, 12, 26]:
                point = int(latest["waitlist_total"] * max(0.54, 1 - 0.018 * horizon))
                forecast_rows.append(
                    {
                        "site_id": site_id,
                        "program": program,
                        "horizon_weeks": horizon,
                        "model_name": "ambulatory_backlog_forecast_synth",
                        "model_version": "v2.0",
                        "prediction": point,
                        "p10": int(point * 0.82),
                        "p90": int(point * 1.18),
                        "breach_probability": round(float(np.clip(point / 2200, 0.03, 0.72)), 3),
                        "top_drivers": ["referral demand", "template capacity", "no-show/late-cancel risk"],
                        "freshness": now.isoformat(),
                        "validation_status": "Synthetic v2 demonstration; not clinically validated",
                        "caveat": "Backlog forecast is a planning estimate.",
                    }
                )
            follow_rows.append(
                {
                    "site_id": site_id,
                    "program": program,
                    "overdue_followup": int(rng.integers(18, 150)),
                    "post_discharge_followup_on_time_pct": round(float(np.clip(rng.normal(0.78, 0.08), 0.45, 0.96)), 3),
                    "surveillance_interval_reliability": round(float(np.clip(rng.normal(0.82, 0.07), 0.5, 0.98)), 3),
                }
            )
            diagnostic_rows.append(
                {
                    "site_id": site_id,
                    "program": program,
                    "missing_prerequisite_count": int(rng.integers(8, 64)),
                    "median_dependency_delay_days": int(rng.integers(5, 38)),
                    "pre_visit_ready_pct": round(float(np.clip(rng.normal(0.74, 0.08), 0.42, 0.96)), 3),
                    "protected_slot_scenario_gain": int(rng.integers(12, 75)),
                }
            )
            travel_rows.append(
                {
                    "site_id": site_id,
                    "program": program,
                    "virtual_suitable_share": round(float(np.clip(rng.normal(0.28, 0.11), 0.04, 0.68)), 3),
                    "regional_or_remote_share": round(float(np.clip(rng.normal(0.24, 0.09), 0.04, 0.52)), 3),
                    "travel_burden_index": round(float(np.clip(rng.normal(1.38, 0.22), 0.9, 2.4)), 3),
                    "weather_sensitivity": round(float(np.clip(rng.normal(1.08, 0.06), 0.92, 1.28)), 3),
                }
            )

    access = pd.DataFrame(access_rows)
    latest_access = access.sort_values("week_start").groupby(["site_id", "program"], as_index=False).tail(1)
    mission = (
        latest_access.groupby(["site_id"], as_index=False)
        .agg(
            waitlist_total=("waitlist_total", "sum"),
            waitlist_over_target=("waitlist_over_target", "sum"),
            median_wait_days=("median_wait_days", "median"),
            p90_wait_days=("p90_wait_days", "median"),
            third_next_available_days=("third_next_available_days", "median"),
            urgent_breach_risk=("urgent_breach_risk", "mean"),
            demand_capacity_gap=("demand_capacity_gap", "sum"),
        )
    )
    mission["data_freshness"] = now.isoformat()
    mission["top_driver_1"] = "referral demand"
    mission["top_driver_2"] = "template capacity"
    mission["top_driver_3"] = "no-show/late-cancel risk"

    return {
        "history": access,
        "latest_access": latest_access,
        "mission": mission,
        "referrals": pd.DataFrame(referral_rows),
        "slots": pd.DataFrame(slot_rows),
        "followup": pd.DataFrame(follow_rows),
        "diagnostics": pd.DataFrame(diagnostic_rows),
        "travel": pd.DataFrame(travel_rows),
        "forecasts": pd.DataFrame(forecast_rows),
    }


def make_scenarios(rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame]:
    inpatient = []
    for name, effort, risk, fairness, base in [
        ("Current state baseline", 1, 1, 0.0, 86),
        ("Open staffed surge beds", 3, 2, 0.02, 54),
        ("Increase morning discharges", 2, 1, 0.03, 61),
        ("Add evening/weekend discharge support", 3, 2, 0.04, 49),
        ("Protect PICU/NICU step-down capacity", 4, 2, 0.01, 44),
        ("Reduce bed turnaround by 20 minutes", 2, 1, 0.00, 66),
        ("Smooth elective OR load", 4, 3, 0.02, 58),
        ("Inter-site transfer support", 5, 3, 0.05, 51),
    ]:
        inpatient.append(
            {
                "scenario_name": name,
                "impact_score": int(100 - base + rng.integers(-4, 5)),
                "effort_score": effort,
                "operational_risk_score": risk,
                "fairness_proxy_delta": fairness,
                "boarder_hours_mean": int(base + rng.integers(-5, 6)),
                "boarder_hours_p10": int(base * 0.62),
                "boarder_hours_p90": int(base * 1.32),
                "bed_shortage_hours": int(base / 4 + rng.integers(0, 8)),
                "elective_cancellation_risk": round(float(np.clip(base / 500, 0.03, 0.28)), 3),
                "discharge_reliability": round(float(np.clip(0.92 - base / 500, 0.55, 0.94)), 3),
                "picu_nicu_pressure": round(float(np.clip(0.72 + base / 380, 0.72, 1.08)), 3),
            }
        )
    ambulatory = []
    for name, effort, risk, fairness, backlog in [
        ("Current access plan", 1, 1, 0.0, 1260),
        ("Add clinic sessions", 3, 2, 0.02, 850),
        ("Rebalance new/follow-up slots", 2, 2, 0.01, 940),
        ("Guarded overbooking", 3, 3, -0.01, 910),
        ("Reminder/navigation support", 2, 1, 0.05, 980),
        ("Protected urgent slots", 3, 2, 0.04, 1060),
        ("Diagnostic readiness improvement", 4, 2, 0.03, 790),
        ("Outreach/regional clinic", 5, 3, 0.08, 870),
    ]:
        ambulatory.append(
            {
                "scenario_name": name,
                "impact_score": int(100 - backlog / 18 + rng.integers(-3, 4)),
                "effort_score": effort,
                "operational_risk_score": risk,
                "fairness_proxy_delta": fairness,
                "final_backlog": int(backlog + rng.integers(-40, 41)),
                "backlog_p10": int(backlog * 0.78),
                "backlog_p90": int(backlog * 1.18),
                "clearance_weeks": int(np.clip(backlog / 72, 4, 52)),
                "urgent_breach_risk": round(float(np.clip(backlog / 4200, 0.05, 0.55)), 3),
                "slot_utilization": round(float(np.clip(0.78 + (1400 - backlog) / 5000, 0.72, 0.98)), 3),
                "no_show_adjusted_capacity": int(420 + (1260 - backlog) / 6),
            }
        )
    return pd.DataFrame(inpatient), pd.DataFrame(ambulatory)


def coefficient_registry() -> pd.DataFrame:
    rows = []
    definitions = [
        ("arrival_rate_lambda", "lambda", "Arrivals per hour/day/service/site", 4.2),
        ("service_rate_mu", "mu", "Completions per resource per time unit", 0.26),
        ("servers_resources", "c", "Beds, rooms, providers, or constrained resources", 12),
        ("utilization", "rho", "lambda / (c * mu)", utilization(4.2, 0.26, 18)),
        ("interarrival_variability", "Ca2", "Squared coefficient of variation for interarrival times", 1.15),
        ("service_variability", "Cs2", "Squared coefficient of variation for service times", 1.32),
        ("erlang_c_wait_probability", "Erlang C", "M/M/c wait probability", erlang_c_wait_probability(4.2, 0.26, 18)),
        ("erlang_b_blocking_probability", "Erlang B", "Loss-system blocking probability", erlang_b_blocking_probability(4.2, 0.26, 18)),
        ("kingman_wait_hours", "Kingman", "G/G/1 wait approximation", kingman_gg1_wait(0.22, 0.32, 1.15, 1.32).expected_wait_time),
        ("allen_cunneen_wait_hours", "Allen-Cunneen", "G/G/c wait approximation", allen_cunneen_ggc_wait(4.2, 0.26, 18, 1.15, 1.32).expected_wait_time),
        ("little_law", "L=lambda W", "System size relationship", 9.7),
        ("discharge_completion_rate", "delta_discharge", "Hourly discharge completion coefficient", 0.055),
        ("bed_turnaround_minutes", "turnaround", "EVS/bed clean turnaround", 72),
        ("effective_staffed_bed_coefficient", "effective_beds", "Capacity after staffing constraints", 0.91),
        ("isolation_constraint_factor", "isolation", "Respiratory/isolation bed constraint", 0.96),
        ("step_down_constraint_factor", "stepdown", "PICU/NICU step-down constraint", 0.93),
        ("respiratory_surge_multiplier", "resp_surge", "Respiratory activity demand multiplier", 1.35),
        ("weather_smoke_multiplier", "weather_smoke", "Weather/AQHI/smoke demand multiplier", 1.07),
        ("school_holiday_multiplier", "school_holiday", "School and holiday demand multiplier", 1.05),
        ("no_show_probability", "p_no_show", "Appointment no-show probability", 0.088),
        ("overbooking_coefficient", "overbook", "Guarded overbooking coefficient", 0.09),
        ("diagnostic_dependency_delay", "dx_delay", "Median diagnostic dependency delay in days", 14),
        ("protected_slot_coefficient", "urgent_slots", "Urgent-slot protection coefficient", 0.16),
        ("virtual_care_conversion", "virtual", "Share of visits suitable for virtual conversion", 0.27),
    ]
    for name, symbol, definition, default in definitions:
        rows.append(
            {
                "coefficient_name": name,
                "symbol": symbol,
                "definition": definition,
                "default_value": round(float(default), 5),
                "source": "synthetic v2 configuration",
                "caveat": "Demonstration coefficient; calibrate locally before operational use.",
            }
        )
    return pd.DataFrame(rows)


def model_cards(now: pd.Timestamp) -> pd.DataFrame:
    cards = []
    for model_id, name, horizon, metric in [
        ("MODEL_INPT_OCC_V2", "Probabilistic occupancy forecast", "6-72 hours", "MAE, interval coverage"),
        ("MODEL_INPT_DISCHARGE_V2", "Discharge by time-band probability", "same day", "Brier, calibration"),
        ("MODEL_INPT_PICU_V2", "PICU/NICU pressure forecast", "6-72 hours", "MAE, threshold calibration"),
        ("MODEL_AMB_BACKLOG_V2", "Ambulatory backlog forecast", "4-26 weeks", "MAE, pinball loss"),
        ("MODEL_AMB_NOSHOW_V2", "No-show and late-cancel probability", "appointment date", "AUROC, Brier, subgroup calibration"),
        ("MODEL_AMB_BREACH_V2", "Urgent breach risk", "1-12 weeks", "PR-AUC, calibration"),
    ]:
        cards.append(
            {
                "model_id": model_id,
                "model_name": name,
                "version": "v2.0",
                "prediction_horizon": horizon,
                "intended_use": "Synthetic scenario planning and executive demonstration",
                "training_data": "Deterministic synthetic pediatric operations data",
                "validation_status": "Synthetic validation only; not validated for clinical decision-making",
                "metrics": metric,
                "top_driver_method": "Permutation importance and coefficient decomposition",
                "data_freshness": now.isoformat(),
                "caveat": "Future production use requires local temporal validation, subgroup calibration, and governance approval.",
            }
        )
    return pd.DataFrame(cards)


def quality_payload(now: pd.Timestamp, rng: np.random.Generator) -> pd.DataFrame:
    tables = [
        "INPATIENT_MISSION_CONTROL",
        "INPATIENT_FLOW",
        "INPATIENT_FORECASTS",
        "INPATIENT_SCENARIOS",
        "AMBULATORY_MISSION_CONTROL",
        "AMBULATORY_ACCESS",
        "AMBULATORY_FORECASTS",
        "AMBULATORY_SCENARIOS",
        "MODEL_CARDS",
        "OPEN_DATA_CONTEXT",
    ]
    rows = []
    checks = ["freshness", "primary_key", "direct_identifier_scan", "bounds", "missingness", "timestamp_order"]
    for table in tables:
        for check in checks:
            rows.append(
                {
                    "table_name": table,
                    "check_name": check,
                    "status": "pass" if rng.random() > 0.04 else "review",
                    "failed_rows": 0 if rng.random() > 0.06 else int(rng.integers(1, 5)),
                    "last_checked": now.isoformat(),
                    "owner": "synthetic prototype data quality",
                }
            )
    return pd.DataFrame(rows)


def open_data_context(now: pd.Timestamp) -> pd.DataFrame:
    weeks = pd.date_range(now - pd.Timedelta(weeks=52), periods=53, freq="W-MON")
    rows = []
    for week in weeks:
        multiplier = winter_respiratory_multiplier(week.to_pydatetime())
        rows.append(
            {
                "week_start": week.date().isoformat(),
                "respiratory_activity_index": round(multiplier * 8.6, 2),
                "aqhi_max_proxy": 6 if week.month in [5, 6, 7, 8] else 3,
                "mean_temperature_c_proxy": round(float(5 + 16 * np.sin(week.dayofyear / 365 * 6.28)), 1),
                "school_in_session_proxy": week.month not in [7, 8],
                "holiday_week_proxy": week.month == 12 or (week.month == 1 and week.day < 8),
                "population_context": "Statistics Canada pediatric age-band mapping placeholder",
                "source_mode": "cached public-context fallback",
            }
        )
    return pd.DataFrame(rows)


def write_outputs() -> None:
    rng = np.random.default_rng(SEED)
    now = pd.Timestamp("2026-06-10T12:00:00-06:00")
    out = ROOT / "apps" / "showcase" / "public" / "data" / "v2"
    sample = ROOT / "apps" / "snowflake_streamlit" / "shared" / "sample_data"
    inpatient = make_inpatient(rng, now)
    ambulatory = make_ambulatory(rng, now)
    inpatient_scenarios, ambulatory_scenarios = make_scenarios(rng)
    coeffs = coefficient_registry()
    cards = model_cards(now)
    quality = quality_payload(now, rng)
    open_context = open_data_context(now)

    write_json(
        out / "metadata.json",
        {
            "appVersion": "v2.0",
            "generatedAt": now.isoformat(),
            "mode": "Synthetic demonstration data",
            "clinicalUse": "Not validated for clinical decision-making",
            "historyWindow": "12 months synthetic context",
            "sourceBoundary": "Future real data maps through curated governed Snowflake views only.",
        },
    )
    write_json(out / "inpatient_mission_control.json", {"rows": records(inpatient["mission"])})
    write_json(
        out / "inpatient_flow.json",
        {
            "hourly": records(inpatient["hourly"].tail(24 * 14 // 6)),
            "unitPressure": records(inpatient["flow_latest"]),
            "bedStatus": records(inpatient["bed_status"]),
            "dischargeBarriers": records(inpatient["discharge_barriers"]),
            "handshake": records(inpatient["handshake"]),
            "orPacu": records(inpatient["or_pacu"].tail(60)),
            "highResource": records(inpatient["high_resource"]),
            "staffing": records(inpatient["staffing"]),
            "safety": records(inpatient["safety"]),
        },
    )
    write_json(out / "inpatient_forecasts.json", {"rows": records(inpatient["forecasts"])})
    write_json(out / "inpatient_scenarios.json", {"rows": records(inpatient_scenarios)})
    write_json(out / "ambulatory_mission_control.json", {"rows": records(ambulatory["mission"])})
    write_json(
        out / "ambulatory_access.json",
        {
            "history": records(ambulatory["history"].tail(53 * len(PROGRAMS))),
            "latestAccess": records(ambulatory["latest_access"]),
            "referrals": records(ambulatory["referrals"].tail(53 * len(PROGRAMS))),
            "slots": records(ambulatory["slots"].tail(53 * len(PROGRAMS))),
            "followup": records(ambulatory["followup"]),
            "diagnostics": records(ambulatory["diagnostics"]),
            "travel": records(ambulatory["travel"]),
        },
    )
    write_json(out / "ambulatory_forecasts.json", {"rows": records(ambulatory["forecasts"])})
    write_json(out / "ambulatory_scenarios.json", {"rows": records(ambulatory_scenarios)})
    write_json(out / "model_cards.json", {"rows": records(cards)})
    write_json(out / "data_quality.json", {"rows": records(quality)})
    write_json(out / "open_data_context.json", {"rows": records(open_context)})
    write_json(out / "coefficient_registry.json", {"rows": records(coeffs)})

    sample.mkdir(parents=True, exist_ok=True)
    inpatient["mission"].to_csv(sample / "v2_inpatient_mission.csv", index=False)
    inpatient["flow_latest"].to_csv(sample / "v2_inpatient_flow.csv", index=False)
    inpatient["forecasts"].to_csv(sample / "v2_inpatient_forecasts.csv", index=False)
    inpatient_scenarios.to_csv(sample / "v2_inpatient_scenarios.csv", index=False)
    inpatient["or_pacu"].tail(60).to_csv(sample / "v2_inpatient_or_pacu.csv", index=False)
    inpatient["high_resource"].to_csv(sample / "v2_inpatient_high_resource.csv", index=False)
    inpatient["staffing"].to_csv(sample / "v2_inpatient_staffing.csv", index=False)
    inpatient["discharge_barriers"].to_csv(sample / "v2_inpatient_discharge_barriers.csv", index=False)
    inpatient["handshake"].to_csv(sample / "v2_inpatient_handshake.csv", index=False)
    inpatient["safety"].to_csv(sample / "v2_inpatient_safety.csv", index=False)
    pd.concat([inpatient["or_pacu"].tail(24), inpatient["high_resource"]], ignore_index=True).to_csv(sample / "v2_inpatient_or_high_resource.csv", index=False)
    pd.concat([inpatient["staffing"], inpatient["discharge_barriers"]], ignore_index=True).to_csv(sample / "v2_inpatient_staffing_discharge.csv", index=False)
    ambulatory["mission"].to_csv(sample / "v2_ambulatory_mission.csv", index=False)
    ambulatory["latest_access"].to_csv(sample / "v2_ambulatory_access.csv", index=False)
    ambulatory["forecasts"].to_csv(sample / "v2_ambulatory_forecasts.csv", index=False)
    ambulatory_scenarios.to_csv(sample / "v2_ambulatory_scenarios.csv", index=False)
    ambulatory["referrals"].tail(160).to_csv(sample / "v2_ambulatory_referrals.csv", index=False)
    ambulatory["slots"].tail(160).to_csv(sample / "v2_ambulatory_slots.csv", index=False)
    ambulatory["followup"].to_csv(sample / "v2_ambulatory_followup.csv", index=False)
    ambulatory["diagnostics"].to_csv(sample / "v2_ambulatory_diagnostics.csv", index=False)
    ambulatory["travel"].to_csv(sample / "v2_ambulatory_travel.csv", index=False)
    pd.concat([ambulatory["referrals"].tail(80), ambulatory["slots"].tail(80)], ignore_index=True).to_csv(sample / "v2_ambulatory_referral_template.csv", index=False)
    pd.concat([ambulatory["followup"], ambulatory["diagnostics"], ambulatory["travel"]], ignore_index=True).to_csv(sample / "v2_ambulatory_dependencies.csv", index=False)
    cards.to_csv(sample / "v2_model_registry.csv", index=False)
    coeffs.to_csv(sample / "v2_coefficient_registry.csv", index=False)
    quality.to_csv(sample / "v2_data_quality.csv", index=False)
    print(f"Wrote v2 assets to {out}")


if __name__ == "__main__":
    write_outputs()
