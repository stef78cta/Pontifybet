"""Teste orchestration: fetch model-aware, snapshot, export fără recalcul."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import httpx
import pytest

from src.adapters.over05 import Over05Adapter
from src.api.cache import ResponseCache
from src.api.client import FootyStatsClient, FootyStatsError
from src.api.mock import MockFootyStatsClient
from src.excel.integrity import get_template_baseline
from src.orchestration.fetch_plan import needs_last5, needs_last10, required_lastx_nums
from src.orchestration.match_fetcher import enrich_matches_batch
from src.orchestration.profiler import RunProfiler
from src.pipeline import run_analysis, run_export


def _mock_matches(client: MockFootyStatsClient) -> list[dict]:
    return client.matches_by_date("2026-03-15")


@pytest.fixture
def mock_client() -> MockFootyStatsClient:
    client = MockFootyStatsClient()
    client._call_counts.clear()
    return client


def test_last10_not_required_for_active_models():
    assert needs_last10(["over05", "double_chance", "corners"]) is False
    assert 10 not in required_lastx_nums(["over05", "corners"])


def test_only_double_chance_skips_last5(mock_client: MockFootyStatsClient):
    matches = _mock_matches(mock_client)[:2]
    enrich_matches_batch(mock_client, matches, model_ids=["double_chance"], tz_name="Europe/Bucharest")
    assert mock_client._call_counts.get("last_x_5", 0) == 0
    assert mock_client._call_counts.get("last_x_10", 0) == 0


def test_over05_collects_last5(mock_client: MockFootyStatsClient):
    matches = _mock_matches(mock_client)[:1]
    enrich_matches_batch(mock_client, matches, model_ids=["over05"], tz_name="Europe/Bucharest")
    assert mock_client._call_counts.get("last_x_5", 0) >= 2


def test_corners_collects_last5(mock_client: MockFootyStatsClient):
    matches = _mock_matches(mock_client)[:1]
    enrich_matches_batch(mock_client, matches, model_ids=["corners"], tz_name="Europe/Bucharest")
    assert mock_client._call_counts.get("last_x_5", 0) >= 2


def test_over05_and_corners_deduplicate_last5(mock_client: MockFootyStatsClient):
    matches = _mock_matches(mock_client)[:1]
    enrich_matches_batch(
        mock_client,
        matches,
        model_ids=["over05", "corners"],
        tz_name="Europe/Bucharest",
    )
    # home + away, o singură dată fiecare
    assert mock_client._call_counts.get("last_x_5", 0) == 2


def test_league_context_once_per_season(mock_client: MockFootyStatsClient):
    matches = _mock_matches(mock_client)[:3]
    enrich_matches_batch(
        mock_client,
        matches,
        model_ids=["over05"],
        tz_name="Europe/Bucharest",
    )
    assert mock_client._call_counts.get("league_teams", 0) == 2


def test_two_seasons_two_league_contexts(mock_client: MockFootyStatsClient):
    matches = _mock_matches(mock_client)[:3]
    enrich_matches_batch(mock_client, matches, model_ids=["over05"], tz_name="Europe/Bucharest")
    assert mock_client._call_counts.get("league_teams_2012", 0) == 1
    assert mock_client._call_counts.get("league_teams_2013", 0) == 1


def test_concurrency_respects_max_workers(monkeypatch):
    monkeypatch.setattr("config.settings.FOOTYSTATS_MAX_WORKERS", 2)
    calls: list[int] = []

    class _CountClient(MockFootyStatsClient):
        def last_x(self, team_id: int, num: int = 5) -> dict[str, Any]:
            calls.append(1)
            return super().last_x(team_id, num)

    client = _CountClient()
    matches = [
        {"homeID": 1, "awayID": 2, "competition_id": 2012, "id": "1"},
        {"homeID": 3, "awayID": 4, "competition_id": 2012, "id": "2"},
    ]
    enrich_matches_batch(client, matches, model_ids=["over05"], tz_name="Europe/Bucharest")
    assert len(calls) == 4


def test_429_retry_then_fail():
    attempts = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["n"] += 1
        return httpx.Response(429, json={"success": False, "message": "limit reached"})

    transport = httpx.MockTransport(handler)
    client = FootyStatsClient(
        api_key="test-key",
        retries=2,
        cache=ResponseCache(use_disk=False),
        transport=transport,
    )
    with pytest.raises(FootyStatsError) as exc:
        client.list_leagues()
    assert attempts["n"] == 3
    assert "limită" in exc.value.user_message.lower() or "limit" in exc.value.user_message.lower()
    client.close()


def test_analysis_does_not_create_xlsx_or_zip(tmp_path: Path, monkeypatch):
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    result = run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012],
        match_ids=["90001"],
        model_ids=["over05"],
        timezone_name="Europe/Bucharest",
    )
    assert result["phase"] == "analysis"
    assert "snapshot" in result
    assert list(tmp_path.iterdir()) == []


def test_analysis_rows_available(tmp_path: Path, monkeypatch):
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    result = run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012],
        match_ids=["90001"],
        model_ids=["over05"],
    )
    assert result["rows"]
    assert result["profiler"]["time_to_table_sec"] is not None


def test_export_no_footystats_calls(tmp_path: Path, monkeypatch):
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    client = MockFootyStatsClient()
    monkeypatch.setattr(pipeline, "get_client", lambda: client)
    analysis = run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012],
        match_ids=["90001"],
        model_ids=["over05", "double_chance"],
    )
    client._call_counts.clear()
    run_export(analysis["snapshot"])
    assert client._call_counts.get("last_x", 0) == 0
    assert client._call_counts.get("league_teams", 0) == 0


def test_export_does_not_recompute_engines(tmp_path: Path, monkeypatch):
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    analysis = run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012],
        match_ids=["90001"],
        model_ids=["over05", "double_chance"],
    )
    with patch("src.pipeline.compute_over05") as over05_mock, patch(
        "src.orchestration.double_chance_bundle.compute_double_chance"
    ) as dc_mock:
        export = run_export(analysis["snapshot"])
    over05_mock.assert_not_called()
    dc_mock.assert_not_called()
    assert Path(export["zip_path"]).exists()


def test_single_compute_over05_per_match(tmp_path: Path, monkeypatch):
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    profiler = RunProfiler()
    with patch("src.pipeline.compute_over05", wraps=__import__("src.engines.over05", fromlist=["compute_over05"]).compute_over05) as wrapped:
        result = run_analysis(
            date_iso="2026-03-15",
            league_ids=[2012],
            match_ids=["90001", "90002"],
            model_ids=["over05"],
        )
    assert wrapped.call_count == 2
    run_export(result["snapshot"])
    assert wrapped.call_count == 2


def test_single_compute_double_chance_per_match(tmp_path: Path, monkeypatch):
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    with patch(
        "src.orchestration.double_chance_bundle.compute_double_chance",
        wraps=__import__(
            "src.engines.double_chance.engine", fromlist=["compute_double_chance"]
        ).compute_double_chance,
    ) as wrapped:
        result = run_analysis(
            date_iso="2026-03-15",
            league_ids=[2012],
            match_ids=["90001", "90002"],
            model_ids=["double_chance"],
        )
    assert wrapped.call_count == 2
    run_export(result["snapshot"])
    assert wrapped.call_count == 2


def test_derived_trace_not_duplicated_for_audit(tmp_path: Path, monkeypatch):
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    with patch(
        "src.orchestration.double_chance_bundle.derived_1x2_trace",
        wraps=__import__(
            "src.engines.double_chance.inputs", fromlist=["derived_1x2_trace"]
        ).derived_1x2_trace,
    ) as wrapped:
        run_analysis(
            date_iso="2026-03-15",
            league_ids=[2012],
            match_ids=["90001"],
            model_ids=["double_chance"],
        )
    assert wrapped.call_count == 1


def test_template_baseline_reused():
    adapter = Over05Adapter()
    path = adapter.template_path()
    fp1 = get_template_baseline(path)
    fp2 = get_template_baseline(path)
    assert fp1.formulas == fp2.formulas


def test_fingerprint_still_detects_formula_change(tmp_path: Path):
    from src.excel.generator import SafeWorkbookWriter
    from src.excel.integrity import IntegrityError, compare_fingerprints, fingerprint_workbook

    adapter = Over05Adapter()
    dest = tmp_path / "t.xlsx"
    adapter.prepare_copy(dest)
    baseline = get_template_baseline(adapter.template_path())
    writer = SafeWorkbookWriter(dest, adapter.build_whitelist(), template_baseline=baseline)
    writer.wb[writer.wb.sheetnames[0]]["A1"].value = "=1+1"
    writer.wb.save(dest)
    writer.wb.close()
    after = fingerprint_workbook(dest)
    with pytest.raises(IntegrityError):
        compare_fingerprints(baseline, after)


def test_fingerprint_detects_sheet_structure_change():
    from src.excel.integrity import IntegrityError, WorkbookFingerprint, compare_fingerprints

    before = WorkbookFingerprint(sheet_names=["A", "B"], formulas={"A!A1": "=1"})
    after = WorkbookFingerprint(sheet_names=["A"], formulas={"A!A1": "=1"})
    with pytest.raises(IntegrityError, match="foi"):
        compare_fingerprints(before, after)


def test_whitelist_blocks_unlisted_writes(tmp_path: Path):
    from src.excel.generator import SafeWorkbookWriter
    from src.excel.integrity import IntegrityError, get_template_baseline

    adapter = Over05Adapter()
    dest = tmp_path / "t.xlsx"
    adapter.prepare_copy(dest)
    baseline = get_template_baseline(adapter.template_path())
    writer = SafeWorkbookWriter(dest, {"Input!Z99"}, template_baseline=baseline)
    with pytest.raises(IntegrityError, match="whitelist|listei albe"):
        writer.write("Input", "A1", 1)


def test_sentinels_do_not_become_zero(mock_client: MockFootyStatsClient):
    """null / -1 / -2 rămân NOT AVAILABLE, nu 0."""
    matches = [
        {
            "id": "99999",
            "homeID": 1,
            "awayID": 2,
            "competition_id": 2012,
            "date_unix": -1,
            "odds_ft_1": -1,
            "odds_ft_x": None,
            "odds_ft_2": -2,
        }
    ]
    enriched = enrich_matches_batch(
        mock_client,
        matches,
        model_ids=["double_chance"],
        tz_name="Europe/Bucharest",
    )
    md = enriched[0]
    assert md.kickoff_bucharest is None
    assert md.odds_ft_1.is_unavailable()
    assert md.odds_ft_1.numeric_or_none() is None
    assert md.odds_ft_x.is_unavailable()
    assert md.odds_ft_x.numeric_or_none() is None
    assert md.odds_ft_2.is_unavailable()
    assert md.odds_ft_2.numeric_or_none() is None


def test_over05_parity_rows_unchanged(tmp_path: Path, monkeypatch):
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    result = run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012, 2013],
        match_ids=["90001", "90002", "90003"],
        model_ids=["over05"],
    )
    for row in result["rows"]:
        if row["model_id"] != "over05" or row["g0"] == "FAIL":
            continue
        assert row["recommendation"]
        assert row["p_over"] is not None
        assert row["confidence"] is not None


def test_double_chance_parity_audit_columns(tmp_path: Path, monkeypatch):
    import config.settings as settings
    import src.pipeline as pipeline

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "get_client", lambda: MockFootyStatsClient())
    result = run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012],
        match_ids=["90001"],
        model_ids=["double_chance"],
    )
    row = result["rows"][0]
    assert row["dc_shrinkage_applied"] in {"DA", "NU"}
    assert "dc_weight_current" in row
    selections = row["dc_selections"]
    assert {s["selection"] for s in selections} == {"1X", "X2", "12"}
    for code in ("1X", "X2", "12"):
        sel = next(s for s in selections if s["selection"] == code)
        assert sel["p_adj"] is not None
        assert sel["verdict"]
