import { useEffect, useMemo, useState } from "react";
import { AppHeader, ControlBand, ProductFooter, ProductNav, type PageId } from "./components/AppShell";
import { useV3Data } from "./data/v3Data";
import { HORIZONS, PERSONAS } from "./data/types";
import type { AppContext, ControlOptions, DataRow, SelectOption } from "./data/types";
import {
  FrontierAmbulatoryPage,
  FrontierInpatientPage,
  FutureWiringPage,
  GatekeeperControlPlanePage,
  LearningMemoryPage,
  PredictiveAssetsPage,
  ScenarioLabPage,
  SystemPosturePage,
} from "./pages/FrontierPages";
import { WalkthroughPage } from "./pages/WalkthroughPage";

function App() {
  const { data, isLoading } = useV3Data();
  const showInternalWalkthrough = import.meta.env.DEV || import.meta.env.VITE_SHOW_WALKTHROUGH === "true";
  const [activePage, setActivePage] = useState<PageId>("posture");
  const [memoryEvents, setMemoryEvents] = useState<DataRow[]>(data.learningMemory.events);
  const [context, setContext] = useState<AppContext>({
    persona: PERSONAS[0],
    site: "All sites",
    horizon: HORIZONS[3],
    service: "All services",
    unit: "All units",
    program: "All programs",
    scenario: "All scenarios",
  });

  const controlOptions = useMemo<ControlOptions>(() => {
    const serviceRows = data.commandCenter.serviceLines.length
      ? data.commandCenter.serviceLines
      : data.inpatient.unitDetails;
    const services = uniqueOptions(serviceRows, "service_id", "service_line", "All services", "All services");
    const unitRows = data.inpatient.unitDetails.filter((row) => {
      const siteOk = context.site === "All sites" || String(row.site_id) === context.site;
      const serviceOk = context.service === "All services" || String(row.service_id) === context.service;
      return siteOk && serviceOk;
    });
    const units = uniqueOptions(unitRows, "unit_id", "unit_name", "All units", "All units");
    const programRows = data.ambulatory.programDetails.filter((row) => context.site === "All sites" || String(row.site_id) === context.site);
    const programs = uniqueOptions(programRows, "program_id", "program", "All programs", "All programs");
    const scenarios = uniqueOptions(data.scenarioLab.scenarios, "scenario_id", "scenario_name", "All scenarios", "All scenarios");
    return { services, units, programs, scenarios };
  }, [context.service, context.site, data.ambulatory.programDetails, data.commandCenter.serviceLines, data.inpatient.unitDetails, data.scenarioLab.scenarios]);

  useEffect(() => {
    if (!controlOptions.units.some((unit) => unit.value === context.unit)) {
      setContext((current) => ({ ...current, unit: "All units" }));
    }
    if (!controlOptions.programs.some((program) => program.value === context.program)) {
      setContext((current) => ({ ...current, program: "All programs" }));
    }
  }, [context.program, context.unit, controlOptions.programs, controlOptions.units]);

  const events = memoryEvents.length ? memoryEvents : data.learningMemory.events;
  function addMemoryEvent(event: DataRow) {
    setMemoryEvents((current) => [event, ...(current.length ? current : data.learningMemory.events)]);
  }

  return (
    <main className="app-shell">
      <AppHeader metadata={data.metadata} isLoading={isLoading} />
      <ControlBand context={context} setContext={setContext} generatedAt={data.metadata.generatedAt} controlOptions={controlOptions} />
      <ProductNav activePage={activePage} setActivePage={setActivePage} showInternal={showInternalWalkthrough} />

      {activePage === "posture" && <SystemPosturePage data={data} context={context} goTo={setActivePage} />}
      {activePage === "inpatient" && <FrontierInpatientPage data={data} context={context} />}
      {activePage === "ambulatory" && <FrontierAmbulatoryPage data={data} context={context} />}
      {activePage === "predictive" && <PredictiveAssetsPage data={data} context={context} />}
      {activePage === "scenarios" && <ScenarioLabPage data={data} context={context} addMemoryEvent={addMemoryEvent} />}
      {activePage === "gatekeeper" && <GatekeeperControlPlanePage data={data} />}
      {activePage === "memory" && <LearningMemoryPage data={data} events={events} addMemoryEvent={addMemoryEvent} />}
      {activePage === "wiring" && <FutureWiringPage data={data} />}
      {showInternalWalkthrough && activePage === "walkthrough" && <WalkthroughPage data={data} context={context} />}

      <ProductFooter />
    </main>
  );
}

function uniqueOptions(rows: DataRow[], valueKey: string, labelKey: string, allValue: string, allLabel: string): SelectOption[] {
  const seen = new Set<string>();
  const options: SelectOption[] = [{ value: allValue, label: allLabel }];
  for (const row of rows) {
    const value = String(row[valueKey] ?? "");
    const label = String(row[labelKey] ?? value);
    if (!value || seen.has(value)) continue;
    seen.add(value);
    options.push({ value, label });
  }
  return options.sort((a, b) => (a.value === allValue ? -1 : b.value === allValue ? 1 : a.label.localeCompare(b.label)));
}

export default App;
