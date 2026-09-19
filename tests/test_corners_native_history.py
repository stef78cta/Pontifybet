"""Colectarea istoricului nativ FootyStats pentru V14.

Verifică maparea câmpurilor reale ale endpointului `league-matches`, deduplicarea,
paginarea, sentinelele, proveniența declarată și partiționarea pe loturi care
respectă capacitatea fizică a foii `Istoric_Nativ`.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pytest

from src.api.client import FootyStatsError
from src.engines.corners.inputs import MAX_HISTORY_ROWS
from src.models.match_data import MatchData, TeamSideStats
from src.orchestration.native_history import (
    CORNER_DEFINITION,
    build_match_input,
    canonical_labels,
    collect_season_history,
    plan_batches,
    source_url,
)


MOMENT = datetime(2026, 3, 15, 9, 0, tzinfo=timezone.utc)


def fixture(
    fixture_id: int,
    *,
    home: str,
    away: str,
    day: int,
    home_corners: object = 5,
    away_corners: object = 4,
    status: str = "complete",
) -> dict:
    """Un element `league-matches` cu numele de câmpuri folosite de client."""
    return {
        "id": fixture_id,
        "status": status,
        "date_unix": int(datetime(2026, 2, day, 18, 0, tzinfo=timezone.utc).timestamp()),
        "home_name": home,
        "away_name": away,
        "team_a_corners": home_corners,
        "team_b_corners": away_corners,
    }


class _Client:
    def __init__(self, fixtures: list[dict]) -> None:
        self.fixtures = fixtures
        self.calls: list[tuple[int, bool]] = []

    def league_matches(self, season_id: int, page: int = 1, *, all_pages: bool = False):
        self.calls.append((season_id, all_pages))
        return list(self.fixtures)


class _FailingClient:
    def league_matches(self, season_id: int, page: int = 1, *, all_pages: bool = False):
        raise FootyStatsError(
            "Liga nu este în abonament.", technical="HTTP 403 league-matches"
        )


def collect(fixtures: list[dict], client: object | None = None):
    return collect_season_history(
        client or _Client(fixtures),
        2012,
        league="Premier League",
        season="2025/2026",
        retrieved_utc=MOMENT,
    )


# --- Maparea câmpurilor -------------------------------------------------------


def test_fixture_fields_map_to_native_history_columns():
    history = collect([fixture(1, home="Arsenal", away="Chelsea", day=3, home_corners=7, away_corners=2)])
    assert len(history.rows) == 1
    row = history.rows[0]
    assert row.event_id == "FS-1"
    assert row.league == "Premier League"
    assert row.season == "2025/2026"
    assert row.match_date == date(2026, 2, 3)
    assert (row.home, row.away) == ("Arsenal", "Chelsea")
    assert (row.home_corners, row.away_corners) == (7, 2)
    assert row.source_id == "FS_2012"
    assert row.definition == CORNER_DEFINITION
    assert row.evidence == "league-matches season_id=2012 match_id=1"
    assert row.retrieved_utc == MOMENT.replace(tzinfo=None)


def test_history_is_collected_once_per_season_with_full_pagination():
    client = _Client([fixture(1, home="A", away="B", day=3)])
    collect_season_history(
        client, 2012, league="L", season="S", retrieved_utc=MOMENT
    )
    assert client.calls == [(2012, True)]


def test_source_url_is_public_and_carries_no_api_key():
    url = source_url(2012)
    assert url == "https://api.football-data-api.com/league-matches?season_id=2012"
    assert "key" not in url


# --- Date lipsă versus zero ---------------------------------------------------


@pytest.mark.parametrize("sentinel", [-1, -2, "-1", None, "", "abc", 101])
def test_api_sentinels_do_not_become_zero_corners(sentinel):
    history = collect(
        [
            fixture(1, home="A", away="B", day=3, home_corners=sentinel),
            fixture(2, home="C", away="D", day=4),
        ]
    )
    assert [row.event_id for row in history.rows] == ["FS-2"]
    assert history.missing_corners == 1


def test_zero_corners_is_a_real_observation():
    history = collect([fixture(1, home="A", away="B", day=3, home_corners=0, away_corners=0)])
    assert len(history.rows) == 1
    assert (history.rows[0].home_corners, history.rows[0].away_corners) == (0, 0)
    assert history.missing_corners == 0


def test_unfinished_fixtures_are_ignored_not_counted_as_missing():
    history = collect(
        [
            fixture(1, home="A", away="B", day=3, status="incomplete"),
            fixture(2, home="C", away="D", day=4),
        ]
    )
    assert [row.event_id for row in history.rows] == ["FS-2"]
    assert history.total_fixtures == 2
    assert history.complete_fixtures == 1
    assert history.missing_corners == 0


def test_rows_without_teams_or_date_are_reported_as_missing():
    broken = fixture(1, home="", away="B", day=3)
    undated = fixture(2, home="C", away="D", day=4)
    undated["date_unix"] = None
    history = collect([broken, undated, fixture(3, home="E", away="F", day=5)])
    assert [row.event_id for row in history.rows] == ["FS-3"]
    assert history.missing_corners == 2


# --- Deduplicare --------------------------------------------------------------


def test_repeated_fixture_id_is_dropped_once():
    item = fixture(1, home="A", away="B", day=3)
    history = collect([item, dict(item)])
    assert len(history.rows) == 1
    assert history.duplicates_dropped == 1


def test_same_teams_and_date_under_different_ids_is_also_a_duplicate():
    history = collect(
        [
            fixture(1, home="A", away="B", day=3),
            fixture(2, home="A", away="B", day=3, home_corners=6),
        ]
    )
    assert len(history.rows) == 1
    assert history.duplicates_dropped == 1


def test_reverse_fixture_is_not_a_duplicate():
    history = collect(
        [
            fixture(1, home="A", away="B", day=3),
            fixture(2, home="B", away="A", day=10),
        ]
    )
    assert len(history.rows) == 2


# --- Proveniență --------------------------------------------------------------


def test_complete_season_declares_full_export_and_a_real_digest():
    history = collect([fixture(i, home=f"H{i}", away=f"A{i}", day=3 + i) for i in range(1, 6)])
    assert history.source is not None
    assert history.source.coverage == "FULL SEASON EXPORT"
    assert history.source.status == "IMPORTED"
    assert history.source.rows == 5
    assert len(history.source.sha256) == 64
    attempts = json.loads(history.source.attempts)[0]
    assert attempts["endpoint"] == "league-matches"
    assert attempts["all_pages"] is True
    assert attempts["fixtures_returned"] == 5
    assert attempts["page_cap_reached"] is False


def test_digest_tracks_the_accepted_rows():
    base = [fixture(1, home="A", away="B", day=3)]
    first = collect(base)
    same = collect(list(base))
    other = collect([fixture(1, home="A", away="B", day=3, home_corners=9)])
    assert first.source.sha256 == same.source.sha256
    assert first.source.sha256 != other.source.sha256


def test_empty_season_is_not_available_instead_of_full_export():
    history = collect([])
    assert history.source is not None
    assert history.source.status == "NOT AVAILABLE"
    assert history.source.coverage == "PARTIAL"
    assert history.source.rows == 0
    assert history.rows == ()


def test_blocked_access_is_reported_without_fabricated_rows():
    history = collect([], client=_FailingClient())
    assert history.source is not None
    assert history.source.status == "ACCESS BLOCKED"
    assert history.source.coverage == "NOT AVAILABLE"
    assert history.rows == ()
    assert "abonament" in history.error
    assert "403" in json.loads(history.source.attempts)[0]["error"]


# --- Etichete canonice și input de meci --------------------------------------


def _match(match_id: str, *, home: str, away: str, season_id: int | None = 2012) -> MatchData:
    return MatchData(
        match_id=match_id,
        competition_id=2012,
        competition_name="Premier League",
        season="2025/2026",
        season_id=season_id,
        kickoff_utc=datetime(2026, 3, 15, 18, 0, tzinfo=timezone.utc),
        home=TeamSideStats(team_id=1, name=home),
        away=TeamSideStats(team_id=2, name=away),
    )


def test_labels_are_fixed_once_per_season():
    labels = canonical_labels(
        [
            _match("1", home="A", away="B"),
            _match("2", home="C", away="D"),
            _match("3", home="E", away="F", season_id=None),
        ]
    )
    assert labels == {2012: ("Premier League", "2025/2026")}


def test_match_input_is_live_and_keeps_the_prior_disabled():
    item = build_match_input(
        _match("90001", home="Arsenal", away="Chelsea"),
        league="Premier League",
        season="2025/2026",
        cutoff_utc=MOMENT.replace(tzinfo=None),
        sourcing_decision="AUTO",
    )
    assert item.mode == "LIVE"
    assert item.cutoff_utc == MOMENT.replace(tzinfo=None)
    assert item.kickoff_utc == datetime(2026, 3, 15, 18, 0)
    assert item.prior_allowed == "NO"
    assert item.prior_season == ""
    assert item.context == {}


# --- Loturi și capacitate -----------------------------------------------------


def _season_history(rows: int, *, league: str = "L1", season: str = "S1"):
    fixtures = [
        fixture(
            index,
            home="Alpha" if index % 2 else f"T{index}",
            away=f"T{index}" if index % 2 else "Beta",
            day=1 + index % 27,
        )
        for index in range(1, rows + 1)
    ]
    # Datele se repetă la ciclu, deci variem ziua prin decalaj de an ca să evităm
    # deduplicarea pe (ligă, sezon, dată, echipe).
    for offset, item in enumerate(fixtures):
        item["date_unix"] = int(
            datetime(2025, 8, 1, tzinfo=timezone.utc).timestamp() + offset * 86400
        )
    return collect_season_history(
        _Client(fixtures), 2012, league=league, season=season, retrieved_utc=MOMENT
    )


def test_single_batch_keeps_the_workbook_ranking():
    history = _season_history(40)
    matches = [
        build_match_input(
            _match(str(90000 + i), home="Alpha", away="Beta"),
            league="L1",
            season="S1",
            cutoff_utc=MOMENT.replace(tzinfo=None),
            sourcing_decision="AUTO",
        )
        for i in range(3)
    ]
    batches, notes, partitioned = plan_batches(matches, {2012: history}, {})
    assert len(batches) == 1
    assert notes == []
    assert partitioned is False
    assert len(batches[0].history) <= MAX_HISTORY_ROWS
    assert batches[0].sources[0].source_id == "FS_2012"


def test_batch_history_is_filtered_to_the_teams_of_its_matches():
    history = _season_history(60)
    match = build_match_input(
        _match("90001", home="Alpha", away="Beta"),
        league="L1",
        season="S1",
        cutoff_utc=MOMENT.replace(tzinfo=None),
        sourcing_decision="AUTO",
    )
    batches, _, _ = plan_batches([match], {2012: history}, {})
    rows = batches[0].history
    assert rows
    assert all({"Alpha", "Beta"} & set(row.teams()) for row in rows)
    # Toate rândurile relevante pentru cele două echipe rămân în lot.
    expected = [row for row in history.rows if {"Alpha", "Beta"} & set(row.teams())]
    assert len(rows) == len(expected)


def _deep_season(teams: list[str], per_team: int):
    """Istoric în care fiecare echipă din `teams` are `per_team` meciuri proprii."""
    fixtures: list[dict] = []
    fixture_id = 1
    day = 0
    for team in teams:
        for index in range(per_team):
            item = fixture(fixture_id, home=team, away=f"Filler{index}", day=1)
            item["date_unix"] = int(
                datetime(2025, 7, 1, tzinfo=timezone.utc).timestamp() + day * 3600
            )
            fixtures.append(item)
            fixture_id += 1
            day += 1
    return collect_season_history(
        _Client(fixtures), 2012, league="L1", season="S1", retrieved_utc=MOMENT
    )


def test_oversized_analysis_is_partitioned_with_an_explicit_note():
    teams = [f"P{index}" for index in range(1, 9)]
    history = _deep_season(teams, 70)
    assert len(history.rows) == 560 > MAX_HISTORY_ROWS
    matches = [
        build_match_input(
            _match(str(90000 + index), home=teams[index], away=teams[index + 1]),
            league="L1",
            season="S1",
            cutoff_utc=MOMENT.replace(tzinfo=None),
            sourcing_decision="AUTO",
        )
        for index in range(0, len(teams), 2)
    ]
    batches, notes, partitioned = plan_batches(matches, {2012: history}, {})
    assert partitioned is True
    assert len(batches) > 1
    assert all(len(batch.history) <= MAX_HISTORY_ROWS for batch in batches)
    # Nicio pierdere de meci: partiționarea redistribuie, nu elimină.
    assert sum(len(batch.matches) for batch in batches) == len(matches)
    assert any("împărțită în loturi" in note for note in notes)
    # Fiecare meci își păstrează integral rândurile celor două echipe.
    for batch in batches:
        for item in batch.matches:
            wanted = [
                row
                for row in history.rows
                if {item.home, item.away} & set(row.teams())
            ]
            present = [
                row
                for row in batch.history
                if {item.home, item.away} & set(row.teams())
            ]
            assert len(present) == len(wanted)


def test_a_match_needing_more_than_the_sheet_capacity_is_reported_not_truncated():
    history = _deep_season(["Solo", "Rival"], 250)
    match = build_match_input(
        _match("90001", home="Solo", away="Rival"),
        league="L1",
        season="S1",
        cutoff_utc=MOMENT.replace(tzinfo=None),
        sourcing_decision="AUTO",
    )
    batches, notes, _ = plan_batches([match], {2012: history}, {})
    assert batches == ()
    assert len(notes) == 1
    assert "90001" in notes[0]
    assert str(MAX_HISTORY_ROWS) in notes[0]


def test_history_without_a_source_yields_no_batch_rows():
    history = collect([])
    match = build_match_input(
        _match("90001", home="Alpha", away="Beta"),
        league="Premier League",
        season="2025/2026",
        cutoff_utc=MOMENT.replace(tzinfo=None),
        sourcing_decision="NOT AVAILABLE",
    )
    batches, notes, partitioned = plan_batches([match], {2012: history}, {})
    assert notes == []
    assert partitioned is False
    assert batches[0].history == ()
    assert batches[0].sources[0].status == "NOT AVAILABLE"
