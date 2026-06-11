import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  DatabaseZap,
  DollarSign,
  FileCheck2,
  Flag,
  Gauge,
  GitBranch,
  History,
  Layers3,
  ListChecks,
  Network,
  Plus,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Users,
  Workflow,
  X,
} from "lucide-react";
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

function csvIds(value: unknown): string[] {
  return String(value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function sourceReadiness(data: V3Data, sourceId: string): DataRow | undefined {
  return data.directLinkValidation.find((row) => stringValue(row, "source_id") === sourceId);
}

function Drawer({
  eyebrow,
  title,
  onClose,
  children,
}: {
  eyebrow: string;
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return (
    <div className="drawer-backdrop" role="presentation" onMouseDown={onClose}>
      <aside className="workspace-drawer" role="dialog" aria-modal="true" aria-label={title} onMouseDown={(event) => event.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <p className="eyebrow">{eyebrow}</p>
            <h2>{title}</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose} aria-label="Close drawer">
            <X size={20} />
          </button>
        </div>
        {children}
      </aside>
    </div>
  );
}

function SourceStoplightButton({
  data,
  sourceId,
  onOpen,
}: {
  data: V3Data;
  sourceId: string;
  onOpen: (sourceId: string) => void;
}) {
  const readiness = sourceReadiness(data, sourceId);
  const status = stringValue(readiness, "overall_readiness", "pending");
  return (
    <button
      type="button"
      className={`source-chip ${statusTone(status)}`}
      onClick={(event) => {
        event.stopPropagation();
        onOpen(sourceId);
      }}
      title={stringValue(readiness, "curated_view", sourceId)}
    >
      <span aria-hidden="true" />
      {stringValue(readiness, "source_view_name", sourceId)}
    </button>
  );
}

function SourceChipGroup({
  data,
  sourceIds,
  onOpen,
  limit = 4,
}: {
  data: V3Data;
  sourceIds: string[];
  onOpen: (sourceId: string) => void;
  limit?: number;
}) {
  const visible = sourceIds.slice(0, limit);
  return (
    <div className="source-chip-row">
      {visible.map((sourceId) => (
        <SourceStoplightButton key={sourceId} data={data} sourceId={sourceId} onOpen={onOpen} />
      ))}
      {sourceIds.length > visible.length && <span className="mini-badge neutral">+{sourceIds.length - visible.length} sources</span>}
    </div>
  );
}

function WorkspaceMetricTile({
  label,
  value,
  detail,
  delta,
  tone,
  classification,
  sourceIds,
  data,
  onOpenSource,
  onClick,
}: {
  label: string;
  value: string;
  detail: string;
  delta: string;
  tone: Tone;
  classification: string;
  sourceIds: string[];
  data: V3Data;
  onOpenSource: (sourceId: string) => void;
  onClick?: () => void;
}) {
  return (
    <article
      className={`workspace-metric-tile ${tone}`}
      onClick={onClick}
      onKeyDown={(event) => {
        if (!onClick || (event.key !== "Enter" && event.key !== " ")) return;
        event.preventDefault();
        onClick();
      }}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="workspace-metric-top">
        <span>{label}</span>
        <ClassificationBadge value={classification} />
      </div>
      <strong>{value}</strong>
      <p>{detail}</p>
      <em>{delta}</em>
      <SourceChipGroup data={data} sourceIds={sourceIds} onOpen={onOpenSource} limit={3} />
    </article>
  );
}

function SourceDrawerContent({ data, sourceId }: { data: V3Data; sourceId: string }) {
  const readiness = sourceReadiness(data, sourceId);
  const source = data.sourceRegistry.find((row) => stringValue(row, "source_id") === sourceId);
  const row = readiness ?? source;
  if (!row) return <p className="muted">Source readiness record not found.</p>;
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Readiness</span>
          <ReadinessBadge value={row.overall_readiness ?? "registered"} />
        </div>
        <div>
          <span>Freshness</span>
          <strong>{stringValue(row, "freshness", stringValue(source, "cadence"))}</strong>
        </div>
        <div>
          <span>Row count</span>
          <strong>{formatInteger(numberValue(row, "row_count_value"))}</strong>
        </div>
        <div>
          <span>Domain</span>
          <strong>{stringValue(row, "source_domain", stringValue(source, "source_domain"))}</strong>
        </div>
      </div>
      <div className="detail-list">
        <div>
          <dt>Curated view</dt>
          <dd>{stringValue(row, "curated_view", stringValue(source, "curated_view"))}</dd>
        </div>
        <div>
          <dt>Grain</dt>
          <dd>{stringValue(source, "grain")}</dd>
        </div>
        <div>
          <dt>Fields</dt>
          <dd>{stringValue(source, "fields")}</dd>
        </div>
        <div>
          <dt>Validation</dt>
          <dd>{stringValue(source, "validation_rules", stringValue(row, "caveat"))}</dd>
        </div>
      </div>
      <RegistryTable rows={[row]} columns={["source_view_present", "field_populated", "freshness", "row_count", "timestamp_logic", "metric_definition_approved", "small_cell_suppression"]} />
    </div>
  );
}

function DetailList({ rows }: { rows: Array<[string, unknown]> }) {
  return (
    <dl className="detail-list">
      {rows.map(([label, value]) => (
        <div key={label}>
          <dt>{label}</dt>
          <dd>{String(value ?? "")}</dd>
        </div>
      ))}
    </dl>
  );
}

function TimelineStrip({ rows, labelKey, valueKey }: { rows: DataRow[]; labelKey: string; valueKey: string }) {
  const values = rows.map((row) => numberValue(row, valueKey));
  const max = Math.max(...values, 1);
  return (
    <div className="timeline-strip" aria-label={`${valueKey} trend`}>
      {rows.map((row, index) => (
        <span key={`${stringValue(row, labelKey)}-${index}`} style={{ height: `${Math.max(12, (numberValue(row, valueKey) / max) * 92)}%` }} title={`${stringValue(row, labelKey)}: ${numberValue(row, valueKey).toFixed(2)}`} />
      ))}
    </div>
  );
}

function UnitDrilldownBoard({
  rows,
  selectedId,
  onSelect,
}: {
  rows: DataRow[];
  selectedId: string;
  onSelect: (unitId: string) => void;
}) {
  return (
    <div className="drilldown-card-grid">
      {rows.map((row) => {
        const unitId = stringValue(row, "unit_id");
        return (
          <button type="button" className={`drilldown-card ${selectedId === unitId ? "active" : ""}`} key={unitId} onClick={() => onSelect(unitId)}>
            <div>
              <strong>{stringValue(row, "unit_name")}</strong>
              <ReadinessBadge value={row.source_readiness} />
            </div>
            <span>{stringValue(row, "site_name")}</span>
            <dl>
              <div>
                <dt>Occupancy</dt>
                <dd>{formatPct(numberValue(row, "occupancy_pct"))}</dd>
              </div>
              <div>
                <dt>Boarders</dt>
                <dd>{formatInteger(numberValue(row, "ed_boarders"))}</dd>
              </div>
              <div>
                <dt>Staff gap</dt>
                <dd>{formatPct(numberValue(row, "staffing_gap_pct"))}</dd>
              </div>
            </dl>
          </button>
        );
      })}
    </div>
  );
}

function ProgramDrilldownBoard({
  rows,
  selectedId,
  onSelect,
}: {
  rows: DataRow[];
  selectedId: string;
  onSelect: (programId: string) => void;
}) {
  return (
    <div className="drilldown-card-grid">
      {rows.map((row) => {
        const programId = stringValue(row, "program_id");
        return (
          <button type="button" className={`drilldown-card ${selectedId === programId ? "active" : ""}`} key={programId} onClick={() => onSelect(programId)}>
            <div>
              <strong>{stringValue(row, "program")}</strong>
              <ReadinessBadge value={row.source_readiness} />
            </div>
            <span>{stringValue(row, "freshness")}</span>
            <dl>
              <div>
                <dt>Waitlist</dt>
                <dd>{formatInteger(numberValue(row, "waitlist_total"))}</dd>
              </div>
              <div>
                <dt>TNA</dt>
                <dd>{Math.round(numberValue(row, "third_next_available_days"))}d</dd>
              </div>
              <div>
                <dt>Breach</dt>
                <dd>{formatPct(numberValue(row, "urgent_breach_risk"))}</dd>
              </div>
            </dl>
          </button>
        );
      })}
    </div>
  );
}

function UnitDrawerContent({ data, unitId, onOpenSource }: { data: V3Data; unitId: string; onOpenSource: (sourceId: string) => void }) {
  const detail = data.inpatient.unitDetails.find((row) => stringValue(row, "unit_id") === unitId);
  const timeline = data.inpatient.unitTimeline.filter((row) => stringValue(row, "unit_id") === unitId);
  if (!detail) return <p className="muted">Unit drilldown not found.</p>;
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Census</span>
          <strong>{formatInteger(numberValue(detail, "census"))}</strong>
        </div>
        <div>
          <span>Effective beds</span>
          <strong>{formatInteger(numberValue(detail, "effective_beds"))}</strong>
        </div>
        <div>
          <span>Step-down ready</span>
          <strong>{formatInteger(numberValue(detail, "step_down_ready"))}</strong>
        </div>
        <div>
          <span>Staff gap hours</span>
          <strong>{numberValue(detail, "staffing_gap_hours").toFixed(1)}</strong>
        </div>
      </div>
      <TimelineStrip rows={timeline} labelKey="horizon_hours" valueKey="occupancy_pct" />
      <DetailList
        rows={[
          ["Service line", stringValue(detail, "service_line")],
          ["Level of care", stringValue(detail, "level_of_care_mix")],
          ["Respiratory support", formatInteger(numberValue(detail, "respiratory_support_count"))],
          ["Discharge barriers", formatInteger(numberValue(detail, "discharge_barriers"))],
          ["Skill mix gap", stringValue(detail, "skill_mix_gap")],
          ["Models", stringValue(detail, "model_ids")],
        ]}
      />
      <SourceChipGroup data={data} sourceIds={csvIds(detail.source_ids)} onOpen={onOpenSource} limit={8} />
      <p className="muted">{stringValue(detail, "caveat")}</p>
    </div>
  );
}

function ProgramDrawerContent({ data, programId, onOpenSource }: { data: V3Data; programId: string; onOpenSource: (sourceId: string) => void }) {
  const detail = data.ambulatory.programDetails.find((row) => stringValue(row, "program_id") === programId);
  const timeline = data.ambulatory.programTimeline.filter((row) => stringValue(row, "program_id") === programId);
  if (!detail) return <p className="muted">Program drilldown not found.</p>;
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Waitlist</span>
          <strong>{formatInteger(numberValue(detail, "waitlist_total"))}</strong>
        </div>
        <div>
          <span>Over target</span>
          <strong>{formatInteger(numberValue(detail, "over_target_count"))}</strong>
        </div>
        <div>
          <span>Protected slots</span>
          <strong>{formatInteger(numberValue(detail, "protected_urgent_slots"))}</strong>
        </div>
        <div>
          <span>Diagnostic gaps</span>
          <strong>{formatInteger(numberValue(detail, "missing_prerequisites"))}</strong>
        </div>
      </div>
      <TimelineStrip rows={timeline} labelKey="horizon_weeks" valueKey="waitlist_total" />
      <DetailList
        rows={[
          ["Urgent waitlist", formatInteger(numberValue(detail, "urgent_waitlist"))],
          ["p90 wait", `${formatInteger(numberValue(detail, "p90_wait_days"))} days`],
          ["No-show rate", formatPct(numberValue(detail, "no_show_rate"))],
          ["Virtual suitability", formatPct(numberValue(detail, "virtual_suitability"))],
          ["Travel burden", numberValue(detail, "travel_burden_index").toFixed(2)],
          ["Models", stringValue(detail, "model_ids")],
        ]}
      />
      <SourceChipGroup data={data} sourceIds={csvIds(detail.source_ids)} onOpen={onOpenSource} limit={8} />
      <p className="muted">{stringValue(detail, "caveat")}</p>
    </div>
  );
}

