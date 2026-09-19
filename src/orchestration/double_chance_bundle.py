"""Bundle Șansă Dublă: mapping + motor + audit prior/shrinkage o singură dată."""

from __future__ import annotations

from typing import Any

from src.engines.double_chance.engine import DoubleChanceOfficialResult, compute_double_chance
from src.engines.double_chance.inputs import (
    Upstream1X2Trace,
    derived_1x2_trace,
    league_prior_is_valid,
    match_to_double_chance_inputs,
    needs_early_season_prior,
)
from src.models.match_data import MatchData
from src.orchestration.profiler import FetchCounters
from src.orchestration.snapshot import DoubleChanceMatchArtifacts


def prior_weights_from_trace(trace: Upstream1X2Trace, applied: bool) -> dict[str, Any]:
    """Extrage coloanele de audit V2 din urma deja calculată."""
    rate = trace.rate("scoreline.home_attack")
    return {
        "dc_shrinkage_applied": "DA" if applied else "NU",
        "dc_weight_current": rate.weight_current if rate else None,
        "dc_weight_prior": rate.weight_prior if rate else None,
        "dc_rate_before_shrinkage": rate.observed if rate else None,
        "dc_rate_after_shrinkage": rate.shrunk if rate else None,
        "dc_lambda_home_before": trace.lambda_scoreline_raw[0],
        "dc_lambda_home_after": trace.lambda_scoreline[0],
        "dc_lambda_away_before": trace.lambda_scoreline_raw[1],
        "dc_lambda_away_after": trace.lambda_scoreline[1],
    }


def build_double_chance_artifacts(
    match: MatchData,
    counters: FetchCounters | None = None,
) -> DoubleChanceMatchArtifacts:
    """Un singur derived_1x2_trace + mapping + compute_double_chance per meci."""
    sample_home = match.home.matches_played_home.numeric_or_none()
    sample_away = match.away.matches_played_away.numeric_or_none()
    applied = needs_early_season_prior(sample_home, sample_away) and league_prior_is_valid(match)
    if counters is not None:
        counters.derived_1x2_trace += 1
    trace = derived_1x2_trace(match, apply_shrinkage=applied)
    mapping = match_to_double_chance_inputs(match, _upstream_trace=trace)
    if counters is not None:
        counters.compute_double_chance += 1
    official = compute_double_chance(mapping)
    prior_weights = prior_weights_from_trace(trace, applied)
    return DoubleChanceMatchArtifacts(
        mapping=mapping,
        official=official,
        prior_weights=prior_weights,
    )
