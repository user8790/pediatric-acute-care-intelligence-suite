# Showcase App

Version A is a Vite + React + TypeScript showcase optimized for executive and clinical operations demonstrations.

Run locally:

```powershell
pnpm install
python packages/synthetic/generate_synthetic_data.py
pnpm run dev:showcase
```

The app loads `apps/showcase/public/demo-data.json` and falls back to a bundled small dataset if that file is missing.

Charting approach:

- SVG primitives for forecast bands.
- CSS grid heatmaps for unit pressure.
- Lightweight bar lists for aggregate comparisons.
- No live hospital APIs or patient-level data.

