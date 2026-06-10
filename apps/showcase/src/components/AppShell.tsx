import {
  BedDouble,
  CalendarClock,
  DatabaseZap,
  FileText,
  FlaskConical,
  HeartPulse,
  Home,
  MapPinned,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
} from "lucide-react";
import type { AppContext, Metadata } from "../data/types";
import { HORIZONS, PERSONAS, SITES } from "../data/types";

export type PageId = "overview" | "inpatient" | "ambulatory" | "simulation" | "methods" | "governance" | "walkthrough";

type PageConfig = { id: PageId; label: string; icon: typeof Home };

export const PUBLIC_PAGES: PageConfig[] = [
  { id: "overview", label: "Overview", icon: Home },
  { id: "inpatient", label: "Inpatient", icon: BedDouble },
  { id: "ambulatory", label: "Ambulatory", icon: CalendarClock },
  { id: "simulation", label: "Simulation", icon: SlidersHorizontal },
  { id: "methods", label: "Methods", icon: FlaskConical },
  { id: "governance", label: "Governance", icon: ShieldCheck },
];

export const INTERNAL_PAGES: PageConfig[] = [
  { id: "walkthrough", label: "Walkthrough", icon: Sparkles },
];

export function AppHeader({ metadata, isLoading }: { metadata: Metadata; isLoading: boolean }) {
  return (
    <header className="topbar">
      <div className="brand-block">
        <div className="brand-mark" aria-hidden="true">
          <HeartPulse size={28} />
        </div>
        <div>
          <p className="eyebrow">Pediatric Acute Care Intelligence Suite</p>
          <h1>Executive command centre for inpatient flow and ambulatory access</h1>
        </div>
      </div>
      <div className="status-stack">
        <span className="status-pill">{metadata.mode}</span>
        <span className="status-pill quiet">{metadata.clinicalUse}</span>
        {isLoading && <span className="status-pill loading">Loading v2 assets</span>}
      </div>
    </header>
  );
}

export function ControlBand({
  context,
  setContext,
  generatedAt,
}: {
  context: AppContext;
  setContext: (context: AppContext) => void;
  generatedAt: string;
}) {
  return (
    <section className="control-band" aria-label="Product controls">
      <label>
        Persona
        <select value={context.persona} onChange={(event) => setContext({ ...context, persona: event.target.value })}>
          {PERSONAS.map((persona) => (
            <option key={persona}>{persona}</option>
          ))}
        </select>
      </label>
      <label>
        Site
        <select value={context.site} onChange={(event) => setContext({ ...context, site: event.target.value })}>
          {SITES.map((site) => (
            <option key={site.value} value={site.value}>
              {site.label}
            </option>
          ))}
        </select>
      </label>
      <label>
        Horizon
        <select value={context.horizon} onChange={(event) => setContext({ ...context, horizon: event.target.value })}>
          {HORIZONS.map((horizon) => (
            <option key={horizon}>{horizon}</option>
          ))}
        </select>
      </label>
      <div className="freshness">
        <DatabaseZap size={18} />
        <span>Generated {new Date(generatedAt).toLocaleString()}</span>
      </div>
      <div className="freshness">
        <MapPinned size={18} />
        <span>Curated-view real-data path, synthetic demo only</span>
      </div>
    </section>
  );
}

export function ProductNav({
  activePage,
  setActivePage,
  showInternal = false,
}: {
  activePage: PageId;
  setActivePage: (page: PageId) => void;
  showInternal?: boolean;
}) {
  const pages = showInternal ? [...PUBLIC_PAGES, ...INTERNAL_PAGES] : PUBLIC_PAGES;
  return (
    <nav className="tab-strip" aria-label="Product areas">
      {pages.map((page) => {
        const Icon = page.icon;
        return (
          <button key={page.id} className={activePage === page.id ? "active" : ""} onClick={() => setActivePage(page.id)} title={page.label}>
            <Icon size={18} />
            <span>{page.label}</span>
          </button>
        );
      })}
    </nav>
  );
}

export function ProductFooter() {
  return (
    <footer>
      Synthetic demonstration data only. Not connected to real hospital systems. Not validated for clinical decision-making. Future production use requires local governance, validation, and curated governed views.
      <span>
        <FileText size={15} /> v2 Snowflake transferability hardening
      </span>
    </footer>
  );
}
