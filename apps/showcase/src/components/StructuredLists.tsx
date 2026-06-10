import { CheckCircle2, CircleAlert, Info } from "lucide-react";
import type { DataRow } from "../data/types";
import { numberValue, stringValue, titleCase } from "../lib/format";

export function DriverStack({ drivers }: { drivers: string[] }) {
  return (
    <div className="driver-stack">
      {drivers.map((driver, index) => (
        <article key={driver}>
          <span>{index + 1}</span>
          <strong>{titleCase(driver)}</strong>
          <em>{index === 0 ? "Primary driver" : "Contributing signal"}</em>
        </article>
      ))}
    </div>
  );
}

export function ScenarioCards({ rows, outcomeKey }: { rows: DataRow[]; outcomeKey: string }) {
  return (
    <div className="scenario-card-grid">
      {rows.slice(0, 6).map((row) => (
        <article className="scenario-card" key={stringValue(row, "scenario_name")}>
          <div>
            <strong>{stringValue(row, "scenario_name")}</strong>
            <span>Impact {numberValue(row, "impact_score").toFixed(0)} | Effort {numberValue(row, "effort_score").toFixed(0)}</span>
          </div>
          <p>{numberValue(row, outcomeKey).toLocaleString()}</p>
          <em>Risk {numberValue(row, "operational_risk_score").toFixed(0)} | Fairness proxy {numberValue(row, "fairness_proxy_delta").toFixed(2)}</em>
        </article>
      ))}
    </div>
  );
}

export function QualityTable({ rows }: { rows: DataRow[] }) {
  return (
    <div className="quality-table" role="table" aria-label="Data quality checks">
      {rows.slice(0, 18).map((row, index) => {
        const status = stringValue(row, "status", "review");
        return (
          <div className="quality-row" role="row" key={`${stringValue(row, "table_name")}-${stringValue(row, "check_name")}-${index}`}>
            <span>{titleCase(stringValue(row, "table_name"))}</span>
            <strong>{titleCase(stringValue(row, "check_name"))}</strong>
            <em data-status={status}>{status === "pass" ? <CheckCircle2 size={14} /> : <CircleAlert size={14} />} {status}</em>
          </div>
        );
      })}
    </div>
  );
}

export function ModelCardGrid({ rows }: { rows: DataRow[] }) {
  return (
    <div className="model-card-grid">
      {rows.map((row) => (
        <article className="model-card" key={stringValue(row, "model_id")}>
          <p className="eyebrow">{stringValue(row, "model_id")}</p>
          <h4>{stringValue(row, "model_name")}</h4>
          <dl>
            <div>
              <dt>Version</dt>
              <dd>{stringValue(row, "version")}</dd>
            </div>
            <div>
              <dt>Horizon</dt>
              <dd>{stringValue(row, "prediction_horizon")}</dd>
            </div>
            <div>
              <dt>Validation</dt>
              <dd>{stringValue(row, "validation_status")}</dd>
            </div>
            <div>
              <dt>Metrics</dt>
              <dd>{stringValue(row, "metrics")}</dd>
            </div>
          </dl>
          <p>{stringValue(row, "caveat")}</p>
        </article>
      ))}
    </div>
  );
}

export function DefinitionList({ rows }: { rows: Array<[string, string]> }) {
  return (
    <div className="definition-grid">
      {rows.map(([term, definition]) => (
        <article key={term}>
          <Info size={16} />
          <strong>{term}</strong>
          <span>{definition}</span>
        </article>
      ))}
    </div>
  );
}
