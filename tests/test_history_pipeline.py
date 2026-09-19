"""Jurnalul pre-match produs de `run_analysis` + ingestia workbook-ului recalculat."""

from __future__ import annotations

import pytest
from openpyxl import Workbook

from src.api.mock import MockFootyStatsClient
from src.excel.integrity import IntegrityError
from src.history import excel_ingest
from src.history import repository as repo
from src.history.db import open_db
from src.history.models import SnapshotStatus
from src.history.snapshots import (
    CORNERS_RESULT_SHEET,
    corners_lines,
    model_version,
    model_versions,
)


@pytest.fixture
def analysis(tmp_path, monkeypatch, isolated_history_db):
    """Analiză MOCK completă, fără cheie FootyStats în mediu."""
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.delenv("FOOTYSTATS_API_KEY", raising=False)
    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path / "outputs")
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    return pipeline.run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012, 2013],
        match_ids=["90001", "90002", "90003"],
        model_ids=["over05", "double_chance", "corners"],
        timezone_name="Europe/Bucharest",
    )


def test_model_versions_come_from_template_names():
    versions = model_versions()
    assert versions["over05"] == "V4"
    assert versions["double_chance"] == "V2"
    assert versions["corners"] == "V14"


def test_corners_lines_are_read_from_template():
    lines = corners_lines()
    assert len(lines) == 14
    markets = {market for market, _ in lines}
    assert markets == {"CORNERS_OVER", "CORNERS_UNDER"}
    assert all(abs(line % 1 - 0.5) < 1e-9 for _, line in lines)


def test_mock_analysis_persists_snapshots(analysis, isolated_history_db):
    assert analysis["mode"] == "mock"
    assert analysis["errors"] == []
    assert analysis["history"]["created"] > 0

    with open_db(isolated_history_db) as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM prediction_snapshots")]
        runs = conn.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0]

    assert runs == 1
    over05 = [r for r in rows if r["model_key"] == "over05"]
    assert over05
    assert all(r["snapshot_status"] == SnapshotStatus.FROZEN_PREMATCH.value for r in over05)
    assert all(r["market"] == "OVER_0_5" and r["line"] == 0.5 for r in over05)
    assert all(r["recommendation"] for r in over05)
    assert all(r["frozen_at"] for r in over05)

    dc = [r for r in rows if r["model_key"] == "double_chance"]
    assert {r["market"] for r in dc} == {"1X", "X2", "12"}
    assert all(r["line"] is None for r in dc)
    assert all(r["snapshot_status"] == SnapshotStatus.FROZEN_PREMATCH.value for r in dc)

    corners = [r for r in rows if r["model_key"] == "corners"]
    assert corners
    # Verdictul Cornere este calculat de Microsoft Excel, deci aici e doar rezervat.
    assert all(
        r["snapshot_status"] == SnapshotStatus.PENDING_EXCEL_RECALC.value for r in corners
    )
    assert all(r["recommendation"] is None for r in corners)
    assert all(r["frozen_at"] is None for r in corners)
    assert len(corners) == 14 * len({r["provider_match_id"] for r in corners})

    # Kickoff-ul și identitatea meciului vin din FootyStats, nu din numele echipelor.
    assert all(r["provider_match_id"].isdigit() for r in rows)
    assert all(r["kickoff_unix"] for r in rows)


def test_rerunning_the_same_analysis_creates_no_duplicates(analysis, isolated_history_db, monkeypatch, tmp_path):
    import config.settings as settings
    import src.pipeline as pipeline

    with open_db(isolated_history_db) as conn:
        before = conn.execute("SELECT COUNT(*) FROM prediction_snapshots").fetchone()[0]

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path / "outputs")
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    second = pipeline.run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012, 2013],
        match_ids=["90001", "90002", "90003"],
        model_ids=["over05", "double_chance", "corners"],
        timezone_name="Europe/Bucharest",
    )
    assert second["history"]["created"] == 0
    assert second["history"]["existing"] == before

    with open_db(isolated_history_db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM prediction_snapshots").fetchone()[0] == before
        assert conn.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0] == 1


def test_persist_history_can_be_disabled(tmp_path, monkeypatch, isolated_history_db):
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path / "outputs")
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    result = pipeline.run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012],
        match_ids=["90001"],
        model_ids=["over05"],
        timezone_name="Europe/Bucharest",
        persist_history=False,
    )
    assert result["history"] == {}
    assert not isolated_history_db.exists()


