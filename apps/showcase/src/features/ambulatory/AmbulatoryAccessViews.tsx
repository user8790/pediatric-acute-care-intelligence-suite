import { CalendarRange, Funnel, MapPinned, Route, TimerReset } from "lucide-react";
import {
  AccessCalendarHeatmap,
  ForecastRibbonChart,
  HorizontalBarChart,
} from "../../components/ProductCharts";
import { Panel } from "../../components/Panel";
import type { AmbulatoryAccessPayload, AppContext, DataRow } from "../../data/types";
import { filterBySite } from "../../lib/format";

export function AmbulatoryAccessViews({
  access,
  forecasts,
  context,
}: {
  access: AmbulatoryAccessPayload;
  forecasts: DataRow[];
  context: AppContext;
}) {
  const latestAccess = filterBySite(access.latestAccess, context.site);
  const referrals = filterBySite(access.referrals, context.site);
  const slots = filterBySite(access.slots, context.site);
  const diagnostics = filterBySite(access.diagnostics, context.site);
  const followup = filterBySite(access.followup, context.site);
  const travel = filterBySite(access.travel, context.site);
  const scopedForecasts = filterBySite(forecasts, context.site).filter((row) => !context.horizon.includes("hour"));

  return (
    <>
      <Panel span="xlarge" eyebrow="4 to 26 weeks" title="Backlog forecast ribbon" icon={<CalendarRange size={22} />}>
        <ForecastRibbonChart rows={scopedForecasts} xKey="horizon_weeks" predictionKey="prediction" lowerKey="p10" upperKey="p90" label="Ambulatory backlog forecast with uncertainty band" />
      </Panel>
      <Panel span="normal" eyebrow="Clinic template" title="Calendar heatmap" icon={<TimerReset size={22} />}>
        <AccessCalendarHeatmap rows={latestAccess} />
      </Panel>
      <Panel span="normal" eyebrow="Referral and triage" title="New referrals by program" icon={<Funnel size={22} />}>
        <HorizontalBarChart rows={referrals} labelKey="program" valueKey="new_referrals" label="Referral demand by program" />
      </Panel>
      <Panel span="normal" eyebrow="Waitlist ageing" title="Over-target count">
        <HorizontalBarChart rows={latestAccess} labelKey="program" valueKey="waitlist_over_target" label="Waitlist over target by program" />
      </Panel>
      <Panel span="normal" eyebrow="No-show/late-cancel" title="Completed visits and risk">
        <HorizontalBarChart rows={slots} labelKey="program" valueKey="completed_visits" label="Completed clinic visits by program" />
      </Panel>
      <Panel span="normal" eyebrow="Diagnostic dependency" title="Missing prerequisites" icon={<Route size={22} />}>
        <HorizontalBarChart rows={diagnostics} labelKey="program" valueKey="missing_prerequisite_count" label="Diagnostic dependency bottleneck" />
      </Panel>
      <Panel span="normal" eyebrow="Follow-up reliability" title="Overdue follow-up">
        <HorizontalBarChart rows={followup} labelKey="program" valueKey="overdue_followup" label="Overdue follow-up by program" />
      </Panel>
      <Panel span="normal" eyebrow="Virtual/outreach/travel" title="Regional burden lens" icon={<MapPinned size={22} />}>
        <HorizontalBarChart rows={travel} labelKey="program" valueKey="travel_burden_index" label="Travel burden proxy by program" />
      </Panel>
    </>
  );
}
