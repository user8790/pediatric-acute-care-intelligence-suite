export type DataRow = Record<string, unknown>;

export type Metadata = {
  appVersion: string;
  generatedAt: string;
  mode: string;
  clinicalUse: string;
  historyWindow: string;
  sourceBoundary: string;
};

export type RowsPayload = { rows: DataRow[] };

export type InpatientFlowPayload = {
  hourly: DataRow[];
  unitPressure: DataRow[];
  bedStatus: DataRow[];
  dischargeBarriers: DataRow[];
  handshake: DataRow[];
  orPacu: DataRow[];
  highResource: DataRow[];
  staffing: DataRow[];
  safety: DataRow[];
};

export type AmbulatoryAccessPayload = {
  history: DataRow[];
  latestAccess: DataRow[];
  referrals: DataRow[];
  slots: DataRow[];
  followup: DataRow[];
  diagnostics: DataRow[];
  travel: DataRow[];
};

export type V2Data = {
  metadata: Metadata;
  inpatientMission: DataRow[];
  inpatientFlow: InpatientFlowPayload;
  inpatientForecasts: DataRow[];
  inpatientScenarios: DataRow[];
  ambulatoryMission: DataRow[];
  ambulatoryAccess: AmbulatoryAccessPayload;
  ambulatoryForecasts: DataRow[];
  ambulatoryScenarios: DataRow[];
  modelCards: DataRow[];
  dataQuality: DataRow[];
  openDataContext: DataRow[];
  coefficients: DataRow[];
};

export type AppContext = {
  persona: string;
  site: string;
  horizon: string;
};

export const PERSONAS = [
  "Executive",
  "Site operations leader",
  "Patient-flow leader",
  "Unit manager",
  "Ambulatory program leader",
  "Clinic operations leader",
  "Analytics / informatics / AI team",
];

export const SITES = [
  { value: "All sites", label: "Provincial pediatric network" },
  { value: "SITE_STOLLERY_INSPIRED", label: "Stollery-inspired" },
  { value: "SITE_ACH_INSPIRED", label: "Alberta Children's-inspired" },
  { value: "SITE_PROV_NETWORK", label: "Provincial network" },
];

export const HORIZONS = ["Now", "Next 6 hours", "Next 24 hours", "Next 72 hours", "Next 14 days", "Next 26 weeks"];
