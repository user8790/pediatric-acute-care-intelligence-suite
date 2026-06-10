import type { DataRow } from "../data/types";

export function numberValue(row: DataRow | undefined, key: string, fallback = 0): number {
  const value = row?.[key];
  const numeric = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
}

export function stringValue(row: DataRow | undefined, key: string, fallback = ""): string {
  const value = row?.[key];
  return value === undefined || value === null ? fallback : String(value);
}

export function sumRows(rows: DataRow[], key: string): number {
  return rows.reduce((total, row) => total + numberValue(row, key), 0);
}

export function avgRows(rows: DataRow[], key: string): number {
  return rows.length ? sumRows(rows, key) / rows.length : 0;
}

export function filterBySite(rows: DataRow[], site: string): DataRow[] {
  if (site === "All sites") return rows;
  return rows.filter((row) => stringValue(row, "site_id") === site);
}

export function formatInteger(value: number): string {
  return Math.round(value).toLocaleString();
}

export function formatPct(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

export function formatCompact(value: number): string {
  return Intl.NumberFormat("en-CA", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

export function titleCase(value: unknown): string {
  return String(value ?? "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function latestTimestamp(rows: DataRow[], key: string): string {
  const values = rows.map((row) => Date.parse(stringValue(row, key))).filter(Number.isFinite);
  if (!values.length) return "";
  return new Date(Math.max(...values)).toLocaleString("en-CA", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function siteLabel(site: string): string {
  if (site === "SITE_STOLLERY_INSPIRED") return "Stollery-inspired";
  if (site === "SITE_ACH_INSPIRED") return "Alberta Children's-inspired";
  if (site === "SITE_PROV_NETWORK") return "Provincial network";
  return "Provincial pediatric network";
}
