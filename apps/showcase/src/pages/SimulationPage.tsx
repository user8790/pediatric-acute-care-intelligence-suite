import type { AppContext, V2Data } from "../data/types";
import { ScenarioLab } from "../features/simulation/ScenarioLab";

export function SimulationPage({ data, context }: { data: V2Data; context: AppContext }) {
  return (
    <section className="dashboard-grid">
      <ScenarioLab
        inpatientScenarios={data.inpatientScenarios}
        ambulatoryScenarios={data.ambulatoryScenarios}
        inpatientForecasts={data.inpatientForecasts}
        ambulatoryForecasts={data.ambulatoryForecasts}
        coefficients={data.coefficients}
        context={context}
      />
    </section>
  );
}
