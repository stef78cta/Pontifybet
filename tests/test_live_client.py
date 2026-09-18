"""Teste client real FootyStats cu transport mock (fără rețea, fără cheie reală)."""

from __future__ import annotations

import httpx

from src.api.cache import ResponseCache
from src.api.client import FootyStatsClient, FootyStatsError, current_season_id


def _client(handler) -> FootyStatsClient:
    transport = httpx.MockTransport(handler)
    return FootyStatsClient(
        api_key="test-key",
        retries=0,
        cache=ResponseCache(use_disk=False),
        transport=transport,
    )


def test_current_season_id_picks_latest():
    league = {
        "name": "England Premier League",
        "season": [
            {"id": 1, "year": "2016"},
            {"id": 2012, "year": "2018/2019"},
            {"id": 12325, "year": "2024/2025"},
        ],
    }
    assert current_season_id(league) == 12325


def test_test_call_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/test-call")
        assert "key=" in str(request.url)
        return httpx.Response(
            200,
            json={
                "success": True,
                "data": "Successful Test Call",
                "metadata": {"request_remaining": "1790", "request_limit": "1800"},
            },
        )

    with _client(handler) as client:
        result = client.test_call()
    assert result["ok"] is True
    assert result["request_remaining"] == "1790"


def test_success_false_invalid_key():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"success": False, "message": "Invalid API Key"})

    with _client(handler) as client:
        try:
            client.list_leagues()
            raise AssertionError("trebuia să arunce FootyStatsError")
        except FootyStatsError as exc:
            assert "invalidă" in exc.user_message.lower() or "invalid" in exc.user_message.lower()


def test_matches_pagination_and_timezone():
    seen_pages: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        page = request.url.params.get("page", "1")
        seen_pages.append(page)
        assert request.url.params.get("timezone") == "Europe/Bucharest"
        assert request.url.params.get("date") == "2026-09-17"
        if page == "1":
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "pager": {"current_page": 1, "max_page": 2, "results_per_page": 1, "total_results": 2},
                    "data": [{"id": 1, "home_name": "A", "away_name": "B"}],
                },
            )
        return httpx.Response(
            200,
            json={
                "success": True,
                "pager": {"current_page": 2, "max_page": 2, "results_per_page": 1, "total_results": 2},
                "data": [{"id": 2, "home_name": "C", "away_name": "D"}],
            },
        )

    with _client(handler) as client:
        matches = client.matches_by_date("2026-09-17", timezone_name="Europe/Bucharest")
    assert [m["id"] for m in matches] == [1, 2]
    assert seen_pages == ["1", "2"]


def test_team_filters_competition_id():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "success": True,
                "pager": {"current_page": 1, "max_page": 1, "results_per_page": 25, "total_results": 2},
                "data": [
                    {"id": 59, "name": "Arsenal", "competition_id": 17086, "season_format": "Cup", "stats": {}},
                    {
                        "id": 59,
                        "name": "Arsenal",
                        "competition_id": 12325,
                        "season_format": "Domestic League",
                        "stats": {"seasonMatchesPlayed_overall": 8},
                    },
                ],
            },
        )

    with _client(handler) as client:
        team = client.team(59, competition_id=12325)
    assert team["competition_id"] == 12325
    assert team["stats"]["seasonMatchesPlayed_overall"] == 8


def test_lastx_picks_overall_block():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get("num") == "5"
        return httpx.Response(
            200,
            json={
                "success": True,
                "pager": {"current_page": 1, "max_page": 1, "results_per_page": 50, "total_results": 3},
                "data": [
                    {"last_x_home_away_or_overall": "1", "stats": {"seasonGoals_overall": 99}},
                    {"last_x_home_away_or_overall": "0", "stats": {"seasonGoals_overall": 8, "seasonMatchesPlayed_overall": 5}},
                    {"last_x_home_away_or_overall": "2", "stats": {"seasonGoals_overall": 1}},
                ],
            },
        )

    with _client(handler) as client:
        block = client.last_x(59, 5)
    assert block["stats"]["seasonGoals_overall"] == 8


def test_cache_does_not_include_api_key():
    from src.api.cache import cache_key

    key = cache_key("league-list", {"chosen_leagues_only": "true", "key": "super-secret"})
    assert "super-secret" not in key
    assert len(key) == 64
