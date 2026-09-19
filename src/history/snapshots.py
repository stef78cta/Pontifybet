"""Construirea jurnalului pre-match din rezultatul fazei ANALYSIS.

Toate cele trei modele au verdictul disponibil în runtime-ul Python, pentru că
`src/engines/*` *evaluează formulele din workbook* (nu le reimplementează):
Over 0.5 V4, Șansă Dublă V2 și Cornere Multi-Line V14. Snapshot-urile lor se nasc
direct `FROZEN_PREMATCH`.

`PENDING_EXCEL_RECALC` rămâne doar ca stare istorică: înregistrările Cornere
salvate înainte de motorul V14 se completează în continuare prin
`excel_ingest.py`. Analizele noi nu mai creează pending-uri.
"""

from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from typing import Any

from openpyxl import load_workbook

from config.settings import TEMPLATES_DIR
from src.adapters.base import load_registry
from src.history import repository as repo
from src.history.db import open_db
from src.history.models import (
    Market,
    PredictionSnapshot,
    SnapshotStatus,
)

CORNERS_RESULT_SHEET = "Analiza_Linii"
# Blocul de linii al primului slot din `Analiza_Linii`; F/G/H sunt literali în
# șablon (Line / Type / k), deci cele 14 linii se citesc, nu se inventează.
CORNERS_FIRST_SLOT_ROWS = range(6, 20)
CORNERS_ROWS_PER_SLOT = len(CORNERS_FIRST_SLOT_ROWS)


@lru_cache(maxsize=1)
def model_versions() -> dict[str, str]:
    """Versiunea fiecărui model, derivată din numele șablonului din registry.

    Nu hardcodăm „V4/V2/V14”: dacă șablonul pilot este înlocuit cu o versiune
    nouă, istoricul vechi rămâne distinct pentru că versiunea intră în cheia de
    deduplicare a predicțiilor.
    """
    registry = load_registry()
    fallback = str(registry.get("version") or "unknown")
    out: dict[str, str] = {}
    for model_id, cfg in (registry.get("models") or {}).items():
        match = re.search(r"_V(\d+[A-Za-z]?)", str(cfg.get("template") or ""))
        out[str(model_id)] = f"V{match.group(1)}" if match else fallback
    return out


def model_version(model_key: str) -> str:
    return model_versions().get(model_key, "unknown")


@lru_cache(maxsize=1)
def corners_lines() -> tuple[tuple[str, float], ...]:
    """Cele 14 linii Cornere, citite din șablonul V14.

    @returns - tupluri `(market, line)`, unde `line = k + 0.5` conform coloanei H.
    """
    path = TEMPLATES_DIR / load_registry()["models"]["corners"]["template"]
    wb = load_workbook(path, data_only=False, read_only=True)
    try:
        ws = wb[CORNERS_RESULT_SHEET]
        out: list[tuple[str, float]] = []
        for row in CORNERS_FIRST_SLOT_ROWS:
            kind = ws.cell(row=row, column=7).value  # G = Type
            k = ws.cell(row=row, column=8).value  # H = k
            if kind is None or k is None:
                continue
            market = (
                Market.CORNERS_OVER.value
                if str(kind).strip().upper() == "OVER"
                else Market.CORNERS_UNDER.value
            )
            out.append((market, float(k) + 0.5))
        return tuple(out)
    finally:
        wb.close()


def fingerprint_hash(fingerprint: Any) -> str:
    """Amprentă textuală stabilă a parametrilor unei analize."""
    return hashlib.sha1(repr(fingerprint).encode("utf-8")).hexdigest()


def _kickoff(md: Any) -> tuple[str | None, int | None]:
    kickoff = getattr(md, "kickoff_utc", None)
    if kickoff is None:
        return None, None
    return kickoff.isoformat(), int(kickoff.timestamp())


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _base_snapshot(row: dict[str, Any], md: Any, *, model_key: str) -> dict[str, Any]:
    kickoff_iso, kickoff_unix = _kickoff(md)
    return {
        "provider_match_id": str(row.get("match_id") or getattr(md, "match_id", "")),
        "model_key": model_key,
        "model_version": model_version(model_key),
        "kickoff_utc": kickoff_iso,
        "kickoff_unix": kickoff_unix,
        "league": _as_text(row.get("liga")) or _as_text(getattr(md, "competition_name", None)),
        "home_team": _as_text(getattr(getattr(md, "home", None), "name", None)),
        "away_team": _as_text(getattr(getattr(md, "away", None), "name", None)),
        "data_status": _as_text(row.get("data_status")),
    }


