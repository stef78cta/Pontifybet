"""Coloanele tabelului „Istoric și rezultate”."""

from __future__ import annotations

from src.history.views import history_table_rows

EXPECTED_COLUMNS = [
    "Data",
    "Liga",
    "Meci",
    "Model",
    "Piață/Linie",
    "Recomandare",
    "Risk Level",
    "P ajustată",
    "Rezultat",
    "Outcome",
    "Status",
]


def _row(**overrides):
    row = {
        "kickoff_unix": 1773550800,
        "league": "Premier League",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "model_key": "over05",
        "market": "OVER_0_5",
        "line": 0.5,
        "recommendation": "PARIU RECOMANDAT",
        "risk_level": 2,
        "p_adjusted": 0.9412,
        "home_goals": 2,
        "away_goals": 1,
        "total_corners": None,
        "outcome": "HIT",
        "settlement_status": "SETTLED",
        "snapshot_status": "FROZEN_PREMATCH",
    }
    row.update(overrides)
    return row


def test_columns_and_formatting():
    rows = history_table_rows([_row()])
    assert list(rows[0].keys()) == EXPECTED_COLUMNS
    assert rows[0]["Meci"] == "Arsenal vs Chelsea"
    assert rows[0]["Model"] == "Over 0.5 V4"
    assert rows[0]["Piață/Linie"] == "Over 0.5"
    assert rows[0]["P ajustată"] == "94.12%"
    assert rows[0]["Rezultat"] == "2-1"
    assert rows[0]["Status"] == "SETTLED"


def test_corners_line_label_and_total():
    rows = history_table_rows(
        [_row(model_key="corners", market="CORNERS_UNDER", line=10.5, total_corners=7)]
    )
    assert rows[0]["Piață/Linie"] == "Cornere Under 10.5"
    assert rows[0]["Rezultat"] == "2-1 | 7 cornere"


def test_missing_corners_are_labelled_not_available():
    rows = history_table_rows(
        [_row(model_key="corners", market="CORNERS_OVER", line=8.5, total_corners=None)]
    )
    assert "NOT AVAILABLE" in rows[0]["Rezultat"]


def test_missing_kickoff_and_probability_are_not_zero():
    rows = history_table_rows([_row(kickoff_unix=None, p_adjusted=None, outcome=None)])
    assert rows[0]["Data"] == "—"
    assert rows[0]["P ajustată"] == "—"
    assert rows[0]["Outcome"] == "—"


def test_pending_snapshot_falls_back_to_snapshot_status():
    rows = history_table_rows(
        [
            _row(
                settlement_status=None,
                snapshot_status="PENDING_EXCEL_RECALC",
                recommendation=None,
            )
        ]
    )
    assert rows[0]["Status"] == "PENDING_EXCEL_RECALC"
    assert rows[0]["Recomandare"] == "—"
