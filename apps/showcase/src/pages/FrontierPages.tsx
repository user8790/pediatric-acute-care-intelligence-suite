import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BedDouble,
  BrainCircuit,
  CalendarClock,
  CheckCircle2,
  DatabaseZap,
  DollarSign,
  FileCheck2,
  GitBranch,
  History,
  Layers3,
  ListChecks,
  MapPinned,
  Network,
  Plus,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Users,
  Workflow,
  X,
} from "lucide-react";
import { Panel, PostureCard } from "../components/Panel";
import {
  AccessCalendarHeatmap,
  DischargeFunnel,
  FlowSankey,
  ForecastRibbonChart,
  HorizontalBarChart,
  OpenContextChart,
  ScenarioFrontier,
  SensitivityTornado,
  UnitPressureHeatmap,
  WorkloadMatrix,
} from "../components/ProductCharts";
import type { AppContext, DataRow, V3Data } from "../data/types";
import { avgRows, formatCompact, formatInteger, formatPct, numberValue, siteLabel, stringValue, sumRows, titleCase } from "../lib/format";
import type { PageId } from "../components/AppShell";

type Tone = "neutral" | "watch" | "high" | "good";
type DrawerState =
  | { kind: "source"; id: string }
  | { kind: "unit"; id: string }
  | { kind: "program"; id: string }
  | { kind: "model"; id: string }
  | { kind: "metric"; id: string; row: DataRow }
  | { kind: "site"; id: string; row?: DataRow }
  | { kind: "warning"; id: string; row: DataRow }
  | { kind: "scenario"; id: string; row?: DataRow }
  | { kind: "packet"; id: string; row: DataRow }
  | { kind: "lens"; id: string; row: DataRow }
  | { kind: "huddle"; id: string; row: DataRow }
  | { kind: "escalation"; id: string; row: DataRow }
  | null;

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
  if (status.includes("now") || status.includes("hold") || status.includes("blocked") || status.includes("not_connected") || status.includes("not mapped") || status.includes("high")) return "high";
  if (status.includes("next") || status.includes("pending") || status.includes("review") || status.includes("watch") || status.includes("open")) return "review";
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

function openContextRows(data: V3Data): DataRow[] {
  return data.commandCenter.openContext.length ? data.commandCenter.openContext : [];
}

function latestOpenContext(data: V3Data): DataRow | undefined {
  const rows = openContextRows(data);
  return rows[rows.length - 1];
}

function horizonFactor(horizon: string): number {
  if (horizon.includes("6")) return 1.025;
  if (horizon.includes("24")) return 1.055;
  if (horizon.includes("72")) return 1.085;
  if (horizon.includes("14")) return 1.12;
  if (horizon.includes("26")) return 1.18;
  return 1;
}

function serviceProgramLens(service: string): string | undefined {
  const map: Record<string, string> = {
    respiratory: "respiratory",
    cardiology: "cardiology",
    neurology: "neurology",
    surgery: "surgery_follow_up",
    oncology: "oncology_survivorship",
    complex_care: "complex_care",
    mental_health: "mental_health",
    general_pediatrics: "post_discharge_follow_up",
    short_stay: "post_discharge_follow_up",
    procedural_recovery: "diagnostics",
    picu: "complex_care",
    nicu: "complex_care",
  };
  return map[service];
}

function filterUnits(data: V3Data, context: AppContext): DataRow[] {
  return data.inpatient.unitDetails.filter((row) => {
    const siteOk = context.site === "All sites" || stringValue(row, "site_id") === context.site;
    const serviceOk = context.service === "All services" || stringValue(row, "service_id") === context.service;
    const unitOk = context.unit === "All units" || stringValue(row, "unit_id") === context.unit;
    return siteOk && serviceOk && unitOk;
  });
}

function filterPrograms(data: V3Data, context: AppContext): DataRow[] {
  const lens = context.program === "All programs" ? serviceProgramLens(context.service) : undefined;
  return data.ambulatory.programDetails.filter((row) => {
    const siteOk = context.site === "All sites" || stringValue(row, "site_id") === context.site;
    const explicitProgramOk = context.program === "All programs" || stringValue(row, "program_id") === context.program;
    const serviceLensOk = !lens || stringValue(row, "program_id") === lens;
    return siteOk && explicitProgramOk && serviceLensOk;
  });
}

function filteredTimeline(rows: DataRow[], visibleRows: DataRow[], key: "unit_id" | "program_id"): DataRow[] {
  const visibleIds = new Set(visibleRows.map((row) => stringValue(row, key)));
  if (!visibleIds.size) return rows;
  return rows.filter((row) => visibleIds.has(stringValue(row, key)));
}

function aggregateInpatientTimeline(rows: DataRow[], context: AppContext, data: V3Data): DataRow[] {
  const latest = latestOpenContext(data);
  const openLift =
    numberValue(latest, "respiratory_activity_index") * 0.018 +
    numberValue(latest, "aqhi_max_proxy") * 0.004 +
    (latest?.school_break_flag ? 0.018 : 0);
  const grouped = new Map<number, DataRow[]>();
  for (const row of rows) {
    const hour = numberValue(row, "hour");
    grouped.set(hour, [...(grouped.get(hour) ?? []), row]);
  }
  return Array.from(grouped.entries())
    .sort(([a], [b]) => a - b)
    .map(([hour, group]) => {
      const forecast = avgRows(group, "predicted_occupancy") * horizonFactor(context.horizon) + openLift;
      return {
        hour,
        predicted_occupancy: Math.min(1.35, forecast),
        lower: Math.max(0.3, avgRows(group, "lower") + openLift * 0.6),
        upper: Math.min(1.45, avgRows(group, "upper") + openLift * 1.2),
      };
    });
}

function aggregateProgramTimeline(rows: DataRow[], context: AppContext, data: V3Data): DataRow[] {
  const latest = latestOpenContext(data);
  const openLift =
    1 +
    numberValue(latest, "respiratory_activity_index") * 0.025 +
    numberValue(latest, "aqhi_max_proxy") * 0.006 +
    (latest?.school_break_flag ? 0.035 : 0);
  const grouped = new Map<number, DataRow[]>();
  for (const row of rows) {
    const week = numberValue(row, "week");
    grouped.set(week, [...(grouped.get(week) ?? []), row]);
  }
  return Array.from(grouped.entries())
    .sort(([a], [b]) => a - b)
    .map(([week, group]) => {
      const forecast = sumRows(group, "forecast_waitlist") * horizonFactor(context.horizon) * openLift;
      return {
        week,
        forecast_waitlist: forecast,
        lower: forecast * 0.9,
        upper: forecast * 1.12,
      };
    });
}

