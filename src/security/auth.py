"""Autentificare simplă pe parolă unică (sesiune Streamlit)."""

from __future__ import annotations

import hmac
import os

from config import settings


def get_app_password() -> str:
    """Citește APP_PASSWORD din mediu sau Streamlit secrets."""
    if settings.APP_PASSWORD:
        return settings.APP_PASSWORD
    try:
        import streamlit as st

        if "APP_PASSWORD" in st.secrets:
            return str(st.secrets["APP_PASSWORD"])
    except Exception:
        pass
    return os.getenv("APP_PASSWORD", "")


def verify_password(candidate: str) -> bool:
    expected = get_app_password()
    if not expected:
        # Dezvoltare: dacă nu e setată parola, permite acces (documentat în README)
        return True
    return hmac.compare_digest(candidate.encode("utf-8"), expected.encode("utf-8"))
