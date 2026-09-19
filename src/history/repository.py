"""Repository pentru rulări, predicții, rezultate și settlements.

Singurul modul care conține SQL. Regulile de settlement stau în `settlement.py`,
orchestrarea în `results.py`, iar UI-ul în `app.py` — separarea există ca o
schimbare de schemă să nu ceară modificări în interfață și invers.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Iterable, Sequence

from src.history.db import utc_now_iso
from src.history.models import (
    MatchResult,
    PredictionKey,
    PredictionSnapshot,
    SettlementDecision,
    SettlementStatus,
    SnapshotStatus,
    line_key,
)

# Coloanele care descriu verdictul; se scriu o singură dată, la îngheț.
_VERDICT_COLUMNS: tuple[str, ...] = (
    "recommendation",
    "p_adjusted",
    "failure_mode",
    "risk_score",
    "risk_level",
    "confidence",
    "confidence_label",
    "data_status",
    "hard_gate",
    "motivation",
)


class FrozenSnapshotError(RuntimeError):
    """Ridicată când se încearcă rescrierea unei predicții FROZEN_PREMATCH."""


def upsert_run(
    conn: sqlite3.Connection,
    *,
    analysis_date: str,
    timezone_name: str,
    analysis_fingerprint: str,
    run_status: str = "COMPLETED",
    source_mode: str | None = None,
    model_ids: Sequence[str] | None = None,
) -> int:
    """Salvează (sau reutilizează) rularea identificată prin fingerprint.

    Aceeași analiză regenerată cu parametri identici nu creează o a doua rulare:
    fingerprint-ul pipeline-ului este identitatea stabilă a parametrilor.
    """
    models = ",".join(model_ids or [])
    now = utc_now_iso()
    with conn:
        conn.execute(
            """
            INSERT INTO analysis_runs (
                created_at, analysis_date, timezone, run_status,
                source_mode, model_ids, analysis_fingerprint
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(analysis_fingerprint) DO UPDATE SET
                run_status = excluded.run_status,
                source_mode = excluded.source_mode,
                model_ids = excluded.model_ids
            """,
            (now, analysis_date, timezone_name, run_status, source_mode, models, analysis_fingerprint),
        )
    row = conn.execute(
        "SELECT id FROM analysis_runs WHERE analysis_fingerprint = ?",
        (analysis_fingerprint,),
    ).fetchone()
    return int(row["id"])


def get_run(conn: sqlite3.Connection, run_id: int) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM analysis_runs WHERE id = ?", (run_id,)).fetchone()
    return dict(row) if row else None


def find_prediction(
    conn: sqlite3.Connection, key: PredictionKey
) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT * FROM prediction_snapshots
        WHERE provider_match_id = ? AND model_key = ? AND model_version = ?
          AND market = ? AND line_key = ?
        """,
        (key.provider_match_id, key.model_key, key.model_version, key.market, key.line_key),
    ).fetchone()
    return dict(row) if row else None


