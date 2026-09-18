"""Teste pentru listarea meciurilor pe dată + ligă (fără enrich)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from src.api.mock import MockFootyStatsClient
from src.pipeline import list_matches_for_filters, sort_listed_matches


def _ora_bucuresti(date_unix: int) -> str:
    return (
        datetime.fromtimestamp(date_unix, tz=timezone.utc)
        .astimezone(ZoneInfo("Europe/Bucharest"))
        .strftime("%H:%M")
    )


def test_premier_league_only_returns_two_matches():
    client = MockFootyStatsClient()
    rows = list_matches_for_filters(
        date_iso="2026-03-15",
        league_ids=[2012],
        timezone_name="Europe/Bucharest",
        client=client,
    )
    ids = [r["match_id"] for r in rows]
    assert ids == ["90001", "90002"]
    assert all(r["liga"] == "Premier League" for r in rows)
    assert all(r["selected"] is True for r in rows)
    arsenal = next(r for r in rows if r["match_id"] == "90001")
    assert arsenal["echipe"] == "Arsenal vs Chelsea"
    assert arsenal["ora_sort"] == 1773550800
    assert arsenal["ora"] == _ora_bucuresti(1773550800)


def test_both_leagues_returns_three_matches():
    rows = list_matches_for_filters(
        date_iso="2026-03-15",
        league_ids=[2012, 2013],
        timezone_name="Europe/Bucharest",
        client=MockFootyStatsClient(),
    )
    assert [r["match_id"] for r in rows] == ["90001", "90002", "90003"]


def test_unknown_league_returns_empty():
    rows = list_matches_for_filters(
        date_iso="2026-03-15",
        league_ids=[9999],
        timezone_name="Europe/Bucharest",
        client=MockFootyStatsClient(),
    )
    assert rows == []


def test_empty_league_ids_skips_api():
    client = MockFootyStatsClient()
    rows = list_matches_for_filters(
        date_iso="2026-03-15",
        league_ids=[],
        timezone_name="Europe/Bucharest",
        client=client,
    )
    assert rows == []
    assert client._call_counts.get("matches_by_date", 0) == 0


def test_sort_by_league_is_alphabetical():
    rows = list_matches_for_filters(
        date_iso="2026-03-15",
        league_ids=[2012, 2013],
        timezone_name="Europe/Bucharest",
        client=MockFootyStatsClient(),
    )
    sorted_rows = sort_listed_matches(rows, "liga")
    ligi = [r["liga"] for r in sorted_rows]
    assert ligi == ["La Liga", "Premier League", "Premier League"]
    assert sorted_rows[0]["match_id"] == "90003"


def test_sort_by_kickoff_is_chronological():
    rows = list_matches_for_filters(
        date_iso="2026-03-15",
        league_ids=[2012, 2013],
        timezone_name="Europe/Bucharest",
        client=MockFootyStatsClient(),
    )
    sorted_rows = sort_listed_matches(rows, "ora")
    assert [r["match_id"] for r in sorted_rows] == ["90001", "90002", "90003"]


class _LiveShapedClient:
    """todays-matches real nu include league_name, doar competition_id."""

    def matches_by_date(self, *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
        return [
            {
                "id": 1,
                "home_name": "Remo",
                "away_name": "Santos",
                "competition_id": 16544,
                "date_unix": 1773550800,
            }
        ]

    def list_leagues(self, chosen_only: bool = True) -> list[dict[str, Any]]:
        _ = chosen_only
        return [
            {
                "name": "Brazil Serie A",
                "league_name": "Serie A",
                "season": [{"id": 16544, "year": "2026"}],
            }
        ]


def test_live_match_without_league_name_uses_league_list():
    rows = list_matches_for_filters(
        date_iso="2026-09-17",
        league_ids=[16544],
        timezone_name="Europe/Bucharest",
        client=_LiveShapedClient(),
    )
    assert len(rows) == 1
    assert rows[0]["liga"] == "Brazil Serie A"
    assert rows[0]["echipe"] == "Remo vs Santos"


class _MissingUnixClient:
    def matches_by_date(self, *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
        return [
            {
                "id": 42,
                "home_name": "A",
                "away_name": "B",
                "competition_id": 2012,
                "league_name": "Premier League",
                "date_unix": -1,
            }
        ]


def test_missing_date_unix_keeps_row_without_inventing_time():
    rows = list_matches_for_filters(
        date_iso="2026-03-15",
        league_ids=[2012],
        timezone_name="Europe/Bucharest",
        client=_MissingUnixClient(),
    )
    assert len(rows) == 1
    assert rows[0]["match_id"] == "42"
    assert rows[0]["ora"] == ""
    assert rows[0]["ora_sort"] is None
    missing_last = sort_listed_matches(rows + [
        {
            "match_id": "1",
            "liga": "Premier League",
            "ora": "12:00",
            "ora_sort": 1,
            "echipe": "C vs D",
            "selected": True,
        }
    ], "ora")
    assert missing_last[-1]["match_id"] == "42"
