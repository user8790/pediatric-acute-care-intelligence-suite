import { BedDouble } from "lucide-react";
import { Panel } from "../components/Panel";
import { InpatientCommand } from "../features/inpatient/InpatientCommand";
import { InpatientFlowViews } from "../features/inpatient/InpatientFlowViews";
import type { AppContext, V2Data } from "../data/types";

export function InpatientPage({ data, context }: { data: V2Data; context: AppContext }) {
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Executive Inpatient Mission Control" title="Current state, 72-hour risk, bottlenecks, and scenario options" icon={<BedDouble size={22} />}>
        <p className="section-intro">
          Aggregate inpatient flow across staffed/effective capacity, ED boarding, discharge reliability, OR/PACU demand,
          PICU/NICU pressure, staffing/workload, and synthetic reliability signals.
        </p>
      </Panel>
      <InpatientCommand mission={data.inpatientMission} flow={data.inpatientFlow} context={context} />
      <InpatientFlowViews flow={data.inpatientFlow} forecasts={data.inpatientForecasts} context={context} />
    </section>
  );
}