function barrierRows(units: DataRow[]): DataRow[] {
  const total = Math.max(1, sumRows(units, "discharge_barriers"));
  return [
    { barrier: "pharmacy", active_count: Math.round(total * 0.28) },
    { barrier: "imaging", active_count: Math.round(total * 0.2) },
    { barrier: "transport", active_count: Math.round(total * 0.17) },
    { barrier: "home supports", active_count: Math.round(total * 0.18) },
    { barrier: "equipment", active_count: Math.round(total * 0.17) },
  ];
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

function ClassificationBadge({ value }: { value: unknown }) {
  const label = titleCase(String(value || "derived"));
  return <span className={`mini-badge ${statusTone(value)}`}>{label}</span>;
}

function ReadinessBadge({ value }: { value: unknown }) {
  return <span className={`mini-badge ${statusTone(value)}`}>{titleCase(String(value || "pending"))}</span>;
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
  const status = stringValue(readiness, "overall_readiness", "registered");
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
      {stringValue(readiness, "source_view_name", sourceId).replace("VW_", "")}
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
  if (!visible.length) return <span className="mini-badge neutral">No source badge</span>;
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

function RegistryTable({
  rows,
  columns,
  limit = 10,
  onSelect,
}: {
  rows: DataRow[];
  columns: string[];
  limit?: number;
  onSelect?: (row: DataRow) => void;
}) {
  return (
    <div className="registry-table">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{titleCase(column)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, limit).map((row, index) => (
            <tr
              key={`${columns.map((column) => stringValue(row, column)).join("-")}-${index}`}
              onClick={() => onSelect?.(row)}
              className={onSelect ? "clickable-row" : undefined}
            >
              {columns.map((column) => (
                <td key={column}>{String(row[column] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SourceReadinessTable({ rows, limit = 8, onSelect }: { rows: DataRow[]; limit?: number; onSelect?: (sourceId: string) => void }) {
  return (
    <div className="source-readiness-table">
      {rows.slice(0, limit).map((row) => (
        <button type="button" key={stringValue(row, "source_id")} onClick={() => onSelect?.(stringValue(row, "source_id"))}>
          <span>{stringValue(row, "source_view_name", stringValue(row, "source_id"))}</span>
          <ReadinessBadge value={row.overall_readiness} />
        </button>
      ))}
    </div>
  );
}

function WarningList({ rows, onSelect }: { rows: DataRow[]; onSelect?: (row: DataRow) => void }) {
  if (!rows.length) return <p className="muted">No active synthetic warnings for this lens.</p>;
  return (
    <div className="warning-list">
      {rows.slice(0, 8).map((row) => (
        <button type="button" key={stringValue(row, "warning_id")} onClick={() => onSelect?.(row)}>
          <AlertTriangle size={17} />
          <span>
            <strong>{stringValue(row, "title", stringValue(row, "warning_id"))}</strong>
            <em>{stringValue(row, "message", stringValue(row, "recommended_action"))}</em>
          </span>
          <ReadinessBadge value={row.severity} />
        </button>
      ))}
    </div>
  );
}

function ModelCardGrid({ rows, limit = 15, onSelect }: { rows: DataRow[]; limit?: number; onSelect?: (assetId: string) => void }) {
  return (
    <div className="model-card-grid">
      {rows.slice(0, limit).map((model) => (
        <button className="model-card-button" type="button" key={stringValue(model, "asset_id")} onClick={() => onSelect?.(stringValue(model, "asset_id"))}>
          <article className="model-card">
            <div className="model-card-top">
              <BrainCircuit size={20} />
              <ReadinessBadge value={model.governance_status} />
            </div>
            <strong>{stringValue(model, "name")}</strong>
            <p>{stringValue(model, "intended_use")}</p>
            <dl>
              <div>
                <dt>Domain</dt>
                <dd>{stringValue(model, "domain")}</dd>
              </div>
              <div>
                <dt>Threshold</dt>
                <dd>{stringValue(model, "threshold_logic", stringValue(model, "thresholds"))}</dd>
              </div>
              <div>
                <dt>Drift</dt>
                <dd>{stringValue(model, "drift", stringValue(model, "drift_status"))}</dd>
              </div>
            </dl>
          </article>
        </button>
      ))}
    </div>
  );
}

function UnitDrilldownBoard({ rows, onSelect }: { rows: DataRow[]; onSelect: (unitId: string) => void }) {
  return (
    <div className="object-card-grid">
      {rows.slice(0, 18).map((row) => (
        <button className="object-card" type="button" key={stringValue(row, "unit_id")} onClick={() => onSelect(stringValue(row, "unit_id"))}>
          <span className="object-card-heading">
            <strong>{stringValue(row, "unit_name")}</strong>
            <ReadinessBadge value={row.source_readiness} />
          </span>
          <span>{stringValue(row, "site_name")}</span>
          <dl>
            <div>
              <dt>Occ</dt>
              <dd>{formatPct(numberValue(row, "occupancy_pct"))}</dd>
            </div>
            <div>
              <dt>Boarders</dt>
              <dd>{formatInteger(numberValue(row, "ed_boarders"))}</dd>
            </div>
            <div>
              <dt>HR gap</dt>
              <dd>{formatInteger(numberValue(row, "staffing_gap_hours"))}h</dd>
            </div>
            <div>
              <dt>Resource</dt>
              <dd>${numberValue(row, "margin_pressure_k").toFixed(1)}k</dd>
            </div>
          </dl>
        </button>
      ))}
    </div>
  );
}

function ProgramDrilldownBoard({ rows, onSelect }: { rows: DataRow[]; onSelect: (programId: string) => void }) {
  return (
    <div className="object-card-grid">
      {rows.slice(0, 18).map((row) => (
        <button className="object-card" type="button" key={`${stringValue(row, "site_id")}-${stringValue(row, "program_id")}`} onClick={() => onSelect(stringValue(row, "program_id"))}>
          <span className="object-card-heading">
            <strong>{stringValue(row, "program")}</strong>
            <ReadinessBadge value={row.source_readiness} />
          </span>
          <span>{stringValue(row, "site_name")}</span>
          <dl>
            <div>
              <dt>Waitlist</dt>
              <dd>{formatInteger(numberValue(row, "waitlist_total"))}</dd>
            </div>
            <div>
              <dt>TNA</dt>
              <dd>{formatInteger(numberValue(row, "third_next_available_days"))}d</dd>
            </div>
            <div>
              <dt>No-show</dt>
              <dd>{formatPct(numberValue(row, "no_show_rate"))}</dd>
            </div>
            <div>
              <dt>Resource</dt>
              <dd>${numberValue(row, "finance_pressure_k").toFixed(1)}k</dd>
            </div>
          </dl>
        </button>
      ))}
    </div>
  );
}

function LineageCard({ data, panelId }: { data: V3Data; panelId: string }) {
  const panel = data.panelLineage.find((row) => stringValue(row, "panel_id") === panelId);
  if (!panel) return <p className="muted">Panel lineage is pending for this surface.</p>;
  return (
    <article className="lineage-card">
      <div>
        <ClassificationBadge value={panel.classification} />
        <ReadinessBadge value={panel.readiness_status} />
      </div>
      <p>{stringValue(panel, "lineage_summary")}</p>
      <em>{stringValue(panel, "caveat")}</em>
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
      <DetailList
        rows={[
          ["Curated view", stringValue(row, "curated_view", stringValue(source, "curated_view"))],
          ["Grain", stringValue(source, "grain")],
          ["Fields", stringValue(source, "fields")],
          ["Validation", stringValue(source, "validation_rules", stringValue(row, "caveat"))],
          ["Caveat", stringValue(row, "caveat", "Synthetic readiness demonstration.")],
        ]}
      />
      <RegistryTable rows={[row]} columns={["source_view_present", "field_populated", "freshness", "row_count", "timestamp_logic", "metric_definition_approved", "small_cell_suppression"]} />
    </div>
  );
}

function MetricDrawerContent({ data, row, onOpenSource }: { data: V3Data; row: DataRow; onOpenSource: (sourceId: string) => void }) {
  const metric = data.metricRegistry.find((item) => stringValue(item, "metric_id") === stringValue(row, "metric_id"));
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Value</span>
          <strong>{stringValue(row, "value")}</strong>
        </div>
        <div>
          <span>Classification</span>
          <ClassificationBadge value={row.classification} />
        </div>
        <div>
          <span>Validation</span>
          <ReadinessBadge value={metric?.validation ?? "review"} />
        </div>
        <div>
          <span>Panel</span>
          <strong>{stringValue(row, "panel_id", "PANEL_SYSTEM_POSTURE")}</strong>
        </div>
      </div>
      <DetailList
        rows={[
          ["Metric", stringValue(row, "label", stringValue(metric, "name"))],
          ["Formula", stringValue(metric, "formula", "Synthetic aggregate calculation")],
          ["Owner", stringValue(metric, "owner", "Synthetic product owner")],
          ["Detail", stringValue(row, "detail")],
          ["Change driver", stringValue(row, "delta")],
          ["Lineage", stringValue(metric, "lineage_summary", "Direct/derived/modelled lineage is synthetic and requires local validation.")],
        ]}
      />
      <SourceChipGroup data={data} sourceIds={csvIds(row.source_ids ?? metric?.source_ids)} onOpen={onOpenSource} limit={8} />
    </div>
  );
}

function SiteDrawerContent({ data, siteId, row, onOpenSource }: { data: V3Data; siteId: string; row?: DataRow; onOpenSource: (sourceId: string) => void }) {
  const site = row ?? data.commandCenter.sites.find((item) => stringValue(item, "site_id") === siteId);
  const units = data.inpatient.unitDetails.filter((item) => siteId === "All sites" || stringValue(item, "site_id") === siteId);
  const programs = data.ambulatory.programDetails.filter((item) => siteId === "All sites" || stringValue(item, "site_id") === siteId);
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Occupancy</span>
          <strong>{formatPct(numberValue(site, "occupancy_pct", sumRows(units, "census") / Math.max(1, sumRows(units, "effective_beds"))))}</strong>
        </div>
        <div>
          <span>ED boarders</span>
          <strong>{formatInteger(numberValue(site, "ed_boarders", sumRows(units, "ed_boarders")))}</strong>
        </div>
        <div>
          <span>Waitlist</span>
          <strong>{formatCompact(numberValue(site, "waitlist_total", sumRows(programs, "waitlist_total")))}</strong>
        </div>
        <div>
          <span>Resource</span>
          <strong>${numberValue(site, "resource_pressure_k").toFixed(1)}k</strong>
        </div>
      </div>
      <DetailList
        rows={[
          ["Catchment", stringValue(site, "catchment", siteLabel(siteId))],
          ["Units in lens", units.length],
          ["Programs in lens", programs.length],
          ["HR gap hours", `${formatInteger(numberValue(site, "hr_gap_hours", sumRows(units, "staffing_gap_hours")))}h`],
          ["Caveat", "Synthetic aggregate command-centre site summary."],
        ]}
      />
      <SourceChipGroup data={data} sourceIds={csvIds(site?.source_ids)} onOpen={onOpenSource} limit={8} />
    </div>
  );
}

function UnitDrawerContent({ data, unitId, onOpenSource, onOpenModel }: { data: V3Data; unitId: string; onOpenSource: (sourceId: string) => void; onOpenModel: (assetId: string) => void }) {
  const unit = data.inpatient.unitDetails.find((row) => stringValue(row, "unit_id") === unitId);
  if (!unit) return <p className="muted">Unit record not found for the current synthetic data lens.</p>;
  const timeline = data.inpatient.unitTimeline.filter((row) => stringValue(row, "unit_id") === unitId);
  const warnings = data.inpatient.warnings.filter((row) => stringValue(row, "unit_id") === unitId);
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Capacity</span>
          <strong>{numberValue(unit, "census")} / {numberValue(unit, "effective_beds")}</strong>
        </div>
        <div>
          <span>ED boarders</span>
          <strong>{formatInteger(numberValue(unit, "ed_boarders"))}</strong>
        </div>
        <div>
          <span>Predicted 24h</span>
          <strong>{formatInteger(numberValue(unit, "predicted_admissions_24h"))} in / {formatInteger(numberValue(unit, "predicted_discharges_24h"))} out</strong>
        </div>
        <div>
          <span>Readiness</span>
          <ReadinessBadge value={unit.source_readiness} />
        </div>
      </div>
      <DetailList
        rows={[
          ["Site", stringValue(unit, "site_name")],
          ["Service", stringValue(unit, "service_line")],
          ["Physical/staffed/effective beds", `${numberValue(unit, "physical_beds")} / ${numberValue(unit, "staffed_beds")} / ${numberValue(unit, "effective_beds")}`],
          ["Transfers", `${numberValue(unit, "transfer_in_requests")} in / ${numberValue(unit, "transfer_out_requests")} out`],
          ["Discharge barriers", numberValue(unit, "discharge_barriers")],
          ["RN required/available", `${numberValue(unit, "rn_required")} / ${numberValue(unit, "rn_available")} hours`],
          ["Allied gap", `${numberValue(unit, "allied_health_gap_hours")} hours`],
          ["Finance/resource proxy", `$${numberValue(unit, "variable_staffing_cost_k").toFixed(1)}k cost vs $${numberValue(unit, "resource_ceiling_k").toFixed(1)}k ceiling`],
          ["Open data adjustment", formatPct(numberValue(unit, "open_data_adjustment"))],
          ["Caveat", stringValue(unit, "caveat")],
        ]}
      />
      <ForecastRibbonChart rows={timeline} xKey="hour" predictionKey="predicted_occupancy" lowerKey="lower" upperKey="upper" label="Unit occupancy forecast drawer chart" height={240} />
      <div className="source-chip-row">
        {csvIds(unit.model_ids).map((modelId) => (
          <button type="button" key={modelId} className="source-chip review" onClick={() => onOpenModel(modelId)}>
            <span aria-hidden="true" />
            {modelId}
          </button>
        ))}
      </div>
      <SourceChipGroup data={data} sourceIds={csvIds(unit.source_ids)} onOpen={onOpenSource} limit={10} />
      <WarningList rows={warnings} />
    </div>
  );
}

function ProgramDrawerContent({ data, programId, context, onOpenSource, onOpenModel }: { data: V3Data; programId: string; context: AppContext; onOpenSource: (sourceId: string) => void; onOpenModel: (assetId: string) => void }) {
  const candidates = data.ambulatory.programDetails.filter((row) => stringValue(row, "program_id") === programId);
  const program = candidates.find((row) => context.site === "All sites" || stringValue(row, "site_id") === context.site) ?? candidates[0];
  if (!program) return <p className="muted">Program record not found for the current synthetic data lens.</p>;
  const timeline = data.ambulatory.programTimeline.filter((row) => stringValue(row, "program_id") === programId && (context.site === "All sites" || stringValue(row, "site_id") === context.site));
  const warnings = data.ambulatory.warnings.filter((row) => stringValue(row, "program_id") === programId && (context.site === "All sites" || stringValue(row, "site_id") === context.site));
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Referrals</span>
          <strong>{formatInteger(numberValue(program, "referrals_4w"))}</strong>
        </div>
        <div>
          <span>Waitlist</span>
          <strong>{formatInteger(numberValue(program, "waitlist_total"))}</strong>
        </div>
        <div>
          <span>TNA</span>
          <strong>{formatInteger(numberValue(program, "third_next_available_days"))}d</strong>
        </div>
        <div>
          <span>Readiness</span>
          <ReadinessBadge value={program.source_readiness} />
        </div>
      </div>
      <DetailList
        rows={[
          ["Site", stringValue(program, "site_name")],
          ["Program", stringValue(program, "program")],
          ["Triage volume", numberValue(program, "triage_volume_4w")],
          ["Urgent/routine waitlist", `${numberValue(program, "urgent_waitlist")} / ${numberValue(program, "routine_waitlist")}`],
          ["Template capacity/gap", `${numberValue(program, "template_capacity_4w")} / ${numberValue(program, "template_gap_4w")}`],
          ["No-show rate", formatPct(numberValue(program, "no_show_rate"))],
          ["Diagnostics readiness", formatPct(numberValue(program, "diagnostic_readiness"))],
          ["Provider/allied capacity", `${numberValue(program, "provider_capacity_sessions_4w")} / ${numberValue(program, "allied_health_capacity_sessions_4w")} sessions`],
          ["HR gap", `${numberValue(program, "hr_gap_sessions_4w")} sessions`],
          ["Finance/resource proxy", `$${numberValue(program, "marginal_resource_need_k").toFixed(1)}k need vs $${numberValue(program, "resource_ceiling_k").toFixed(1)}k ceiling`],
          ["Open data adjustment", formatPct(numberValue(program, "open_data_adjustment"))],
          ["Caveat", stringValue(program, "caveat")],
        ]}
      />
      <ForecastRibbonChart rows={timeline.slice(0, 26)} xKey="week" predictionKey="forecast_waitlist" lowerKey="lower" upperKey="upper" label="Program waitlist forecast drawer chart" height={240} />
      <div className="source-chip-row">
        {csvIds(program.model_ids).map((modelId) => (
          <button type="button" key={modelId} className="source-chip review" onClick={() => onOpenModel(modelId)}>
            <span aria-hidden="true" />
            {modelId}
          </button>
        ))}
      </div>
      <SourceChipGroup data={data} sourceIds={csvIds(program.source_ids)} onOpen={onOpenSource} limit={10} />
      <WarningList rows={warnings} />
    </div>
  );
}

function ModelDrawerContent({ data, assetId, onOpenSource }: { data: V3Data; assetId: string; onOpenSource: (sourceId: string) => void }) {
  const model = data.modelRegistry.find((row) => stringValue(row, "asset_id") === assetId);
  const drift = data.gatekeeper.validationDrift.find((row) => stringValue(row, "asset_id") === assetId);
  const release = data.gatekeeper.releaseRollback.find((row) => stringValue(row, "asset_id") === assetId);
  if (!model) return <p className="muted">Model card not found.</p>;
  let coefficients: Record<string, unknown> = {};
  try {
    coefficients = JSON.parse(stringValue(model, "proxy_coefficients", "{}")) as Record<string, unknown>;
  } catch {
    coefficients = {};
  }
  const coefficientRows = Object.entries(coefficients).map(([coefficient_name, default_value]) => ({ coefficient_name, default_value }));
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Governance</span>
          <ReadinessBadge value={model.governance_status} />
        </div>
        <div>
          <span>Calibration</span>
          <strong>{stringValue(model, "calibration")}</strong>
        </div>
        <div>
          <span>Drift</span>
          <strong>{stringValue(model, "drift")}</strong>
        </div>
        <div>
          <span>Alert burden</span>
          <strong>{stringValue(model, "alert_burden")}</strong>
        </div>
      </div>
      <DetailList
        rows={[
          ["Asset", stringValue(model, "asset_id")],
          ["Output type", stringValue(model, "output_type")],
          ["Source fields", stringValue(model, "source_fields")],
          ["Feature families", stringValue(model, "feature_families")],
          ["Threshold logic", stringValue(model, "threshold_logic", stringValue(model, "thresholds"))],
          ["Validation", stringValue(model, "validation")],
          ["Panels using it", stringValue(model, "panels_using_it")],
          ["Source lineage", stringValue(model, "source_lineage")],
          ["Caveats", stringValue(model, "caveats")],
          ["Rollback", stringValue(release, "rollback_trigger", stringValue(model, "rollback_plan"))],
        ]}
      />
      <SensitivityTornado rows={coefficientRows} label="Proxy coefficients" />
      <RegistryTable rows={[drift ?? {}, release ?? {}]} columns={["asset_id", "primary_metric", "primary_metric_value", "drift_status", "release_gate", "release_status"]} limit={2} />
      <SourceChipGroup data={data} sourceIds={csvIds(model.source_ids)} onOpen={onOpenSource} limit={10} />
    </div>
  );
}

function WarningDrawerContent({ data, row, onOpenSource, onOpenModel }: { data: V3Data; row: DataRow; onOpenSource: (sourceId: string) => void; onOpenModel: (assetId: string) => void }) {
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Severity</span>
          <ReadinessBadge value={row.severity} />
        </div>
        <div>
          <span>Readiness</span>
          <ReadinessBadge value={row.source_readiness} />
        </div>
        <div>
          <span>Classification</span>
          <ClassificationBadge value={row.classification} />
        </div>
        <div>
          <span>Metric</span>
          <strong>{stringValue(row, "metric_id")}</strong>
        </div>
      </div>
      <DetailList
        rows={[
          ["Warning", stringValue(row, "title", stringValue(row, "warning_id"))],
          ["Message", stringValue(row, "message")],
          ["Object", stringValue(row, "unit_name", stringValue(row, "program"))],
          ["Recommended action", stringValue(row, "recommended_action")],
          ["Caveat", "Synthetic warning logic; no clinical action and not validated for clinical decision-making."],
        ]}
      />
      <div className="source-chip-row">
        {csvIds(row.model_ids).map((modelId) => (
          <button type="button" key={modelId} className="source-chip review" onClick={() => onOpenModel(modelId)}>
            <span aria-hidden="true" />
            {modelId}
          </button>
        ))}
      </div>
      <SourceChipGroup data={data} sourceIds={csvIds(row.source_ids)} onOpen={onOpenSource} limit={8} />
    </div>
  );
}

function ScenarioDrawerContent({ data, row, onOpenSource }: { data: V3Data; row: DataRow; onOpenSource: (sourceId: string) => void }) {
  const controls = data.scenarioLab.controlRanges.filter((control) => stringValue(control, "scenario_id") === stringValue(row, "scenario_id"));
  const affectedUnits = csvIds(row.affected_units)
    .map((id) => data.inpatient.unitDetails.find((unit) => stringValue(unit, "unit_id") === id))
    .filter(Boolean) as DataRow[];
  const affectedPrograms = csvIds(row.affected_programs)
    .map((id) => data.ambulatory.programDetails.find((program) => stringValue(program, "program_id") === id))
    .filter(Boolean) as DataRow[];
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Baseline</span>
          <strong>{formatInteger(numberValue(row, "baseline_value"))}</strong>
        </div>
        <div>
          <span>Scenario</span>
          <strong>{formatInteger(numberValue(row, "scenario_value"))}</strong>
        </div>
        <div>
          <span>CI</span>
          <strong>{formatInteger(numberValue(row, "confidence_low"))}-{formatInteger(numberValue(row, "confidence_high"))}</strong>
        </div>
        <div>
          <span>Readiness</span>
          <ReadinessBadge value={row.readiness} />
        </div>
      </div>
      <DetailList
        rows={[
          ["Domain", stringValue(row, "domain")],
          ["Primary outcome", stringValue(row, "primary_outcome")],
          ["HR hours required", numberValue(row, "hr_hours_required")],
          ["Cost required", `$${numberValue(row, "cost_k_required").toFixed(1)}k`],
          ["Resource ceiling", `$${numberValue(row, "resource_ceiling_k").toFixed(1)}k`],
          ["Trade-off", stringValue(row, "tradeoff")],
          ["Writeback", stringValue(row, "writeback_table")],
        ]}
      />
      <RegistryTable rows={controls} columns={["control_id", "domain", "default_value", "unit", "impact_per_unit", "cost_k_per_unit"]} />
      <RegistryTable rows={affectedUnits} columns={["unit_name", "site_name", "occupancy_pct", "ed_boarders", "staffing_gap_hours"]} limit={6} />
      <RegistryTable rows={affectedPrograms} columns={["program", "site_name", "waitlist_total", "third_next_available_days", "hr_gap_sessions_4w"]} limit={6} />
      <SourceChipGroup data={data} sourceIds={csvIds(row.source_ids)} onOpen={onOpenSource} limit={8} />
    </div>
  );
}

function PacketDrawerContent({
  data,
  row,
  onOpenSource,
  onOpenModel,
}: {
  data: V3Data;
  row: DataRow;
  onOpenSource: (sourceId: string) => void;
  onOpenModel: (assetId: string) => void;
}) {
  const scenario = data.scenarioLab.scenarios.find((item) => stringValue(item, "scenario_id") === stringValue(row, "scenario_id"));
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Urgency</span>
          <ReadinessBadge value={row.urgency} />
        </div>
        <div>
          <span>Confidence</span>
          <strong>{stringValue(row, "confidence")}</strong>
        </div>
        <div>
          <span>Expected impact</span>
          <strong>{numberValue(row, "expected_impact").toFixed(1)}</strong>
        </div>
        <div>
          <span>Readiness</span>
          <ReadinessBadge value={row.readiness} />
        </div>
      </div>
      <DetailList
        rows={[
          ["Signal", stringValue(row, "signal")],
          ["Interpretation", stringValue(row, "interpretation")],
          ["Primary driver", stringValue(row, "primary_driver")],
          ["Now what", stringValue(row, "now_what")],
          ["Owner", stringValue(row, "owner_persona")],
          ["Huddle cadence", stringValue(row, "huddle_cadence")],
          ["Scenario", stringValue(row, "scenario_name", stringValue(scenario, "scenario_name"))],
          ["Evidence to clear", stringValue(row, "evidence_to_clear")],
          ["Safety gate", stringValue(row, "safety_gate")],
          ["Learning metric", stringValue(row, "learning_metric")],
          ["Writeback", stringValue(row, "writeback_table")],
          ["Caveat", stringValue(row, "caveat")],
        ]}
      />
      <div className="drawer-summary-grid">
        <div>
          <span>HR constraint</span>
          <strong>{stringValue(row, "hr_constraint")}</strong>
        </div>
        <div>
          <span>Finance constraint</span>
          <strong>{stringValue(row, "finance_constraint")}</strong>
        </div>
      </div>
      <div className="source-chip-row">
        {csvIds(row.model_ids).map((modelId) => (
          <button type="button" key={modelId} className="source-chip review" onClick={() => onOpenModel(modelId)}>
            <span aria-hidden="true" />
            {modelId}
          </button>
        ))}
      </div>
      <SourceChipGroup data={data} sourceIds={csvIds(row.source_ids)} onOpen={onOpenSource} limit={10} />
    </div>
  );
}

function LensDrawerContent({ row }: { row: DataRow }) {
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Priority</span>
          <strong>{formatInteger(numberValue(row, "priority"))}</strong>
        </div>
        <div>
          <span>Status</span>
          <ReadinessBadge value={row.status} />
        </div>
        <div>
          <span>Owner</span>
          <strong>{stringValue(row, "owner")}</strong>
        </div>
      </div>
      <DetailList
        rows={[
          ["Lens", stringValue(row, "lens")],
          ["Finding", stringValue(row, "finding")],
          ["Improvement added", stringValue(row, "improvement_added")],
          ["Acceptance signal", stringValue(row, "acceptance_signal")],
          ["Research inspiration", stringValue(row, "source_inspiration")],
        ]}
      />
    </div>
  );
}

function HuddleDrawerContent({ data, row, onOpenSource }: { data: V3Data; row: DataRow; onOpenSource: (sourceId: string) => void }) {
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>Cadence</span>
          <strong>{stringValue(row, "cadence")}</strong>
        </div>
        <div>
          <span>Decision window</span>
          <strong>{formatInteger(numberValue(row, "decision_window_minutes"))} min</strong>
        </div>
        <div>
          <span>Packets</span>
          <strong>{formatInteger(numberValue(row, "packets_reviewed"))}</strong>
        </div>
        <div>
          <span>Status</span>
          <ReadinessBadge value={row.status} />
        </div>
      </div>
      <DetailList
        rows={[
          ["Owner", stringValue(row, "owner")],
          ["Participants", stringValue(row, "participants")],
          ["Input objects", stringValue(row, "input_objects")],
          ["Expected outputs", stringValue(row, "expected_outputs")],
          ["Escalation triggers", stringValue(row, "escalation_triggers")],
          ["Writeback", stringValue(row, "writeback_table")],
          ["Reliability score", formatPct(numberValue(row, "reliability_score"))],
        ]}
      />
      <SourceChipGroup data={data} sourceIds={csvIds(row.source_ids)} onOpen={onOpenSource} limit={8} />
    </div>
  );
}

function EscalationDrawerContent({ data, row, onOpenSource }: { data: V3Data; row: DataRow; onOpenSource: (sourceId: string) => void }) {
  return (
    <div className="drawer-stack">
      <div className="drawer-summary-grid">
        <div>
          <span>SLA</span>
          <strong>{formatInteger(numberValue(row, "escalation_sla_minutes"))} min</strong>
        </div>
        <div>
          <span>Active packets</span>
          <strong>{formatInteger(numberValue(row, "active_packets"))}</strong>
        </div>
        <div>
          <span>Readiness</span>
          <ReadinessBadge value={row.readiness} />
        </div>
        <div>
          <span>Reliability</span>
          <strong>{formatPct(numberValue(row, "reliability_score"))}</strong>
        </div>
      </div>
      <DetailList
        rows={[
          ["Trigger", stringValue(row, "trigger")],
          ["Owner", stringValue(row, "owner")],
          ["Next action", stringValue(row, "next_action")],
          ["Safety gate", stringValue(row, "safety_gate")],
          ["Learning metric", stringValue(row, "learning_metric")],
        ]}
      />
      <SourceChipGroup data={data} sourceIds={csvIds(row.source_ids)} onOpen={onOpenSource} limit={8} />
    </div>
  );
}

function ObjectDrawer({
  data,
  drawer,
  context,
  onClose,
  setDrawer,
}: {
  data: V3Data;
  drawer: DrawerState;
  context: AppContext;
  onClose: () => void;
  setDrawer: (drawer: DrawerState) => void;
}) {
  if (!drawer) return null;
  const openSource = (sourceId: string) => setDrawer({ kind: "source", id: sourceId });
  const openModel = (assetId: string) => setDrawer({ kind: "model", id: assetId });
  const title =
    drawer.kind === "source"
      ? drawer.id
      : drawer.kind === "unit"
        ? stringValue(data.inpatient.unitDetails.find((row) => stringValue(row, "unit_id") === drawer.id), "unit_name", drawer.id)
        : drawer.kind === "program"
          ? stringValue(data.ambulatory.programDetails.find((row) => stringValue(row, "program_id") === drawer.id), "program", drawer.id)
          : drawer.kind === "model"
            ? stringValue(data.modelRegistry.find((row) => stringValue(row, "asset_id") === drawer.id), "name", drawer.id)
            : drawer.kind === "metric"
              ? stringValue(drawer.row, "label", drawer.id)
              : drawer.kind === "site"
                ? siteLabel(drawer.id)
                : drawer.kind === "scenario"
                  ? stringValue(drawer.row, "scenario_name", drawer.id)
                  : drawer.kind === "packet"
                    ? stringValue(drawer.row, "packet_name", drawer.id)
                    : drawer.kind === "lens"
                      ? stringValue(drawer.row, "lens", drawer.id)
                      : drawer.kind === "huddle"
                        ? stringValue(drawer.row, "cadence_name", drawer.id)
                        : drawer.kind === "escalation"
                          ? stringValue(drawer.row, "lane", drawer.id)
                          : stringValue(drawer.row, "title", drawer.id);
  return (
    <Drawer eyebrow={titleCase(drawer.kind)} title={title} onClose={onClose}>
      {drawer.kind === "source" && <SourceDrawerContent data={data} sourceId={drawer.id} />}
      {drawer.kind === "unit" && <UnitDrawerContent data={data} unitId={drawer.id} onOpenSource={openSource} onOpenModel={openModel} />}
      {drawer.kind === "program" && <ProgramDrawerContent data={data} programId={drawer.id} context={context} onOpenSource={openSource} onOpenModel={openModel} />}
      {drawer.kind === "model" && <ModelDrawerContent data={data} assetId={drawer.id} onOpenSource={openSource} />}
      {drawer.kind === "metric" && <MetricDrawerContent data={data} row={drawer.row} onOpenSource={openSource} />}
      {drawer.kind === "site" && <SiteDrawerContent data={data} siteId={drawer.id} row={drawer.row} onOpenSource={openSource} />}
      {drawer.kind === "warning" && <WarningDrawerContent data={data} row={drawer.row} onOpenSource={openSource} onOpenModel={openModel} />}
      {drawer.kind === "scenario" && <ScenarioDrawerContent data={data} row={drawer.row ?? { scenario_id: drawer.id }} onOpenSource={openSource} />}
      {drawer.kind === "packet" && <PacketDrawerContent data={data} row={drawer.row} onOpenSource={openSource} onOpenModel={openModel} />}
      {drawer.kind === "lens" && <LensDrawerContent row={drawer.row} />}
      {drawer.kind === "huddle" && <HuddleDrawerContent data={data} row={drawer.row} onOpenSource={openSource} />}
      {drawer.kind === "escalation" && <EscalationDrawerContent data={data} row={drawer.row} onOpenSource={openSource} />}
    </Drawer>
  );
}

function contextSummary(data: V3Data, context: AppContext): string {
  const unit = context.unit === "All units" ? "all units" : stringValue(data.inpatient.unitDetails.find((row) => stringValue(row, "unit_id") === context.unit), "unit_name", context.unit);
  const program = context.program === "All programs" ? "all programs" : stringValue(data.ambulatory.programDetails.find((row) => stringValue(row, "program_id") === context.program), "program", context.program);
  const service = context.service === "All services" ? "all services" : stringValue(data.commandCenter.serviceLines.find((row) => stringValue(row, "service_id") === context.service), "service_line", titleCase(context.service));
  const scenario = context.scenario === "All scenarios" ? "scenario-neutral" : stringValue(data.scenarioLab.scenarios.find((row) => stringValue(row, "scenario_id") === context.scenario), "scenario_name", context.scenario);
  return `${context.persona} lens | ${siteLabel(context.site)} | ${context.horizon} | ${service} | ${unit} | ${program} | ${scenario}`;
}

function roleGuidance(data: V3Data, persona: string): DataRow | undefined {
  return data.commandCenter.roleGuidance.find((row) => stringValue(row, "persona") === persona) ?? data.commandCenter.roleGuidance[0];
}

function contextInterpretations(data: V3Data, context: AppContext, limit = 4): DataRow[] {
  const rows = data.commandCenter.interpretations.filter((row) => {
    const persona = stringValue(row, "persona");
    const objectType = stringValue(row, "object_type");
    const objectId = stringValue(row, "object_id");
    const personaOk = persona === context.persona || persona === "Executive" || context.persona === "Analytics / informatics / AI team";
    const unitOk = context.unit === "All units" || objectId === context.unit || objectType !== "unit";
    const programOk = context.program === "All programs" || objectId === context.program || objectType !== "program";
    const scenarioOk = context.scenario === "All scenarios" || objectId === context.scenario || objectType !== "scenario";
    return personaOk && unitOk && programOk && scenarioOk;
  });
  return (rows.length ? rows : data.commandCenter.interpretations).slice(0, limit);
}

function RoleGuidancePanel({ data, context }: { data: V3Data; context: AppContext }) {
  const row = roleGuidance(data, context.persona);
  if (!row) return null;
  return (
    <article className="decision-support-card role-card">
      <div>
        <Users size={18} />
        <strong>{stringValue(row, "persona")}</strong>
        <ClassificationBadge value="role lens" />
      </div>
      <p>{stringValue(row, "value_question")}</p>
      <DetailList
        rows={[
          ["Primary view", stringValue(row, "primary_view")],
          ["Math alignment", stringValue(row, "math_note")],
          ["Reasonable next action", stringValue(row, "recommended_actions")],
        ]}
      />
    </article>
  );
}

function InterpretationPanel({
  data,
  context,
  onOpenSource,
  limit = 4,
}: {
  data: V3Data;
  context: AppContext;
  onOpenSource: (sourceId: string) => void;
  limit?: number;
}) {
  const rows = contextInterpretations(data, context, limit);
  if (!rows.length) return <p className="muted">No interpretation rows are available for this lens.</p>;
  return (
    <div className="interpretation-grid">
      {rows.map((row) => (
        <article className="decision-support-card" key={stringValue(row, "signal_id")}>
          <div>
            <Activity size={18} />
            <strong>{stringValue(row, "headline")}</strong>
            <ReadinessBadge value={row.confidence} />
          </div>
          <dl className="so-what-list">
            <div>
              <dt>What changed</dt>
              <dd>{stringValue(row, "what_changed")}</dd>
            </div>
            <div>
              <dt>Likely drivers</dt>
              <dd>{stringValue(row, "likely_drivers")}</dd>
            </div>
            <div>
              <dt>Now what</dt>
              <dd>{stringValue(row, "review_action")}</dd>
            </div>
            <div>
              <dt>Confidence</dt>
              <dd>{stringValue(row, "confidence_reason")}</dd>
            </div>
          </dl>
          <SourceChipGroup data={data} sourceIds={csvIds(row.source_ids)} onOpen={onOpenSource} limit={4} />
        </article>
      ))}
    </div>
  );
}

function readinessSummary(rows: DataRow[]) {
  return {
    ready: rows.filter((row) => statusTone(row.status) === "ready" || statusTone(row.synthetic_demo_status) === "ready").length,
    review: rows.filter((row) => statusTone(row.status) === "review").length,
    blocked: rows.filter((row) => statusTone(row.status) === "high" || statusTone(row.real_data_status) === "high").length,
  };
}

function actionLoopStages(data: V3Data, loopId?: string): DataRow[] {
  const rows = data.commandCenter.actionLearningLoops;
  const selectedLoop = loopId ?? stringValue(rows[0], "loop_id");
  return rows.filter((row) => stringValue(row, "loop_id") === selectedLoop).sort((a, b) => numberValue(a, "stage_index") - numberValue(b, "stage_index"));
}

function ActionLearningLoopBoard({
  data,
  loopId,
}: {
  data: V3Data;
  loopId?: string;
}) {
  const stages = actionLoopStages(data, loopId);
  if (!stages.length) return <p className="muted">No action-learning loop has been generated.</p>;
  return (
    <div className="learning-loop-board">
      {stages.map((stage) => (
        <article key={`${stringValue(stage, "loop_id")}-${stringValue(stage, "stage_id")}`}>
          <span>{numberValue(stage, "stage_index")}</span>
          <strong>{stringValue(stage, "stage_name")}</strong>
          <p>{stringValue(stage, "description")}</p>
          <em>{stringValue(stage, "status")} | {stringValue(stage, "owner")}</em>
        </article>
      ))}
    </div>
  );
}

function filteredDecisionPackets(data: V3Data, context: AppContext): DataRow[] {
  const serviceLabelValue =
    context.service === "All services"
      ? ""
      : stringValue(data.commandCenter.serviceLines.find((row) => stringValue(row, "service_id") === context.service), "service_line", context.service).toLowerCase();
  const programLabelValue =
    context.program === "All programs"
      ? ""
      : stringValue(data.commandCenter.programs.find((row) => stringValue(row, "program_id") === context.program), "program", context.program).toLowerCase();
  const rows = data.commandCenter.decisionPackets.filter((packet) => {
    const siteOk = context.site === "All sites" || stringValue(packet, "site_id") === context.site || stringValue(packet, "site_id") === "SITE_PROV_NETWORK";
    const serviceText = stringValue(packet, "service_or_program").toLowerCase();
    const serviceOk = !serviceLabelValue || serviceText.includes(serviceLabelValue);
    const programOk = !programLabelValue || serviceText.includes(programLabelValue);
    const scenarioOk = context.scenario === "All scenarios" || stringValue(packet, "scenario_id") === context.scenario;
    const personaOk =
      context.persona === "Executive" ||
      stringValue(packet, "owner_persona") === context.persona ||
      (context.persona === "Analytics / informatics / AI team" && stringValue(packet, "packet_type").includes("governance"));
    return siteOk && serviceOk && programOk && scenarioOk && personaOk;
  });
  return rows.length ? rows : data.commandCenter.decisionPackets;
}

function packetTone(packet: DataRow): Tone {
  const urgency = stringValue(packet, "urgency").toLowerCase();
  if (urgency.includes("now") || urgency.includes("hold")) return "high";
  if (urgency.includes("next") || urgency.includes("review")) return "watch";
  return "neutral";
}

function packetChartRows(rows: DataRow[]): DataRow[] {
  return rows.map((row) => ({
    packet_name: stringValue(row, "packet_name").replace(" packet", ""),
    expected_impact: numberValue(row, "expected_impact"),
    queue_pressure: numberValue(row, "queue_pressure") * 100,
  }));
}

function commandDeskKpis(data: V3Data, packets: DataRow[]): DataRow[] {
  const huddles = data.commandCenter.operatingCadence;
  const escalations = data.commandCenter.escalationLanes;
  const nowCount = packets.filter((row) => stringValue(row, "urgency").includes("Now")).length;
  const holds = packets.filter((row) => statusTone(row.readiness) === "high").length;
  return [
    {
      metric_id: "CMD_PACKET_COUNT",
      label: "Decision packets",
      value: formatInteger(packets.length),
      detail: "Signals packaged with owner, evidence, scenario, safety gate, and learning metric",
      delta: `${nowCount} now-huddle items`,
      tone: packets.length > 5 ? "watch" : "good",
      classification: "decision support",
      source_ids: "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_HR_SHIFT_ROSTER",
    },
    {
      metric_id: "CMD_GOV_HOLDS",
      label: "Governance holds",
      value: formatInteger(holds),
      detail: "Packets blocked until implementation, validation, or governance evidence clears",
      delta: holds ? "Safety gate active" : "No holds",
      tone: holds ? "high" : "good",
      classification: "governance",
      source_ids: "SRC_MODEL_VALIDATION_RESULTS,SRC_GOVERNANCE_APPROVALS",
    },
    {
      metric_id: "CMD_CADENCE_LOAD",
      label: "Cadence load",
      value: formatInteger(sumRows(huddles, "packets_reviewed")),
      detail: "Synthetic packets allocated across huddles and review boards",
      delta: `${formatInteger(avgRows(huddles, "decision_window_minutes"))} min avg window`,
      tone: "watch",
      classification: "workflow",
      source_ids: "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_WAITLIST_SNAPSHOTS",
    },
    {
      metric_id: "CMD_ESCALATION_RELIABILITY",
      label: "Escalation reliability",
      value: formatPct(avgRows(escalations, "reliability_score")),
      detail: "Prototype reliability of escalation lane ownership and feedback loops",
      delta: `${formatInteger(sumRows(escalations, "active_packets"))} active packet links`,
      tone: avgRows(escalations, "reliability_score") >= 0.75 ? "good" : "watch",
      classification: "derived",
      source_ids: "SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE,SRC_MODEL_VALIDATION_RESULTS",
    },
  ];
}

export function CommandDeskPage({
  data,
  context,
  addMemoryEvent,
}: {
  data: V3Data;
  context: AppContext;
  addMemoryEvent: (event: DataRow) => void;
}) {
  const [drawer, setDrawer] = useState<DrawerState>(null);
  const packets = useMemo(() => filteredDecisionPackets(data, context), [data, context]);
  const [selectedPacketId, setSelectedPacketId] = useState("");
  const [selectedLensId, setSelectedLensId] = useState("LENS-01");
  const selectedPacket = packets.find((packet) => stringValue(packet, "packet_id") === selectedPacketId) ?? packets[0];
  const selectedLens = data.commandCenter.expertLensReviews.find((lens) => stringValue(lens, "lens_id") === selectedLensId) ?? data.commandCenter.expertLensReviews[0];
  const kpis = useMemo(() => commandDeskKpis(data, packets), [data, packets]);

  useEffect(() => {
    if (packets.length && !packets.some((packet) => stringValue(packet, "packet_id") === selectedPacketId)) {
      setSelectedPacketId(stringValue(packets[0], "packet_id"));
    }
  }, [packets, selectedPacketId]);

  function capturePacketDecision() {
    if (!selectedPacket) return;
    addMemoryEvent({
      event_id: `LOCAL_PACKET_${Date.now()}`,
      event_type: "command_packet_review",
      app_area: "Command Desk",
      title: `${stringValue(selectedPacket, "packet_name")} reviewed`,
      narrative: `${stringValue(selectedPacket, "packet_name")} captured as a synthetic command-desk review with owner ${stringValue(selectedPacket, "owner_persona")} and follow-up window ${stringValue(selectedPacket, "follow_up_window")}.`,
      created_at: new Date().toISOString(),
      owner: stringValue(selectedPacket, "owner_persona"),
      note: `${stringValue(selectedPacket, "packet_name")} captured as a synthetic command-desk review.`,
      writeback_table: stringValue(selectedPacket, "writeback_table"),
      caveat: "Local showcase memory only; production would use governed Snowflake writeback tables.",
    });
  }

  if (!selectedPacket) {
    return (
      <section className="dashboard-grid">
        <Panel span="wide" eyebrow="Command desk" title="No decision packets generated" icon={<Workflow size={22} />}>
          <p className="section-intro">The synthetic command-centre data did not include decision packets for this build.</p>
        </Panel>
      </section>
    );
  }

  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Command operating desk" title="Signal-to-action workbench for huddles, escalation, readiness, and learning" icon={<Workflow size={22} />}>
        <p className="section-intro">
          {contextSummary(data, context)}. This page packages signals into decision packets: each packet has an owner, urgency, evidence-to-clear, scenario link, safety gate, follow-up window, and learning metric. It is synthetic demonstration data and not an operational directive.
        </p>
      </Panel>

      {kpis.map((row) => (
        <WorkspaceMetricTile
          key={stringValue(row, "metric_id")}
          label={stringValue(row, "label")}
          value={stringValue(row, "value")}
          detail={stringValue(row, "detail")}
          delta={stringValue(row, "delta")}
          tone={kpiTone(row.tone)}
          classification={stringValue(row, "classification")}
          sourceIds={csvIds(row.source_ids)}
          data={data}
          onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })}
          onClick={() => setDrawer({ kind: "metric", id: stringValue(row, "metric_id"), row })}
        />
      ))}

      <Panel span="xlarge" eyebrow="Decision packet worklist" title="What should the command centre review next?" icon={<ListChecks size={22} />}>
        <div className="packet-worklist">
          {packets.map((packet) => {
            const packetId = stringValue(packet, "packet_id");
            const selected = packetId === stringValue(selectedPacket, "packet_id");
            return (
              <button type="button" key={packetId} className={selected ? "active" : undefined} onClick={() => setSelectedPacketId(packetId)}>
                <span>
                  <strong>{stringValue(packet, "packet_name")}</strong>
                  <em>{stringValue(packet, "signal")}</em>
                </span>
                <ReadinessBadge value={packet.urgency} />
              </button>
            );
          })}
        </div>
      </Panel>

      <Panel span="normal" eyebrow="Selected packet" title={stringValue(selectedPacket, "packet_name")} icon={<FileCheck2 size={22} />}>
        <article className={`packet-detail-card ${packetTone(selectedPacket)}`}>
          <div className="packet-detail-top">
            <ReadinessBadge value={selectedPacket.urgency} />
            <ReadinessBadge value={selectedPacket.readiness} />
          </div>
          <p>{stringValue(selectedPacket, "interpretation")}</p>
          <DetailList
            rows={[
              ["Now what", stringValue(selectedPacket, "now_what")],
              ["Owner", stringValue(selectedPacket, "owner_persona")],
              ["Scenario", stringValue(selectedPacket, "scenario_name")],
              ["Safety gate", stringValue(selectedPacket, "safety_gate")],
              ["Learning metric", stringValue(selectedPacket, "learning_metric")],
            ]}
          />
          <SourceChipGroup data={data} sourceIds={csvIds(selectedPacket.source_ids)} onOpen={(sourceId) => setDrawer({ kind: "source", id: sourceId })} limit={4} />
          <div className="hero-actions compact">
            <button type="button" onClick={() => setDrawer({ kind: "packet", id: stringValue(selectedPacket, "packet_id"), row: selectedPacket })}>
              <FileCheck2 size={17} />
              Open packet evidence
            </button>
            <button type="button" onClick={capturePacketDecision}>
              <History size={17} />
              Capture review
            </button>
          </div>
        </article>
      </Panel>

      <Panel span="xlarge" eyebrow="Impact / pressure" title="Expected impact by decision packet" icon={<Activity size={22} />}>
        <HorizontalBarChart rows={packetChartRows(packets)} labelKey="packet_name" valueKey="expected_impact" label="Decision packet expected impact" />
      </Panel>

      <Panel span="normal" eyebrow="Operating cadence" title="Where packets get reviewed" icon={<CalendarClock size={22} />}>
        <HorizontalBarChart rows={data.commandCenter.operatingCadence} labelKey="cadence_name" valueKey="packets_reviewed" label="Operating cadence packet load" height={260} />
        <div className="cadence-list">
          {data.commandCenter.operatingCadence.map((row) => (
            <button type="button" key={stringValue(row, "huddle_id")} onClick={() => setDrawer({ kind: "huddle", id: stringValue(row, "huddle_id"), row })}>
              <strong>{stringValue(row, "cadence_name")}</strong>
              <span>{stringValue(row, "owner")} | {stringValue(row, "cadence")}</span>
            </button>
          ))}
        </div>
      </Panel>

      <Panel span="xlarge" eyebrow="15 expert lenses" title="World-class review board embedded into the product backlog" icon={<BrainCircuit size={22} />}>
        <div className="lens-board">
          {data.commandCenter.expertLensReviews.map((lens) => {
            const lensId = stringValue(lens, "lens_id");
            return (
              <button type="button" key={lensId} className={lensId === stringValue(selectedLens, "lens_id") ? "active" : undefined} onClick={() => setSelectedLensId(lensId)}>
                <span>{formatInteger(numberValue(lens, "priority"))}</span>
                <strong>{stringValue(lens, "lens")}</strong>
                <ReadinessBadge value={lens.status} />
              </button>
            );
          })}
        </div>
      </Panel>

      <Panel span="normal" eyebrow="Selected lens" title={stringValue(selectedLens, "lens", "Expert review")} icon={<Sparkles size={22} />}>
        <article className="decision-support-card">
          <div>
            <BrainCircuit size={18} />
            <strong>{stringValue(selectedLens, "lens")}</strong>
            <ReadinessBadge value={selectedLens.status} />
          </div>
          <dl className="so-what-list">
            <div>
              <dt>Finding</dt>
              <dd>{stringValue(selectedLens, "finding")}</dd>
            </div>
            <div>
              <dt>Improvement added</dt>
              <dd>{stringValue(selectedLens, "improvement_added")}</dd>
            </div>
            <div>
              <dt>Acceptance signal</dt>
              <dd>{stringValue(selectedLens, "acceptance_signal")}</dd>
            </div>
          </dl>
          <button type="button" className="secondary-action" onClick={() => setDrawer({ kind: "lens", id: stringValue(selectedLens, "lens_id"), row: selectedLens })}>
            Open lens detail
          </button>
        </article>
      </Panel>

      <Panel span="xlarge" eyebrow="Escalation lanes" title="When local review needs sponsorship, repair, or safety hold" icon={<AlertTriangle size={22} />}>
        <div className="escalation-lane-grid">
          {data.commandCenter.escalationLanes.map((lane) => (
            <button type="button" key={stringValue(lane, "lane_id")} onClick={() => setDrawer({ kind: "escalation", id: stringValue(lane, "lane_id"), row: lane })}>
              <span className="object-card-heading">
                <strong>{stringValue(lane, "lane")}</strong>
                <ReadinessBadge value={lane.readiness} />
              </span>
              <em>{stringValue(lane, "trigger")}</em>
              <dl>
                <div>
                  <dt>SLA</dt>
                  <dd>{formatInteger(numberValue(lane, "escalation_sla_minutes"))}m</dd>
                </div>
                <div>
                  <dt>Packets</dt>
                  <dd>{formatInteger(numberValue(lane, "active_packets"))}</dd>
                </div>
                <div>
                  <dt>Reliability</dt>
                  <dd>{formatPct(numberValue(lane, "reliability_score"))}</dd>
                </div>
              </dl>
            </button>
          ))}
        </div>
      </Panel>

      <Panel span="wide" eyebrow="Learning loop" title="How command packets become organizational learning" icon={<History size={22} />}>
        <ActionLearningLoopBoard data={data} loopId="LOOP-UNIT-PRESSURE" />
      </Panel>

      <ObjectDrawer data={data} drawer={drawer} context={context} onClose={() => setDrawer(null)} setDrawer={setDrawer} />
    </section>
  );
}

