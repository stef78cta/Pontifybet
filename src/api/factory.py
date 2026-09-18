"""Fabrică client FootyStats, fără import circular cu mock/pipeline."""

from __future__ import annotations


def get_client():
    """Returnează clientul live FootyStats."""
    from src.api.client import FootyStatsClient

    return FootyStatsClient()
