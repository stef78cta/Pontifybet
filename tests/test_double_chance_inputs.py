"""Mapping Șansă Dublă LIVE: cronologie Surse_Date + 1X2 DERIVED, fără CRITICAL MISSING fals."""

from src.api.mock import MockFootyStatsClient
from src.engines.double_chance import compute_double_chance, match_to_double_chance_inputs
from src.engines.double_chance.inputs import empirical_bayes_rate
from src.models.match_data import DataStatus, Indicator


def _mock_match():
    client = MockFootyStatsClient()
    return client.enrich_match(client.matches_by_date("2026-03-15")[0])


def _wipe_attack_stats(match):
    names = (
        "goals_for_home",
        "goals_against_home",
        "goals_for_away",
        "goals_against_away",
        "goals_for_overall",
        "goals_against_overall",
        "xg_for_home",
        "xg_against_home",
        "xg_for_away",
        "xg_against_away",
    )
    for side in (match.home, match.away):
        for name in names:
            current = getattr(side, name, None)
            if isinstance(current, Indicator):
                current.value = None
                current.data_status = DataStatus.NOT_AVAILABLE


def test_source_timestamps_are_not_after_kickoff():
    values = match_to_double_chance_inputs(_mock_match())
    kickoff = values["Input_Meci!B6"]
    for prefix in ("E", "F"):
        for row in (5, 6, 7, 8, 9, 10, 11):
            cell = f"Surse_Date!{prefix}{row}"
            if cell not in values:
                continue
            assert values[cell] <= kickoff, cell
    for row in (5, 6, 7, 8, 9, 10, 11):
        e, f = f"Surse_Date!E{row}", f"Surse_Date!F{row}"
        if e in values and f in values:
            assert values[f] <= values[e], row


def test_live_mapping_does_not_write_formula_cells():
    values = match_to_double_chance_inputs(_mock_match())
    forbidden = {
        "Surse_Date!D8",
        "Surse_Date!G9",
        "Surse_Date!H9",
        "Model_1X2!B8",
        "Model_1X2!C8",
        "Model_1X2!D8",
    }
    assert forbidden.isdisjoint(values)


def test_unavailable_odds_are_not_written_as_zero():
    match = _mock_match()
    match.odds_ft_1.value = -1
    match.odds_ft_1.data_status = DataStatus.NOT_AVAILABLE
    match.odds_ft_x.value = -2
    match.odds_ft_x.data_status = DataStatus.NOT_AVAILABLE
    match.odds_ft_2.value = None
    match.odds_ft_2.data_status = DataStatus.NOT_AVAILABLE
    values = match_to_double_chance_inputs(match)
    for cell in (
        "Input_Meci!B28",
        "Input_Meci!B29",
        "Input_Meci!B30",
        "Input_Meci!B31",
        "Input_Meci!B32",
        "Input_Meci!B33",
    ):
        assert cell not in values or values[cell] not in (0, 0.0, -1, -2)
    assert values["Surse_Date!C8"] == "NOT AVAILABLE"


def test_live_derived_1x2_is_not_market_copy_and_not_critical_missing():
    values = match_to_double_chance_inputs(_mock_match())
    for cell in (
        "Model_1X2!B6",
        "Model_1X2!C6",
        "Model_1X2!D6",
        "Model_1X2!B7",
        "Model_1X2!C7",
        "Model_1X2!D7",
    ):
        assert cell in values
        assert 0 <= values[cell] <= 1
    assert abs(sum(values[f"Model_1X2!{c}6"] for c in "BCD") - 1) < 1e-9
    assert abs(sum(values[f"Model_1X2!{c}7"] for c in "BCD") - 1) < 1e-9
    assert values["Surse_Date!C6"] == "DERIVED"
    assert values["Surse_Date!C7"] == "DERIVED"
    assert values["Surse_Date!C6"] != "NOT AVAILABLE"
    market = (values["Input_Meci!B28"], values["Input_Meci!B29"], values["Input_Meci!B30"])
    scoreline = (values["Model_1X2!B6"], values["Model_1X2!C6"], values["Model_1X2!D6"])
    assert scoreline != market

    result = compute_double_chance(
        values,
        evaluate=(
            "Surse_Date!L5",
            "Surse_Date!L6",
            "Surse_Date!L8",
            "Surse_Date!L9",
            "Surse_Date!L15",
            "Model_1X2!F12",
            "Model_1X2!F14",
            "Double_Chance!AD4",
            "Double_Chance!F4",
            "Double_Chance!N4",
        ),
    )
    assert result.cells["Surse_Date!L15"] != "CRITICAL MISSING"
    assert result.cells["Model_1X2!F14"] == "READY"
    assert result.cells["Double_Chance!AD4"] == "READY"
    assert result.by_code("1X").p_adj is not None
    assert result.by_code("1X").verdict not in {None, "VERIFICARE NECESARĂ – NO RANK"}
    assert result.by_code("1X").release != "CRITICAL MISSING"


def _set_ha_sample(match, home_n: float, away_n: float) -> None:
    match.home.matches_played_home.value = home_n
    match.home.matches_played_home.data_status = DataStatus.SMALL_SAMPLE
    match.away.matches_played_away.value = away_n
    match.away.matches_played_away.data_status = DataStatus.SMALL_SAMPLE


