"""Fetch model-aware: league context, lastx dedup, concurență controlată."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from config import settings
from src.api.client import FootyStatsClient, _unavailable, league_goal_averages
from src.api.mock import MockFootyStatsClient
from src.models.match_data import MatchData
from src.orchestration.fetch_plan import needs_league_teams, required_lastx_nums
from src.orchestration.profiler import FetchCounters, RunProfiler


@dataclass(frozen=True)
class LeagueSeasonContext:
    """Context reutilizabil per sezon — teams + medii ligă."""

    season_id: int
    teams: dict[int, dict[str, Any]]
    avg_home: float | None
    avg_away: float | None
    avg_total: float | None
    n_home: float | None
    n_away: float | None


def _season_id(match: dict[str, Any]) -> int | None:
    cid = match.get("competition_id") or match.get("season_id")
    if _unavailable(cid):
        return None
    return int(cid)


def _team_ids_from_matches(matches: list[dict[str, Any]]) -> set[int]:
    ids: set[int] = set()
    for match in matches:
        for key in ("homeID", "home_id", "awayID", "away_id"):
            raw = match.get(key)
            if not _unavailable(raw):
                ids.add(int(raw))
    return ids


def build_league_contexts(
    client: Any,
    matches: list[dict[str, Any]],
    model_ids: list[str],
    counters: FetchCounters,
) -> dict[int, LeagueSeasonContext]:
    """Încarcă league-teams o singură dată per season_id."""
    if not needs_league_teams(model_ids):
        return {}

    season_ids: set[int] = set()
    for match in matches:
        sid = _season_id(match)
        if sid is not None:
            season_ids.add(sid)

    contexts: dict[int, LeagueSeasonContext] = {}
    for season_id in sorted(season_ids):
        counters.league_teams += 1
        raw_teams = client.league_teams(season_id)
        teams = {
            int(t["id"]): t
            for t in raw_teams
            if isinstance(t, dict) and not _unavailable(t.get("id"))
        }
        avg_home, avg_away, avg_total, n_home, n_away = league_goal_averages(list(teams.values()))
        contexts[season_id] = LeagueSeasonContext(
            season_id=season_id,
            teams=teams,
            avg_home=avg_home,
            avg_away=avg_away,
            avg_total=avg_total,
            n_home=n_home,
            n_away=n_away,
        )
    return contexts


def _fetch_lastx_pair(client_factory, team_id: int, num: int) -> tuple[int, int, dict[str, Any]]:
    """Worker: client propriu; ResponseCache partajat este thread-safe."""
    client = client_factory()
    try:
        return team_id, num, client.last_x(team_id, num)
    finally:
        client.close()


def prefetch_lastx(
    client: Any,
    matches: list[dict[str, Any]],
    model_ids: list[str],
    counters: FetchCounters,
) -> dict[tuple[int, int], dict[str, Any]]:
    """Deduplică și încarcă lastx concurent pentru perechile necesare."""
    nums = required_lastx_nums(model_ids)
    if not nums:
        return {}

    team_ids = _team_ids_from_matches(matches)
    pairs = sorted((tid, num) for tid in team_ids for num in sorted(nums))
    if not pairs:
        return {}

    results: dict[tuple[int, int], dict[str, Any]] = {}
    shared_cache = getattr(client, "cache", None)

    def client_factory():
        if isinstance(client, MockFootyStatsClient):
            return client
        if isinstance(client, FootyStatsClient):
            return FootyStatsClient(
                api_key=client.api_key,
                timeout=client.timeout,
                retries=client.retries,
                cache=shared_cache,
            )
        return client

    max_workers = max(1, settings.FOOTYSTATS_MAX_WORKERS)
    if len(pairs) == 1 or max_workers == 1:
        for team_id, num in pairs:
            if num == 5:
                counters.lastx_5 += 1
            elif num == 10:
                counters.lastx_10 += 1
            results[(team_id, num)] = client.last_x(team_id, num)
        return results

    with ThreadPoolExecutor(max_workers=min(max_workers, len(pairs))) as pool:
        futures = [
            pool.submit(_fetch_lastx_pair, client_factory, team_id, num) for team_id, num in pairs
        ]
        for future in as_completed(futures):
            team_id, num, payload = future.result()
            if num == 5:
                counters.lastx_5 += 1
            elif num == 10:
                counters.lastx_10 += 1
            results[(team_id, num)] = payload
    return results


def build_match_data(
    client: Any,
    match: dict[str, Any],
    *,
    model_ids: list[str],
    league_contexts: dict[int, LeagueSeasonContext],
    lastx_cache: dict[tuple[int, int], dict[str, Any]],
    tz_name: str,
    counters: FetchCounters,
) -> MatchData:
    """Construiește MatchData fără apeluri redundante."""
    home_id = match.get("homeID") or match.get("home_id")
    away_id = match.get("awayID") or match.get("away_id")
    season_int = _season_id(match)

    home: dict[str, Any] = {}
    away: dict[str, Any] = {}
    ctx = league_contexts.get(season_int) if season_int is not None else None

    if ctx is not None:
        if not _unavailable(home_id):
            home = ctx.teams.get(int(home_id), {})
        if not _unavailable(away_id):
            away = ctx.teams.get(int(away_id), {})

    if not home and not _unavailable(home_id):
        counters.team += 1
        home = client.team(int(home_id), season_int)
    if not away and not _unavailable(away_id):
        counters.team += 1
        away = client.team(int(away_id), season_int)

    nums = required_lastx_nums(model_ids)
    h5 = lastx_cache.get((int(home_id), 5), {}) if 5 in nums and not _unavailable(home_id) else {}
    a5 = lastx_cache.get((int(away_id), 5), {}) if 5 in nums and not _unavailable(away_id) else {}

    avg_home = avg_away = avg_total = n_home = n_away = None
    if ctx is not None:
        avg_home, avg_away, avg_total = ctx.avg_home, ctx.avg_away, ctx.avg_total
        n_home, n_away = ctx.n_home, ctx.n_away

    md = client.build_match_data(
        match,
        home,
        away,
        h5,
        a5,
        tz_name=tz_name,
        league_avg_gf_home=avg_home,
        league_avg_gf_away=avg_away,
        league_avg_gf_total=avg_total,
        league_sample_n_home=n_home,
        league_sample_n_away=n_away,
    )
    md.source_mode = getattr(md, "source_mode", "live") or "live"
    return md


def enrich_matches_batch(
    client: Any,
    matches: list[dict[str, Any]],
    *,
    model_ids: list[str],
    tz_name: str,
    profiler: RunProfiler | None = None,
) -> list[MatchData]:
    """Orchestrează fetch-ul pentru toate meciurile selectate."""
    counters = profiler.counters if profiler else FetchCounters()

    profiler and profiler.start("league_context")
    contexts = build_league_contexts(client, matches, model_ids, counters)
    profiler and profiler.stop("league_context")

    profiler and profiler.start("lastx")
    lastx_cache = prefetch_lastx(client, matches, model_ids, counters)
    profiler and profiler.stop("lastx")

    profiler and profiler.start("build_match_data")
    out: list[MatchData] = []
    for match in matches:
        out.append(
            build_match_data(
                client,
                match,
                model_ids=model_ids,
                league_contexts=contexts,
                lastx_cache=lastx_cache,
                tz_name=tz_name,
                counters=counters,
            )
        )
    profiler and profiler.stop("build_match_data")
    return out
