"""Mapping FootyStats → celule Șansă Dublă.

Distribuțiile 1X2 din Model_1X2 B6:D7 sunt DERIVED (Poisson independent
din goluri/xG). Nu sunt Dixon–Coles sau Elo din Excel.
"""

from __future__ import annotations

import math
from datetime import timezone
from typing import Any

from src.excel.generator import unix_to_excel_serial
from src.models.match_data import Indicator, MatchData

_LAMBDA_MIN = 0.2
_LAMBDA_MAX = 4.0
_MAX_GOALS = 12
# Parametri!B17 — pragul Excel existent, nu un prag nou de producție.
_SMALL_SAMPLE_N = 8


def _indicator(owner: object, name: str) -> Indicator:
    value = getattr(owner, name, None)
    if isinstance(value, Indicator):
        return value
    return Indicator()


def _n(indicator: Indicator) -> float | None:
    return indicator.numeric_or_none()


def _per_match(total: Indicator, sample: Indicator) -> float | None:
    goals = total.numeric_or_none()
    played = sample.numeric_or_none()
    if goals is None or played is None or played == 0:
        return None
    return goals / played


def _rate(indicator: Indicator) -> float | None:
    value = indicator.numeric_or_none()
    if value is None:
        return None
    return value / 100.0 if value > 1 else value


def _excel_time(moment) -> float | None:
    if moment is None:
        return None
    if hasattr(moment, "timestamp"):
        dt = moment
        if getattr(dt, "tzinfo", None) is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return unix_to_excel_serial(dt.timestamp())
    return None


def _prematch_times(
    kickoff: float | None, extracted: float | None
) -> tuple[float | None, float | None]:
    """cutoff ≤ verificat ≤ kickoff, ca în L5/L8/L9."""
    if kickoff is None and extracted is None:
        return None, None
    if kickoff is None:
        return extracted, extracted
    verified = extracted if extracted is not None else kickoff
    verified = min(verified, kickoff)
    return verified, verified


def _source_status(verified: bool) -> str:
    return "VERIFIED" if verified else "NOT AVAILABLE"


def _clamp_lambda(value: float) -> float:
    return min(_LAMBDA_MAX, max(_LAMBDA_MIN, value))


def _blend_rate(*rates: float | None) -> float | None:
    usable = [rate for rate in rates if rate is not None and rate >= 0]
    if not usable:
        return None
    return sum(usable) / len(usable)


def _combined_per_match(
    gf_home: Indicator,
    n_home: Indicator,
    gf_away: Indicator,
    n_away: Indicator,
    gf_overall: Indicator,
    n_overall: Indicator,
) -> float | None:
    overall = _per_match(gf_overall, n_overall)
    if overall is not None:
        return overall
    home = gf_home.numeric_or_none()
    away = gf_away.numeric_or_none()
    nh = n_home.numeric_or_none()
    na = n_away.numeric_or_none()
    if home is None or away is None or not nh or not na:
        return None
    return (home + away) / (nh + na)


def _poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def poisson_1x2(lambda_home: float, lambda_away: float) -> tuple[float, float, float]:
    """P(1), P(X), P(2) din Poisson independent, normalizate pe grila 0..12."""
    p_home = p_draw = p_away = 0.0
    for home_goals in range(_MAX_GOALS + 1):
        p_h = _poisson_pmf(home_goals, lambda_home)
        for away_goals in range(_MAX_GOALS + 1):
            mass = p_h * _poisson_pmf(away_goals, lambda_away)
            if home_goals > away_goals:
                p_home += mass
            elif home_goals == away_goals:
                p_draw += mass
            else:
                p_away += mass
    total = p_home + p_draw + p_away
    return p_home / total, p_draw / total, p_away / total


def _lambda_from_sides(attack: float | None, defence: float | None) -> float | None:
    blended = _blend_rate(attack, defence)
    if blended is None:
        return None
    return _clamp_lambda(blended)