def _wipe_league_prior(match) -> None:
    for name in ("league_avg_gf_home", "league_avg_gf_away", "league_avg_gf_total"):
        current = getattr(match, name)
        current.value = None
        current.n = None
        current.data_status = DataStatus.NOT_AVAILABLE


def _small_sample_cells():
    return (
        "Surse_Date!L9",
        "Surse_Date!L10",
        "Surse_Date!L15",
        "Model_1X2!F14",
        "Double_Chance!AD4",
        "Double_Chance!N4",
    )


def test_empirical_bayes_rate_blends_current_n_with_league_prior():
    assert empirical_bayes_rate(3.0, 2, 1.0, 8) == (2 * 3.0 + 8 * 1.0) / 10
    assert empirical_bayes_rate(None, 0, 1.4, 40) == 1.4
    assert empirical_bayes_rate(2.2, 6, None, None) == 2.2


def test_small_sample_without_league_prior_stays_pending():
    match = _mock_match()
    _set_ha_sample(match, 6, 5)
    _wipe_league_prior(match)
    values = match_to_double_chance_inputs(match)
    assert values["Surse_Date!C9"] == "SMALL SAMPLE"
    assert values["Input_Meci!B36"] == 6
    assert values["Input_Meci!C36"] == 5
    assert values.get("Surse_Date!K10") != "INTEGRAT IN MODELE"
    assert "Surse_Date!G10" not in values
    result = compute_double_chance(values, evaluate=_small_sample_cells())
    assert result.cells["Surse_Date!L9"] == "READY"
    assert result.cells["Surse_Date!L10"] == "PENDING"
    assert result.cells["Model_1X2!F14"] == "PENDING"
    assert result.by_code("1X").verdict == "VERIFICARE NECESARĂ – NO RANK"


def test_small_sample_with_league_prior_integrates_shrinkage_and_stays_visible():
    match = _mock_match()
    _set_ha_sample(match, 6, 5)
    assert match.league_avg_gf_home.n and match.league_avg_gf_home.n > 0
    assert match.league_avg_gf_away.n and match.league_avg_gf_away.n > 0
    values = match_to_double_chance_inputs(match)
    assert values["Surse_Date!C9"] == "SMALL SAMPLE"
    assert values["Surse_Date!C10"] == "PRIOR / SHRINKAGE"
    assert values["Surse_Date!K10"] == "INTEGRAT IN MODELE"
    assert values["Surse_Date!G10"] == match.league_avg_gf_home.n
    assert values["Surse_Date!H10"] == match.league_avg_gf_away.n
    assert values["Surse_Date!G10"] != 30
    assert values["Surse_Date!H10"] != 30
    assert "6/5" in values["Surse_Date!I10"]
    assert str(match.league_avg_gf_home.n) in values["Surse_Date!I10"]
    assert values["Input_Meci!B36"] == 6
    assert values["Input_Meci!C36"] == 5
    assert values["Input_Meci!B36"] != values.get("Input_Meci!B12")
    result = compute_double_chance(values, evaluate=_small_sample_cells())
    assert result.cells["Surse_Date!L9"] == "READY"
    assert result.cells["Surse_Date!L10"] == "READY"
    assert result.cells["Model_1X2!F14"] == "READY"
    assert result.cells["Double_Chance!AD4"] == "READY"
    assert result.by_code("1X").verdict not in {None, "VERIFICARE NECESARĂ – NO RANK"}


def test_shrinkage_moves_derived_1x2_toward_league_prior():
    match = _mock_match()
    _set_ha_sample(match, 6, 5)
    shrunk = match_to_double_chance_inputs(match)
    _wipe_league_prior(match)
    raw = match_to_double_chance_inputs(match)
    assert shrunk["Model_1X2!B6"] != raw["Model_1X2!B6"]
    assert shrunk["Surse_Date!K10"] == "INTEGRAT IN MODELE"
    assert raw.get("Surse_Date!K10") != "INTEGRAT IN MODELE"


def test_adequate_sample_does_not_write_prior_row():
    values = match_to_double_chance_inputs(_mock_match())
    assert values["Input_Meci!B36"] >= 8
    assert values["Input_Meci!C36"] >= 8
    assert values["Surse_Date!C9"] == "VERIFIED"
    assert "Surse_Date!C10" not in values
    assert "Surse_Date!G10" not in values
    assert "Surse_Date!K10" not in values


def test_missing_stats_is_pending_not_critical_missing():
    match = _mock_match()
    _wipe_attack_stats(match)
    values = match_to_double_chance_inputs(match)
    for cell in (
        "Model_1X2!B6",
        "Model_1X2!C6",
        "Model_1X2!D6",
        "Model_1X2!B7",
        "Model_1X2!C7",
        "Model_1X2!D7",
    ):
        assert cell not in values
    assert values.get("Surse_Date!C6") != "NOT AVAILABLE"
    assert values.get("Surse_Date!C7") != "NOT AVAILABLE"
    result = compute_double_chance(values)
    assert result.by_code("1X").release != "CRITICAL MISSING"
    assert result.by_code("1X").verdict == "VERIFICARE NECESARĂ – NO RANK"
    assert result.by_code("1X").p_adj is None
