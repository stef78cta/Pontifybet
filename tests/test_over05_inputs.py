"""Mapping FootyStats → celule Over 0.5: conversii de unitate, fără date inventate."""

import pytest

from src.api.mock import MockFootyStatsClient
from src.engines.over05 import compute_over05
from src.engines.over05.inputs import (
    _indicator,
    complement_rate,
    excel_rate,
    match_to_over05_inputs,
    per_match_average,
    under_rate,
)
from src.models.match_data import Indicator


def test_excel_rate_converts_percent_scale():
    assert excel_rate(Indicator(value=93)) == 0.93
    assert excel_rate(Indicator(value=0.9)) == 0.9
    assert excel_rate(Indicator(value=-1)) is None


def test_indicator_missing_attribute_is_blank():
    assert _indicator(object(), "league_avg_gf_home").numeric_or_none() is None


def test_complement_rate_is_under05_identity():
    assert complement_rate(Indicator(value=93)) == pytest.approx(0.07)
    assert complement_rate(Indicator(value=0)) == pytest.approx(1.0)
    assert complement_rate(Indicator(value=-1)) is None


def test_under_rate_prefers_direct_under05():
    assert under_rate(Indicator(value=8), Indicator(value=93)) == pytest.approx(0.08)
    assert under_rate(Indicator(value=None), Indicator(value=93)) == pytest.approx(0.07)


def test_per_match_average_requires_sample():
    assert per_match_average(Indicator(value=32), Indicator(value=14)) == 32 / 14
    assert per_match_average(Indicator(value=32), Indicator(value=None)) is None
    assert per_match_average(Indicator(value=-1), Indicator(value=14)) is None


def test_mock_mapping_does_not_invent_context_or_h2h():
    client = MockFootyStatsClient()
    md = client.enrich_match(client.matches_by_date("2026-03-15")[0])
    values = match_to_over05_inputs(md)

    assert values["N"] == 0.93
    assert values["U"] == 0.88
    assert values["O"] == 0.07
    assert values["J"] == 32 / 14
    assert values["Q"] == 20 / 14
    assert values["X"] == 9 / 5
    assert values["EX"] == 0.43
    assert values["EY"] == 0.25

    for col in ("AH", "AI", "AM", "AN"):
        assert values[col] is None
    for col in ("AV", "AW", "AX", "AY", "AZ", "BA", "BB", "BC", "BD", "BE", "BF", "BG"):
        assert values[col] is None
    for col in ("CM", "CN", "CO", "CP", "CJ", "CK", "CL"):
        assert values[col] is None
    assert values["FB"] is None


def test_mock_mapping_fills_zero_mass_from_footystats():
    """0-0 FT = Under 0.5 = complement Over 0.5; HT și last-x sunt câmpuri API."""
    client = MockFootyStatsClient()
    md = client.enrich_match(client.matches_by_date("2026-03-15")[0])
    values = match_to_over05_inputs(md)

    assert values["EV"] == pytest.approx(0.07)
    assert values["EW"] == pytest.approx(0.12)
    assert values["EZ"] == pytest.approx(0.30)
    assert values["FA"] == pytest.approx(0.35)
    assert values["FY"] == pytest.approx(0.20)
    assert values["FZ"] == pytest.approx(0.20)
    assert values["GA"] == 0
    assert values["GB"] == 0
    assert values["AJ"] is not None
    assert values["AK"] is not None
    assert values["AL"] == pytest.approx(values["AJ"] + values["AK"])


def test_mock_over05_g0_not_zero_mass_incomplete():
    client = MockFootyStatsClient()
    md = client.enrich_match(client.matches_by_date("2026-03-15")[0])
    result = compute_over05(match_to_over05_inputs(md))
    assert result.g0 is not None
    assert "ZERO-MASS INCOMPLETE" not in result.g0
    assert result.g0 == "PASS"
