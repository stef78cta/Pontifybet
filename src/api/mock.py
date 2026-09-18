"""Client MOCK — aceleași metode ca FootyStatsClient, fără apeluri API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config.settings import MOCKS_DIR
from src.api.client import FootyStatsClient
from src.models.match_data import MatchData


class MockFootyStatsClient(FootyStatsClient):
    """Citește răspunsuri locale din mocks/."""

    def __init__(self, mocks_dir: Path | None = None) -> None:
        # Nu apelăm super().__init__ cu cheie — evităm httpx real
        self.api_key = "MOCK"
        self.timeout = 1.0
        self.retries = 0
        self.cache = None  # type: ignore[assignment]
        self._client = None  # type: ignore[assignment]
        self.mocks_dir = mocks_dir or MOCKS_DIR
        self._call_counts: dict[str, int] = {}

    def close(self) -> None:
        return None

    def _load(self, name: str) -> Any:
        path = self.mocks_dir / name
        if not path.exists():
            raise FileNotFoundError(f"Mock lipsă: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _count(self, name: str) -> None:
        self._call_counts[name] = self._call_counts.get(name, 0) + 1

    def list_leagues(self, chosen_only: bool = True) -> list[dict[str, Any]]:
        self._count("list_leagues")
        return self._load("leagues.json")

    def matches_by_date(
        self,
        date_yyyy_mm_dd: str,
        page: int = 1,
        *,
        timezone_name: str = "Europe/Bucharest",
        all_pages: bool = True,
    ) -> list[dict[str, Any]]:
        self._count("matches_by_date")
        _ = timezone_name, all_pages, page
        matches = self._load("matches.json")
        # Filtru simplu pe dată (mock poate avea date_iso)
        out = []
        for m in matches:
            if m.get("date_iso") == date_yyyy_mm_dd or date_yyyy_mm_dd in (
                m.get("date_iso"),
                "2026-03-15",
            ):
                out.append(m)
        return out or matches

    def test_call(self) -> dict[str, Any]:
        self._count("test_call")
        return {"ok": True, "data": "Successful Test Call", "request_remaining": None, "request_limit": None}

    def league_teams(self, season_id: int) -> list[dict[str, Any]]:
        self._count("league_teams")
        teams = self._load("teams.json")
        return [t for t in teams if t.get("competition_id") == season_id] or teams

    def team(self, team_id: int, competition_id: int | None = None) -> dict[str, Any]:
        self._count("team")
        teams = self._load("teams.json")
        for t in teams:
            same_team = t.get("id") == team_id
            same_season = competition_id is None or t.get("competition_id") == competition_id
            if same_team and same_season:
                return t
        return teams[0] if teams else {}

    def last_x(self, team_id: int, num: int = 5) -> dict[str, Any]:
        self._count("last_x")
        data = self._load("lastx.json")
        key = f"{team_id}_{num}"
        return data.get(key) or data.get(str(team_id)) or data.get("default") or {}

    def match_details(self, match_id: int) -> dict[str, Any]:
        self._count("match_details")
        details = self._load("match_details.json")
        return details.get(str(match_id)) or details.get("default") or {}

    def referee(self, referee_id: int) -> dict[str, Any]:
        self._count("referee")
        return {"id": referee_id, "full_name": "Mock Referee"}

    def enrich_match(self, match: dict[str, Any], tz_name: str = "Europe/Bucharest") -> MatchData:
        """Încarcă stats + last5 și construiește MatchData."""
        home_id = match.get("homeID")
        away_id = match.get("awayID")
        home = self.team(int(home_id)) if home_id else {}
        away = self.team(int(away_id)) if away_id else {}
        h5 = self.last_x(int(home_id), 5) if home_id else {}
        a5 = self.last_x(int(away_id), 5) if away_id else {}
        md = self.build_match_data(match, home, away, h5, a5, tz_name=tz_name)
        md.source_mode = "mock"
        return md


def get_client() -> FootyStatsClient | MockFootyStatsClient:
    """Returnează MOCK sau client real în funcție de setări."""
    from config.settings import is_mock_mode

    if is_mock_mode():
        return MockFootyStatsClient()
    return FootyStatsClient()