function systemKpis(data: V3Data, context: AppContext, units: DataRow[], programs: DataRow[]): DataRow[] {
  const latest = latestOpenContext(data);
  const factor = horizonFactor(context.horizon);
  const occupancy = (sumRows(units, "census") / Math.max(1, sumRows(units, "effective_beds"))) * factor;
  const boarders = sumRows(units, "ed_boarders") * factor;
  const hrGap = sumRows(units, "staffing_gap_hours") * (context.persona.includes("Unit") ? 1.08 : 1);
  const waitlist = sumRows(programs, "waitlist_total") * (context.program === "All programs" ? 1 : 0.96) * factor;
  const resource = sumRows(units, "margin_pressure_k") + sumRows(programs, "finance_pressure_k");
  const openPressure = numberValue(latest, "respiratory_activity_index") * 100 + numberValue(latest, "aqhi_max_proxy") * 2 + (latest?.school_break_flag ? 5 : 0);
  return [
    {
      metric_id: "METRIC_OCCUPANCY",
      label: "Effective occupancy",
      value: formatPct(occupancy),
      detail: "Census against staffed/effective pediatric beds in the active lens",
      delta: `${context.horizon} factor ${factor.toFixed(2)}`,
      tone: occupancy >= 1 ? "high" : occupancy >= 0.92 ? "watch" : "good",
      classification: "derived",
      source_ids: "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_BED_STATUS,SRC_SYNTH_HR_SHIFT_ROSTER",
      panel_id: "PANEL_SYSTEM_POSTURE",
    },
    {
      metric_id: "METRIC_ED_BOARDERS",
      label: "ED boarders",
      value: formatInteger(boarders),
      detail: "Synthetic admits awaiting inpatient bed assignment",
      delta: `${formatPct(numberValue(latest, "ed_wait_pressure_proxy"))} ED wait-style pressure`,
      tone: boarders > 80 ? "high" : boarders > 35 ? "watch" : "good",
      classification: "direct",
      source_ids: "SRC_SYNTH_ED_VISITS,SRC_OPEN_ED_WAIT_TIME_LOGIC",
      panel_id: "PANEL_SYSTEM_POSTURE",
    },
    {
      metric_id: "METRIC_HR_GAP_HOURS",
      label: "HR gap hours",
      value: `${formatInteger(hrGap)}h`,
      detail: "Required minus available aggregate role-group hours",
      delta: context.persona.includes("Unit") ? "Unit lens amplifies staffing detail" : "Workforce constraint active",
      tone: hrGap > 260 ? "high" : hrGap > 120 ? "watch" : "good",
      classification: "HR",
      source_ids: "SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_HR_FLOAT_POOL",
      panel_id: "PANEL_SYSTEM_POSTURE",
    },
    {
      metric_id: "METRIC_TNA",
      label: "Ambulatory backlog",
      value: formatCompact(waitlist),
      detail: "Waitlist total for visible programs and service lens",
      delta: `${formatInteger(avgRows(programs, "third_next_available_days"))}d avg TNA`,
      tone: avgRows(programs, "third_next_available_days") > 60 ? "high" : "watch",
      classification: "derived",
      source_ids: "SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_CLINIC_TEMPLATES",
      panel_id: "PANEL_SYSTEM_POSTURE",
    },
    {
      metric_id: "METRIC_FINANCE_RESOURCE_PRESSURE",
      label: "Resource pressure",
      value: `$${formatInteger(resource)}k`,
      detail: "Marginal staffing, diagnostic, template, and surge-resource proxy",
      delta: context.scenario === "All scenarios" ? "No scenario selected" : "Scenario feasibility recalculated",
      tone: resource > 140 ? "high" : "watch",
      classification: "finance",
      source_ids: "SRC_SYNTH_FINANCE_COST_CENTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE",
      panel_id: "PANEL_SYSTEM_POSTURE",
    },
    {
      metric_id: "METRIC_OPEN_CONTEXT_LIFT",
      label: "Open-context pressure",
      value: formatInteger(openPressure),
      detail: "Respiratory virus, AQHI/smoke, school calendar, population context",
      delta: `Resp ${numberValue(latest, "respiratory_activity_index").toFixed(2)} | AQHI ${numberValue(latest, "aqhi_max_proxy").toFixed(1)}`,
      tone: openPressure > 85 ? "high" : openPressure > 60 ? "watch" : "good",
      classification: "open data",
      source_ids: "SRC_OPEN_RESPIRATORY_VIRUS_DASHBOARD,SRC_OPEN_AQHI_SMOKE_CONTEXT,SRC_OPEN_SCHOOL_HOLIDAY_CALENDAR,SRC_OPEN_STATCAN_PED_POPULATION",
      panel_id: "PANEL_SYSTEM_POSTURE",
    },
  ];
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
  const [drawer, setDrawer] = useState<DrawerState>(null);
  const units = useMemo(() => filterUnits(data, context), [data, context]);
  const programs = useMemo(() => filterPrograms(data, context), [data, context]);
  const kpis = useMemo(() => systemKpis(data, context, units, programs), [context, data, programs, units]);
  const warnings = [...data.inpatient.warnings, ...data.ambulatory.warnings].filter((row) => {
    const siteOk = context.site === "All sites" || stringValue(row, "site_id") === context.site;
    const unitOk = context.unit === "All units" || stringValue(row, "unit_id") === context.unit;
    const programOk = context.program === "All programs" || stringValue(row, "program_id") === context.program;
    return siteOk && unitOk && programOk;
  });
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Pediatric command centre" title="Progression hub for today's inpatient, ambulatory, workforce, resource, and public-context pressure" icon={<Activity size={22} />}>
        <p className="section-intro">
          {contextSummary(data, context)}. Every number below is clickable and carries direct, derived, modelled, HR, finance, or open-data lineage. The active controls change the object lists, metrics, charts, warnings, and scenario narrative.
        </p>
        <div className="hero-actions">
          <button type="button" onClick={() => goTo("ops")}>
            <Workflow size={18} />
            Command desk
          </button>
          <button type="button" onClick={() => goTo("inpatient")}>
            <BedDouble size={18} />
            Inpatient objects
          </button>
          <button type="button" onClick={() => goTo("ambulatory")}>
            <CalendarClock size={18} />
            Ambulatory objects
          </button>
          <button type="button" onClick={() => goTo("scenarios")}>
            <SlidersHorizontal size={18} />
            Scenario lab
          </button>
        </div>
      </Panel>

      <Panel span="normal" eyebrow="Role value" title="Why this persona exists" icon={<Users size={22} />}>
        <RoleGuidancePanel data={data} context={context} />
      </Panel>

      <Panel span="xlarge" eyebrow="So what / now what" title="Interpretation, drivers, confidence, and review path" icon={<Sparkles size={22} />}>
        <InterpretationPanel data={data} context={context} onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })} />
      </Panel>

      {kpis.map((row) => (
        <WorkspaceMetricTile
          key={stringValue(row, "metric_id")}
          label={stringValue(row, "label")}
          value={stringValue(row, "value")}
          detail={stringValue(row, "detail")}
          delta={stringValue(row, "delta")}
          tone={kpiTone(row.tone)}
          classification={stringValue(row, "classification")}
          sourceIds={csvIds(row.source_ids)}
          data={data}
          onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })}
          onClick={() => setDrawer({ kind: "metric", id: stringValue(row, "metric_id"), row })}
        />
      ))}

      <Panel span="xlarge" eyebrow="Site objects" title="Clickable site command posture" icon={<MapPinned size={22} />}>
        <div className="object-card-grid">
          {data.commandCenter.sites.map((site) => (
            <button type="button" className="object-card" key={stringValue(site, "site_id")} onClick={() => setDrawer({ kind: "site", id: stringValue(site, "site_id"), row: site })}>
              <span className="object-card-heading">
                <strong>{stringValue(site, "site_name")}</strong>
                <ClassificationBadge value="derived" />
              </span>
              <span>{stringValue(site, "catchment")}</span>
              <dl>
                <div>
                  <dt>Occ</dt>
                  <dd>{formatPct(numberValue(site, "occupancy_pct"))}</dd>
                </div>
                <div>
                  <dt>Boarders</dt>
                  <dd>{formatInteger(numberValue(site, "ed_boarders"))}</dd>
                </div>
                <div>
                  <dt>Waitlist</dt>
                  <dd>{formatCompact(numberValue(site, "waitlist_total"))}</dd>
                </div>
                <div>
                  <dt>Resource</dt>
                  <dd>${numberValue(site, "resource_pressure_k").toFixed(1)}k</dd>
                </div>
              </dl>
            </button>
          ))}
        </div>
      </Panel>

      <Panel span="normal" eyebrow="Warnings" title="Click a warning for object-level action context" icon={<AlertTriangle size={22} />}>
        <WarningList rows={warnings} onSelect={(row) => setDrawer({ kind: "warning", id: stringValue(row, "warning_id"), row })} />
      </Panel>

      <Panel span="xlarge" eyebrow="Public context" title="Respiratory, AQHI/smoke, temperature, school/holiday context" icon={<DatabaseZap size={22} />}>
        <OpenContextChart rows={openContextRows(data)} />
      </Panel>

      <Panel span="normal" eyebrow="Unit pressure" title="Current service/unit heatmap" icon={<BedDouble size={22} />}>
        <UnitPressureHeatmap rows={units.slice(0, 10)} />
      </Panel>

      <Panel span="normal" eyebrow="Ambulatory backlog" title="Programs in the active lens" icon={<CalendarClock size={22} />}>
        <HorizontalBarChart rows={programs} labelKey="program" valueKey="waitlist_total" label="Program waitlist bars" />
      </Panel>

      <Panel span="normal" eyebrow="HR constraint" title="Workforce pressure matrix" icon={<Users size={22} />}>
        <WorkloadMatrix rows={units.slice(0, 12)} />
      </Panel>

      <Panel span="wide" eyebrow="Lakehouse footprint" title="Synthetic source-layer lakehouse behind the command centre" icon={<Layers3 size={22} />}>
        <RegistryTable rows={data.commandCenter.lakehouseTables} columns={["table", "rows", "domain"]} limit={8} />
      </Panel>

      <ObjectDrawer data={data} drawer={drawer} context={context} onClose={() => setDrawer(null)} setDrawer={setDrawer} />
    </section>
  );
}

