import {
  Activity,
  BedDouble,
  CalendarClock,
  ClipboardCheck,
  DatabaseZap,
  FileText,
  FlaskConical,
  Gauge,
  GitBranch,
  HeartPulse,
  LineChart,
  MapPin,
  Network,
  Radio,
  ShieldCheck,
  SlidersHorizontal,
  Stethoscope,
  TimerReset,
  Users,
} from "lucide-react";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { BarList, ForecastBand, HeatGrid, KpiTile } from "./components/Charts";
import { fallbackDemoData } from "./data/fallbackDemoData";

type Kpi = { label: string; value: number; unit: string; trend: string };
type Option = { option: string; expected_effect: string; watch: string };
type DemoData = {
  metadata: { appVersion: string; generatedAt: string; mode: string; clinicalUse: string };
  inpatientKpis: Kpi[];
  ambulatoryKpis: Kpi[];
  siteSnapshots: Record<string, unknown>[];
  inpatientForecast: Record<string, unknown>[];
  unitPressure: Record<string, unknown>[];
  dischargeBarriers: Record<string, unknown>[];
  staffing: Record<string, unknown>[];
  safetySignals: Record<string, unknown>[];
  ambulatoryAccess: Record<string, unknown>[];
  clinicUtilization: Record<string, unknown>[];
  referralTrend: Record<string, unknown>[];
  simulationInpatient: Record<string, unknown>[];
  simulationAmbulatory: Record<string, unknown>[];
  quality: Record<string, unknown>[];
  modelCards: Record<string, unknown>[];
  inpatientOptions: Option[];
  ambulatoryOptions: Option[];
};

const tabs = [
  { id: "inpatient", label: "Inpatient", icon: BedDouble },
  { id: "ambulatory", label: "Ambulatory", icon: CalendarClock },
  { id: "simulation", label: "Simulation", icon: SlidersHorizontal },
  { id: "methods", label: "Methods", icon: FlaskConical },
  { id: "quality", label: "Quality", icon: ShieldCheck },
  { id: "governance", label: "Governance", icon: FileText },
] as const;

const personas = [
  "Executive",
  "Site operations",
  "Patient flow",
  "Unit manager",
  "Ambulatory program",
  "Analytics",
];

const inpatientModules = [
  ["Flow command", "ADT, beds, EVS, transport, staffing", "1-5 min future feed"],
  ["Deterioration watch", "Vitals, PEWS, labs, oxygen support", "5-15 min future feed"],
  ["Sepsis surveillance", "Labs, cultures, antimicrobials, organ support", "5-15 min future feed"],
  ["Medication safety", "Orders, MAR, allergy, renal/weight context", "daily stewardship view"],
  ["Discharge and transfer", "Milestones, pharmacy, imaging, home supports", "hourly"],
  ["Equity and family", "Interpreter, geography, family readiness, PROs", "daily to weekly"],
];

const ambulatoryModules = [
  ["Access and referrals", "Referral demand, waitlists, templates", "hourly to daily"],
  ["No-show optimization", "Lead time, reminders, distance, weather", "daily"],
  ["Chronic disease and PROs", "PROMIS, labs, meds, utilization", "daily to weekly future feed"],
  ["Acute follow-up", "ED/inpatient discharge, callbacks, revisit risk", "1-4 h future feed"],
  ["Virtual and outreach", "Travel burden, virtual suitability, outreach slots", "daily to monthly"],
];

const governanceRows = [
  ["Alberta HIA", "Purpose limitation, minimization, role-based access, auditability"],
  ["TRIPOD+AI", "Prediction-model documentation, validation, intended use, limitations"],
  ["NIST AI RMF", "Map, measure, manage, and govern model risk through the lifecycle"],
  ["GMLP", "Human-AI performance, quality systems, transparency, monitoring"],
  ["FHIR/SMART/CDS Hooks", "Standards path for future EHR-embedded apps and workflow triggers"],
];

const metricDefinitions = [
  ["Effective beds", "Physical capacity after staffing, isolation, and step-down constraints"],
  ["Boarder hours", "Admitted ED patients awaiting inpatient placement times wait duration"],
  ["Third next available", "Access metric less sensitive to short-term cancellations than next open slot"],
  ["Breach risk", "Synthetic probability proxy that a cohort exceeds local target wait time"],
  ["Fairness drift", "Subgroup calibration, alert burden, and intervention-receipt monitoring"],
];

