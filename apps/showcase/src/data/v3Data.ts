import { useEffect, useState } from "react";
import { fallbackV3Data } from "./fallbackV3Data";
import type { Metadata, RowsPayload, V3Data } from "./types";

const BASE = "/data/v3";

async function fetchJson<T>(fileName: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${BASE}/${fileName}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    console.warn(`Using fallback v3 data for ${fileName}`, error);
    return fallback;
  }
}

export async function loadV3Data(): Promise<V3Data> {
  const [
    metadata,
    sourceRegistry,
    directLinkValidation,
    metricRegistry,
    modelRegistry,
    panelLineage,
    systemPosture,
    inpatient,
    ambulatory,
    predictiveAssets,
    scenarioLab,
    gatekeeper,
    learningMemory,
    futureWiring,
  ] = await Promise.all([
    fetchJson<Metadata>("metadata.json", fallbackV3Data.metadata),
    fetchJson<RowsPayload>("source_registry.json", { rows: fallbackV3Data.sourceRegistry }),
    fetchJson<RowsPayload>("direct_link_validation.json", { rows: fallbackV3Data.directLinkValidation }),
    fetchJson<RowsPayload>("metric_registry.json", { rows: fallbackV3Data.metricRegistry }),
    fetchJson<RowsPayload>("model_registry.json", { rows: fallbackV3Data.modelRegistry }),
    fetchJson<RowsPayload>("panel_lineage.json", { rows: fallbackV3Data.panelLineage }),
    fetchJson<V3Data["systemPosture"]>("system_posture.json", fallbackV3Data.systemPosture),
    fetchJson<V3Data["inpatient"]>("inpatient_intelligence.json", fallbackV3Data.inpatient),
    fetchJson<V3Data["ambulatory"]>("ambulatory_intelligence.json", fallbackV3Data.ambulatory),
    fetchJson<V3Data["predictiveAssets"]>("predictive_assets.json", fallbackV3Data.predictiveAssets),
    fetchJson<V3Data["scenarioLab"]>("scenario_lab.json", fallbackV3Data.scenarioLab),
    fetchJson<V3Data["gatekeeper"]>("gatekeeper_control_plane.json", fallbackV3Data.gatekeeper),
    fetchJson<V3Data["learningMemory"]>("learning_system_memory.json", fallbackV3Data.learningMemory),
    fetchJson<V3Data["futureWiring"]>("future_real_data_wiring.json", fallbackV3Data.futureWiring),
  ]);

  return {
    metadata,
    sourceRegistry: sourceRegistry.rows,
    directLinkValidation: directLinkValidation.rows,
    metricRegistry: metricRegistry.rows,
    modelRegistry: modelRegistry.rows,
    panelLineage: panelLineage.rows,
    systemPosture,
    inpatient,
    ambulatory,
    predictiveAssets,
    scenarioLab,
    gatekeeper,
    learningMemory,
    futureWiring,
  };
}

export function useV3Data() {
  const [data, setData] = useState<V3Data>(fallbackV3Data);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    loadV3Data()
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
