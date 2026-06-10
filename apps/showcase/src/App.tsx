import { useState } from "react";
import { AppHeader, ControlBand, ProductFooter, ProductNav, type PageId } from "./components/AppShell";
import { useV2Data } from "./data/v2Data";
import { HORIZONS, PERSONAS } from "./data/types";
import type { AppContext } from "./data/types";
import { AmbulatoryPage } from "./pages/AmbulatoryPage";
import { GovernancePage } from "./pages/GovernancePage";
import { InpatientPage } from "./pages/InpatientPage";
import { LandingPage } from "./pages/LandingPage";
import { MethodsPage } from "./pages/MethodsPage";
import { SimulationPage } from "./pages/SimulationPage";
import { WalkthroughPage } from "./pages/WalkthroughPage";

function App() {
  const { data, isLoading } = useV2Data();
  const [activePage, setActivePage] = useState<PageId>("overview");
  const [context, setContext] = useState<AppContext>({
    persona: PERSONAS[0],
    site: "All sites",
    horizon: HORIZONS[3],
  });

  return (
    <main className="app-shell">
      <AppHeader metadata={data.metadata} isLoading={isLoading} />
      <ControlBand context={context} setContext={setContext} generatedAt={data.metadata.generatedAt} />
      <ProductNav activePage={activePage} setActivePage={setActivePage} />

      {activePage === "overview" && <LandingPage data={data} context={context} goTo={(page) => setActivePage(page as PageId)} />}
      {activePage === "inpatient" && <InpatientPage data={data} context={context} />}
      {activePage === "ambulatory" && <AmbulatoryPage data={data} context={context} />}
      {activePage === "simulation" && <SimulationPage data={data} context={context} />}
      {activePage === "methods" && <MethodsPage data={data} />}
      {activePage === "governance" && <GovernancePage data={data} />}
      {activePage === "walkthrough" && <WalkthroughPage data={data} context={context} />}

      <ProductFooter />
    </main>
  );
}

export default App;
