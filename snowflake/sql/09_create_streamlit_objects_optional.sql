-- 09_create_streamlit_objects_optional.sql
-- Optional Streamlit object setup. Primary deployment guide remains Snowsight upload/copy.
--
-- 1. In Snowsight, create a Streamlit app in PEDIATRIC_AHA_DEMO.APP.
-- 2. Upload or paste streamlit_app.py, environment.yml, pages/, and shared/lib/.
-- 3. If using staged files, adapt the template below.

USE DATABASE PEDIATRIC_AHA_DEMO;

CREATE STAGE IF NOT EXISTS APP.STREAMLIT_SOURCE_STAGE
  COMMENT = 'Optional upload location for Streamlit source files.';

-- Template only. Adjust ROOT_LOCATION and MAIN_FILE after uploading source files:
-- CREATE STREAMLIT IF NOT EXISTS APP.INPATIENT_COMMAND_CENTRE
--   ROOT_LOCATION = '@APP.STREAMLIT_SOURCE_STAGE/inpatient'
--   MAIN_FILE = 'streamlit_app.py'
--   QUERY_WAREHOUSE = '<APPROVED_WAREHOUSE>';

-- CREATE STREAMLIT IF NOT EXISTS APP.AMBULATORY_ACCESS_CENTRE
--   ROOT_LOCATION = '@APP.STREAMLIT_SOURCE_STAGE/ambulatory'
--   MAIN_FILE = 'streamlit_app.py'
--   QUERY_WAREHOUSE = '<APPROVED_WAREHOUSE>';

