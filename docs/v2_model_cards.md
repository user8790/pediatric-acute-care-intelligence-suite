# v2 Model Cards

The v2 model registry is generated into `apps/showcase/public/data/v2/model_cards.json`, `apps/snowflake_streamlit/shared/sample_data/v2_model_registry.csv`, and `MODEL.DIM_V2_MODEL_REGISTRY`.

## Model Card Fields

Each displayed model output carries:

- model id and name;
- version;
- prediction horizon;
- intended use;
- training data statement;
- validation status;
- metrics;
- top-driver method;
- data freshness;
- caveat.

## Models

- `MODEL_INPT_OCC_V2`: probabilistic occupancy forecast.
- `MODEL_INPT_DISCHARGE_V2`: discharge by time-band probability.
- `MODEL_INPT_PICU_V2`: PICU/NICU pressure forecast.
- `MODEL_AMB_BACKLOG_V2`: ambulatory backlog forecast.
- `MODEL_AMB_NOSHOW_V2`: no-show and late-cancel probability.
- `MODEL_AMB_BREACH_V2`: urgent breach risk.

All model outputs are synthetic and not validated for clinical decision-making.
