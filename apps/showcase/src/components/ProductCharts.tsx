import type * as echarts from "echarts";
import type { DataRow } from "../data/types";
import { avgRows, numberValue, stringValue, titleCase } from "../lib/format";
import { EChart } from "./EChart";

const palette = ["#176b87", "#38a3a5", "#f2a65a", "#8e6c88", "#5863f8", "#d65f5f", "#6f8f72"];

export function ForecastRibbonChart({
  rows,
  xKey,
  predictionKey,
  lowerKey,
  upperKey,
  label,
  height = 310,
}: {
  rows: DataRow[];
  xKey: string;
  predictionKey: string;
  lowerKey: string;
  upperKey: string;
  label: string;
  height?: number;
}) {
  const sorted = [...rows].sort((a, b) => numberValue(a, xKey) - numberValue(b, xKey));
  const categories = sorted.map((row) => `${numberValue(row, xKey)}${xKey.includes("week") ? "w" : "h"}`);
  const prediction = sorted.map((row) => numberValue(row, predictionKey));
  const lower = sorted.map((row) => numberValue(row, lowerKey));
  const upperDelta = sorted.map((row) => Math.max(0, numberValue(row, upperKey) - numberValue(row, lowerKey)));
  const option: echarts.EChartsOption = {
    color: palette,
    tooltip: { trigger: "axis" },
    legend: { bottom: 0, textStyle: { color: "#51606a" } },
    grid: { left: 42, right: 18, top: 24, bottom: 52 },
    xAxis: { type: "category", data: categories, boundaryGap: false },
    yAxis: { type: "value", axisLabel: { formatter: (value: number) => (value <= 1.5 ? `${Math.round(value * 100)}%` : value.toLocaleString()) } },
    series: [
      {
        name: "Lower bound",
        type: "line",
        data: lower,
        stack: "band",
        lineStyle: { opacity: 0 },
        symbol: "none",
        areaStyle: { opacity: 0 },
      },
      {
        name: "Uncertainty band",
        type: "line",
        data: upperDelta,
        stack: "band",
        lineStyle: { opacity: 0 },
        symbol: "none",
        areaStyle: { color: "rgba(56, 163, 165, 0.22)" },
      },
      {
        name: "Forecast",
        type: "line",
        smooth: true,
        data: prediction,
        symbolSize: 8,
        lineStyle: { width: 3 },
        markLine: prediction.some((value) => value <= 1.5)
          ? {
              symbol: "none",
              lineStyle: { color: "#d65f5f", type: "dashed" },
              data: [{ yAxis: 0.95, name: "95% threshold" }],
            }
          : undefined,
      },
    ],
  };
  return <EChart option={option} ariaLabel={label} height={height} />;
}

export function UnitPressureHeatmap({ rows }: { rows: DataRow[] }) {
  const units = rows.map((row) => titleCase(stringValue(row, "unit_name", stringValue(row, "service_line"))));
  const metrics = ["Occupancy", "Staffing gap", "ED boarders"];
  const values = rows.flatMap((row, unitIndex) => [
    [0, unitIndex, Math.round(numberValue(row, "occupancy_pct") * 100)],
    [1, unitIndex, Math.round(numberValue(row, "staffing_gap_pct") * 100)],
    [2, unitIndex, numberValue(row, "ed_boarders")],
  ]);
  const option: echarts.EChartsOption = {
    tooltip: { position: "top" },
    grid: { left: 118, right: 24, top: 28, bottom: 38 },
    xAxis: { type: "category", data: metrics, splitArea: { show: true } },
    yAxis: { type: "category", data: units, splitArea: { show: true } },
    visualMap: { min: 0, max: 115, orient: "horizontal", left: "center", bottom: 0, inRange: { color: ["#e8f3f1", "#f2a65a", "#d65f5f"] } },
    series: [{ type: "heatmap", data: values, label: { show: true }, emphasis: { itemStyle: { shadowBlur: 8, shadowColor: "rgba(0,0,0,.18)" } } }],
  };
  return <EChart option={option} ariaLabel="Unit pressure heatmap" height={360} />;
}

