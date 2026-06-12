-- Optional Streamlit object placeholders for Snowsight deployment.
USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE STAGE IF NOT EXISTS APP.STREAMLIT_APP_STAGE DIRECTORY = (ENABLE = TRUE);

-- In Snowsight, create Streamlit apps from apps/snowflake_streamlit/* and point
-- them at MART, MODEL, CONFIG, GOVERNANCE, QUALITY, OPEN_DATA, and APP objects.
-- Keep baseline dependencies on the Snowflake Anaconda channel.
