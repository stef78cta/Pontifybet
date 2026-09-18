"""Generator Excel: copiere șablon + scriere controlată + ZIP."""

from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from config.settings import OUTPUTS_DIR, TEMPLATES_DIR, ensure_runtime_dirs
from src.excel.integrity import (
    IntegrityError,
    assert_whitelist_write,
    compare_fingerprints,
    fingerprint_workbook,
)


def copy_template(template_name: str, dest: Path) -> Path:
    """Copiază șablonul read-only într-un fișier nou."""
    src = TEMPLATES_DIR / template_name
    if not src.exists():
        raise FileNotFoundError(f"Șablon lipsă: {src}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def unix_to_excel_serial(ts: int | float) -> float:
    """Unix timestamp → serial Excel (zile de la 1899-12-30)."""
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
    delta = dt - epoch
    # Excel epoch 1899-12-30; Unix epoch = 25569 zile
    return 25569 + delta.total_seconds() / 86400.0


class SafeWorkbookWriter:
    """Scrie doar pe whitelist; verifică că nu atinge formule."""

    def __init__(self, path: Path, whitelist: set[str]) -> None:
        self.path = path
        self.whitelist = whitelist
        self.before = fingerprint_workbook(path)
        self.wb = load_workbook(path)
        self._writes: list[str] = []

    def write(self, sheet: str, coordinate: str, value: Any) -> None:
        assert_whitelist_write(sheet, coordinate, self.whitelist)
        if sheet not in self.wb.sheetnames:
            raise IntegrityError(f"EXPORT BLOCAT. Motiv: foaia {sheet} nu există.")
        ws = self.wb[sheet]
        cell = ws[coordinate]
        if isinstance(cell.value, str) and cell.value.startswith("="):
            raise IntegrityError(
                f"EXPORT BLOCAT. Motiv: formula {sheet}!{coordinate} a fost modificată."
            )
        cell.value = value
        self._writes.append(f"{sheet}!{coordinate}")

    def save(self) -> Path:
        self.wb.save(self.path)
        self.wb.close()
        after = fingerprint_workbook(self.path)
        compare_fingerprints(self.before, after)
        return self.path


def make_run_dir(run_id: str | None = None) -> Path:
    ensure_runtime_dirs()
    rid = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUTS_DIR / rid
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_validation_report(run_dir: Path, report: dict[str, Any]) -> Path:
    path = run_dir / "validation_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    # CSV scurt
    csv_path = run_dir / "validation_report.csv"
    lines = ["match_id,model_id,indicator,g_level,status,blocking,reason"]
    for issue in report.get("issues", []):
        reason = str(issue.get("reason", "")).replace('"', "'")
        lines.append(
            f"{issue.get('match_id')},{issue.get('model_id')},{issue.get('indicator')},"
            f"{issue.get('g_level')},{issue.get('status')},{issue.get('blocking')},\"{reason}\""
        )
    csv_path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_over05_results_csv(run_dir: Path, rows: list[dict[str, Any]]) -> Path | None:
    """Scrie verdicturile Over 0.5 calculate în Python, vizibile în ZIP."""
    official = [r for r in rows if r.get("model_id") == "over05"]
    if not official:
        return None
    path = run_dir / "over05_rezultate.csv"
    lines = [
        "match_id,echipe,recomandare_HK,nivel_HH,g0_HG,p_over_GP,p0_GL,confidence_GT,risk_score_HE"
    ]
    for row in official:
        rec = str(row.get("recommendation") or "").replace('"', "'")
        lines.append(
            f"{row.get('match_id')},\"{row.get('echipe','')}\",\"{rec}\","
            f"{row.get('risk_level') or ''},{row.get('model_g0') or ''},"
            f"{row.get('p_over') or ''},{row.get('p0_recalibrated') or ''},"
            f"{row.get('confidence') or ''},{row.get('risk_score') or ''}"
        )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def zip_outputs(run_dir: Path, zip_name: str = "pontifybet_export.zip") -> Path:
    zip_path = run_dir / zip_name
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in run_dir.iterdir():
            if file.is_file() and file.name != zip_name:
                zf.write(file, arcname=file.name)
    return zip_path


def cleanup_run_dir(run_dir: Path) -> None:
    if run_dir.exists() and run_dir.is_dir():
        shutil.rmtree(run_dir, ignore_errors=True)
