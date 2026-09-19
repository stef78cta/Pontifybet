"""Actualizarea rezultatelor: fetch unic pe meci, idempotență, izolarea forecastului."""

from __future__ import annotations

import shutil

from src.api.mock import MockFootyStatsClient
from src.history import backtest
from src.history import repository as repo
from src.history.db import open_db
from src.history.models import PredictionSnapshot, SnapshotStatus
from src.history.results import update_results

KICKOFF_UNIX = 1773550800
NOW_UNIX = KICKOFF_UNIX + 20_000


def _seed(db, predictions: list[PredictionSnapshot]) -> dict[str, int]:
    ids: dict[str, int] = {}
    with open_db(db) as conn:
        run_id = repo.upsert_run(
            conn,
            analysis_date="2026-03-15",
            timezone_name="Europe/Bucharest",
            analysis_fingerprint="fp-results",
            source_mode="mock",
        )
        for snapshot in predictions:
            pid, _ = repo.save_prediction(conn, run_id, snapshot)
            ids[f"{snapshot.provider_match_id}:{snapshot.market}:{snapshot.line}"] = pid
    return ids


def _frozen(provider_match_id: str, model_key: str, version: str, market: str, line) -> PredictionSnapshot:
    return PredictionSnapshot(
        provider_match_id=provider_match_id,
        model_key=model_key,
        model_version=version,
        market=market,
        line=line,
        kickoff_utc="2026-03-15T09:00:00+00:00",
        kickoff_unix=KICKOFF_UNIX,
        league="Premier League",
        home_team="Arsenal",
        away_team="Chelsea",
        recommendation="PRUDENT",
        risk_level=2,
        p_adjusted=0.8,
        snapshot_status=SnapshotStatus.FROZEN_PREMATCH.value,
    )


