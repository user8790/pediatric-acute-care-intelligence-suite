import { CalendarClock, MapPinned, Route, TimerReset, Users } from "lucide-react";
import { KpiTile } from "../../components/KpiTile";
import { InsightPanel, Panel, PostureCard } from "../../components/Panel";
import { DriverStack } from "../../components/StructuredLists";
import type { AmbulatoryAccessPayload, AppContext, DataRow } from "../../data/types";
import { avgRows, filterBySite, formatInteger, formatPct, numberValue, stringValue, sumRows } from "../../lib/format";
import { horizonLens, roleLens } from "../../lib/narrative";

export function AmbulatoryCommand({
  mission,
  access,
  context,
}: {
  mission: DataRow[];
  access: AmbulatoryAccessPayload;
  context: AppContext;
}) {
  const scopedMission = filterBySite(mission, context.site);
  const latestAccess = filterBySite(access.latestAccess, context.site);
  const travel = filterBySite(access.travel, context.site);
  const totals = {
    waitlist: sumRows(scopedMission, "waitlist_total"),
    overTarget: sumRows(scopedMission, "waitlist_over_target"),
    medianWait: avgRows(scopedMission, "median_wait_days"),
    p90Wait: avgRows(scopedMission, "p90_wait_days"),
    tna: avgRows(scopedMission, "third_next_available_days"),
    breachRisk: avgRows(scopedMission, "urgent_breach_risk"),
    demandGap: sumRows(scopedMission, "demand_capacity_gap"),
    virtualShare: avgRows(travel, "virtual_suitable_share"),
    travelBurden: avgRows(travel, "travel_burden_index"),
  };
  const drivers = [
    stringValue(scopedMission[0], "top_driver_1", "referral demand"),
    stringValue(scopedMission[0], "top_driver_2", "template capacity"),
    stringValue(scopedMission[0], "top_driver_3", "no-show/late-cancel risk"),
  ];

  return (
    <>
      <section className="kpi-grid wide">
        <KpiTile label="Waitlist" value={formatInteger(totals.waitlist)} detail={`${formatInteger(totals.overTarget)} over target`} delta="+3.8% over 4 weeks" tone={totals.overTarget > 1000 ? "high" : "watch"} />
        <KpiTile label="Median wait" value={`${Math.round(totals.medianWait)} days`} detail={`p90 ${Math.round(totals.p90Wait)} days`} delta="+5 days vs baseline" tone="watch" />
        <KpiTile label="Third next available" value={`${Math.round(totals.tna)} days`} detail="Program median across selected scope" delta="-2 days projected" tone="neutral" />
        <KpiTile label="Urgent breach risk" value={formatPct(totals.breachRisk)} detail="Synthetic probability proxy" delta="+4 pts" tone={totals.breachRisk > 0.3 ? "high" : "watch"} />
      </section>

      <section className="posture-grid wide">
        <PostureCard icon={<CalendarClock size={19} />} label="Demand-capacity posture" value={`${formatInteger(totals.demandGap)} gap`} detail="Positive gap means weekly referral demand is above completed capacity in the selected scope." tone={totals.demandGap > 0 ? "watch" : "steady"} />
        <PostureCard icon={<MapPinned size={19} />} label="Travel and virtual lens" value={formatPct(totals.virtualShare)} detail={`Virtual-suitable proxy; travel-burden index ${totals.travelBurden.toFixed(2)}.`} tone="steady" />
        <PostureCard icon={<Route size={19} />} label="Access variation" value={`${latestAccess.length} programs`} detail="Program-level rows stay aggregate; patient-level rows are suppressed by default." tone="steady" />
      </section>

      <Panel span="normal" eyebrow="Why this changed" title="Access risk drivers" icon={<TimerReset size={22} />}>
        <DriverStack drivers={drivers} />
      </Panel>

      <Panel span="normal" eyebrow="What would I do with this?" title="Role-aware interpretation" icon={<Users size={22} />}>
        <InsightPanel
          title={context.persona}
          body={roleLens(context.persona, "ambulatory")}
          actions={[
            "Compare session, template, protected-slot, overbooking, and diagnostic-readiness scenarios.",
            "Pair TNA with waitlist ageing so short-term openings do not hide long waits.",
          ]}
          caveat="Access scenarios are data-informed planning comparisons, not scheduling directives."
        />
      </Panel>

      <Panel span="normal" eyebrow="Time lens" title={context.horizon} icon={<CalendarClock size={22} />}>
        <InsightPanel title="Forecast interpretation" body={horizonLens(context.horizon)} actions={["For seasonal views, combine forecast trends with cached public respiratory/weather context."]} />
      </Panel>
    </>
  );
}
