import { useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  DatabaseZap,
  FileCheck2,
  Flag,
  GitBranch,
  History,
  Layers3,
  ListChecks,
  Network,
  Plus,
  ShieldCheck,
  Sparkles,
  Workflow,
} from "lucide-react";
import { KpiTile } from "../components/KpiTile";
import { InsightPanel, Panel, PostureCard } from "../components/Panel";
import { ForecastRibbonChart, HorizontalBarChart, ScenarioFrontier, UnitPressureHeatmap } from "../components/ProductCharts";
import type { AppContext, DataRow, V3Data } from "../data/types";
import { avgRows, formatInteger, formatPct, numberValue, siteLabel, stringValue, sumRows, titleCase } from "../lib/format";
import type { PageId } from "../components/AppShell";

type Tone = "neutral" | "watch" | "high" | "good";

function kpiTone(value: unknown): Tone {
  const tone = String(value ?? "neutral");
  if (tone === "watch" || tone === "high" || tone === "good") return tone;
  return "neutral";
}

function postureTone(value: unknown): "steady" | "watch" | "high" {
  const tone = String(value ?? "steady");
  if (tone === "watch" || tone === "high") return tone;
  return "steady";
}

function statusTone(value: unknown): string {
  const status = String(value ?? "").toLowerCase();
  if (status.includes("ready") || status.includes("approved") || status.includes("pass")) return "ready";
  if (status.includes("hold") || status.includes("blocked") || status.includes("high")) return "high";
  if (status.includes("review") || status.includes("watch") || status.includes("open")) return "review";
  return "neutral";
}

function ClassificationBadge({ value }: { value: unknown }) {
  const label = titleCase(value || "derived");
  return <span className={`mini-badge ${statusTone(value)}`}>{label}</span>;
}

function ReadinessBadge({ value }: { value: unknown }) {
  const label = titleCase(value || "ready");
  return <span className={`mini-badge ${statusTone(value)}`}>{label}</span>;
}

function LineageCard({ data, panelId }: { data: V3Data; panelId: string }) {
  const lineage = data.panelLineage.find((row) => stringValue(row, "panel_id") === panelId) ?? data.panelLineage[0];
  if (!lineage) return null;
  return (
    <article className="lineage-card">
      <div>
        <p className="eyebrow">Lineage and readiness</p>
        <strong>{stringValue(lineage, "title")}</strong>
      </div>
      <div className="lineage-badges">
        <ClassificationBadge value={lineage.classification} />
        <ReadinessBadge value={lineage.readiness_status} />
        <span className="mini-badge neutral">{stringValue(lineage, "freshness")}</span>
        <span className="mini-badge neutral">{titleCase(stringValue(lineage, "confidence", "confidence pending"))}</span>
      </div>
      <p>{stringValue(lineage, "lineage_summary")}</p>
      <em>{stringValue(lineage, "caveat")}</em>
    </article>
  );
}

