import { FlaskConical, LineChart, Sigma } from "lucide-react";
import { Panel } from "../../components/Panel";
import { HorizontalBarChart, OpenContextChart, SensitivityTornado } from "../../components/ProductCharts";
import { DefinitionList, ModelCardGrid } from "../../components/StructuredLists";
import type { DataRow } from "../../data/types";

const definitions: Array<[string, string]> = [
  ["Erlang C", "Queueing approximation for probability that an arrival waits when all servers are busy."],
  ["Erlang B", "Loss-system approximation for blocking probability when no waiting room exists."],
  ["Kingman", "G/G/1 wait approximation using utilization and arrival/service variability."],
  ["Allen-Cunneen", "G/G/c wait approximation used for multi-server planning signals."],
  ["Little's Law", "Relationship between arrivals, time in system, and average number in system."],
  ["Effective beds", "Physical capacity after staffing, isolation, and step-down constraints."],
];

export function ModelExplorer({
  modelCards,
  coefficients,
  openDataContext,
}: {
  modelCards: DataRow[];
  coefficients: DataRow[];
  openDataContext: DataRow[];
}) {
  return (
    <>
      <Panel span="wide" eyebrow="Model Registry and Methods Explorer" title="Every visible model output carries identity, horizon, uncertainty, drivers, freshness, validation status, and caveat" icon={<FlaskConical size={22} />}>
        <ModelCardGrid rows={modelCards} />
      </Panel>
      <Panel span="normal" eyebrow="Coefficient registry" title="Queueing and scenario coefficients" icon={<Sigma size={22} />}>
        <HorizontalBarChart rows={coefficients} labelKey="coefficient_name" valueKey="default_value" label="Coefficient registry values" />
      </Panel>
      <Panel span="normal" eyebrow="Sensitivity" title="Planning coefficient sensitivity">
        <SensitivityTornado rows={coefficients} label="Coefficient tornado chart" />
      </Panel>
      <Panel span="normal" eyebrow="Open context" title="Cached public-context snapshots" icon={<LineChart size={22} />}>
        <OpenContextChart rows={openDataContext} />
      </Panel>
      <Panel span="wide" eyebrow="Definitions" title="Operational and modelling terms">
        <DefinitionList rows={definitions} />
      </Panel>
    </>
  );
}
