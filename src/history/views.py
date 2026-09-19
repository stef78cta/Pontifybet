"""Formatarea istoricului pentru UI.

Trăiește lângă repository, nu în `app.py`, ca testele să poată verifica coloanele
fără să pornească Streamlit — același motiv pentru care există `src/ui_tables.py`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from src.history import repository as repo
from src.history.db import open_db
from src.history.models import CORNERS_MARKETS, Market

MARKET_LABELS = {
    Market.OVER_0_5.value: "Over 0.5",
    Market.DC_1X.value: "Șansă dublă 1X",
    Market.DC_X2.value: "Șansă dublă X2",
    Market.DC_12.value: "Șansă dublă 12",
}

MODEL_LABELS = {
    "over05": "Over 0.5 V4",
    "double_chance": "Șansă Dublă V2",
    "corners": "Cornere Multi-Line V14",
}

NA = "—"


def _market_label(market: str, line: float | None) -> str:
    if market in CORNERS_MARKETS:
        direction = "Over" if market == Market.CORNERS_OVER.value else "Under"
        return f"Cornere {direction} {line:g}" if line is not None else f"Cornere {direction}"
    return MARKET_LABELS.get(market, market)


def _local_datetime(kickoff_unix: int | None, timezone_name: str) -> str:
    """Kickoff-ul în fusul ales; sentinelul FootyStats nu devine o dată inventată."""
    if not kickoff_unix:
        return NA
    local = datetime.fromtimestamp(int(kickoff_unix), tz=timezone.utc).astimezone(
        ZoneInfo(timezone_name)
    )
    return local.strftime("%Y-%m-%d %H:%M")


def _score(row: dict[str, Any]) -> str:
    """Rezultatul afișat: scor și, pentru Cornere, totalul de cornere oficiale."""
    parts: list[str] = []
    if row.get("home_goals") is not None and row.get("away_goals") is not None:
        parts.append(f"{row['home_goals']}-{row['away_goals']}")
    if str(row.get("market") or "") in CORNERS_MARKETS:
        if row.get("total_corners") is not None:
            parts.append(f"{row['total_corners']} cornere")
        else:
            parts.append("cornere NOT AVAILABLE")
    return " | ".join(parts) or NA


def _percent(value: Any) -> str:
    if value is None:
        return NA
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(value)


def history_table_rows(
    rows: list[dict[str, Any]],
    *,
    timezone_name: str = "Europe/Bucharest",
) -> list[dict[str, Any]]:
    """Rândurile tabelului „Istoric și rezultate”, în ordinea cerută de UI."""
    out: list[dict[str, Any]] = []
    for row in rows:
        home = row.get("home_team") or NA
        away = row.get("away_team") or NA
        out.append(
            {
                "Data": _local_datetime(row.get("kickoff_unix"), timezone_name),
                "Liga": row.get("league") or NA,
                "Meci": f"{home} vs {away}",
                "Model": MODEL_LABELS.get(str(row.get("model_key")), row.get("model_key")),
                "Piață/Linie": _market_label(str(row.get("market")), row.get("line")),
                "Recomandare": row.get("recommendation") or NA,
                "Risk Level": row.get("risk_level") if row.get("risk_level") is not None else NA,
                "P ajustată": _percent(row.get("p_adjusted")),
                "Rezultat": _score(row),
                "Outcome": row.get("outcome") or NA,
                "Status": row.get("settlement_status") or row.get("snapshot_status") or NA,
            }
        )
    return out


def load_history(
    *,
    model_keys: list[str] | None = None,
    leagues: list[str] | None = None,
    outcomes: list[str] | None = None,
    limit: int = 1000,
    timezone_name: str = "Europe/Bucharest",
    db_path: str | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Istoricul filtrat plus lista de ligi disponibile pentru filtru."""
    with open_db(db_path) as conn:
        rows = repo.history_rows(
            conn,
            model_keys=model_keys,
            leagues=leagues,
            outcomes=outcomes,
            limit=limit,
        )
        available_leagues = repo.distinct_leagues(conn)
    return history_table_rows(rows, timezone_name=timezone_name), available_leagues
