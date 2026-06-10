export const fallbackDemoData = {
  metadata: {
    appVersion: "0.1.0",
    generatedAt: "2026-06-10T00:00:00Z",
    mode: "Synthetic demonstration data",
    clinicalUse: "Not validated for clinical decision-making",
  },
  inpatientKpis: [
    { label: "Occupancy", value: 91.4, unit: "%", trend: "+3.1" },
    { label: "Effective beds", value: 354, unit: "beds", trend: "-6" },
    { label: "ED boarders", value: 14, unit: "patients", trend: "+4" },
    { label: "Discharge confidence", value: 72.5, unit: "%", trend: "-2.8" },
  ],
  ambulatoryKpis: [
    { label: "Waitlist", value: 4820, unit: "referrals", trend: "+5.2" },
    { label: "Median wait", value: 42, unit: "days", trend: "+3" },
    { label: "Third next available", value: 31, unit: "days", trend: "+2" },
    { label: "No-show risk", value: 8.8, unit: "%", trend: "-0.4" },
  ],
  siteSnapshots: [],
  inpatientForecast: [
    { site_id: "SITE_STOLLERY_INSPIRED", prediction_horizon_hours: 6, prediction: 0.92, p10: 0.84, p90: 1.01 },
    { site_id: "SITE_STOLLERY_INSPIRED", prediction_horizon_hours: 12, prediction: 0.94, p10: 0.86, p90: 1.04 },
    { site_id: "SITE_STOLLERY_INSPIRED", prediction_horizon_hours: 24, prediction: 0.97, p10: 0.89, p90: 1.07 },
    { site_id: "SITE_STOLLERY_INSPIRED", prediction_horizon_hours: 48, prediction: 1.01, p10: 0.93, p90: 1.11 },
    { site_id: "SITE_STOLLERY_INSPIRED", prediction_horizon_hours: 72, prediction: 1.04, p10: 0.96, p90: 1.14 },
  ],
  unitPressure: [
    { site_id: "SITE_STOLLERY_INSPIRED", unit_id: "PICU", service_line: "PICU", occupancy_pct: 0.96, ed_boarders: 2, staffing_gap_pct: 0.08 },
    { site_id: "SITE_STOLLERY_INSPIRED", unit_id: "RESP", service_line: "respiratory", occupancy_pct: 1.02, ed_boarders: 5, staffing_gap_pct: 0.07 },
  ],
  dischargeBarriers: [
    { barrier_type: "meds", active_count: 19, median_age_hours: 13 },
    { barrier_type: "transport", active_count: 15, median_age_hours: 18 },
    { barrier_type: "imaging", active_count: 9, median_age_hours: 23 },
  ],
  staffing: [],
  safetySignals: [],
  ambulatoryAccess: [
    { program: "respiratory", waitlist_total: 720, median_wait_days: 48, urgent_breach_risk: 0.22, third_next_available_days: 34 },
    { program: "cardiology", waitlist_total: 560, median_wait_days: 36, urgent_breach_risk: 0.14, third_next_available_days: 28 },
  ],
  clinicUtilization: [
    { program: "respiratory", slots_available: 36, completed_visits: 33, no_show_rate: 0.08, virtual_share: 0.21 },
    { program: "cardiology", slots_available: 30, completed_visits: 28, no_show_rate: 0.06, virtual_share: 0.18 },
  ],
  referralTrend: [],
  simulationInpatient: [
    { scenario_name: "Current state baseline", boarder_hours_mean: 44, boarder_hours_p10: 18, boarder_hours_p90: 71, p95_occupancy_mean: 1.02 },
    { scenario_name: "Open surge beds", boarder_hours_mean: 19, boarder_hours_p10: 4, boarder_hours_p90: 34, p95_occupancy_mean: 0.94 },
  ],
  simulationAmbulatory: [
    { scenario_name: "Current access plan", final_backlog: 1010, clearance_week: 999, mean_utilization: 0.96, breach_probability_proxy: 0.28 },
    { scenario_name: "Add clinics/sessions", final_backlog: 640, clearance_week: 999, mean_utilization: 0.9, breach_probability_proxy: 0.18 },
  ],
  quality: [
    { table_name: "FCT_BED_CENSUS_HOURLY", check: "census_non_negative", passed: true, failed_rows: 0 },
    { table_name: "FCT_WAITLIST_SNAPSHOT", check: "no_direct_identifiers", passed: true, failed_rows: 0 },
  ],
  modelCards: [
    {
      model_id: "MODEL_INPT_OCC",
      model_name: "probabilistic occupancy forecast",
      version: "0.1.0",
      prediction_horizon: "6-72 hours",
      validation_status: "Not validated for clinical decision-making",
      caveat: "Synthetic demo only.",
    },
  ],
  inpatientOptions: [
    { option: "Open targeted surge capacity", expected_effect: "Adds short-horizon bed buffer.", watch: "Staffing constraints." },
  ],
  ambulatoryOptions: [
    { option: "Add pooled clinic sessions", expected_effect: "Creates backlog clearance capacity.", watch: "Room and diagnostic constraints." },
  ],
};

