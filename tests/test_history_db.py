"""Schema SQLite: creare, idempotență, imutabilitate, deduplicare."""

from __future__ import annotations

import sqlite3

import pytest

from src.history import repository as repo
from src.history.db import SCHEMA_VERSION, connect, initialize, open_db, schema_version
from src.history.models import (
    MatchResult,
    PredictionSnapshot,
    SettlementDecision,
    SettlementStatus,
    SnapshotStatus,
)

EXPECTED_TABLES = {
    "analysis_runs",
    "match_results",
    "prediction_snapshots",
    "schema_version",
    "settlements",
}


def _snapshot(**overrides) -> PredictionSnapshot:
    data = {
        "provider_match_id": "90001",
        "model_key": "over05",
        "model_version": "V4",
        "market": "OVER_0_5",
        "line": 0.5,
        "kickoff_utc": "2026-03-15T18:00:00+00:00",
        "kickoff_unix": 1773597600,
        "league": "Premier League",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "recommendation": "PARIU RECOMANDAT",
        "p_adjusted": 0.94,
        "snapshot_status": SnapshotStatus.FROZEN_PREMATCH.value,
    }
    data.update(overrides)
    return PredictionSnapshot(**data)


def test_empty_db_is_created_with_all_tables(tmp_path):
    db = tmp_path / "fresh.sqlite3"
    assert not db.exists()
    with open_db(db) as conn:
        names = {
            r[0]
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    assert db.exists()
    assert EXPECTED_TABLES <= names


def test_initialize_is_idempotent_and_keeps_data(tmp_path):
    db = tmp_path / "again.sqlite3"
    with open_db(db) as conn:
        run_id = repo.upsert_run(
            conn,
            analysis_date="2026-03-15",
            timezone_name="Europe/Bucharest",
            analysis_fingerprint="fp-1",
        )
        repo.save_prediction(conn, run_id, _snapshot())

    conn = connect(db)
    try:
        assert initialize(conn) == SCHEMA_VERSION
        assert initialize(conn) == SCHEMA_VERSION
        assert schema_version(conn) == SCHEMA_VERSION
        versions = conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0]
        assert versions == SCHEMA_VERSION
        assert conn.execute("SELECT COUNT(*) FROM prediction_snapshots").fetchone()[0] == 1
    finally:
        conn.close()


def test_foreign_keys_are_enforced(tmp_path):
    with open_db(tmp_path / "fk.sqlite3") as conn:
        with pytest.raises(sqlite3.IntegrityError):
            with conn:
                conn.execute(
                    """
                    INSERT INTO settlements (
                        prediction_id, settlement_status, updated_at
                    ) VALUES (999999, 'PENDING_RESULT', '2026-01-01T00:00:00+00:00')
                    """
                )


def test_run_is_saved_once_per_fingerprint(tmp_path):
    with open_db(tmp_path / "runs.sqlite3") as conn:
        first = repo.upsert_run(
            conn,
            analysis_date="2026-03-15",
            timezone_name="Europe/Bucharest",
            analysis_fingerprint="fp-run",
            model_ids=["over05"],
        )
        second = repo.upsert_run(
            conn,
            analysis_date="2026-03-15",
            timezone_name="Europe/Bucharest",
            analysis_fingerprint="fp-run",
            model_ids=["over05", "corners"],
        )
        assert first == second
        assert conn.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0] == 1
        assert repo.get_run(conn, first)["model_ids"] == "over05,corners"


def test_prediction_snapshot_is_saved_and_deduplicated(tmp_path):
    with open_db(tmp_path / "dedup.sqlite3") as conn:
        run_id = repo.upsert_run(
            conn,
            analysis_date="2026-03-15",
            timezone_name="Europe/Bucharest",
            analysis_fingerprint="fp-dedup",
        )
        pid, created = repo.save_prediction(conn, run_id, _snapshot())
        assert created is True
        same_pid, created_again = repo.save_prediction(conn, run_id, _snapshot())
        assert created_again is False
        assert same_pid == pid
        assert conn.execute("SELECT COUNT(*) FROM prediction_snapshots").fetchone()[0] == 1