function sumRows(rows: Record<string, unknown>[], key: string) {
  return rows.reduce((total, row) => total + (Number(row[key]) || 0), 0);
}

function avgRows(rows: Record<string, unknown>[], key: string) {
  if (!rows.length) return 0;
  return sumRows(rows, key) / rows.length;
}

function App() {
  const [data, setData] = useState<DemoData>(fallbackDemoData as DemoData);
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]["id"]>("inpatient");
  const [site, setSite] = useState("All sites");
  const [persona, setPersona] = useState(personas[0]);
  const [surgeBeds, setSurgeBeds] = useState(6);
  const [clinicSessions, setClinicSessions] = useState(4);

  useEffect(() => {
    fetch("/demo-data.json")
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((payload: DemoData) => setData(payload))
      .catch(() => setData(fallbackDemoData as DemoData));
  }, []);

  const siteOptions = useMemo(() => {
    const ids = new Set<string>();
    data.siteSnapshots.forEach((row) => ids.add(String(row.site_id)));
    data.unitPressure.forEach((row) => ids.add(String(row.site_id)));
    return ["All sites", ...Array.from(ids)];
  }, [data]);

  const scopedForecast = data.inpatientForecast
    .filter((row) => site === "All sites" || String(row.site_id) === site)
    .slice(0, 5)
    .map((row) => ({
      label: `${String(row.prediction_horizon_hours)}h`,
      value: Number(row.prediction),
      lower: Number(row.p10),
      upper: Number(row.p90),
    }));

  const scopedUnits = data.unitPressure.filter((row) => site === "All sites" || String(row.site_id) === site);
  const adjustedBoarderDelta = Math.round(surgeBeds * -2.4);
  const adjustedBacklogDelta = Math.round(clinicSessions * -42);
  const syntheticWatch = sumRows(data.safetySignals, "deterioration_watch_count_synth");
  const sepsisSignals = sumRows(data.safetySignals, "sepsis_screen_signal_count_synth");
  const staffingStrain = avgRows(scopedUnits, "staffing_gap_pct");
  const urgentBreach = avgRows(data.ambulatoryAccess, "urgent_breach_risk");
  const noShowAvg = avgRows(data.clinicUtilization, "no_show_rate");
  const virtualShare = avgRows(data.clinicUtilization, "virtual_share");
  const qualityFailures = sumRows(data.quality, "failed_rows");

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <div className="brand-mark" aria-hidden="true">
            <HeartPulse size={28} />
          </div>
          <div>
            <p className="eyebrow">Pediatric Acute Care Intelligence Suite</p>
            <h1>Mission control for inpatient flow and ambulatory access</h1>
          </div>
        </div>
        <div className="status-stack">
          <span className="status-pill">Synthetic demonstration data</span>
          <span className="status-pill subtle">Not validated for clinical decision-making</span>
        </div>
      </header>

      <section className="control-band" aria-label="Dashboard controls">
        <label>
          Persona
          <select value={persona} onChange={(event) => setPersona(event.target.value)}>
            {personas.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </label>
        <label>
          Site
          <select value={site} onChange={(event) => setSite(event.target.value)}>
            {siteOptions.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </label>
        <label>
          Horizon
          <select defaultValue="72h">
            <option>72h</option>
            <option>14 days</option>
            <option>26 weeks</option>
          </select>
        </label>
        <div className="freshness">
          <DatabaseZap size={18} />
          <span>Generated {new Date(data.metadata.generatedAt).toLocaleString()}</span>
        </div>
      </section>

      <nav className="tab-strip" aria-label="Product areas">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              className={activeTab === tab.id ? "active" : ""}
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              title={tab.label}
            >
              <Icon size={18} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      {activeTab === "inpatient" && (
        <section className="dashboard-grid">
          <div className="panel wide intro-panel">
            <div>
              <p className="eyebrow">Executive Inpatient Mission Control</p>
              <h2>What is happening now, what comes next, and what is driving risk</h2>
            </div>
            <div className="persona-chip">
              <Stethoscope size={18} />
              {persona}
            </div>
          </div>
          <section className="kpi-grid wide">
            {data.inpatientKpis.map((kpi) => (
              <KpiTile key={kpi.label} {...kpi} />
            ))}
          </section>
          <section className="posture-grid wide" aria-label="Inpatient posture summary">
            <PostureCard
              icon={<BedDouble size={19} />}
              title="Hospital posture"
              value={`${data.inpatientKpis[0]?.value ?? 0}${data.inpatientKpis[0]?.unit ?? "%"}`}
              detail="Flow risk is driven by effective capacity, boarders, and discharge reliability."
            />
            <PostureCard
              icon={<Radio size={19} />}
              title="Safety posture"
              value={`${syntheticWatch} watch`}
              detail={`${sepsisSignals} synthetic sepsis-screen signals. Demonstration indicators only.`}
            />
            <PostureCard
              icon={<Users size={19} />}
              title="Equity and family posture"
              value={`${Math.round(staffingStrain * 100)}% strain`}
              detail="Future lens: interpreter demand, family readiness, geography, and travel burden."
            />
          </section>
          <section className="panel xlarge">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">6h to 72h forecast</p>
                <h3>Occupancy probability band</h3>
              </div>
              <Gauge size={22} />
            </div>
            <ForecastBand points={scopedForecast} />
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Unit pressure</p>
                <h3>Bed flow and census</h3>
              </div>
              <Activity size={22} />
            </div>
            <HeatGrid rows={scopedUnits} />
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Discharge system</p>
                <h3>Active barriers</h3>
              </div>
              <LineChart size={22} />
            </div>
            <BarList rows={data.dischargeBarriers} labelKey="barrier_type" valueKey="active_count" />
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Scenario option</p>
                <h3>Open surge beds</h3>
              </div>
              <SlidersHorizontal size={22} />
            </div>
            <label className="slider-label">
              Surge beds
              <input min="0" max="20" value={surgeBeds} type="range" onChange={(event) => setSurgeBeds(Number(event.target.value))} />
              <strong>{surgeBeds}</strong>
            </label>
            <div className="impact-callout">
              <strong>{adjustedBoarderDelta} projected boarder-hour delta</strong>
              <span>Estimate from transparent fallback simulation.</span>
            </div>
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">What would I do with this?</p>
                <h3>Operational options</h3>
              </div>
              <Network size={22} />
            </div>
            <OptionList rows={data.inpatientOptions} />
          </section>
          <section className="panel wide">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Role-based module stack</p>
                <h3>Command centre, unit awareness, and future in-EHR worklists</h3>
              </div>
              <GitBranch size={22} />
            </div>
            <ModuleMap rows={inpatientModules} />
          </section>
        </section>
      )}

      {activeTab === "ambulatory" && (
        <section className="dashboard-grid">
          <div className="panel wide intro-panel">
            <div>
              <p className="eyebrow">Executive Ambulatory Access Mission Control</p>
              <h2>Referral pressure, waitlist aging, capacity, and access reliability</h2>
            </div>
            <div className="persona-chip">
              <CalendarClock size={18} />
              {persona}
            </div>
          </div>
          <section className="kpi-grid wide">
            {data.ambulatoryKpis.map((kpi) => (
              <KpiTile key={kpi.label} {...kpi} />
            ))}
          </section>
          <section className="posture-grid wide" aria-label="Ambulatory posture summary">
            <PostureCard
              icon={<CalendarClock size={19} />}
              title="Access posture"
              value={`${Math.round(urgentBreach * 100)}%`}
              detail="Mean urgent breach-risk proxy across visible programs."
            />
            <PostureCard
              icon={<TimerReset size={19} />}
              title="Reliability posture"
              value={`${(noShowAvg * 100).toFixed(1)}%`}
              detail="Synthetic no-show and late-cancel risk informs guarded overbooking."
            />
            <PostureCard
              icon={<MapPin size={19} />}
              title="Virtual and travel posture"
              value={`${(virtualShare * 100).toFixed(1)}%`}
              detail="Virtual-care share is a proxy lens for geography and family burden."
            />
          </section>
          <section className="panel xlarge">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Waitlist and access</p>
                <h3>Backlog by program</h3>
              </div>
              <LineChart size={22} />
            </div>
            <BarList rows={data.ambulatoryAccess} labelKey="program" valueKey="waitlist_total" maxRows={10} />
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Clinic template</p>
                <h3>Slot utilization</h3>
              </div>
              <Gauge size={22} />
            </div>
            <BarList rows={data.clinicUtilization} labelKey="program" valueKey="completed_visits" maxRows={8} />
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">No-show and late cancel</p>
                <h3>Risk lens</h3>
              </div>
              <Activity size={22} />
            </div>
            <div className="driver-list">
              {data.clinicUtilization.slice(0, 6).map((row) => (
                <div key={String(row.program)} className="driver-row">
                  <span>{String(row.program).replaceAll("_", " ")}</span>
                  <strong>{(Number(row.no_show_rate) * 100).toFixed(1)}%</strong>
                </div>
              ))}
            </div>
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Scenario option</p>
                <h3>Add clinic sessions</h3>
              </div>
              <SlidersHorizontal size={22} />
            </div>
            <label className="slider-label">
              Sessions/week
              <input min="0" max="12" value={clinicSessions} type="range" onChange={(event) => setClinicSessions(Number(event.target.value))} />
              <strong>{clinicSessions}</strong>
            </label>
            <div className="impact-callout amber">
              <strong>{adjustedBacklogDelta} projected backlog delta</strong>
              <span>Estimate from weekly access simulation.</span>
            </div>
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">What would I do with this?</p>
                <h3>Access options</h3>
              </div>
              <Network size={22} />
            </div>
            <OptionList rows={data.ambulatoryOptions} />
          </section>
          <section className="panel wide">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Role-based module stack</p>
                <h3>Access hub, clinic operations, and outreach intelligence</h3>
              </div>
              <GitBranch size={22} />
            </div>
            <ModuleMap rows={ambulatoryModules} />
          </section>
        </section>
      )}

      {activeTab === "simulation" && (
        <section className="dashboard-grid">
          <div className="panel wide intro-panel">
            <div>
              <p className="eyebrow">Scenario Simulation Lab</p>
              <h2>Monte Carlo outputs with confidence bands and explicit caveats</h2>
            </div>
            <div className="persona-chip">
              <SlidersHorizontal size={18} />
              Synthetic scenarios
            </div>
          </div>
          <section className="panel xlarge">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Inpatient</p>
                <h3>Boarder hours by scenario</h3>
              </div>
              <BedDouble size={22} />
            </div>
            <BarList rows={data.simulationInpatient} labelKey="scenario_name" valueKey="boarder_hours_mean" maxRows={8} />
          </section>
          <section className="panel xlarge">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Ambulatory</p>
                <h3>Final backlog by scenario</h3>
              </div>
              <CalendarClock size={22} />
            </div>
            <BarList rows={data.simulationAmbulatory} labelKey="scenario_name" valueKey="final_backlog" maxRows={8} />
          </section>
        </section>
      )}

      {activeTab === "methods" && (
        <section className="dashboard-grid">
          <div className="panel wide intro-panel">
            <div>
              <p className="eyebrow">Model Registry and Methods Explorer</p>
              <h2>Every output carries model identity, horizon, uncertainty, and caveats</h2>
            </div>
            <div className="persona-chip">
              <FlaskConical size={18} />
              Transparent methods
            </div>
          </div>
          {data.modelCards.map((card) => (
            <section className="panel model-card" key={String(card.model_id)}>
              <p className="eyebrow">{String(card.model_id)}</p>
              <h3>{String(card.model_name)}</h3>
              <dl>
                <div>
                  <dt>Version</dt>
                  <dd>{String(card.version)}</dd>
                </div>
                <div>
                  <dt>Horizon</dt>
                  <dd>{String(card.prediction_horizon)}</dd>
                </div>
                <div>
                  <dt>Status</dt>
                  <dd>{String(card.validation_status)}</dd>
                </div>
              </dl>
              <p className="caveat">{String(card.caveat)}</p>
            </section>
          ))}
          <section className="panel wide">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Metric definitions</p>
                <h3>Definition-rich displays reduce dashboard ambiguity</h3>
              </div>
              <ClipboardCheck size={22} />
            </div>
            <DefinitionGrid rows={metricDefinitions} />
          </section>
        </section>
      )}

      {activeTab === "quality" && (
        <section className="dashboard-grid">
          <div className="panel wide intro-panel">
            <div>
              <p className="eyebrow">Data Quality and Safety Explorer</p>
              <h2>Privacy checks, schema checks, freshness, and table-level quality status</h2>
            </div>
            <div className="persona-chip">
              <ShieldCheck size={18} />
              No identifiers
            </div>
          </div>
          <section className="panel xlarge">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Quality checks</p>
                <h3>Latest synthetic validation run</h3>
              </div>
              <ShieldCheck size={22} />
            </div>
            <div className="quality-table" role="table" aria-label="Data quality checks">
              {data.quality.slice(0, 14).map((row, idx) => (
                <div className="quality-row" role="row" key={`${String(row.table_name)}-${idx}`}>
                  <span>{String(row.table_name)}</span>
                  <strong>{String(row.check)}</strong>
                  <em data-pass={Boolean(row.passed)}>{Boolean(row.passed) ? "pass" : "review"}</em>
                </div>
              ))}
            </div>
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Audit posture</p>
                <h3>Current validation summary</h3>
              </div>
              <ShieldCheck size={22} />
            </div>
            <div className="impact-callout">
              <strong>{qualityFailures} failed rows in generated checks</strong>
              <span>Checks include uniqueness, non-negative values, bounds, and direct-identifier scans.</span>
            </div>
          </section>
        </section>
      )}

      {activeTab === "governance" && (
        <section className="dashboard-grid">
          <div className="panel wide intro-panel">
            <div>
              <p className="eyebrow">Governance, standards, and future production path</p>
              <h2>AI and operations governance is treated as part of the product surface</h2>
            </div>
            <div className="persona-chip">
              <FileText size={18} />
              Audit-ready prototype
            </div>
          </div>
          <section className="panel xlarge">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Lifecycle controls</p>
                <h3>Minimum governance rail for future real-data implementation</h3>
              </div>
              <ShieldCheck size={22} />
            </div>
            <DefinitionGrid rows={governanceRows} />
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Integration path</p>
                <h3>Curated views before apps</h3>
              </div>
              <DatabaseZap size={22} />
            </div>
            <div className="option-list">
              <article className="option-row">
                <strong>Event-driven future state</strong>
                <span>FHIR, SMART, CDS Hooks, DICOM, ADT, staffing, scheduling, and open context feeds.</span>
                <em>Current prototype remains static synthetic data.</em>
              </article>
              <article className="option-row">
                <strong>Latency tiers</strong>
                <span>Streaming, near-real-time, intra-day, and daily public context refreshes.</span>
                <em>Every model output shows freshness and caveat.</em>
              </article>
              <article className="option-row">
                <strong>Fairness and calibration</strong>
                <span>Subgroup calibration, alert burden, false-negative review, and intervention receipt.</span>
                <em>No patient-level real data is included.</em>
              </article>
            </div>
          </section>
        </section>
      )}

      <footer>
        Synthetic demonstration data. Not connected to real hospital systems. Not validated for clinical decision-making.
      </footer>
    </main>
  );
}

