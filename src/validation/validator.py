"""Validator conform Matrice_lipsa_date_v4 — hard fail doar pe G0 critic."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from src.models.match_data import DataStatus, Indicator, MatchData


@dataclass
class ValidationIssue:
    match_id: str
    model_id: str
    indicator: str
    g_level: str
    status: str
    blocking: bool
    reason: str
    refresh_plan: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    def blocking_for(self, match_id: str, model_id: str) -> list[ValidationIssue]:
        return [i for i in self.issues if i.match_id == match_id and i.model_id == model_id and i.blocking]

    def is_blocked(self, match_id: str, model_id: str) -> bool:
        return bool(self.blocking_for(match_id, model_id))

    def to_dict(self) -> dict[str, Any]:
        return {"issues": [i.to_dict() for i in self.issues]}


def _check_indicator(
    report: ValidationReport,
    match: MatchData,
    model_id: str,
    name: str,
    ind: Indicator,
    g_level: str,
    critical: bool,
) -> None:
    if ind.data_status == DataStatus.SMALL_SAMPLE:
        report.issues.append(
            ValidationIssue(
                match_id=match.match_id,
                model_id=model_id,
                indicator=name,
                g_level=g_level,
                status=ind.data_status.value,
                blocking=False,
                reason="Eșantion mic (SMALL SAMPLE) — nu blochează automat.",
            )
        )
        return

    if ind.data_status == DataStatus.PENDING_OFFICIAL:
        report.issues.append(
            ValidationIssue(
                match_id=match.match_id,
                model_id=model_id,
                indicator=name,
                g_level=g_level,
                status=ind.data_status.value,
                blocking=False,
                reason="Date oficiale încă nepublicate.",
                refresh_plan="Reîncarcă după publicarea XI / datelor oficiale.",
            )
        )
        return

    if ind.data_status == DataStatus.AVAILABLE_NOT_CHECKED:
        report.issues.append(
            ValidationIssue(
                match_id=match.match_id,
                model_id=model_id,
                indicator=name,
                g_level=g_level,
                status=ind.data_status.value,
                blocking=False,
                reason="Sourcing incomplet (AVAILABLE - NOT CHECKED), nu e valoarea zero.",
            )
        )

    if ind.is_unavailable():
        blocking = critical and g_level == "G0"
        status = ind.data_status.value if ind.data_status == DataStatus.NOT_AVAILABLE else DataStatus.NOT_AVAILABLE.value
        report.issues.append(
            ValidationIssue(
                match_id=match.match_id,
                model_id=model_id,
                indicator=name,
                g_level=g_level,
                status=status,
                blocking=blocking,
                reason=(
                    f"Input G0 critic lipsă ({name}). Nu inventăm date; modelul este blocat pentru acest meci."
                    if blocking
                    else f"Valoare indisponibilă pentru {name} (null/-1/-2)."
                ),
            )
        )


def validate_match_for_model(match: MatchData, model_id: str) -> ValidationReport:
    """Validează MatchData pentru un model pilot."""
    report = ValidationReport()

    if model_id == "over05":
        checks = [
            ("home_over05_home", match.home.over05_pct_home, "G0", True),
            ("away_over05_away", match.away.over05_pct_away, "G0", True),
            ("home_fts_home", match.home.fts_pct_home, "G0", True),
            ("away_fts_away", match.away.fts_pct_away, "G0", True),
            ("home_cs_home", match.home.cs_pct_home, "G0", True),
            ("away_cs_away", match.away.cs_pct_away, "G0", True),
            ("home_matches_home", match.home.matches_played_home, "G0", True),
            ("away_matches_away", match.away.matches_played_away, "G0", True),
            ("home_xg_home", match.home.xg_for_home, "G1", False),
            ("odds_over05", match.odds_ft_over05, "G3", False),
        ]
    elif model_id == "double_chance":
        checks = [
            ("odds_1", match.odds_ft_1, "G0", True),
            ("odds_x", match.odds_ft_x, "G0", True),
            ("odds_2", match.odds_ft_2, "G0", True),
            ("home_sample", match.home.matches_played_home, "G0", True),
            ("away_sample", match.away.matches_played_away, "G0", True),
        ]
    elif model_id == "corners":
        checks = [
            ("home_corners_for_season", match.home.corners_for_overall, "G0", True),
            ("home_corners_against_season", match.home.corners_against_overall, "G0", True),
            ("home_corners_for_home", match.home.corners_for_home, "G0", True),
            ("home_corners_against_home", match.home.corners_against_home, "G0", True),
            ("home_corners_for_recent", match.home.last5_corners_for, "G0", True),
            ("home_corners_against_recent", match.home.last5_corners_against, "G0", True),
            ("away_corners_for_season", match.away.corners_for_overall, "G0", True),
            ("away_corners_against_season", match.away.corners_against_overall, "G0", True),
            ("away_corners_for_away", match.away.corners_for_away, "G0", True),
            ("away_corners_against_away", match.away.corners_against_away, "G0", True),
            ("away_corners_for_recent", match.away.last5_corners_for, "G0", True),
            ("away_corners_against_recent", match.away.last5_corners_against, "G0", True),
            ("home_sample", match.home.matches_played_overall, "G0", True),
            ("away_sample", match.away.matches_played_overall, "G0", True),
        ]
    else:
        report.issues.append(
            ValidationIssue(
                match_id=match.match_id,
                model_id=model_id,
                indicator="model",
                g_level="G0",
                status=DataStatus.NOT_AVAILABLE.value,
                blocking=True,
                reason=f"Model necunoscut: {model_id}",
            )
        )
        return report

    for name, ind, g_level, critical in checks:
        _check_indicator(report, match, model_id, name, ind, g_level, critical)

    if not match.kickoff_utc:
        report.issues.append(
            ValidationIssue(
                match_id=match.match_id,
                model_id=model_id,
                indicator="kickoff_utc",
                g_level="G0",
                status=DataStatus.NOT_AVAILABLE.value,
                blocking=True,
                reason="Data/ora meciului lipsește.",
            )
        )

    return report


def merge_reports(reports: list[ValidationReport]) -> ValidationReport:
    out = ValidationReport()
    for r in reports:
        out.issues.extend(r.issues)
    return out
