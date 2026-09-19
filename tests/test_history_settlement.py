"""Reguli de settlement: Over 0.5, Șansă Dublă, Cornere, date lipsă."""

from __future__ import annotations

import pytest

from src.history.models import MatchResult, SettlementStatus
from src.history.results import match_result_from_payload
from src.history.settlement import settle_prediction


def _result(**overrides) -> MatchResult:
    data = {
        "provider_match_id": "90001",
        "match_status": "complete",
        "home_goals": None,
        "away_goals": None,
        "home_corners": None,
        "away_corners": None,
    }
    data.update(overrides)
    return MatchResult(**data)


# --- Over 0.5 -----------------------------------------------------------------


@pytest.mark.parametrize(
    "home,away",
    [(1, 0), (0, 1), (3, 2)],
)
def test_over_05_hit(home, away):
    decision = settle_prediction(
        market="OVER_0_5", line=0.5, result=_result(home_goals=home, away_goals=away)
    )
    assert decision.settlement_status == SettlementStatus.SETTLED.value
    assert decision.outcome == "HIT"


def test_over_05_miss_on_goalless_draw():
    decision = settle_prediction(
        market="OVER_0_5", line=0.5, result=_result(home_goals=0, away_goals=0)
    )
    assert decision.outcome == "MISS"


def test_null_score_is_not_a_miss():
    """`NULL` nu înseamnă 0-0; lipsa datelor nu poate produce MISS."""
    decision = settle_prediction(market="OVER_0_5", line=0.5, result=_result())
    assert decision.settlement_status == SettlementStatus.RESULT_DATA_UNAVAILABLE.value
    assert decision.outcome is None


def test_incomplete_match_stays_pending():
    decision = settle_prediction(
        market="OVER_0_5", line=0.5, result=_result(match_status="incomplete")
    )
    assert decision.settlement_status == SettlementStatus.PENDING_RESULT.value
    assert decision.outcome is None


def test_missing_result_stays_pending():
    decision = settle_prediction(market="OVER_0_5", line=0.5, result=None)
    assert decision.settlement_status == SettlementStatus.PENDING_RESULT.value


def test_canceled_match_is_result_data_unavailable():
    decision = settle_prediction(
        market="OVER_0_5",
        line=0.5,
        result=_result(match_status="canceled", home_goals=0, away_goals=0),
    )
    assert decision.settlement_status == SettlementStatus.RESULT_DATA_UNAVAILABLE.value
    assert decision.outcome is None


# --- Șansă Dublă --------------------------------------------------------------


@pytest.mark.parametrize(
    "market,home,away,expected",
    [
        ("1X", 2, 1, "HIT"),
        ("1X", 1, 1, "HIT"),
        ("1X", 0, 1, "MISS"),
        ("X2", 1, 2, "HIT"),
        ("X2", 1, 1, "HIT"),
        ("X2", 2, 1, "MISS"),
        ("12", 2, 1, "HIT"),
        ("12", 0, 3, "HIT"),
        ("12", 1, 1, "MISS"),
    ],
)
def test_double_chance_settlement(market, home, away, expected):
    decision = settle_prediction(
        market=market, line=None, result=_result(home_goals=home, away_goals=away)
    )
    assert decision.settlement_status == SettlementStatus.SETTLED.value
    assert decision.outcome == expected


# --- Cornere ------------------------------------------------------------------


@pytest.mark.parametrize(
    "market,line,home,away,expected",
    [
        ("CORNERS_OVER", 8.5, 6, 5, "HIT"),
        ("CORNERS_OVER", 8.5, 4, 4, "MISS"),
        ("CORNERS_OVER", 10.5, 5, 6, "HIT"),
        ("CORNERS_UNDER", 10.5, 4, 3, "HIT"),
        ("CORNERS_UNDER", 10.5, 7, 6, "MISS"),
        ("CORNERS_UNDER", 8.5, 4, 4, "HIT"),
    ],
)
def test_corners_settlement_per_line(market, line, home, away, expected):
    decision = settle_prediction(
        market=market, line=line, result=_result(home_corners=home, away_corners=away)
    )
    assert decision.settlement_status == SettlementStatus.SETTLED.value
    assert decision.outcome == expected


def test_missing_corners_is_result_data_unavailable_not_miss():
    decision = settle_prediction(
        market="CORNERS_OVER",
        line=8.5,
        result=_result(home_goals=1, away_goals=1, home_corners=None, away_corners=None),
    )
    assert decision.settlement_status == SettlementStatus.RESULT_DATA_UNAVAILABLE.value
    assert decision.outcome is None


def test_partial_corners_is_not_treated_as_zero():
    decision = settle_prediction(
        market="CORNERS_UNDER", line=8.5, result=_result(home_corners=4, away_corners=None)
    )
    assert decision.settlement_status == SettlementStatus.RESULT_DATA_UNAVAILABLE.value


def test_unknown_market_has_no_settlement_rule():
    decision = settle_prediction(
        market="BTTS", line=None, result=_result(home_goals=1, away_goals=1)
    )
    assert decision.settlement_status == SettlementStatus.RESULT_DATA_UNAVAILABLE.value


# --- Mapare payload FootyStats ------------------------------------------------


def test_payload_mapping_uses_official_field_names():
    payload = {
        "status": "Complete",
        "homeGoals": ["17", "43"],
        "awayGoals": ["66"],
        "homeGoalCount": 2,
        "awayGoalCount": 1,
        "team_a_corners": 6,
        "team_b_corners": 5,
    }
    result = match_result_from_payload("90001", payload)
    assert result.match_status == "complete"
    assert (result.home_goals, result.away_goals, result.total_goals) == (2, 1, 3)
    assert (result.home_corners, result.away_corners, result.total_corners) == (6, 5, 11)


def test_payload_sentinels_stay_none():
    result = match_result_from_payload(
        "90003",
        {
            "status": "complete",
            "homeGoalCount": 1,
            "awayGoalCount": 1,
            "team_a_corners": -1,
            "team_b_corners": -2,
        },
    )
    assert result.home_corners is None
    assert result.away_corners is None
    assert result.total_corners is None
    assert result.has_final_score is True
    assert result.has_final_corners is False
