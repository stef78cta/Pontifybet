"""Invarianți de paritate Excel V2 pentru câmpurile expuse de aplicație.

Testul de paritate pe celule (`test_double_chance_excel_parity`) verifică valorile
față de `cazuri_test.json`. Aici se verifică faptul că obiectele Python expuse mai
departe (Pfail model/piață/DC, haircut descompus, componentele de risc, nivelul)
rămân identice cu relațiile din workbook, nu doar cu celulele izolate.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from src.engines.double_chance import compute_double_chance

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs" / "PontifyBet_Sansa_Dubla_V2_Pachet_Cursor"
TOL = 1e-12


@pytest.fixture(scope="module")
def computed():
    cases = json.loads((SPEC / "cazuri_test.json").read_text(encoding="utf-8"))["cases"]
    return [(case["id"], compute_double_chance(case["inputs"])) for case in cases]


def _close(left, right) -> bool:
    return math.isclose(left, right, rel_tol=TOL, abs_tol=TOL)


def test_suite_covers_all_fixtures(computed):
    assert len(computed) == 37


def test_pfail_dc_is_conservative_max_of_model_and_market(computed):
    checked = 0
    for case_id, result in computed:
        for sel in result.selections:
            if sel.pfail_model is None or sel.pfail_market is None:
                continue
            assert sel.pfail_dc is not None, f"{case_id}/{sel.code}"
            assert _close(sel.pfail_dc, max(sel.pfail_model, sel.pfail_market)), (
                f"{case_id}/{sel.code}: {sel.pfail_dc} != max({sel.pfail_model}, {sel.pfail_market})"
            )
            checked += 1
    assert checked > 0


def test_haircut_total_is_base_plus_early_season(computed):
    checked = 0
    for case_id, result in computed:
        for sel in result.selections:
            if sel.haircut_total is None or sel.haircut_base is None or sel.haircut_early is None:
                continue
            assert _close(sel.haircut_total, sel.haircut_base + sel.haircut_early), (
                f"{case_id}/{sel.code}"
            )
            checked += 1
    assert checked > 0


def test_p_adj_is_p_model_minus_haircut_floored_at_zero(computed):
    checked = 0
    for case_id, result in computed:
        for sel in result.selections:
            if sel.p_adj is None or sel.p_model is None or sel.haircut_total is None:
                continue
            assert _close(sel.p_adj, max(0.0, sel.p_model - sel.haircut_total)), (
                f"{case_id}/{sel.code}"
            )
            checked += 1
    assert checked > 0


def test_blended_1x2_sums_to_one_after_normalisation(computed):
    checked = 0
    for case_id, result in computed:
        parts = [result.cells.get(f"Model_1X2!{col}10") for col in ("B", "C", "D")]
        if any(not isinstance(p, (int, float)) for p in parts):
            continue
        assert _close(sum(parts), 1.0), f"{case_id}: {parts}"
        checked += 1
    assert checked > 0


def test_risk_decomposition_reproduces_excel_score(computed):
    checked = 0
    for case_id, result in computed:
        for sel in result.selections:
            if sel.score is None or sel.risk.score_before_cap is None:
                continue
            cap = sel.risk.score_before_cap
            assert sel.score == min(100, cap), f"{case_id}/{sel.code}: {sel.score} vs cap {cap}"
            checked += 1
    assert checked > 0


def test_capped_scores_keep_distinguishable_raw_value(computed):
    raws = {
        sel.risk.score_before_cap
        for _, result in computed
        for sel in result.selections
        if sel.score == 100 and sel.risk.score_before_cap is not None
    }
    assert len(raws) > 1
    assert max(raws) > 100


def test_risk_level_mapping_is_20_40_60_80(computed):
    checked = 0
    for case_id, result in computed:
        for sel in result.selections:
            if sel.score is None or sel.level is None:
                continue
            expected = 1 if sel.score <= 20 else 2 if sel.score <= 40 else 3 if sel.score <= 60 else 4 if sel.score <= 80 else 5
            # AC poate majora nivelul prin fragilitate materială; nivelul nu scade niciodată.
            assert sel.level >= expected, f"{case_id}/{sel.code}: nivel {sel.level} < {expected}"
            assert sel.level <= 5
            checked += 1
    assert checked > 0


def test_draw_gate_uses_model_plus_haircut_against_market(computed):
    checked = 0
    for case_id, result in computed:
        sel = result.by_code("12")
        draw = sel.draw
        if draw is None or draw.model_plus_haircut is None or draw.market is None:
            continue
        assert _close(draw.adjusted, max(draw.model_plus_haircut, draw.market)), case_id
        if draw.model_raw is not None and sel.haircut_total is not None:
            assert _close(draw.model_plus_haircut, min(1.0, draw.model_raw + sel.haircut_total)), (
                case_id
            )
        checked += 1
    assert checked > 0


def test_defensive_flag_requires_ranking_eligible_and_defensive_verdict(computed):
    for case_id, result in computed:
        for sel in result.selections:
            if sel.defensive_eligible == "YES":
                assert sel.ranking_eligible == "YES", f"{case_id}/{sel.code}"
                assert sel.verdict == "DEFENSIV", f"{case_id}/{sel.code}"


def test_ranking_eligible_requires_ready_release_and_passing_gate(computed):
    for case_id, result in computed:
        for sel in result.selections:
            if sel.ranking_eligible != "YES":
                continue
            assert sel.release == "READY", f"{case_id}/{sel.code}"
            assert sel.p0_final in {"PASS", "PRUDENT"}, f"{case_id}/{sel.code}"
            assert sel.level is not None and sel.level < 5, f"{case_id}/{sel.code}"


def test_gate_status_is_not_the_final_verdict(computed):
    """Un control PRUDENT nu impune verdict PRUDENT; nivelul decide."""
    divergent = [
        (case_id, sel.code, sel.p0_final, sel.verdict)
        for case_id, result in computed
        for sel in result.selections
        if sel.p0_final == "PRUDENT" and sel.verdict not in {None, "PRUDENT"}
    ]
    assert divergent, "fixture-urile ar trebui să conțină cel puțin un gate PRUDENT cu alt verdict"
