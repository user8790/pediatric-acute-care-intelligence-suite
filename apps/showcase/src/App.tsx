import { useState } from "react";
import { AppHeader, ControlBand, ProductFooter, ProductNav, type PageId } from "./components/AppShell";
import { useV3Data } from "./data/v3Data";
import { HORIZONS, PERSONAS } from "./data/types";
import type { AppContext, DataRow } from "./data/types";
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
  });

  const events = memoryEvents.length ? memoryEvents : data.learningMemory.events;
  function addMemoryEvent(event: DataRow) {
    setMemoryEvents((current) => [event, ...(current.length ? current : data.learningMemory.events)]);
  }

  return (
    <main className="app-shell">
      <AppHeader metadata={data.metadata} isLoading={isLoading} />
      <ControlBand context={context} setContext={setContext} generatedAt={data.metadata.generatedAt} />
      <ProductNav activePage={activePage} setActivePage={setActivePage} showInternal={showInternalWalkthrough} />

      {activePage === "posture" && <SystemPosturePage data={data} context={context} goTo={setActivePage} />}
      {activePage === "inpatient" && <FrontierInpatientPage data={data} context={context} />}
      {activePage === "ambulatory" && <FrontierAmbulatoryPage data={data} context={context} />}
      {activePage === "predictive" && <PredictiveAssetsPage data={data} />}
      {activePage === "scenarios" && <ScenarioLabPage data={data} addMemoryEvent={addMemoryEvent} />}
      {activePage === "gatekeeper" && <GatekeeperControlPlanePage data={data} />}
      {activePage === "memory" && <LearningMemoryPage data={data} events={events} addMemoryEvent={addMemoryEvent} />}
      {activePage === "wiring" && <FutureWiringPage data={data} />}
      {showInternalWalkthrough && activePage === "walkthrough" && <WalkthroughPage data={data} context={context} />}

      <ProductFooter />
    </main>
  );
}

export default App;