def empirical_bayes_rate(
    observed: float | None,
    n_obs: float | None,
    prior: float | None,
    n_prior: float | None,
) -> float | None:
    """Blend controlat (n·obs + n0·prior) / (n + n0) pentru LD-0 SMALL SAMPLE.

    Excel nu calculează shrinkage-ul: rândul 10 doar documentează aplicarea
    externă. Fără prior valid rămâne rata observată; nu se inventează 0.
    """
    prior_ok = prior is not None and n_prior is not None and n_prior > 0 and prior >= 0
    if observed is None:
        return prior if prior_ok else None
    if not prior_ok:
        return observed
    sample = 0.0 if n_obs is None or n_obs < 0 else float(n_obs)
    return (sample * observed + float(n_prior) * prior) / (sample + float(n_prior))


def _prior_n(indicator: Indicator) -> float | None:
    if indicator.n is None or indicator.n <= 0:
        return None
    return float(indicator.n)


def league_prior_rates(
    match: MatchData,
) -> tuple[float | None, float | None, float | None, float | None]:
    """Prior de ligă AJ/AK plus N-ul real din league-teams, nu un 30 de test."""
    home_prior = _n(match.league_avg_gf_home)
    away_prior = _n(match.league_avg_gf_away)
    return (
        home_prior,
        away_prior,
        _prior_n(match.league_avg_gf_home),
        _prior_n(match.league_avg_gf_away),
    )


def league_prior_is_valid(match: MatchData) -> bool:
    home_prior, away_prior, n_home, n_away = league_prior_rates(match)
    return (
        home_prior is not None
        and away_prior is not None
        and n_home is not None
        and n_away is not None
        and home_prior >= 0
        and away_prior >= 0
        and n_home > 0
        and n_away > 0
    )


def needs_early_season_prior(sample_home: float | None, sample_away: float | None) -> bool:
    """Ramura Excel L10: prior obligatoriu doar când min(N H/A) < Parametri!B17."""
    if sample_home is None or sample_away is None:
        return False
    return min(sample_home, sample_away) < _SMALL_SAMPLE_N


def _maybe_shrink(
    observed: float | None,
    n_obs: float | None,
    prior: float | None,
    n_prior: float | None,
    *,
    apply: bool,
) -> float | None:
    if not apply:
        return observed
    return empirical_bayes_rate(observed, n_obs, prior, n_prior)