def test_double_chance_without_line_is_still_deduplicated(tmp_path):
    """`line` NULL nu trebuie să ocolească indexul UNIQUE."""
    with open_db(tmp_path / "dc-dedup.sqlite3") as conn:
        run_id = repo.upsert_run(
            conn,
            analysis_date="2026-03-15",
            timezone_name="Europe/Bucharest",
            analysis_fingerprint="fp-dc",
        )
        base = {"model_key": "double_chance", "model_version": "V2", "market": "1X", "line": None}
        repo.save_prediction(conn, run_id, _snapshot(**base))
        repo.save_prediction(conn, run_id, _snapshot(**base))
        assert conn.execute("SELECT COUNT(*) FROM prediction_snapshots").fetchone()[0] == 1


def test_frozen_prediction_cannot_be_overwritten(tmp_path):
    with open_db(tmp_path / "frozen.sqlite3") as conn:
        run_id = repo.upsert_run(
            conn,
            analysis_date="2026-03-15",
            timezone_name="Europe/Bucharest",
            analysis_fingerprint="fp-frozen",
        )
        pid, _ = repo.save_prediction(conn, run_id, _snapshot(recommendation="DEFENSIV"))

        # Calea aplicativă refuză re-îngheţarea.
        assert repo.freeze_prediction(conn, pid, values={"recommendation": "NO BET"}) is False
        with pytest.raises(repo.FrozenSnapshotError):
            repo.assert_not_frozen(conn, pid)

        # Trigger-ul din schemă blochează și un UPDATE direct.
        with pytest.raises(sqlite3.IntegrityError):
            with conn:
                conn.execute(
                    "UPDATE prediction_snapshots SET recommendation = ? WHERE id = ?",
                    ("NO BET", pid),
                )
        row = conn.execute(
            "SELECT recommendation, snapshot_status FROM prediction_snapshots WHERE id = ?",
            (pid,),
        ).fetchone()
        assert row["recommendation"] == "DEFENSIV"
        assert row["snapshot_status"] == SnapshotStatus.FROZEN_PREMATCH.value


def test_pending_snapshot_can_be_frozen_once(tmp_path):
    with open_db(tmp_path / "pending.sqlite3") as conn:
        run_id = repo.upsert_run(
            conn,
            analysis_date="2026-03-15",
            timezone_name="Europe/Bucharest",
            analysis_fingerprint="fp-pending",
        )
        pid, _ = repo.save_prediction(
            conn,
            run_id,
            _snapshot(
                model_key="corners",
                model_version="V14",
                market="CORNERS_OVER",
                line=8.5,
                recommendation=None,
                p_adjusted=None,
                data_status="valid",
                snapshot_status=SnapshotStatus.PENDING_EXCEL_RECALC.value,
            ),
        )
        assert repo.freeze_prediction(conn, pid, values={"recommendation": "PRUDENT"}) is True
        row = conn.execute(
            "SELECT * FROM prediction_snapshots WHERE id = ?", (pid,)
        ).fetchone()
        assert row["snapshot_status"] == SnapshotStatus.FROZEN_PREMATCH.value
        assert row["recommendation"] == "PRUDENT"
        assert row["frozen_at"]
        # Cheile netransmise nu sunt șterse.
        assert row["data_status"] == "valid"
        assert repo.freeze_prediction(conn, pid, values={"recommendation": "NO BET"}) is False


def test_repeated_result_and_settlement_do_not_duplicate(tmp_path):
    with open_db(tmp_path / "idem.sqlite3") as conn:
        run_id = repo.upsert_run(
            conn,
            analysis_date="2026-03-15",
            timezone_name="Europe/Bucharest",
            analysis_fingerprint="fp-idem",
        )
        pid, _ = repo.save_prediction(conn, run_id, _snapshot())
        result = MatchResult(
            provider_match_id="90001",
            match_status="complete",
            home_goals=2,
            away_goals=1,
            total_goals=3,
        )
        decision = SettlementDecision(
            settlement_status=SettlementStatus.SETTLED.value,
            outcome="HIT",
            settlement_reason="test",
        )
        for _ in range(10):
            repo.upsert_match_result(conn, result)
            repo.upsert_settlement(conn, pid, decision)
        assert conn.execute("SELECT COUNT(*) FROM match_results").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM settlements").fetchone()[0] == 1
