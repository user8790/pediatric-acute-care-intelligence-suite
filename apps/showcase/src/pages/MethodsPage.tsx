import type { V2Data } from "../data/types";
import { ModelExplorer } from "../features/methods/ModelExplorer";

export function MethodsPage({ data }: { data: V2Data }) {
  return (
    <section className="dashboard-grid">
      <ModelExplorer modelCards={data.modelCards} coefficients={data.coefficients} openDataContext={data.openDataContext} />
    </section>
  );
}
