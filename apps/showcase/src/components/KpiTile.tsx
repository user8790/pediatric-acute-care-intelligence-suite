import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";

type KpiTileProps = {
  label: string;
  value: string;
  detail: string;
  delta?: string;
  tone?: "neutral" | "watch" | "high" | "good";
};

export function KpiTile({ label, value, detail, delta, tone = "neutral" }: KpiTileProps) {
  const direction = delta?.trim().startsWith("-") ? "down" : delta?.trim().startsWith("+") ? "up" : "flat";
  return (
    <article className="kpi-tile" data-tone={tone}>
      <span className="kpi-label">{label}</span>
      <strong>{value}</strong>
      <span className="kpi-detail">{detail}</span>
      {delta && (
        <em className={`kpi-delta ${direction}`}>
          {direction === "up" ? <ArrowUpRight size={15} /> : direction === "down" ? <ArrowDownRight size={15} /> : <Minus size={15} />}
          {delta}
        </em>
      )}
    </article>
  );
}
