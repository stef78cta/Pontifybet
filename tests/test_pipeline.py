"""Test pipeline MOCK end-to-end."""

from pathlib import Path

from src.pipeline import run_analysis, run_export


def test_run_analysis_fills_liga_when_todays_matches_omit_league_name(
    tmp_path: Path, monkeypatch
):
    """LIVE todays-matches n-are league_name; liga tot trebuie să apară în rezumat."""
    import config.settings as settings
    from src.api.mock import MockFootyStatsClient
    import src.pipeline as pipeline

    class _NoLeagueNameClient(MockFootyStatsClient):
        def matches_by_date(self, *args, **kwargs):
            matches = super().matches_by_date(*args, **kwargs)
            stripped = []
            for m in matches:
                row = dict(m)
                row.pop("league_name", None)
                row.pop("competition_name", None)
                stripped.append(row)
            return stripped

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "get_client", lambda: _NoLeagueNameClient())
    result = pipeline.run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012],
        match_ids=["90001"],
        model_ids=["over05"],
        timezone_name="Europe/Bucharest",
    )
    over05 = [r for r in result["rows"] if r["model_id"] == "over05"]
    assert over05
    assert over05[0]["liga"] == "England Premier League"


def test_pipeline_mock_zip(tmp_path: Path, monkeypatch):
    import config.settings as settings
    from src.api.mock import MockFootyStatsClient
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    analysis = run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012, 2013],
        match_ids=["90001", "90002", "90003"],
        model_ids=["over05", "double_chance", "corners"],
        timezone_name="Europe/Bucharest",
    )
    result = run_export(analysis["snapshot"])
    assert Path(result["zip_path"]).exists()
    assert analysis["mode"] == "mock"
    corners_rows = [
        r for r in analysis["rows"] if r["match_id"] == "90003" and r["model_id"] == "corners"
    ]
    assert corners_rows
    # Mediile agregate lipsesc pentru 90003, dar V14 le derivă din istoricul nativ:
    # validarea nu mai blochează, iar cele 14 linii sunt calculate în ANALYSIS.
    assert corners_rows[0]["g0"] == "OK"
    assert len(corners_rows[0]["corners_selections"]) == 14
    assert any("over05" in p for p in result["generated"])
    assert any("corners" in p for p in result["generated"])
    over05_rows = [r for r in analysis["rows"] if r["model_id"] == "over05"]
    assert over05_rows
    assert all(r.get("recommendation") for r in over05_rows)
    assert all(r.get("model_g0") for r in over05_rows)
    assert all("ZERO-MASS INCOMPLETE" not in str(r.get("model_g0")) for r in over05_rows)
    dc_rows = [r for r in analysis["rows"] if r["model_id"] == "double_chance"]
    assert dc_rows
    assert all(r.get("dc_selections") for r in dc_rows)
    assert all(r.get("recommendation") for r in dc_rows)
    assert all(r.get("model_g0") != "CRITICAL MISSING" for r in dc_rows)
    assert all(
        sel.get("p_adj") is not None
        for r in dc_rows
        for sel in r.get("dc_selections") or []
        if sel.get("selection") == "1X"
    )
    csv_dc = Path(result["run_dir"]) / "double_chance_rezultate.csv"
    assert csv_dc.exists()
