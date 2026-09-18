"""Mapping inputuri Over 0.5: celule Excel ↔ MatchData, fără date inventate."""

from __future__ import annotations

from typing import Any

from src.models.match_data import Indicator, MatchData


def _indicator(owner: object, name: str) -> Indicator:
    """Citește un Indicator; lipsă (model Streamlit vechi) = gol, nu crash."""
    value = getattr(owner, name, None)
    if isinstance(value, Indicator):
        return value
    return Indicator()

ANALYSIS_SHEET = "Analize meciuri"

# Poziții de input din schema V4. FB e retras; rămâne listat ca să poată fi golit.
INPUT_COLUMNS: tuple[str, ...] = (
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "AA",
    "AB",
    "AC",
    "AD",
    "AE",
    "AF",
    "AG",
    "AH",
    "AI",
    "AJ",
    "AK",
    "AL",
    "AM",
    "AN",
    "AO",
    "AP",
    "AQ",
    "AR",
    "AS",
    "AT",
    "AU",
    "AV",
    "AW",
    "AX",
    "AY",
    "AZ",
    "BA",
    "BB",
    "BC",
    "BD",
    "BE",
    "BF",
    "BG",
    "BH",
    "BI",
    "CJ",
    "CK",
    "CL",
    "CM",
    "CN",
    "CO",
    "CP",
    "CQ",
    "CR",
    "CS",
    "CT",
    "CU",
    "CV",
    "CW",
    "CX",
    "CY",
    "CZ",
    "DA",
    "DB",
    "DC",
    "DD",
    "DE",
    "DF",
    "DG",
    "DH",
    "DI",
    "DJ",
    "DK",
    "DL",
    "DM",
    "DN",
    "DO",
    "DP",
    "DQ",
    "DR",
    "DS",
    "DT",
    "DU",
    "DV",
    "EV",
    "EW",
    "EX",
    "EY",
    "EZ",
    "FA",
    "FB",
    "FY",
    "FZ",
    "GA",
    "GB",
)


def excel_rate(ind: Indicator) -> float | None:
    """Convertește un procent FootyStats (0–100 sau 0–1) în fracție Excel."""
    value = ind.numeric_or_none()
    if value is None:
        return None
    if value > 1:
        return value / 100.0
    return value


def complement_rate(ind: Indicator) -> float | None:
    """Complementul unei rate: Over 0.5 → Under 0.5 / 0-0. Nu inventează dacă sursa lipsește."""
    rate = excel_rate(ind)
    if rate is None:
        return None
    return max(0.0, min(1.0, 1.0 - rate))


def under_rate(direct: Indicator, over_pct: Indicator) -> float | None:
    """Rata 0-0 = Under 0.5, altfel complementul Over 0.5 (identitate, nu proxy FTS×CS)."""
    value = excel_rate(direct)
    if value is not None:
        return value
    return complement_rate(over_pct)


def per_match_average(total: Indicator, sample: Indicator) -> float | None:
    """Transformă un total de sezon în medie pe meci; nu inventează dacă N lipsește."""
    raw_total = total.numeric_or_none()
    n = sample.numeric_or_none()
    if raw_total is None or n is None or n <= 0:
        return None
    return raw_total / n


def blank_inputs() -> dict[str, Any]:
    """Toate inputurile V4, goale. Previne scurgerea valorilor DEMO din șablon."""
    return {col: None for col in INPUT_COLUMNS}


def match_to_over05_inputs(match: MatchData) -> dict[str, Any]:
    """Mapează doar câmpurile FootyStats verificate; restul rămân goale.

    Conversii de unitate (nu sunt date noi): procent 0–100 → fracție; goluri
    sezon/last5 ca totaluri → medie pe meci. xG din API este deja medie.
    0-0 FT = Under 0.5 = complement Over 0.5; 0-0 HT = complement Over 0.5 HT.
    """
    values = blank_inputs()
    home = match.home
    away = match.away

    values["A"] = match.match_id
    values["B"] = "LIVE"
    values["C"] = match.kickoff_utc
    values["D"] = match.competition_name or None
    values["E"] = "Campionat intern"
    values["F"] = match.round or None
    values["G"] = home.name or None
    values["H"] = away.name or None

    values["I"] = home.matches_played_home.numeric_or_none()
    values["J"] = per_match_average(home.goals_for_home, home.matches_played_home)
    values["K"] = per_match_average(home.goals_against_home, home.matches_played_home)
    values["L"] = home.xg_for_home.numeric_or_none()
    values["M"] = home.xg_against_home.numeric_or_none()
    values["N"] = excel_rate(home.over05_pct_home)
    values["O"] = excel_rate(home.fts_pct_home)

    values["P"] = away.matches_played_away.numeric_or_none()
    values["Q"] = per_match_average(away.goals_for_away, away.matches_played_away)
    values["R"] = per_match_average(away.goals_against_away, away.matches_played_away)
    values["S"] = away.xg_for_away.numeric_or_none()
    values["T"] = away.xg_against_away.numeric_or_none()
    values["U"] = excel_rate(away.over05_pct_away)
    values["V"] = excel_rate(away.fts_pct_away)

    values["W"] = home.last5_n.numeric_or_none()
    values["X"] = per_match_average(home.last5_gf, home.last5_n)
    values["Y"] = per_match_average(home.last5_ga, home.last5_n)
    values["Z"] = home.last5_xgf.numeric_or_none()
    values["AA"] = home.last5_xga.numeric_or_none()

    values["AB"] = away.last5_n.numeric_or_none()
    values["AC"] = per_match_average(away.last5_gf, away.last5_n)
    values["AD"] = per_match_average(away.last5_ga, away.last5_n)
    values["AE"] = away.last5_xgf.numeric_or_none()
    values["AF"] = away.last5_xga.numeric_or_none()

    values["AG"] = match.h2h_n.numeric_or_none()
    values["AJ"] = _indicator(match, "league_avg_gf_home").numeric_or_none()
    values["AK"] = _indicator(match, "league_avg_gf_away").numeric_or_none()
    values["AL"] = _indicator(match, "league_avg_gf_total").numeric_or_none()
    values["AO"] = match.odds_ft_1.numeric_or_none()
    values["AP"] = match.odds_ft_x.numeric_or_none()
    values["AQ"] = match.odds_ft_2.numeric_or_none()
    values["AR"] = match.odds_ft_over05.numeric_or_none()
    values["AS"] = match.odds_ft_under05.numeric_or_none()
    values["AT"] = 3
    values["BI"] = "https://footystats.org/"
    values["DE"] = "Pre-match"

    values["EV"] = under_rate(_indicator(home, "under05_pct_home"), home.over05_pct_home)
    values["EW"] = under_rate(_indicator(away, "under05_pct_away"), away.over05_pct_away)
    values["EX"] = excel_rate(home.cs_pct_home)
    values["EY"] = excel_rate(away.cs_pct_away)
    values["EZ"] = complement_rate(_indicator(home, "over05_ht_pct_home"))
    values["FA"] = complement_rate(_indicator(away, "over05_ht_pct_away"))
    values["FY"] = excel_rate(_indicator(home, "last5_fts"))
    values["FZ"] = excel_rate(_indicator(away, "last5_fts"))
    values["GA"] = _indicator(home, "last5_under05_n").numeric_or_none()
    values["GB"] = _indicator(away, "last5_under05_n").numeric_or_none()

    return values
