"""Snapshot de analiză — material pentru export fără refetch/recalcul."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.engines.double_chance.engine import DoubleChanceOfficialResult
from src.engines.over05.engine import Over05OfficialResult
from src.models.match_data import MatchData
from src.validation.validator import ValidationReport


def analysis_fingerprint(
    *,
    date_iso: str,
    timezone_name: str,
    league_ids: list[int],
    match_ids: list[str],
    model_ids: list[str],
) -> tuple[Any, ...]:
    """Identificator determinist al parametrilor ultimei analize."""
    return (
        date_iso,
        timezone_name,
        tuple(sorted(int(x) for x in league_ids)),
        tuple(sorted(str(x) for x in match_ids)),
        tuple(sorted(model_ids)),
    )


@dataclass
class Over05MatchArtifacts:
    mapping: dict[str, Any]
    official: Over05OfficialResult


@dataclass
class DoubleChanceMatchArtifacts:
    mapping: dict[str, Any]
    official: DoubleChanceOfficialResult
    prior_weights: dict[str, Any]


@dataclass
class AnalysisSnapshot:
    """Date calculate în faza ANALYSIS — exportul le materializează."""

    fingerprint: tuple[Any, ...]
    date_iso: str
    timezone_name: str
    league_ids: list[int]
    match_ids: list[str]
    model_ids: list[str]
    match_data: list[MatchData]
    allowed_by_model: dict[str, list[MatchData]]
    reports: list[ValidationReport]
    rows: list[dict[str, Any]]
    over05: dict[str, Over05MatchArtifacts] = field(default_factory=dict)
    double_chance: dict[str, DoubleChanceMatchArtifacts] = field(default_factory=dict)
    mode: str = "live"

    def merged_report_dict(self) -> dict[str, Any]:
        from src.validation.validator import merge_reports

        return merge_reports(self.reports).to_dict()
