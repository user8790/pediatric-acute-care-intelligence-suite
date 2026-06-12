import { DatabaseZap, FileCheck2, ShieldCheck, Workflow } from "lucide-react";
import { InsightPanel, Panel } from "../../components/Panel";
import { OpenContextChart } from "../../components/ProductCharts";
import { DefinitionList, QualityTable } from "../../components/StructuredLists";
import type { DataRow } from "../../data/types";

const governanceRows: Array<[string, string]> = [
  ["Synthetic-only boundary", "No direct identifiers or contact-detail fields are generated."],
  ["Aggregate-first product surface", "Patient-level rows are suppressed by default; operational displays use aggregate synthetic rows."],
  ["Curated governed views", "Future real-data implementation maps through governed Snowflake views, not raw PHI tables."],
  ["Clinical-use caveat", "The prototype is not validated for clinical decision-making and should be treated as planning/demo software."],
  ["Model monitoring path", "Future production use requires temporal validation, subgroup calibration, drift monitoring, audit logs, and local governance approval."],
  ["Standards path", "FHIR, SMART on FHIR, CDS Hooks, DICOM/ImagingStudy, and Snowflake curated marts are documented as future integration paths."],
];

export function GovernanceExplorer({ quality, openDataContext }: { quality: DataRow[]; openDataContext: DataRow[] }) {
  return (
    <>
      <Panel span="wide" eyebrow="Governance, Privacy, Safety" title="The product surface includes caveats, quality status, and future real-data controls" icon={<ShieldCheck size={22} />}>
        <DefinitionList rows={governanceRows} />
      </Panel>
      <Panel span="xlarge" eyebrow="Data quality" title="Latest synthetic quality and identifier checks" icon={<FileCheck2 size={22} />}>
        <QualityTable rows={quality} />
      </Panel>
      <Panel span="normal" eyebrow="Future integration path" title="Curated views before apps" icon={<Workflow size={22} />}>
        <InsightPanel
          title="Minimum viable real-data connection"
          body="Start with census and bed status, then add ADT, ED boarding, discharge milestones, OR/PACU, ambulatory access, staffing/workload, model outputs, and scenario logs."
          actions={["No confidential table names are assumed.", "All production fields require validation checks and aggregation rules."]}
        />
      </Panel>
      <Panel span="normal" eyebrow="Public context" title="Open-data context is cached" icon={<DatabaseZap size={22} />}>
        <OpenContextChart rows={openDataContext} />
      </Panel>
    </>
  );
}
