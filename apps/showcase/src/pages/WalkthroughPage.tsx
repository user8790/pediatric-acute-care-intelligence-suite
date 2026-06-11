import { Clock3, ListChecks, MonitorPlay } from "lucide-react";
import { InsightPanel, Panel } from "../components/Panel";
import type { AppContext, V3Data } from "../data/types";
import { avgRows, formatPct, stringValue } from "../lib/format";

export function WalkthroughPage({ data, context }: { data: V3Data; context: AppContext }) {
  const occupancy = avgRows(data.inpatient.unitPressure, "occupancy_pct");
  const breach = avgRows(data.ambulatory.programAccess, "urgent_breach_risk");
  const reviewSources = data.directLinkValidation.filter((row) => stringValue(row, "overall_readiness") !== "ready").length;
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Executive walkthrough mode" title="A guided story for 3, 10, or 20 minutes" icon={<MonitorPlay size={22} />}>
        <div className="walkthrough-grid">
          <InsightPanel
            title="3-minute overview"
            body="Show the suite as a synthetic demonstration of a provincial pediatric operations layer, then point to current posture, readiness, and governance."
            actions={[`Current synthetic unit occupancy: ${formatPct(occupancy)}.`, `Current urgent ambulatory breach risk: ${formatPct(breach)}.`, `${data.modelRegistry.length} model cards and ${reviewSources} source reviews are visible.`]}
          />
          <InsightPanel
            title="10-minute walkthrough"
            body="Move from posture to inpatient, ambulatory, predictive assets, scenarios, Gatekeeper, memory, and wiring. Keep each section anchored to a named operational question."
            actions={["What is happening now?", "Which layer produced this?", "Why did risk change?", "Which options are plausible?", "What caveats and governance gates matter?"]}
          />
          <InsightPanel
            title="20-minute deep dive"
            body="Use the same path, but pause on model cards, source readiness, Snowflake writeback tables, real-data mapping, and quality checks."
            actions={["Explain curated-view mapping.", "Review scenario and warning evidence.", "Discuss local validation, rollback, and governance gates."]}
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