function SourceReadinessTable({ rows, limit = 8 }: { rows: DataRow[]; limit?: number }) {
  return (
    <div className="data-table-wrap">
      <table className="compact-table">
        <thead>
          <tr>
            <th>Source</th>
            <th>Readiness</th>
            <th>Freshness</th>
            <th>Metric approval</th>
            <th>Small cells</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, limit).map((row) => (
            <tr key={stringValue(row, "source_id")}>
              <td>{stringValue(row, "source_id")}</td>
              <td>
                <ReadinessBadge value={row.overall_readiness} />
              </td>
              <td>{stringValue(row, "freshness")}</td>
              <td>{stringValue(row, "metric_definition_approved")}</td>
              <td>{stringValue(row, "small_cell_suppression")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function WarningList({ rows }: { rows: DataRow[] }) {
  if (!rows.length) return <p className="muted">No active synthetic warnings in this lens.</p>;
  return (
    <div className="stack-list">
      {rows.map((row) => (
        <article className="warning-card" key={stringValue(row, "warning_id", stringValue(row, "signal_id"))}>
          <div>
            <AlertTriangle size={18} />
            <strong>{stringValue(row, "asset_id")}</strong>
          </div>
          <p>{stringValue(row, "message", `${titleCase(stringValue(row, "unit_or_program"))} score ${numberValue(row, "score").toFixed(2)}`)}</p>
          <div className="lineage-badges">
            <ReadinessBadge value={row.severity} />
            <ReadinessBadge value={row.status ?? row.readiness} />
            <ClassificationBadge value={row.classification ?? "modelled"} />
          </div>
        </article>
      ))}
    </div>
  );
}

function RegistryTable({ rows, columns, limit = 10 }: { rows: DataRow[]; columns: string[]; limit?: number }) {
  return (
    <div className="data-table-wrap">
      <table className="compact-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{titleCase(column)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, limit).map((row, index) => (
            <tr key={`${stringValue(row, columns[0])}-${index}`}>
              {columns.map((column) => (
                <td key={column}>{stringValue(row, column)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ModelCardGrid({ rows, limit = 15 }: { rows: DataRow[]; limit?: number }) {
  return (
    <div className="model-card-grid">
      {rows.slice(0, limit).map((row) => (
        <article className="model-card" key={stringValue(row, "asset_id")}>
          <div className="model-card-top">
            <BrainCircuit size={18} />
            <ReadinessBadge value={row.governance_status} />
          </div>
          <strong>{stringValue(row, "asset_id")}</strong>
          <p>{stringValue(row, "name")}</p>
          <dl>
            <div>
              <dt>Domain</dt>
              <dd>{stringValue(row, "domain")}</dd>
            </div>
            <div>
              <dt>Output</dt>
              <dd>{stringValue(row, "output_type")}</dd>
            </div>
            <div>
              <dt>Cadence</dt>
              <dd>{stringValue(row, "cadence")}</dd>
            </div>
            <div>
              <dt>Fallback</dt>
              <dd>{stringValue(row, "fallback", "Hide modelled layer and revert to direct metrics.")}</dd>
            </div>
          </dl>
          <em>{stringValue(row, "caveats", stringValue(row, "warnings"))}</em>
        </article>
      ))}
    </div>
  );
}

function MemoryEventLog({ events }: { events: DataRow[] }) {
  return (
    <div className="event-log">
      {events.map((event) => (
        <article key={stringValue(event, "event_id")}>
          <div>
            <strong>{titleCase(stringValue(event, "event_type"))}</strong>
            <ReadinessBadge value={event.status} />
          </div>
          <p>{stringValue(event, "note")}</p>
          <span>
            {stringValue(event, "writeback_table")} | {stringValue(event, "created_by")} | {stringValue(event, "created_at")}
          </span>
        </article>
      ))}
    </div>
  );
}

type ReadinessCounts = { ready: number; review: number; high: number };

function readinessCounts(rows: DataRow[]): ReadinessCounts {
  return rows.reduce<ReadinessCounts>(
    (counts, row) => {
      const status = statusTone(row.overall_readiness ?? row.readiness_status ?? row.governance_status);
      if (status === "ready") counts.ready += 1;
      else if (status === "high") counts.high += 1;
      else counts.review += 1;
      return counts;
    },
    { ready: 0, review: 0, high: 0 },
  );
}

export function SystemPosturePage({
  data,
  context,
  goTo,
}: {
  data: V3Data;
  context: AppContext;
  goTo: (page: PageId) => void;
}) {
  const counts = readinessCounts(data.directLinkValidation);
  return (
    <section className="dashboard-grid">
      <section className="hero-surface wide frontier-hero">
        <div>
          <p className="eyebrow">v3 operating layer</p>
          <h2>Today’s Pediatric System Posture</h2>
          <p>
            A synthetic provincial command surface that separates direct operational signals, derived operational intelligence,
            and governed modelled assets. Every major panel carries freshness, confidence, caveats, and a lineage path.
          </p>
          <div className="hero-actions">
            <button onClick={() => goTo("gatekeeper")}>
              <ShieldCheck size={18} />
              Gatekeeper control plane
            </button>
            <button onClick={() => goTo("scenarios")}>
              <Sparkles size={18} />
              Scenario comparison
            </button>
            <button onClick={() => goTo("memory")}>
              <History size={18} />
              Learning memory
            </button>
          </div>
        </div>
        <div className="operating-layer-map" aria-label="Direct derived modelled operating layer map">
          {["Direct signals", "Derived metrics", "Modelled assets", "Gatekeeper", "Learning memory"].map((label, index) => (
            <span key={label} style={{ ["--i" as string]: index }}>
              {label}
            </span>
          ))}
        </div>
      </section>

      <section className="kpi-grid wide">
        {data.systemPosture.kpis.map((row) => (
          <KpiTile
            key={stringValue(row, "label")}
            label={stringValue(row, "label")}
            value={stringValue(row, "value")}
            detail={stringValue(row, "detail")}
            delta={stringValue(row, "delta")}
            tone={kpiTone(row.tone)}
          />
        ))}
      </section>

      <section className="posture-grid wide">
        {data.systemPosture.postureCards.map((row) => (
          <PostureCard
            key={stringValue(row, "label")}
            label={stringValue(row, "label")}
            value={stringValue(row, "value")}
            detail={stringValue(row, "detail")}
            tone={postureTone(row.tone)}
            icon={statusTone(row.tone) === "review" ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}
          />
        ))}
      </section>

      <Panel span="xlarge" eyebrow="Command summary" title="Why this changed" icon={<Activity size={22} />}>
        <div className="driver-stack">
          {data.systemPosture.whyChanged.map((row) => (
            <article key={stringValue(row, "driver")}>
              <div>
                <strong>{stringValue(row, "driver")}</strong>
                <span>{stringValue(row, "change")}</span>
              </div>
              <progress max={100} value={numberValue(row, "contribution")} />
              <p>{stringValue(row, "evidence")}</p>
            </article>
          ))}
        </div>
      </Panel>

      <Panel span="normal" eyebrow="Current lens" title={context.persona} icon={<ListChecks size={22} />}>
        <InsightPanel
          title={`${siteLabel(context.site)} | ${context.horizon}`}
          body="Huddle mode keeps the executive view short: what changed, which sources are ready, which outputs are modelled, and which decisions need a human review."
          actions={["Review high-severity warnings.", "Open Gatekeeper before trusting new derived or modelled outputs.", "Capture scenario notes in the learning memory."]}
          caveat={data.metadata.clinicalUse}
        />
      </Panel>

      <Panel span="xlarge" eyebrow="Readiness overlay" title={`${counts.ready} ready, ${counts.review} review, ${counts.high} blocked`} icon={<DatabaseZap size={22} />}>
        <SourceReadinessTable rows={data.directLinkValidation} />
      </Panel>

      <Panel span="normal" eyebrow="Panel lineage" title="This page is derived, not a direct chart" icon={<Layers3 size={22} />}>
        <LineageCard data={data} panelId="PANEL_SYSTEM_POSTURE" />
      </Panel>
    </section>
  );
}

export function FrontierInpatientPage({ data }: { data: V3Data; context: AppContext }) {
  const censusProxy = Math.round(sumRows(data.inpatient.unitPressure, "occupancy_pct") * 42);
  const boarders = sumRows(data.inpatient.unitPressure, "ed_boarders");
  const staffingGap = avgRows(data.inpatient.unitPressure, "staffing_gap_pct");
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Inpatient Intelligence" title="Huddle view with source-readiness and model warnings" icon={<Activity size={22} />}>
        <LineageCard data={data} panelId="PANEL_INPATIENT_COMMAND" />
      </Panel>
      <section className="kpi-grid wide">
        <KpiTile label="Occupancy proxy" value={formatInteger(censusProxy)} detail="Synthetic weighted census pressure" delta="+2.8 pts" tone="watch" />
        <KpiTile label="ED boarders" value={formatInteger(boarders)} detail="Across selected synthetic units" delta="+21" tone="high" />
        <KpiTile label="Staffing gap" value={formatPct(staffingGap)} detail="Mean unit-shift gap" delta="+1.9 pts" tone="watch" />
        <KpiTile label="Source reviews" value={formatInteger(data.inpatient.unitPressure.filter((row) => stringValue(row, "source_readiness") !== "ready").length)} detail="Panel rows requiring owner review" delta="review" tone="watch" />
      </section>
      <Panel span="xlarge" eyebrow="Unit drilldown" title="Occupancy, staffing gap, and ED boarding" icon={<GitBranch size={22} />}>
        <UnitPressureHeatmap rows={data.inpatient.unitPressure} />
      </Panel>
      <Panel span="normal" eyebrow="Warning logic" title="Governed warning queue" icon={<AlertTriangle size={22} />}>
        <WarningList rows={data.inpatient.warnings} />
      </Panel>
      <Panel span="xlarge" eyebrow="Forecast ribbon" title="Occupancy forecast carries model-card caveats" icon={<BrainCircuit size={22} />}>
        <ForecastRibbonChart rows={data.inpatient.forecast} xKey="horizon_hours" predictionKey="occupancy_forecast" lowerKey="p10" upperKey="p90" label="Inpatient occupancy forecast" />
      </Panel>
      <Panel span="normal" eyebrow="Why bed pressure moved" title="Discharge and step-down drivers" icon={<FileCheck2 size={22} />}>
        <HorizontalBarChart rows={data.inpatient.flowDrivers} labelKey="driver" valueKey="active_count" label="Discharge and step-down drivers" height={280} />
      </Panel>
    </section>
  );
}

export function FrontierAmbulatoryPage({ data }: { data: V3Data; context: AppContext }) {
  const waitlist = sumRows(data.ambulatory.programAccess, "waitlist_total");
  const tna = avgRows(data.ambulatory.programAccess, "third_next_available_days");
  const breach = avgRows(data.ambulatory.programAccess, "urgent_breach_risk");
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Ambulatory Access Intelligence" title="Backlog, template capacity, no-show guardrails, and diagnostic readiness" icon={<Workflow size={22} />}>
        <LineageCard data={data} panelId="PANEL_AMBULATORY_COMMAND" />
      </Panel>
      <section className="kpi-grid wide">
        <KpiTile label="Waitlist" value={formatInteger(waitlist)} detail="Synthetic aggregate referral backlog" delta="+4.6%" tone="watch" />
        <KpiTile label="Third next available" value={`${Math.round(tna)} days`} detail="Mean by program" delta="+3" tone="watch" />
        <KpiTile label="Urgent breach risk" value={formatPct(breach)} detail="Synthetic program-week probability" delta="+4 pts" tone="high" />
        <KpiTile label="Diagnostic readiness" value={formatPct(avgRows(data.ambulatory.programAccess, "diagnostic_readiness"))} detail="Dependency completion proxy" delta="-6 pts" tone="watch" />
      </section>
      <Panel span="xlarge" eyebrow="Access drilldown" title="Waitlist and urgent breach risk by program" icon={<Activity size={22} />}>
        <HorizontalBarChart rows={data.ambulatory.programAccess} labelKey="program" valueKey="waitlist_total" label="Ambulatory waitlist by program" />
      </Panel>
      <Panel span="normal" eyebrow="No-show frontier" title="Guardrailed capacity recovery" icon={<Flag size={22} />}>
        <RegistryTable rows={data.ambulatory.noShowFrontier} columns={["program", "guarded_overbook_pct", "expected_recovered_slots", "equity_guardrail", "no_show_risk"]} limit={8} />
      </Panel>
      <Panel span="xlarge" eyebrow="Backlog forecast" title="Scenario planning forecast, not a scheduling directive" icon={<BrainCircuit size={22} />}>
        <ForecastRibbonChart rows={data.ambulatory.forecast} xKey="horizon_weeks" predictionKey="backlog_forecast" lowerKey="p10" upperKey="p90" label="Ambulatory backlog forecast" />
      </Panel>
      <Panel span="normal" eyebrow="Warning logic" title="Program huddle queue" icon={<AlertTriangle size={22} />}>
        <WarningList rows={data.ambulatory.warnings} />
      </Panel>
    </section>
  );
}

export function PredictiveAssetsPage({ data }: { data: V3Data }) {
  const signalRows = data.predictiveAssets.signals;
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Clinical Surveillance / Predictive Asset Layer" title="Modelled outputs remain governed, labelled, and reversible" icon={<BrainCircuit size={22} />}>
        <LineageCard data={data} panelId="PANEL_PREDICTIVE_ASSETS" />
      </Panel>
      <Panel span="xlarge" eyebrow="Model-card drilldown" title="15 governed synthetic assets" icon={<ShieldCheck size={22} />}>
        <ModelCardGrid rows={data.modelRegistry} />
      </Panel>
      <Panel span="normal" eyebrow="Warning overlay" title="Synthetic surveillance signals" icon={<AlertTriangle size={22} />}>
        <WarningList rows={signalRows} />
      </Panel>
      <Panel span="xlarge" eyebrow="Evidence overlay" title="Trace warnings to review evidence and caveats" icon={<GitBranch size={22} />}>
        <RegistryTable rows={data.predictiveAssets.evidenceTrails} columns={["trail_id", "asset_id", "evidence_step", "detail"]} limit={8} />
      </Panel>
      <Panel span="normal" eyebrow="Safety boundary" title="No clinical decisioning" icon={<FileCheck2 size={22} />}>
        <InsightPanel
          title="Displayed as synthetic-only"
          body="Clinical surveillance assets are shown to demonstrate governance and warning controls. They are not validated for diagnosis, triage, treatment, or patient-level action."
          actions={["Require threshold review.", "Suppress small cells.", "Retain rollback path and evidence trail."]}
        />
      </Panel>
    </section>
  );
}

export function ScenarioLabPage({
  data,
  addMemoryEvent,
}: {
  data: V3Data;
  addMemoryEvent: (event: DataRow) => void;
}) {
  const [selectedScenario, setSelectedScenario] = useState("SCN-INPT-001");
  const selected = data.scenarioLab.scenarios.find((row) => stringValue(row, "scenario_id") === selectedScenario) ?? data.scenarioLab.scenarios[0];
  function storeScenarioRun() {
    addMemoryEvent({
      event_id: `EVT-LOCAL-${Date.now()}`,
      event_type: "scenario_run",
      created_at: new Date().toISOString(),
      created_by: "showcase_local_user",
      app_area: "Scenario Simulation Lab",
      site_id: "SITE_PROV_NETWORK",
      unit_or_program: stringValue(selected, "domain", "network"),
      related_ids: stringValue(selected, "scenario_id"),
      status: "captured locally",
      severity: "low",
      note: `${stringValue(selected, "scenario_name")} captured in local showcase memory.`,
      payload_json: JSON.stringify({ synthetic_demo: true, showcase_local: true }),
      synthetic_demo_flag: true,
      writeback_table: "APP.SCENARIO_RUN_LOG",
    });
  }
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Scenario Simulation Lab" title="Compare operational options and capture learning-system memory" icon={<Sparkles size={22} />}>
        <LineageCard data={data} panelId="PANEL_SCENARIO_LAB" />
      </Panel>
      <Panel span="xlarge" eyebrow="Scenario comparison mode" title="Impact versus effort and risk" icon={<GitBranch size={22} />}>
        <ScenarioFrontier rows={data.scenarioLab.scenarios} outcomeKey="outcome_value" label="Scenario frontier" />
      </Panel>
      <Panel span="normal" eyebrow="Writeback rehearsal" title="Scenario run log" icon={<Plus size={22} />}>
        <label className="field-stack">
          Scenario
          <select value={selectedScenario} onChange={(event) => setSelectedScenario(event.target.value)}>
            {data.scenarioLab.scenarios.map((row) => (
              <option key={stringValue(row, "scenario_id")} value={stringValue(row, "scenario_id")}>
                {stringValue(row, "scenario_name")}
              </option>
            ))}
          </select>
        </label>
        <button className="primary-action" onClick={storeScenarioRun}>
          <Plus size={18} />
          Capture synthetic run
        </button>
        <p className="muted">Showcase stores locally; Snowflake path writes to APP.SCENARIO_RUN_LOG.</p>
      </Panel>
      <Panel span="xlarge" eyebrow="Comparison register" title="Candidate bundles for huddle review" icon={<ListChecks size={22} />}>
        <RegistryTable rows={data.scenarioLab.comparisons} columns={["comparison_id", "name", "baseline", "scenario", "decision"]} limit={6} />
      </Panel>
      <Panel span="normal" eyebrow="Scenario table" title="Readiness and classification" icon={<FileCheck2 size={22} />}>
        <RegistryTable rows={data.scenarioLab.scenarios} columns={["scenario_id", "domain", "scenario_name", "readiness", "classification", "writeback_table"]} limit={8} />
      </Panel>
    </section>
  );
}

export function GatekeeperControlPlanePage({ data }: { data: V3Data }) {
  const [mode, setMode] = useState<"lite" | "deep">("lite");
  const controlRows = useMemo(() => {
    if (mode === "lite") return data.gatekeeper.controlPlane.filter((row) => stringValue(row, "mode").includes("executive"));
    return data.gatekeeper.controlPlane;
  }, [data.gatekeeper.controlPlane, mode]);
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="AHA Gatekeeper Control Plane" title="Govern direct linkages, calculated metrics, model assets, warnings, scenarios, and release decisions" icon={<ShieldCheck size={22} />}>
        <div className="segmented-control" role="group" aria-label="Gatekeeper mode">
          <button className={mode === "lite" ? "active" : ""} onClick={() => setMode("lite")}>
            Executive lite
          </button>
          <button className={mode === "deep" ? "active" : ""} onClick={() => setMode("deep")}>
            Technical deep
          </button>
        </div>
        <LineageCard data={data} panelId="PANEL_GATEKEEPER" />
      </Panel>
      <Panel span="xlarge" eyebrow="Stoplight control" title="Registry health by governed area" icon={<DatabaseZap size={22} />}>
        <div className="control-plane-grid">
          {controlRows.map((row) => (
            <article key={stringValue(row, "area")}>
              <strong>{stringValue(row, "area")}</strong>
              <div className="stoplight-row">
                <span className="ready">{numberValue(row, "ready")} ready</span>
                <span className="review">{numberValue(row, "review")} review</span>
                <span className="high">{numberValue(row, "blocked")} blocked</span>
              </div>
              <small>{stringValue(row, "mode")}</small>
            </article>
          ))}
        </div>
      </Panel>
      <Panel span="normal" eyebrow="Issue queue" title="Approvals, holds, and review notes" icon={<AlertTriangle size={22} />}>
        <RegistryTable rows={data.gatekeeper.issues} columns={["issue_id", "severity", "related_id", "status", "note"]} limit={6} />
      </Panel>
      <Panel span="xlarge" eyebrow="Dependency graph" title="Sources and assets feeding public panels" icon={<Network size={22} />}>
        <div className="dependency-graph">
          {data.gatekeeper.dependencyEdges.slice(0, 18).map((edge, index) => (
            <span key={`${stringValue(edge, "from")}-${index}`}>
              {stringValue(edge, "from")} {"->"} {stringValue(edge, "to")}
            </span>
          ))}
        </div>
      </Panel>
      <Panel span="normal" eyebrow="Decision ledger" title="Recent governance decisions" icon={<CheckCircle2 size={22} />}>
        <RegistryTable rows={data.gatekeeper.approvals} columns={["decision_id", "related_id", "decision", "reviewer_role"]} limit={5} />
      </Panel>
    </section>
  );
}

export function LearningMemoryPage({
  data,
  events,
  addMemoryEvent,
}: {
  data: V3Data;
  events: DataRow[];
  addMemoryEvent: (event: DataRow) => void;
}) {
  function addAcknowledgement() {
    addMemoryEvent({
      event_id: `EVT-LOCAL-${Date.now()}`,
      event_type: "warning_acknowledgement",
      created_at: new Date().toISOString(),
      created_by: "showcase_local_user",
      app_area: "Learning System Memory",
      site_id: "SITE_PROV_NETWORK",
      unit_or_program: "Network",
      related_ids: "WARN-INPT-001",
      status: "acknowledged locally",
      severity: "medium",
      note: "Synthetic acknowledgement captured from the public showcase.",
      payload_json: JSON.stringify({ synthetic_demo: true, showcase_local: true }),
      synthetic_demo_flag: true,
      writeback_table: "APP.WARNING_ACKNOWLEDGEMENT",
    });
  }
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Learning System Memory" title="Snowflake writeback tables turn the product into a governed learning loop" icon={<History size={22} />}>
        <LineageCard data={data} panelId="PANEL_MEMORY" />
      </Panel>
      <Panel span="normal" eyebrow="Local showcase action" title="Capture an acknowledgement" icon={<Plus size={22} />}>
        <button className="primary-action" onClick={addAcknowledgement}>
          <Plus size={18} />
          Add synthetic acknowledgement
        </button>
        <p className="muted">The deployed showcase stores this only in browser state; the Streamlit/Snowflake pattern writes to APP tables.</p>
      </Panel>
      <Panel span="xlarge" eyebrow="Event log" title="Scenario runs, notes, warnings, issues, reviews, and decisions" icon={<ListChecks size={22} />}>
        <MemoryEventLog events={events} />
      </Panel>
      <Panel span="wide" eyebrow="Writeback contract" title="Required APP and GOVERNANCE tables" icon={<DatabaseZap size={22} />}>
        <RegistryTable rows={data.learningMemory.writebackTables} columns={["table_name", "required", "status"]} limit={12} />
      </Panel>
    </section>
  );
}

export function FutureWiringPage({ data }: { data: V3Data }) {
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Future Real-Data Wiring" title="A governed read-only augmentation layer for Connect Care-era operations" icon={<Network size={22} />}>
        <LineageCard data={data} panelId="PANEL_WIRING" />
      </Panel>
      <Panel span="xlarge" eyebrow="Implementation phases" title="Curated views before apps; governance before warnings" icon={<Workflow size={22} />}>
        <div className="phase-grid">
          {data.futureWiring.phases.map((row) => (
            <article key={stringValue(row, "phase")}>
              <strong>{stringValue(row, "phase")}</strong>
              <p>{stringValue(row, "scope")}</p>
              <em>{stringValue(row, "governance_gate")}</em>
            </article>
          ))}
        </div>
      </Panel>
      <Panel span="normal" eyebrow="Direct-link stoplight" title="Source validation checks" icon={<FileCheck2 size={22} />}>
        <SourceReadinessTable rows={data.directLinkValidation} limit={6} />
      </Panel>
      <Panel span="wide" eyebrow="Curated-view registry" title="Connect Care-realistic synthetic wiring placeholders" icon={<DatabaseZap size={22} />}>
        <RegistryTable rows={data.sourceRegistry} columns={["source_id", "curated_view", "grain", "cadence", "classification", "future_mapping_placeholder"]} limit={24} />
      </Panel>
    </section>
  );
}
