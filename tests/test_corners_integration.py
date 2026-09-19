"""Integrarea Cornere V14 în pipeline: un singur calcul, un singur snapshot.

Verifică cerințele de fază: ANALYSIS calculează și nu generează fișiere, EXPORT
scrie și nu recalculează, iar UI / istoric / export citesc aceleași valori.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src import ui_tables
from src.api.mock import MockFootyStatsClient
from src.history.db import open_db
from src.history import repository as repo


MATCH_IDS = ["90001", "90002", "90003"]


class _CountingClient(MockFootyStatsClient):
    """Client mock care numără apelurile, ca să putem dovedi „zero API în EXPORT”."""

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[str] = []

    def league_matches(self, season_id: int, page: int = 1, *, all_pages: bool = False):
        self.calls.append(f"league_matches:{season_id}")
        return super().league_matches(season_id, page, all_pages=all_pages)

    def league_teams(self, season_id: int):
        self.calls.append(f"league_teams:{season_id}")
        return super().league_teams(season_id)

    def team(self, team_id: int, competition_id: int | None = None):
        self.calls.append(f"team:{team_id}")
        return super().team(team_id, competition_id)

    def last_x(self, team_id: int, num: int = 5):
        self.calls.append(f"last_x:{team_id}:{num}")
        return super().last_x(team_id, num)

    def matches_by_date(self, *args, **kwargs):
        self.calls.append("matches_by_date")
        return super().matches_by_date(*args, **kwargs)


@pytest.fixture
def corners_analysis(tmp_path, monkeypatch, isolated_history_db):
    import config.settings as settings
    import src.pipeline as pipeline

    client = _CountingClient()
    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path / "outputs")
    monkeypatch.setattr(pipeline, "get_client", lambda: client)
    analysis = pipeline.run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012, 2013],
        match_ids=MATCH_IDS,
        model_ids=["corners"],
        timezone_name="Europe/Bucharest",
    )
    return analysis, client, tmp_path


def _corners_rows(analysis) -> list[dict]:
    return [r for r in analysis["rows"] if r["model_id"] == "corners"]


# --- ANALYSIS -----------------------------------------------------------------


def test_analysis_produces_fourteen_lines_per_match(corners_analysis):
    analysis, _, _ = corners_analysis
    rows = _corners_rows(analysis)
    assert len(rows) == len(MATCH_IDS)
    for row in rows:
        selections = row["corners_selections"]
        assert len(selections) == 14
        labels = [item["line"] for item in selections]
        assert labels == [
            "O3,5", "O4,5", "O5,5", "O6,5", "O7,5", "O8,5",
            "U10,5", "U11,5", "U12,5", "U13,5", "U14,5", "U15,5", "U16,5", "U17,5",
        ]


def test_analysis_computes_corners_once_per_match(corners_analysis):
    analysis, client, _ = corners_analysis
    counters = analysis["profiler"]["counters"]
    # Un singur lot acoperă toate meciurile, deci o singură trecere prin workbook.
    assert counters["compute_corners"] == 1
    # Istoricul nativ se colectează o dată pe sezon, nu o dată pe meci sau pe linie.
    league_calls = [call for call in client.calls if call.startswith("league_matches")]
    assert sorted(league_calls) == ["league_matches:2012", "league_matches:2013"]


def test_analysis_does_not_generate_files(corners_analysis):
    analysis, _, tmp_path = corners_analysis
    outputs = tmp_path / "outputs"
    produced = list(outputs.rglob("*.xlsx")) + list(outputs.rglob("*.zip"))
    assert produced == []
    assert "zip_path" not in analysis


def test_analysis_records_traceable_provenance(corners_analysis):
    analysis, _, _ = corners_analysis
    for row in _corners_rows(analysis):
        provenance = row["corners_provenance"]
        assert provenance["provider"] == "FootyStats"
        assert provenance["source_status"] == "IMPORTED"
        assert provenance["source_url"].startswith("https://api.football-data-api.com/")
        assert len(provenance["source_sha256"]) == 64
        assert provenance["cutoff_utc"] == provenance["retrieved_utc"]
        assert provenance["native_rows_in_batch"] > 0
        assert provenance["fixtures_returned"] >= provenance["native_rows_season"]


def test_top_live_has_at_most_one_line_per_match(corners_analysis):
    analysis, _, _ = corners_analysis
    top = analysis["snapshot"].corners.top_live
    assert top
    assert len(top) <= 10
    assert len({entry["match_id"] for entry in top}) == len(top)
    assert [entry["rank"] for entry in top] == list(range(1, len(top) + 1))


# --- UI -----------------------------------------------------------------------


def test_ui_rows_show_all_fourteen_lines_and_match_the_snapshot(corners_analysis):
    analysis, _, _ = corners_analysis
    rows = _corners_rows(analysis)
    display = ui_tables.corners_summary_rows(
        rows, fmt_prob=lambda v: "" if v is None else f"{v:.4f}", fmt_score=str, show_all=True
    )
    assert len(display) == 14 * len(rows)
    first = rows[0]["corners_selections"][0]
    shown = display[0]
    assert shown["Linie"] == first["line"]
    assert shown["Verdict"] == first["verdict"]
    assert shown["Nivel"] == first["risk_level"]
    assert shown["P_FINAL"] == f"{first['p_final']:.4f}"


def test_ui_shortlist_keeps_only_eligible_lines(corners_analysis):
    analysis, _, _ = corners_analysis
    rows = _corners_rows(analysis)
    shortlist = ui_tables.corners_summary_rows(
        rows, fmt_prob=str, fmt_score=str, show_all=False
    )
    eligible = [
        item
        for row in rows
        for item in row["corners_selections"]
        if item["eligible"]
    ]
    assert len(shortlist) == len(eligible)
    assert all(item["Eligibil"] == "DA" for item in shortlist)


# --- Istoric ------------------------------------------------------------------


def test_history_stores_the_same_values_as_the_snapshot(corners_analysis, isolated_history_db):
    analysis, _, _ = corners_analysis
    with open_db(isolated_history_db) as conn:
        stored = {
            (row["provider_match_id"], row["market"], row["line"]): dict(row)
            for row in conn.execute(
                "SELECT * FROM prediction_snapshots WHERE model_key = 'corners'"
            )
        }
    assert stored
    for row in _corners_rows(analysis):
        for item in row["corners_selections"]:
            market = (
                "CORNERS_OVER" if item["market_type"] == "OVER" else "CORNERS_UNDER"
            )
            record = stored[(row["match_id"], market, item["line_value"])]
            assert record["recommendation"] == item["verdict"]
            assert record["p_adjusted"] == pytest.approx(item["p_final"])
            assert record["risk_score"] == pytest.approx(item["risk_score"])
            assert record["risk_level"] == item["risk_level"]
            assert record["confidence"] == pytest.approx(item["confidence_final"])
            assert record["snapshot_status"] == "FROZEN_PREMATCH"


def test_history_creates_no_pending_excel_recalc(corners_analysis, isolated_history_db):
    analysis, _, _ = corners_analysis
    assert analysis["history"]["pending_excel_recalc"] == 0
    with open_db(isolated_history_db) as conn:
        pending = repo.pending_excel_recalc(conn, model_key="corners")
    assert pending == []


# --- EXPORT -------------------------------------------------------------------


def test_export_neither_calls_the_api_nor_recomputes(corners_analysis, monkeypatch):
    analysis, client, _ = corners_analysis
    import src.engines.corners.engine as engine
    import src.pipeline as pipeline

    calls_before = len(client.calls)

    def _fail(*args, **kwargs):
        raise AssertionError("EXPORT nu are voie să reevalueze modelul")

    monkeypatch.setattr(engine, "compute_corners_batch", _fail)
    monkeypatch.setattr(pipeline, "get_client", _fail)

    export = pipeline.run_export(analysis["snapshot"])
    assert export["errors"] == []
    assert any("corners" in path for path in export["generated"])
    assert len(client.calls) == calls_before


def test_export_writes_the_snapshot_values_into_the_result_zone(corners_analysis):
    from openpyxl import load_workbook

    from src.adapters.corners import CornersAdapter
    import src.pipeline as pipeline

    analysis, _, _ = corners_analysis
    export = pipeline.run_export(analysis["snapshot"])
    path = next(Path(p) for p in export["generated"] if "corners" in p)

    adapter = CornersAdapter()
    zone = adapter.cfg["result_zone"]
    first = int(zone["first_row"])
    wb = load_workbook(path)
    try:
        sheet = wb[zone["sheet"]]
        headers = [sheet[f"{col}{first}"].value for col in zone["columns"]]
        assert headers[0] == "Match_ID"
        expected = [
            item
            for row in _corners_rows(analysis)
            for item in row["corners_selections"]
        ]
        for offset, item in enumerate(expected):
            excel_row = first + 1 + offset
            assert sheet[f"D{excel_row}"].value == item["line"]
            assert sheet[f"H{excel_row}"].value == pytest.approx(item["p_final"])
            assert sheet[f"N{excel_row}"].value == item["risk_level"]
            assert sheet[f"O{excel_row}"].value == item["verdict"]
    finally:
        wb.close()


def test_export_keeps_all_original_formulas(corners_analysis):
    from src.adapters.corners import CornersAdapter
    from src.excel.integrity import fingerprint_workbook
    import src.pipeline as pipeline

    analysis, _, _ = corners_analysis
    export = pipeline.run_export(analysis["snapshot"])
    path = next(Path(p) for p in export["generated"] if "corners" in p)

    adapter = CornersAdapter()
    max_rows = adapter.integrity_max_rows
    before = fingerprint_workbook(adapter.template_path(), max_rows=max_rows)
    after = fingerprint_workbook(path, max_rows=max_rows)
    assert after.formulas == before.formulas
    assert after.sheet_names == before.sheet_names
    assert len(before.formulas) == 85647


def test_templates_and_reference_workbooks_stay_untouched(corners_analysis):
    """Originalele din `templates/` și `modele_analize/` nu sunt modificate."""
    from hashlib import sha256

    from config.settings import ROOT, TEMPLATES_DIR
    from src.adapters.corners import CornersAdapter
    import src.pipeline as pipeline

    analysis, _, _ = corners_analysis
    name = CornersAdapter().template_name
    template = TEMPLATES_DIR / name
    reference = ROOT / "modele_analize" / name
    digests = {
        path: sha256(path.read_bytes()).hexdigest()
        for path in (template, reference)
        if path.exists()
    }
    assert digests

    pipeline.run_export(analysis["snapshot"])

    for path, digest in digests.items():
        assert sha256(path.read_bytes()).hexdigest() == digest


# --- Regresii pentru celelalte modele ----------------------------------------


def test_other_models_are_unaffected_by_the_corners_engine(tmp_path, monkeypatch, isolated_history_db):
    """Over 0.5 și Șansă Dublă produc aceleași valori cu și fără Cornere în lot."""
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path / "outputs")
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())

    def run(models: list[str]) -> dict:
        analysis = pipeline.run_analysis(
            date_iso="2026-03-15",
            league_ids=[2012, 2013],
            match_ids=MATCH_IDS,
            model_ids=models,
            timezone_name="Europe/Bucharest",
            persist_history=False,
        )
        return {
            (row["match_id"], row["model_id"]): (
                row.get("recommendation"),
                row.get("risk_level"),
                row.get("risk_score"),
                row.get("confidence"),
                row.get("p_over"),
                row.get("p0_recalibrated"),
                row.get("model_g0"),
            )
            for row in analysis["rows"]
            if row["model_id"] in {"over05", "double_chance"}
        }

    without_corners = run(["over05", "double_chance"])
    with_corners = run(["over05", "double_chance", "corners"])
    assert without_corners == with_corners
