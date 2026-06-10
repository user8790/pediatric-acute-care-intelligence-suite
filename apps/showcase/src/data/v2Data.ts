import { useEffect, useState } from "react";
import { fallbackV2Data } from "./fallbackV2Data";
import type { AmbulatoryAccessPayload, InpatientFlowPayload, Metadata, RowsPayload, V2Data } from "./types";

const BASE = "/data/v2";

async function fetchJson<T>(fileName: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${BASE}/${fileName}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    console.warn(`Using fallback v2 data for ${fileName}`, error);
    return fallback;
  }
}

export async function loadV2Data(): Promise<V2Data> {
  const [
    metadata,
    inpatientMission,
    inpatientFlow,
    inpatientForecasts,
    inpatientScenarios,
    ambulatoryMission,
    ambulatoryAccess,
    ambulatoryForecasts,
    ambulatoryScenarios,
    modelCards,
    dataQuality,
    openDataContext,
    coefficients,
  ] = await Promise.all([
    fetchJson<Metadata>("metadata.json", fallbackV2Data.metadata),
    fetchJson<RowsPayload>("inpatient_mission_control.json", { rows: fallbackV2Data.inpatientMission }),
    fetchJson<InpatientFlowPayload>("inpatient_flow.json", fallbackV2Data.inpatientFlow),
    fetchJson<RowsPayload>("inpatient_forecasts.json", { rows: fallbackV2Data.inpatientForecasts }),
    fetchJson<RowsPayload>("inpatient_scenarios.json", { rows: fallbackV2Data.inpatientScenarios }),
    fetchJson<RowsPayload>("ambulatory_mission_control.json", { rows: fallbackV2Data.ambulatoryMission }),
    fetchJson<AmbulatoryAccessPayload>("ambulatory_access.json", fallbackV2Data.ambulatoryAccess),
    fetchJson<RowsPayload>("ambulatory_forecasts.json", { rows: fallbackV2Data.ambulatoryForecasts }),
    fetchJson<RowsPayload>("ambulatory_scenarios.json", { rows: fallbackV2Data.ambulatoryScenarios }),
    fetchJson<RowsPayload>("model_cards.json", { rows: fallbackV2Data.modelCards }),
    fetchJson<RowsPayload>("data_quality.json", { rows: fallbackV2Data.dataQuality }),
    fetchJson<RowsPayload>("open_data_context.json", { rows: fallbackV2Data.openDataContext }),
    fetchJson<RowsPayload>("coefficient_registry.json", { rows: fallbackV2Data.coefficients }),
  ]);

  return {
    metadata,
    inpatientMission: inpatientMission.rows,
    inpatientFlow,
    inpatientForecasts: inpatientForecasts.rows,
    inpatientScenarios: inpatientScenarios.rows,
    ambulatoryMission: ambulatoryMission.rows,
    ambulatoryAccess,
    ambulatoryForecasts: ambulatoryForecasts.rows,
    ambulatoryScenarios: ambulatoryScenarios.rows,
    modelCards: modelCards.rows,
    dataQuality: dataQuality.rows,
    openDataContext: openDataContext.rows,
    coefficients: coefficients.rows,
  };
}

export function useV2Data() {
  const [data, setData] = useState<V2Data>(fallbackV2Data);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    loadV2Data()
      .then((payload) => {
        if (mounted) {
          setData(payload);
        }
      })
      .finally(() => {
        if (mounted) {
          setIsLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  return { data, isLoading };
}
