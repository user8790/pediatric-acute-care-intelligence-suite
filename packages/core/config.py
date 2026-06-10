"""Shared configuration constants for synthetic pediatric operations data."""

from __future__ import annotations

from dataclasses import dataclass


AGE_BANDS = [
    "neonate",
    "infant",
    "toddler",
    "preschool",
    "school_age",
    "adolescent",
    "young_adult_transition",
]

SERVICE_LINES = [
    "general_pediatrics",
    "surgery",
    "PICU",
    "NICU",
    "cardiology",
    "oncology",
    "neurology",
    "respiratory",
    "mental_health",
    "rehabilitation_complex_care",
]

AMBULATORY_PROGRAMS = [
    "respiratory",
    "cardiology",
    "neurology",
    "surgery_followup",
    "oncology_survivorship",
    "complex_care",
    "mental_health",
    "diagnostic_procedures",
]

SITES = [
    {
        "site_id": "SITE_STOLLERY_INSPIRED",
        "site_name": "Stollery-inspired pediatric site",
        "zone": "Edmonton zone proxy",
        "latitude": 53.52,
        "longitude": -113.52,
    },
    {
        "site_id": "SITE_ACH_INSPIRED",
        "site_name": "Alberta Children's-inspired pediatric site",
        "zone": "Calgary zone proxy",
        "latitude": 51.06,
        "longitude": -114.13,
    },
    {
        "site_id": "SITE_PROV_NETWORK",
        "site_name": "Provincial pediatric network proxy",
        "zone": "Provincial network",
        "latitude": 52.5,
        "longitude": -113.5,
    },
]


@dataclass(frozen=True)
class SuiteConfig:
    """Small immutable configuration object used across generators and tests."""

    seed: int = 20260610
    start_date: str = "2026-01-01"
    days: int = 120
    output_dir: str = "data/synthetic"
    showcase_public_dir: str = "apps/showcase/public"
    streamlit_sample_dir: str = "apps/snowflake_streamlit/shared/sample_data"
    app_version: str = "0.1.0"