def derived_1x2_distributions(
    match: MatchData,
    *,
    apply_shrinkage: bool = False,
) -> tuple[tuple[float, float, float] | None, tuple[float, float, float] | None]:
    """Scoreline din H/A+xG, strength din sezon overall. Lipsă = None, nu 0 inventat.

    La SMALL SAMPLE, λ este tras către priorul de ligă (AJ/AK) cu N-ul real
    din league-teams. Confidence cap rămâne haircut-ul Excel (Uncertainty_v2).
    """
    home = match.home
    away = match.away
    home_prior, away_prior, n_prior_home, n_prior_away = league_prior_rates(match)
    n_home = _n(home.matches_played_home)
    n_away = _n(away.matches_played_away)
    n_home_ov = _n(home.matches_played_overall)
    n_away_ov = _n(away.matches_played_overall)
    overall_prior = None
    n_prior_overall = None
    if (
        home_prior is not None
        and away_prior is not None
        and n_prior_home is not None
        and n_prior_away is not None
    ):
        overall_prior = (
            n_prior_home * home_prior + n_prior_away * away_prior
        ) / (n_prior_home + n_prior_away)
        n_prior_overall = n_prior_home + n_prior_away

    home_att_ha = _maybe_shrink(
        _blend_rate(
            _per_match(home.goals_for_home, home.matches_played_home),
            _n(home.xg_for_home),
        ),
        n_home,
        home_prior,
        n_prior_home,
        apply=apply_shrinkage,
    )
    away_def_ha = _maybe_shrink(
        _blend_rate(
            _per_match(away.goals_against_away, away.matches_played_away),
            _n(away.xg_against_away),
        ),
        n_away,
        home_prior,
        n_prior_home,
        apply=apply_shrinkage,
    )
    away_att_ha = _maybe_shrink(
        _blend_rate(
            _per_match(away.goals_for_away, away.matches_played_away),
            _n(away.xg_for_away),
        ),
        n_away,
        away_prior,
        n_prior_away,
        apply=apply_shrinkage,
    )
    home_def_ha = _maybe_shrink(
        _blend_rate(
            _per_match(home.goals_against_home, home.matches_played_home),
            _n(home.xg_against_home),
        ),
        n_home,
        away_prior,
        n_prior_away,
        apply=apply_shrinkage,
    )
    lambda_home_ha = _lambda_from_sides(home_att_ha, away_def_ha)
    lambda_away_ha = _lambda_from_sides(away_att_ha, home_def_ha)
    scoreline = (
        poisson_1x2(lambda_home_ha, lambda_away_ha)
        if lambda_home_ha is not None and lambda_away_ha is not None
        else None
    )

    home_att_ov = _maybe_shrink(
        _blend_rate(
            _combined_per_match(
                home.goals_for_home,
                home.matches_played_home,
                home.goals_for_away,
                home.matches_played_away,
                _indicator(home, "goals_for_overall"),
                home.matches_played_overall,
            ),
            _blend_rate(_n(home.xg_for_home), _n(home.xg_for_away)),
        ),
        n_home_ov if n_home_ov is not None else n_home,
        overall_prior,
        n_prior_overall,
        apply=apply_shrinkage,
    )
    away_def_ov = _maybe_shrink(
        _blend_rate(
            _combined_per_match(
                away.goals_against_home,
                away.matches_played_home,
                away.goals_against_away,
                away.matches_played_away,
                _indicator(away, "goals_against_overall"),
                away.matches_played_overall,
            ),
            _blend_rate(_n(away.xg_against_home), _n(away.xg_against_away)),
        ),
        n_away_ov if n_away_ov is not None else n_away,
        overall_prior,
        n_prior_overall,
        apply=apply_shrinkage,
    )
    away_att_ov = _maybe_shrink(
        _blend_rate(
            _combined_per_match(
                away.goals_for_home,
                away.matches_played_home,
                away.goals_for_away,
                away.matches_played_away,
                _indicator(away, "goals_for_overall"),
                away.matches_played_overall,
            ),
            _blend_rate(_n(away.xg_for_home), _n(away.xg_for_away)),
        ),
        n_away_ov if n_away_ov is not None else n_away,
        overall_prior,
        n_prior_overall,
        apply=apply_shrinkage,
    )
    home_def_ov = _maybe_shrink(
        _blend_rate(
            _combined_per_match(
                home.goals_against_home,
                home.matches_played_home,
                home.goals_against_away,
                home.matches_played_away,
                _indicator(home, "goals_against_overall"),
                home.matches_played_overall,
            ),
            _blend_rate(_n(home.xg_against_home), _n(home.xg_against_away)),
        ),
        n_home_ov if n_home_ov is not None else n_home,
        overall_prior,
        n_prior_overall,
        apply=apply_shrinkage,
    )
    lambda_home_ov = _lambda_from_sides(home_att_ov, away_def_ov)
    lambda_away_ov = _lambda_from_sides(away_att_ov, home_def_ov)
    strength = (
        poisson_1x2(lambda_home_ov, lambda_away_ov)
        if lambda_home_ov is not None and lambda_away_ov is not None
        else None
    )

    if scoreline is None:
        scoreline = strength
    if strength is None:
        strength = scoreline
    return scoreline, strength


def _put_source(
    values: dict[str, Any],
    row: int,
    *,
    status: str,
    source: str,
    verified: float | None,
    cutoff: float | None,
    method: str,
    same_match: bool = True,
    treatment: str | None = None,
) -> None:
    values[f"Surse_Date!C{row}"] = status
    if row != 8:
        values[f"Surse_Date!D{row}"] = source
    values[f"Surse_Date!E{row}"] = verified
    values[f"Surse_Date!F{row}"] = cutoff
    values[f"Surse_Date!I{row}"] = method
    values[f"Surse_Date!J{row}"] = "DA" if same_match else None
    if treatment is not None:
        values[f"Surse_Date!K{row}"] = treatment


