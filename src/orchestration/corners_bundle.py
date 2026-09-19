"""Construiește o singură dată mapping-ul și rezultatul Cornere V14 pentru o analiză.

Pattern-ul urmează `double_chance_bundle`: faza ANALYSIS apelează bundle-ul o
dată, iar snapshot-ul rezultat alimentează UI, istoricul și exportul. Diferența
este că V14 evaluează mai multe meciuri în aceeași trecere prin workbook, pentru
că toate partajează `Istoric_Nativ` și clasamentul `Dashboard`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.engines.corners import (
    CornersBatchInput,
    CornersCapacityError,
    CornersEngineError,
    CornersLineResult,
    CornersMatchInput,
    CornersMatchResult,
    compute_corners_batch,
    rank_top_live,
)
from src.engines.corners.engine import TOP_LIVE_LIMIT
from src.models.match_data import MatchData
from src.orchestration.native_history import (
    CornersSourcingPlan,
    SeasonHistory,
    build_match_input,
    canonical_labels,
    collect_season_history,
    plan_batches,
)
from src.orchestration.profiler import FetchCounters


@dataclass
class CornersMatchArtifacts:
    """Materialul pe meci: inputul trasabil, rezultatul oficial și proveniența."""

    match_input: CornersMatchInput
    result: CornersMatchResult | None
    batch_index: int
    provenance: dict[str, Any]
    error: str = ""

    @property
    def lines(self) -> tuple[CornersLineResult, ...]:
        return self.result.lines if self.result is not None else ()

    def payload(self) -> list[dict[str, Any]]:
        return self.result.payload() if self.result is not None else []


@dataclass
class CornersBundle:
    """Rezultatul complet Cornere al unei analize."""

    by_match: dict[str, CornersMatchArtifacts] = field(default_factory=dict)
    batches: tuple[CornersBatchInput, ...] = ()
    seasons: dict[int, SeasonHistory] = field(default_factory=dict)
    top_live: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    rank_live_source: str = "workbook"

    def artifacts_for(self, match_id: str) -> CornersMatchArtifacts | None:
        return self.by_match.get(str(match_id))


def _sourcing_decision(history: SeasonHistory | None) -> tuple[str, str]:
    """Decizia de sursă și dovezile ei, conform stărilor din `Motor_Meciuri!H`."""
    if history is None:
        return "NOT AVAILABLE", "Sezon fără identificator FootyStats pentru istoricul nativ."
    if history.source is None:
        return "NOT AVAILABLE", history.error or "Sursa nu a răspuns."
    if history.source.status == "ACCESS BLOCKED":
        return "ACCESS BLOCKED", history.source.attempts
    if not history.rows:
        return "NOT AVAILABLE", history.source.attempts
    return "AUTO", ""


def _notes_for(history: SeasonHistory | None) -> str:
    if history is None or history.source is None:
        return "Istoric nativ indisponibil."
    source = history.source
    return (
        f"{source.provider} {source.coverage}; rânduri={source.rows}; "
        f"fixture-uri={history.total_fixtures}; fără cornere={source.missing_corners}; "
        f"sha256={source.sha256[:12]}"
    )


def _top_live_from_workbook(
    results: list[CornersMatchResult],
) -> list[CornersLineResult]:
    """Clasamentul LIVE calculat de `Dashboard` în interiorul unui singur lot."""
    ranked: list[tuple[int, CornersLineResult]] = []
    for result in results:
        for item in result.lines:
            if item.live_eligible_best and isinstance(item.rank_live, int):
                ranked.append((item.rank_live, item))
    ranked.sort(key=lambda entry: entry[0])
    return [item for _, item in ranked]


def build_corners_artifacts(
    client: Any,
    matches: list[MatchData],
    counters: FetchCounters | None = None,
    *,
    retrieved_utc: datetime | None = None,
) -> CornersBundle:
    """Colectează istoricul nativ, evaluează V14 și returnează rezultatele oficiale.

    @param client - clientul FootyStats reutilizat de restul analizei.
    @param matches - meciurile care au trecut validarea pentru modelul Cornere.
    @param retrieved_utc - momentul colectării; implicit „acum” (UTC). Este și
        cutoff-ul fiecărui meci, exact ca în definiția V14 a închiderii sursei.
    @returns - bundle cu rezultatele celor 14 linii per meci, clasamentul Top LIVE
        și notele de limitare reale ale sursei.
    """
    bundle = CornersBundle()
    if not matches:
        return bundle

    moment = (retrieved_utc or datetime.now(timezone.utc)).replace(tzinfo=None, microsecond=0)
    labels = canonical_labels(matches)

    seasons: dict[int, SeasonHistory] = {}
    for season_id in sorted(labels):
        league, season = labels[season_id]
        if counters is not None:
            counters.league_matches += 1
        seasons[season_id] = collect_season_history(
            client,
            season_id,
            league=league,
            season=season,
            retrieved_utc=moment,
        )
    bundle.seasons = seasons

    match_inputs: list[CornersMatchInput] = []
    match_seasons: dict[str, int] = {}
    inputs_by_id: dict[str, CornersMatchInput] = {}
    provenance: dict[str, dict[str, Any]] = {}

    for md in matches:
        season_id = int(md.season_id) if md.season_id is not None else None
        history = seasons.get(season_id) if season_id is not None else None
        league, season = labels.get(season_id, ("", "")) if season_id is not None else ("", "")
        decision, evidence = _sourcing_decision(history)
        item = build_match_input(
            md,
            league=league,
            season=season,
            cutoff_utc=moment,
            sourcing_decision=decision,
            evidence_or_attempts=evidence,
            notes=_notes_for(history),
        )
        match_inputs.append(item)
        inputs_by_id[item.match_id] = item
        if season_id is not None:
            match_seasons[item.match_id] = season_id
        provenance[item.match_id] = {
            "season_id": season_id,
            "league": league,
            "season": season,
            "sourcing_decision": decision,
            "provider": history.source.provider if history and history.source else None,
            "coverage": history.source.coverage if history and history.source else None,
            "source_status": history.source.status if history and history.source else None,
            "source_url": history.source.url if history and history.source else None,
            "source_sha256": history.source.sha256 if history and history.source else None,
            "retrieved_utc": moment.isoformat(),
            "cutoff_utc": moment.isoformat(),
            "native_rows_season": len(history.rows) if history else 0,
            "fixtures_returned": history.total_fixtures if history else 0,
            "complete_fixtures": history.complete_fixtures if history else 0,
            "missing_corners": history.missing_corners if history else 0,
            "duplicates_dropped": history.duplicates_dropped if history else 0,
            "page_cap_reached": history.truncated if history else False,
        }
        if history is not None and history.error:
            bundle.errors.append(f"Cornere — istoric nativ {league} {season}: {history.error}")

    batches, notes, partitioned = plan_batches(match_inputs, seasons, match_seasons)
    bundle.batches = batches
    bundle.notes.extend(notes)

    evaluated: list[CornersMatchResult] = []
    for batch_index, batch in enumerate(batches):
        try:
            batch_result = compute_corners_batch(batch)
        except (CornersEngineError, CornersCapacityError) as exc:
            message = getattr(exc, "message", str(exc))
            bundle.errors.append(f"Cornere — evaluare eșuată: {message}")
            for item in batch.matches:
                bundle.by_match[item.match_id] = CornersMatchArtifacts(
                    match_input=item,
                    result=None,
                    batch_index=batch_index,
                    provenance=provenance.get(item.match_id, {}),
                    error=message,
                )
            continue
        if counters is not None:
            counters.compute_corners += 1
        for item in batch.matches:
            result = batch_result.matches.get(item.match_id)
            if result is not None:
                evaluated.append(result)
            details = dict(provenance.get(item.match_id, {}))
            details["native_rows_in_batch"] = len(batch.history)
            details["batch_matches"] = len(batch.matches)
            bundle.by_match[item.match_id] = CornersMatchArtifacts(
                match_input=item,
                result=result,
                batch_index=batch_index,
                provenance=details,
            )

    missing = [item for item in match_inputs if item.match_id not in bundle.by_match]
    for item in missing:
        bundle.by_match[item.match_id] = CornersMatchArtifacts(
            match_input=item,
            result=None,
            batch_index=-1,
            provenance=provenance.get(item.match_id, {}),
            error="Meciul nu a intrat în niciun lot de evaluare (vezi limitele de capacitate).",
        )

    if partitioned or len(batches) > 1:
        ordered = rank_top_live(evaluated)
        bundle.rank_live_source = "python_cross_batch"
    else:
        ordered = _top_live_from_workbook(evaluated)
        bundle.rank_live_source = "workbook"
    bundle.top_live = [
        {
            "rank": position,
            "match_id": _owner_match_id(evaluated, item),
            "match": _owner_label(evaluated, item),
            "line": item.line.label,
            "p_final": item.p_final,
            "risk_level": item.risk_level,
            "verdict": item.verdict,
            "confidence_final": item.confidence_final,
            "reason": item.reason,
        }
        for position, item in enumerate(ordered[:TOP_LIVE_LIMIT], start=1)
    ]
    return bundle


def _owner(results: list[CornersMatchResult], item: CornersLineResult) -> CornersMatchResult | None:
    for result in results:
        if item in result.lines:
            return result
    return None


def _owner_match_id(results: list[CornersMatchResult], item: CornersLineResult) -> str | None:
    owner = _owner(results, item)
    return owner.match_id if owner else None


def _owner_label(results: list[CornersMatchResult], item: CornersLineResult) -> str | None:
    owner = _owner(results, item)
    return owner.match_label if owner else None
