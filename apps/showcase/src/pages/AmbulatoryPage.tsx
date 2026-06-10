import { CalendarClock } from "lucide-react";
import { Panel } from "../components/Panel";
import { AmbulatoryAccessViews } from "../features/ambulatory/AmbulatoryAccessViews";
import { AmbulatoryCommand } from "../features/ambulatory/AmbulatoryCommand";
import type { AppContext, V2Data } from "../data/types";

export function AmbulatoryPage({ data, context }: { data: V2Data; context: AppContext }) {
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Executive Ambulatory Access Mission Control" title="Referral pressure, waitlist ageing, clinic capacity, and access reliability" icon={<CalendarClock size={22} />}>
        <p className="section-intro">
          Program-level access intelligence covering referrals, triage, waitlists, third-next-available, clinic templates,
          no-show risk, follow-up reliability, diagnostics, virtual care, outreach, and travel burden.
        </p>
      </Panel>
      <AmbulatoryCommand mission={data.ambulatoryMission} access={data.ambulatoryAccess} context={context} />
      <AmbulatoryAccessViews access={data.ambulatoryAccess} forecasts={data.ambulatoryForecasts} context={context} />
    </section>
  );
}
