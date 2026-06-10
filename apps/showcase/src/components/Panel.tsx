import type { ReactNode } from "react";

type PanelProps = {
  eyebrow?: string;
  title: string;
  icon?: ReactNode;
  children: ReactNode;
  span?: "normal" | "wide" | "xlarge";
  className?: string;
};

export function Panel({ eyebrow, title, icon, children, span = "normal", className = "" }: PanelProps) {
  return (
    <section className={`panel ${span} ${className}`.trim()}>
      <div className="panel-heading">
        <div>
          {eyebrow && <p className="eyebrow">{eyebrow}</p>}
          <h3>{title}</h3>
        </div>
        {icon && <span className="panel-icon">{icon}</span>}
      </div>
      {children}
    </section>
  );
}

type InsightPanelProps = {
  title: string;
  body: string;
  actions?: string[];
  caveat?: string;
};

export function InsightPanel({ title, body, actions = [], caveat }: InsightPanelProps) {
  return (
    <article className="insight-panel">
      <strong>{title}</strong>
      <p>{body}</p>
      {actions.length > 0 && (
        <ul>
          {actions.map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ul>
      )}
      {caveat && <em>{caveat}</em>}
    </article>
  );
}

type PostureCardProps = {
  label: string;
  value: string;
  detail: string;
  tone?: "steady" | "watch" | "high";
  icon?: ReactNode;
};

export function PostureCard({ label, value, detail, tone = "steady", icon }: PostureCardProps) {
  return (
    <article className="posture-card" data-tone={tone}>
      {icon && <span className="posture-icon">{icon}</span>}
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
        <em>{detail}</em>
      </div>
    </article>
  );
}
