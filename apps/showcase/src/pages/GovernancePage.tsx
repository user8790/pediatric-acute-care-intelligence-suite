import type { V2Data } from "../data/types";
import { GovernanceExplorer } from "../features/governance/GovernanceExplorer";

export function GovernancePage({ data }: { data: V2Data }) {
  return (
    <section className="dashboard-grid">
      <GovernanceExplorer quality={data.dataQuality} openDataContext={data.openDataContext} />
    </section>
  );
}
