"""Reguli de settlement: recomandare înghețată vs. rezultat oficial.

Acest modul NU conține model. Nu recalculează Pfail, gates, Risk Score,
probabilități 1X2 sau distribuția Cornere V14 — acelea rămân în Excel. Aici se
compară doar piața înghețată a unei predicții cu scorul/statistica oficială
FootyStats și se decide HIT / MISS / date insuficiente.

Consecință directă: lipsa datelor nu este niciodată MISS. Un `NULL` la scor sau
la cornere înseamnă NOT AVAILABLE, nu 0-0 și nu 0 cornere.

Outcome-ul răspunde la întrebarea „a intrat piața înghețată?”, nu la „am pariat?”.
Se calculează și pentru selecțiile cu verdict WATCH / NO BET, fiindcă altfel nu s-ar
putea măsura dacă gate-urile resping corect. Filtrarea pe `recommendation` sau
`risk_level` rămâne treaba stratului de backtest.
"""

from __future__ import annotations

from src.history.models import (
    CORNERS_MARKETS,
    Market,
    MatchResult,
    Outcome,
    SettlementDecision,
    SettlementStatus,
)

_PENDING_NO_RESULT = SettlementDecision(
    settlement_status=SettlementStatus.PENDING_RESULT.value,
    outcome=None,
    settlement_reason="Rezultatul oficial nu este încă disponibil la FootyStats.",
)


def _unavailable(reason: str) -> SettlementDecision:
    return SettlementDecision(
        settlement_status=SettlementStatus.RESULT_DATA_UNAVAILABLE.value,
        outcome=None,
        settlement_reason=reason,
    )


def _settled(outcome: Outcome, reason: str) -> SettlementDecision:
    return SettlementDecision(
        settlement_status=SettlementStatus.SETTLED.value,
        outcome=outcome.value,
        settlement_reason=reason,
    )


def _settle_over_05(result: MatchResult) -> SettlementDecision:
    """Over 0.5: cel puțin un gol în meci.

    `total_goals >= 1` → HIT, `== 0` → MISS. Scorul absent nu devine 0-0.
    """
    total = int(result.home_goals or 0) + int(result.away_goals or 0)
    if total >= 1:
        return _settled(Outcome.HIT, f"Scor final {result.home_goals}-{result.away_goals}: {total} goluri.")
    return _settled(Outcome.MISS, "Scor final 0-0: Over 0.5 pierdut.")


def _settle_double_chance(market: str, result: MatchResult) -> SettlementDecision:
    """Șansă Dublă: doar comparație de scor, fără recalcularea probabilităților."""
    home = int(result.home_goals or 0)
    away = int(result.away_goals or 0)
    score = f"{home}-{away}"
    if market == Market.DC_1X.value:
        won = home >= away
    elif market == Market.DC_X2.value:
        won = away >= home
    elif market == Market.DC_12.value:
        won = home != away
    else:  # pragma: no cover - apelul este filtrat de `settle_prediction`
        return _unavailable(f"Piață Șansă Dublă necunoscută: {market}.")
    if won:
        return _settled(Outcome.HIT, f"Scor final {score}: {market} câștigat.")
    return _settled(Outcome.MISS, f"Scor final {score}: {market} pierdut.")


def _settle_corners(market: str, line: float | None, result: MatchResult) -> SettlementDecision:
    """Cornere Multi-Line: o decizie per linie salvată.

    Totalul se calculează doar când ambele valori oficiale există. Distribuția și
    probabilitățile V14 nu sunt atinse; se verifică doar linia înghețată.
    """
    if line is None:
        return _unavailable("Linia Cornere lipsește din predicție; settlement imposibil.")
    total = int(result.home_corners or 0) + int(result.away_corners or 0)
    detail = f"Cornere oficiale {result.home_corners}+{result.away_corners} = {total}"
    if market == Market.CORNERS_OVER.value:
        won = total > float(line)
        label = f"Over {line}"
    else:
        won = total < float(line)
        label = f"Under {line}"
    if won:
        return _settled(Outcome.HIT, f"{detail}: {label} câștigat.")
    return _settled(Outcome.MISS, f"{detail}: {label} pierdut.")


def settle_prediction(
    *,
    market: str,
    line: float | None,
    result: MatchResult | None,
) -> SettlementDecision:
    """Decide settlement-ul unei predicții pe baza rezultatului oficial.

    @param market - piața înghețată (`Market`), nu textul recomandării.
    @param line - linia numerică pentru piețele cu linie, `None` altfel.
    @param result - rezultatul FootyStats sau `None` dacă nu a fost încă preluat.
    @returns {SettlementDecision} - status + outcome + motivul deciziei.
    """
    if result is None:
        return _PENDING_NO_RESULT
    if result.is_abandoned:
        return _unavailable(
            f"Meci {result.match_status}: nu există rezultat oficial pentru settlement."
        )
    if not result.is_complete:
        return SettlementDecision(
            settlement_status=SettlementStatus.PENDING_RESULT.value,
            outcome=None,
            settlement_reason=f"Status FootyStats '{result.match_status}': meciul nu este încheiat.",
        )

    if market in CORNERS_MARKETS:
        if not result.has_final_corners:
            return _unavailable(
                "Cornerele oficiale lipsesc (NOT AVAILABLE); nu le tratăm ca 0."
            )
        return _settle_corners(market, line, result)

    if not result.has_final_score:
        return _unavailable("Scorul final lipsește (NOT AVAILABLE); nu îl tratăm ca 0-0.")

    if market == Market.OVER_0_5.value:
        return _settle_over_05(result)
    if market in {Market.DC_1X.value, Market.DC_X2.value, Market.DC_12.value}:
        return _settle_double_chance(market, result)

    return _unavailable(f"Nu există regulă de settlement pentru piața {market}.")
