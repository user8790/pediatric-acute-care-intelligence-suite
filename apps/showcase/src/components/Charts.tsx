import { ArrowDownRight, ArrowUpRight } from "lucide-react";

type Point = { label: string; value: number; lower?: number; upper?: number };

export function KpiTile({
  label,
  value,
  unit,
  trend,
}: {
  label: string;
  value: number;
  unit: string;
  trend: string;
}) {
  const isUp = trend.trim().startsWith("+");
  return (
    <section className="kpi-tile" aria-label={label}>
      <span className="kpi-label">{label}</span>
      <strong>
        {value.toLocaleString()}
        <small>{unit}</small>
      </strong>
      <span className={isUp ? "trend up" : "trend down"}>
        {isUp ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
        {trend}
      </span>
    </section>
  );
}

export function ForecastBand({ points }: { points: Point[] }) {
  const width = 520;
  const height = 210;
  const pad = 28;
  const values = points.flatMap((p) => [p.value, p.lower ?? p.value, p.upper ?? p.value]);
  const min = Math.min(...values, 0.65);
  const max = Math.max(...values, 1.2);
  const x = (idx: number) => pad + (idx / Math.max(points.length - 1, 1)) * (width - pad * 2);
  const y = (value: number) => height - pad - ((value - min) / Math.max(max - min, 0.01)) * (height - pad * 2);
  const line = (selector: (p: Point) => number | undefined) =>
    points
      .map((p, idx) => `${idx === 0 ? "M" : "L"} ${x(idx).toFixed(2)} ${y(selector(p) ?? p.value).toFixed(2)}`)
      .join(" ");
  const bandPath = `${line((p) => p.upper)} ${points
    .map((p, idx) => `L ${x(points.length - 1 - idx).toFixed(2)} ${y(points[points.length - 1 - idx].lower ?? p.value).toFixed(2)}`)
    .join(" ")} Z`;

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Occupancy forecast band">
      <rect x="0" y="0" width={width} height={height} rx="8" />
      <line x1={pad} x2={width - pad} y1={y(0.95)} y2={y(0.95)} className="threshold" />
      <path d={bandPath} className="band" />
      <path d={line((p) => p.value)} className="forecast-line" />
      {points.map((p, idx) => (
        <g key={p.label}>
          <circle cx={x(idx)} cy={y(p.value)} r="4" className="dot" />
          <text x={x(idx)} y={height - 8} textAnchor="middle">
            {p.label}
          </text>
        </g>
      ))}
    </svg>
  );
}

export function BarList({
  rows,
  labelKey,
  valueKey,
  maxRows = 8,
}: {
  rows: Record<string, unknown>[];
  labelKey: string;
  valueKey: string;
  maxRows?: number;
}) {
  const sliced = rows.slice(0, maxRows);
  const max = Math.max(...sliced.map((row) => Number(row[valueKey]) || 0), 1);
  return (
    <div className="bar-list">
      {sliced.map((row, idx) => {
        const value = Number(row[valueKey]) || 0;
        return (
          <div className="bar-row" key={`${String(row[labelKey])}-${idx}`}>
            <span>{String(row[labelKey]).replaceAll("_", " ")}</span>
            <div className="bar-track" aria-hidden="true">
              <div className="bar-fill" style={{ width: `${Math.max(4, (value / max) * 100)}%` }} />
            </div>
            <strong>{value.toLocaleString()}</strong>
          </div>
        );
      })}
    </div>
  );
}

export function HeatGrid({ rows }: { rows: Record<string, unknown>[] }) {
  return (
    <div className="heat-grid" aria-label="Unit pressure heatmap">
      {rows.slice(0, 18).map((row, idx) => {
        const occ = Number(row.occupancy_pct) || 0;
        return (
          <div
            className="heat-cell"
            data-risk={occ > 1 ? "high" : occ > 0.92 ? "watch" : "steady"}
            key={`${String(row.unit_id)}-${idx}`}
            title={`${String(row.service_line)} ${(occ * 100).toFixed(1)}%`}
          >
            <span>{String(row.service_line).replaceAll("_", " ")}</span>
            <strong>{(occ * 100).toFixed(0)}%</strong>
          </div>
        );
      })}
    </div>
  );
}