export function FrontierInpatientPage({ data, context }: { data: V3Data; context: AppContext }) {
  const [drawer, setDrawer] = useState<DrawerState>(null);
  const units = useMemo(() => filterUnits(data, context), [data, context]);
  const timeline = aggregateInpatientTimeline(filteredTimeline(data.inpatient.unitTimeline, units, "unit_id"), context, data);
  const warnings = data.inpatient.warnings.filter((row) => {
    const siteOk = context.site === "All sites" || stringValue(row, "site_id") === context.site;
    const serviceOk = context.service === "All services" || stringValue(row, "service_id") === context.service;
    const unitOk = context.unit === "All units" || stringValue(row, "unit_id") === context.unit;
    return siteOk && serviceOk && unitOk;
  });
  const metricRows = [
    {
      metric_id: "METRIC_OCCUPANCY",
      label: "Visible occupancy",
      value: formatPct(sumRows(units, "census") / Math.max(1, sumRows(units, "effective_beds"))),
      detail: `${units.length} units in active site/service/unit lens`,
      delta: `${formatInteger(sumRows(units, "predicted_admissions_24h"))} predicted admits`,
      tone: "watch",
      classification: "derived",
      source_ids: "SRC_SYNTH_UNIT_CENSUS_HOURLY,SRC_SYNTH_HR_SHIFT_ROSTER",
      panel_id: "PANEL_INPATIENT_COMMAND",
    },
    {
      metric_id: "METRIC_ED_BOARDERS",
      label: "ED boarders",
      value: formatInteger(sumRows(units, "ed_boarders")),
      detail: "Admission decisions awaiting pediatric bed placement",
      delta: `${formatInteger(sumRows(units, "transfer_in_requests"))} transfer-in requests`,
      tone: sumRows(units, "ed_boarders") > 45 ? "high" : "watch",
      classification: "direct",
      source_ids: "SRC_SYNTH_ED_VISITS,SRC_SYNTH_TRANSFER_REQUESTS,SRC_OPEN_ED_WAIT_TIME_LOGIC",
      panel_id: "PANEL_INPATIENT_COMMAND",
    },
    {
      metric_id: "METRIC_HR_GAP_HOURS",
      label: "HR and allied gap",
      value: `${formatInteger(sumRows(units, "staffing_gap_hours") + sumRows(units, "allied_health_gap_hours"))}h`,
      detail: "RN, allied, and effective-bed constraint proxy",
      delta: `${formatInteger(sumRows(units, "effective_beds_lost"))} effective beds lost`,
      tone: "watch",
      classification: "HR",
      source_ids: "SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_HR_FLOAT_POOL",
      panel_id: "PANEL_INPATIENT_COMMAND",
    },
    {
      metric_id: "METRIC_FINANCE_RESOURCE_PRESSURE",
      label: "Resource pressure",
      value: `$${sumRows(units, "margin_pressure_k").toFixed(1)}k`,
      detail: "Variable staffing and constrained resource proxy",
      delta: `$${sumRows(units, "variable_staffing_cost_k").toFixed(1)}k variable cost`,
      tone: "watch",
      classification: "finance",
      source_ids: "SRC_SYNTH_FINANCE_COST_CENTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE",
      panel_id: "PANEL_INPATIENT_COMMAND",
    },
  ];
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Inpatient progression hub" title="Service and unit objects with capacity, flow, HR, finance, warnings, and source readiness" icon={<BedDouble size={22} />}>
        <p className="section-intro">{contextSummary(data, context)}. Select a unit or click any card to open the operational drawer.</p>
        <LineageCard data={data} panelId="PANEL_INPATIENT_COMMAND" />
      </Panel>

      <Panel span="wide" eyebrow="Decision support" title="What is changing, why it may matter, and what to review" icon={<Sparkles size={22} />}>
        <InterpretationPanel data={data} context={context} onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })} limit={3} />
      </Panel>

      {metricRows.map((row) => (
        <WorkspaceMetricTile
          key={stringValue(row, "metric_id")}
          label={stringValue(row, "label")}
          value={stringValue(row, "value")}
          detail={stringValue(row, "detail")}
          delta={stringValue(row, "delta")}
          tone={kpiTone(row.tone)}
          classification={stringValue(row, "classification")}
          sourceIds={csvIds(row.source_ids)}
          data={data}
          onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })}
          onClick={() => setDrawer({ kind: "metric", id: stringValue(row, "metric_id"), row })}
        />
      ))}

      <Panel span="xlarge" eyebrow="Unit objects" title={`${units.length} clickable units in this lens`} icon={<ListChecks size={22} />}>
        <UnitDrilldownBoard rows={units} onSelect={(unitId) => setDrawer({ kind: "unit", id: unitId })} />
      </Panel>
      <Panel span="normal" eyebrow="Warnings" title="Unit warnings and actions" icon={<AlertTriangle size={22} />}>
        <WarningList rows={warnings} onSelect={(row) => setDrawer({ kind: "warning", id: stringValue(row, "warning_id"), row })} />
      </Panel>
      <Panel span="xlarge" eyebrow="Forecast" title="Baseline plus open-context adjusted occupancy forecast" icon={<Activity size={22} />}>
        <ForecastRibbonChart rows={timeline} xKey="hour" predictionKey="predicted_occupancy" lowerKey="lower" upperKey="upper" label="Inpatient occupancy forecast" />
      </Panel>
      <Panel span="normal" eyebrow="Heatmap" title="Occupancy, staffing gap, ED boarders" icon={<GaugeIcon />}>
        <UnitPressureHeatmap rows={units.slice(0, 12)} />
      </Panel>
      <Panel span="normal" eyebrow="Flow" title="ED-to-inpatient bottleneck network" icon={<Workflow size={22} />}>
        <FlowSankey rows={units} />
      </Panel>
      <Panel span="normal" eyebrow="Discharge" title="Barrier funnel" icon={<FileCheck2 size={22} />}>
        <DischargeFunnel rows={barrierRows(units)} />
      </Panel>
      <Panel span="normal" eyebrow="Workforce" title="Effective beds lost vs workload" icon={<Users size={22} />}>
        <WorkloadMatrix rows={units.slice(0, 12)} />
      </Panel>
      <Panel span="normal" eyebrow="Boarders" title="ED boarders by unit" icon={<AlertTriangle size={22} />}>
        <HorizontalBarChart rows={units} labelKey="unit_name" valueKey="ed_boarders" label="ED boarders by unit" />
      </Panel>
      <Panel span="normal" eyebrow="Finance" title="Variable staffing cost proxy" icon={<DollarSign size={22} />}>
        <HorizontalBarChart rows={units} labelKey="unit_name" valueKey="variable_staffing_cost_k" label="Variable staffing cost proxy" />
      </Panel>
      <Panel span="normal" eyebrow="Open context" title="Public context affecting forecasts" icon={<DatabaseZap size={22} />}>
        <OpenContextChart rows={openContextRows(data)} />
      </Panel>
      <Panel span="wide" eyebrow="Source readiness" title="Major inpatient sources behind this lens" icon={<ShieldCheck size={22} />}>
        <SourceReadinessTable rows={data.directLinkValidation.filter((row) => csvIds(units[0]?.source_ids).includes(stringValue(row, "source_id")))} limit={12} onSelect={(sourceId) => setDrawer({ kind: "source", id: sourceId })} />
      </Panel>
      <ObjectDrawer data={data} drawer={drawer} context={context} onClose={() => setDrawer(null)} setDrawer={setDrawer} />
    </section>
  );
}