def build_snapshots(analysis: Any) -> list[PredictionSnapshot]:
    """Transformă rândurile fazei ANALYSIS în predicții de jurnalizat.

    Rândurile blocate (G0 FAIL) sau cu eroare de motor nu produc snapshot: un
    model blocat nu a emis un forecast, iar înregistrarea lui ar denatura
    hit-rate-ul. SMALL SAMPLE / `pending` rămân incluse — nu sunt hard fail.
    """
    by_match = {str(md.match_id): md for md in getattr(analysis, "match_data", [])}
    allowed = {
        model: {str(md.match_id) for md in matches}
        for model, matches in (getattr(analysis, "allowed_by_model", {}) or {}).items()
    }
    out: list[PredictionSnapshot] = []

    for row in getattr(analysis, "rows", []) or []:
        model_key = str(row.get("model_id") or "")
        match_id = str(row.get("match_id") or "")
        md = by_match.get(match_id)
        if md is None or match_id not in allowed.get(model_key, set()):
            continue
        if str(row.get("recommendation") or "") == "EROARE MOTOR":
            continue
        base = _base_snapshot(row, md, model_key=model_key)

        if model_key == "over05":
            out.append(
                PredictionSnapshot(
                    **base,
                    market=Market.OVER_0_5.value,
                    line=0.5,
                    recommendation=_as_text(row.get("recommendation")),
                    # GP = Over 0.5 raportat; GL = P0 recalibrat, adică modul de eșec.
                    p_adjusted=_as_float(row.get("p_over")),
                    failure_mode=_as_float(row.get("p0_recalibrated")),
                    risk_score=_as_float(row.get("risk_score")),
                    risk_level=_as_float(row.get("risk_level")),
                    confidence=_as_float(row.get("confidence")),
                    hard_gate=_as_text(row.get("model_g0")),
                    motivation=_as_text(row.get("motiv")),
                    snapshot_status=SnapshotStatus.FROZEN_PREMATCH.value,
                )
            )
        elif model_key == "double_chance":
            for sel in row.get("dc_selections") or []:
                code = _as_text(sel.get("selection"))
                if code not in {Market.DC_1X.value, Market.DC_X2.value, Market.DC_12.value}:
                    continue
                out.append(
                    PredictionSnapshot(
                        **base,
                        market=code,
                        line=None,
                        recommendation=_as_text(sel.get("verdict")),
                        p_adjusted=_as_float(sel.get("p_adj")),
                        failure_mode=_as_float(sel.get("pfail_dc")),
                        risk_score=_as_float(sel.get("score")),
                        risk_level=_as_float(sel.get("level")),
                        # Confidence V2 este o etichetă textuală (A/B/…), nu un număr.
                        confidence_label=_as_text(sel.get("confidence")),
                        hard_gate=_as_text(sel.get("p0_final")),
                        motivation=_as_text(sel.get("motivation")),
                        snapshot_status=SnapshotStatus.FROZEN_PREMATCH.value,
                    )
                )
        elif model_key == "corners":
            selections = row.get("corners_selections") or []
            if not selections:
                # Fără rezultat de motor nu inventăm verdicte: rândul rămâne în
                # regimul vechi, completabil prin importul workbook-ului recalculat.
                for market, line in corners_lines():
                    out.append(
                        PredictionSnapshot(
                            **base,
                            market=market,
                            line=line,
                            snapshot_status=SnapshotStatus.PENDING_EXCEL_RECALC.value,
                        )
                    )
                continue
            for sel in selections:
                market = (
                    Market.CORNERS_OVER.value
                    if str(sel.get("market_type") or "").strip().upper() == "OVER"
                    else Market.CORNERS_UNDER.value
                )
                out.append(
                    PredictionSnapshot(
                        **base,
                        market=market,
                        line=_as_float(sel.get("line_value")),
                        recommendation=_as_text(sel.get("verdict")),
                        p_adjusted=_as_float(sel.get("p_final")),
                        failure_mode=_as_float(sel.get("failure_model")),
                        risk_score=_as_float(sel.get("risk_score")),
                        risk_level=_as_float(sel.get("risk_level")),
                        confidence=_as_float(sel.get("confidence_final")),
                        hard_gate=_as_text(sel.get("g0")),
                        motivation=_as_text(sel.get("reason")),
                        snapshot_status=SnapshotStatus.FROZEN_PREMATCH.value,
                    )
                )
    return out


def persist_analysis(analysis: Any, *, db_path: str | None = None) -> dict[str, Any]:
    """Scrie jurnalul pre-match al unei analize în SQLite.

    Idempotent: predicțiile deja existente nu sunt rescrise, iar rularea repetată
    a aceleiași analize reutilizează rândul din `analysis_runs`.
    """
    snapshots = build_snapshots(analysis)
    fingerprint = fingerprint_hash(getattr(analysis, "fingerprint", None))
    created = 0
    existing = 0
    pending = 0
    with open_db(db_path) as conn:
        run_id = repo.upsert_run(
            conn,
            analysis_date=str(getattr(analysis, "date_iso", "")),
            timezone_name=str(getattr(analysis, "timezone_name", "")),
            analysis_fingerprint=fingerprint,
            source_mode=str(getattr(analysis, "mode", "")) or None,
            model_ids=list(getattr(analysis, "model_ids", []) or []),
        )
        for snapshot in snapshots:
            _, was_created = repo.save_prediction(conn, run_id, snapshot)
            if was_created:
                created += 1
            else:
                existing += 1
            if snapshot.snapshot_status == SnapshotStatus.PENDING_EXCEL_RECALC.value:
                pending += 1
    return {
        "run_id": run_id,
        "created": created,
        "existing": existing,
        "pending_excel_recalc": pending,
        "total": len(snapshots),
    }