def test_single_match_result_is_reused_for_all_corner_lines(isolated_history_db):
    db = isolated_history_db
    predictions = [_frozen("90001", "over05", "V4", "OVER_0_5", 0.5)]
    predictions += [
        _frozen("90001", "double_chance", "V2", code, None) for code in ("1X", "X2", "12")
    ]
    predictions += [
        _frozen("90001", "corners", "V14", "CORNERS_OVER", 3.5 + i) for i in range(8)
    ]
    _seed(db, predictions)

    client = MockFootyStatsClient()
    summary = update_results(client=client, now_unix=NOW_UNIX, db_path=str(db))

    assert summary.pending_predictions == len(predictions)
    # Un singur apel `/match`, deși există 12 predicții pe același meci.
    assert summary.matches_queried == 1
    assert client._call_counts.get("match_details") == 1
    assert summary.results_updated == 1

    with open_db(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM match_results").fetchone()[0] == 1
        result = repo.get_match_result(conn, "90001")
    assert (result.home_goals, result.away_goals) == (2, 1)
    assert (result.home_corners, result.away_corners, result.total_corners) == (6, 5, 11)


def test_update_results_settles_each_market_and_is_idempotent(isolated_history_db):
    db = isolated_history_db
    ids = _seed(
        db,
        [
            _frozen("90001", "over05", "V4", "OVER_0_5", 0.5),
            _frozen("90001", "double_chance", "V2", "1X", None),
            _frozen("90001", "double_chance", "V2", "X2", None),
            _frozen("90001", "corners", "V14", "CORNERS_OVER", 8.5),
            _frozen("90001", "corners", "V14", "CORNERS_UNDER", 8.5),
        ],
    )

    first = update_results(client=MockFootyStatsClient(), now_unix=NOW_UNIX, db_path=str(db))
    assert first.hit + first.miss == 5
    assert first.still_pending == 0
    assert not first.errors

    with open_db(db) as conn:
        outcome_of = {
            key: repo.get_settlement(conn, pid)["outcome"] for key, pid in ids.items()
        }
    # 2-1 la Arsenal - Chelsea, 11 cornere.
    assert outcome_of["90001:OVER_0_5:0.5"] == "HIT"
    assert outcome_of["90001:1X:None"] == "HIT"
    assert outcome_of["90001:X2:None"] == "MISS"
    assert outcome_of["90001:CORNERS_OVER:8.5"] == "HIT"
    assert outcome_of["90001:CORNERS_UNDER:8.5"] == "MISS"

    # Rulare repetată: niciun duplicat, nicio nouă interogare necesară.
    for _ in range(9):
        update_results(client=MockFootyStatsClient(), now_unix=NOW_UNIX, db_path=str(db))
    with open_db(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM settlements").fetchone()[0] == 5
        assert conn.execute("SELECT COUNT(*) FROM match_results").fetchone()[0] == 1


def test_goalless_match_produces_over05_miss(isolated_history_db):
    db = isolated_history_db
    ids = _seed(db, [_frozen("90002", "over05", "V4", "OVER_0_5", 0.5)])
    summary = update_results(client=MockFootyStatsClient(), now_unix=NOW_UNIX, db_path=str(db))
    assert (summary.hit, summary.miss) == (0, 1)
    with open_db(db) as conn:
        settlement = repo.get_settlement(conn, ids["90002:OVER_0_5:0.5"])
    assert settlement["outcome"] == "MISS"


def test_missing_official_corners_do_not_become_miss(isolated_history_db):
    db = isolated_history_db
    ids = _seed(
        db,
        [
            _frozen("90003", "corners", "V14", "CORNERS_OVER", 8.5),
            _frozen("90003", "over05", "V4", "OVER_0_5", 0.5),
        ],
    )
    summary = update_results(client=MockFootyStatsClient(), now_unix=NOW_UNIX, db_path=str(db))
    assert summary.result_data_unavailable == 1
    with open_db(db) as conn:
        corners = repo.get_settlement(conn, ids["90003:CORNERS_OVER:8.5"])
        goals = repo.get_settlement(conn, ids["90003:OVER_0_5:0.5"])
    assert corners["settlement_status"] == "RESULT_DATA_UNAVAILABLE"
    assert corners["outcome"] is None
    # Scorul există (1-1), deci Over 0.5 se decontează normal.
    assert goals["outcome"] == "HIT"


def test_forecast_is_not_modified_by_results(isolated_history_db):
    db = isolated_history_db
    _seed(db, [_frozen("90001", "over05", "V4", "OVER_0_5", 0.5)])
    with open_db(db) as conn:
        before = dict(conn.execute("SELECT * FROM prediction_snapshots").fetchone())
    update_results(client=MockFootyStatsClient(), now_unix=NOW_UNIX, db_path=str(db))
    with open_db(db) as conn:
        after = dict(conn.execute("SELECT * FROM prediction_snapshots").fetchone())
    assert before == after


def test_matches_not_yet_finished_are_not_queried(isolated_history_db):
    db = isolated_history_db
    _seed(db, [_frozen("90001", "over05", "V4", "OVER_0_5", 0.5)])
    client = MockFootyStatsClient()
    summary = update_results(client=client, now_unix=KICKOFF_UNIX + 60, db_path=str(db))
    assert summary.pending_predictions == 0
    assert summary.matches_queried == 0
    assert client._call_counts.get("match_details") is None
    assert summary.still_pending == 1


def test_backtest_groups_by_model_risk_level_league_and_line(isolated_history_db):
    db = isolated_history_db
    _seed(
        db,
        [
            _frozen("90001", "over05", "V4", "OVER_0_5", 0.5),
            _frozen("90001", "corners", "V14", "CORNERS_OVER", 8.5),
            _frozen("90001", "corners", "V14", "CORNERS_UNDER", 8.5),
        ],
    )
    update_results(client=MockFootyStatsClient(), now_unix=NOW_UNIX, db_path=str(db))

    total = backtest.summary(db_path=str(db))
    assert total["settled"] == 3
    assert total["hit"] == 2
    assert total["miss"] == 1
    assert total["hit_rate"] == 2 / 3

    models = {row["model"]: row for row in backtest.by_model(db_path=str(db))}
    assert models["over05 V4"]["hit"] == 1
    assert models["corners V14"]["settled"] == 2

    levels = {row["risk_level"]: row for row in backtest.by_risk_level(db_path=str(db))}
    assert levels[2.0]["settled"] == 3

    leagues = {row["league"]: row for row in backtest.by_league(db_path=str(db))}
    assert leagues["Premier League"]["settled"] == 3

    lines = {row["market_line"] for row in backtest.by_corners_line(db_path=str(db))}
    assert lines == {"CORNERS_OVER 8.5", "CORNERS_UNDER 8.5"}


def test_hit_rate_is_none_without_settlements(isolated_history_db):
    """Fără settlement, hit-rate-ul este NOT AVAILABLE, nu 0%."""
    assert backtest.summary(db_path=str(isolated_history_db))["hit_rate"] is None


def test_outputs_cleanup_does_not_touch_sqlite(tmp_path, isolated_history_db, monkeypatch):
    import config.settings as settings
    from src.excel.generator import cleanup_run_dir, make_run_dir

    db = isolated_history_db
    _seed(db, [_frozen("90001", "over05", "V4", "OVER_0_5", 0.5)])
    assert db.exists()

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path / "outputs")
    run_dir = make_run_dir("run-1")
    (run_dir / "dummy.xlsx").write_bytes(b"x")
    cleanup_run_dir(run_dir)
    shutil.rmtree(tmp_path / "outputs", ignore_errors=True)

    assert not run_dir.exists()
    assert db.exists()
    with open_db(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM prediction_snapshots").fetchone()[0] == 1
