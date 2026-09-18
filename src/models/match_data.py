"""Schema canonică MatchData + Indicator pentru toate adaptoarele."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class DataStatus(str, Enum):
    AVAILABLE_CHECKED = "AVAILABLE - CHECKED"
    AVAILABLE_NOT_CHECKED = "AVAILABLE - NOT CHECKED"
    DERIVED = "DERIVED"
    PROXY_ONLY = "PROXY ONLY"
    PENDING_OFFICIAL = "PENDING OFFICIAL"
    SOURCE_CONFLICT = "SOURCE CONFLICT"
    NOT_AVAILABLE = "NOT AVAILABLE"
    SMALL_SAMPLE = "SMALL SAMPLE"


SENTINEL_UNAVAILABLE = {-1, -2}


def make_trace_id() -> str:
    return uuid4().hex[:12]


class Indicator(BaseModel):
    """Un indicator cu valoare + metadate de trasabilitate."""

    value: Any = None
    n: int | None = None
    unit: str | None = None
    endpoint: str | None = None
    extracted_at: datetime | None = None
    cutoff: datetime | None = None
    method: str = "direct"
    data_status: DataStatus = DataStatus.AVAILABLE_NOT_CHECKED
    trace_id: str = Field(default_factory=make_trace_id)

    def is_unavailable(self) -> bool:
        if self.value is None:
            return True
        if isinstance(self.value, (int, float)) and self.value in SENTINEL_UNAVAILABLE:
            return True
        return self.data_status == DataStatus.NOT_AVAILABLE

    def numeric_or_none(self) -> float | None:
        """Returnează numărul doar dacă e disponibil real (nu -1/-2/null)."""
        if self.is_unavailable():
            return None
        if isinstance(self.value, (int, float)) and not isinstance(self.value, bool):
            return float(self.value)
        return None


def indicator_from_raw(
    raw: Any,
    *,
    unit: str | None = None,
    endpoint: str | None = None,
    method: str = "direct",
    n: int | None = None,
    extracted_at: datetime | None = None,
    cutoff: datetime | None = None,
    small_sample_threshold: int = 8,
) -> Indicator:
    """Construiește Indicator din valoare brută FootyStats (respectă -1/-2)."""
    now = extracted_at or datetime.utcnow()
    if raw is None:
        return Indicator(
            value=None,
            n=n,
            unit=unit,
            endpoint=endpoint,
            extracted_at=now,
            cutoff=cutoff,
            method=method,
            data_status=DataStatus.NOT_AVAILABLE,
        )
    if isinstance(raw, (int, float)) and raw in SENTINEL_UNAVAILABLE:
        return Indicator(
            value=raw,
            n=n,
            unit=unit,
            endpoint=endpoint,
            extracted_at=now,
            cutoff=cutoff,
            method=method,
            data_status=DataStatus.NOT_AVAILABLE,
        )
    status = DataStatus.AVAILABLE_CHECKED
    if n is not None and n < small_sample_threshold:
        status = DataStatus.SMALL_SAMPLE
    return Indicator(
        value=raw,
        n=n,
        unit=unit,
        endpoint=endpoint,
        extracted_at=now,
        cutoff=cutoff,
        method=method,
        data_status=status,
    )


class TeamSideStats(BaseModel):
    """Statistici pe o parte (home sau away)."""

    team_id: int | None = None
    name: str = ""
    matches_played_overall: Indicator = Field(default_factory=Indicator)
    matches_played_home: Indicator = Field(default_factory=Indicator)
    matches_played_away: Indicator = Field(default_factory=Indicator)
    goals_for_overall: Indicator = Field(default_factory=Indicator)
    goals_against_overall: Indicator = Field(default_factory=Indicator)
    goals_for_home: Indicator = Field(default_factory=Indicator)
    goals_against_home: Indicator = Field(default_factory=Indicator)
    goals_for_away: Indicator = Field(default_factory=Indicator)
    goals_against_away: Indicator = Field(default_factory=Indicator)
    xg_for_home: Indicator = Field(default_factory=Indicator)
    xg_against_home: Indicator = Field(default_factory=Indicator)
    xg_for_away: Indicator = Field(default_factory=Indicator)
    xg_against_away: Indicator = Field(default_factory=Indicator)
    over05_pct_home: Indicator = Field(default_factory=Indicator)
    over05_pct_away: Indicator = Field(default_factory=Indicator)
    fts_pct_home: Indicator = Field(default_factory=Indicator)
    fts_pct_away: Indicator = Field(default_factory=Indicator)
    fts_pct_overall: Indicator = Field(default_factory=Indicator)
    cs_pct_home: Indicator = Field(default_factory=Indicator)
    cs_pct_away: Indicator = Field(default_factory=Indicator)
    corners_for_overall: Indicator = Field(default_factory=Indicator)
    corners_against_overall: Indicator = Field(default_factory=Indicator)
    corners_for_home: Indicator = Field(default_factory=Indicator)
    corners_against_home: Indicator = Field(default_factory=Indicator)
    corners_for_away: Indicator = Field(default_factory=Indicator)
    corners_against_away: Indicator = Field(default_factory=Indicator)
    last5_n: Indicator = Field(default_factory=Indicator)
    last5_gf: Indicator = Field(default_factory=Indicator)
    last5_ga: Indicator = Field(default_factory=Indicator)
    last5_xgf: Indicator = Field(default_factory=Indicator)
    last5_xga: Indicator = Field(default_factory=Indicator)
    last5_corners_for: Indicator = Field(default_factory=Indicator)
    last5_corners_against: Indicator = Field(default_factory=Indicator)
    last10_n: Indicator = Field(default_factory=Indicator)
    last10_gf: Indicator = Field(default_factory=Indicator)
    last10_ga: Indicator = Field(default_factory=Indicator)


class MatchData(BaseModel):
    """Obiect canonic folosit de validator și adaptoare."""

    match_id: str
    season_id: int | None = None
    competition_id: int | None = None
    competition_name: str = ""
    season: str = ""
    kickoff_utc: datetime | None = None
    kickoff_bucharest: datetime | None = None
    home: TeamSideStats = Field(default_factory=TeamSideStats)
    away: TeamSideStats = Field(default_factory=TeamSideStats)
    odds_ft_1: Indicator = Field(default_factory=Indicator)
    odds_ft_x: Indicator = Field(default_factory=Indicator)
    odds_ft_2: Indicator = Field(default_factory=Indicator)
    odds_ft_over05: Indicator = Field(default_factory=Indicator)
    odds_ft_under05: Indicator = Field(default_factory=Indicator)
    h2h_n: Indicator = Field(default_factory=Indicator)
    round: str | None = None
    native_match_history: list[dict[str, Any]] = Field(default_factory=list)
    source_mode: str = "mock"
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