function OptionList({ rows }: { rows: { option: string; expected_effect: string; watch: string }[] }) {
  return (
    <div className="option-list">
      {rows.slice(0, 4).map((row) => (
        <article className="option-row" key={row.option}>
          <strong>{row.option}</strong>
          <span>{row.expected_effect}</span>
          <em>{row.watch}</em>
        </article>
      ))}
    </div>
  );
}

function PostureCard({
  icon,
  title,
  value,
  detail,
}: {
  icon: ReactNode;
  title: string;
  value: string;
  detail: string;
}) {
  return (
    <article className="posture-card">
      <span className="posture-icon">{icon}</span>
      <div>
        <p>{title}</p>
        <strong>{value}</strong>
        <em>{detail}</em>
      </div>
    </article>
  );
}

function ModuleMap({ rows }: { rows: string[][] }) {
  return (
    <div className="module-map">
      {rows.map(([name, inputs, cadence]) => (
        <article className="module-row" key={name}>
          <strong>{name}</strong>
          <span>{inputs}</span>
          <em>{cadence}</em>
        </article>
      ))}
    </div>
  );
}

function DefinitionGrid({ rows }: { rows: string[][] }) {
  return (
    <div className="definition-grid">
      {rows.map(([term, definition]) => (
        <article key={term}>
          <strong>{term}</strong>
          <span>{definition}</span>
        </article>
      ))}
    </div>
  );
}

export default App;
