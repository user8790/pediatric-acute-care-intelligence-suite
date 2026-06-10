"""Scenario option helpers for command-centre interpretation panels."""

from __future__ import annotations


def inpatient_scenario_options(metrics: dict[str, float]) -> list[dict[str, object]]:
    occupancy = metrics.get("occupancy_pct", 0)
    boarders = metrics.get("ed_boarders", 0)
    staffing_gap = metrics.get("staffing_gap_pct", 0)
    discharge_confidence = metrics.get("discharge_confidence", 0.5)
    options: list[dict[str, object]] = []

    if occupancy >= 0.92:
        options.append(
            {
                "option": "Open targeted surge capacity",
                "expected_effect": "Adds short-horizon bed buffer for respiratory and surgery-linked demand.",
                "watch": "Staffing and isolation constraints may reduce usable capacity.",
            }
        )
    if boarders >= 6:
        options.append(
            {
                "option": "Accelerate ED-to-inpatient handshake",
                "expected_effect": "Reduces decision-to-bed and bed-to-arrival intervals.",
                "watch": "Unit readiness and bed-clean turnaround are the limiting resources.",
            }
        )
    if staffing_gap >= 0.08:
        options.append(
            {
                "option": "Deploy float/resource staffing",
                "expected_effect": "Restores effective beds without changing physical capacity.",
                "watch": "Skill mix should match high-acuity workload.",
            }
        )
    if discharge_confidence < 0.7:
        options.append(
            {
                "option": "Focus discharge barriers",
                "expected_effect": "Improves morning and afternoon discharge reliability.",
                "watch": "Meds, transport, imaging, and family readiness age differently.",
            }
        )
    return options[:4] or [
        {
            "option": "Maintain current escalation posture",
            "expected_effect": "Current forecast remains inside synthetic risk thresholds.",
            "watch": "Respiratory activity and staffing freshness.",
        }
    ]


def ambulatory_scenario_options(metrics: dict[str, float]) -> list[dict[str, object]]:
    backlog = metrics.get("waitlist_total", 0)
    tna = metrics.get("third_next_available_days", 0)
    no_show = metrics.get("no_show_rate", 0)
    urgent_breach = metrics.get("urgent_breach_risk", 0)
    options: list[dict[str, object]] = []

    if backlog > 1000:
        options.append(
            {
                "option": "Add pooled clinic sessions",
                "expected_effect": "Creates backlog clearance capacity across providers and sites.",
                "watch": "Room, nurse, allied-health, and diagnostic readiness constraints.",
            }
        )
    if tna > 30:
        options.append(
            {
                "option": "Rebalance new/follow-up templates",
                "expected_effect": "Improves first-appointment access without hiding follow-up debt.",
                "watch": "Condition-specific surveillance intervals.",
            }
        )
    if no_show > 0.1:
        options.append(
            {
                "option": "Use guarded overbooking and reminders",
                "expected_effect": "Improves utilization while bounding overflow risk.",
                "watch": "Fairness and travel burden impact.",
            }
        )
    if urgent_breach > 0.15:
        options.append(
            {
                "option": "Protect urgent slots",
                "expected_effect": "Reduces breach probability for time-sensitive referrals.",
                "watch": "Routine queue aging may worsen without added capacity.",
            }
        )
    return options[:4] or [
        {
            "option": "Continue current access plan",
            "expected_effect": "Backlog trend is stable in the synthetic forecast.",
            "watch": "Referral surge, cancellations, and diagnostic dependencies.",
        }
    ]