function ModelDrawerContent({ data, assetId, onOpenSource }: { data: V3Data; assetId: string; onOpenSource: (sourceId: string) => void }) {
  const model = data.modelRegistry.find((row) => stringValue(row, "asset_id") === assetId);
  const warnings = data.gatekeeper.warningLogic.filter((row) => stringValue(row, "asset_id") === assetId);
  const validation = data.gatekeeper.validationDrift.find((row) => stringValue(row, "asset_id") === assetId);
  const release = data.gatekeeper.releaseRollback.find((row) => stringValue(row, "asset_id") === assetId);
  const metricIds = Array.from(new Set(warnings.map((row) => stringValue(row, "metric_id")).filter(Boolean)));
  const metrics = data.metricRegistry.filter((row) => metricIds.includes(stringValue(row, "metric_id")));
  const sourceIds = Array.from(new Set(metrics.flatMap((row) => csvIds(row.source_fields))));
  const coefficients = data.gatekeeper.coefficients.filter((row) => metricIds.some((metricId) => stringValue(row, "applies_to").includes(metricId)) || stringValue(row, "applies_to").includes(assetId));
  if (!model) return <p className="muted">Model card not found.</p>;
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Governance</span>
          <ReadinessBadge value={model.governance_status} />
        </div>
        <div>
          <span>Calibration</span>
          <strong>{stringValue(validation, "calibration_status", stringValue(model, "calibration_status"))}</strong>
        </div>
        <div>
          <span>Drift</span>
          <strong>{stringValue(validation, "drift_status", stringValue(model, "drift_status"))}</strong>
        </div>
        <div>
          <span>Release gate</span>
          <strong>{stringValue(validation, "release_gate", stringValue(release, "release_status"))}</strong>
        </div>
      </div>
      <DetailList
        rows={[
          ["Intended use", stringValue(model, "intended_use")],
          ["Not intended", stringValue(model, "not_intended_use")],
          ["Features", stringValue(model, "features")],
          ["Thresholds", stringValue(model, "thresholds")],
          ["Alert burden", stringValue(validation, "alert_burden", stringValue(model, "alert_burden"))],
          ["Rollback", stringValue(release, "rollback_action", stringValue(model, "rollback_plan"))],
        ]}
      />
      <div className="drawer-section">
        <h3>Warning logic</h3>
        <RegistryTable rows={warnings} columns={["warning_id", "metric_id", "condition", "threshold", "severity", "status"]} limit={8} />
      </div>
      <div className="drawer-section">
        <h3>Coefficients</h3>
        <RegistryTable rows={coefficients} columns={["coefficient_id", "coefficient_name", "value", "unit", "review_status"]} limit={8} />
      </div>
      <div className="drawer-section">
        <h3>Source lineage</h3>
        <SourceChipGroup data={data} sourceIds={sourceIds} onOpen={onOpenSource} limit={12} />
      </div>
      <p className="muted">{stringValue(model, "caveats", stringValue(model, "warnings"))}</p>
    </div>
  );
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

