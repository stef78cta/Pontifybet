"""Paritate motor Over 0.5 V4 față de fixture-urile și scenariile din specificație."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from src.engines.over05 import OFFICIAL_COLUMNS, compute_over05

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs" / "Pontifybet_Over05_V4_specificatii"
TOL = 1e-12
WORKBOOK_SHA256 = "8068c1f95c8dfa28def846b51b9f152a9e52fd085d8085344a5321b97338c42a"


def _load_json(name: str):
    return json.loads((SPEC / name).read_text(encoding="utf-8"))


def _blank(value) -> bool:
    return value is None or value == ""


def _same(actual, expected) -> bool:
    if isinstance(actual, str) and actual.startswith("ERROR:"):
        return isinstance(expected, str) and expected.startswith("ERROR:")
    if _blank(actual) and _blank(expected):
        return True
    if isinstance(actual, (int, float)) and not isinstance(actual, bool):
        if isinstance(expected, (int, float)) and not isinstance(expected, bool):
            return math.isclose(float(actual), float(expected), rel_tol=TOL, abs_tol=TOL)
        return False
    return actual == expected


@pytest.fixture(scope="module")
def fixtures():
    return _load_json("golden_fixtures.json")


@pytest.fixture(scope="module")
def simulations():
    return _load_json("simulations.json")


def test_workbook_sha256_matches_spec(fixtures):
    from hashlib import sha256

    from config.settings import TEMPLATES_DIR

    path = TEMPLATES_DIR / "1_model_analiza_over0.5_optimizat_V4.xlsx"
    assert sha256(path.read_bytes()).hexdigest() == WORKBOOK_SHA256
    assert fixtures["workbook_sha256"] == WORKBOOK_SHA256


@pytest.mark.parametrize("index", range(5))
def test_demo_official_outputs_match_cache(fixtures, index):
    fixture = fixtures["fixtures"][index]
    result = compute_over05(fixture["inputs"], excel_row=fixture["excel_row"])
    for col in OFFICIAL_COLUMNS:
        expected = fixture["outputs"][col]["cache"]
        actual = result.cells[col]
        assert _same(actual, expected), (
            f"{fixture['match_id']} {col}: actual={actual!r} expected={expected!r}"
        )


def test_demo_liga_reference_values(fixtures):
    fixture = fixtures["fixtures"][0]
    result = compute_over05(fixture["inputs"], excel_row=4)
    assert _same(result.p0_recalibrated, 0.05643773654116299)
    assert _same(result.p_over_reported, 0.92)
    assert _same(result.confidence, 59.194772288905426)
    assert _same(result.risk_score, 7.870120560697213)
    assert result.g0 == "PASS"
    assert result.risk_level == 1
    assert result.recommendation == "DEFENSIV"


@pytest.mark.parametrize("index", range(13))
def test_specification_scenarios(fixtures, simulations, index):
    scenario = simulations[index]
    base = dict(fixtures["fixtures"][0]["inputs"])
    base.update(scenario["overrides"])
    result = compute_over05(base, excel_row=4)
    for col, expected in scenario["simulated"].items():
        if col not in OFFICIAL_COLUMNS and col not in {"GJ", "GM", "GO"}:
            continue
        actual = result.cells[col]
        assert _same(actual, expected), (
            f"{scenario['name']} {col}: actual={actual!r} expected={expected!r}"
        )


def test_odds_and_lineup_do_not_change_recommendation(fixtures, simulations):
    by_name = {s["name"]: s for s in simulations}
    base_hk = "DEFENSIV"
    base_he = fixtures["fixtures"][0]["outputs"]["HE"]["cache"]
    for name in ("no_odds", "confirmed_lineup", "striker_absent", "odds_changed"):
        sim = by_name[name]
        inputs = dict(fixtures["fixtures"][0]["inputs"])
        inputs.update(sim["overrides"])
        result = compute_over05(inputs, excel_row=4)
        assert result.recommendation == base_hk
        assert _same(result.risk_score, base_he)


def test_unused_fb_does_not_change_official_outputs(fixtures, simulations):
    sim = next(s for s in simulations if s["name"] == "unused_FB")
    inputs = dict(fixtures["fixtures"][0]["inputs"])
    inputs.update(sim["overrides"])
    result = compute_over05(inputs, excel_row=4)
    for col in OFFICIAL_COLUMNS:
        assert _same(result.cells[col], sim["simulated"][col])


@pytest.mark.parametrize(
    ("he", "expected_level", "expected_hk"),
    [
        (20, 1, "DEFENSIV"),
        (20.1, 2, "PRUDENT"),
        (40, 2, "PRUDENT"),
        (40.1, 3, "MODERAT"),
        (60, 3, "MODERAT"),
        (60.1, 4, "RIDICAT"),
        (80, 4, "RIDICAT"),
        (80.1, 5, "WATCH / NO BET"),
    ],
)
def test_selector_thresholds_on_injected_he(fixtures, he, expected_level, expected_hk):
    result = compute_over05(
        fixtures["fixtures"][0]["inputs"],
        excel_row=4,
        formula_overrides={"HE": he},
    )
    assert result.g0 == "PASS"
    assert result.risk_level == expected_level
    assert result.recommendation == expected_hk


def test_g0_fail_forces_watch(fixtures, simulations):
    sim = next(s for s in simulations if s["name"] == "missing_EV")
    inputs = dict(fixtures["fixtures"][0]["inputs"])
    inputs.update(sim["overrides"])
    result = compute_over05(inputs, excel_row=4)
    assert result.g0 == "FAIL – DATE CRITICE ZERO-MASS INCOMPLETE"
    assert result.risk_level == 5
    assert result.recommendation == "WATCH / NO BET"
