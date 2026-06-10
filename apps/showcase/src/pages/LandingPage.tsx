import { BedDouble, CalendarClock, GitCompareArrows, LineChart, ShieldCheck, Sparkles } from "lucide-react";
import { KpiTile } from "../components/KpiTile";
import { InsightPanel, Panel, PostureCard } from "../components/Panel";
import { OpenContextChart } from "../components/ProductCharts";
import type { AppContext, V2Data } from "../data/types";
import { avgRows, formatInteger, formatPct, siteLabel, sumRows } from "../lib/format";
import { horizonLens, roleLens } from "../lib/narrative";

export function LandingPage({ data, context, goTo }: { data: V2Data; context: AppContext; goTo: (page: string) => void }) {
  const inpatientCensus = sumRows(data.inpatientMission, "census");
  const inpatientEffective = Math.max(1, sumRows(data.inpatientMission, "effective_beds"));
  const waitlist = sumRows(data.ambulatoryMission, "waitlist_total");
  const breachRisk = avgRows(data.ambulatoryMission, "urgent_breach_risk");
  const qualityReviews = data.dataQuality.filter((row) => String(row.status) !== "pass").length;

  return (
    <section className="dashboard-grid">
      <section className="hero-surface wide">
        <div>
          <p className="eyebrow">v2 product suite</p>
          <h2>Pediatric operations intelligence that moves from posture to explanation to options.</h2>
          <p>
            A synthetic, executive-ready prototype for Alberta pediatric inpatient flow and ambulatory access. It shows what is
            happening now, what may happen next, why risk is changing, what options are available, and what caveats matter.
          </p>
          <div className="hero-actions">
            <button onClick={() => goTo("inpatient")}>
              <BedDouble size={18} />
              Inpatient command
            </button>
            <button onClick={() => goTo("ambulatory")}>
              <CalendarClock size={18} />
              Ambulatory access
            </button>
            <button onClick={() => goTo("walkthrough")}>
              <Sparkles size={18} />
              10-minute walkthrough
            </button>
          </div>
        </div>
        <div className="network-schematic" aria-label="Provincial pediatric network schematic">
          {["Emergency", "Inpatient units", "PICU/NICU", "OR/PACU", "Ambulatory", "Outreach"].map((node, index) => (
            <span key={node} style={{ ["--i" as string]: index }}>
              {node}
            </span>
          ))}
        </div>
      </section>

      <section className="kpi-grid wide">
        <KpiTile label="Inpatient occupancy" value={formatPct(inpatientCensus / inpatientEffective)} detail={`${formatInteger(inpatientCensus)} census across selected synthetic network`} delta="+2.4 pts" tone="watch" />
        <KpiTile label="Ambulatory waitlist" value={formatInteger(waitlist)} detail="Aggregate synthetic program backlog" delta="+3.8%" tone="watch" />
        <KpiTile label="Urgent breach risk" value={formatPct(breachRisk)} detail="Synthetic probability proxy" delta="+4 pts" tone="high" />
        <KpiTile label="Quality checks needing review" value={formatInteger(qualityReviews)} detail="Synthetic v2 validation checks" delta="review" tone={qualityReviews > 0 ? "watch" : "good"} />
      </section>

      <section className="posture-grid wide">
        <PostureCard icon={<LineChart size={19} />} label="Selected horizon" value={context.horizon} detail={horizonLens(context.horizon)} tone="steady" />
        <PostureCard icon={<GitCompareArrows size={19} />} label="Selected site lens" value={siteLabel(context.site)} detail="Site selection changes posture, forecasts, flow, and access interpretation." tone="steady" />
        <PostureCard icon={<ShieldCheck size={19} />} label="Safety boundary" value="Synthetic only" detail="No connection to real hospital systems and no direct identifiers." tone="steady" />
      </section>

      <Panel span="xlarge" eyebrow="Public context" title="Respiratory, weather, AQHI/smoke, and school-calendar context">
        <OpenContextChart rows={data.openDataContext} />
      </Panel>
      <Panel span="normal" eyebrow="Persona lens" title={context.persona}>
        <InsightPanel
          title="How to read this prototype"
          body={roleLens(context.persona, "simulation")}
          actions={[
            "Start with posture and forecast uncertainty.",
            "Open the relevant mission centre to understand bottlenecks.",
            "Use scenarios to compare trade-offs, not to prescribe action.",
          ]}
          caveat={data.metadata.clinicalUse}
        />
      </Panel>
    </section>
  );
}
