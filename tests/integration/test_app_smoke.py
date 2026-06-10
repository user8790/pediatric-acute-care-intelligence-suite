import py_compile
from pathlib import Path


def test_streamlit_apps_compile():
    files = [
        Path("apps/snowflake_streamlit/inpatient/streamlit_app.py"),
        Path("apps/snowflake_streamlit/ambulatory/streamlit_app.py"),
        Path("apps/snowflake_streamlit/shared/lib/common.py"),
    ]
    for file in files:
        py_compile.compile(str(file), doraise=True)


def test_showcase_entry_files_exist():
    assert Path("apps/showcase/src/App.tsx").exists()
    assert Path("apps/showcase/public/demo-data.json").exists()

