"""Explainability and model-card utilities."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass(frozen=True)
class ModelCard:
    model_id: str
    model_name: str
    version: str
    owner: str
    intended_use: str
    prediction_horizon: str
    training_data: str
    validation_status: str
    caveat: str
    last_reviewed: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def synthetic_model_card(model_id: str, model_name: str, horizon: str) -> ModelCard:
    return ModelCard(
        model_id=model_id,
        model_name=model_name,
        version="0.1.0",
        owner="Synthetic prototype analytics team",
        intended_use="Scenario planning and executive demonstration",
        prediction_horizon=horizon,
        training_data="Deterministic synthetic pediatric operations data",
        validation_status="Not validated for clinical decision-making",
        caveat="Use for demonstration only. Future production use requires local validation.",
        last_reviewed=datetime.now(timezone.utc).date().isoformat(),
    )


def driver_decomposition(current: dict[str, float], baseline: dict[str, float]) -> list[dict[str, float | str]]:
    """Return sorted additive driver deltas for an interpretation panel."""

    rows = []
    for key, value in current.items():
        if isinstance(value, (int, float)) and isinstance(baseline.get(key), (int, float)):
            rows.append({"driver": key, "delta": float(value) - float(baseline[key])})
    return sorted(rows, key=lambda row: abs(float(row["delta"])), reverse=True)

