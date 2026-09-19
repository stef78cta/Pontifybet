"""Colectarea istoricului nativ de cornere din FootyStats, pentru modelul V14.

V14 nu consumă medii agregate: `Core_Nativ` recalculează cele 12 medii native din
evenimente individuale. Modulul transformă `league-matches` într-un set de rânduri
`Istoric_Nativ` deduplicate, plus metadatele de sursă pe care `Core_Nativ!R` le
verifică (`Coverage`, `Status`, `URL`, `SHA256`, `Retrieved_UTC`).

Colectarea se face o singură dată pe sezon și este reutilizată de toate meciurile
analizei; nu există apel separat pe linie sau pe meci.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Iterable

from src.api.client import MAX_PAGES, FootyStatsError, _unavailable
from src.engines.corners.inputs import (
    MAX_HISTORY_ROWS,
    MAX_MATCHES,
    MAX_SOURCES,
    CornersBatchInput,
    CornersMatchInput,
    NativeHistoryRow,
    NativeSource,
)
from src.models.match_data import MatchData

PROVIDER = "FootyStats"
ENDPOINT = "league-matches"

#: Definiția statistică declarată pentru cornerele FootyStats: total pe meciul
#: regulamentar, egal cu suma reprizelor când `corner_timings_recorded` e activ.
CORNER_DEFINITION = "FT90"

#: Statusul FootyStats pentru care cornerele sunt finale.
COMPLETE_STATUS = "complete"


def source_url(season_id: int) -> str:
    """URL-ul public al sursei, fără cheia API."""
    return f"https://api.football-data-api.com/{ENDPOINT}?season_id={season_id}"


@dataclass
class SeasonHistory:
    """Istoricul nativ al unui sezon plus metadatele lui de proveniență."""

    season_id: int
    league: str
    season: str
    source: NativeSource | None
    rows: tuple[NativeHistoryRow, ...] = ()
    total_fixtures: int = 0
    complete_fixtures: int = 0
    missing_corners: int = 0
    duplicates_dropped: int = 0
    pages: int = 0
    truncated: bool = False
    error: str = ""

    @property
    def key(self) -> tuple[str, str]:
        return (self.league, self.season)

    @property
    def available(self) -> bool:
        return self.source is not None and bool(self.rows)


@dataclass
class CornersSourcingPlan:
    """Loturile de evaluare plus raportul de proveniență al analizei."""

    batches: tuple[CornersBatchInput, ...]
    seasons: dict[int, SeasonHistory]
    match_seasons: dict[str, int]
    notes: list[str] = field(default_factory=list)
    partitioned: bool = False

    def batch_of(self, match_id: str) -> CornersBatchInput | None:
        for batch in self.batches:
            if any(item.match_id == match_id for item in batch.matches):
                return batch
        return None


def _corner_count(value: Any) -> int | None:
    """Cornerele unui meci; sentinelele FootyStats (-1/-2) nu devin zero."""
    if _unavailable(value):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    # `Istoric_Nativ!O` cere întregi în 0–100; orice altceva e dată lipsă.
    if number < 0 or number > 100:
        return None
    return number


def _match_date(date_unix: Any) -> Any:
    if _unavailable(date_unix):
        return None
    try:
        stamp = int(date_unix)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(stamp, tz=timezone.utc).date()


def canonical_labels(matches: Iterable[MatchData]) -> dict[int, tuple[str, str]]:
    """Etichetele (ligă, sezon) folosite în toate foile, derivate o singură dată.

    Egalitatea textuală dintre `Input_Meci`, `Istoric_Nativ` și `Surse_Import` este
    o condiție de model (`Core_Nativ!Q`, `Motor_Meciuri!AR`), deci eticheta nu se
    ia din fiecare payload separat, ci se fixează per sezon.
    """
    labels: dict[int, tuple[str, str]] = {}
    for md in matches:
        season_id = md.season_id
        if season_id is None:
            continue
        key = int(season_id)
        if key in labels:
            continue
        league = str(md.competition_name or "").strip() or f"FS-{key}"
        season = str(md.season or "").strip() or f"FS-{key}"
        labels[key] = (league, season)
    return labels


def collect_season_history(
    client: Any,
    season_id: int,
    *,
    league: str,
    season: str,
    retrieved_utc: datetime | None = None,
) -> SeasonHistory:
    """Descarcă și normalizează istoricul nativ al unui sezon.

    @param client - clientul FootyStats (sau mock) reutilizat de analiză.
    @returns - rândurile acceptate plus starea reală a sursei; o eroare de acces
        produce `Status = ACCESS BLOCKED`, nu rânduri fabricate.
    """
    moment = (retrieved_utc or datetime.now(timezone.utc)).replace(tzinfo=None, microsecond=0)
    url = source_url(season_id)
    try:
        fixtures = client.league_matches(int(season_id), all_pages=True)
    except FootyStatsError as exc:
        return SeasonHistory(
            season_id=season_id,
            league=league,
            season=season,
            source=NativeSource(
                source_id=f"FS_{season_id}",
                league=league,
                season=season,
                provider=PROVIDER,
                url=url,
                retrieved_utc=moment,
                coverage="NOT AVAILABLE",
                status="ACCESS BLOCKED",
                rows=0,
                missing_corners=0,
                attempts=json.dumps(
                    [{"endpoint": ENDPOINT, "season_id": season_id, "error": exc.technical or str(exc)}],
                    ensure_ascii=False,
                ),
                sha256="",
            ),
            error=exc.user_message,
        )

    fixtures = [item for item in fixtures if isinstance(item, dict)]
    total = len(fixtures)
    complete = 0
    missing = 0
    duplicates = 0
    seen_ids: set[str] = set()
    seen_keys: set[tuple[str, str, str, str, str]] = set()
    rows: list[NativeHistoryRow] = []

    for item in sorted(fixtures, key=lambda x: (int(x.get("date_unix") or 0), str(x.get("id")))):
        if str(item.get("status") or "").lower() != COMPLETE_STATUS:
            continue
        complete += 1
        fixture_id = str(item.get("id") or "")
        if not fixture_id or fixture_id in seen_ids:
            duplicates += 1
            continue
        home = str(item.get("home_name") or "").strip()
        away = str(item.get("away_name") or "").strip()
        match_date = _match_date(item.get("date_unix"))
        home_corners = _corner_count(item.get("team_a_corners"))
        away_corners = _corner_count(item.get("team_b_corners"))
        if not home or not away or match_date is None:
            missing += 1
            continue
        if home_corners is None or away_corners is None:
            missing += 1
            continue
        key = (league, season, match_date.strftime("%Y%m%d"), home, away)
        if key in seen_keys:
            duplicates += 1
            continue
        seen_ids.add(fixture_id)
        seen_keys.add(key)
        rows.append(
            NativeHistoryRow(
                event_id=f"FS-{fixture_id}",
                league=league,
                season=season,
                match_date=match_date,
                home=home,
                away=away,
                home_corners=home_corners,
                away_corners=away_corners,
                source_id=f"FS_{season_id}",
                source_url=url,
                retrieved_utc=moment,
                definition=CORNER_DEFINITION,
                evidence=f"{ENDPOINT} season_id={season_id} match_id={fixture_id}",
            )
        )

    pages = max(1, -(-total // 500)) if total else 1
    truncated = pages >= MAX_PAGES
    digest = sha256(
        json.dumps(
            [
                [row.event_id, row.match_date.isoformat(), row.home, row.away,
                 row.home_corners, row.away_corners]
                for row in rows
            ],
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()

    source = NativeSource(
        source_id=f"FS_{season_id}",
        league=league,
        season=season,
        provider=PROVIDER,
        url=url,
        retrieved_utc=moment,
        # `FULL SEASON EXPORT` descrie extragerea completă a programului sezonului;
        # o paginare plafonată rămâne `PARTIAL` și modelul o marchează incompletă.
        coverage="PARTIAL" if truncated or not rows else "FULL SEASON EXPORT",
        status="IMPORTED" if rows else "NOT AVAILABLE",
        rows=len(rows),
        missing_corners=missing,
        attempts=json.dumps(
            [
                {
                    "endpoint": ENDPOINT,
                    "season_id": season_id,
                    "all_pages": True,
                    "fixtures_returned": total,
                    "complete_fixtures": complete,
                    "rows_accepted": len(rows),
                    "missing_corners": missing,
                    "duplicates_dropped": duplicates,
                    "page_cap_reached": truncated,
                }
            ],
            ensure_ascii=False,
        ),
        sha256=digest,
    )
    return SeasonHistory(
        season_id=season_id,
        league=league,
        season=season,
        source=source,
        rows=tuple(rows),
        total_fixtures=total,
        complete_fixtures=complete,
        missing_corners=missing,
        duplicates_dropped=duplicates,
        pages=pages,
        truncated=truncated,
    )


def build_match_input(
    md: MatchData,
    *,
    league: str,
    season: str,
    cutoff_utc: datetime,
    sourcing_decision: str,
    evidence_or_attempts: str = "",
    notes: str = "",
    prior_allowed: str = "NO",
) -> CornersMatchInput:
    """Construiește rândul `Input_Meci` al unui meci LIVE."""
    return CornersMatchInput(
        match_id=str(md.match_id),
        league=league,
        season=season,
        home=str(md.home.name or ""),
        away=str(md.away.name or ""),
        kickoff_utc=md.kickoff_utc.replace(tzinfo=None) if md.kickoff_utc else cutoff_utc,
        cutoff_utc=cutoff_utc,
        mode="LIVE",
        sourcing_decision=sourcing_decision,
        evidence_or_attempts=evidence_or_attempts,
        prior_season="",
        # Priorul de sezon anterior cere un al doilea export complet; aplicația nu
        # îl alimentează, deci rămâne dezactivat, iar modelul raportează sincer
        # eșantionul insuficient dacă sezonul curent nu are minimul cerut.
        prior_allowed=prior_allowed,
        notes=notes,
        context={},
    )


def _history_index(
    histories: dict[tuple[str, str], tuple[NativeHistoryRow, ...]],
) -> dict[tuple[str, str, str], set[int]]:
    """Indexează rândurile pe (ligă, sezon, echipă) pentru filtrarea pe loturi."""
    index: dict[tuple[str, str, str], set[int]] = {}
    for key, rows in histories.items():
        for position, row in enumerate(rows):
            for team in row.teams():
                index.setdefault((key[0], key[1], team), set()).add(position)
    return index


def plan_batches(
    matches: list[CornersMatchInput],
    seasons: dict[int, SeasonHistory],
    match_seasons: dict[str, int],
) -> tuple[tuple[CornersBatchInput, ...], list[str], bool]:
    """Împarte analiza în loturi care respectă capacitatea fizică a șablonului.

    Un lot conține meciuri, istoricul lor nativ și sursele care îl acoperă. Când
    istoricul unui sezon depășește cele 400 de rânduri ale `Istoric_Nativ`,
    meciurile sunt grupate astfel încât fiecare lot să păstreze **integral**
    rândurile echipelor lui: toate filtrele V14 sunt limitate la cele două echipe
    ale meciului, deci partiționarea nu schimbă niciun rezultat pe linie.

    @returns - loturile, notele de limitare și dacă s-a folosit partiționarea.
    """
    notes: list[str] = []
    by_key: dict[tuple[str, str], tuple[NativeHistoryRow, ...]] = {}
    source_by_key: dict[tuple[str, str], NativeSource] = {}
    for history in seasons.values():
        if history.source is not None:
            source_by_key[history.key] = history.source
        if history.rows:
            by_key[history.key] = history.rows
    index = _history_index(by_key)

    batches: list[CornersBatchInput] = []
    current: list[CornersMatchInput] = []
    current_rows: dict[tuple[str, str], set[int]] = {}
    current_sources: dict[tuple[str, str], NativeSource] = {}
    partitioned = False

    def rows_for(match: CornersMatchInput) -> dict[tuple[str, str], set[int]]:
        key = (match.league, match.season)
        wanted: set[int] = set()
        for team in (match.home, match.away):
            wanted |= index.get((key[0], key[1], team), set())
        return {key: wanted} if wanted else {}

    def total_rows(selection: dict[tuple[str, str], set[int]]) -> int:
        return sum(len(positions) for positions in selection.values())

    def flush() -> None:
        nonlocal current, current_rows, current_sources
        if not current:
            return
        history_rows: list[NativeHistoryRow] = []
        for key in sorted(current_rows):
            rows = by_key[key]
            history_rows.extend(rows[position] for position in sorted(current_rows[key]))
        batches.append(
            CornersBatchInput(
                matches=tuple(current),
                history=tuple(history_rows),
                sources=tuple(current_sources[key] for key in sorted(current_sources)),
            )
        )
        current = []
        current_rows = {}
        current_sources = {}

    for match in matches:
        key = (match.league, match.season)
        addition = rows_for(match)
        merged = {k: set(v) for k, v in current_rows.items()}
        for k, positions in addition.items():
            merged.setdefault(k, set()).update(positions)
        sources = dict(current_sources)
        if key in source_by_key:
            sources[key] = source_by_key[key]

        fits = (
            len(current) + 1 <= MAX_MATCHES
            and total_rows(merged) <= MAX_HISTORY_ROWS
            and len(sources) <= MAX_SOURCES
        )
        if not fits and current:
            partitioned = True
            flush()
            merged = {k: set(v) for k, v in addition.items()}
            sources = {key: source_by_key[key]} if key in source_by_key else {}
            fits = total_rows(merged) <= MAX_HISTORY_ROWS

        if not fits:
            notes.append(
                f"{match.match_id}: istoricul nativ al echipelor ({total_rows(merged)} rânduri) "
                f"depășește capacitatea `Istoric_Nativ` ({MAX_HISTORY_ROWS}). "
                "Meciul nu poate fi evaluat fără a tăia date."
            )
            continue

        current.append(match)
        current_rows = merged
        current_sources = sources

    flush()
    if partitioned:
        notes.append(
            "Istoricul nativ a depășit 400 de rânduri pentru o singură trecere; analiza a fost "
            "împărțită în loturi filtrate pe echipele fiecărui meci. Rezultatele pe linie sunt "
            "identice, dar clasamentul Top LIVE este recalculat în Python cu criteriile "
            "`Dashboard!P`, nu preluat din workbook."
        )
    _ = match_seasons
    return tuple(batches), notes, partitioned
