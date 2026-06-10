import { Activity, BedDouble, CalendarClock, GitCompareArrows, SlidersHorizontal } from "lucide-react";
import { Panel } from "../../components/Panel";
import { ForecastRibbonChart, ScenarioFrontier, SensitivityTornado } from "../../components/ProductCharts";
import { ScenarioCards } from "../../components/StructuredLists";
import type { AppContext, DataRow } from "../../data/types";
import { roleLens } from "../../lib/narrative";

export function ScenarioLab({
  inpatientScenarios,
  ambulatoryScenarios,
  inpatientForecasts,
  ambulatoryForecasts,
  coefficients,
  context,
}: {
  inpatientScenarios: DataRow[];
  ambulatoryScenarios: DataRow[];
  inpatientForecasts: DataRow[];
  ambulatoryForecasts: DataRow[];
  coefficients: DataRow[];
  context: AppContext;
}) {
  return (
    <>
      <Panel span="wide" eyebrow="Scenario Simulation Lab" title="Precomputed scenario grids, uncertainty, and coefficient sensitivity" icon={<SlidersHorizontal size={22} />}>
        <div className="narrative-band">
          <p>{roleLens(context.persona, "simulation")}</p>
          <p>Scenario grids are generated from queueing coefficients, Monte Carlo-style uncertainty bands, and deterministic fallbacks. They are planning comparisons, not operational orders.</p>
        </div>
      </Panel>

      <Panel span="xlarge" eyebrow="Inpatient options" title="Impact, effort, risk, and boarder-hour frontier" icon={<BedDouble size={22} />}>
        <ScenarioFrontier rows={inpatientScenarios} outcomeKey="boarder_hours_mean" label="Inpatient scenario frontier" />
      </Panel>
      <Panel span="normal" eyebrow="Inpatient" title="Scenario outputs" icon={<Activity size={22} />}>
        <ScenarioCards rows={inpatientScenarios} outcomeKey="boarder_hours_mean" />
      </Panel>

      <Panel span="xlarge" eyebrow="Ambulatory options" title="Access impact and backlog frontier" icon={<CalendarClock size={22} />}>
        <ScenarioFrontier rows={ambulatoryScenarios} outcomeKey="final_backlog" label="Ambulatory scenario frontier" />
      </Panel>
      <Panel span="normal" eyebrow="Ambulatory" title="Scenario outputs" icon={<GitCompareArrows size={22} />}>
        <ScenarioCards rows={ambulatoryScenarios} outcomeKey="final_backlog" />
      </Panel>

      <Panel span="normal" eyebrow="Sensitivity" title="Coefficient tornado">
        <SensitivityTornado rows={coefficients} label="Scenario coefficient sensitivity tornado" />
      </Panel>
      <Panel span="normal" eyebrow="Occupancy risk" title="Inpatient probability band">
        <ForecastRibbonChart rows={inpatientForecasts} xKey="horizon_hours" predictionKey="threshold_probability" lowerKey="p10" upperKey="p90" label="Inpatient threshold probability scenario band" />
      </Panel>
      <Panel span="normal" eyebrow="Access risk" title="Ambulatory breach probability">
        <ForecastRibbonChart rows={ambulatoryForecasts} xKey="horizon_weeks" predictionKey="breach_probability" lowerKey="p10" upperKey="p90" label="Ambulatory breach probability scenario band" />
      </Panel>
    </>
  );
}