function GaugeIcon() {
  return <Activity size={22} />;
}

export function FrontierAmbulatoryPage({ data, context }: { data: V3Data; context: AppContext }) {
  const [drawer, setDrawer] = useState<DrawerState>(null);
  const programs = useMemo(() => filterPrograms(data, context), [data, context]);
  const timeline = aggregateProgramTimeline(filteredTimeline(data.ambulatory.programTimeline, programs, "program_id"), context, data);
  const warnings = data.ambulatory.warnings.filter((row) => {
    const siteOk = context.site === "All sites" || stringValue(row, "site_id") === context.site;
    const programOk = context.program === "All programs" || stringValue(row, "program_id") === context.program;
    return siteOk && programOk;
  });
  const metricRows = [
    {
      metric_id: "METRIC_WAITLIST_PRESSURE",
      label: "Visible waitlist",
      value: formatCompact(sumRows(programs, "waitlist_total")),
      detail: `${programs.length} program-site objects in active lens`,
      delta: `${formatInteger(sumRows(programs, "urgent_waitlist"))} urgent waitlist`,
      tone: "watch",
      classification: "derived",
      source_ids: "SRC_SYNTH_WAITLIST_SNAPSHOTS,SRC_SYNTH_REFERRALS,SRC_SYNTH_REFERRAL_TRIAGE",
      panel_id: "PANEL_AMBULATORY_COMMAND",
    },
    {
      metric_id: "METRIC_TNA",
      label: "Average TNA",
      value: `${formatInteger(avgRows(programs, "third_next_available_days"))}d`,
      detail: "Third-next-available proxy from template capacity",
      delta: `${formatInteger(sumRows(programs, "template_gap_4w"))} template gap`,
      tone: avgRows(programs, "third_next_available_days") > 60 ? "high" : "watch",
      classification: "derived",
      source_ids: "SRC_SYNTH_CLINIC_TEMPLATES,SRC_SYNTH_PROVIDER_AVAILABILITY",
      panel_id: "PANEL_AMBULATORY_COMMAND",
    },
    {
      metric_id: "METRIC_DIAGNOSTIC_READINESS",
      label: "Diagnostics readiness",
      value: formatPct(avgRows(programs, "diagnostic_readiness")),
      detail: "Diagnostic precondition readiness for visits and follow-up",
      delta: `${formatInteger(sumRows(programs, "followup_overdue"))} overdue follow-ups`,
      tone: avgRows(programs, "diagnostic_readiness") < 0.68 ? "high" : "watch",
      classification: "direct",
      source_ids: "SRC_SYNTH_DIAGNOSTIC_READINESS,SRC_SYNTH_OVERDUE_FOLLOWUP",
      panel_id: "PANEL_AMBULATORY_COMMAND",
    },
    {
      metric_id: "METRIC_FINANCE_RESOURCE_PRESSURE",
      label: "Resource pressure",
      value: `$${sumRows(programs, "finance_pressure_k").toFixed(1)}k`,
      detail: "Provider, allied-health, diagnostics, and template resource proxy",
      delta: `${formatInteger(sumRows(programs, "hr_gap_sessions_4w"))} HR gap sessions`,
      tone: "watch",
      classification: "finance",
      source_ids: "SRC_SYNTH_HR_SHIFT_ROSTER,SRC_SYNTH_FINANCE_RESOURCE_ENVELOPE",
      panel_id: "PANEL_AMBULATORY_COMMAND",
    },
  ];
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Ambulatory access command centre" title="Program objects with referrals, triage, waitlists, TNA, templates, diagnostics, HR, finance, and source readiness" icon={<CalendarClock size={22} />}>
        <p className="section-intro">{contextSummary(data, context)}. The service control acts as a program lens when there is a natural pediatric progression relationship.</p>
        <LineageCard data={data} panelId="PANEL_AMBULATORY_COMMAND" />
      </Panel>

      <Panel span="wide" eyebrow="Decision support" title="Access interpretation, drivers, confidence, and review path" icon={<Sparkles size={22} />}>
        <InterpretationPanel data={data} context={context} onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })} limit={3} />
      </Panel>

      {metricRows.map((row) => (
        <WorkspaceMetricTile
          key={stringValue(row, "metric_id")}
          label={stringValue(row, "label")}
          value={stringValue(row, "value")}
          detail={stringValue(row, "detail")}
          delta={stringValue(row, "delta")}
          tone={kpiTone(row.tone)}
          classification={stringValue(row, "classification")}
          sourceIds={csvIds(row.source_ids)}
          data={data}
          onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })}
          onClick={() => setDrawer({ kind: "metric", id: stringValue(row, "metric_id"), row })}
        />
      ))}

      <Panel span="xlarge" eyebrow="Program objects" title={`${programs.length} clickable program-site objects in this lens`} icon={<ListChecks size={22} />}>
        <ProgramDrilldownBoard rows={programs} onSelect={(programId) => setDrawer({ kind: "program", id: programId })} />
      </Panel>
      <Panel span="normal" eyebrow="Warnings" title="Program warnings and actions" icon={<AlertTriangle size={22} />}>
        <WarningList rows={warnings} onSelect={(row) => setDrawer({ kind: "warning", id: stringValue(row, "warning_id"), row })} />
      </Panel>
      <Panel span="xlarge" eyebrow="Forecast" title="Baseline plus open-context adjusted waitlist forecast" icon={<Activity size={22} />}>
        <ForecastRibbonChart rows={timeline} xKey="week" predictionKey="forecast_waitlist" lowerKey="lower" upperKey="upper" label="Ambulatory waitlist forecast" />
      </Panel>
      <Panel span="normal" eyebrow="Access heatmap" title="TNA by program and week" icon={<CalendarClock size={22} />}>
        <AccessCalendarHeatmap rows={filteredTimeline(data.ambulatory.programTimeline, programs, "program_id")} />
      </Panel>
      <Panel span="normal" eyebrow="Waitlist" title="Waitlist by program" icon={<Users size={22} />}>
        <HorizontalBarChart rows={programs} labelKey="program" valueKey="waitlist_total" label="Waitlist by program" />
      </Panel>
      <Panel span="normal" eyebrow="TNA" title="Third-next-available by program" icon={<Activity size={22} />}>
        <HorizontalBarChart rows={programs} labelKey="program" valueKey="third_next_available_days" label="TNA by program" />
      </Panel>
      <Panel span="normal" eyebrow="Diagnostics" title="Diagnostic readiness by program" icon={<FileCheck2 size={22} />}>
        <HorizontalBarChart rows={programs} labelKey="program" valueKey="diagnostic_readiness" label="Diagnostic readiness by program" />
      </Panel>
      <Panel span="normal" eyebrow="No-show frontier" title="Recovered-slot opportunity" icon={<Sparkles size={22} />}>
        <ScenarioFrontier rows={data.ambulatory.noShowFrontier.filter((row) => programs.some((program) => stringValue(program, "program_id") === stringValue(row, "program_id")))} outcomeKey="recovered_slots" label="No-show opportunity frontier" />
      </Panel>
      <Panel span="normal" eyebrow="Provider capacity" title="Provider sessions by program" icon={<Users size={22} />}>
        <HorizontalBarChart rows={programs} labelKey="program" valueKey="provider_capacity_sessions_4w" label="Provider capacity by program" />
      </Panel>
      <Panel span="normal" eyebrow="Resource" title="Marginal resource need" icon={<DollarSign size={22} />}>
        <HorizontalBarChart rows={programs} labelKey="program" valueKey="marginal_resource_need_k" label="Marginal resource need" />
      </Panel>
      <Panel span="normal" eyebrow="Open context" title="Public context changing access assumptions" icon={<DatabaseZap size={22} />}>
        <OpenContextChart rows={openContextRows(data)} />
      </Panel>
      <ObjectDrawer data={data} drawer={drawer} context={context} onClose={() => setDrawer(null)} setDrawer={setDrawer} />
    </section>
  );
}

