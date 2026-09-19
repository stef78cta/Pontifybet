"""Setări Pontifybet — citite din mediu / .env (fără secrete în cod)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

TEMPLATES_DIR = ROOT / "templates"
OUTPUTS_DIR = ROOT / "outputs"
CACHE_DIR = ROOT / ".cache"
MOCKS_DIR = ROOT / "mocks"
CONFIG_DIR = ROOT / "config"
REGISTRY_PATH = CONFIG_DIR / "model_registry.yaml"

FOOTYSTATS_BASE_URL = "https://api.football-data-api.com"
FOOTYSTATS_TIMEOUT = float(os.getenv("FOOTYSTATS_TIMEOUT", "20"))
FOOTYSTATS_RETRIES = int(os.getenv("FOOTYSTATS_RETRIES", "2"))
FOOTYSTATS_MAX_WORKERS = int(os.getenv("FOOTYSTATS_MAX_WORKERS", "3"))
FOOTYSTATS_429_BACKOFF_SEC = float(os.getenv("FOOTYSTATS_429_BACKOFF_SEC", "0.6"))

APP_PASSWORD = os.getenv("APP_PASSWORD", "").strip()
DEV_MODULE_RELOAD = os.getenv("DEV_MODULE_RELOAD", "false").strip().lower() in {
    "1",
    "true",
    "yes",
}

DEFAULT_TIMEZONE = "Europe/Bucharest"


def _from_streamlit_secrets(name: str) -> str:
    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name]).strip()
    except Exception:
        return ""
    return ""


def get_footystats_api_key() -> str:
    """Cheia FootyStats din .env / mediu, apoi din Streamlit secrets. Nu loga valoarea."""
    env = os.getenv("FOOTYSTATS_API_KEY", "").strip()
    if env:
        return env
    return _from_streamlit_secrets("FOOTYSTATS_API_KEY")


# Compatibilitate: citire la import (fără secrets Streamlit încărcate).
FOOTYSTATS_API_KEY = get_footystats_api_key()


def ensure_runtime_dirs() -> None:
    """Creează directoarele runtime necesare."""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