# --- Ingestia workbook-ului recalculat ---------------------------------------


def _recalculated_workbook(path, rows):
    """Workbook care imită valorile salvate de Microsoft Excel în `Analiza_Linii`."""
    wb = Workbook()
    ws = wb.active
    ws.title = CORNERS_RESULT_SHEET
    for offset, row in enumerate(rows):
        excel_row = 6 + offset
        for col, value in row.items():
            ws[f"{col}{excel_row}"] = value
    wb.save(path)
    wb.close()
    return path


def test_export_without_excel_recalc_is_blocked(analysis, tmp_path, monkeypatch):
    """Copia produsă de Pontifybet nu are valorile Excel; importul trebuie blocat."""
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path / "outputs")
    export = pipeline.run_export(analysis["snapshot"])
    corners_files = [p for p in export["generated"] if "corners" in p]
    assert corners_files
    with pytest.raises(IntegrityError) as exc:
        excel_ingest.read_recalculated_lines(corners_files[0])
    assert "IMPORT BLOCAT" in str(exc.value)


def test_workbook_off_template_is_blocked(tmp_path):
    path = _recalculated_workbook(tmp_path / "fake.xlsx", [{"B": "90001"}])
    with pytest.raises(IntegrityError) as exc:
        excel_ingest.read_recalculated_lines(path)
    assert "IMPORT BLOCAT" in str(exc.value)


def test_ingestion_freezes_corners_and_is_idempotent(analysis, tmp_path, monkeypatch, isolated_history_db):
    db = isolated_history_db
    # Poarta de integritate este verificată separat; aici testăm citirea și îngheţul.
    monkeypatch.setattr(excel_ingest, "assert_matches_template", lambda path: None)

    lines = corners_lines()
    rows = []
    for market, line in lines:
        rows.append(
            {
                "B": "90001",
                "G": "OVER" if market == "CORNERS_OVER" else "UNDER",
                "H": line - 0.5,
                "J": "PASS",
                "S": 0.18,
                "T": 34.0,
                "V": 0.72,
                "Z": 2,
                "AA": "PRUDENT",
                "AB": 0.82,
                "AH": "Dispersie în limite",
            }
        )
    path = _recalculated_workbook(tmp_path / "corners_recalc.xlsx", rows)

    report = excel_ingest.ingest_corners_workbook(path, db_path=str(db))
    assert report["lines_read"] == 14
    assert report["frozen"] == 14
    assert report["unknown_predictions"] == 0

    with open_db(db) as conn:
        frozen = repo.predictions_for_match(conn, "90001", only_frozen=True)
        pending = repo.pending_excel_recalc(conn, model_key="corners")
    corners_frozen = [r for r in frozen if r["model_key"] == "corners"]
    assert len(corners_frozen) == 14
    assert all(r["recommendation"] == "PRUDENT" for r in corners_frozen)
    assert all(r["risk_level"] == 2 for r in corners_frozen)
    assert all(r["p_adjusted"] == 0.82 for r in corners_frozen)
    assert all(r["data_status"] for r in corners_frozen), "data_status din validator se păstrează"
    assert all(r["provider_match_id"] != "90001" for r in pending)

    # A doua ingestie nu rescrie un forecast deja publicat.
    rows_v2 = [dict(r, AA="NO BET", Z=5) for r in rows]
    path2 = _recalculated_workbook(tmp_path / "corners_recalc_2.xlsx", rows_v2)
    again = excel_ingest.ingest_corners_workbook(path2, db_path=str(db))
    assert again["frozen"] == 0
    assert again["already_frozen"] == 14
    with open_db(db) as conn:
        after = [
            r
            for r in repo.predictions_for_match(conn, "90001")
            if r["model_key"] == "corners"
        ]
    assert all(r["recommendation"] == "PRUDENT" for r in after)


def test_ingestion_ignores_lines_without_known_prediction(tmp_path, monkeypatch, isolated_history_db):
    monkeypatch.setattr(excel_ingest, "assert_matches_template", lambda path: None)
    path = _recalculated_workbook(
        tmp_path / "orphan.xlsx",
        [{"B": "777777", "G": "OVER", "H": 8, "AA": "PRUDENT"}],
    )
    report = excel_ingest.ingest_corners_workbook(path, db_path=str(isolated_history_db))
    assert report["lines_read"] == 1
    assert report["frozen"] == 0
    assert report["unknown_predictions"] == 1


def test_corners_model_version_is_used_as_identity():
    assert model_version("corners") == "V14"
