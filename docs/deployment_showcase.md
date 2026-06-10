# Showcase Deployment

The showcase is a local React app.

## Validated Local Commands

```powershell
python packages/synthetic/generate_synthetic_data.py
pnpm install
pnpm run dev:showcase
pnpm run build:showcase
```

## Data Refresh

The app reads `apps/showcase/public/demo-data.json`. Regenerate it with:

```powershell
python packages/synthetic/generate_synthetic_data.py
```

## Demo Mode

The app remains demoable without network connectivity because it uses static JSON and a bundled fallback fixture.

