"""Actualizarea rezultatelor și rularea settlement-ului.

Complet separat de `run_analysis`: forecastul și rezultatul sunt două fluxuri
diferite, cu momente diferite și cu garanții diferite. Această funcție nu atinge
niciodată `prediction_snapshots` — scrie doar în `match_results` și `settlements`.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import config.settings as settings
from src.api.client import FootyStatsError
from src.api.factory import get_client
from src.history import repository as repo
from src.history.db import open_db
from src.history.models import (
    MatchResult,
    SettlementStatus,
    UpdateResultsSummary,
)
from src.history.settlement import settle_prediction

logger = logging.getLogger(__name__)

# Sentinelele FootyStats înseamnă NOT AVAILABLE, nu zero.
_SENTINELS = {None, "", -1, -2, "-1", "-2"}


def _available_int(raw: Any) -> int | None:
    """Întreg oficial FootyStats sau `None`; `-1`/`-2` nu devin 0."""
    if raw in _SENTINELS or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return int(raw)
    if isinstance(raw, str):
        try:
            return int(float(raw.strip()))
        except ValueError:
            return None
    return None


def match_result_from_payload(provider_match_id: str, payload: dict[str, Any]) -> MatchResult:
    """Mapează răspunsul `/match` FootyStats pe `MatchResult`.

    Câmpurile sunt cele documentate de FootyStats pentru endpoint-ul Match Details:
    `status` ('complete' / 'incomplete' / 'suspended' / 'canceled'),
    `homeGoalCount` / `awayGoalCount` pentru scorul final și
    `team_a_corners` / `team_b_corners` pentru cornerele oficiale.

    Atenție: `homeGoals` / `awayGoals` sunt liste de minute, nu totaluri, deci nu
    pot fi folosite ca scor.
    """
    home_goals = _available_int(payload.get("homeGoalCount"))
    away_goals = _available_int(payload.get("awayGoalCount"))
    home_corners = _available_int(payload.get("team_a_corners"))
    away_corners = _available_int(payload.get("team_b_corners"))
    total_goals = (
        home_goals + away_goals if home_goals is not None and away_goals is not None else None
    )
    total_corners = (
        home_corners + away_corners
        if home_corners is not None and away_corners is not None
        else None
    )
    status = payload.get("status")
    return MatchResult(
        provider_match_id=str(provider_match_id),
        match_status=str(status).strip().lower() if status not in _SENTINELS else None,
        home_goals=home_goals,
        away_goals=away_goals,
        total_goals=total_goals,
        home_corners=home_corners,
        away_corners=away_corners,
        total_corners=total_corners,
        source_endpoint="match",
    )


def _now_unix(now_unix: int | None) -> int:
    if now_unix is not None:
        return int(now_unix)
    return int(datetime.now(timezone.utc).timestamp())


def update_results(
    *,
    client: Any | None = None,
    now_unix: int | None = None,
    db_path: str | None = None,
    settle_delay_sec: int | None = None,
) -> UpdateResultsSummary:
    """Preia rezultatele oficiale ale meciurilor încheiate și rulează settlement-ul.

    Un meci este interogat o singură dată, chiar dacă are 14 linii Cornere plus
    Over 0.5 și trei selecții Șansă Dublă: rezultatul este reutilizat pentru toate
    predicțiile lui.

    @param client - client FootyStats; implicit cel din `src/api/factory.py`.
    @param now_unix - „acum” injectabil, pentru teste deterministe.
    @param settle_delay_sec - cât timp după kickoff considerăm meciul încheiat.
    @returns {UpdateResultsSummary} - contoare pentru UI, plus erori nefatale.
    """
    delay = (
        settle_delay_sec
        if settle_delay_sec is not None
        else getattr(settings, "RESULT_SETTLE_DELAY_SEC", 9000)
    )
    cutoff = _now_unix(now_unix) - int(delay)
    summary = UpdateResultsSummary()

    owned = client is None
    active = get_client() if owned else client
    try:
        with open_db(db_path) as conn:
            pending = repo.unsettled_predictions(conn, before_unix=cutoff)
            summary.pending_predictions = len(pending)

            by_match: dict[str, list[dict[str, Any]]] = {}
            for row in pending:
                by_match.setdefault(str(row["provider_match_id"]), []).append(row)

            for provider_match_id, predictions in by_match.items():
                result = None
                try:
                    payload = active.match_details(int(provider_match_id))
                    summary.matches_queried += 1
                    result = match_result_from_payload(provider_match_id, payload or {})
                    repo.upsert_match_result(conn, result)
                    summary.results_updated += 1
                except FootyStatsError as exc:
                    summary.errors.append(f"Meci {provider_match_id}: {exc.user_message}")
                except (TypeError, ValueError) as exc:
                    summary.errors.append(f"Meci {provider_match_id}: ID invalid ({exc}).")
                except Exception as exc:  # noqa: BLE001 - un meci nu blochează restul
                    logger.warning("update_results failed match=%s", provider_match_id)
                    summary.errors.append(f"Meci {provider_match_id}: {exc}")

                if result is None:
                    result = repo.get_match_result(conn, provider_match_id)

                for row in predictions:
                    decision = settle_prediction(
                        market=str(row["market"]),
                        line=row["line"],
                        result=result,
                    )
                    repo.upsert_settlement(conn, int(row["id"]), decision)
                    if decision.settlement_status == SettlementStatus.SETTLED.value:
                        if decision.outcome == "HIT":
                            summary.hit += 1
                        else:
                            summary.miss += 1
                    elif decision.settlement_status == (
                        SettlementStatus.RESULT_DATA_UNAVAILABLE.value
                    ):
                        summary.result_data_unavailable += 1

            summary.still_pending = repo.count_pending_settlement(conn)
    finally:
        if owned:
            try:
                active.close()
            except Exception:  # noqa: BLE001
                pass
    return summary


def pending_count(*, db_path: str | None = None) -> int:
    """Câte predicții înghețate mai așteaptă un settlement final."""
    with open_db(db_path) as conn:
        return repo.count_pending_settlement(conn)