function SourceReadinessTable({ rows, limit = 8, onSelect }: { rows: DataRow[]; limit?: number; onSelect?: (sourceId: string) => void }) {
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
            <tr key={stringValue(row, "source_id")} className={onSelect ? "clickable-row" : ""} onClick={() => onSelect?.(stringValue(row, "source_id"))}>
              <td>
                <strong>{stringValue(row, "source_view_name", stringValue(row, "source_id"))}</strong>
                <span className="table-subtext">{stringValue(row, "source_domain", stringValue(row, "source_id"))}</span>
              </td>
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

function ModelCardGrid({ rows, limit = 15, onSelect }: { rows: DataRow[]; limit?: number; onSelect?: (assetId: string) => void }) {
  return (
    <div className="model-card-grid">
      {rows.slice(0, limit).map((row) => (
        <button type="button" className="model-card model-card-button" key={stringValue(row, "asset_id")} onClick={() => onSelect?.(stringValue(row, "asset_id"))}>
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
        </button>
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

const POSTURE_METRIC_SOURCES: Record<string, { classification: string; sources: string[] }> = {
  "Network occupancy": { classification: "derived", sources: ["SRC_SYNTH_UNIT_CENSUS_HOURLY", "SRC_SYNTH_BED_STATUS", "SRC_SYNTH_STAFFING_ROSTER"] },
  "ED boarder hours": { classification: "derived", sources: ["SRC_SYNTH_ED_VISITS", "SRC_SYNTH_ADT_EVENTS", "SRC_SYNTH_PATIENT_CLASS_STATUS"] },
  "Ambulatory backlog": { classification: "derived", sources: ["SRC_SYNTH_WAITLIST_SNAPSHOTS", "SRC_SYNTH_REFERRALS", "SRC_SYNTH_REFERRAL_TRIAGE"] },
  "Governed active assets": { classification: "modelled", sources: ["SRC_MODEL_CARD_REGISTRY", "SRC_MODEL_VALIDATION_RESULTS", "SRC_WARNING_LOGIC_REGISTRY"] },
};

function readinessCounts(rows: DataRow[]): ReadinessCounts {
  return rows.reduce<ReadinessCounts>(
    (counts, row) => {
      const status = statusTone(row.overall_readiness ?? row.readiness_status ?? row.governance_status);
      if (status === "ready") counts.ready += 1;
      else if (status === "high") counts.high += 1;
      else if (stringValue(row, "overall_readiness") === "not_mapped") counts.high += 1;
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
  const [selectedSourceId, setSelectedSourceId] = useState("");
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
        {data.systemPosture.kpis.map((row) => {
          const label = stringValue(row, "label");
          const wiring = POSTURE_METRIC_SOURCES[label] ?? { classification: "derived", sources: [] };
          return (
            <WorkspaceMetricTile
              key={label}
              label={label}
              value={stringValue(row, "value")}
              detail={stringValue(row, "detail")}
              delta={stringValue(row, "delta")}
              tone={kpiTone(row.tone)}
              classification={wiring.classification}
              sourceIds={wiring.sources}
              data={data}
              onOpenSource={setSelectedSourceId}
              onClick={() => wiring.sources[0] && setSelectedSourceId(wiring.sources[0])}
            />
          );
        })}
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
        <SourceReadinessTable rows={data.directLinkValidation} onSelect={setSelectedSourceId} />
      </Panel>

      <Panel span="normal" eyebrow="Panel lineage" title="This page is derived, not a direct chart" icon={<Layers3 size={22} />}>
        <LineageCard data={data} panelId="PANEL_SYSTEM_POSTURE" />
      </Panel>
      {selectedSourceId && (
        <Drawer eyebrow="Source Readiness" title={selectedSourceId} onClose={() => setSelectedSourceId("")}>
          <SourceDrawerContent data={data} sourceId={selectedSourceId} />
        </Drawer>
      )}
    </section>
  );
}

export function FrontierInpatientPage({ data, context }: { data: V3Data; context: AppContext }) {
  const scopedUnits = context.site === "All sites" ? data.inpatient.unitPressure : data.inpatient.unitPressure.filter((row) => stringValue(row, "site_id") === context.site);
  const visibleUnits = scopedUnits.length ? scopedUnits : data.inpatient.unitPressure;
  const censusProxy = Math.round(sumRows(data.inpatient.unitPressure, "occupancy_pct") * 42);
  const boarders = sumRows(data.inpatient.unitPressure, "ed_boarders");
  const staffingGap = avgRows(data.inpatient.unitPressure, "staffing_gap_pct");
  const [selectedUnitId, setSelectedUnitId] = useState("");
  const [selectedSourceId, setSelectedSourceId] = useState("");
  const activeUnitId = selectedUnitId || stringValue(visibleUnits[0], "unit_id");
  const activeUnit = visibleUnits.find((row) => stringValue(row, "unit_id") === activeUnitId);
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Inpatient Intelligence" title="Huddle view with source-readiness and model warnings" icon={<Activity size={22} />}>
        <LineageCard data={data} panelId="PANEL_INPATIENT_COMMAND" />
      </Panel>
      <section className="kpi-grid wide">
        <WorkspaceMetricTile label="Occupancy proxy" value={formatInteger(censusProxy)} detail="Synthetic weighted census pressure" delta="+2.8 pts" tone="watch" classification="derived" sourceIds={["SRC_SYNTH_UNIT_CENSUS_HOURLY", "SRC_SYNTH_BED_STATUS", "SRC_SYNTH_STAFFING_ROSTER"]} data={data} onOpenSource={setSelectedSourceId} />
        <WorkspaceMetricTile label="ED boarders" value={formatInteger(boarders)} detail="Across selected synthetic units" delta="+21" tone="high" classification="derived" sourceIds={["SRC_SYNTH_ED_VISITS", "SRC_SYNTH_ADT_EVENTS", "SRC_SYNTH_PATIENT_CLASS_STATUS"]} data={data} onOpenSource={setSelectedSourceId} />
        <WorkspaceMetricTile label="Staffing gap" value={formatPct(staffingGap)} detail="Mean unit-shift gap" delta="+1.9 pts" tone="watch" classification="derived" sourceIds={["SRC_SYNTH_STAFFING_ROSTER", "SRC_SYNTH_STAFFING_GAPS", "SRC_SYNTH_WORKLOAD_ACUITY"]} data={data} onOpenSource={setSelectedSourceId} />
        <WorkspaceMetricTile label="Source reviews" value={formatInteger(data.inpatient.unitPressure.filter((row) => stringValue(row, "source_readiness") !== "ready").length)} detail="Panel rows requiring owner review" delta="review" tone="watch" classification="direct" sourceIds={["SRC_DIRECT_LINKAGE_VALIDATION", "SRC_SYNTH_DIAGNOSTIC_READINESS", "SRC_MODEL_DRIFT_RESULTS"]} data={data} onOpenSource={setSelectedSourceId} />
      </section>
      <Panel span="xlarge" eyebrow="Clickable unit workspace" title="Select a unit to open source-layer detail" icon={<GitBranch size={22} />}>
        <UnitDrilldownBoard rows={visibleUnits} selectedId={activeUnitId} onSelect={setSelectedUnitId} />
        <button type="button" className="primary-action" disabled={!activeUnit} onClick={() => activeUnit && setSelectedUnitId(activeUnitId)}>
          <ArrowRight size={18} />
          Open selected unit drawer
        </button>
      </Panel>
      <Panel span="normal" eyebrow="Warning logic" title="Governed warning queue" icon={<AlertTriangle size={22} />}>
        <WarningList rows={data.inpatient.warnings} />
      </Panel>
      <Panel span="xlarge" eyebrow="Unit heatmap" title="Chart supports the clickable unit cards" icon={<Gauge size={22} />}>
        <UnitPressureHeatmap rows={visibleUnits} />
      </Panel>
      <Panel span="xlarge" eyebrow="Forecast ribbon" title="Occupancy forecast carries model-card caveats" icon={<BrainCircuit size={22} />}>
        <ForecastRibbonChart rows={data.inpatient.forecast} xKey="horizon_hours" predictionKey="occupancy_forecast" lowerKey="p10" upperKey="p90" label="Inpatient occupancy forecast" />
      </Panel>
      <Panel span="normal" eyebrow="Why bed pressure moved" title="Discharge and step-down drivers" icon={<FileCheck2 size={22} />}>
        <HorizontalBarChart rows={data.inpatient.flowDrivers} labelKey="driver" valueKey="active_count" label="Discharge and step-down drivers" height={280} />
      </Panel>
      {selectedUnitId && (
        <Drawer eyebrow="Unit Drilldown" title={stringValue(activeUnit, "unit_name", selectedUnitId)} onClose={() => setSelectedUnitId("")}>
          <UnitDrawerContent data={data} unitId={selectedUnitId} onOpenSource={setSelectedSourceId} />
        </Drawer>
      )}
      {selectedSourceId && (
        <Drawer eyebrow="Source Readiness" title={selectedSourceId} onClose={() => setSelectedSourceId("")}>
          <SourceDrawerContent data={data} sourceId={selectedSourceId} />
        </Drawer>
      )}
    </section>
  );
}

export function FrontierAmbulatoryPage({ data }: { data: V3Data; context: AppContext }) {
  const waitlist = sumRows(data.ambulatory.programAccess, "waitlist_total");
  const tna = avgRows(data.ambulatory.programAccess, "third_next_available_days");
  const breach = avgRows(data.ambulatory.programAccess, "urgent_breach_risk");
  const [selectedProgramId, setSelectedProgramId] = useState("");
  const [selectedSourceId, setSelectedSourceId] = useState("");
  const activeProgramId = selectedProgramId || stringValue(data.ambulatory.programAccess[0], "program_id");
  const activeProgram = data.ambulatory.programAccess.find((row) => stringValue(row, "program_id") === activeProgramId);
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Ambulatory Access Intelligence" title="Backlog, template capacity, no-show guardrails, and diagnostic readiness" icon={<Workflow size={22} />}>
        <LineageCard data={data} panelId="PANEL_AMBULATORY_COMMAND" />
      </Panel>
      <section className="kpi-grid wide">
        <WorkspaceMetricTile label="Waitlist" value={formatInteger(waitlist)} detail="Synthetic aggregate referral backlog" delta="+4.6%" tone="watch" classification="derived" sourceIds={["SRC_SYNTH_WAITLIST_SNAPSHOTS", "SRC_SYNTH_REFERRALS", "SRC_SYNTH_REFERRAL_TRIAGE"]} data={data} onOpenSource={setSelectedSourceId} />
        <WorkspaceMetricTile label="Third next available" value={`${Math.round(tna)} days`} detail="Mean by program" delta="+3" tone="watch" classification="derived" sourceIds={["SRC_SYNTH_CLINIC_TEMPLATES", "SRC_SYNTH_CLINIC_SLOTS", "SRC_SYNTH_APPOINTMENTS"]} data={data} onOpenSource={setSelectedSourceId} />
        <WorkspaceMetricTile label="Urgent breach risk" value={formatPct(breach)} detail="Synthetic program-week probability" delta="+4 pts" tone="high" classification="modelled" sourceIds={["SRC_MODEL_PREDICTIONS", "SRC_SYNTH_WAITLIST_SNAPSHOTS", "SRC_WARNING_LOGIC_REGISTRY"]} data={data} onOpenSource={setSelectedSourceId} />
        <WorkspaceMetricTile label="Diagnostic readiness" value={formatPct(avgRows(data.ambulatory.programAccess, "diagnostic_readiness"))} detail="Dependency completion proxy" delta="-6 pts" tone="watch" classification="derived" sourceIds={["SRC_SYNTH_DIAGNOSTIC_READINESS", "SRC_SYNTH_IMAGING_ORDERS", "SRC_SYNTH_LAB_RESULTS"]} data={data} onOpenSource={setSelectedSourceId} />
      </section>
      <Panel span="xlarge" eyebrow="Clickable program workspace" title="Select a program to open access, template, diagnostic, and source detail" icon={<Activity size={22} />}>
        <ProgramDrilldownBoard rows={data.ambulatory.programAccess} selectedId={activeProgramId} onSelect={setSelectedProgramId} />
        <button type="button" className="primary-action" disabled={!activeProgram} onClick={() => activeProgram && setSelectedProgramId(activeProgramId)}>
          <ArrowRight size={18} />
          Open selected program drawer
        </button>
      </Panel>
      <Panel span="normal" eyebrow="No-show frontier" title="Guardrailed capacity recovery" icon={<Flag size={22} />}>
        <RegistryTable rows={data.ambulatory.noShowFrontier} columns={["program", "guarded_overbook_pct", "expected_recovered_slots", "equity_guardrail", "no_show_risk"]} limit={8} />
      </Panel>
      <Panel span="xlarge" eyebrow="Access chart" title="Waitlist and urgent breach risk by program" icon={<Gauge size={22} />}>
        <HorizontalBarChart rows={data.ambulatory.programAccess} labelKey="program" valueKey="waitlist_total" label="Ambulatory waitlist by program" />
      </Panel>
      <Panel span="xlarge" eyebrow="Backlog forecast" title="Scenario planning forecast, not a scheduling directive" icon={<BrainCircuit size={22} />}>
        <ForecastRibbonChart rows={data.ambulatory.forecast} xKey="horizon_weeks" predictionKey="backlog_forecast" lowerKey="p10" upperKey="p90" label="Ambulatory backlog forecast" />
      </Panel>
      <Panel span="normal" eyebrow="Warning logic" title="Program huddle queue" icon={<AlertTriangle size={22} />}>
        <WarningList rows={data.ambulatory.warnings} />
      </Panel>
      {selectedProgramId && (
        <Drawer eyebrow="Program Drilldown" title={stringValue(activeProgram, "program", selectedProgramId)} onClose={() => setSelectedProgramId("")}>
          <ProgramDrawerContent data={data} programId={selectedProgramId} onOpenSource={setSelectedSourceId} />
        </Drawer>
      )}
      {selectedSourceId && (
        <Drawer eyebrow="Source Readiness" title={selectedSourceId} onClose={() => setSelectedSourceId("")}>
          <SourceDrawerContent data={data} sourceId={selectedSourceId} />
        </Drawer>
      )}
    </section>
  );
}

export function PredictiveAssetsPage({ data }: { data: V3Data }) {
  const signalRows = data.predictiveAssets.signals;
  const [selectedAssetId, setSelectedAssetId] = useState(stringValue(data.modelRegistry[0], "asset_id"));
  const [drawerAssetId, setDrawerAssetId] = useState("");
  const [selectedSourceId, setSelectedSourceId] = useState("");
  const selectedAsset = data.modelRegistry.find((row) => stringValue(row, "asset_id") === selectedAssetId) ?? data.modelRegistry[0];
  const drawerAsset = data.modelRegistry.find((row) => stringValue(row, "asset_id") === drawerAssetId);
  const selectedEvidence = data.predictiveAssets.evidenceTrails.filter((row) => stringValue(row, "asset_id") === selectedAssetId);
  const selectedValidation = data.gatekeeper.validationDrift.find((row) => stringValue(row, "asset_id") === selectedAssetId);
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Clinical Surveillance / Predictive Asset Layer" title="Modelled outputs remain governed, labelled, and reversible" icon={<BrainCircuit size={22} />}>
        <LineageCard data={data} panelId="PANEL_PREDICTIVE_ASSETS" />
      </Panel>
      <Panel span="xlarge" eyebrow="Model-card drilldown" title="15 governed synthetic assets" icon={<ShieldCheck size={22} />}>
        <ModelCardGrid rows={data.modelRegistry} onSelect={(assetId) => {
          setSelectedAssetId(assetId);
          setDrawerAssetId(assetId);
        }} />
      </Panel>
      <Panel span="normal" eyebrow="Warning overlay" title="Synthetic surveillance signals" icon={<AlertTriangle size={22} />}>
        <WarningList rows={signalRows} />
      </Panel>
      <Panel span="xlarge" eyebrow="Evidence overlay" title="Trace warnings to review evidence and caveats" icon={<GitBranch size={22} />}>
        <label className="field-stack">
          Asset
          <select value={selectedAssetId} onChange={(event) => setSelectedAssetId(event.target.value)}>
            {data.modelRegistry.map((row) => (
              <option key={stringValue(row, "asset_id")} value={stringValue(row, "asset_id")}>
                {stringValue(row, "name")} ({stringValue(row, "asset_id")})
              </option>
            ))}
          </select>
        </label>
        <div className="model-evidence-card">
          <strong>{stringValue(selectedAsset, "name")}</strong>
          <p>{stringValue(selectedAsset, "intended_use")}</p>
          <dl>
            <div>
              <dt>Calibration</dt>
              <dd>{stringValue(selectedValidation, "calibration_status", stringValue(selectedAsset, "calibration_status"))}</dd>
            </div>
            <div>
              <dt>Drift</dt>
              <dd>{stringValue(selectedValidation, "drift_status", stringValue(selectedAsset, "drift_status"))}</dd>
            </div>
            <div>
              <dt>Alert burden</dt>
              <dd>{stringValue(selectedValidation, "alert_burden", stringValue(selectedAsset, "alert_burden"))}</dd>
            </div>
            <div>
              <dt>Release gate</dt>
              <dd>{stringValue(selectedValidation, "release_gate", stringValue(selectedAsset, "governance_status"))}</dd>
            </div>
          </dl>
          <em>{stringValue(selectedAsset, "not_intended_use")}</em>
        </div>
        <RegistryTable rows={selectedEvidence.length ? selectedEvidence : data.predictiveAssets.evidenceTrails} columns={["trail_id", "asset_id", "evidence_step", "detail"]} limit={8} />
      </Panel>
      <Panel span="normal" eyebrow="Safety boundary" title="No clinical decisioning" icon={<FileCheck2 size={22} />}>
        <InsightPanel
          title="Displayed as synthetic-only"
          body="Clinical surveillance assets are shown to demonstrate governance and warning controls. They are not validated for diagnosis, triage, treatment, or patient-level action."
          actions={["Require threshold review.", "Suppress small cells.", "Retain rollback path and evidence trail."]}
        />
      </Panel>
      {drawerAssetId && (
        <Drawer eyebrow="Model Card" title={stringValue(drawerAsset, "name", drawerAssetId)} onClose={() => setDrawerAssetId("")}>
          <ModelDrawerContent data={data} assetId={drawerAssetId} onOpenSource={setSelectedSourceId} />
        </Drawer>
      )}
      {selectedSourceId && (
        <Drawer eyebrow="Source Readiness" title={selectedSourceId} onClose={() => setSelectedSourceId("")}>
          <SourceDrawerContent data={data} sourceId={selectedSourceId} />
        </Drawer>
      )}
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
  const [domain, setDomain] = useState<"inpatient" | "ambulatory">("inpatient");
  const [controlValues, setControlValues] = useState<Record<string, number>>({});
  const [toggles, setToggles] = useState({
    surgeProtocol: true,
    weekendClinics: false,
    equityGuardrail: true,
    diagnosticHuddle: true,
  });
  const [hrCapacity, setHrCapacity] = useState(18);
  const [financeBudget, setFinanceBudget] = useState(260);
  const controls = data.scenarioLab.controlRanges.filter((row) => stringValue(row, "domain") === domain);
  const baseline = data.scenarioLab.baselines.find((row) => stringValue(row, "domain") === domain) ?? {};
  const getValue = (control: DataRow) => controlValues[stringValue(control, "control_id")] ?? numberValue(control, "default");
  const totalHr = controls.reduce((total, control) => total + getValue(control) * numberValue(control, "hr_per_unit"), 0);
  const totalCost = controls.reduce((total, control) => total + getValue(control) * numberValue(control, "cost_k_per_unit"), 0) + (toggles.weekendClinics ? 42 : 0) + (toggles.surgeProtocol ? 28 : 0);
  const constraintFactor = Math.min(1, hrCapacity / Math.max(1, totalHr), financeBudget / Math.max(1, totalCost));
  const stepdown = controlValues.stepdown_beds ?? 5;
  const pharmacy = controlValues.pharmacy_acceleration ?? 12;
  const staffing = controlValues.staffing_shifts ?? 8;
  const surge = controlValues.surge_beds ?? 4;
  const urgent = controlValues.urgent_slots ?? 48;
  const virtual = controlValues.virtual_conversion ?? 10;
  const diagnostics = controlValues.diagnostic_huddle ?? 14;
  const overbook = controlValues.guarded_overbook ?? 3;
  const inpatientReduction = (stepdown * 7.2 + pharmacy * 1.15 + staffing * 2.4 + surge * 4.8 + (toggles.surgeProtocol ? 18 : 0)) * constraintFactor;
  const ambulatoryReduction = (urgent * 4.1 + virtual * 31 + diagnostics * 24 + overbook * 38 + (toggles.weekendClinics ? 310 : 0)) * constraintFactor * (toggles.equityGuardrail ? 0.88 : 1);
  const scenarioOutcomes =
    domain === "inpatient"
      ? {
          primaryLabel: "Boarder hours",
          baselinePrimary: numberValue(baseline, "boarder_hours", 186),
          scenarioPrimary: Math.max(42, numberValue(baseline, "boarder_hours", 186) - inpatientReduction),
          secondaryLabel: "Occupancy",
          baselineSecondary: numberValue(baseline, "occupancy_pct", 0.934),
          scenarioSecondary: Math.max(0.82, numberValue(baseline, "occupancy_pct", 0.934) - inpatientReduction / 1400),
          improvementLabel: "Boarder-hour reduction",
          improvement: inpatientReduction,
        }
      : {
          primaryLabel: "Backlog",
          baselinePrimary: numberValue(baseline, "backlog", 8940),
          scenarioPrimary: Math.max(6200, numberValue(baseline, "backlog", 8940) - ambulatoryReduction),
          secondaryLabel: "Urgent breach risk",
          baselineSecondary: numberValue(baseline, "urgent_breach_risk", 0.337),
          scenarioSecondary: Math.max(0.08, numberValue(baseline, "urgent_breach_risk", 0.337) - ambulatoryReduction / 22000),
          improvementLabel: "Backlog reduction",
          improvement: ambulatoryReduction,
        };
  function updateControl(controlId: string, value: number) {
    setControlValues((current) => ({ ...current, [controlId]: value }));
  }
  function storeScenarioRun() {
    addMemoryEvent({
      event_id: `EVT-LOCAL-${Date.now()}`,
      event_type: "scenario_run",
      created_at: new Date().toISOString(),
      created_by: "showcase_local_user",
      app_area: "Scenario Simulation Lab",
      site_id: "SITE_PROV_NETWORK",
      unit_or_program: domain,
      related_ids: `${domain}-interactive-scenario`,
      related_metric_id: domain === "inpatient" ? "METRIC_OCCUPANCY" : "METRIC_WAITLIST_PRESSURE",
      related_model_id: domain === "inpatient" ? "INPT_OCCUPANCY_FORECAST" : "AMB_BACKLOG_FORECAST",
      related_panel_id: "PANEL_SCENARIO_LAB",
      related_scenario_id: `${domain}-interactive-scenario`,
      status: "captured locally",
      severity: "low",
      note: `${domain} what-if captured: ${scenarioOutcomes.improvementLabel} ${Math.round(scenarioOutcomes.improvement).toLocaleString()}.`,
      payload_json: JSON.stringify({ synthetic_demo: true, showcase_local: true, controls: controlValues, toggles, hrCapacity, financeBudget }),
      synthetic_demo_flag: true,
      writeback_table: "APP.SCENARIO_RUN_LOG",
    });
  }
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Interactive Scenario Workspace" title="Move sliders, apply constraints, and compare baseline to what-if outcomes" icon={<SlidersHorizontal size={22} />}>
        <div className="scenario-workspace-header">
          <div className="segmented-control" role="group" aria-label="Scenario domain">
            <button className={domain === "inpatient" ? "active" : ""} onClick={() => setDomain("inpatient")}>
              Inpatient flow
            </button>
            <button className={domain === "ambulatory" ? "active" : ""} onClick={() => setDomain("ambulatory")}>
              Ambulatory access
            </button>
          </div>
          <div className="scenario-constraint-pills">
            <span className={totalHr <= hrCapacity ? "ready" : "high"}>
              <Users size={15} /> {totalHr.toFixed(1)} / {hrCapacity} HR shifts
            </span>
            <span className={totalCost <= financeBudget ? "ready" : "high"}>
              <DollarSign size={15} /> ${Math.round(totalCost)}k / ${financeBudget}k
            </span>
            <span className={constraintFactor >= 1 ? "ready" : "review"}>{Math.round(constraintFactor * 100)}% feasible</span>
          </div>
        </div>
        <LineageCard data={data} panelId="PANEL_SCENARIO_LAB" />
      </Panel>

      <Panel span="xlarge" eyebrow="What-if controls" title="Operational levers" icon={<SlidersHorizontal size={22} />}>
        <div className="scenario-control-grid">
          {controls.map((control) => {
            const controlId = stringValue(control, "control_id");
            const value = getValue(control);
            return (
              <label className="slider-control" key={controlId}>
                <span>
                  <strong>{stringValue(control, "label")}</strong>
                  <em>
                    {value}
                    {stringValue(control, "unit") ? ` ${stringValue(control, "unit")}` : ""}
                  </em>
                </span>
                <input
                  type="range"
                  min={numberValue(control, "min")}
                  max={numberValue(control, "max")}
                  value={value}
                  onChange={(event) => updateControl(controlId, Number(event.target.value))}
                />
              </label>
            );
          })}
        </div>
        <div className="toggle-grid">
          {[
            ["surgeProtocol", "Respiratory surge protocol"],
            ["weekendClinics", "Weekend clinic capacity"],
            ["equityGuardrail", "Equity/travel guardrail"],
            ["diagnosticHuddle", "Diagnostic huddle routing"],
          ].map(([key, label]) => (
            <button
              type="button"
              className={toggles[key as keyof typeof toggles] ? "active" : ""}
              key={key}
              onClick={() => setToggles((current) => ({ ...current, [key]: !current[key as keyof typeof toggles] }))}
            >
              <CheckCircle2 size={16} />
              {label}
            </button>
          ))}
        </div>
      </Panel>

      <Panel span="normal" eyebrow="Constraints" title="HR and finance feasibility" icon={<DollarSign size={22} />}>
        <label className="slider-control compact">
          <span>
            <strong>Available HR shifts</strong>
            <em>{hrCapacity}</em>
          </span>
          <input type="range" min={4} max={42} value={hrCapacity} onChange={(event) => setHrCapacity(Number(event.target.value))} />
        </label>
        <label className="slider-control compact">
          <span>
            <strong>Finance cap</strong>
            <em>${financeBudget}k</em>
          </span>
          <input type="range" min={60} max={520} step={10} value={financeBudget} onChange={(event) => setFinanceBudget(Number(event.target.value))} />
        </label>
        <button className="primary-action" onClick={storeScenarioRun}>
          <Plus size={18} />
          Capture what-if
        </button>
        <p className="muted">Captured what-ifs stay local in the showcase; Snowflake Streamlit writes to APP.SCENARIO_RUN_LOG.</p>
      </Panel>

      <Panel span="xlarge" eyebrow="Baseline vs scenario" title="Live outcome comparison" icon={<GitBranch size={22} />}>
        <div className="comparison-board">
          <article>
            <span>{scenarioOutcomes.primaryLabel}</span>
            <div className="comparison-bars">
              <div>
                <em>Baseline</em>
                <strong>{formatInteger(scenarioOutcomes.baselinePrimary)}</strong>
                <progress max={scenarioOutcomes.baselinePrimary} value={scenarioOutcomes.baselinePrimary} />
              </div>
              <div>
                <em>Scenario</em>
                <strong>{formatInteger(scenarioOutcomes.scenarioPrimary)}</strong>
                <progress max={scenarioOutcomes.baselinePrimary} value={scenarioOutcomes.scenarioPrimary} />
              </div>
            </div>
          </article>
          <article>
            <span>{scenarioOutcomes.secondaryLabel}</span>
            <div className="comparison-bars">
              <div>
                <em>Baseline</em>
                <strong>{scenarioOutcomes.baselineSecondary <= 1 ? formatPct(scenarioOutcomes.baselineSecondary) : formatInteger(scenarioOutcomes.baselineSecondary)}</strong>
                <progress max={1} value={scenarioOutcomes.baselineSecondary <= 1 ? scenarioOutcomes.baselineSecondary : 1} />
              </div>
              <div>
                <em>Scenario</em>
                <strong>{scenarioOutcomes.scenarioSecondary <= 1 ? formatPct(scenarioOutcomes.scenarioSecondary) : formatInteger(scenarioOutcomes.scenarioSecondary)}</strong>
                <progress max={1} value={scenarioOutcomes.scenarioSecondary <= 1 ? scenarioOutcomes.scenarioSecondary : Math.min(1, scenarioOutcomes.scenarioSecondary / scenarioOutcomes.baselineSecondary)} />
              </div>
            </div>
          </article>
          <article className="improvement-card">
            <span>{scenarioOutcomes.improvementLabel}</span>
            <strong>{formatInteger(scenarioOutcomes.improvement)}</strong>
            <p>{constraintFactor < 1 ? "Constrained by HR or finance. Increase capacity to unlock more impact." : "Within active HR and finance constraints."}</p>
          </article>
        </div>
      </Panel>

      <Panel span="normal" eyebrow="Scenario frontier" title="Precomputed scenario anchors" icon={<Sparkles size={22} />}>
        <ScenarioFrontier rows={data.scenarioLab.scenarios.filter((row) => stringValue(row, "domain") === domain)} outcomeKey="outcome_value" label="Scenario frontier" />
      </Panel>

      <Panel span="wide" eyebrow="Scenario table" title="Readiness, classification, and writeback path" icon={<FileCheck2 size={22} />}>
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
      <Panel span="xlarge" eyebrow="Warning registry" title="Thresholds, acknowledgement, and rollback controls" icon={<AlertTriangle size={22} />}>
        <RegistryTable rows={data.gatekeeper.warningLogic} columns={["warning_id", "asset_id", "metric_id", "threshold", "severity", "status"]} limit={10} />
      </Panel>
      <Panel span="normal" eyebrow="Coefficient registry" title="Synthetic parameters requiring review" icon={<ListChecks size={22} />}>
        <RegistryTable rows={data.gatekeeper.coefficients} columns={["coefficient_id", "coefficient_name", "applies_to", "value", "review_status"]} limit={8} />
      </Panel>
      <Panel span="xlarge" eyebrow="Data quality rules" title="Contract checks behind the readiness stoplight" icon={<FileCheck2 size={22} />}>
        <RegistryTable rows={data.gatekeeper.dataQualityRules} columns={["check_id", "source_id", "rule_name", "severity", "status", "failed_rows"]} limit={10} />
      </Panel>
      <Panel span="normal" eyebrow="Validation and drift" title="Model release gates" icon={<BrainCircuit size={22} />}>
        <RegistryTable rows={data.gatekeeper.validationDrift} columns={["asset_id", "primary_metric", "primary_metric_value", "drift_status", "release_gate"]} limit={8} />
      </Panel>
      <Panel span="wide" eyebrow="Release and rollback" title="Every modelled asset has a reversible path" icon={<Workflow size={22} />}>
        <RegistryTable rows={data.gatekeeper.releaseRollback} columns={["release_id", "asset_id", "release_status", "canary_scope", "rollback_trigger"]} limit={10} />
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
      <Panel span="wide" eyebrow="Curated-view registry" title={`${data.sourceRegistry.length} Connect Care-realistic synthetic wiring placeholders`} icon={<DatabaseZap size={22} />}>
        <RegistryTable rows={data.sourceRegistry} columns={["source_view_name", "curated_view", "source_domain", "grain", "cadence", "classification"]} limit={80} />
      </Panel>
    </section>
  );
}
