import { Activity, BedDouble, HeartPulse, Radio, TimerReset, Users } from "lucide-react";
import { KpiTile } from "../../components/KpiTile";
import { InsightPanel, Panel, PostureCard } from "../../components/Panel";
import { DriverStack } from "../../components/StructuredLists";
import type { AppContext, DataRow, InpatientFlowPayload } from "../../data/types";
import { avgRows, filterBySite, formatInteger, formatPct, numberValue, stringValue, sumRows } from "../../lib/format";
import { horizonLens, roleLens } from "../../lib/narrative";

export function InpatientCommand({
  mission,
  flow,
  context,
}: {
  mission: DataRow[];
  flow: InpatientFlowPayload;
  context: AppContext;
}) {
  const scopedMission = filterBySite(mission, context.site);
  const scopedUnits = filterBySite(flow.unitPressure, context.site);
  const scopedSafety = filterBySite(flow.safety, context.site);
  const totals = {
    census: sumRows(scopedMission, "census"),
    physicalBeds: sumRows(scopedMission, "physical_beds"),
    effectiveBeds: Math.max(1, sumRows(scopedMission, "effective_beds")),
    boarders: sumRows(scopedMission, "ed_boarders"),
    discharges: sumRows(scopedMission, "predicted_discharges"),
    probAbove95: avgRows(scopedMission, "prob_above_95"),
    picuNicu: avgRows(scopedMission, "picu_nicu_pressure"),
  };
  const occupancy = totals.census / totals.effectiveBeds;
  const drivers = [
    stringValue(scopedMission[0], "top_driver_1", "effective staffed capacity"),
    stringValue(scopedMission[0], "top_driver_2", "respiratory activity"),
    stringValue(scopedMission[0], "top_driver_3", "discharge reliability"),
  ];
  const deteriorationWatch = sumRows(scopedSafety, "deterioration_watch_synth");
  const sepsisSignals = sumRows(scopedSafety, "sepsis_screen_signal_synth");

  return (
    <>
      <section className="kpi-grid wide">
        <KpiTile label="Current occupancy" value={formatPct(occupancy)} detail={`${formatInteger(totals.census)} census / ${formatInteger(totals.effectiveBeds)} effective beds`} delta="+2.6 pts vs baseline" tone={occupancy > 0.95 ? "high" : "watch"} />
        <KpiTile label="ED boarders" value={formatInteger(totals.boarders)} detail="Admitted patients awaiting inpatient placement" delta="+4 since morning" tone={totals.boarders > 20 ? "high" : "watch"} />
        <KpiTile label="Predicted discharges" value={formatInteger(totals.discharges)} detail="Expected in current planning window" delta="-3 vs target" tone="neutral" />
        <KpiTile label="Probability above 95%" value={formatPct(totals.probAbove95)} detail="Forecast threshold risk across selected scope" delta="+8 pts" tone={totals.probAbove95 > 0.5 ? "high" : "watch"} />
      </section>

      <section className="posture-grid wide">
        <PostureCard icon={<BedDouble size={19} />} label="Effective capacity posture" value={`${formatInteger(totals.effectiveBeds)} beds`} detail={`${formatInteger(totals.physicalBeds - totals.effectiveBeds)} physical beds constrained by staffing, isolation, or step-down limits.`} tone={occupancy > 0.95 ? "high" : "watch"} />
        <PostureCard icon={<Radio size={19} />} label="PICU/NICU posture" value={formatPct(totals.picuNicu)} detail="High-resource pressure and step-down availability are shown as aggregate synthetic signals." tone={totals.picuNicu > 0.9 ? "high" : "watch"} />
        <PostureCard icon={<HeartPulse size={19} />} label="Reliability and safety signals" value={`${formatInteger(deteriorationWatch)} watch`} detail={`${formatInteger(sepsisSignals)} synthetic sepsis-screen signals; demonstration indicators only.`} tone="steady" />
      </section>

      <Panel span="normal" eyebrow="Why this changed" title="Top risk drivers" icon={<Activity size={22} />}>
        <DriverStack drivers={drivers} />
      </Panel>

      <Panel span="normal" eyebrow="What would I do with this?" title="Role-aware interpretation" icon={<Users size={22} />}>
        <InsightPanel
          title={context.persona}
          body={roleLens(context.persona, "inpatient")}
          actions={[
            "Compare options by boarder-hour impact, discharge reliability, and operational risk.",
            "Use unit-level heatmaps to identify where effective capacity, not physical capacity, is the constraint.",
          ]}
          caveat="Scenario options are planning inputs, not directives."
        />
      </Panel>

      <Panel span="normal" eyebrow="Time lens" title={context.horizon} icon={<TimerReset size={22} />}>
        <InsightPanel title="Forecast interpretation" body={horizonLens(context.horizon)} actions={["Pair near-term actions with a 72-hour view so today's improvement does not create tomorrow's constraint."]} />
      </Panel>

      <Panel span="wide" eyebrow="Aggregate bed state" title="Staffed versus physical capacity, by selected scope">
        <div className="bed-state-board">
          {scopedUnits.slice(0, 12).map((row) => {
            const occ = numberValue(row, "occupancy_pct");
            return (
              <article key={`${stringValue(row, "site_id")}-${stringValue(row, "unit_id", stringValue(row, "unit_name"))}`} data-tone={occ > 1 ? "high" : occ > 0.92 ? "watch" : "steady"}>
                <span>{stringValue(row, "unit_name", stringValue(row, "service_line"))}</span>
                <strong>{formatPct(occ, 0)}</strong>
                <em>Staffing gap {formatPct(numberValue(row, "staffing_gap_pct"))}</em>
              </article>
            );
          })}
        </div>
      </Panel>
    </>
  );
}
