"""Backtest minim: interogări read-only peste settlement-uri.

Acesta este **strict stratul de măsurare**. Nu modifică modelele, pragurile sau
calibrările pe baza rezultatelor: o buclă în care măsurătoarea își schimbă propriul
obiect de măsură nu mai este backtest.

Structura este pregătită pentru metrici avansate (Wilson, Brier, log-loss,
calibration curve, failure distribution, OOS înghețat), care cer `p_adjusted` și
outcome-ul binar — ambele sunt deja stocate. Metricile nu sunt implementate încă:
fără volum de settlement-uri, ele ar produce cifre fără sens.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from src.history.db import open_db
from src.history.models import Outcome, SettlementStatus

_SETTLED_JOIN = """
FROM prediction_snapshots p
JOIN settlements s ON s.prediction_id = p.id
WHERE s.settlement_status = ? AND s.outcome IS NOT NULL
"""


def _hit_rate(hit: int, total: int) -> float | None:
    """Rata de succes sau `None` când nu există settlement — nu 0.0."""
    return (hit / total) if total else None


def _aggregate(conn: sqlite3.Connection, group_sql: str, label: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        f"""
        SELECT {group_sql} AS grp,
               COUNT(*) AS settled,
               SUM(CASE WHEN s.outcome = ? THEN 1 ELSE 0 END) AS hit,
               SUM(CASE WHEN s.outcome = ? THEN 1 ELSE 0 END) AS miss
        {_SETTLED_JOIN}
        GROUP BY grp
        ORDER BY settled DESC, grp
        """,
        (Outcome.HIT.value, Outcome.MISS.value, SettlementStatus.SETTLED.value),
    ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        settled = int(row["settled"])
        hit = int(row["hit"] or 0)
        out.append(
            {
                label: row["grp"],
                "settled": settled,
                "hit": hit,
                "miss": int(row["miss"] or 0),
                "hit_rate": _hit_rate(hit, settled),
            }
        )
    return out


def summary(*, db_path: str | None = None) -> dict[str, Any]:
    """Totalul settled / HIT / MISS / hit-rate plus starea settlement-urilor."""
    with open_db(db_path) as conn:
        row = conn.execute(
            f"""
            SELECT COUNT(*) AS settled,
                   SUM(CASE WHEN s.outcome = ? THEN 1 ELSE 0 END) AS hit,
                   SUM(CASE WHEN s.outcome = ? THEN 1 ELSE 0 END) AS miss
            {_SETTLED_JOIN}
            """,
            (Outcome.HIT.value, Outcome.MISS.value, SettlementStatus.SETTLED.value),
        ).fetchone()
        settled = int(row["settled"] or 0)
        hit = int(row["hit"] or 0)
        statuses = {
            str(r["settlement_status"]): int(r["n"])
            for r in conn.execute(
                "SELECT settlement_status, COUNT(*) AS n FROM settlements GROUP BY settlement_status"
            ).fetchall()
        }
        predictions = int(
            conn.execute("SELECT COUNT(*) AS n FROM prediction_snapshots").fetchone()["n"]
        )
        return {
            "predictions": predictions,
            "settled": settled,
            "hit": hit,
            "miss": int(row["miss"] or 0),
            "hit_rate": _hit_rate(hit, settled),
            "by_settlement_status": statuses,
        }


def by_model(*, db_path: str | None = None) -> list[dict[str, Any]]:
    with open_db(db_path) as conn:
        return _aggregate(conn, "p.model_key || ' ' || p.model_version", "model")


def by_risk_level(*, db_path: str | None = None) -> list[dict[str, Any]]:
    with open_db(db_path) as conn:
        return _aggregate(conn, "p.risk_level", "risk_level")


def by_league(*, db_path: str | None = None) -> list[dict[str, Any]]:
    with open_db(db_path) as conn:
        return _aggregate(conn, "IFNULL(p.league, '—')", "league")


def by_corners_line(*, db_path: str | None = None) -> list[dict[str, Any]]:
    """Grupare pe market/linie, relevantă doar pentru Cornere Multi-Line."""
    with open_db(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT p.market || ' ' || IFNULL(CAST(p.line AS TEXT), '') AS grp,
                   COUNT(*) AS settled,
                   SUM(CASE WHEN s.outcome = ? THEN 1 ELSE 0 END) AS hit,
                   SUM(CASE WHEN s.outcome = ? THEN 1 ELSE 0 END) AS miss
            {_SETTLED_JOIN}
              AND p.model_key = 'corners'
            GROUP BY grp
            ORDER BY p.market, p.line
            """,
            (Outcome.HIT.value, Outcome.MISS.value, SettlementStatus.SETTLED.value),
        ).fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            settled = int(row["settled"])
            hit = int(row["hit"] or 0)
            out.append(
                {
                    "market_line": row["grp"],
                    "settled": settled,
                    "hit": hit,
                    "miss": int(row["miss"] or 0),
                    "hit_rate": _hit_rate(hit, settled),
                }
            )
        return out
