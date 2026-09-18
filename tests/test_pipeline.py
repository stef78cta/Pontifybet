"""Test pipeline MOCK end-to-end."""

from pathlib import Path

from src.pipeline import run_analysis


def test_pipeline_mock_zip(tmp_path: Path, monkeypatch):
    # redirect outputs
    import config.settings as settings

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    result = run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012, 2013],
        match_ids=["90001", "90002", "90003"],
        model_ids=["over05", "double_chance", "corners"],
        timezone_name="Europe/Bucharest",
    )
    assert Path(result["zip_path"]).exists()
    assert result["mode"] == "mock"
    # Madrid corners should be blocked
    blocked_corners = [
        r for r in result["rows"] if r["match_id"] == "90003" and r["model_id"] == "corners"
    ]
    assert blocked_corners
    assert blocked_corners[0]["g0"] == "FAIL"
    assert any("over05" in p for p in result["generated"])