export function PredictiveAssetsPage({ data, context }: { data: V3Data; context: AppContext }) {
  const [drawer, setDrawer] = useState<DrawerState>(null);
  const unitModels = new Set(filterUnits(data, context).flatMap((row) => csvIds(row.model_ids)));
  const programModels = new Set(filterPrograms(data, context).flatMap((row) => csvIds(row.model_ids)));
  const visibleModels = data.modelRegistry.filter((model) => {
    if (context.service === "All services" && context.program === "All programs" && context.unit === "All units") return true;
    const id = stringValue(model, "asset_id");
    return unitModels.has(id) || programModels.has(id) || stringValue(model, "domain").toLowerCase().includes("operational");
  });
  const validationRows = data.gatekeeper.validationDrift.filter((row) => visibleModels.some((model) => stringValue(model, "asset_id") === stringValue(row, "asset_id")));
  const alertRows = visibleModels.map((model, index) => ({
    asset_id: stringValue(model, "asset_id"),
    name: stringValue(model, "name"),
    alert_burden_count: Number.parseInt(stringValue(model, "alert_burden").match(/\d+/)?.[0] ?? String(index + 2), 10),
  }));
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Predictive asset layer" title="Clickable model cards with wiring, coefficients, thresholds, validation, drift, alert burden, and lineage" icon={<BrainCircuit size={22} />}>
        <p className="section-intro">{contextSummary(data, context)}. Model cards are not static descriptions; open one to inspect sources, proxy coefficients, thresholds, validation, drift, panels using it, caveats, and rollback.</p>
        <LineageCard data={data} panelId="PANEL_PREDICTIVE_ASSETS" />
      </Panel>
      <Panel span="xlarge" eyebrow="Model cards" title={`${visibleModels.length} contextual assets`} icon={<BrainCircuit size={22} />}>
        <ModelCardGrid rows={visibleModels} onSelect={(assetId) => setDrawer({ kind: "model", id: assetId })} />
      </Panel>
      <Panel span="normal" eyebrow="Alert burden" title="Expected aggregate alerts/week" icon={<AlertTriangle size={22} />}>
        <HorizontalBarChart rows={alertRows} labelKey="asset_id" valueKey="alert_burden_count" label="Model alert burden" />
      </Panel>
      <Panel span="normal" eyebrow="Validation" title="Primary metric by model" icon={<FileCheck2 size={22} />}>
        <HorizontalBarChart rows={validationRows} labelKey="asset_id" valueKey="primary_metric_value" label="Validation metric values" />
      </Panel>
      <Panel span="normal" eyebrow="Sensitivity" title="Synthetic coefficients under review" icon={<SlidersHorizontal size={22} />}>
        <SensitivityTornado rows={data.gatekeeper.coefficients} label="Coefficient sensitivity" />
      </Panel>
      <Panel span="wide" eyebrow="Source readiness" title="Model and feature-store source stoplights" icon={<DatabaseZap size={22} />}>
        <SourceReadinessTable rows={data.directLinkValidation.filter((row) => stringValue(row, "source_domain").includes("model") || stringValue(row, "source_domain").includes("open data") || stringValue(row, "source_domain").includes("staffing"))} limit={18} onSelect={(sourceId) => setDrawer({ kind: "source", id: sourceId })} />
      </Panel>
      <ObjectDrawer data={data} drawer={drawer} context={context} onClose={() => setDrawer(null)} setDrawer={setDrawer} />
    </section>
  );
}

