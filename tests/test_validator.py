"""Teste validator."""

from src.api.mock import MockFootyStatsClient
from src.validation.validator import validate_match_for_model


def test_over05_valid_for_arsenal():
    client = MockFootyStatsClient()
    md = client.enrich_match(client.matches_by_date("2026-03-15")[0])
    report = validate_match_for_model(md, "over05")
    assert not report.is_blocked(md.match_id, "over05")


def test_corners_not_blocked_by_missing_aggregated_averages():
    """Mediile agregate lipsă nu mai blochează Cornere V14.

    V14 derivă cele 12 medii native din evenimentele din `Istoric_Nativ`, deci un
    meci fără `cornersAVG_*` din API poate avea totuși istoric nativ complet.
    Lipsa lor rămâne raportată, dar ca observație G1, nu ca blocaj.
    """
    client = MockFootyStatsClient()
    matches = client.matches_by_date("2026-03-15")
    madrid = next(m for m in matches if m["id"] == 90003)
    md = client.enrich_match(madrid)
    report = validate_match_for_model(md, "corners")
    assert not report.is_blocked(md.match_id, "corners")
    indicators = {i.indicator for i in report.issues if not i.blocking}
    assert "home_corners_for_recent" in indicators
    assert all(i.g_level == "G1" for i in report.issues if "corners" in i.indicator)


def test_corners_blocked_without_native_source_identity():
    """Fără sezon FootyStats istoricul nativ nu poate fi colectat: G0 blocant."""
    client = MockFootyStatsClient()
    md = client.enrich_match(client.matches_by_date("2026-03-15")[0])
    md.season_id = None
    report = validate_match_for_model(md, "corners")
    assert report.is_blocked(md.match_id, "corners")
    blocking = report.blocking_for(md.match_id, "corners")
    assert {i.indicator for i in blocking} == {"season_id"}


def test_corners_blocked_without_team_names():
    client = MockFootyStatsClient()
    md = client.enrich_match(client.matches_by_date("2026-03-15")[0])
    md.away.name = ""
    report = validate_match_for_model(md, "corners")
    assert report.is_blocked(md.match_id, "corners")
    assert {i.indicator for i in report.blocking_for(md.match_id, "corners")} == {
        "team_names"
    }


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
