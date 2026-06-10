# Showcase Deployment

The showcase is a modular Vite/React app deployed as a static Vercel site.

## Validated Local Commands

```powershell
python packages/synthetic/generate_synthetic_data.py
python packages/synthetic/generate_v2_showcase_data.py
pnpm install
pnpm run dev:showcase
pnpm run build:showcase
```

## Data Refresh

The v2 app reads app-ready JSON under `apps/showcase/public/data/v2/`. Regenerate it with:

```powershell
python packages/synthetic/generate_v2_showcase_data.py
```

## Demo Mode

The app remains demoable without network connectivity because it uses static JSON and bundled fallback fixtures.

## Vercel

The root `vercel.json` builds from the monorepo root and outputs `apps/showcase/dist`.
