import { Clock3, ListChecks, MonitorPlay } from "lucide-react";
import { InsightPanel, Panel } from "../components/Panel";
import type { AppContext, V2Data } from "../data/types";
import { avgRows, formatPct, sumRows } from "../lib/format";

export function WalkthroughPage({ data, context }: { data: V2Data; context: AppContext }) {
  const occupancy = sumRows(data.inpatientMission, "census") / Math.max(1, sumRows(data.inpatientMission, "effective_beds"));
  const breach = avgRows(data.ambulatoryMission, "urgent_breach_risk");
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Executive walkthrough mode" title="A guided story for 3, 10, or 20 minutes" icon={<MonitorPlay size={22} />}>
        <div className="walkthrough-grid">
          <InsightPanel
            title="3-minute overview"
            body="Show the suite as a synthetic demonstration of inpatient and ambulatory operations intelligence, then point to the two current posture numbers."
            actions={[`Current inpatient occupancy: ${formatPct(occupancy)}.`, `Current urgent ambulatory breach risk: ${formatPct(breach)}.`, "Close with the governance boundary and transfer path."]}
          />
          <InsightPanel
            title="10-minute walkthrough"
            body="Move from overview to inpatient, ambulatory, simulation, methods, and governance. Keep each section anchored to a named operational question."
            actions={["What is happening now?", "What is likely next?", "Why did risk change?", "Which options are plausible?", "What caveats matter?"]}
          />
          <InsightPanel
            title="20-minute deep dive"
            body="Use the same path, but pause on model cards, coefficients, Snowflake marts, real-data mapping, and quality checks."
            actions={["Explain curated-view mapping.", "Review scenario coefficients and uncertainty.", "Discuss local validation and governance gates."]}
          />
        </div>
      </Panel>
      <Panel span="normal" eyebrow="Step 1" title="Open with posture" icon={<Clock3 size={22} />}>
        <InsightPanel title={context.horizon} body="Use the selected horizon to frame whether the discussion is a huddle, daily flow review, seasonal access plan, or executive planning conversation." />
      </Panel>
      <Panel span="normal" eyebrow="Step 2" title="Explain the bottleneck" icon={<ListChecks size={22} />}>
        <InsightPanel title="Move from signal to driver" body="Use the driver panels and heatmaps to show why risk changed, then use scenarios to make trade-offs explicit." />
      </Panel>
      <Panel span="normal" eyebrow="Step 3" title="End with guardrails">
        <InsightPanel title="Governed next step" body="The demo ends with what would be needed for a real Stollery/Snowflake connection: curated views, validation, monitoring, and local governance approval." caveat={data.metadata.clinicalUse} />
      </Panel>
    </section>
  );
}