function selectedScenario(data: V3Data, context: AppContext): DataRow {
  if (context.scenario !== "All scenarios") {
    return data.scenarioLab.scenarios.find((row) => stringValue(row, "scenario_id") === context.scenario) ?? data.scenarioLab.scenarios[0] ?? {};
  }
  return data.scenarioLab.scenarios[0] ?? {};
}

export function ScenarioLabPage({
  data,
  context,
  addMemoryEvent,
}: {
  data: V3Data;
  context: AppContext;
  addMemoryEvent: (event: DataRow) => void;
}) {
  const [drawer, setDrawer] = useState<DrawerState>(null);
  const scenario = selectedScenario(data, context);
  const controlsForScenario = data.scenarioLab.controlRanges.filter((control) => {
    if (context.scenario === "All scenarios") return true;
    return stringValue(control, "scenario_id") === context.scenario || stringValue(control, "domain") === stringValue(scenario, "domain");
  });
  const [controlValues, setControlValues] = useState<Record<string, number>>({});
  const [toggles, setToggles] = useState({
    respiratory: true,
    smoke: true,
    school: true,
    hrConstraint: true,
    financeConstraint: true,
  });
  const [hrCapacity, setHrCapacity] = useState(90);
  const [financeBudget, setFinanceBudget] = useState(120);

  useEffect(() => {
    setControlValues((current) => {
      const next = { ...current };
      for (const control of data.scenarioLab.controlRanges) {
        const id = stringValue(control, "control_id");
        if (!(id in next)) next[id] = numberValue(control, "default_value");
      }
      return next;
    });
  }, [data.scenarioLab.controlRanges]);

  function updateControl(id: string, value: number) {
    setControlValues((current) => ({ ...current, [id]: value }));
  }

  const latest = latestOpenContext(data);
  const baseline = numberValue(scenario, "baseline_value", 320);
  const defaultScenario = numberValue(scenario, "scenario_value", baseline * 0.8);
  const rawImpact = controlsForScenario.reduce((total, control) => {
    const id = stringValue(control, "control_id");
    const current = controlValues[id] ?? numberValue(control, "default_value");
    const delta = current - numberValue(control, "default_value");
    return total + delta * numberValue(control, "impact_per_unit");
  }, baseline - defaultScenario);
  const openFactor =
    (toggles.respiratory ? numberValue(latest, "respiratory_activity_index") * 0.08 : 0) +
    (toggles.smoke ? numberValue(latest, "aqhi_max_proxy") * 0.008 : 0) +
    (toggles.school && latest?.school_break_flag ? 0.05 : 0);
  const hrRequired = numberValue(scenario, "hr_hours_required", 60) + controlsForScenario.reduce((total, control) => total + Math.max(0, (controlValues[stringValue(control, "control_id")] ?? numberValue(control, "default_value")) - numberValue(control, "default_value")) * 0.38, 0);
  const costRequired = numberValue(scenario, "cost_k_required", 40) + controlsForScenario.reduce((total, control) => total + Math.max(0, (controlValues[stringValue(control, "control_id")] ?? numberValue(control, "default_value")) - numberValue(control, "default_value")) * numberValue(control, "cost_k_per_unit") * 0.18, 0);
  const hrConstraint = toggles.hrConstraint ? Math.min(1, hrCapacity / Math.max(1, hrRequired)) : 1;
  const financeConstraint = toggles.financeConstraint ? Math.min(1, financeBudget / Math.max(1, costRequired)) : 1;
  const constraintFactor = Math.min(hrConstraint, financeConstraint);
  const impact = Math.max(0, rawImpact * (1 + openFactor) * constraintFactor);
  const scenarioValue = Math.max(0, baseline - impact);
  const ciLow = Math.max(0, scenarioValue - Math.max(8, impact * 0.18));
  const ciHigh = scenarioValue + Math.max(10, impact * 0.24);
  const affectedUnits = csvIds(scenario.affected_units)
    .map((id) => data.inpatient.unitDetails.find((row) => stringValue(row, "unit_id") === id))
    .filter(Boolean) as DataRow[];
  const affectedPrograms = csvIds(scenario.affected_programs)
    .map((id) => data.ambulatory.programDetails.find((row) => stringValue(row, "program_id") === id))
    .filter(Boolean) as DataRow[];
  const sensitivityRows = controlsForScenario.map((control) => ({
    coefficient_name: stringValue(control, "control_id"),
    default_value: Math.abs((controlValues[stringValue(control, "control_id")] ?? numberValue(control, "default_value")) * numberValue(control, "impact_per_unit")) / 100,
  }));

  function storeScenarioRun() {
    addMemoryEvent({
      event_id: `EVT-SCN-${Date.now()}`,
      event_type: "scenario_run",
      created_at: new Date().toISOString(),
      created_by: "showcase_local_user",
      app_area: "Scenario Lab",
      site_id: context.site,
      unit_or_program: context.unit !== "All units" ? context.unit : context.program,
      related_ids: stringValue(scenario, "scenario_id"),
      related_scenario_id: stringValue(scenario, "scenario_id"),
      status: "captured locally",
      severity: constraintFactor < 0.85 ? "medium" : "low",
      note: `Baseline ${formatInteger(baseline)} to scenario ${formatInteger(scenarioValue)} with HR ${formatInteger(hrCapacity)} and finance $${formatInteger(financeBudget)}k.`,
      payload_json: JSON.stringify({ synthetic_demo: true, controlValues, toggles }),
      synthetic_demo_flag: true,
      writeback_table: "APP.SCENARIO_RUN_LOG",
    });
  }

  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Interactive scenario lab" title="Baseline-vs-scenario workspace with inpatient, ambulatory, HR, finance, and open-data constraints" icon={<SlidersHorizontal size={22} />}>
        <p className="section-intro">
          {contextSummary(data, context)}. Sliders change the outcome immediately; toggles decide whether respiratory, AQHI/smoke, calendar, HR, and finance constraints are applied.
        </p>
        <LineageCard data={data} panelId="PANEL_SCENARIO_WORKSPACE" />
      </Panel>

      <Panel span="xlarge" eyebrow="Controls" title={`${stringValue(scenario, "scenario_name", "All scenario anchors")} controls`} icon={<SlidersHorizontal size={22} />}>
        <div className="scenario-control-grid">
          {controlsForScenario.slice(0, 10).map((control) => {
            const id = stringValue(control, "control_id");
            const value = controlValues[id] ?? numberValue(control, "default_value");
            return (
              <label className="slider-control" key={id}>
                <span>
                  <strong>{titleCase(id)}</strong>
                  <em>
                    {value}
                    {stringValue(control, "unit") ? ` ${stringValue(control, "unit")}` : ""}
                  </em>
                </span>
                <input
                  type="range"
                  min={numberValue(control, "min_value")}
                  max={numberValue(control, "max_value")}
                  value={value}
                  onChange={(event) => updateControl(id, Number(event.target.value))}
                />
              </label>
            );
          })}
        </div>
        <div className="toggle-grid">
          {[
            ["respiratory", "Respiratory context"],
            ["smoke", "AQHI/smoke context"],
            ["school", "School/holiday calendar"],
            ["hrConstraint", "HR capacity constraint"],
            ["financeConstraint", "Finance/resource cap"],
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
            <strong>Available HR hours</strong>
            <em>{hrCapacity}</em>
          </span>
          <input type="range" min={20} max={220} value={hrCapacity} onChange={(event) => setHrCapacity(Number(event.target.value))} />
        </label>
        <label className="slider-control compact">
          <span>
            <strong>Finance cap</strong>
            <em>${financeBudget}k</em>
          </span>
          <input type="range" min={20} max={260} step={5} value={financeBudget} onChange={(event) => setFinanceBudget(Number(event.target.value))} />
        </label>
        <button className="primary-action" onClick={storeScenarioRun}>
          <Plus size={18} />
          Capture what-if
        </button>
      </Panel>

      <Panel span="xlarge" eyebrow="Baseline vs scenario" title="Live outcome comparison with confidence interval" icon={<GitBranch size={22} />}>
        <div className="comparison-board">
          <article>
            <span>{titleCase(stringValue(scenario, "primary_outcome", "primary outcome"))}</span>
            <div className="comparison-bars">
              <div>
                <em>Baseline</em>
                <strong>{formatInteger(baseline)}</strong>
                <progress max={baseline} value={baseline} />
              </div>
              <div>
                <em>Scenario</em>
                <strong>{formatInteger(scenarioValue)}</strong>
                <progress max={baseline} value={scenarioValue} />
              </div>
            </div>
          </article>
          <article>
            <span>Confidence interval</span>
            <strong>{formatInteger(ciLow)} to {formatInteger(ciHigh)}</strong>
            <p>Open-data lift {formatPct(openFactor)}; HR constraint {formatPct(hrConstraint)}; finance constraint {formatPct(financeConstraint)}.</p>
          </article>
          <article className="improvement-card">
            <span>Improvement</span>
            <strong>{formatInteger(impact)}</strong>
            <p>{constraintFactor < 1 ? "Constrained by HR or finance. Increase capacity to unlock more impact." : "Within active HR and finance constraints."}</p>
          </article>
        </div>
      </Panel>

      <Panel span="normal" eyebrow="Scenario anchors" title="Click a scenario for trade-offs and affected objects" icon={<Sparkles size={22} />}>
        <ScenarioFrontier rows={data.scenarioLab.scenarios} outcomeKey="outcome_value" label="Scenario frontier" />
      </Panel>
      <Panel span="normal" eyebrow="Sensitivity" title="Control sensitivity" icon={<SlidersHorizontal size={22} />}>
        <SensitivityTornado rows={sensitivityRows} label="Scenario sensitivity tornado" />
      </Panel>
      <Panel span="normal" eyebrow="Affected units" title="Units most exposed to selected scenario" icon={<BedDouble size={22} />}>
        <HorizontalBarChart rows={affectedUnits} labelKey="unit_name" valueKey="ed_boarders" label="Affected unit boarders" />
      </Panel>
      <Panel span="normal" eyebrow="Affected programs" title="Programs most exposed to selected scenario" icon={<CalendarClock size={22} />}>
        <HorizontalBarChart rows={affectedPrograms} labelKey="program" valueKey="waitlist_total" label="Affected program waitlists" />
      </Panel>
      <Panel span="normal" eyebrow="Open context" title="Public-context assumptions" icon={<DatabaseZap size={22} />}>
        <OpenContextChart rows={openContextRows(data)} />
      </Panel>
      <Panel span="wide" eyebrow="Scenario table" title="Readiness, writeback path, and clickable scenario drawers" icon={<FileCheck2 size={22} />}>
        <RegistryTable rows={data.scenarioLab.scenarios} columns={["scenario_id", "domain", "scenario_name", "readiness", "classification", "writeback_table"]} limit={10} onSelect={(row) => setDrawer({ kind: "scenario", id: stringValue(row, "scenario_id"), row })} />
      </Panel>
      <Panel span="wide" eyebrow="Action and learning loop" title="Detection to review to action to follow-up to learning" icon={<Workflow size={22} />}>
        <ActionLearningLoopBoard data={data} loopId="LOOP-UNIT-PRESSURE" />
      </Panel>
      <ObjectDrawer data={data} drawer={drawer} context={context} onClose={() => setDrawer(null)} setDrawer={setDrawer} />
    </section>
  );
}

export function ImplementationReadinessPage({ data, context }: { data: V3Data; context: AppContext }) {
  const [category, setCategory] = useState("all");
  const [drawer, setDrawer] = useState<DrawerState>(null);
  const rows = data.commandCenter.implementationReadiness;
  const filtered = category === "all" ? rows : rows.filter((row) => stringValue(row, "category") === category);
  const categories = Array.from(new Set(rows.map((row) => stringValue(row, "category"))));
  const summary = readinessSummary(rows);
  const blocked = rows.filter((row) => statusTone(row.status) === "high" || statusTone(row.real_data_status) === "high");
  const readySynthetic = rows.filter((row) => statusTone(row.synthetic_demo_status) === "ready");
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Data & Model Readiness" title="Implementation transparency for feeds, calculations, coefficients, models, validation, governance, and dependencies" icon={<DatabaseZap size={22} />}>
        <p className="section-intro">
          {contextSummary(data, context)}. This surface intentionally separates synthetic demo readiness from real-data readiness. Green synthetic variables show the future-state experience; red and pending real-data items show the honest implementation path.
        </p>
        <RoleGuidancePanel data={data} context={{ ...context, persona: "Analytics / informatics / AI team" }} />
      </Panel>

      <WorkspaceMetricTile
        label="Synthetic demo ready"
        value={formatInteger(readySynthetic.length)}
        detail="Variables, calculations, or scenarios ready for future-state demonstration"
        delta="Synthetic does not imply production-ready"
        tone="good"
        classification="synthetic demo"
        sourceIds={["SRC_SYNTH_UNIT_CENSUS_HOURLY", "SRC_SYNTH_WAITLIST_SNAPSHOTS"]}
        data={data}
        onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })}
      />
      <WorkspaceMetricTile
        label="Review / pending"
        value={formatInteger(summary.review)}
        detail="Definitions, coefficients, validation, governance, or dependencies needing owner review"
        delta="Honest implementation queue"
        tone="watch"
        classification="implementation readiness"
        sourceIds={["SRC_MODEL_VALIDATION_RESULTS", "SRC_MODEL_DRIFT_RESULTS"]}
        data={data}
        onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })}
      />
      <WorkspaceMetricTile
        label="Blocked / not connected"
        value={formatInteger(summary.blocked)}
        detail="Real data feeds or model signals intentionally blocked until governance and validation"
        delta="Safety feature, not a product defect"
        tone="high"
        classification="governance"
        sourceIds={["SRC_DIRECT_LINKAGE_VALIDATION", "SRC_MODEL_VALIDATION_RESULTS"]}
        data={data}
        onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })}
      />

      <Panel span="wide" eyebrow="Readiness filters" title="Implementation queue by category" icon={<SlidersHorizontal size={22} />}>
        <div className="segmented-control wrap" role="group" aria-label="Readiness category">
          <button className={category === "all" ? "active" : ""} onClick={() => setCategory("all")}>
            All
          </button>
          {categories.map((item) => (
            <button key={item} className={category === item ? "active" : ""} onClick={() => setCategory(item)}>
              {titleCase(item)}
            </button>
          ))}
        </div>
      </Panel>

      <Panel span="xlarge" eyebrow="Implementation details" title="Status, owner, trust note, and next implementation step" icon={<FileCheck2 size={22} />}>
        <RegistryTable
          rows={filtered}
          columns={["category", "item", "status", "synthetic_demo_status", "real_data_status", "owner", "next_implementation_step"]}
          limit={40}
        />
      </Panel>
      <Panel span="normal" eyebrow="Blocked items" title="Red/pending by design" icon={<AlertTriangle size={22} />}>
        <RegistryTable rows={blocked} columns={["item_id", "item", "real_data_status", "next_implementation_step"]} limit={8} />
      </Panel>
      <Panel span="xlarge" eyebrow="Dependencies" title="Source readiness and validation gates" icon={<Network size={22} />}>
        <SourceReadinessTable rows={data.directLinkValidation} limit={18} onSelect={(sourceId) => setDrawer({ kind: "source", id: sourceId })} />
      </Panel>
      <Panel span="normal" eyebrow="Model release gates" title="Validation, drift, release, rollback" icon={<BrainCircuit size={22} />}>
        <RegistryTable rows={data.gatekeeper.validationDrift} columns={["asset_id", "primary_metric", "primary_metric_value", "drift_status", "release_gate"]} limit={8} />
      </Panel>
      <ObjectDrawer data={data} drawer={drawer} context={context} onClose={() => setDrawer(null)} setDrawer={setDrawer} />
    </section>
  );
}

