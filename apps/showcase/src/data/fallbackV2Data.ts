import type { V2Data } from "./types";

export const fallbackV2Data: V2Data = {
  metadata: {
    appVersion: "v2.0-fallback",
    generatedAt: "2026-06-10T12:00:00-06:00",
    mode: "Synthetic demonstration data",
    clinicalUse: "Not validated for clinical decision-making",
    historyWindow: "Compact fallback snapshot",
    sourceBoundary: "Future real data maps through curated governed Snowflake views only.",
  },
  inpatientMission: [
    {
      site_id: "SITE_STOLLERY_INSPIRED",
      site_name: "Stollery-inspired",
      census: 178,
      physical_beds: 212,
      effective_beds: 190,
      ed_boarders: 15,
      predicted_discharges: 24,
      occupancy_pct: 0.937,
      prob_above_95: 0.42,
      picu_nicu_pressure: 0.91,
      data_freshness: "2026-06-10T12:00:00-06:00",
      top_driver_1: "effective staffed capacity",
      top_driver_2: "respiratory activity",
      top_driver_3: "discharge reliability",
    },
    {
      site_id: "SITE_ACH_INSPIRED",
      site_name: "Alberta Children's-inspired",
      census: 166,
      physical_beds: 205,
      effective_beds: 184,
      ed_boarders: 11,
      predicted_discharges: 19,
      occupancy_pct: 0.902,
      prob_above_95: 0.29,
      picu_nicu_pressure: 0.88,
      data_freshness: "2026-06-10T12:00:00-06:00",
      top_driver_1: "OR demand",
      top_driver_2: "staffing gap",
      top_driver_3: "PICU/NICU step-down",
    },
  ],
  inpatientFlow: {
    hourly: [
      { ts: "2026-06-10T00:00:00-06:00", site_id: "SITE_STOLLERY_INSPIRED", census: 172, effective_beds: 190, ed_boarders: 12 },
      { ts: "2026-06-10T06:00:00-06:00", site_id: "SITE_STOLLERY_INSPIRED", census: 178, effective_beds: 190, ed_boarders: 15 },
      { ts: "2026-06-10T12:00:00-06:00", site_id: "SITE_ACH_INSPIRED", census: 166, effective_beds: 184, ed_boarders: 11 },
    ],
    unitPressure: [
      { site_id: "SITE_STOLLERY_INSPIRED", unit_name: "Respiratory", service_line: "respiratory", occupancy_pct: 1.02, staffing_gap_pct: 0.08, ed_boarders: 4 },
      { site_id: "SITE_STOLLERY_INSPIRED", unit_name: "PICU", service_line: "PICU", occupancy_pct: 0.96, staffing_gap_pct: 0.06, ed_boarders: 2 },
      { site_id: "SITE_ACH_INSPIRED", unit_name: "Surgery", service_line: "surgery", occupancy_pct: 0.88, staffing_gap_pct: 0.04, ed_boarders: 1 },
    ],
    bedStatus: [
      { site_id: "SITE_STOLLERY_INSPIRED", unit_name: "Respiratory", clean_ready: 1, occupied: 29, cleaning: 2, isolation_blocked: 3 },
      { site_id: "SITE_ACH_INSPIRED", unit_name: "Surgery", clean_ready: 5, occupied: 26, cleaning: 1, isolation_blocked: 1 },
    ],
    dischargeBarriers: [
      { site_id: "SITE_STOLLERY_INSPIRED", barrier: "pharmacy", active_count: 9, median_age_hours: 12, p90_age_hours: 32 },
      { site_id: "SITE_STOLLERY_INSPIRED", barrier: "home_supports", active_count: 7, median_age_hours: 18, p90_age_hours: 46 },
      { site_id: "SITE_ACH_INSPIRED", barrier: "transport", active_count: 5, median_age_hours: 9, p90_age_hours: 22 },
    ],
    handshake: [
      { site_id: "SITE_STOLLERY_INSPIRED", unit_name: "Respiratory", ed_admissions_awaiting_bed: 4, decision_to_bed_median_min: 166, bed_to_arrival_median_min: 49 },
      { site_id: "SITE_ACH_INSPIRED", unit_name: "Surgery", ed_admissions_awaiting_bed: 2, decision_to_bed_median_min: 112, bed_to_arrival_median_min: 38 },
    ],
    orPacu: [
      { date: "2026-06-10", site_id: "SITE_STOLLERY_INSPIRED", elective_cases: 17, urgent_cases: 4, post_op_bed_demand: 7, pacu_hold_risk: 0.16, cancellation_risk: 0.09 },
      { date: "2026-06-10", site_id: "SITE_ACH_INSPIRED", elective_cases: 15, urgent_cases: 5, post_op_bed_demand: 6, pacu_hold_risk: 0.13, cancellation_risk: 0.07 },
    ],
    highResource: [
      { site_id: "SITE_STOLLERY_INSPIRED", service_line: "PICU", occupied: 19, high_resource_beds: 20, step_down_ready_waiting: 4, transfer_in_requests: 2 },
      { site_id: "SITE_ACH_INSPIRED", service_line: "NICU", occupied: 31, high_resource_beds: 36, step_down_ready_waiting: 3, transfer_in_requests: 1 },
    ],
    staffing: [
      { site_id: "SITE_STOLLERY_INSPIRED", unit_name: "Respiratory", scheduled_hours: 78, required_hours: 86, effective_beds_lost: 4, workload_index: 1.08 },
      { site_id: "SITE_ACH_INSPIRED", unit_name: "Surgery", scheduled_hours: 76, required_hours: 73, effective_beds_lost: 2, workload_index: 0.91 },
    ],
    safety: [
      { site_id: "SITE_STOLLERY_INSPIRED", unit_name: "Respiratory", deterioration_watch_synth: 3, sepsis_screen_signal_synth: 2 },
      { site_id: "SITE_ACH_INSPIRED", unit_name: "Surgery", deterioration_watch_synth: 1, sepsis_screen_signal_synth: 1 },
    ],
  },
  inpatientForecasts: [
    { site_id: "SITE_STOLLERY_INSPIRED", horizon_hours: 6, prediction: 0.94, p10: 0.89, p90: 1.01, threshold_probability: 0.39 },
    { site_id: "SITE_STOLLERY_INSPIRED", horizon_hours: 24, prediction: 0.98, p10: 0.91, p90: 1.08, threshold_probability: 0.51 },
    { site_id: "SITE_STOLLERY_INSPIRED", horizon_hours: 72, prediction: 1.03, p10: 0.94, p90: 1.15, threshold_probability: 0.64 },
    { site_id: "SITE_ACH_INSPIRED", horizon_hours: 24, prediction: 0.91, p10: 0.84, p90: 1.0, threshold_probability: 0.31 },
  ],
  inpatientScenarios: [
    { scenario_name: "Current state baseline", impact_score: 16, effort_score: 1, operational_risk_score: 1, fairness_proxy_delta: 0, boarder_hours_mean: 86, boarder_hours_p10: 53, boarder_hours_p90: 114 },
    { scenario_name: "Protect PICU/NICU step-down capacity", impact_score: 55, effort_score: 4, operational_risk_score: 2, fairness_proxy_delta: 0.01, boarder_hours_mean: 44, boarder_hours_p10: 27, boarder_hours_p90: 58 },
    { scenario_name: "Add evening/weekend discharge support", impact_score: 50, effort_score: 3, operational_risk_score: 2, fairness_proxy_delta: 0.04, boarder_hours_mean: 49, boarder_hours_p10: 30, boarder_hours_p90: 65 },
  ],
  ambulatoryMission: [
    { site_id: "SITE_STOLLERY_INSPIRED", waitlist_total: 2110, waitlist_over_target: 730, median_wait_days: 49, p90_wait_days: 123, third_next_available_days: 39, urgent_breach_risk: 0.29, demand_capacity_gap: 22 },
    { site_id: "SITE_ACH_INSPIRED", waitlist_total: 1950, waitlist_over_target: 640, median_wait_days: 44, p90_wait_days: 112, third_next_available_days: 36, urgent_breach_risk: 0.25, demand_capacity_gap: 16 },
  ],
  ambulatoryAccess: {
    history: [
      { week_start: "2026-05-25", site_id: "SITE_STOLLERY_INSPIRED", program: "respiratory", waitlist_total: 310, third_next_available_days: 36 },
      { week_start: "2026-06-01", site_id: "SITE_STOLLERY_INSPIRED", program: "respiratory", waitlist_total: 326, third_next_available_days: 39 },
    ],
    latestAccess: [
      { site_id: "SITE_STOLLERY_INSPIRED", program: "respiratory", waitlist_total: 326, waitlist_over_target: 118, median_wait_days: 46, p90_wait_days: 124, third_next_available_days: 39, urgent_breach_risk: 0.31 },
      { site_id: "SITE_ACH_INSPIRED", program: "cardiology", waitlist_total: 284, waitlist_over_target: 86, median_wait_days: 41, p90_wait_days: 103, third_next_available_days: 33, urgent_breach_risk: 0.22 },
    ],
    referrals: [
      { week_start: "2026-06-01", site_id: "SITE_STOLLERY_INSPIRED", program: "respiratory", new_referrals: 34, urgent_referrals: 8, triage_median_days: 2.4, referral_completeness_pct: 0.93 },
    ],
    slots: [
      { week_start: "2026-06-01", site_id: "SITE_STOLLERY_INSPIRED", program: "respiratory", slots_available: 42, completed_visits: 37, no_show_rate: 0.09, late_cancel_rate: 0.03, new_visit_share: 0.47 },
    ],
    followup: [{ site_id: "SITE_STOLLERY_INSPIRED", program: "respiratory", overdue_followup: 45, post_discharge_followup_on_time_pct: 0.78 }],
    diagnostics: [{ site_id: "SITE_STOLLERY_INSPIRED", program: "respiratory", missing_prerequisite_count: 24, median_dependency_delay_days: 14, pre_visit_ready_pct: 0.76 }],
    travel: [{ site_id: "SITE_STOLLERY_INSPIRED", program: "respiratory", virtual_suitable_share: 0.31, regional_or_remote_share: 0.26, travel_burden_index: 1.42 }],
  },
  ambulatoryForecasts: [
    { site_id: "SITE_STOLLERY_INSPIRED", program: "respiratory", horizon_weeks: 4, prediction: 301, p10: 247, p90: 356, breach_probability: 0.19 },
    { site_id: "SITE_STOLLERY_INSPIRED", program: "respiratory", horizon_weeks: 12, prediction: 251, p10: 205, p90: 296, breach_probability: 0.15 },
    { site_id: "SITE_STOLLERY_INSPIRED", program: "respiratory", horizon_weeks: 26, prediction: 182, p10: 149, p90: 215, breach_probability: 0.1 },
  ],
  ambulatoryScenarios: [
    { scenario_name: "Current access plan", impact_score: 29, effort_score: 1, operational_risk_score: 1, fairness_proxy_delta: 0, final_backlog: 1260, backlog_p10: 982, backlog_p90: 1486 },
    { scenario_name: "Diagnostic readiness improvement", impact_score: 57, effort_score: 4, operational_risk_score: 2, fairness_proxy_delta: 0.03, final_backlog: 790, backlog_p10: 616, backlog_p90: 932 },
    { scenario_name: "Outreach/regional clinic", impact_score: 52, effort_score: 5, operational_risk_score: 3, fairness_proxy_delta: 0.08, final_backlog: 870, backlog_p10: 679, backlog_p90: 1027 },
  ],
  modelCards: [
    {
      model_id: "MODEL_INPT_OCC_V2",
      model_name: "Probabilistic occupancy forecast",
      version: "v2.0",
      prediction_horizon: "6-72 hours",
      validation_status: "Synthetic validation only; not validated for clinical decision-making",
      metrics: "MAE, interval coverage",
      top_driver_method: "Permutation importance and coefficient decomposition",
      data_freshness: "2026-06-10T12:00:00-06:00",
      caveat: "Future production use requires local temporal validation, subgroup calibration, and governance approval.",
    },
  ],
  dataQuality: [
    { table_name: "INPATIENT_MISSION_CONTROL", check_name: "direct_identifier_scan", status: "pass", failed_rows: 0, last_checked: "2026-06-10T12:00:00-06:00" },
    { table_name: "AMBULATORY_ACCESS", check_name: "timestamp_order", status: "pass", failed_rows: 0, last_checked: "2026-06-10T12:00:00-06:00" },
  ],
  openDataContext: [
    { week_start: "2026-06-01", respiratory_activity_index: 9.8, aqhi_max_proxy: 4, mean_temperature_c_proxy: 18.1, school_in_session_proxy: true, source_mode: "cached public-context fallback" },
  ],
  coefficients: [
    { coefficient_name: "arrival_rate_lambda", symbol: "lambda", definition: "Arrivals per hour/day/service/site", default_value: 4.2, caveat: "Demonstration coefficient; calibrate locally before operational use." },
    { coefficient_name: "erlang_c_wait_probability", symbol: "Erlang C", definition: "M/M/c wait probability", default_value: 0.157, caveat: "Demonstration coefficient; calibrate locally before operational use." },
  ],
};
