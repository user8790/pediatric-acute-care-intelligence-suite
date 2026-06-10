import {
  Activity,
  BedDouble,
  CalendarClock,
  DatabaseZap,
  FlaskConical,
  Gauge,
  HeartPulse,
  LineChart,
  Network,
  ShieldCheck,
  SlidersHorizontal,
  Stethoscope,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
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
] as const;

const personas = [
  "Executive",
  "Site operations",
  "Patient flow",
  "Unit manager",
  "Ambulatory program",
  "Analytics",
];

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

export default App;