export function SignalSimulationsPage({
  data,
  context,
  addMemoryEvent,
}: {
  data: V3Data;
  context: AppContext;
  addMemoryEvent: (event: DataRow) => void;
}) {
  const simulations = data.commandCenter.signalSimulations;
  const [selectedId, setSelectedId] = useState(stringValue(simulations[0], "simulation_id"));
  const [drawer, setDrawer] = useState<DrawerState>(null);
  const selected = simulations.find((row) => stringValue(row, "simulation_id") === selectedId) ?? simulations[0] ?? {};
  const timeline = (selected.timeline as DataRow[] | undefined) ?? [];
  const factors = (selected.factors as DataRow[] | undefined) ?? [];
  const coefficients = (selected.coefficients as DataRow[] | undefined) ?? [];
  const baseline = (selected.baseline_vs_scenario as DataRow[] | undefined) ?? [];
  const implementationSteps = (selected.implementation_steps as string[] | undefined) ?? [];

  function captureReview() {
    addMemoryEvent({
      event_id: `EVT-SIGNAL-${Date.now()}`,
      event_type: "signal_simulation_review",
      created_at: new Date().toISOString(),
      created_by: "showcase_local_user",
      app_area: "AI Signals",
      site_id: context.site,
      unit_or_program: stringValue(selected, "domain"),
      related_ids: stringValue(selected, "simulation_id"),
      related_model_id: stringValue(selected, "simulation_id"),
      status: "review captured locally",
      severity: "medium",
      note: `${stringValue(selected, "label")} reviewed as a synthetic implementation rehearsal.`,
      payload_json: JSON.stringify({ synthetic_demo: true, simulation_id: stringValue(selected, "simulation_id") }),
      synthetic_demo_flag: true,
      writeback_table: "APP.MODEL_REVIEW_NOTE",
    });
  }

  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="AI Signal Simulations" title="Four deep-dive implementation rehearsals for high-value pediatric intelligence signals" icon={<Sparkles size={22} />}>
        <p className="section-intro">
          {contextSummary(data, context)}. These pages show how advanced signals could be governed, interpreted, validated, constrained, and learned from. They do not diagnose, triage, alarm, recommend treatment, or display patient identifiers.
        </p>
        <div className="segmented-control wrap" role="group" aria-label="AI simulation selector">
          {simulations.map((simulation) => (
            <button key={stringValue(simulation, "simulation_id")} className={selectedId === stringValue(simulation, "simulation_id") ? "active" : ""} onClick={() => setSelectedId(stringValue(simulation, "simulation_id"))}>
              {stringValue(simulation, "label")}
            </button>
          ))}
        </div>
      </Panel>

      <Panel span="wide" eyebrow={stringValue(selected, "domain")} title={stringValue(selected, "label", "Signal simulation")} icon={<BrainCircuit size={22} />}>
        <div className="simulation-hero">
          <div>
            <strong>{stringValue(selected, "target_question")}</strong>
            <p>{stringValue(selected, "so_what")}</p>
            <p>{stringValue(selected, "now_what")}</p>
          </div>
          <DetailList
            rows={[
              ["Inspired by", stringValue(selected, "inspiration")],
              ["Clinical boundary", stringValue(selected, "clinical_boundary")],
              ["Cohort", stringValue(selected, "cohort")],
              ["Model family", stringValue(selected, "model_family")],
              ["Threshold logic", stringValue(selected, "threshold_logic")],
              ["Validation", stringValue(selected, "validation_status")],
              ["Governance", stringValue(selected, "governance_status")],
            ]}
          />
        </div>
      </Panel>

      <WorkspaceMetricTile
        label="Signal output"
        value={titleCase(stringValue(selected, "primary_output"))}
        detail="Primary synthetic model output for this rehearsal"
        delta={stringValue(selected, "governance_status")}
        tone={statusTone(selected.governance_status) === "high" ? "high" : "watch"}
        classification="modelled"
        sourceIds={csvIds(selected.source_ids)}
        data={data}
        onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })}
      />
      <WorkspaceMetricTile
        label="Feature families"
        value={formatInteger(stringValue(selected, "feature_families").split(",").length)}
        detail={stringValue(selected, "feature_families")}
        delta="Transparent model wiring"
        tone="watch"
        classification="derived"
        sourceIds={csvIds(selected.source_ids)}
        data={data}
        onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })}
      />
      <WorkspaceMetricTile
        label="Identifier stance"
        value="Aggregate only"
        detail="No direct personal identifiers or free-text extraction in the synthetic display"
        delta="Aggregate feature windows only"
        tone="good"
        classification="governance"
        sourceIds={csvIds(selected.source_ids)}
        data={data}
        onOpenSource={(sourceId) => setDrawer({ kind: "source", id: sourceId })}
      />

      <Panel span="xlarge" eyebrow="Risk trajectory" title="Forecast ribbon with uncertainty" icon={<Activity size={22} />}>
        <ForecastRibbonChart rows={timeline} xKey={timeline[0]?.week ? "week" : "hour"} predictionKey="risk" lowerKey="lower" upperKey="upper" label={`${stringValue(selected, "label")} risk trajectory`} />
      </Panel>
      <Panel span="normal" eyebrow="Demand / supply" title="System factors shaping signal usefulness" icon={<Workflow size={22} />}>
        <HorizontalBarChart rows={factors} labelKey="factor" valueKey="pressure" label="Signal pressure factors" />
      </Panel>
      <Panel span="normal" eyebrow="Coefficients" title="Transparent proxy feature weights" icon={<SlidersHorizontal size={22} />}>
        <SensitivityTornado rows={coefficients} label={`${stringValue(selected, "label")} coefficients`} />
      </Panel>
      <Panel span="normal" eyebrow="Baseline vs governed signal" title="Decision-support comparison" icon={<GitBranch size={22} />}>
        <RegistryTable rows={baseline} columns={["label", "value", "classification"]} limit={4} />
      </Panel>
      <Panel span="xlarge" eyebrow="Implementation steps" title="What has to be true before a real signal could be trusted" icon={<FileCheck2 size={22} />}>
        <div className="phase-grid">
          {implementationSteps.map((step, index) => (
            <article key={step}>
              <strong>{index + 1}. {step}</strong>
              <em>Required before production display</em>
            </article>
          ))}
        </div>
      </Panel>
      <Panel span="normal" eyebrow="Action loop" title="Capture a governed review note" icon={<History size={22} />}>
        <button className="primary-action" onClick={captureReview}>
          <Plus size={18} />
          Capture signal review
        </button>
        <p className="muted">This writes only to local showcase memory; production would use governed Snowflake APP/GOVERNANCE tables.</p>
      </Panel>
      <Panel span="wide" eyebrow="Learning loop" title="How this signal moves from detection to learning" icon={<Workflow size={22} />}>
        <ActionLearningLoopBoard data={data} loopId="LOOP-MODEL-READINESS" />
      </Panel>
      <ObjectDrawer data={data} drawer={drawer} context={context} onClose={() => setDrawer(null)} setDrawer={setDrawer} />
    </section>
  );
}

export function GatekeeperControlPlanePage({ data }: { data: V3Data }) {
  const [mode, setMode] = useState<"lite" | "deep">("lite");
  const [drawer, setDrawer] = useState<DrawerState>(null);
  const controlRows = mode === "lite" ? data.gatekeeper.controlPlane.filter((row) => stringValue(row, "mode").includes("executive")) : data.gatekeeper.controlPlane;
  return (
    <section className="dashboard-grid">
      <Panel span="wide" eyebrow="Gatekeeper Control Plane" title="Govern direct linkages, calculated metrics, models, warnings, scenarios, and release decisions" icon={<ShieldCheck size={22} />}>
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
      <Panel span="wide" eyebrow="Warning registry" title="Thresholds, acknowledgement, and rollback controls" icon={<AlertTriangle size={22} />}>
        <RegistryTable rows={data.gatekeeper.warningLogic} columns={["warning_id", "asset_id", "metric_id", "threshold", "severity", "status"]} limit={10} />
      </Panel>
      <Panel span="wide" eyebrow="Data quality and drift" title="Contract checks, validation, and model release gates" icon={<FileCheck2 size={22} />}>
        <RegistryTable rows={[...data.gatekeeper.dataQualityRules.slice(0, 6), ...data.gatekeeper.validationDrift.slice(0, 6)]} columns={["check_id", "asset_id", "source_id", "rule_name", "status", "release_gate"]} limit={12} />
      </Panel>
      <Panel span="wide" eyebrow="Sources" title="Clickable readiness stoplights" icon={<DatabaseZap size={22} />}>
        <SourceReadinessTable rows={data.directLinkValidation} limit={24} onSelect={(sourceId) => setDrawer({ kind: "source", id: sourceId })} />
      </Panel>
      <ObjectDrawer data={data} drawer={drawer} context={{ persona: "", site: "All sites", horizon: "Now", service: "All services", unit: "All units", program: "All programs", scenario: "All scenarios" }} onClose={() => setDrawer(null)} setDrawer={setDrawer} />
    </section>
  );
}

function MemoryEventLog({ events }: { events: DataRow[] }) {
  return (
    <div className="memory-log">
      {events.slice(0, 12).map((event) => (
        <article key={stringValue(event, "event_id")}>
          <span>{stringValue(event, "event_type")}</span>
          <strong>{stringValue(event, "note")}</strong>
          <em>
            {stringValue(event, "created_at")} | {stringValue(event, "writeback_table")}
          </em>
        </article>
      ))}
    </div>
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
      <Panel span="wide" eyebrow="Action and learning loop" title="Signals move from detection to review, action, follow-up, learning, and spread" icon={<Workflow size={22} />}>
        <ActionLearningLoopBoard data={data} />
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
  const [drawer, setDrawer] = useState<DrawerState>(null);
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
        <SourceReadinessTable rows={data.directLinkValidation} limit={8} onSelect={(sourceId) => setDrawer({ kind: "source", id: sourceId })} />
      </Panel>
      <Panel span="wide" eyebrow="Curated-view registry" title={`${data.sourceRegistry.length} synthetic wiring placeholders`} icon={<DatabaseZap size={22} />}>
        <RegistryTable rows={data.sourceRegistry} columns={["source_view_name", "curated_view", "source_domain", "grain", "cadence", "classification"]} limit={80} onSelect={(row) => setDrawer({ kind: "source", id: stringValue(row, "source_id") })} />
      </Panel>
      <ObjectDrawer data={data} drawer={drawer} context={{ persona: "", site: "All sites", horizon: "Now", service: "All services", unit: "All units", program: "All programs", scenario: "All scenarios" }} onClose={() => setDrawer(null)} setDrawer={setDrawer} />
    </section>
  );
}