export function FlowSankey({ rows }: { rows: DataRow[] }) {
  const awaiting = rows.reduce((total, row) => total + numberValue(row, "ed_admissions_awaiting_bed"), 0);
  const consults = rows.reduce((total, row) => total + numberValue(row, "consult_bottleneck_count"), 0);
  const option: echarts.EChartsOption = {
    color: palette,
    tooltip: { trigger: "item", triggerOn: "mousemove" },
    series: [
      {
        type: "sankey",
        nodeAlign: "justify",
        draggable: false,
        emphasis: { focus: "adjacency" },
        data: [
          { name: "ED decision to admit" },
          { name: "Consults" },
          { name: "Bed assignment" },
          { name: "Transport/arrival" },
          { name: "Inpatient unit" },
        ],
        links: [
          { source: "ED decision to admit", target: "Consults", value: Math.max(1, consults) },
          { source: "ED decision to admit", target: "Bed assignment", value: Math.max(1, awaiting * 1.4) },
          { source: "Consults", target: "Bed assignment", value: Math.max(1, consults * 0.8) },
          { source: "Bed assignment", target: "Transport/arrival", value: Math.max(1, awaiting) },
          { source: "Transport/arrival", target: "Inpatient unit", value: Math.max(1, awaiting * 0.9) },
        ],
      },
    ],
  };
  return <EChart option={option} ariaLabel="ED to inpatient flow network" height={310} />;
}

export function HorizontalBarChart({
  rows,
  labelKey,
  valueKey,
  label,
  height = 320,
}: {
  rows: DataRow[];
  labelKey: string;
  valueKey: string;
  label: string;
  height?: number;
}) {
  const sliced = [...rows].sort((a, b) => numberValue(b, valueKey) - numberValue(a, valueKey)).slice(0, 10).reverse();
  const option: echarts.EChartsOption = {
    color: ["#176b87"],
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: 126, right: 18, top: 20, bottom: 28 },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: sliced.map((row) => titleCase(stringValue(row, labelKey))) },
    series: [{ type: "bar", data: sliced.map((row) => numberValue(row, valueKey)), itemStyle: { borderRadius: [0, 6, 6, 0] } }],
  };
  return <EChart option={option} ariaLabel={label} height={height} />;
}

export function DischargeFunnel({ rows }: { rows: DataRow[] }) {
  const total = rows.reduce((sum, row) => sum + numberValue(row, "active_count"), 0);
  const pharmacy = rows.filter((row) => stringValue(row, "barrier") === "pharmacy").reduce((sum, row) => sum + numberValue(row, "active_count"), 0);
  const imaging = rows.filter((row) => stringValue(row, "barrier") === "imaging").reduce((sum, row) => sum + numberValue(row, "active_count"), 0);
  const transport = rows.filter((row) => stringValue(row, "barrier") === "transport").reduce((sum, row) => sum + numberValue(row, "active_count"), 0);
  const option: echarts.EChartsOption = {
    color: palette,
    tooltip: { trigger: "item" },
    series: [
      {
        type: "funnel",
        left: "8%",
        top: 20,
        bottom: 20,
        width: "84%",
        minSize: "18%",
        maxSize: "92%",
        sort: "descending",
        label: { formatter: "{b}: {c}" },
        data: [
          { name: "Medically ready with barrier", value: total },
          { name: "Pharmacy", value: pharmacy },
          { name: "Imaging", value: imaging },
          { name: "Transport", value: transport },
          { name: "Ready by 16:00", value: Math.max(1, Math.round(total * 0.42)) },
        ],
      },
    ],
  };
  return <EChart option={option} ariaLabel="Discharge readiness funnel" height={310} />;
}

export function ScenarioFrontier({
  rows,
  outcomeKey,
  label,
}: {
  rows: DataRow[];
  outcomeKey: string;
  label: string;
}) {
  const option: echarts.EChartsOption = {
    color: palette,
    tooltip: {
      trigger: "item",
      formatter: (params: unknown) => {
        const item = params as { data?: unknown[] };
        return `${item.data?.[3] ?? "Scenario"}<br/>Impact: ${item.data?.[0]}<br/>Effort: ${item.data?.[1]}<br/>Outcome: ${item.data?.[2]}`;
      },
    },
    grid: { left: 42, right: 28, top: 22, bottom: 48 },
    xAxis: { name: "Impact", min: 0, max: 100 },
    yAxis: { name: "Effort / risk", min: 0, max: 6 },
    series: [
      {
        type: "scatter",
        symbolSize: (data: unknown) => Math.max(14, Math.min(42, Number((data as unknown[])[2]) / 20)),
        data: rows.map((row) => [
          numberValue(row, "impact_score"),
          numberValue(row, "effort_score") + numberValue(row, "operational_risk_score") / 3,
          numberValue(row, outcomeKey),
          stringValue(row, "scenario_name"),
        ]),
        label: { show: true, formatter: (params: unknown) => String((params as { data?: unknown[] }).data?.[3] ?? ""), position: "top", color: "#26323b", fontSize: 10 },
      },
    ],
  };
  return <EChart option={option} ariaLabel={label} height={380} />;
}

