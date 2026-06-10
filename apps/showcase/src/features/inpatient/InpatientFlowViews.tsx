import { GitBranch, Hospital, Network, Stethoscope, TimerReset } from "lucide-react";
import {
  DischargeFunnel,
  FlowSankey,
  ForecastRibbonChart,
  HorizontalBarChart,
  UnitPressureHeatmap,
  WorkloadMatrix,
} from "../../components/ProductCharts";
import { Panel } from "../../components/Panel";
import type { AppContext, DataRow, InpatientFlowPayload } from "../../data/types";
import { filterBySite } from "../../lib/format";

export function InpatientFlowViews({
  flow,
  forecasts,
  context,
}: {
  flow: InpatientFlowPayload;
  forecasts: DataRow[];
  context: AppContext;
}) {
  const unitPressure = filterBySite(flow.unitPressure, context.site);
  const barriers = filterBySite(flow.dischargeBarriers, context.site);
  const handshake = filterBySite(flow.handshake, context.site);
  const orPacu = filterBySite(flow.orPacu, context.site);
  const highResource = filterBySite(flow.highResource, context.site);
  const staffing = filterBySite(flow.staffing, context.site);
  const scopedForecasts = filterBySite(forecasts, context.site);

  return (
    <>
      <Panel span="xlarge" eyebrow="6h to 72h" title="Occupancy forecast ribbon" icon={<Hospital size={22} />}>
        <ForecastRibbonChart rows={scopedForecasts} xKey="horizon_hours" predictionKey="prediction" lowerKey="p10" upperKey="p90" label="Occupancy forecast with uncertainty band" />
      </Panel>
      <Panel span="normal" eyebrow="Unit pressure" title="Staffed/effective capacity heatmap" icon={<Stethoscope size={22} />}>
        <UnitPressureHeatmap rows={unitPressure} />
      </Panel>
      <Panel span="xlarge" eyebrow="ED-to-inpatient handshake" title="Boarding and handoff network" icon={<Network size={22} />}>
        <FlowSankey rows={handshake} />
      </Panel>
      <Panel span="normal" eyebrow="Discharge reliability" title="Barrier funnel" icon={<GitBranch size={22} />}>
        <DischargeFunnel rows={barriers} />
      </Panel>
      <Panel span="normal" eyebrow="OR/PACU impact" title="Post-op bed demand and hold risk">
        <HorizontalBarChart rows={orPacu} labelKey="date" valueKey="post_op_bed_demand" label="OR and PACU post-op bed demand" />
      </Panel>
      <Panel span="normal" eyebrow="PICU/NICU" title="Step-down bottleneck">
        <HorizontalBarChart rows={highResource} labelKey="service_line" valueKey="step_down_ready_waiting" label="PICU/NICU step-down waiting" />
      </Panel>
      <Panel span="normal" eyebrow="Staffing/workload" title="Pressure matrix" icon={<TimerReset size={22} />}>
        <WorkloadMatrix rows={staffing} />
      </Panel>
    </>
  );
}
