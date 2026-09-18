"""Teste validator."""

from src.api.mock import MockFootyStatsClient
from src.validation.validator import validate_match_for_model


def test_over05_valid_for_arsenal():
    client = MockFootyStatsClient()
    md = client.enrich_match(client.matches_by_date("2026-03-15")[0])
    report = validate_match_for_model(md, "over05")
    assert not report.is_blocked(md.match_id, "over05")


def test_corners_blocked_when_native_missing():
    client = MockFootyStatsClient()
    matches = client.matches_by_date("2026-03-15")
    madrid = next(m for m in matches if m["id"] == 90003)
    md = client.enrich_match(madrid)
    report = validate_match_for_model(md, "corners")
    assert report.is_blocked(md.match_id, "corners")
    reasons = [i.reason for i in report.blocking_for(md.match_id, "corners")]
    assert any("G0 critic" in r for r in reasons)


def test_double_chance_blocked_without_odds():
    client = MockFootyStatsClient()
    matches = client.matches_by_date("2026-03-15")
    madrid = next(m for m in matches if m["id"] == 90003)
    # odds 1X2 still present for madrid; over05 is -1. Force odds missing:
    md = client.enrich_match(madrid)
    md.odds_ft_1.value = -1
    md.odds_ft_1.data_status = md.odds_ft_over05.data_status
    report = validate_match_for_model(md, "double_chance")
    assert report.is_blocked(md.match_id, "double_chance")