def match_to_double_chance_inputs(match: MatchData) -> dict[str, Any]:
    """Mapează FootyStats și, dacă se poate, 1X2 DERIVED din goluri/xG.

    Nu copiază piața în B6:D7. Fără rate de goluri, C6/C7 rămân PENDING
    (nu NOT AVAILABLE), ca PENDING să nu devină nivel 5. La SMALL SAMPLE,
    priorul de ligă este integrat în λ și documentat pe rândul 10; C9 rămâne
    SMALL SAMPLE. Gate-ul L10 nu se slăbește: fără prior valid rămâne PENDING.
    """
    home = match.home
    away = match.away
    kickoff = _excel_time(match.kickoff_utc)
    extracted = _excel_time(getattr(match, "extracted_at", None))
    verified, cutoff = _prematch_times(kickoff, extracted)
    sample_home = _n(home.matches_played_home)
    sample_away = _n(away.matches_played_away)
    o1, ox, o2 = _n(match.odds_ft_1), _n(match.odds_ft_x), _n(match.odds_ft_2)

    p1 = px = p2 = None
    odds_1x = odds_x2 = odds_12 = None
    if o1 and ox and o2 and o1 > 1 and ox > 1 and o2 > 1:
        inv = (1 / o1) + (1 / ox) + (1 / o2)
        p1, px, p2 = (1 / o1) / inv, (1 / ox) / inv, (1 / o2) / inv
        odds_1x = 1 / (p1 + px) if (p1 + px) > 0 else None
        odds_x2 = 1 / (px + p2) if (px + p2) > 0 else None
        odds_12 = 1 / (p1 + p2) if (p1 + p2) > 0 else None

    has_fixture = bool(home.name and away.name and match.competition_name and kickoff is not None)
    has_market = p1 is not None
    sample_ok = sample_home is not None and sample_away is not None
    sample_status = "NOT AVAILABLE"
    if sample_ok:
        sample_status = (
            "SMALL SAMPLE"
            if min(sample_home, sample_away) < _SMALL_SAMPLE_N
            else "VERIFIED"
        )
    apply_shrinkage = needs_early_season_prior(sample_home, sample_away) and league_prior_is_valid(
        match
    )
    scoreline, strength = derived_1x2_distributions(match, apply_shrinkage=apply_shrinkage)

    values: dict[str, Any] = {
        "Input_Meci!B4": home.name or None,
        "Input_Meci!C4": away.name or None,
        "Input_Meci!B5": match.competition_name or None,
        "Input_Meci!B6": kickoff,
        "Input_Meci!B7": "NU",
        "Input_Meci!B12": _per_match(
            _indicator(home, "goals_for_overall"), home.matches_played_overall
        )
        or _combined_per_match(
            home.goals_for_home,
            home.matches_played_home,
            home.goals_for_away,
            home.matches_played_away,
            _indicator(home, "goals_for_overall"),
            home.matches_played_overall,
        ),
        "Input_Meci!C12": _per_match(
            _indicator(away, "goals_for_overall"), away.matches_played_overall
        )
        or _combined_per_match(
            away.goals_for_home,
            away.matches_played_home,
            away.goals_for_away,
            away.matches_played_away,
            _indicator(away, "goals_for_overall"),
            away.matches_played_overall,
        ),
        "Input_Meci!B13": _per_match(
            _indicator(home, "goals_against_overall"), home.matches_played_overall
        )
        or _combined_per_match(
            home.goals_against_home,
            home.matches_played_home,
            home.goals_against_away,
            home.matches_played_away,
            _indicator(home, "goals_against_overall"),
            home.matches_played_overall,
        ),
        "Input_Meci!C13": _per_match(
            _indicator(away, "goals_against_overall"), away.matches_played_overall
        )
        or _combined_per_match(
            away.goals_against_home,
            away.matches_played_home,
            away.goals_against_away,
            away.matches_played_away,
            _indicator(away, "goals_against_overall"),
            away.matches_played_overall,
        ),
        "Input_Meci!B14": _per_match(home.goals_for_home, home.matches_played_home),
        "Input_Meci!C14": _per_match(away.goals_for_away, away.matches_played_away),
        "Input_Meci!B15": _per_match(home.goals_against_home, home.matches_played_home),
        "Input_Meci!C15": _per_match(away.goals_against_away, away.matches_played_away),
        "Input_Meci!B16": _n(home.xg_for_home),
        "Input_Meci!C16": _n(away.xg_for_away),
        "Input_Meci!B17": _n(home.xg_against_home),
        "Input_Meci!C17": _n(away.xg_against_away),
        "Input_Meci!B21": _rate(home.fts_pct_home),
        "Input_Meci!C21": _rate(away.fts_pct_away),
        "Input_Meci!B22": _rate(home.cs_pct_home),
        "Input_Meci!C22": _rate(away.cs_pct_away),
        "Input_Meci!B28": p1,
        "Input_Meci!B29": px,
        "Input_Meci!B30": p2,
        "Input_Meci!B31": odds_1x,
        "Input_Meci!B32": odds_x2,
        "Input_Meci!B33": odds_12,
        "Input_Meci!B34": "B",
        "Input_Meci!B36": sample_home,
        "Input_Meci!C36": sample_away,
        "Input_Meci!B37": "NU",
        "Input_Meci!B38": "NU",
        "Input_Meci!B43": "NU",
        "Input_Meci!C41": 0,
        "Input_Meci!B42": "FootyStats 1X2",
    }
    if scoreline is not None:
        values["Model_1X2!B6"] = scoreline[0]
        values["Model_1X2!C6"] = scoreline[1]
        values["Model_1X2!D6"] = scoreline[2]
    if strength is not None:
        values["Model_1X2!B7"] = strength[0]
        values["Model_1X2!C7"] = strength[1]
        values["Model_1X2!D7"] = strength[2]

    if has_fixture:
        _put_source(
            values,
            5,
            status="VERIFIED",
            source="FootyStats",
            verified=verified,
            cutoff=cutoff,
            method="todays-matches + team stats",
        )
    else:
        values["Surse_Date!C5"] = "NOT AVAILABLE"

    ha_method = "Poisson independent H/A+xG; nu este Dixon-Coles Excel"
    ov_method = "Poisson independent overall; nu este Elo Excel"
    if apply_shrinkage:
        ha_method = "Poisson H/A+xG + shrinkage ligă; nu este Dixon-Coles Excel"
        ov_method = "Poisson overall + shrinkage ligă; nu este Elo Excel"
    if scoreline is not None:
        _put_source(
            values,
            6,
            status="DERIVED",
            source="FootyStats goluri/xG",
            verified=verified,
            cutoff=cutoff,
            method=ha_method,
        )
    if strength is not None:
        _put_source(
            values,
            7,
            status="DERIVED",
            source="FootyStats goluri/xG sezon",
            verified=verified,
            cutoff=cutoff,
            method=ov_method,
        )

    if has_market:
        _put_source(
            values,
            8,
            status="VERIFIED",
            source="FootyStats 1X2",
            verified=verified,
            cutoff=cutoff,
            method="de-vig din cote 1X2 FootyStats",
        )
        # D8 e formulă din B42; nu se scrie.
    else:
        values["Surse_Date!C8"] = "NOT AVAILABLE"

    if sample_ok:
        _put_source(
            values,
            9,
            status=sample_status,
            source="FootyStats",
            verified=verified,
            cutoff=cutoff,
            method="seasonMatchesPlayed home/away",
        )
    else:
        values["Surse_Date!C9"] = "NOT AVAILABLE"

    if apply_shrinkage and scoreline is not None:
        _, _, n_prior_home, n_prior_away = league_prior_rates(match)
        _put_source(
            values,
            10,
            status="PRIOR / SHRINKAGE",
            source="FootyStats league-teams",
            verified=verified,
            cutoff=cutoff,
            method=(
                f"blend (n*obs+n0*liga)/(n+n0); N curent H/A={sample_home:g}/{sample_away:g}; "
                f"N prior H/A={n_prior_home:g}/{n_prior_away:g}; "
                f"N/prior={sample_home / n_prior_home:.3f}/{sample_away / n_prior_away:.3f}"
            ),
            treatment="INTEGRAT IN MODELE",
        )
        values["Surse_Date!G10"] = n_prior_home
        values["Surse_Date!H10"] = n_prior_away

    _put_source(
        values,
        11,
        status="NOT AVAILABLE",
        source="FootyStats nu furnizează absențe/lot",
        verified=verified,
        cutoff=cutoff,
        method="implicit FARA IMPACT MATERIAL",
        treatment="FARA IMPACT MATERIAL",
    )
    return {key: value for key, value in values.items() if value is not None}