def save_prediction(
    conn: sqlite3.Connection,
    run_id: int,
    snapshot: PredictionSnapshot,
) -> tuple[int, bool]:
    """Inserează predicția dacă identitatea ei nu există deja.

    Returnează `(id, created)`. O predicție existentă nu este niciodată rescrisă:
    primul forecast înghețat pentru un meci × model × piață/linie este cel care
    contează, iar re-rularea aceleiași analize trebuie să fie fără efect.
    """
    now = utc_now_iso()
    existing = find_prediction(conn, snapshot.key)
    if existing is not None:
        return int(existing["id"]), False

    frozen = snapshot.snapshot_status == SnapshotStatus.FROZEN_PREMATCH.value
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO prediction_snapshots (
                run_id, provider_match_id, kickoff_utc, kickoff_unix, league,
                home_team, away_team, model_key, model_version, market, line, line_key,
                recommendation, p_adjusted, failure_mode, risk_score, risk_level,
                confidence, confidence_label, data_status, hard_gate, motivation,
                frozen_at, snapshot_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider_match_id, model_key, model_version, market, line_key)
                DO NOTHING
            """,
            (
                run_id,
                snapshot.provider_match_id,
                snapshot.kickoff_utc,
                snapshot.kickoff_unix,
                snapshot.league,
                snapshot.home_team,
                snapshot.away_team,
                snapshot.model_key,
                snapshot.model_version,
                snapshot.market,
                snapshot.line,
                snapshot.key.line_key,
                snapshot.recommendation,
                snapshot.p_adjusted,
                snapshot.failure_mode,
                snapshot.risk_score,
                snapshot.risk_level,
                snapshot.confidence,
                snapshot.confidence_label,
                snapshot.data_status,
                snapshot.hard_gate,
                snapshot.motivation,
                now if frozen else None,
                snapshot.snapshot_status,
                now,
                now,
            ),
        )
    # `rowcount`, nu `lastrowid`: la un conflict rezolvat cu DO NOTHING, `lastrowid`
    # poate păstra rowid-ul unui insert anterior pe aceeași conexiune.
    if cursor.rowcount == 1 and cursor.lastrowid:
        return int(cursor.lastrowid), True
    again = find_prediction(conn, snapshot.key)
    return (int(again["id"]), False) if again else (0, False)


def freeze_prediction(
    conn: sqlite3.Connection,
    prediction_id: int,
    *,
    values: dict[str, Any],
) -> bool:
    """Completează verdictul unei predicții PENDING_EXCEL_RECALC și o îngheață.

    Este singura cale prin care valorile finale ale unui model calculat de
    Microsoft Excel intră în istoric. O predicție deja FROZEN_PREMATCH nu se
    atinge — trigger-ul din schemă ar aborta oricum tranzacția.
    """
    row = conn.execute(
        "SELECT snapshot_status FROM prediction_snapshots WHERE id = ?",
        (prediction_id,),
    ).fetchone()
    if row is None:
        return False
    if row["snapshot_status"] == SnapshotStatus.FROZEN_PREMATCH.value:
        return False

    now = utc_now_iso()
    # Doar cheile transmise explicit sunt scrise: o cheie absentă nu trebuie să
    # șteargă o valoare deja cunoscută (ex. `data_status` venit din validator).
    columns = [col for col in _VERDICT_COLUMNS if col in values]
    assignments = ", ".join(f"{col} = ?" for col in columns)
    if assignments:
        assignments += ", "
    params: list[Any] = [values[col] for col in columns]
    params.extend([now, SnapshotStatus.FROZEN_PREMATCH.value, now, prediction_id])
    with conn:
        conn.execute(
            f"""
            UPDATE prediction_snapshots
            SET {assignments}frozen_at = ?, snapshot_status = ?, updated_at = ?
            WHERE id = ?
            """,
            params,
        )
    return True


def assert_not_frozen(conn: sqlite3.Connection, prediction_id: int) -> None:
    row = conn.execute(
        "SELECT snapshot_status FROM prediction_snapshots WHERE id = ?",
        (prediction_id,),
    ).fetchone()
    if row is not None and row["snapshot_status"] == SnapshotStatus.FROZEN_PREMATCH.value:
        raise FrozenSnapshotError(
            "FROZEN_PREMATCH imuabil: predicția pre-match nu poate fi modificată."
        )


def upsert_match_result(conn: sqlite3.Connection, result: MatchResult) -> None:
    """Salvează rezultatul oficial; un meci are exact un rând, deci re-rularea
    actualizării nu poate crea duplicate."""
    now = utc_now_iso()
    with conn:
        conn.execute(
            """
            INSERT INTO match_results (
                provider_match_id, match_status, home_goals, away_goals, total_goals,
                home_corners, away_corners, total_corners, source_endpoint, result_fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider_match_id) DO UPDATE SET
                match_status = excluded.match_status,
                home_goals = excluded.home_goals,
                away_goals = excluded.away_goals,
                total_goals = excluded.total_goals,
                home_corners = excluded.home_corners,
                away_corners = excluded.away_corners,
                total_corners = excluded.total_corners,
                source_endpoint = excluded.source_endpoint,
                result_fetched_at = excluded.result_fetched_at
            """,
            (
                result.provider_match_id,
                result.match_status,
                result.home_goals,
                result.away_goals,
                result.total_goals,
                result.home_corners,
                result.away_corners,
                result.total_corners,
                result.source_endpoint,
                now,
            ),
        )


def get_match_result(conn: sqlite3.Connection, provider_match_id: str) -> MatchResult | None:
    row = conn.execute(
        "SELECT * FROM match_results WHERE provider_match_id = ?",
        (str(provider_match_id),),
    ).fetchone()
    if row is None:
        return None
    return MatchResult(
        provider_match_id=row["provider_match_id"],
        match_status=row["match_status"],
        home_goals=row["home_goals"],
        away_goals=row["away_goals"],
        total_goals=row["total_goals"],
        home_corners=row["home_corners"],
        away_corners=row["away_corners"],
        total_corners=row["total_corners"],
        source_endpoint=row["source_endpoint"],
    )


def upsert_settlement(
    conn: sqlite3.Connection,
    prediction_id: int,
    decision: SettlementDecision,
) -> None:
    """Un settlement pe predicție (UNIQUE), deci actualizarea repetată a
    rezultatelor nu produce rânduri duplicate."""
    now = utc_now_iso()
    settled_at = now if decision.settlement_status == SettlementStatus.SETTLED.value else None
    with conn:
        conn.execute(
            """
            INSERT INTO settlements (
                prediction_id, settlement_status, outcome, settled_at,
                settlement_reason, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(prediction_id) DO UPDATE SET
                settlement_status = excluded.settlement_status,
                outcome = excluded.outcome,
                settled_at = COALESCE(settlements.settled_at, excluded.settled_at),
                settlement_reason = excluded.settlement_reason,
                updated_at = excluded.updated_at
            """,
            (
                prediction_id,
                decision.settlement_status,
                decision.outcome,
                settled_at,
                decision.settlement_reason,
                now,
            ),
        )


def get_settlement(conn: sqlite3.Connection, prediction_id: int) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM settlements WHERE prediction_id = ?", (prediction_id,)
    ).fetchone()
    return dict(row) if row else None


def unsettled_predictions(
    conn: sqlite3.Connection,
    *,
    before_unix: int | None = None,
) -> list[dict[str, Any]]:
    """Predicțiile înghețate care încă așteaptă un settlement final.

    `before_unix` filtrează meciurile care ar fi trebuit deja să se termine, ca
    să nu interogăm FootyStats pentru meciuri încă neîncepute. Predicțiile fără
    kickoff (sentinel FootyStats) nu sunt incluse: nu inventăm o dată.
    """
    sql = [
        """
        SELECT p.*, s.settlement_status, s.outcome
        FROM prediction_snapshots p
        LEFT JOIN settlements s ON s.prediction_id = p.id
        WHERE p.snapshot_status = ?
          AND (s.settlement_status IS NULL OR s.settlement_status != ?)
          AND p.kickoff_unix IS NOT NULL
        """
    ]
    params: list[Any] = [SnapshotStatus.FROZEN_PREMATCH.value, SettlementStatus.SETTLED.value]
    if before_unix is not None:
        sql.append("AND p.kickoff_unix <= ?")
        params.append(int(before_unix))
    sql.append("ORDER BY p.kickoff_unix, p.provider_match_id, p.model_key, p.market, p.line")
    rows = conn.execute("\n".join(sql), params).fetchall()
    return [dict(r) for r in rows]


def predictions_for_match(
    conn: sqlite3.Connection,
    provider_match_id: str,
    *,
    only_frozen: bool = True,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM prediction_snapshots WHERE provider_match_id = ?"
    params: list[Any] = [str(provider_match_id)]
    if only_frozen:
        sql += " AND snapshot_status = ?"
        params.append(SnapshotStatus.FROZEN_PREMATCH.value)
    sql += " ORDER BY model_key, market, line"
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def pending_excel_recalc(
    conn: sqlite3.Connection,
    *,
    model_key: str | None = None,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM prediction_snapshots WHERE snapshot_status = ?"
    params: list[Any] = [SnapshotStatus.PENDING_EXCEL_RECALC.value]
    if model_key:
        sql += " AND model_key = ?"
        params.append(model_key)
    sql += " ORDER BY provider_match_id, market, line"
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def count_pending_settlement(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        """
        SELECT COUNT(*) AS n
        FROM prediction_snapshots p
        LEFT JOIN settlements s ON s.prediction_id = p.id
        WHERE p.snapshot_status = ?
          AND (s.settlement_status IS NULL OR s.settlement_status != ?)
        """,
        (SnapshotStatus.FROZEN_PREMATCH.value, SettlementStatus.SETTLED.value),
    ).fetchone()
    return int(row["n"])


def history_rows(
    conn: sqlite3.Connection,
    *,
    model_keys: Iterable[str] | None = None,
    leagues: Iterable[str] | None = None,
    outcomes: Iterable[str] | None = None,
    limit: int = 1000,
) -> list[dict[str, Any]]:
    """Istoricul complet pentru tabelul din UI (read-only)."""
    sql = [
        """
        SELECT
            p.id AS prediction_id,
            p.provider_match_id,
            p.kickoff_utc,
            p.kickoff_unix,
            p.league,
            p.home_team,
            p.away_team,
            p.model_key,
            p.model_version,
            p.market,
            p.line,
            p.recommendation,
            p.risk_level,
            p.p_adjusted,
            p.snapshot_status,
            r.match_status,
            r.home_goals,
            r.away_goals,
            r.home_corners,
            r.away_corners,
            r.total_corners,
            s.settlement_status,
            s.outcome,
            s.settlement_reason
        FROM prediction_snapshots p
        LEFT JOIN match_results r ON r.provider_match_id = p.provider_match_id
        LEFT JOIN settlements s ON s.prediction_id = p.id
        WHERE 1 = 1
        """
    ]
    params: list[Any] = []
    models = list(model_keys or [])
    if models:
        sql.append(f"AND p.model_key IN ({','.join('?' * len(models))})")
        params.extend(models)
    league_list = list(leagues or [])
    if league_list:
        sql.append(f"AND IFNULL(p.league, '') IN ({','.join('?' * len(league_list))})")
        params.extend(league_list)
    outcome_list = list(outcomes or [])
    if outcome_list:
        sql.append(f"AND IFNULL(s.outcome, '') IN ({','.join('?' * len(outcome_list))})")
        params.extend(outcome_list)
    sql.append("ORDER BY IFNULL(p.kickoff_unix, 0) DESC, p.id DESC LIMIT ?")
    params.append(int(limit))
    return [dict(r) for r in conn.execute("\n".join(sql), params).fetchall()]


def distinct_leagues(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT DISTINCT league FROM prediction_snapshots
        WHERE league IS NOT NULL AND league != ''
        ORDER BY league
        """
    ).fetchall()
    return [str(r["league"]) for r in rows]


def line_key_for(line: float | None) -> str:
    """Re-export pentru consumatori care nu importă `models`."""
    return line_key(line)
