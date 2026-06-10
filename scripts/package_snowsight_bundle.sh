#!/usr/bin/env bash
set -euo pipefail
mkdir -p dist/snowsight_bundle
cp -R apps/snowflake_streamlit/inpatient dist/snowsight_bundle/
cp -R apps/snowflake_streamlit/ambulatory dist/snowsight_bundle/
mkdir -p dist/snowsight_bundle/shared
cp -R apps/snowflake_streamlit/shared/lib dist/snowsight_bundle/shared/
cp apps/snowflake_streamlit/shared/README.md dist/snowsight_bundle/shared/
cp apps/snowflake_streamlit/shared/environment_optional_pending.yml dist/snowsight_bundle/shared/
cp -R snowflake/sql dist/snowsight_bundle/
echo "Snowsight bundle staged in dist/snowsight_bundle"

