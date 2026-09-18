"""Paritate motor Șansă Dublă V2 față de cazuri_test.json."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from src.engines.double_chance import compute_double_chance

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs" / "PontifyBet_Sansa_Dubla_V2_Pachet_Cursor"
TOL = 1e-12
WORKBOOK_SHA256 = "321546054b7199ba1f4f7f96599cb7f6c43a88c526da25e24fa2a31d3235821b"


def _load_suite():
    return json.loads((SPEC / "cazuri_test.json").read_text(encoding="utf-8"))


def _blank(value) -> bool:
    return value is None or value == ""


def _same(actual, expected, *, exact_number: bool = False) -> bool:
    if isinstance(actual, str) and actual.startswith("ERROR:"):
        return False
    if _blank(actual) and _blank(expected):
        return True
    if isinstance(actual, (int, float)) and not isinstance(actual, bool):
        if isinstance(expected, (int, float)) and not isinstance(expected, bool):
            if exact_number:
                return float(actual) == float(expected)
            return math.isclose(float(actual), float(expected), rel_tol=TOL, abs_tol=TOL)
        return False
    return actual == expected


def _exact_score_or_level(cell: str) -> bool:
    return bool(
        cell.startswith("Double_Chance!L") or cell.startswith("Double_Chance!M")
    ) and cell[-1] in "456"


@pytest.fixture(scope="module")
def suite():
    return _load_suite()


@pytest.fixture(scope="module")
def cases(suite):
    return suite["cases"]


def test_workbook_sha256_matches_manifest(suite):
    from hashlib import sha256

    from config.settings import TEMPLATES_DIR

    path = TEMPLATES_DIR / "11_model_analiza_pariu_sansadubla_optimizat_V2.xlsx"
    digest = sha256(path.read_bytes()).hexdigest()
    manifest = json.loads((SPEC / "manifest.json").read_text(encoding="utf-8"))
    assert digest == WORKBOOK_SHA256
    assert manifest["sha256"] == WORKBOOK_SHA256
    assert suite["numeric_tolerance"] == TOL


def test_suite_has_37_cases(cases):
    assert len(cases) == 37
    assert cases[0]["id"] == "baseline"


@pytest.mark.parametrize("index", range(37))
def test_fixture_expected_cells(cases, index):
    case = cases[index]
    result = compute_double_chance(case["inputs"], evaluate=case["expected"].keys())
    mismatches = []
    for cell, expected in case["expected"].items():
        actual = result.cells.get(cell)
        exact = _exact_score_or_level(cell)
        if not _same(actual, expected, exact_number=exact):
            mismatches.append(f"{cell}: actual={actual!r} expected={expected!r}")
    assert not mismatches, f"{case['id']}:\n" + "\n".join(mismatches)


def test_baseline_official_reference(cases):
    result = compute_double_chance(cases[0]["inputs"])
    one_x, x2, dnb = result.by_code("1X"), result.by_code("X2"), result.by_code("12")
    assert _same(one_x.p_adj, 0.92)
    assert one_x.score == 16
    assert one_x.level == 1
    assert one_x.verdict == "DEFENSIV"
    assert _same(x2.p_adj, 0.165)
    assert x2.score == 100
    assert x2.level == 5
    assert x2.verdict == "NO BET"
    assert _same(dnb.p_adj, 0.885)
    assert dnb.score == 22
    assert dnb.level == 2
    assert dnb.verdict == "PRUDENT"


def test_price_invariance_does_not_change_verdict_or_eligibility(cases):
    by_id = {c["id"]: c for c in cases}
    base = compute_double_chance(by_id["baseline"]["inputs"])
    invariant = compute_double_chance(by_id["price_invariance"]["inputs"])
    for code in ("1X", "X2", "12"):
        left, right = base.by_code(code), invariant.by_code(code)
        assert left.verdict == right.verdict
        assert left.score == right.score
        assert left.level == right.level
        assert left.ranking_eligible == right.ranking_eligible


def test_audit_1x_does_not_auto_block_x2_or_12(cases):
    case = next(c for c in cases if c["id"] == "fragility_open")
    result = compute_double_chance(case["inputs"], evaluate=case["expected"].keys())
    assert result.cells["Double_Chance!N4"] == case["expected"]["Double_Chance!N4"]
    assert result.cells["Double_Chance!N5"] == case["expected"]["Double_Chance!N5"]
    assert result.cells["Double_Chance!N6"] == case["expected"]["Double_Chance!N6"]
    assert result.cells["Double_Chance!N5"] != result.cells["Double_Chance!N4"]
    assert result.cells["Double_Chance!N6"] != result.cells["Double_Chance!N4"]
