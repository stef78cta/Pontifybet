"""Constructori de FIXTURE-URI SINTETICE pentru Cornere V14.

Datele produse aici NU sunt observații reale și nu provin din FootyStats sau din
pachetul tehnic: sunt evenimente construite explicit pentru a atinge ramuri pe care
cele trei exemple REPLAY nu le acoperă (cutoff, duplicate, small sample, prior,
egalități de dată, context invalid, praguri de dispersie, OOS).

Valorile așteptate în teste se citesc din rezultatul formulelor originale, nu sunt
praguri rescrise aici.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from src.engines.corners import (
    CornersBatchInput,
    CornersMatchInput,
    CornersMatchResult,
    NativeHistoryRow,
    NativeSource,
    compute_corners_batch,
)

LEAGUE = "Synthetic League"
SEASON = "2025/2026"
PRIOR_SEASON = "2024/2025"
HOME = "Alfa FC"
AWAY = "Beta FC"
OTHERS = ("Gama FC", "Delta FC")
SOURCE_URL = "https://example.invalid/league-matches"


def source_id_for(season: str) -> str:
    """`Istoric_Nativ!S` leagă fiecare eveniment de sursa lui prin `Source_ID`.

    `Row_State` cere ca liga și sezonul sursei să coincidă cu cele ale rândului,
    deci un eveniment de sezon anterior trebuie să indice sursa acelui sezon.
    """
    return f"SYN_{season.replace('/', '_')}"


SOURCE_ID = source_id_for(SEASON)

KICKOFF = datetime(2026, 5, 1, 18, 0)
CUTOFF = datetime(2026, 4, 30, 12, 0)
SEASON_START = date(2025, 8, 1)


def source(
    *,
    season: str = SEASON,
    status: str = "IMPORTED",
    coverage: str = "FULL SEASON EXPORT",
    rows: int = 0,
    missing_corners: int = 0,
    source_id: str | None = None,
    attempts: str = "",
) -> NativeSource:
    return NativeSource(
        source_id=source_id or source_id_for(season),
        league=LEAGUE,
        season=season,
        provider="FootyStats",
        url=SOURCE_URL,
        retrieved_utc=CUTOFF,
        coverage=coverage,
        status=status,
        rows=rows,
        missing_corners=missing_corners,
        attempts=attempts,
        sha256="a" * 64,
    )


def event(
    index: int,
    *,
    match_date: date,
    home: str,
    away: str,
    home_corners: int,
    away_corners: int,
    season: str = SEASON,
    event_id: str | None = None,
    definition: str = "FT90",
) -> NativeHistoryRow:
    return NativeHistoryRow(
        event_id=event_id or f"SYN-{index}",
        league=LEAGUE,
        season=season,
        match_date=match_date,
        home=home,
        away=away,
        home_corners=home_corners,
        away_corners=away_corners,
        source_id=source_id_for(season),
        source_url=SOURCE_URL,
        retrieved_utc=CUTOFF,
        definition=definition,
        evidence="fixture sintetic",
    )


def round_robin(
    *,
    count: int,
    season: str = SEASON,
    first_date: date = SEASON_START,
    step_days: int = 5,
    home_corners: int = 6,
    away_corners: int = 5,
    variation: int = 1,
    teams: tuple[str, ...] = (HOME, AWAY, *OTHERS),
) -> list[NativeHistoryRow]:
    """Sezon sintetic: fiecare echipă joacă alternativ acasă și în deplasare.

    `variation` controlează amplitudinea oscilației cornerelor, deci și dispersia:
    valorile mici rămân în ramura Poisson, cele mari trec în Negative Binomial.
    """
    rows: list[NativeHistoryRow] = []
    index = 0
    day = first_date
    while len(rows) < count:
        for home in teams:
            for away in teams:
                if home == away or len(rows) >= count:
                    continue
                index += 1
                swing = variation * (1 if index % 2 else -1) * (index % 4)
                rows.append(
                    event(
                        index,
                        match_date=day,
                        home=home,
                        away=away,
                        home_corners=max(0, home_corners + swing),
                        away_corners=max(0, away_corners - swing),
                        season=season,
                    )
                )
                day = day + timedelta(days=step_days)
    return rows


def match_input(
    *,
    match_id: str = "SYN1",
    home: str = HOME,
    away: str = AWAY,
    mode: str = "LIVE",
    cutoff_utc: datetime = CUTOFF,
    kickoff_utc: datetime = KICKOFF,
    prior_season: str = "",
    prior_allowed: str = "NO",
    sourcing_decision: str = "AUTO",
    evidence_or_attempts: str = "",
    context: dict[str, float | None] | None = None,
    notes: str = "fixture sintetic",
) -> CornersMatchInput:
    return CornersMatchInput(
        match_id=match_id,
        league=LEAGUE,
        season=SEASON,
        home=home,
        away=away,
        kickoff_utc=kickoff_utc,
        cutoff_utc=cutoff_utc,
        mode=mode,
        sourcing_decision=sourcing_decision,
        evidence_or_attempts=evidence_or_attempts,
        prior_season=prior_season,
        prior_allowed=prior_allowed,
        notes=notes,
        context=context or {},
    )


def oos_record(
    *,
    fixture_id: str,
    line: str = "O3,5",
    total_corners: int = 9,
    p_final: float = 0.95,
    candidate_confidence: float = 95.0,
    dispersion: float = 1.0,
    risk_score: float = 10.0,
    prior_active: str = "NO",
    native_core_count: int = 12,
    candidate_tail: str = "PASS",
    mode: str = "LIVE",
    snapshot: datetime = datetime(2026, 4, 20, 10, 0),
    kickoff: datetime = datetime(2026, 4, 21, 18, 0),
    training_end: datetime = datetime(2026, 4, 19, 0, 0),
    settled: datetime = datetime(2026, 4, 21, 20, 0),
) -> tuple:
    """Un rând `OOS_Predictii` complet, în ordinea coloanelor `OOSTable`.

    Valorile implicite respectă toate condițiile din `Record_Valid`; testele
    modifică un singur câmp pentru a verifica respingerea.
    """
    from src.engines.over05.evaluator import to_serial

    return (
        fixture_id,
        LEAGUE,
        line,
        to_serial(snapshot),
        to_serial(kickoff),
        to_serial(training_end),
        p_final,
        candidate_confidence,
        dispersion,
        risk_score,
        prior_active,
        native_core_count,
        candidate_tail,
        total_corners,
        "https://example.invalid/outcome",
        to_serial(settled),
        "https://example.invalid/evidence",
        "CORNERS_NATIVE_V14|semnatura fixture",
        mode,
    )


def run(
    history: list[NativeHistoryRow],
    *,
    matches: tuple[CornersMatchInput, ...] | None = None,
    sources: tuple[NativeSource, ...] | None = None,
    oos_records: tuple[tuple, ...] = (),
) -> CornersMatchResult:
    """Evaluează un lot sintetic și întoarce rezultatul primului meci."""
    items = matches or (match_input(),)
    batch = CornersBatchInput(
        matches=items,
        history=tuple(history),
        sources=sources or (source(rows=len(history)),),
        oos_records=oos_records,
    )
    return compute_corners_batch(batch).matches[items[0].match_id]


def run_batch(
    history: list[NativeHistoryRow],
    matches: tuple[CornersMatchInput, ...],
    *,
    sources: tuple[NativeSource, ...] | None = None,
    oos_records: tuple[tuple, ...] = (),
) -> dict[str, CornersMatchResult]:
    batch = CornersBatchInput(
        matches=matches,
        history=tuple(history),
        sources=sources or (source(rows=len(history)),),
        oos_records=oos_records,
    )
    return compute_corners_batch(batch).matches


def run_with_cells(
    history: list[NativeHistoryRow],
    *,
    cells: list[str],
    matches: tuple[CornersMatchInput, ...] | None = None,
    sources: tuple[NativeSource, ...] | None = None,
    oos_records: tuple[tuple, ...] = (),
) -> dict[str, object]:
    """Evaluează lotul și întoarce celulele suplimentare cerute, pentru audit."""
    items = matches or (match_input(),)
    batch = CornersBatchInput(
        matches=items,
        history=tuple(history),
        sources=sources or (source(rows=len(history)),),
        oos_records=oos_records,
    )
    return compute_corners_batch(batch, extra_cells=cells).extras
