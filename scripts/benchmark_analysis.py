"""Benchmark controlat ANALYSIS + EXPORT pe același set MOCK."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings
from src.api.mock import MockFootyStatsClient
from src.pipeline import run_analysis, run_export


def main() -> None:
    settings.ensure_runtime_dirs()
    client = MockFootyStatsClient()
    client._call_counts.clear()
    match_ids = ["90001", "90002", "90003"]
    model_ids = ["over05", "double_chance", "corners"]

    import src.pipeline as pipeline

    pipeline.get_client = lambda: client  # type: ignore[method-assign]

    analysis = run_analysis(
        date_iso="2026-03-15",
        league_ids=[2012, 2013],
        match_ids=match_ids,
        model_ids=model_ids,
    )
    counts_after_analysis = dict(client._call_counts)
    export = run_export(analysis["snapshot"])
    report = {
        "matches": len(match_ids),
        "models": model_ids,
        "analysis_profiler": analysis["profiler"],
        "export_profiler": export["profiler"],
        "counters_after_analysis": counts_after_analysis,
        "time_to_table_sec": analysis["profiler"].get("time_to_table_sec"),
        "time_to_export_sec": export["profiler"].get("time_to_export_sec"),
    }
    out = ROOT / "docs" / "performance_report_analysis.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