export function SensitivityTornado({ rows, label }: { rows: DataRow[]; label: string }) {
  const values = rows
    .slice(0, 10)
    .map((row) => ({
      name: titleCase(stringValue(row, "coefficient_name")),
      value: Math.abs(numberValue(row, "default_value")) * 100,
    }))
    .sort((a, b) => a.value - b.value);
  const option: echarts.EChartsOption = {
    color: ["#8e6c88"],
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: 150, right: 24, top: 20, bottom: 28 },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: values.map((item) => item.name) },
    series: [{ type: "bar", data: values.map((item) => item.value), itemStyle: { borderRadius: [0, 6, 6, 0] } }],
  };
  return <EChart option={option} ariaLabel={label} height={350} />;
}

export function AccessCalendarHeatmap({ rows }: { rows: DataRow[] }) {
  const programs = Array.from(new Set(rows.map((row) => titleCase(stringValue(row, "program"))))).slice(0, 8);
  const data = rows.slice(-programs.length * 8).map((row, index) => [
    index % 8,
    programs.indexOf(titleCase(stringValue(row, "program"))),
    Math.round(numberValue(row, "third_next_available_days")),
  ]);
  const option: echarts.EChartsOption = {
    tooltip: { position: "top" },
    grid: { left: 118, right: 24, top: 28, bottom: 42 },
    xAxis: { type: "category", data: ["W-7", "W-6", "W-5", "W-4", "W-3", "W-2", "W-1", "Now"], splitArea: { show: true } },
    yAxis: { type: "category", data: programs, splitArea: { show: true } },
    visualMap: { min: 0, max: 90, orient: "horizontal", left: "center", bottom: 0, inRange: { color: ["#e8f3f1", "#f2a65a", "#d65f5f"] } },
    series: [{ type: "heatmap", data, label: { show: true } }],
  };
  return <EChart option={option} ariaLabel="Clinic template calendar heatmap" height={360} />;
}

export function OpenContextChart({ rows }: { rows: DataRow[] }) {
  const sliced = rows.slice(-26);
  const option: echarts.EChartsOption = {
    color: ["#176b87", "#f2a65a", "#8e6c88"],
    tooltip: { trigger: "axis" },
    legend: { bottom: 0 },
    grid: { left: 42, right: 18, top: 20, bottom: 52 },
    xAxis: { type: "category", data: sliced.map((row) => stringValue(row, "week_start").slice(5)) },
    yAxis: { type: "value" },
    series: [
      { name: "Respiratory activity", type: "line", smooth: true, data: sliced.map((row) => numberValue(row, "respiratory_activity_index")) },
      { name: "AQHI/smoke proxy", type: "line", smooth: true, data: sliced.map((row) => numberValue(row, "aqhi_max_proxy")) },
      { name: "Temperature proxy", type: "line", smooth: true, data: sliced.map((row) => numberValue(row, "mean_temperature_c_proxy")) },
    ],
  };
  return <EChart option={option} ariaLabel="Cached public context trend" height={330} />;
}

export function WorkloadMatrix({ rows }: { rows: DataRow[] }) {
  const option: echarts.EChartsOption = {
    color: ["#5863f8"],
    tooltip: { trigger: "item" },
    grid: { left: 52, right: 24, top: 20, bottom: 44 },
    xAxis: { name: "Effective beds lost", type: "value" },
    yAxis: { name: "Workload index", type: "value" },
    series: [
      {
        type: "scatter",
        symbolSize: (value: unknown) => 14 + Number((value as unknown[])[2]) * 1.6,
        data: rows.map((row) => [
          numberValue(row, "effective_beds_lost"),
          numberValue(row, "workload_index"),
          Math.max(1, avgRows([row], "required_hours") / 10),
          titleCase(stringValue(row, "unit_name")),
        ]),
        label: { show: true, formatter: (params: unknown) => String((params as { data?: unknown[] }).data?.[3] ?? ""), position: "top", fontSize: 10 },
      },
    ],
  };
  return <EChart option={option} ariaLabel="Staffing and workload pressure matrix" height={320} />;
}
