"""Conexiune și schemă SQLite pentru istoric/backtest.

Fără ORM: proiectul nu are unul, iar `sqlite3` din biblioteca standard acoperă
complet nevoile MVP-ului. Versionarea se face cu un `schema_version` intern,
nu cu un framework de migrare — inițializarea trebuie să poată rula repetat fără
pierdere de date, deci nu există `DROP TABLE` în startup.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import config.settings as settings

SCHEMA_VERSION = 1

# Migrările sunt aplicate în ordine, o singură dată, pe baza `schema_version`.
# Fiecare intrare: (versiune, listă de instrucțiuni DDL idempotente).
_MIGRATIONS: list[tuple[int, tuple[str, ...]]] = [
    (
        1,
        (
            """
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                analysis_date TEXT NOT NULL,
                timezone TEXT NOT NULL,
                run_status TEXT NOT NULL,
                source_mode TEXT,
                model_ids TEXT,
                analysis_fingerprint TEXT NOT NULL
            )
            """,
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_analysis_runs_fingerprint
                ON analysis_runs(analysis_fingerprint)
            """,
            """
            CREATE TABLE IF NOT EXISTS prediction_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL REFERENCES analysis_runs(id),
                provider_match_id TEXT NOT NULL,
                kickoff_utc TEXT,
                kickoff_unix INTEGER,
                league TEXT,
                home_team TEXT,
                away_team TEXT,
                model_key TEXT NOT NULL,
                model_version TEXT NOT NULL,
                market TEXT NOT NULL,
                line REAL,
                line_key TEXT NOT NULL,
                recommendation TEXT,
                p_adjusted REAL,
                failure_mode REAL,
                risk_score REAL,
                risk_level REAL,
                confidence REAL,
                confidence_label TEXT,
                data_status TEXT,
                hard_gate TEXT,
                motivation TEXT,
                frozen_at TEXT,
                snapshot_status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_prediction_identity
                ON prediction_snapshots(
                    provider_match_id, model_key, model_version, market, line_key
                )
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_prediction_status
                ON prediction_snapshots(snapshot_status, kickoff_unix)
            """,
            # Imutabilitatea FROZEN_PREMATCH este impusă în baza de date, nu doar
            # în Python: un apel greșit din orice modul viitor trebuie să eșueze,
            # nu să rescrie discret un forecast deja publicat. Rezultatul meciului
            # se scrie exclusiv în `match_results`/`settlements`.
            """
            CREATE TRIGGER IF NOT EXISTS trg_prediction_frozen_immutable
            BEFORE UPDATE ON prediction_snapshots
            FOR EACH ROW
            WHEN OLD.snapshot_status = 'FROZEN_PREMATCH' AND (
                NEW.recommendation IS NOT OLD.recommendation
                OR NEW.p_adjusted IS NOT OLD.p_adjusted
                OR NEW.failure_mode IS NOT OLD.failure_mode
                OR NEW.risk_score IS NOT OLD.risk_score
                OR NEW.risk_level IS NOT OLD.risk_level
                OR NEW.confidence IS NOT OLD.confidence
                OR NEW.confidence_label IS NOT OLD.confidence_label
                OR NEW.data_status IS NOT OLD.data_status
                OR NEW.hard_gate IS NOT OLD.hard_gate
                OR NEW.motivation IS NOT OLD.motivation
                OR NEW.model_version IS NOT OLD.model_version
                OR NEW.market IS NOT OLD.market
                OR NEW.line IS NOT OLD.line
                OR NEW.line_key IS NOT OLD.line_key
                OR NEW.frozen_at IS NOT OLD.frozen_at
                OR NEW.snapshot_status IS NOT OLD.snapshot_status
            )
            BEGIN
                SELECT RAISE(
                    ABORT,
                    'FROZEN_PREMATCH imuabil: predicția pre-match nu poate fi modificată.'
                );
            END
            """,
            """
            CREATE TABLE IF NOT EXISTS match_results (
                provider_match_id TEXT PRIMARY KEY,
                match_status TEXT,
                home_goals INTEGER,
                away_goals INTEGER,
                total_goals INTEGER,
                home_corners INTEGER,
                away_corners INTEGER,
                total_corners INTEGER,
                source_endpoint TEXT NOT NULL,
                result_fetched_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS settlements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER NOT NULL UNIQUE
                    REFERENCES prediction_snapshots(id) ON DELETE CASCADE,
                settlement_status TEXT NOT NULL,
                outcome TEXT,
                settled_at TEXT,
                settlement_reason TEXT,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS ix_settlement_status
                ON settlements(settlement_status)
            """,
        ),
    ),
]


def utc_now_iso() -> str:
    """Timestamp ISO-8601 UTC, folosit pentru toate coloanele de tip *_at."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def resolve_db_path() -> Path:
    """Calea bazei, rezolvată la runtime prin `config.settings`.

    Modulele nu au voie să-și hardcodeze propria cale: un al doilea default ar
    duce la două baze paralele și la un istoric fragmentat.
    """
    return settings.get_sqlite_path()


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Deschide o conexiune cu `foreign_keys` activ și rânduri accesibile pe nume.

    WAL este activat best-effort: pe rulările Streamlit locale reduce blocajele
    între reruns, dar pe unele sisteme de fișiere nu este disponibil, caz în care
    rămânem pe jurnalul implicit fără a eșua.
    """
    path = Path(db_path) if db_path is not None else resolve_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.execute("PRAGMA journal_mode = WAL")
    except sqlite3.DatabaseError:
        pass
    return conn


@contextmanager
def open_db(db_path: Path | str | None = None) -> Iterator[sqlite3.Connection]:
    """Conexiune inițializată, închisă determinist la ieșire."""
    conn = connect(db_path)
    try:
        initialize(conn)
        yield conn
    finally:
        conn.close()


def _current_version(conn: sqlite3.Connection) -> int:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
    return int(row["v"]) if row and row["v"] is not None else 0


def initialize(conn: sqlite3.Connection) -> int:
    """Aplică migrările lipsă și returnează versiunea finală a schemei.

    Idempotentă: rularea repetată nu modifică datele existente și nu șterge
    nimic. Toate migrările unei versiuni rulează în aceeași tranzacție.
    """
    current = _current_version(conn)
    for version, statements in _MIGRATIONS:
        if version <= current:
            continue
        with conn:
            for statement in statements:
                conn.execute(statement)
            conn.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                (version, utc_now_iso()),
            )
        current = version
    return current


def schema_version(conn: sqlite3.Connection) -> int:
    return _current_version(conn)
