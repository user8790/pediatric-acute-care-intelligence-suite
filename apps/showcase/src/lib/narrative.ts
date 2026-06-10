export function roleLens(persona: string, area: "inpatient" | "ambulatory" | "simulation" | "governance"): string {
  if (persona.includes("Analytics")) {
    return "Review model freshness, drivers, caveats, quality status, and whether the data contract is strong enough for the next decision cycle.";
  }
  if (persona.includes("Unit")) {
    return "Focus on the units with constrained effective capacity, discharge barriers that can move today, and staffing/workload signals that may change safe flow.";
  }
  if (persona.includes("Patient-flow")) {
    return "Start with boarders, effective beds, discharge reliability, and handoff delays, then compare options by expected impact and operational risk.";
  }
  if (persona.includes("Ambulatory") || persona.includes("Clinic")) {
    return "Prioritise waitlist ageing, third-next-available, no-show-adjusted capacity, diagnostic readiness, and access trade-offs by program.";
  }
  if (area === "governance") {
    return "Use the governance view to confirm the prototype remains synthetic, aggregate-first, and ready for a curated-view real-data pathway.";
  }
  if (area === "simulation") {
    return "Use scenarios as planning comparisons: identify robust options, fairness trade-offs, and assumptions that deserve local review.";
  }
  return "Scan posture, forecast, risk drivers, and plausible options. The product is designed to make the next executive question obvious.";
}

export function horizonLens(horizon: string): string {
  if (horizon.includes("6")) return "Near-term view: operational huddles, bed turns, discharge milestones, and same-shift escalation.";
  if (horizon.includes("24")) return "One-day view: discharge reliability, OR/PACU impact, staffing, and unit-level flow risks.";
  if (horizon.includes("72")) return "Three-day view: respiratory surge, PICU/NICU step-down pressure, and scenario durability.";
  if (horizon.includes("14")) return "Two-week view: staffing patterns, outpatient follow-up reliability, and backlog movement.";
  if (horizon.includes("26")) return "Seasonal view: program capacity, demand changes, public context, and governance readiness.";
  return "Current-state view: use aggregate posture first, then drill into the reason a signal changed.";
}
