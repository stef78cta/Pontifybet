"""Orchestrează: fetch → validare → motoare (ANALYSIS) → Excel/ZIP (EXPORT)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from src.adapters.corners import CornersAdapter
from src.adapters.double_chance import DoubleChanceAdapter
from src.adapters.over05 import Over05Adapter
from src.api.client import current_season_id
from src.api.factory import get_client
from src.api.mock import MockFootyStatsClient
from src.engines.over05 import compute_over05, match_to_over05_inputs
from src.excel.generator import cleanup_run_dir, make_run_dir, write_validation_report, zip_outputs
from src.excel import generator as excel_generator
from src.excel.integrity import IntegrityError
from src.models.match_data import MatchData
from src.orchestration.double_chance_bundle import build_double_chance_artifacts
from src.orchestration.match_fetcher import enrich_matches_batch
from src.orchestration.profiler import RunProfiler
from src.orchestration.snapshot import (
    AnalysisSnapshot,
    DoubleChanceMatchArtifacts,
    Over05MatchArtifacts,
    analysis_fingerprint,
)
from src.validation.validator import ValidationReport, merge_reports, validate_match_for_model

ProgressCb = Callable[[str, float], None]

ADAPTERS = {
    "over05": Over05Adapter,
    "double_chance": DoubleChanceAdapter,
    "corners": CornersAdapter,
}

MODEL_LABELS = {
    "over05": "Over 0.5",
    "double_chance": "Șansă Dublă",
    "corners": "Cornere Multi-Line V14",
}

_UNIX_SENTINELS = {None, "", -1, -2, "-1", "-2"}


def _unix_to_local_hhmm(date_unix: Any, timezone_name: str) -> tuple[str, int | None]:
    """Convertește kickoff-ul; sentinelul nu devine 00:00."""
    if date_unix in _UNIX_SENTINELS:
        return "", None
    try:
        ts = int(date_unix)
    except (TypeError, ValueError):
        return "", None
    local = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(ZoneInfo(timezone_name))
    return local.strftime("%H:%M"), ts


def _direct_league_name(match: dict[str, Any]) -> str:
    raw = match.get("league_name") or match.get("competition_name")
    if isinstance(raw, dict):
        raw = raw.get("name") or raw.get("league_name") or ""
    return str(raw or "")


def _league_names_by_season(client: Any) -> dict[int, str]:
    """todays-matches LIVE are doar competition_id; numele e pe league-list."""
    out: dict[int, str] = {}
    if not hasattr(client, "list_leagues"):
        return out
    for lg in client.list_leagues() or []:
        if not isinstance(lg, dict):
            continue
        sid = current_season_id(lg)
        if sid is None:
            continue
        label = lg.get("name") or lg.get("league_name") or ""
        if label:
            out[int(sid)] = str(label)
    return out


def _resolved_league_name(
    match: dict[str, Any],
    names_by_season: dict[int, str] | None = None,
) -> str:
    liga = _direct_league_name(match)
    if liga:
        return liga
    if not names_by_season:
        return ""
    cid = match.get("competition_id")
    try:
        return names_by_season.get(int(cid), "")
    except (TypeError, ValueError):
        return ""


def attach_league_names(
    matches: list[dict[str, Any]],
    names_by_season: dict[int, str] | None,
) -> list[dict[str, Any]]:
    """Completează league_name din league-list când todays-matches nu îl trimite."""
    names = names_by_season or {}
    out: list[dict[str, Any]] = []
    for match in matches:
        liga = _resolved_league_name(match, names)
        if liga and not _direct_league_name(match):
            copy = dict(match)
            copy["league_name"] = liga
            out.append(copy)
        else:
            out.append(match)
    return out


def _row_from_match(
    match: dict[str, Any],
    timezone_name: str,
    names_by_season: dict[int, str] | None = None,
) -> dict[str, Any]:
    ora, ora_sort = _unix_to_local_hhmm(match.get("date_unix"), timezone_name)
    home = match.get("home_name") or ""
    away = match.get("away_name") or ""
    return {
        "match_id": str(match.get("id")),
        "liga": _resolved_league_name(match, names_by_season),
        "ora": ora,
        "ora_sort": ora_sort,
        "echipe": f"{home} vs {away}",
        "selected": True,
    }


def list_matches_for_filters(
    *,
    date_iso: str,
    league_ids: list[int],
    timezone_name: str,
    client: Any | None = None,
) -> list[dict[str, Any]]:
    """Încarcă programul zilei filtrat pe ligi, fără stats sau Excel."""
    if not league_ids:
        return []

    owned = client is None
    active = get_client() if owned else client
    try:
        wanted = {int(x) for x in league_ids}
        raw = active.matches_by_date(date_iso, timezone_name=timezone_name)
        needs_names = any(not _direct_league_name(m) for m in raw if isinstance(m, dict))
        names = _league_names_by_season(active) if needs_names else {}
        rows: list[dict[str, Any]] = []
        for match in raw:
            cid = match.get("competition_id")
            if cid in _UNIX_SENTINELS:
                continue
            try:
                if int(cid) not in wanted:
                    continue
            except (TypeError, ValueError):
                continue
            rows.append(_row_from_match(match, timezone_name, names))
        return rows
    finally:
        if owned:
            try:
                active.close()
            except Exception:
                pass


def sort_listed_matches(rows: list[dict[str, Any]], by: str) -> list[dict[str, Any]]:
    """Ordonează după ligă sau oră; rândurile fără kickoff rămân la sfârșit."""

    def liga_key(row: dict[str, Any]) -> tuple[Any, ...]:
        ts = row.get("ora_sort")
        return (
            str(row.get("liga") or ""),
            ts is None,
            ts if ts is not None else 0,
            str(row.get("echipe") or ""),
        )

    def ora_key(row: dict[str, Any]) -> tuple[Any, ...]:
        ts = row.get("ora_sort")
        return (
            ts is None,
            ts if ts is not None else 0,
            str(row.get("liga") or ""),
            str(row.get("echipe") or ""),
        )

    key = liga_key if by == "liga" else ora_key
    return sorted(rows, key=key)


def _build_rows_and_snapshot(
    match_data_list: list[MatchData],
    *,
    model_ids: list[str],
    profiler: RunProfiler,
) -> tuple[list[dict[str, Any]], dict[str, list[MatchData]], list[ValidationReport], dict[str, Over05MatchArtifacts], dict[str, DoubleChanceMatchArtifacts]]:
    reports: list[ValidationReport] = []
    rows: list[dict[str, Any]] = []
    allowed_by_model: dict[str, list[MatchData]] = {m: [] for m in model_ids}
    over05_art: dict[str, Over05MatchArtifacts] = {}
    dc_art: dict[str, DoubleChanceMatchArtifacts] = {}

    profiler.start("validation_and_engines")
    for md in match_data_list:
        for model_id in model_ids:
            report = validate_match_for_model(md, model_id)
            reports.append(report)
            blocked = report.is_blocked(md.match_id, model_id)
            blocking = report.blocking_for(md.match_id, model_id)
            reason = blocking[0].reason if blocking else ""
            g0 = "FAIL" if blocked else "OK"
            status = "blocat" if blocked else ("pending" if any(not i.blocking for i in report.issues) else "valid")
            row = {
                "liga": md.competition_name,
                "ora_bucuresti": md.kickoff_bucharest.strftime("%H:%M") if md.kickoff_bucharest else "",
                "echipe": f"{md.home.name} vs {md.away.name}",
                "model": MODEL_LABELS.get(model_id, model_id),
                "model_id": model_id,
                "match_id": md.match_id,
                "data_status": status,
                "g0": g0,
                "motiv": reason,
                "p0_recalibrated": None,
                "p_over": None,
                "confidence": None,
                "risk_score": None,
                "model_g0": None,
                "risk_level": None,
                "recommendation": None,
            }
            if model_id == "over05":
                try:
                    mapping = match_to_over05_inputs(md)
                    profiler.counters.compute_over05 += 1
                    official = compute_over05(mapping)
                    over05_art[md.match_id] = Over05MatchArtifacts(mapping=mapping, official=official)
                    row["p0_recalibrated"] = official.p0_recalibrated
                    row["p_over"] = official.p_over_reported
                    row["confidence"] = official.confidence
                    row["risk_score"] = official.risk_score
                    row["model_g0"] = official.g0 or official.cells.get("HG")
                    row["risk_level"] = official.risk_level
                    row["recommendation"] = official.recommendation or official.cells.get("HK")
                except Exception as exc:
                    row["recommendation"] = "EROARE MOTOR"
                    row["model_g0"] = "FAIL"
                    row["motiv"] = row["motiv"] or f"Motor Over 0.5: {exc}"
                if not row["recommendation"]:
                    row["recommendation"] = "WATCH / NO BET"
            if model_id == "double_chance":
                try:
                    bundle = build_double_chance_artifacts(md, profiler.counters)
                    dc_art[md.match_id] = bundle
                    mapping = bundle.mapping
                    official = bundle.official
                    row["dc_selections"] = official.payload()
                    row["recommendation"] = official.summary_recommendation()
                    row["model_g0"] = official.by_code("1X").release
                    row["risk_level"] = official.by_code("1X").level
                    row["dc_sample_status"] = mapping.get("Surse_Date!C9")
                    row["dc_prior_status"] = mapping.get("Surse_Date!C10")
                    row["dc_prior_method"] = mapping.get("Surse_Date!I10")
                    row["dc_prior_source"] = mapping.get("Surse_Date!D10")
                    row["dc_prior_cutoff"] = mapping.get("Surse_Date!F10")
                    row["dc_prior_n_home"] = mapping.get("Surse_Date!G10")
                    row["dc_prior_n_away"] = mapping.get("Surse_Date!H10")
                    row["dc_sample_n_home"] = mapping.get("Input_Meci!B36")
                    row["dc_sample_n_away"] = mapping.get("Input_Meci!C36")
                    row.update(bundle.prior_weights)
                except Exception as exc:
                    row["recommendation"] = "EROARE MOTOR"
                    row["model_g0"] = "FAIL"
                    row["motiv"] = row["motiv"] or f"Motor Șansă Dublă: {exc}"
            rows.append(row)
            if not blocked:
                allowed_by_model[model_id].append(md)
    profiler.stop("validation_and_engines")
    return rows, allowed_by_model, reports, over05_art, dc_art


def run_analysis(
    *,
    date_iso: str,
    league_ids: list[int],
    match_ids: list[str],
    model_ids: list[str],
    timezone_name: str = "Europe/Bucharest",
    progress: ProgressCb | None = None,
) -> dict[str, Any]:
    """Faza ANALYSIS: fetch → MatchData → validare → motoare → tabel UI (fără Excel/ZIP)."""

    def prog(msg: str, pct: float) -> None:
        if progress:
            progress(msg, pct)

    profiler = RunProfiler()
    client = get_client()
    fp = analysis_fingerprint(
        date_iso=date_iso,
        timezone_name=timezone_name,
        league_ids=league_ids,
        match_ids=match_ids,
        model_ids=model_ids,
    )

    try:
        prog("Încarc meciurile…", 0.05)
        profiler.start("fetch_matches")
        matches_raw = client.matches_by_date(date_iso, timezone_name=timezone_name)
        selected = [m for m in matches_raw if str(m.get("id")) in {str(x) for x in match_ids}]
        if league_ids:
            selected = [
                m
                for m in selected
                if int(m.get("competition_id") or 0) in {int(x) for x in league_ids}
            ]
        names = _league_names_by_season(client)
        selected = attach_league_names(selected, names)
        profiler.stop("fetch_matches")

        prog("Încarc contextul ligilor…", 0.15)
        prog("Încarc statisticile echipelor…", 0.25)
        match_data_list = enrich_matches_batch(
            client,
            selected,
            model_ids=model_ids,
            tz_name=timezone_name,
            profiler=profiler,
        )

        prog("Validez…", 0.55)
        rows, allowed_by_model, reports, over05_art, dc_art = _build_rows_and_snapshot(
            match_data_list,
            model_ids=model_ids,
            profiler=profiler,
        )

        prog("Calculez modelele…", 0.85)
        snapshot = AnalysisSnapshot(
            fingerprint=fp,
            date_iso=date_iso,
            timezone_name=timezone_name,
            league_ids=list(league_ids),
            match_ids=list(match_ids),
            model_ids=list(model_ids),
            match_data=match_data_list,
            allowed_by_model=allowed_by_model,
            reports=reports,
            rows=rows,
            over05=over05_art,
            double_chance=dc_art,
            mode="mock" if isinstance(client, MockFootyStatsClient) else "live",
        )

        profiler.mark_time_to_table()
        profiler.finalize_total()
        prog("Analiza este gata.", 1.0)

        merged = merge_reports(reports)
        return {
            "phase": "analysis",
            "snapshot": snapshot,
            "rows": rows,
            "report": merged.to_dict(),
            "errors": [],
            "mode": snapshot.mode,
            "profiler": profiler.to_dict(),
            "analysis_fingerprint": fp,
            "export_ready": True,
        }
    finally:
        try:
            client.close()
        except Exception:
            pass


def run_export(
    snapshot: AnalysisSnapshot,
    *,
    progress: ProgressCb | None = None,
) -> dict[str, Any]:
    """Faza EXPORT: materializează Excel/ZIP din snapshot, fără refetch sau recalcul motor."""

    def prog(msg: str, pct: float) -> None:
        if progress:
            progress(msg, pct)

    profiler = RunProfiler()
    run_dir = make_run_dir()
    generated: list[Path] = []
    errors: list[str] = []
    date_iso = snapshot.date_iso
    model_ids = snapshot.model_ids
    rows = snapshot.rows

    over05_artifacts = {
        mid: (art.mapping, art.official) for mid, art in snapshot.over05.items()
    }

    try:
        prog("Pregătesc fișierele Excel…", 0.1)
        profiler.start("export_over05")
        if "over05" in model_ids and snapshot.allowed_by_model.get("over05"):
            path = run_dir / f"over05_{date_iso}.xlsx"
            try:
                Over05Adapter().write_matches(
                    snapshot.allowed_by_model["over05"],
                    path,
                    artifacts=over05_artifacts,
                )
                generated.append(path)
            except IntegrityError as exc:
                errors.append(exc.message)
        profiler.stop("export_over05")

        profiler.start("export_corners")
        if "corners" in model_ids and snapshot.allowed_by_model.get("corners"):
            path = run_dir / f"corners_{date_iso}.xlsx"
            try:
                CornersAdapter().write_matches(snapshot.allowed_by_model["corners"], path)
                generated.append(path)
            except IntegrityError as exc:
                errors.append(exc.message)
        profiler.stop("export_corners")

        profiler.start("export_double_chance")
        if "double_chance" in model_ids:
            for md in snapshot.allowed_by_model.get("double_chance", []):
                path = run_dir / f"double_chance_{md.match_id}.xlsx"
                try:
                    DoubleChanceAdapter().write_matches(
                        [md],
                        path,
                        artifacts=snapshot.double_chance,
                    )
                    generated.append(path)
                except IntegrityError as exc:
                    errors.append(exc.message)
        profiler.stop("export_double_chance")

        prog("Verific integritatea…", 0.75)
        profiler.start("fingerprint_and_reports")
        merged = merge_reports(snapshot.reports)
        write_validation_report(run_dir, merged.to_dict())
        if hasattr(excel_generator, "write_over05_results_csv"):
            excel_generator.write_over05_results_csv(run_dir, rows)
        if hasattr(excel_generator, "write_double_chance_results_csv"):
            excel_generator.write_double_chance_results_csv(run_dir, rows)
        profiler.stop("fingerprint_and_reports")

        prog("Creez arhiva ZIP…", 0.9)
        profiler.start("zip")
        zip_path = zip_outputs(run_dir)
        profiler.stop("zip")

        profiler.mark_time_to_export()
        profiler.finalize_total()
        prog("Export gata.", 1.0)

        return {
            "phase": "export",
            "run_dir": str(run_dir),
            "zip_path": str(zip_path),
            "generated": [str(p) for p in generated],
            "errors": errors,
            "profiler": profiler.to_dict(),
        }
    except Exception:
        cleanup_run_dir(run_dir)
        raise


def cleanup_after_download(run_dir: str | Path) -> None:
    cleanup_run_dir(Path(run_dir))
