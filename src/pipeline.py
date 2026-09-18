"""Orchestrează: fetch → validare → Excel → ZIP."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from src.adapters.corners import CornersAdapter
from src.adapters.double_chance import DoubleChanceAdapter
from src.adapters.over05 import Over05Adapter
from src.api.client import current_season_id
from src.api.mock import MockFootyStatsClient, get_client
from src.excel.generator import cleanup_run_dir, make_run_dir, write_validation_report, zip_outputs
from src.excel.integrity import IntegrityError
from src.models.match_data import MatchData
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


def _row_from_match(
    match: dict[str, Any],
    timezone_name: str,
    names_by_season: dict[int, str] | None = None,
) -> dict[str, Any]:
    ora, ora_sort = _unix_to_local_hhmm(match.get("date_unix"), timezone_name)
    home = match.get("home_name") or ""
    away = match.get("away_name") or ""
    liga = _direct_league_name(match)
    if not liga and names_by_season:
        cid = match.get("competition_id")
        try:
            liga = names_by_season.get(int(cid), "")
        except (TypeError, ValueError):
            liga = ""
    return {
        "match_id": str(match.get("id")),
        "liga": liga,
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
    """Încarcă programul zilei filtrat pe ligi, fără stats sau Excel.

    Separat de run_analysis ca listarea să nu consume cota API pe team/lastx.
    """
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


def run_analysis(
    *,
    date_iso: str,
    league_ids: list[int],
    match_ids: list[str],
    model_ids: list[str],
    timezone_name: str = "Europe/Bucharest",
    progress: ProgressCb | None = None,
) -> dict[str, Any]:
    """Rulează fluxul complet și returnează rezumat + cale ZIP."""

    def prog(msg: str, pct: float) -> None:
        if progress:
            progress(msg, pct)

    client = get_client()
    run_dir = make_run_dir()
    reports: list[ValidationReport] = []
    generated: list[Path] = []
    rows: list[dict[str, Any]] = []
    errors: list[str] = []

    try:
        prog("Încarc meciurile…", 0.1)
        matches_raw = client.matches_by_date(date_iso, timezone_name=timezone_name)
        selected = [m for m in matches_raw if str(m.get("id")) in {str(x) for x in match_ids}]
        if league_ids:
            selected = [
                m
                for m in selected
                if int(m.get("competition_id") or 0) in {int(x) for x in league_ids}
            ]

        match_data_list: list[MatchData] = []
        for i, raw in enumerate(selected):
            prog(f"Statistici meci {i + 1}/{len(selected)}…", 0.2 + 0.3 * (i / max(len(selected), 1)))
            md = client.enrich_match(raw, tz_name=timezone_name)
            match_data_list.append(md)

        prog("Validez datele…", 0.55)
        allowed_by_model: dict[str, list[MatchData]] = {m: [] for m in model_ids}
        for md in match_data_list:
            for model_id in model_ids:
                report = validate_match_for_model(md, model_id)
                reports.append(report)
                blocked = report.is_blocked(md.match_id, model_id)
                blocking = report.blocking_for(md.match_id, model_id)
                reason = blocking[0].reason if blocking else ""
                g0 = "FAIL" if blocked else "OK"
                status = "blocat" if blocked else ("pending" if any(not i.blocking for i in report.issues) else "valid")
                rows.append(
                    {
                        "liga": md.competition_name,
                        "ora_bucuresti": md.kickoff_bucharest.strftime("%H:%M") if md.kickoff_bucharest else "",
                        "echipe": f"{md.home.name} vs {md.away.name}",
                        "model": MODEL_LABELS.get(model_id, model_id),
                        "model_id": model_id,
                        "match_id": md.match_id,
                        "data_status": status,
                        "g0": g0,
                        "motiv": reason,
                    }
                )
                if not blocked:
                    allowed_by_model[model_id].append(md)

        prog("Generez fișierele Excel…", 0.7)
        if "over05" in model_ids and allowed_by_model["over05"]:
            path = run_dir / f"over05_{date_iso}.xlsx"
            try:
                Over05Adapter().write_matches(allowed_by_model["over05"], path)
                generated.append(path)
            except IntegrityError as exc:
                errors.append(exc.message)

        if "corners" in model_ids and allowed_by_model["corners"]:
            path = run_dir / f"corners_{date_iso}.xlsx"
            try:
                CornersAdapter().write_matches(allowed_by_model["corners"], path)
                generated.append(path)
            except IntegrityError as exc:
                errors.append(exc.message)

        if "double_chance" in model_ids:
            for md in allowed_by_model["double_chance"]:
                path = run_dir / f"double_chance_{md.match_id}.xlsx"
                try:
                    DoubleChanceAdapter().write_matches([md], path)
                    generated.append(path)
                except IntegrityError as exc:
                    errors.append(exc.message)

        merged = merge_reports(reports)
        write_validation_report(run_dir, merged.to_dict())
        prog("Creez arhiva ZIP…", 0.9)
        zip_path = zip_outputs(run_dir)
        prog("Gata.", 1.0)

        return {
            "run_dir": str(run_dir),
            "zip_path": str(zip_path),
            "rows": rows,
            "report": merged.to_dict(),
            "generated": [str(p) for p in generated],
            "errors": errors,
            "mode": "mock" if isinstance(client, MockFootyStatsClient) else "live",
        }
    finally:
        try:
            client.close()
        except Exception:
            pass


def cleanup_after_download(run_dir: str | Path) -> None:
    cleanup_run_dir(Path(run_dir))
