"""Client FootyStats (httpx) + mapare către MatchData."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from config import settings
from config.settings import FOOTYSTATS_429_BACKOFF_SEC
from src.api.cache import ResponseCache, cache_key
from src.models.match_data import (
    Indicator,
    MatchData,
    TeamSideStats,
    indicator_from_raw,
)

logger = logging.getLogger(__name__)

MAX_PAGES = 20
OVERALL_LASTX_MARKERS = {"0", "overall", "Overall"}


def current_season_id(league: dict[str, Any]) -> int | None:
    """Alege sezonul cel mai recent din obiectul league-list (nu primul, care e cel mai vechi)."""
    seasons = league.get("season") or []
    if not seasons:
        raw = league.get("id")
        return int(raw) if isinstance(raw, (int, float)) else None

    def year_rank(season: dict[str, Any]) -> int:
        year = str(season.get("year") or "")
        parts = [p for p in year.replace("-", "/").split("/") if p.isdigit()]
        if parts:
            return max(int(p) for p in parts)
        sid = season.get("id")
        return int(sid) if isinstance(sid, (int, float)) else 0

    latest = max(seasons, key=year_rank)
    sid = latest.get("id")
    return int(sid) if isinstance(sid, (int, float)) else None


def _unavailable(value: Any) -> bool:
    return value in (None, "", -1, -2, "-1", "-2")


def _as_number(raw: Any) -> float | None:
    """Extrage un număr din payload FootyStats.

    LIVE: seasonGoals_home/away sunt liste de minute ('25', '90+1'), nu totaluri.
    Totalul numeric e seasonScoredNum_* sau lungimea listei. Mock păstrează int.
    """
    if _unavailable(raw):
        return None
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        try:
            return float(raw.replace(",", "."))
        except ValueError:
            return None
    if isinstance(raw, list):
        return float(len(raw))
    return None


def _first_number(*values: Any) -> float | None:
    """Prima valoare numerică din candidați API, fără a inventa."""
    for value in values:
        number = _as_number(value)
        if number is not None:
            return number
    return None


def _under05_count(stats: dict[str, Any], n_int: int | None) -> Any:
    """Număr 0-0 = Under 0.5; fallback identitar played − Over 0.5."""
    raw = stats.get("seasonUnder05Num_overall")
    if not _unavailable(raw):
        return raw
    over_n = stats.get("seasonOver05Num_overall")
    if n_int is not None and not _unavailable(over_n):
        over_count = _as_number(over_n)
        if over_count is None:
            return None
        return max(0.0, float(n_int) - over_count)
    return None


def league_goal_averages(
    teams: list[dict[str, Any]],
) -> tuple[float | None, float | None, float | None, float | None, float | None]:
    """Medii AJ/AK/AL din league-teams: goluri pe meci gazde, oaspeți și total.

    Agregare din payload-ul oficial, nu valori inventate. AL = AJ + AK când ambele există.
    N prior H/A = suma seasonMatchesPlayed; dacă meciurile lipsesc, numărul de echipe cu rată.
    """
    home_rates: list[float] = []
    away_rates: list[float] = []
    home_matches: list[float] = []
    away_matches: list[float] = []
    for team in teams:
        stats = team.get("stats") if isinstance(team, dict) else None
        if not isinstance(stats, dict):
            continue
        matches_home = _as_number(stats.get("seasonMatchesPlayed_home"))
        matches_away = _as_number(stats.get("seasonMatchesPlayed_away"))
        home_avg = _first_number(stats.get("seasonScoredAVG_home"))
        if home_avg is None:
            goals_home = _first_number(stats.get("seasonScoredNum_home"), stats.get("seasonGoals_home"))
            if goals_home is not None and matches_home is not None and matches_home > 0:
                home_avg = goals_home / matches_home
        away_avg = _first_number(stats.get("seasonScoredAVG_away"))
        if away_avg is None:
            goals_away = _first_number(stats.get("seasonScoredNum_away"), stats.get("seasonGoals_away"))
            if goals_away is not None and matches_away is not None and matches_away > 0:
                away_avg = goals_away / matches_away
        if home_avg is not None:
            home_rates.append(home_avg)
            if matches_home is not None and matches_home > 0:
                home_matches.append(matches_home)
        if away_avg is not None:
            away_rates.append(away_avg)
            if matches_away is not None and matches_away > 0:
                away_matches.append(matches_away)
    avg_home = sum(home_rates) / len(home_rates) if home_rates else None
    avg_away = sum(away_rates) / len(away_rates) if away_rates else None
    avg_total = (avg_home + avg_away) if avg_home is not None and avg_away is not None else None
    n_home = sum(home_matches) if home_matches else (float(len(home_rates)) if home_rates else None)
    n_away = sum(away_matches) if away_matches else (float(len(away_rates)) if away_rates else None)
    return avg_home, avg_away, avg_total, n_home, n_away


def _league_n(raw: Any) -> int | None:
    """N prior din league-teams: doar număr pozitiv real, nu un 30 inventat."""
    number = _as_number(raw)
    if number is None or number <= 0:
        return None
    return int(number)


def _user_message_for_failure(payload: dict[str, Any], status_code: int, endpoint: str) -> str:
    raw = str(payload.get("message") or payload.get("error") or "").lower()
    if status_code in {401, 403} or "invalid" in raw and "key" in raw:
        return "Cheia FootyStats este invalidă. Verifică FOOTYSTATS_API_KEY."
    if status_code == 429 or "limit" in raw or "quota" in raw:
        return "Limita de cereri FootyStats a fost atinsă. Reîncearcă mai târziu."
    if "chosen" in raw or "no league" in raw:
        return "Nu sunt ligi alese în contul FootyStats. Selectează-le din API Settings."
    if status_code >= 400:
        return "FootyStats a returnat o eroare. Încearcă din nou mai târziu."
    return f"FootyStats a refuzat cererea ({endpoint})."


def _pick_lastx_block(data: Any) -> dict[str, Any]:
    """lastx întoarce 3 blocuri (overall/home/away); folosim overall."""
    if isinstance(data, dict):
        return data
    if not isinstance(data, list) or not data:
        return {}
    for item in data:
        if not isinstance(item, dict):
            continue
        marker = str(item.get("last_x_home_away_or_overall", ""))
        if marker in OVERALL_LASTX_MARKERS:
            return item
    first = data[0]
    return first if isinstance(first, dict) else {}


class FootyStatsError(Exception):
    """Eroare controlată pentru UI (mesaj scurt) + detalii tehnice în log."""

    def __init__(self, user_message: str, technical: str = "") -> None:
        super().__init__(user_message)
        self.user_message = user_message
        self.technical = technical


class FootyStatsClient:
    """Conector centralizat: timeout, retry, auth, cache, paginare."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        timeout: float | None = None,
        retries: int | None = None,
        cache: ResponseCache | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        resolved = api_key if api_key is not None else settings.get_footystats_api_key()
        self.api_key = str(resolved).strip()
        self.timeout = timeout if timeout is not None else settings.FOOTYSTATS_TIMEOUT
        self.retries = retries if retries is not None else settings.FOOTYSTATS_RETRIES
        self.cache = cache or ResponseCache(use_disk=True)
        self._client = httpx.Client(
            base_url=settings.FOOTYSTATS_BASE_URL,
            timeout=self.timeout,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> FootyStatsClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """GET JSON envelope {success, pager, data}. Nu loghează cheia."""
        if not self.api_key:
            raise FootyStatsError(
                "Cheia API lipsește. Setează FOOTYSTATS_API_KEY în .env sau secrets.toml.",
                "empty api key",
            )
        query = dict(params or {})
        query["key"] = self.api_key
        key = cache_key(endpoint, query)
        cached = self.cache.get(key)
        if isinstance(cached, dict) and ("success" in cached or "data" in cached or "pager" in cached):
            return cached
        # Cache vechi (doar `data`) — îl ignorăm ca să putem pagina corect.

        last_error: Exception | None = None
        max_attempts = self.retries + 1
        for attempt in range(max_attempts):
            try:
                response = self._client.get(f"/{endpoint}", params=query)
                if response.status_code == 429:
                    technical = f"HTTP 429 on {endpoint}"
                    try:
                        err_payload = response.json()
                    except Exception:
                        err_payload = {}
                    if attempt < max_attempts - 1:
                        time.sleep(FOOTYSTATS_429_BACKOFF_SEC * (attempt + 1))
                        continue
                    if isinstance(err_payload, dict):
                        raise FootyStatsError(
                            _user_message_for_failure(err_payload, response.status_code, endpoint),
                            technical,
                        )
                    raise FootyStatsError(
                        "Limita de cereri FootyStats a fost atinsă. Reîncearcă mai târziu.",
                        technical,
                    )
                if response.status_code >= 400:
                    technical = f"HTTP {response.status_code} on {endpoint}"
                    try:
                        err_payload = response.json()
                    except Exception:
                        err_payload = {}
                    if isinstance(err_payload, dict):
                        raise FootyStatsError(
                            _user_message_for_failure(err_payload, response.status_code, endpoint),
                            technical,
                        )
                    raise FootyStatsError(
                        "FootyStats a returnat o eroare. Încearcă din nou mai târziu.",
                        technical,
                    )
                payload = response.json()
                if not isinstance(payload, dict):
                    raise FootyStatsError(
                        "Răspuns FootyStats invalid.",
                        f"non-dict JSON from {endpoint}",
                    )
                if payload.get("success") is False:
                    raise FootyStatsError(
                        _user_message_for_failure(payload, response.status_code, endpoint),
                        f"success=false on {endpoint}",
                    )
                self.cache.set(key, payload)
                return payload
            except FootyStatsError:
                raise
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("FootyStats request failed attempt=%s endpoint=%s", attempt, endpoint)
                if attempt < self.retries:
                    time.sleep(0.4 * (attempt + 1))
        raise FootyStatsError(
            "Nu am putut contacta FootyStats. Verifică internetul și încearcă din nou.",
            str(last_error) if last_error else "unknown",
        )

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        payload = self._request(endpoint, params)
        return payload.get("data", payload)

    def _get_all_pages(self, endpoint: str, params: dict[str, Any] | None = None) -> list[Any]:
        """Parcurge pager.max_page (plafonat) și concatenează `data`."""
        query = dict(params or {})
        items: list[Any] = []
        page = 1
        while page <= MAX_PAGES:
            query["page"] = page
            payload = self._request(endpoint, query)
            data = payload.get("data", [])
            if isinstance(data, dict):
                return [data] if page == 1 and data else items
            if isinstance(data, list):
                items.extend(data)
            else:
                break
            pager = payload.get("pager") or {}
            max_page = int(pager.get("max_page") or 1)
            if page >= max_page or not data:
                break
            page += 1
        return items

    def test_call(self) -> dict[str, Any]:
        """Verificare cheie + conectivitate (`/test-call`)."""
        payload = self._request("test-call", {})
        meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        return {
            "ok": payload.get("success") is True or payload.get("data") == "Successful Test Call",
            "data": payload.get("data"),
            "request_remaining": meta.get("request_remaining"),
            "request_limit": meta.get("request_limit"),
        }

    def list_leagues(self, chosen_only: bool = True) -> list[dict[str, Any]]:
        params = {"chosen_leagues_only": "true"} if chosen_only else {}
        data = self._get("league-list", params)
        return data if isinstance(data, list) else []

    def matches_by_date(
        self,
        date_yyyy_mm_dd: str,
        page: int = 1,
        *,
        timezone_name: str = "Europe/Bucharest",
        all_pages: bool = True,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "date": date_yyyy_mm_dd,
            "timezone": timezone_name,
        }
        if all_pages:
            return [m for m in self._get_all_pages("todays-matches", params) if isinstance(m, dict)]
        params["page"] = page
        data = self._get("todays-matches", params)
        return data if isinstance(data, list) else []

    def league_season(self, season_id: int) -> dict[str, Any]:
        data = self._get("league-season", {"season_id": season_id})
        if isinstance(data, list) and data:
            first = data[0]
            return first if isinstance(first, dict) else {}
        return data if isinstance(data, dict) else {}

    def league_matches(self, season_id: int, page: int = 1, *, all_pages: bool = False) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"season_id": season_id, "max_per_page": 500}
        if all_pages:
            return [m for m in self._get_all_pages("league-matches", params) if isinstance(m, dict)]
        params["page"] = page
        data = self._get("league-matches", params)
        return data if isinstance(data, list) else []

    def league_teams(self, season_id: int) -> list[dict[str, Any]]:
        data = self._get_all_pages("league-teams", {"season_id": season_id, "include": "stats"})
        return [t for t in data if isinstance(t, dict)]

    def team(self, team_id: int, competition_id: int | None = None) -> dict[str, Any]:
        """
        `/team` poate întoarce mai multe sezoane/competiții pentru același club.
        Filtrăm pe competition_id al meciului, altfel preferăm liga internă.
        """
        items = [t for t in self._get_all_pages("team", {"team_id": team_id, "include": "stats"}) if isinstance(t, dict)]
        if not items:
            return {}
        if not _unavailable(competition_id):
            wanted = int(competition_id)  # type: ignore[arg-type]
            for item in items:
                cid = item.get("competition_id")
                if not _unavailable(cid) and int(cid) == wanted:
                    return item
        for item in items:
            fmt = str(item.get("season_format") or "").lower()
            if "domestic" in fmt and "league" in fmt:
                return item
        return items[0]

    def last_x(self, team_id: int, num: int = 5) -> dict[str, Any]:
        data = self._get("lastx", {"team_id": team_id, "num": num})
        return _pick_lastx_block(data)

    def match_details(self, match_id: int) -> dict[str, Any]:
        data = self._get("match", {"match_id": match_id})
        if isinstance(data, list) and data:
            first = data[0]
            return first if isinstance(first, dict) else {}
        return data if isinstance(data, dict) else {}

    def referee(self, referee_id: int) -> dict[str, Any]:
        data = self._get("referee", {"referee_id": referee_id})
        if isinstance(data, list) and data:
            first = data[0]
            return first if isinstance(first, dict) else {}
        return data if isinstance(data, dict) else {}

    def enrich_match(self, match: dict[str, Any], tz_name: str = "Europe/Bucharest") -> MatchData:
        """Încarcă stats sezon + last 5/10 și construiește MatchData."""
        home_id = match.get("homeID") or match.get("home_id")
        away_id = match.get("awayID") or match.get("away_id")
        competition_id = match.get("competition_id") or match.get("season_id")
        season_int = int(competition_id) if not _unavailable(competition_id) else None

        home: dict[str, Any] = {}
        away: dict[str, Any] = {}
        teams: dict[int, dict[str, Any]] = {}
        if season_int is not None:
            teams = {int(t["id"]): t for t in self.league_teams(season_int) if not _unavailable(t.get("id"))}
            if not _unavailable(home_id):
                home = teams.get(int(home_id), {})
            if not _unavailable(away_id):
                away = teams.get(int(away_id), {})

        if not home and not _unavailable(home_id):
            home = self.team(int(home_id), season_int)
        if not away and not _unavailable(away_id):
            away = self.team(int(away_id), season_int)

        h5 = self.last_x(int(home_id), 5) if not _unavailable(home_id) else {}
        a5 = self.last_x(int(away_id), 5) if not _unavailable(away_id) else {}
        avg_home, avg_away, avg_total, n_home, n_away = league_goal_averages(list(teams.values()))
        md = self.build_match_data(
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
        md.source_mode = "live"
        return md

    def build_match_data(
        self,
        match: dict[str, Any],
        home_stats: dict[str, Any] | None = None,
        away_stats: dict[str, Any] | None = None,
        home_last5: dict[str, Any] | None = None,
        away_last5: dict[str, Any] | None = None,
        tz_name: str = "Europe/Bucharest",
        home_last10: dict[str, Any] | None = None,
        away_last10: dict[str, Any] | None = None,
        league_avg_gf_home: Any = None,
        league_avg_gf_away: Any = None,
        league_avg_gf_total: Any = None,
        league_sample_n_home: Any = None,
        league_sample_n_away: Any = None,
    ) -> MatchData:
        """Construiește MatchData din payload-uri FootyStats."""
        now = datetime.now(timezone.utc)
        home_id = match.get("homeID") or match.get("home_id")
        away_id = match.get("awayID") or match.get("away_id")
        home_name = match.get("home_name") or match.get("homeName") or (home_stats or {}).get("name") or ""
        away_name = match.get("away_name") or match.get("awayName") or (away_stats or {}).get("name") or ""
        date_unix = match.get("date_unix") or match.get("dateUnix")
        kickoff_utc = None
        kickoff_bucharest = None
        if not _unavailable(date_unix):
            kickoff_utc = datetime.fromtimestamp(int(date_unix), tz=timezone.utc)
            kickoff_bucharest = kickoff_utc.astimezone(ZoneInfo(tz_name))

        h_stats = (home_stats or {}).get("stats") or home_stats or {}
        a_stats = (away_stats or {}).get("stats") or away_stats or {}
        endpoint_team = "team"

        def ind(raw: Any, unit: str | None = None, n: int | None = None) -> Indicator:
            return indicator_from_raw(raw, unit=unit, endpoint=endpoint_team, n=n, extracted_at=now)

        def last_block(raw: dict[str, Any] | None, prefix: str) -> dict[str, Indicator]:
            raw = raw or {}
            stats = raw.get("stats") or raw
            n_val = stats.get("played") or stats.get("seasonMatchesPlayed_overall") or raw.get("last_x_match_num") or stats.get("n")
            n_int = int(n_val) if isinstance(n_val, (int, float)) and n_val not in (-1, -2) else None
            return {
                f"{prefix}_n": ind(n_val, "count", n_int),
                f"{prefix}_gf": ind(
                    _first_number(stats.get("seasonScoredNum_overall"), stats.get("seasonGoals_overall"), stats.get("goals_for"), stats.get("gf")),
                    "goals",
                    n_int,
                ),
                f"{prefix}_ga": ind(
                    _first_number(stats.get("seasonConcededNum_overall"), stats.get("seasonConceded_overall"), stats.get("goals_against"), stats.get("ga")),
                    "goals",
                    n_int,
                ),
                f"{prefix}_xgf": ind(stats.get("xg_for_avg") or stats.get("xg_for_avg_overall") or stats.get("xgf"), "xg", n_int),
                f"{prefix}_xga": ind(stats.get("xg_against_avg") or stats.get("xg_against_avg_overall") or stats.get("xga"), "xg", n_int),
                f"{prefix}_fts": ind(stats.get("seasonFTSPercentage_overall"), "percent", n_int),
                f"{prefix}_under05_n": ind(_under05_count(stats, n_int), "count", n_int),
                f"{prefix}_corners_for": ind(stats.get("cornersAVG_overall") or stats.get("corners_for"), "corners", n_int),
                f"{prefix}_corners_against": ind(stats.get("cornersAgainstAVG_overall") or stats.get("corners_against"), "corners", n_int),
            }

        h5 = last_block(home_last5, "last5")
        a5 = last_block(away_last5, "last5")
        h10 = last_block(home_last10, "last10")
        a10 = last_block(away_last10, "last10")

        home = TeamSideStats(
            team_id=int(home_id) if not _unavailable(home_id) else None,
            name=str(home_name),
            matches_played_overall=ind(_first_number(h_stats.get("seasonMatchesPlayed_overall")), "count"),
            matches_played_home=ind(_first_number(h_stats.get("seasonMatchesPlayed_home")), "count"),
            matches_played_away=ind(_first_number(h_stats.get("seasonMatchesPlayed_away")), "count"),
            goals_for_home=ind(_first_number(h_stats.get("seasonScoredNum_home"), h_stats.get("seasonGoals_home")), "goals"),
            goals_against_home=ind(_first_number(h_stats.get("seasonConcededNum_home"), h_stats.get("seasonConceded_home")), "goals"),
            goals_for_away=ind(_first_number(h_stats.get("seasonScoredNum_away"), h_stats.get("seasonGoals_away")), "goals"),
            goals_against_away=ind(_first_number(h_stats.get("seasonConcededNum_away"), h_stats.get("seasonConceded_away")), "goals"),
            xg_for_home=ind(h_stats.get("xg_for_home") or h_stats.get("xg_for_avg_home"), "xg"),
            xg_against_home=ind(h_stats.get("xg_against_home") or h_stats.get("xg_against_avg_home"), "xg"),
            xg_for_away=ind(h_stats.get("xg_for_away") or h_stats.get("xg_for_avg_away"), "xg"),
            xg_against_away=ind(h_stats.get("xg_against_away") or h_stats.get("xg_against_avg_away"), "xg"),
            over05_pct_home=ind(h_stats.get("seasonOver05Percentage_home"), "percent"),
            over05_pct_away=ind(h_stats.get("seasonOver05Percentage_away"), "percent"),
            under05_pct_home=ind(h_stats.get("seasonUnder05Percentage_home"), "percent"),
            under05_pct_away=ind(h_stats.get("seasonUnder05Percentage_away"), "percent"),
            over05_ht_pct_home=ind(h_stats.get("seasonOver05PercentageHT_home"), "percent"),
            over05_ht_pct_away=ind(h_stats.get("seasonOver05PercentageHT_away"), "percent"),
            fts_pct_home=ind(h_stats.get("seasonFTSPercentage_home"), "percent"),
            fts_pct_away=ind(h_stats.get("seasonFTSPercentage_away"), "percent"),
            fts_pct_overall=ind(h_stats.get("seasonFTSPercentage_overall"), "percent"),
            cs_pct_home=ind(h_stats.get("seasonCSPercentage_home"), "percent"),
            cs_pct_away=ind(h_stats.get("seasonCSPercentage_away"), "percent"),
            corners_for_overall=ind(h_stats.get("cornersAVG_overall"), "corners"),
            corners_against_overall=ind(h_stats.get("cornersAgainstAVG_overall"), "corners"),
            corners_for_home=ind(h_stats.get("cornersAVG_home"), "corners"),
            corners_against_home=ind(h_stats.get("cornersAgainstAVG_home"), "corners"),
            corners_for_away=ind(h_stats.get("cornersAVG_away"), "corners"),
            corners_against_away=ind(h_stats.get("cornersAgainstAVG_away"), "corners"),
            last5_n=h5["last5_n"],
            last5_gf=h5["last5_gf"],
            last5_ga=h5["last5_ga"],
            last5_xgf=h5["last5_xgf"],
            last5_xga=h5["last5_xga"],
            last5_fts=h5["last5_fts"],
            last5_under05_n=h5["last5_under05_n"],
            last5_corners_for=h5["last5_corners_for"],
            last5_corners_against=h5["last5_corners_against"],
            last10_n=h10["last10_n"],
            last10_gf=h10["last10_gf"],
            last10_ga=h10["last10_ga"],
        )
        away = TeamSideStats(
            team_id=int(away_id) if not _unavailable(away_id) else None,
            name=str(away_name),
            matches_played_overall=ind(_first_number(a_stats.get("seasonMatchesPlayed_overall")), "count"),
            matches_played_home=ind(_first_number(a_stats.get("seasonMatchesPlayed_home")), "count"),
            matches_played_away=ind(_first_number(a_stats.get("seasonMatchesPlayed_away")), "count"),
            goals_for_home=ind(_first_number(a_stats.get("seasonScoredNum_home"), a_stats.get("seasonGoals_home")), "goals"),
            goals_against_home=ind(_first_number(a_stats.get("seasonConcededNum_home"), a_stats.get("seasonConceded_home")), "goals"),
            goals_for_away=ind(_first_number(a_stats.get("seasonScoredNum_away"), a_stats.get("seasonGoals_away")), "goals"),
            goals_against_away=ind(_first_number(a_stats.get("seasonConcededNum_away"), a_stats.get("seasonConceded_away")), "goals"),
            xg_for_home=ind(a_stats.get("xg_for_home") or a_stats.get("xg_for_avg_home"), "xg"),
            xg_against_home=ind(a_stats.get("xg_against_home") or a_stats.get("xg_against_avg_home"), "xg"),
            xg_for_away=ind(a_stats.get("xg_for_away") or a_stats.get("xg_for_avg_away"), "xg"),
            xg_against_away=ind(a_stats.get("xg_against_away") or a_stats.get("xg_against_avg_away"), "xg"),
            over05_pct_home=ind(a_stats.get("seasonOver05Percentage_home"), "percent"),
            over05_pct_away=ind(a_stats.get("seasonOver05Percentage_away"), "percent"),
            under05_pct_home=ind(a_stats.get("seasonUnder05Percentage_home"), "percent"),
            under05_pct_away=ind(a_stats.get("seasonUnder05Percentage_away"), "percent"),
            over05_ht_pct_home=ind(a_stats.get("seasonOver05PercentageHT_home"), "percent"),
            over05_ht_pct_away=ind(a_stats.get("seasonOver05PercentageHT_away"), "percent"),
            fts_pct_home=ind(a_stats.get("seasonFTSPercentage_home"), "percent"),
            fts_pct_away=ind(a_stats.get("seasonFTSPercentage_away"), "percent"),
            fts_pct_overall=ind(a_stats.get("seasonFTSPercentage_overall"), "percent"),
            cs_pct_home=ind(a_stats.get("seasonCSPercentage_home"), "percent"),
            cs_pct_away=ind(a_stats.get("seasonCSPercentage_away"), "percent"),
            corners_for_overall=ind(a_stats.get("cornersAVG_overall"), "corners"),
            corners_against_overall=ind(a_stats.get("cornersAgainstAVG_overall"), "corners"),
            corners_for_home=ind(a_stats.get("cornersAVG_home"), "corners"),
            corners_against_home=ind(a_stats.get("cornersAgainstAVG_home"), "corners"),
            corners_for_away=ind(a_stats.get("cornersAVG_away"), "corners"),
            corners_against_away=ind(a_stats.get("cornersAgainstAVG_away"), "corners"),
            last5_n=a5["last5_n"],
            last5_gf=a5["last5_gf"],
            last5_ga=a5["last5_ga"],
            last5_xgf=a5["last5_xgf"],
            last5_xga=a5["last5_xga"],
            last5_fts=a5["last5_fts"],
            last5_under05_n=a5["last5_under05_n"],
            last5_corners_for=a5["last5_corners_for"],
            last5_corners_against=a5["last5_corners_against"],
            last10_n=a10["last10_n"],
            last10_gf=a10["last10_gf"],
            last10_ga=a10["last10_ga"],
        )

        return MatchData(
            match_id=str(match.get("id") or match.get("match_id") or ""),
            season_id=match.get("competition_id") or match.get("season_id"),
            competition_id=match.get("competition_id"),
            competition_name=str(match.get("league_name") or match.get("competition_name") or ""),
            season=str(match.get("season") or ""),
            kickoff_utc=kickoff_utc,
            kickoff_bucharest=kickoff_bucharest,
            home=home,
            away=away,
            odds_ft_1=indicator_from_raw(match.get("odds_ft_1"), unit="decimal_odds", endpoint="todays-matches", extracted_at=now),
            odds_ft_x=indicator_from_raw(match.get("odds_ft_x"), unit="decimal_odds", endpoint="todays-matches", extracted_at=now),
            odds_ft_2=indicator_from_raw(match.get("odds_ft_2"), unit="decimal_odds", endpoint="todays-matches", extracted_at=now),
            odds_ft_over05=indicator_from_raw(match.get("odds_ft_over05"), unit="decimal_odds", endpoint="todays-matches", extracted_at=now),
            odds_ft_under05=indicator_from_raw(match.get("odds_ft_under05"), unit="decimal_odds", endpoint="todays-matches", extracted_at=now),
            league_avg_gf_home=indicator_from_raw(
                league_avg_gf_home,
                unit="goals",
                endpoint="league-teams",
                method="derived",
                n=_league_n(league_sample_n_home),
                extracted_at=now,
            ),
            league_avg_gf_away=indicator_from_raw(
                league_avg_gf_away,
                unit="goals",
                endpoint="league-teams",
                method="derived",
                n=_league_n(league_sample_n_away),
                extracted_at=now,
            ),
            league_avg_gf_total=indicator_from_raw(
                league_avg_gf_total,
                unit="goals",
                endpoint="league-teams",
                method="derived",
                n=_league_n(
                    None
                    if league_sample_n_home is None and league_sample_n_away is None
                    else (league_sample_n_home or 0) + (league_sample_n_away or 0)
                ),
                extracted_at=now,
            ),
            round=str(match.get("round") or match.get("game_week") or "") or None,
            source_mode="live",
            extracted_at=now,
        )
