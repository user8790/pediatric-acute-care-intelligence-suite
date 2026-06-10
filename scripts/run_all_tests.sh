#!/usr/bin/env bash
set -euo pipefail
python packages/synthetic/generate_synthetic_data.py
python -m pytest
pnpm install
pnpm run build:showcase

