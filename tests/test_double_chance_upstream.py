"""Invarianți upstream: prior/shrinkage, componentele 1X2 și blend-ul.

Protejează instrumentarea adăugată în auditul upstream: urma trebuie să descrie
exact calculul de producție, iar contribuțiile blend-ului trebuie să reconstituie
`P_model` fără reziduu.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from src.api.mock import MockFootyStatsClient
from src.engines.double_chance import compute_double_chance, match_to_double_chance_inputs
from src.engines.double_chance.inputs import (
    derived_1x2_distributions,
    derived_1x2_trace,
    league_prior_is_valid,
    needs_early_season_prior,
)

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs" / "PontifyBet_Sansa_Dubla_V2_Pachet_Cursor"
TOL = 1e-12


def _close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=TOL, abs_tol=TOL)


@pytest.fixture(scope="module")
def matches():
    client = MockFootyStatsClient()
    return [client.enrich_match(raw) for raw in client.matches_by_date("2026-03-15")]


@pytest.fixture(scope="module")
def small_sample_match():
    client = MockFootyStatsClient()
    match = client.enrich_match(client.matches_by_date("2026-03-15")[0])
    match.home.matches_played_home.value = 3
    match.away.matches_played_away.value = 3
    return match


def test_production_function_delegates_to_trace(matches):
    for match in matches:
        for apply in (False, True):
            scoreline, strength = derived_1x2_distributions(match, apply_shrinkage=apply)
            trace = derived_1x2_trace(match, apply_shrinkage=apply)
            assert scoreline == trace.scoreline
            assert strength == trace.strength


def test_component_distributions_sum_to_one(matches):
    for match in matches:
        trace = derived_1x2_trace(match, apply_shrinkage=False)
        for triplet in (trace.scoreline, trace.strength, trace.scoreline_raw, trace.strength_raw):
            if triplet is None:
                continue
            assert _close(sum(triplet), 1.0)


def test_weights_sum_to_one_and_default_to_current_without_shrinkage(matches):
    for match in matches:
        trace = derived_1x2_trace(match, apply_shrinkage=False)
        for rate in trace.rates:
            assert rate.weight_current == 1.0
            assert rate.weight_prior == 0.0
            assert rate.shrunk == rate.observed


def test_shrinkage_weights_follow_sample_and_prior_size(small_sample_match):
    trace = derived_1x2_trace(small_sample_match, apply_shrinkage=True)
    checked = 0
    for rate in trace.rates:
        if not rate.prior_usable:
            continue
        expected = rate.n_current / (rate.n_current + rate.n_prior)
        assert _close(rate.weight_current, expected)
        assert _close(rate.weight_current + rate.weight_prior, 1.0)
        assert _close(
            rate.shrunk,
            rate.weight_current * rate.observed + rate.weight_prior * rate.prior,
        )
        checked += 1
    assert checked > 0


def test_shrinkage_moves_rates_toward_the_prior(small_sample_match):
    trace = derived_1x2_trace(small_sample_match, apply_shrinkage=True)
    moved = 0
    for rate in trace.rates:
        if not rate.prior_usable or rate.observed is None:
            continue
        if _close(rate.observed, rate.prior):
            continue
        # Valoarea de după trebuie să stea strict între observat și prior.
        low, high = sorted((rate.observed, rate.prior))
        assert low <= rate.shrunk <= high
        assert abs(rate.shrunk - rate.prior) < abs(rate.observed - rate.prior)
        moved += 1
    assert moved > 0


def test_pipeline_decides_shrinkage_from_sample_and_prior_validity(small_sample_match):
    mapping = match_to_double_chance_inputs(small_sample_match)
    applied = needs_early_season_prior(
        mapping.get("Input_Meci!B36"), mapping.get("Input_Meci!C36")
    ) and league_prior_is_valid(small_sample_match)
    assert applied is True
    assert mapping.get("Surse_Date!C10") == "PRIOR / SHRINKAGE"


@pytest.fixture(scope="module")
def fixture_results():
    cases = json.loads((SPEC / "cazuri_test.json").read_text(encoding="utf-8"))["cases"]
    return [(case["id"], compute_double_chance(case["inputs"])) for case in cases]


def test_blend_contributions_reconstruct_p_model(fixture_results):
    checked = 0
    for case_id, result in fixture_results:
        for row in result.payload():
            parts = [
                row["contribution_scoreline"],
                row["contribution_strength"],
                row["contribution_market"],
            ]
            if any(p is None for p in parts) or row["p_model"] is None:
                continue
            assert _close(sum(parts), row["p_model"]), f"{case_id}/{row['selection']}"
            checked += 1
    assert checked > 0


def test_blend_weights_are_50_25_25(fixture_results):
    for case_id, result in fixture_results:
        blend = result.blend
        assert blend.weight_scoreline == 0.50, case_id
        assert blend.weight_strength == 0.25, case_id
        assert blend.weight_market == 0.25, case_id
        assert _close(
            blend.weight_scoreline + blend.weight_strength + blend.weight_market, 1.0
        )


def test_double_chance_probabilities_sum_to_two_for_model_and_market(fixture_results):
    """Fiecare rezultat apare în exact două șanse duble, deci suma este 2.

    Din această identitate rezultă că suma deltelor model-piață pe un meci este
    zero: un bias uniform în jos pe toate cele trei selecții este imposibil.
    """
    checked = 0
    for case_id, result in fixture_results:
        models = [s.p_model for s in result.selections]
        markets = [s.p_market for s in result.selections]
        if any(v is None for v in models) or any(v is None for v in markets):
            continue
        assert _close(sum(models), 2.0), f"{case_id}: model {sum(models)}"
        assert _close(sum(markets), 2.0), f"{case_id}: piață {sum(markets)}"
        assert _close(sum(m - k for m, k in zip(models, markets)), 0.0), case_id
        checked += 1
    assert checked > 0


def test_scoreline_and_strength_are_exposed_separately(fixture_results):
    divergent = 0
    for _, result in fixture_results:
        blend = result.blend
        if blend.scoreline[0] is None or blend.strength[0] is None:
            continue
        if blend.scoreline != blend.strength:
            divergent += 1
    assert divergent > 0, "componentele trebuie expuse distinct, nu ca aceeași valoare"
