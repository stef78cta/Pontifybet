"""Tipuri pentru istoricul pre-match și settlement-ul post-match.

Separarea de `src/models/match_data.py` este intenționată: acolo stau datele de
intrare FootyStats, aici stau **faptele înregistrate** (ce am recomandat, ce s-a
întâmplat). Un forecast înghețat și un rezultat oficial nu au același ciclu de
viață și nu trebuie să locuiască în aceeași structură.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SnapshotStatus(str, Enum):
    """Stările jurnalului pre-match.

    `PENDING_EXCEL_RECALC` există pentru modelele al căror verdict final NU este
    disponibil în runtime-ul Python (Cornere V14): Pontifybet scrie doar inputuri
    în copia șablonului, iar Microsoft Excel calculează verdictul la deschidere.
    Nu reimplementăm formulele; înregistrăm identitatea predicției și așteptăm
    ingestia workbook-ului recalculat.
    """

    PENDING_EXCEL_RECALC = "PENDING_EXCEL_RECALC"
    FROZEN_PREMATCH = "FROZEN_PREMATCH"


class SettlementStatus(str, Enum):
    """Stările settlement-ului post-match."""

    PENDING_RESULT = "PENDING_RESULT"
    SETTLED = "SETTLED"
    RESULT_DATA_UNAVAILABLE = "RESULT_DATA_UNAVAILABLE"


class Outcome(str, Enum):
    """Rezultatul unei predicții raportat la piața înghețată."""

    HIT = "HIT"
    MISS = "MISS"


class Market(str, Enum):
    """Piețele acoperite în această etapă.

    Valorile sunt stabile pentru că intră în cheia de deduplicare a predicțiilor;
    redenumirea lor ar rupe istoricul existent.
    """

    OVER_0_5 = "OVER_0_5"
    DC_1X = "1X"
    DC_X2 = "X2"
    DC_12 = "12"
    CORNERS_OVER = "CORNERS_OVER"
    CORNERS_UNDER = "CORNERS_UNDER"


DOUBLE_CHANCE_MARKETS = {Market.DC_1X.value, Market.DC_X2.value, Market.DC_12.value}
CORNERS_MARKETS = {Market.CORNERS_OVER.value, Market.CORNERS_UNDER.value}

# Status FootyStats (`/match` → `status`): 'complete', 'suspended', 'canceled',
# 'incomplete'. Doar 'complete' autorizează un settlement.
FOOTYSTATS_STATUS_COMPLETE = "complete"
FOOTYSTATS_STATUS_INCOMPLETE = "incomplete"
FOOTYSTATS_ABANDONED_STATUSES = {"suspended", "canceled", "cancelled"}


def line_key(line: float | None) -> str:
    """Reprezentarea textuală a liniei folosită în indexul UNIQUE.

    SQLite tratează fiecare NULL ca distinct într-un index UNIQUE, deci o piață
    fără linie (ex. Șansă Dublă) ar putea fi inserată de mai multe ori. Cheia
    devine string: `''` pentru „fără linie”, altfel valoarea normalizată.
    """
    if line is None:
        return ""
    return f"{float(line):g}"


@dataclass(frozen=True)
class PredictionKey:
    """Identitatea imuabilă a unei predicții pre-match."""

    provider_match_id: str
    model_key: str
    model_version: str
    market: str
    line: float | None

    @property
    def line_key(self) -> str:
        return line_key(self.line)


@dataclass
class PredictionSnapshot:
    """Un forecast pre-match: meci × model × piață/linie.

    Câmpurile provin exclusiv din modelele Excel (evaluate sau ingerate); niciunul
    nu este recalculat în Python. Valorile absente rămân `None` — `-1`, `-2` și
    `null` FootyStats înseamnă NOT AVAILABLE, nu zero.
    """

    provider_match_id: str
    model_key: str
    model_version: str
    market: str
    line: float | None = None
    kickoff_utc: str | None = None
    kickoff_unix: int | None = None
    league: str | None = None
    home_team: str | None = None
    away_team: str | None = None
    recommendation: str | None = None
    p_adjusted: float | None = None
    failure_mode: float | None = None
    risk_score: float | None = None
    risk_level: float | None = None
    confidence: float | None = None
    confidence_label: str | None = None
    data_status: str | None = None
    hard_gate: str | None = None
    motivation: str | None = None
    snapshot_status: str = SnapshotStatus.PENDING_EXCEL_RECALC.value

    @property
    def key(self) -> PredictionKey:
        return PredictionKey(
            provider_match_id=self.provider_match_id,
            model_key=self.model_key,
            model_version=self.model_version,
            market=self.market,
            line=self.line,
        )


@dataclass
class MatchResult:
    """Rezultatul oficial FootyStats al unui meci.

    Un singur rând pe meci: toate liniile Cornere ale aceluiași meci reutilizează
    acest rezultat, deci nu interogăm API-ul o dată pe linie.
    """

    provider_match_id: str
    match_status: str | None = None
    home_goals: int | None = None
    away_goals: int | None = None
    total_goals: int | None = None
    home_corners: int | None = None
    away_corners: int | None = None
    total_corners: int | None = None
    source_endpoint: str = "match"

    @property
    def has_final_score(self) -> bool:
        return self.home_goals is not None and self.away_goals is not None

    @property
    def has_final_corners(self) -> bool:
        return self.home_corners is not None and self.away_corners is not None

    @property
    def is_complete(self) -> bool:
        return str(self.match_status or "").lower() == FOOTYSTATS_STATUS_COMPLETE

    @property
    def is_abandoned(self) -> bool:
        return str(self.match_status or "").lower() in FOOTYSTATS_ABANDONED_STATUSES


@dataclass
class SettlementDecision:
    """Verdictul settlement-ului, fără nicio recalculare de model."""

    settlement_status: str
    outcome: str | None
    settlement_reason: str


@dataclass
class UpdateResultsSummary:
    """Raport pentru UI după „Actualizează rezultate”."""

    pending_predictions: int = 0
    matches_queried: int = 0
    results_updated: int = 0
    hit: int = 0
    miss: int = 0
    result_data_unavailable: int = 0
    still_pending: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pending_predictions": self.pending_predictions,
            "matches_queried": self.matches_queried,
            "results_updated": self.results_updated,
            "hit": self.hit,
            "miss": self.miss,
            "result_data_unavailable": self.result_data_unavailable,
            "still_pending": self.still_pending,
            "errors": list(self.errors),
        }
