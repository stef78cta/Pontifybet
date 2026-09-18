"""Teste client MOCK."""

from src.api.mock import MockFootyStatsClient
from src.models.match_data import DataStatus


def test_mock_list_leagues():
    client = MockFootyStatsClient()
    leagues = client.list_leagues()
    assert len(leagues) >= 2
    assert "Premier League" in (leagues[0].get("league_name") or "")


def test_mock_matches_and_enrich():
    client = MockFootyStatsClient()
    matches = client.matches_by_date("2026-03-15")
    assert len(matches) == 3
    md = client.enrich_match(matches[0])
    assert md.match_id == "90001"
    assert md.home.name == "Arsenal"
    assert md.home.over05_pct_home.numeric_or_none() == 93
    assert md.source_mode == "mock"


def test_sentinel_minus_one_not_zero():
    client = MockFootyStatsClient()
    matches = client.matches_by_date("2026-03-15")
    madrid = next(m for m in matches if m["id"] == 90003)
    md = client.enrich_match(madrid)
    assert md.odds_ft_over05.value == -1
    assert md.odds_ft_over05.data_status == DataStatus.NOT_AVAILABLE
    assert md.odds_ft_over05.numeric_or_none() is None
    assert md.away.corners_for_overall.value == -1
    assert md.away.corners_for_overall.numeric_or_none() is None
